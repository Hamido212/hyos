"use client";

import { motion } from "framer-motion";
import { ArrowUpRight, ArrowRight, CheckCircle2, Terminal, Layers, Zap, Search, Users, Star, Quote } from "lucide-react";
import { useEffect, useState } from "react";
import Magnetic from "@/components/Magnetic";
import TextReveal from "@/components/TextReveal";
import Typewriter from "@/components/Typewriter";
import MobileMenu from "@/components/MobileMenu";
import ContactForm from "@/components/ContactForm";
import ScrollToTop from "@/components/ScrollToTop";
import PageLoader from "@/components/PageLoader";
import Counter from "@/components/Counter";

const fadeInUp: any = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
};

const staggerContainer: any = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const projects = [
  { title: "Brieffix", link: "https://www.brieffix.de/", industry: "SaaS / B2B", role: "Webdesign + Frontend", desc: "Eine moderne Lösung für digitalen Briefversand. Fokus auf extrem schnelle Workflows, sauberes UI und gesteigerte Lead-Generierung.", kpi: "+180% mehr Anfragen", color: "from-blue-500/20 to-cyan-500/10" },
  { title: "Dolmetschernetz", link: "https://dolmetschernetz.com/", industry: "Übersetzung", role: "UI/UX + Development", desc: "Professionelle Plattform für Dolmetscher- und Übersetzungsdienste. Klares, nutzerzentriertes Design für bessere Navigation und Conversion.", kpi: "98 Lighthouse Score", color: "from-purple-500/20 to-pink-500/10" },
  { title: "Montanaro Restaurant", link: "https://montanaro-restaurant.de/", industry: "Gastronomie", role: "Brand Identity + Web", desc: "Premium Webauftritt für ein hochwertiges Restaurant. Elegante digitale Speisekarte und nahtloses Reservierungssystem.", kpi: "+240% Online-Reservierungen", color: "from-amber-500/20 to-orange-500/10" },
  { title: "Amt Vernetzt", link: "https://amt-vernetzt.de/", industry: "Public Sector", role: "Plattform-Architektur", desc: "Digitale Infrastruktur und moderne Kommunikationsplattform für öffentliche Ämter. Fokus auf Accessibility und klare Strukturierung.", kpi: "WCAG 2.1 AA konform", color: "from-green-500/20 to-emerald-500/10" },
  { title: "Domainverkäufe", link: "https://xn--domainverkufe-kfb.com/", industry: "Domain Trading", role: "Landingpage + Conversion", desc: "Übersichtliche und vertrauenswürdige Landingpage für den professionellen Domainhandel, optimiert auf direkte Kaufanfragen.", kpi: "+320% Conversion Rate", color: "from-red-500/20 to-rose-500/10" },
  { title: "seid.dev", link: "https://seid.dev/", industry: "Software", role: "Digitales Portfolio", desc: "Minimalistisches Portfolio und Unternehmensauftritt für Softwareentwicklung. Klare Positionierung und Technik-Fokus.", kpi: "Sub-1s Ladezeit", color: "from-indigo-500/20 to-violet-500/10" },
  { title: "Spontan Bremen", link: "https://www.spontan-bremen.de/", industry: "Event / Lokales", role: "Webentwicklung", desc: "Dynamische Plattform für spontane Events und Aktivitäten im Raum Bremen. Community-fokussiert mit intuitivem Interface.", kpi: "2.000+ aktive Nutzer", color: "from-teal-500/20 to-cyan-500/10" }
];

const processSteps = [
  { num: "01", title: "Discover & Strategy", desc: "Wir analysieren Zielgruppen, Wettbewerb und technische Anforderungen, um eine saubere strategische Basis zu schaffen.", icon: Search },
  { num: "02", title: "UX/UI Design", desc: "Erstellung von Wireframes und hochauflösenden Prototypen. Fokus auf klare Benutzerführung und starke Markenästhetik.", icon: Layers },
  { num: "03", title: "Development", desc: "Pixelgenaue Umsetzung im Frontend und Backend mit modernsten Stacks (Next.js, React, Tailwind).", icon: Terminal },
  { num: "04", title: "Quality Assurance", desc: "Intensive Testing-Phase für Performance, Accessibility und geräteübergreifende Darstellung.", icon: CheckCircle2 },
  { num: "05", title: "Launch & Scale", desc: "Sicheres Deployment, SEO-Monitoring und fortlaufende Skalierung der Plattform.", icon: Zap }
];

