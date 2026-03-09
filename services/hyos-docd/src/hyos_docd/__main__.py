"""hyos-docd entry point."""

import logging
import sys

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

from .service import DocumentService


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    try:
        service = DocumentService(bus)
    except dbus.exceptions.DBusException as e:
        logging.critical("Failed to acquire D-Bus name: %s", e)
        sys.exit(1)

    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
