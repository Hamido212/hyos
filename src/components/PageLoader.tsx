"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function PageLoader() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          exit={{ y: "-100%" }}
          transition={{ duration: 0.7, ease: [0.77, 0, 0.175, 1] }}
          className="fixed inset-0 z-[200] bg-[#080808] flex items-center justify-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className="text-center"
          >
            <div className="text-2xl font-bold tracking-tighter text-white mb-4">
              hyos<span className="text-[#ccff00]">.tech</span>
            </div>
            <div className="w-32 h-[2px] bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ x: "-100%" }}
                animate={{ x: "100%" }}
                transition={{ duration: 0.8, repeat: 1, ease: "easeInOut" }}
                className="w-full h-full bg-[#ccff00]"
              />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
