"use client";

import { ArrowLeft } from "lucide-react";

export default function Impressum() {
  return (
    <div className="min-h-screen bg-[#030303] text-[#ededed] font-sans selection:bg-[#ccff00] selection:text-black">
      <div className="max-w-3xl mx-auto px-6 py-24">
        <a href="/" className="inline-flex items-center gap-2 text-[#ccff00] hover:text-white transition-colors font-bold uppercase tracking-widest text-xs mb-16">
          <ArrowLeft size={16} />
          Zurück zur Startseite
        </a>
        
        <h1 className="text-4xl md:text-5xl font-bold tracking-tighter mb-12">Impressum</h1>
        
        <div className="space-y-8 text-neutral-400 leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-white mb-4">Angaben gemäß § 5 TMG</h2>
            <p>
              Hamid Yosefsei<br />
              hyos.tech<br />
              Osterstr. 14<br />
              28199 Bremen
            </p>
          </section>
          
          <section>
            <h2 className="text-xl font-bold text-white mb-4">Kontakt</h2>
            <p>
              Telefon: 04211616163<br />
              E-Mail: hello@hyos.tech
            </p>
          </section>
          
          <section>
            <h2 className="text-xl font-bold text-white mb-4">Umsatzsteuer-ID</h2>
            <p>
              Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br />
              DE999999999
            </p>
          </section>
          
          <section>
            <h2 className="text-xl font-bold text-white mb-4">Haftung für Inhalte</h2>
            <p>
              Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
