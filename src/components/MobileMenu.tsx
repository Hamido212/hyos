"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

const navItems = [
  { label: "Leistungen", href: "#leistungen" },
  { label: "Projekte", href: "#projekte" },
  { label: "Prozess", href: "#prozess" },
  { label: "Über uns", href: "#ueber-uns" },
  { label: "Kontakt", href: "#kontakt" },
];

export default function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="md:hidden text-white uppercase text-xs font-bold tracking-widest"
      >
        Menü
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-[100] bg-[#080808] flex flex-col"
          >
            <div className="flex items-center justify-between px-6 py-8">
              <div className="text-xl font-bold tracking-tighter text-white flex items-center gap-1">
                hyos<span className="text-[#ccff00]">.tech</span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white p-2"
              >
                <X size={24} />
              </button>
            </div>

            <nav className="flex-1 flex flex-col justify-center px-6 gap-2">
              {navItems.map((item, i) => (
                <motion.a
                  key={item.label}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  initial={{ opacity: 0, x: -30 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + i * 0.05, duration: 0.4 }}
                  className="text-4xl font-bold tracking-tighter text-white hover:text-[#ccff00] transition-colors py-3 border-b border-white/10"
                >
                  {item.label}
                </motion.a>
              ))}
            </nav>

            <div className="px-6 pb-10">
              <a
                href="#kontakt"
                onClick={() => setIsOpen(false)}
                className="block w-full text-center bg-[#ccff00] text-black px-8 py-4 rounded-full font-bold uppercase tracking-widest text-xs"
              >
                Projekt anfragen
              </a>
              <div className="mt-6 text-center text-neutral-400 text-sm">
                hello@hyos.tech
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
