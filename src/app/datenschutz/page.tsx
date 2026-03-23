"use client";

import { ArrowLeft } from "lucide-react";

export default function Datenschutz() {
  return (
    <div className="min-h-screen bg-[#030303] text-[#ededed] font-sans selection:bg-[#ccff00] selection:text-black">
      <div className="max-w-3xl mx-auto px-6 py-24">
        <a href="/" className="inline-flex items-center gap-2 text-[#ccff00] hover:text-white transition-colors font-bold uppercase tracking-widest text-xs mb-16">
          <ArrowLeft size={16} />
          Zurück zur Startseite
        </a>
        
        <h1 className="text-4xl md:text-5xl font-bold tracking-tighter mb-12">Datenschutzerklärung</h1>
        
        <div className="space-y-8 text-neutral-400 leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-white mb-4">1. Datenschutz auf einen Blick</h2>
            <h3 className="text-lg font-bold text-white mb-2 mt-4">Allgemeine Hinweise</h3>
            <p>Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert, wenn Sie diese Website besuchen.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">2. Allgemeine Hinweise und Pflichtinformationen</h2>
            <h3 className="text-lg font-bold text-white mb-2 mt-4">Datenschutz</h3>
            <p>Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Datenschutzvorschriften sowie dieser Datenschutzerklärung.</p>
            
            <h3 className="text-lg font-bold text-white mb-2 mt-4">Hinweis zur verantwortlichen Stelle</h3>
            <p>
              Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:<br /><br />
              Hamid Yosefsei<br />
              hyos.tech<br />
              Osterstr. 14<br />
              28199 Bremen<br /><br />
              Telefon: 04211616163<br />
              E-Mail: hello@hyos.tech
            </p>
          </section>
          
          <section>
            <h2 className="text-xl font-bold text-white mb-4">3. Datenerfassung auf dieser Website</h2>
            <h3 className="text-lg font-bold text-white mb-2 mt-4">Server-Log-Dateien</h3>
            <p>Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien, die Ihr Browser automatisch an uns übermittelt.</p>
          </section>
        </div>
      </div>
    </div>
  );
}
