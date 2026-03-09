"""
hyos-routerd — D-Bus service implementation (org.hyos.Router1)

The central task orchestrator. Every task goes through:
  1. Policy check (hyos-policyd via D-Bus)
  2. Routing to the correct backend (hyos-docd, hyos-indexerd)
  3. Job lifecycle management

Tasks execute in background threads; the main GLib loop stays responsive.
Job state is in-memory only — cleared on service restart.
"""

import logging
import threading
import uuid

import dbus
import dbus.service

from .clients import PolicyClient, IndexerClient, DocClient

log = logging.getLogger(__name__)

_CAPABILITIES = [
    "semantic_search",
    "summarize",
    "extract_deadlines",
    "translate",
    "draft_reply",
]

# Job status values
_PENDING   = "pending"
_RUNNING   = "running"
_FINISHED  = "finished"
_FAILED    = "failed"
_CANCELLED = "cancelled"


def _sv(val) -> dbus.Variant:
    if isinstance(val, bool):
        return dbus.Variant("b", val)
    if isinstance(val, int):
        return dbus.Variant("i", val)
    if isinstance(val, float):
        return dbus.Variant("d", val)
    return dbus.Variant("s", str(val) if val is not None else "")


class RouterService(dbus.service.Object):

    def __init__(self, bus: dbus.SessionBus) -> None:
        name = dbus.service.BusName("org.hyos.Router1", bus)
        super().__init__(name, "/org/hyos/Router")
        self._jobs: dict[str, dict] = {}
        self._jobs_lock = threading.Lock()
        self._policy = PolicyClient(bus)
        self._indexer = IndexerClient(bus)
        self._docs = DocClient(bus)
        log.info("RouterService ready — capabilities: %s", _CAPABILITIES)

    # ------------------------------------------------------------------ #
    # Job helpers (thread-safe)                                            #
    # ------------------------------------------------------------------ #

    def _new_job(self, task_type: str) -> str:
        job_id = str(uuid.uuid4())
        with self._jobs_lock:
            self._jobs[job_id] = {
                "id": job_id,
                "status": _PENDING,
                "type": task_type,
                "result": {},
                "error": {},
            }
        return job_id

    def _set_running(self, job_id: str) -> None:
        with self._jobs_lock:
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = _RUNNING

    def _finish(self, job_id: str, result: dict) -> None:
        with self._jobs_lock:
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = _FINISHED
                self._jobs[job_id]["result"] = result

    def _fail(self, job_id: str, code: str, message: str) -> None:
        with self._jobs_lock:
            if job_id in self._jobs:
                self._jobs[job_id]["status"] = _FAILED
                self._jobs[job_id]["error"] = {"code": code, "message": message}

    def _is_cancelled(self, job_id: str) -> bool:
        with self._jobs_lock:
            return self._jobs.get(job_id, {}).get("status") == _CANCELLED

    # ------------------------------------------------------------------ #
    # Task routing                                                         #
    # ------------------------------------------------------------------ #

    def _execute_task(self, job_id: str, request: dict) -> None:
        task_type = request.get("type", "")
        self._set_running(job_id)
        log.info("Job %s: running task=%s", job_id[:8], task_type)

        try:
            if task_type == "semantic_search":
                query = request.get("query", "")
                limit = int(request.get("limit", 20))
                results = self._indexer.search(query, limit)
                self._finish(job_id, {"results": str(results), "count": len(results)})

            elif task_type == "summarize":
                uri = request.get("uri", "")
                if not uri:
                    raise ValueError("'uri' is required for summarize")
                result = self._docs.summarize(uri)
                self._finish(job_id, result)

            elif task_type == "extract_deadlines":
                uri = request.get("uri", "")
                if not uri:
                    raise ValueError("'uri' is required for extract_deadlines")
                result = self._docs.extract_deadlines(uri)
                self._finish(job_id, result)

            elif task_type == "translate":
                uri = request.get("uri", "")
                target_lang = request.get("target_lang", "English")
                if not uri:
                    raise ValueError("'uri' is required for translate")
                result = self._docs.translate(uri, target_lang)
                self._finish(job_id, result)

            elif task_type == "draft_reply":
                uri = request.get("uri", "")
                tone = request.get("tone", "neutral")
                if not uri:
                    raise ValueError("'uri' is required for draft_reply")
                result = self._docs.draft_reply(uri, tone)
                self._finish(job_id, result)

            else:
                raise ValueError(f"Unknown task type: {task_type!r}")

            log.info("Job %s: finished", job_id[:8])

        except Exception as e:
            log.exception("Job %s: failed", job_id[:8])
            self._fail(job_id, "org.hyos.Error.TaskFailed", str(e))

    # ------------------------------------------------------------------ #
    # D-Bus interface: org.hyos.Router1                                   #
    # ------------------------------------------------------------------ #

    @dbus.service.method(
        dbus_interface="org.hyos.Router1",
        in_signature="a{sv}",
        out_signature="s",
    )
    def RunTask(self, request: dict) -> str:
        # Unpack dbus types
        py_req: dict = {}
        for k, v in request.items():
            py_req[str(k)] = v.unpack() if hasattr(v, "unpack") else str(v)

        task_type = py_req.get("type", "")
        if not task_type:
            raise dbus.exceptions.DBusException(
                "org.hyos.Error.InvalidArgument", "Missing 'type' in request"
            )
        if task_type not in _CAPABILITIES:
            raise dbus.exceptions.DBusException(
                "org.hyos.Error.UnknownTask", f"Unknown task type: {task_type}"
            )

        # Policy check
        policy_action = {
            "type": task_type,
            "network": False,
            "write": False,
            "privileged": False,
        }
        decision = self._policy.evaluate(policy_action)
        if decision.get("decision") == "deny":
            raise dbus.exceptions.DBusException(
                "org.hyos.Error.PolicyDenied",
                decision.get("reason", "Denied by policy"),
            )

        job_id = self._new_job(task_type)
        thread = threading.Thread(
            target=self._execute_task,
            args=(job_id, py_req),
            daemon=True,
            name=f"job-{job_id[:8]}",
        )
        thread.start()
        log.info("RunTask: task=%s → job %s", task_type, job_id[:8])
        return job_id

    @dbus.service.method(
        dbus_interface="org.hyos.Router1",
        in_signature="s",
        out_signature="a{sv}",
    )
    def GetJob(self, job_id: str) -> dict:
        with self._jobs_lock:
            job = self._jobs.get(str(job_id))
        if job is None:
            raise dbus.exceptions.DBusException(
                "org.hyos.Error.NotFound", f"Job not found: {job_id}"
            )
        result = dbus.Dictionary({
            "id":     _sv(job["id"]),
            "status": _sv(job["status"]),
            "type":   _sv(job.get("type", "")),
        })
        if job["status"] == _FINISHED:
            # Summarize result as a flat string dict for simplicity in v0.0.1
            for k, v in job.get("result", {}).items():
                result[str(k)] = _sv(v)
        if job["status"] == _FAILED:
            err = job.get("error", {})
            result["error_code"]    = _sv(err.get("code", ""))
            result["error_message"] = _sv(err.get("message", ""))
        return result

    @dbus.service.method(
        dbus_interface="org.hyos.Router1",
        in_signature="s",
        out_signature="",
    )
    def CancelJob(self, job_id: str) -> None:
        with self._jobs_lock:
            if job_id in self._jobs:
                status = self._jobs[job_id]["status"]
                if status in (_PENDING, _RUNNING):
                    self._jobs[job_id]["status"] = _CANCELLED
                    log.info("CancelJob: %s", job_id[:8])

    @dbus.service.method(
        dbus_interface="org.hyos.Router1",
        in_signature="",
        out_signature="as",
    )
    def ListCapabilities(self) -> list:
        return dbus.Array(_CAPABILITIES, signature="s")

    # Signals
    @dbus.service.signal(dbus_interface="org.hyos.Router1", signature="sa{sv}")
    def JobUpdated(self, job_id: str, state: dict) -> None:
        pass

    @dbus.service.signal(dbus_interface="org.hyos.Router1", signature="sa{sv}")
    def JobFinished(self, job_id: str, result: dict) -> None:
        pass

    @dbus.service.signal(dbus_interface="org.hyos.Router1", signature="sss")
    def JobFailed(self, job_id: str, code: str, message: str) -> None:
        pass
