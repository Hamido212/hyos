"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowUpRight, CheckCircle2 } from "lucide-react";

export default function ContactForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    budget: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const subject = encodeURIComponent(`Projektanfrage von ${formData.name}`);
    const body = encodeURIComponent(
      `Name: ${formData.name}\nE-Mail: ${formData.email}\nBudget: ${formData.budget}\n\nNachricht:\n${formData.message}`
    );
    window.location.href = `mailto:hello@hyos.tech?subject=${subject}&body=${body}`;
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 4000);
  };

  const inputClasses =
    "w-full bg-[#111] border border-white/15 rounded-xl px-5 py-4 text-white placeholder:text-neutral-500 focus:outline-none focus:border-[#ccff00]/50 focus:ring-1 focus:ring-[#ccff00]/20 transition-all text-sm";

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="grid sm:grid-cols-2 gap-4 mb-4">
        <input
          type="text"
          placeholder="Dein Name"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className={inputClasses}
        />
        <input
          type="email"
          placeholder="E-Mail Adresse"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className={inputClasses}
        />
      </div>
      <div className="mb-4">
        <select
          value={formData.budget}
          onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
          className={`${inputClasses} ${!formData.budget ? "text-neutral-500" : ""}`}
        >
          <option value="" disabled>Budget-Rahmen wählen</option>
          <option value="< 3.000€">&lt; 3.000€</option>
          <option value="3.000€ - 5.000€">3.000€ - 5.000€</option>
          <option value="5.000€ - 10.000€">5.000€ - 10.000€</option>
          <option value="10.000€ - 25.000€">10.000€ - 25.000€</option>
          <option value="> 25.000€">&gt; 25.000€</option>
        </select>
      </div>
      <div className="mb-6">
        <textarea
          placeholder="Erzähl uns von deinem Projekt..."
          required
          rows={4}
          value={formData.message}
          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
          className={`${inputClasses} resize-none`}
        />
      </div>

      <button
        type="submit"
        disabled={submitted}
        className="group relative w-full sm:w-auto inline-flex items-center justify-center gap-3 bg-[#ccff00] text-black px-10 py-4 rounded-full font-bold uppercase tracking-widest text-xs transition-all overflow-hidden hover:scale-105 active:scale-95 shadow-[0_0_40px_rgba(204,255,0,0.25)] disabled:opacity-70"
      >
        {submitted ? (
          <span className="flex items-center gap-2">
            <CheckCircle2 size={16} /> Wird gesendet...
          </span>
        ) : (
          <>
            <span className="relative z-10">Projekt anfragen</span>
            <ArrowUpRight size={16} className="relative z-10 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            <div className="absolute inset-0 bg-white transform translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
          </>
        )}
      </button>
    </motion.form>
  );
}