export default function Home() {
  const [scrolled, setScrolled] = useState(false);
  const [activeProcess, setActiveProcess] = useState<number>(0);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const ActiveIcon = processSteps[activeProcess].icon;

  return (
    <div className="min-h-screen bg-[#080808] text-[#f5f5f5] font-sans selection:bg-[#ccff00] selection:text-black">
      <PageLoader />
      <ScrollToTop />

      {/* Header */}
      <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 border-b ${scrolled ? 'bg-[#080808]/90 backdrop-blur-xl border-white/10 py-4 shadow-2xl' : 'bg-transparent border-transparent py-8'}`}>
        <div className="max-w-[1400px] mx-auto px-6 md:px-12 flex items-center justify-between">
          <a href="#" className="text-xl font-bold tracking-tighter text-white flex items-center gap-1">
            hyos<span className="text-[#ccff00]">.tech</span>
          </a>

          <nav className="hidden md:flex gap-12 text-[13px] tracking-widest uppercase font-bold text-neutral-300">
            {[
              { label: 'Leistungen', href: '#leistungen' },
              { label: 'Projekte', href: '#projekte' },
              { label: 'Prozess', href: '#prozess' },
              { label: 'Über uns', href: '#ueber-uns' },
              { label: 'Kontakt', href: '#kontakt' },
            ].map((item) => (
              <a key={item.label} href={item.href} className="hover:text-white transition-colors relative group">
                {item.label}
                <span className="absolute -bottom-2 left-0 w-0 h-px bg-[#ccff00] transition-all group-hover:w-full" />
              </a>
            ))}
          </nav>

          <a href="#kontakt" className="hidden md:flex items-center gap-2 border border-white/20 bg-white/10 backdrop-blur-md text-white px-6 py-3 rounded-full text-[11px] font-bold uppercase tracking-[0.2em] hover:bg-white/20 hover:border-[#ccff00]/50 hover:text-[#ccff00] hover:shadow-[0_0_20px_rgba(204,255,0,0.15)] transition-all duration-500">
            Projekt anfragen
          </a>

          <MobileMenu />
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center pt-20 pb-20 overflow-hidden">
          <div className="absolute inset-0 z-0 bg-grid pointer-events-none" />

          <div className="max-w-[1400px] mx-auto px-6 md:px-12 w-full relative z-10 grid lg:grid-cols-2 gap-16 items-center">

            <motion.div
              initial="hidden"
              animate="visible"
              variants={staggerContainer}
            >
              <motion.div variants={fadeInUp} className="mb-10 flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-[#ccff00] animate-pulse" />
                <span className="text-[11px] font-bold uppercase tracking-[0.2em] text-neutral-300 inline-block min-h-[1em]">
                  <Typewriter text="Premium Web & Tech Agency" delay={0.2} />
                </span>
              </motion.div>

              <h1 className="text-[3.5rem] md:text-[6rem] lg:text-[7rem] leading-[0.9] font-bold tracking-tighter mb-8 text-white text-balance overflow-hidden py-2">
                <TextReveal text="Design." delay={0.1} />
                <TextReveal text="Code." delay={0.2} />
                <div className="text-transparent bg-clip-text bg-gradient-to-r from-[#ccff00] to-[#88cc00]">
                  <TextReveal text="Conversion." delay={0.3} />
                </div>
              </h1>

              <motion.p variants={fadeInUp} className="text-lg md:text-xl text-neutral-200 max-w-xl font-light leading-relaxed mb-12 text-balance">
                Wir gestalten und entwickeln digitale Auftritte, die hochwertig wirken, technisch sauber laufen und messbar performen.
              </motion.p>

              <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-6 items-start sm:items-center">
                <Magnetic>
                  <a href="#kontakt" className="group relative flex items-center justify-between gap-4 bg-[#ccff00] text-black px-8 py-4 rounded-full font-bold uppercase tracking-widest text-xs transition-all overflow-hidden hover:scale-105 active:scale-95 shadow-[0_0_40px_rgba(204,255,0,0.3)]">
                    <span className="relative z-10">Projekt starten</span>
                    <ArrowRight size={16} className="relative z-10 group-hover:translate-x-1 transition-transform" />
                    <div className="absolute inset-0 bg-white transform translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
                  </a>
                </Magnetic>
                <Magnetic>
                  <a href="#projekte" className="group flex items-center gap-3 text-neutral-200 px-6 py-4 font-bold uppercase tracking-widest text-xs hover:text-white transition-colors">
                    Arbeiten ansehen
                    <div className="w-8 h-[1px] bg-neutral-400 group-hover:w-12 group-hover:bg-[#ccff00] transition-all duration-300" />
                  </a>
                </Magnetic>
              </motion.div>
            </motion.div>

            {/* Right Abstract Visual */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
              className="relative w-full h-[500px] lg:h-[600px] hidden lg:flex items-center justify-center pointer-events-none"
            >
              <div className="absolute w-[450px] h-[450px] bg-[#ccff00]/20 rounded-full blur-[120px] mix-blend-screen animate-pulse" />
              <div className="absolute w-[300px] h-[300px] bg-blue-500/15 rounded-full blur-[100px] translate-x-32 -translate-y-20" />

              {/* Main Card */}
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className="relative z-10 w-[320px] h-[400px] bg-[#141414]/95 border border-white/20 rounded-2xl backdrop-blur-2xl shadow-[0_0_60px_rgba(0,0,0,0.6)] p-6 flex flex-col gap-5 transform rotate-[-4deg]"
              >
                <div className="flex justify-between items-center border-b border-white/10 pb-4">
                  <div className="flex gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
                  </div>
                  <div className="text-[10px] font-mono text-neutral-400">hyos.tech/dashboard</div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-[#ccff00]/20 flex items-center justify-center">
                      <Zap size={14} className="text-[#ccff00]" />
                    </div>
                    <div>
                      <div className="text-[10px] text-neutral-400 uppercase tracking-wider">Performance</div>
                      <div className="text-white font-bold">99.8 / 100</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                      <Search size={14} className="text-blue-400" />
                    </div>
                    <div>
                      <div className="text-[10px] text-neutral-400 uppercase tracking-wider">SEO Score</div>
                      <div className="text-white font-bold">100 / 100</div>
                    </div>
                  </div>
                </div>
                <div className="mt-auto h-28 rounded-xl border border-[#ccff00]/30 bg-gradient-to-br from-[#ccff00]/15 to-transparent p-4 flex flex-col justify-end shadow-inner">
                  <div className="text-[#ccff00] font-mono text-xs mb-1 font-semibold uppercase tracking-wider">Conversion Rate</div>
                  <div className="text-white text-3xl font-bold">+240%</div>
                  <div className="w-full h-1.5 bg-white/10 rounded-full mt-2 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: "78%" }}
                      transition={{ duration: 2, delay: 1, ease: "easeOut" }}
                      className="h-full bg-[#ccff00] rounded-full"
                    />
                  </div>
                </div>
              </motion.div>

              {/* Floating Small Card */}
              <motion.div
                animate={{ y: [0, 8, 0] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
                className="absolute z-20 w-[200px] bg-[#0a0a0a]/95 border border-white/20 rounded-xl shadow-[0_0_40px_rgba(0,0,0,0.6)] p-4 transform rotate-[6deg] translate-x-36 translate-y-28"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
                    <CheckCircle2 size={14} className="text-green-400" />
                  </div>
                  <div className="text-xs font-mono text-neutral-300 font-bold">Deployed</div>
                </div>
                <div className="text-[10px] text-neutral-400">Build erfolgreich</div>
                <div className="text-xs text-white font-semibold mt-1">hyos.tech — Live</div>
              </motion.div>
            </motion.div>

          </div>
        </section>

        {/* Trust Bar - echte Projektnamen */}
        <section className="border-y border-white/10 bg-[#0d0d0d] py-16 relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.03)_0,transparent_50%)] pointer-events-none" />
          <div className="max-w-[1400px] mx-auto px-6 md:px-12">
            <div className="flex flex-col items-center justify-center gap-10 text-center">
              <p className="text-[11px] font-bold text-neutral-400 uppercase tracking-[0.2em]">
                Vertrauen von Unternehmen aus verschiedenen Branchen
              </p>
              <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 text-neutral-500 w-full">
                {projects.map((project, i) => (
                  <a
                    key={i}
                    href={project.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-lg md:text-xl font-bold tracking-tighter uppercase hover:text-[#ccff00] transition-colors duration-300"
                  >
                    {project.title}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-20 bg-[#080808] border-b border-white/10">
          <div className="max-w-[1400px] mx-auto px-6 md:px-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
              {[
                { number: 7, suffix: "+", label: "Abgeschlossene Projekte" },
                { number: 3, suffix: "+", label: "Jahre Erfahrung" },
                { number: 99, suffix: "%", label: "Kundenzufriedenheit" },
                { number: 100, suffix: "", label: "Lighthouse Score" },
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  className="text-center"
                >
                  <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                    <Counter target={stat.number} suffix={stat.suffix} />
                  </div>
                  <div className="text-[11px] md:text-xs font-bold uppercase tracking-widest text-neutral-400">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Leistungen */}
        <section id="leistungen" className="py-32 md:py-48 border-b border-white/10 bg-[#080808] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-500/10 blur-[150px] rounded-full pointer-events-none" />

          <div className="max-w-[1400px] mx-auto px-6 md:px-12 relative z-10">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              variants={fadeInUp}
              className="flex flex-col md:flex-row md:items-end justify-between gap-10 mb-20"
            >
              <h2 className="text-4xl md:text-6xl font-bold tracking-tighter text-white max-w-2xl leading-[1.1]">
                Digitale Exzellenz,<br />in jeder Schicht.
              </h2>
              <p className="text-neutral-300 text-lg max-w-md leading-relaxed">
                Wir verbinden präzises Design mit sauberer Technologie. Für Plattformen, die nicht nur gut aussehen, sondern skalieren.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
              {[
                { icon: Layers, title: "Webdesign & UI/UX", desc: "Konzeption und Design von Interfaces, die Nutzer intuitiv führen und die Markenidentität messerscharf positionieren.", tags: ["UX Precision", "Design Systems", "Figma"] },
                { icon: Terminal, title: "Frontend Development", desc: "Schnelle, skalierbare Frontends mit Fokus auf Performance, sauberen Code, Wartbarkeit und Conversion.", tags: ["React", "Next.js", "Scalable Systems"] },
                { icon: Zap, title: "SEO & Web Vitals", desc: "Kompromisslose Ladezeiten und technische Optimierung für maximale organische Sichtbarkeit.", tags: ["Performance", "Core Web Vitals", "Lighthouse 100"] },
                { icon: Search, title: "Conversion Optimierung", desc: "Jedes architektonische Detail ist darauf ausgerichtet, aus anonymen Besuchern echte Anfragen zu machen.", tags: ["Conversion-first", "A/B Ready", "Analytics"] }
              ].map((service, i) => (
                <motion.div
                  key={i}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  className="bg-[#0f0f0f] border border-white/10 rounded-3xl p-10 md:p-14 group hover:bg-[#141414] hover:border-[#ccff00]/40 hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(0,0,0,0.5)] transition-all duration-500"
                >
                  <div className="w-14 h-14 bg-[#1a1a1a] border border-white/15 rounded-2xl flex items-center justify-center mb-10 group-hover:border-[#ccff00]/50 group-hover:bg-[#ccff00]/10 transition-colors">
                    <service.icon size={24} className="text-white group-hover:text-[#ccff00] transition-colors" />
                  </div>

                  <h3 className="text-2xl md:text-3xl font-bold mb-4 tracking-tight">{service.title}</h3>
                  <p className="text-neutral-300 leading-relaxed text-lg max-w-md mb-10">{service.desc}</p>

                  <div className="flex flex-wrap gap-2 mt-auto">
                    {service.tags.map(tag => (
                      <span key={tag} className="px-3 py-1.5 bg-[#080808] border border-white/10 rounded-md text-[11px] uppercase tracking-widest text-neutral-300 font-semibold group-hover:border-white/20 group-hover:text-white transition-colors">
                        {tag}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Projekte */}
        <section id="projekte" className="py-32 md:py-48 border-b border-white/10 bg-[#0d0d0d]">
          <div className="max-w-[1400px] mx-auto px-6 md:px-12">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="mb-20"
            >
              <h2 className="text-4xl md:text-6xl font-bold tracking-tighter text-white mb-4">
                Ausgewählte Arbeiten.
              </h2>
              <p className="text-neutral-400 text-lg max-w-xl">Jedes Projekt ist ein Beweis für messbare Ergebnisse und technische Exzellenz.</p>
            </motion.div>

            <div className="flex flex-col gap-20">
              {projects.map((project, i) => (
                <motion.a
                  key={i}
                  href={project.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true, margin: "-50px" }}
                  variants={fadeInUp}
                  className="group cursor-pointer grid lg:grid-cols-12 gap-8 lg:gap-12 items-center"
                >
                  {/* Image / Mockup Side */}
                  <div className={`lg:col-span-7 ${i % 2 === 1 ? 'lg:order-2' : ''} relative aspect-[4/3] md:aspect-[16/10] bg-gradient-to-br ${project.color} rounded-2xl overflow-hidden border border-white/10 group-hover:border-white/25 group-hover:shadow-[0_0_40px_rgba(255,255,255,0.05)] transition-all duration-700`}>
                    <div className="absolute inset-0 flex items-center justify-center p-8 md:p-12">

                      <div className="w-full h-full border border-white/15 bg-[#080808]/90 shadow-[0_30px_60px_rgba(0,0,0,0.8)] rounded-xl flex flex-col overflow-hidden transform group-hover:scale-[1.03] group-hover:-translate-y-2 transition-all duration-700 ease-out">
                        <div className="h-8 border-b border-white/10 bg-white/5 flex items-center px-4 gap-2 shrink-0">
                          <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                          <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                          <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
                          <div className="ml-auto text-[9px] font-mono text-neutral-500">{project.link.replace('https://', '').replace('www.', '').replace('/', '')}</div>
                        </div>
                        <div className="flex-1 p-6 md:p-8 opacity-60 group-hover:opacity-100 transition-opacity duration-700">
                          <div className="flex items-center gap-3 mb-6">
                            <div className="w-8 h-8 rounded-lg bg-[#ccff00]/20" />
                            <div className="w-24 h-3 bg-white/20 rounded-full" />
                          </div>
                          <div className="text-lg md:text-xl font-bold text-white/80 mb-4">{project.title}</div>
                          <div className="space-y-3">
                            <div className="w-full h-3 bg-white/10 rounded" />
                            <div className="w-5/6 h-3 bg-white/8 rounded" />
                            <div className="w-4/6 h-3 bg-white/6 rounded" />
                          </div>
                          <div className="mt-6 flex gap-3">
                            <div className="w-20 h-8 rounded-lg bg-[#ccff00]/20 border border-[#ccff00]/30" />
                            <div className="w-20 h-8 rounded-lg bg-white/10 border border-white/15" />
                          </div>
                        </div>
                      </div>

                      {/* Floating Action Button */}
                      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 scale-90 opacity-0 group-hover:opacity-100 group-hover:scale-100 transition-all duration-500 pointer-events-none z-10">
                        <span className="flex items-center gap-2 bg-[#ccff00] text-black text-[11px] font-bold uppercase tracking-widest px-6 py-4 rounded-full shadow-[0_0_40px_rgba(204,255,0,0.4)]">
                          Live ansehen <ArrowUpRight size={16} />
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Content Side */}
                  <div className={`lg:col-span-5 ${i % 2 === 1 ? 'lg:order-1' : ''} flex flex-col justify-center`}>
                    <div className="text-[#ccff00] text-[12px] font-bold uppercase tracking-[0.2em] mb-4">{project.industry}</div>
                    <h3 className="text-3xl md:text-5xl font-bold tracking-tighter mb-5 group-hover:text-white transition-colors">{project.title}</h3>

                    <div className="flex gap-3 mb-6">
                      <span className="px-3 py-1 border border-white/20 bg-white/5 rounded text-[11px] uppercase tracking-widest text-neutral-200 font-semibold">{project.role}</span>
                    </div>

                    <p className="text-neutral-300 text-base md:text-lg leading-relaxed mb-8">{project.desc}</p>

                    <div className="pt-6 border-t border-white/15">
                      <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-widest mb-2">Ergebnis</div>
                      <div className="text-xl font-bold text-[#ccff00]">{project.kpi}</div>
                    </div>
                  </div>
                </motion.a>
              ))}
            </div>
          </div>
        </section>

        {/* Prozess */}
        <section id="prozess" className="py-32 md:py-48 border-b border-white/10 bg-[#080808] bg-grid-small">
          <div className="max-w-[1400px] mx-auto px-6 md:px-12">

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="mb-20 max-w-2xl"
            >
              <h2 className="text-4xl md:text-6xl font-bold tracking-tighter mb-6">Unser System.</h2>
              <p className="text-neutral-300 text-lg leading-relaxed">Kein Zufall, sondern ein iterativer, transparenter Prozess, der Qualität auf jedem Schritt garantiert.</p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-start">
              <div className="flex flex-col">
                {processSteps.map((step, i) => (
                  <div
                    key={i}
                    onMouseEnter={() => setActiveProcess(i)}
                    onClick={() => setActiveProcess(i)}
                    className={`py-8 border-b border-white/10 cursor-pointer transition-all duration-300 ${activeProcess === i ? 'opacity-100 pl-4 border-l-2 border-l-[#ccff00]' : 'opacity-60 hover:opacity-100'}`}
                  >
                    <div className="flex items-center gap-6 mb-3">
                      <span className="text-[12px] font-mono font-bold text-[#ccff00]">{step.num}</span>
                      <h3 className="text-2xl md:text-3xl font-bold tracking-tight">{step.title}</h3>
                    </div>
                    {activeProcess === i && (
                      <motion.p
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="text-neutral-300 pl-12 max-w-md leading-relaxed"
                      >
                        {step.desc}
                      </motion.p>
                    )}
                  </div>
                ))}
              </div>

              {/* Dynamic Sticky Info Panel */}
              <div className="hidden lg:block relative sticky top-32">
                <motion.div
                  key={activeProcess}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                  className="w-full aspect-square bg-[#0f0f0f] border border-white/10 rounded-3xl p-12 flex flex-col justify-between overflow-hidden relative shadow-[0_0_50px_rgba(0,0,0,0.5)]"
                >
                  <div className="absolute -top-40 -right-40 w-96 h-96 bg-[#ccff00]/10 rounded-full blur-[80px]" />

                  <div className="relative z-10">
                    <div className="w-14 h-14 rounded-2xl bg-[#ccff00]/10 border border-[#ccff00]/30 flex items-center justify-center mb-8">
                      <ActiveIcon size={24} className="text-[#ccff00]" />
                    </div>
                    <div className="text-[#ccff00] text-sm font-mono font-bold mb-3 uppercase tracking-wider">Schritt {processSteps[activeProcess].num}</div>
                    <h4 className="text-3xl font-bold mb-4 tracking-tight">{processSteps[activeProcess].title}</h4>
                    <p className="text-neutral-300 text-lg leading-relaxed">{processSteps[activeProcess].desc}</p>
                  </div>

                  <div className="pt-8 border-t border-white/10 relative z-10">
                    <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-widest mb-4">Verwendete Technologien</div>
                    <div className="flex flex-wrap gap-2">
                      {["Next.js", "React", "TypeScript", "Tailwind CSS", "Framer Motion"].map(tech => (
                        <span key={tech} className="px-3 py-1.5 border border-white/15 rounded-md text-[11px] font-mono font-semibold text-neutral-200 bg-[#050505]">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* Mobile: Show active step description card */}
              <div className="lg:hidden bg-[#0f0f0f] border border-white/10 rounded-2xl p-8">
                <div className="w-12 h-12 rounded-xl bg-[#ccff00]/10 border border-[#ccff00]/30 flex items-center justify-center mb-6">
                  <ActiveIcon size={20} className="text-[#ccff00]" />
                </div>
                <div className="text-[#ccff00] text-sm font-mono font-bold mb-2 uppercase tracking-wider">Schritt {processSteps[activeProcess].num}</div>
                <h4 className="text-2xl font-bold mb-3 tracking-tight">{processSteps[activeProcess].title}</h4>
                <p className="text-neutral-300 leading-relaxed">{processSteps[activeProcess].desc}</p>
              </div>
            </div>

          </div>
        </section>

        {/* Testimonials */}
        <section className="py-32 md:py-40 border-b border-white/10 bg-[#0d0d0d] relative overflow-hidden">
          <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-purple-500/10 blur-[150px] rounded-full pointer-events-none" />
          <div className="max-w-[1400px] mx-auto px-6 md:px-12 relative z-10">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="mb-20"
            >
              <h2 className="text-4xl md:text-6xl font-bold tracking-tighter text-white mb-4">Was Kunden sagen.</h2>
              <p className="text-neutral-400 text-lg max-w-xl">Ehrliches Feedback von Unternehmen, mit denen wir zusammengearbeitet haben.</p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                { name: "Brieffix", role: "Geschäftsführer", text: "hyos.tech hat unsere Website komplett transformiert. Die Ladezeiten und das Design sind auf einem ganz anderen Level. Die Zusammenarbeit war professionell und ergebnisorientiert.", stars: 5 },
                { name: "Montanaro Restaurant", role: "Inhaber", text: "Endlich ein Webauftritt, der unsere Qualität widerspiegelt. Die Online-Reservierungen haben sich mehr als verdoppelt seit dem Launch.", stars: 5 },
                { name: "Dolmetschernetz", role: "Projektleiter", text: "Technisch sauber, visuell hochwertig und deutlich schneller als erwartet geliefert. Die Kommunikation war durchgehend transparent.", stars: 5 },
              ].map((testimonial, i) => (
                <motion.div
                  key={i}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeInUp}
                  className="bg-[#111] border border-white/10 rounded-2xl p-8 md:p-10 hover:border-white/20 transition-colors"
                >
                  <Quote size={32} className="text-[#ccff00]/30 mb-6" />
                  <p className="text-neutral-200 leading-relaxed mb-8 text-base">{testimonial.text}</p>
                  <div className="flex items-center gap-1 mb-4">
                    {Array.from({ length: testimonial.stars }).map((_, j) => (
                      <Star key={j} size={14} className="text-[#ccff00] fill-[#ccff00]" />
                    ))}
                  </div>
                  <div>
                    <div className="text-white font-bold">{testimonial.name}</div>
                    <div className="text-neutral-400 text-sm">{testimonial.role}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Über uns */}
        <section id="ueber-uns" className="py-32 md:py-48 border-b border-white/10 bg-[#080808] relative overflow-hidden">
          <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-[#ccff00]/5 blur-[150px] rounded-full pointer-events-none" />
          <div className="max-w-[1400px] mx-auto px-6 md:px-12 relative z-10">
            <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
              <motion.div
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInUp}
              >
                <div className="text-[#ccff00] text-[12px] font-bold uppercase tracking-[0.2em] mb-6">Über uns</div>
                <h2 className="text-4xl md:text-5xl font-bold tracking-tighter text-white mb-8 leading-[1.1]">
                  Wir bauen digitale Produkte, die wirklich funktionieren.
                </h2>
                <p className="text-neutral-300 text-lg leading-relaxed mb-6">
                  hyos.tech ist eine Webagentur mit Fokus auf Design, Performance und Conversion. Wir glauben daran, dass großartiges Design und saubere Technologie untrennbar sind.
                </p>
                <p className="text-neutral-300 text-lg leading-relaxed mb-10">
                  Unser Ansatz: Keine Templates, kein Overhead. Jedes Projekt wird individuell konzipiert und mit modernsten Technologien umgesetzt — von der ersten Idee bis zum fertigen Produkt.
                </p>

                <div className="grid grid-cols-2 gap-6">
                  {[
                    { label: "Individuelle Lösungen", desc: "Kein Template, kein Baukasten" },
                    { label: "Modernste Technologie", desc: "React, Next.js, Tailwind" },
                    { label: "Performance-first", desc: "Lighthouse 100 als Standard" },
                    { label: "Transparente Kommunikation", desc: "Klare Prozesse & Updates" },
                  ].map((item, i) => (
                    <div key={i}>
                      <div className="flex items-center gap-2 mb-1">
                        <CheckCircle2 size={14} className="text-[#ccff00]" />
                        <div className="text-white font-bold text-sm">{item.label}</div>
                      </div>
                      <div className="text-neutral-400 text-xs pl-5">{item.desc}</div>
                    </div>
                  ))}
                </div>
              </motion.div>

              <motion.div
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeInUp}
                className="relative"
              >
                <div className="bg-[#0f0f0f] border border-white/10 rounded-3xl p-10 md:p-14">
                  <div className="w-16 h-16 rounded-2xl bg-[#ccff00]/10 border border-[#ccff00]/30 flex items-center justify-center mb-8">
                    <Users size={28} className="text-[#ccff00]" />
                  </div>
                  <h3 className="text-2xl font-bold mb-4 tracking-tight">Das Team</h3>
                  <p className="text-neutral-300 leading-relaxed mb-8">
                    Ein kleines, spezialisiertes Team aus Designern und Entwicklern. Wir arbeiten eng zusammen und setzen auf Qualität statt Quantität.
                  </p>

                  <div className="space-y-6">
                    {[
                      { role: "Design & UX", skills: "UI/UX, Figma, Brand Identity, Design Systems" },
                      { role: "Frontend Development", skills: "React, Next.js, TypeScript, Tailwind, Framer Motion" },
                      { role: "Strategy & SEO", skills: "Performance, Conversion, Analytics, Web Vitals" },
                    ].map((member, i) => (
                      <div key={i} className="flex items-start gap-4 py-4 border-t border-white/10">
                        <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center shrink-0 text-sm font-bold text-[#ccff00]">
                          {String(i + 1).padStart(2, '0')}
                        </div>
                        <div>
                          <div className="text-white font-bold mb-1">{member.role}</div>
                          <div className="text-neutral-400 text-sm">{member.skills}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* CTA + Kontaktformular */}
        <section id="kontakt" className="py-32 md:py-48 bg-gradient-to-b from-[#080808] to-[#111] relative overflow-hidden border-b border-white/10">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-[#ccff00]/10 blur-[150px] rounded-[100%] pointer-events-none" />

          <div className="max-w-[1400px] mx-auto px-6 md:px-12 relative z-10 text-center flex flex-col items-center">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              className="mb-16"
            >
              <h2 className="text-4xl md:text-[5rem] leading-[0.95] font-bold tracking-tighter mb-6 text-white">
                Bereit für einen Auftritt,<br />der wirklich liefert?
              </h2>
              <p className="text-lg md:text-xl text-neutral-300 max-w-2xl mx-auto font-light text-balance">
                Lass uns über dein nächstes Projekt sprechen. Keine Verpflichtungen, nur ehrliches Feedback und saubere Lösungen.
              </p>
            </motion.div>

            <ContactForm />
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-[#050505] py-16 md:py-20">
        <div className="max-w-[1400px] mx-auto px-6 md:px-12">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-10 mb-12">
            <div>
              <div className="text-2xl font-bold tracking-tighter text-white mb-2 flex items-center gap-1">
                hyos<span className="text-[#ccff00]">.tech</span>
              </div>
              <div className="text-neutral-400 text-[12px] tracking-widest uppercase font-semibold">Design. Code. Conversion.</div>
            </div>

            <div className="flex flex-wrap gap-8 text-[12px] tracking-widest uppercase font-bold text-neutral-300">
              <a href="#leistungen" className="hover:text-white transition-colors">Leistungen</a>
              <a href="#projekte" className="hover:text-white transition-colors">Projekte</a>
              <a href="#prozess" className="hover:text-white transition-colors">Prozess</a>
              <a href="#kontakt" className="hover:text-white transition-colors">Kontakt</a>
            </div>
          </div>

          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-neutral-500 text-xs">
              &copy; {new Date().getFullYear()} hyos.tech — Alle Rechte vorbehalten.
            </div>
            <div className="flex gap-6 text-[11px] tracking-widest uppercase font-bold text-neutral-400">
              <a href="/impressum" className="hover:text-white transition-colors">Impressum</a>
              <a href="/datenschutz" className="hover:text-white transition-colors">Datenschutz</a>
            </div>
            <div className="text-neutral-500 text-xs">
              hello@hyos.tech
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
