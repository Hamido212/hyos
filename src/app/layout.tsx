import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import CustomCursor from "@/components/CustomCursor";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "hyos.tech | Design. Code. Conversion.",
  description: "Premium Web & Tech Agency. hyos.tech entwickelt extrem schnelle, hochwertige Websites und digitale Produkte für ambitionierte Marken. Klar, präzise und kompromisslos im Design.",
  metadataBase: new URL("https://hyos.tech"),
  openGraph: {
    title: "hyos.tech | Design. Code. Conversion.",
    description: "Premium Web & Tech Agency. Schnelle und conversion-orientierte Websites für Startups und Unternehmen.",
    url: "https://hyos.tech",
    siteName: "hyos.tech",
    locale: "de_DE",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  twitter: {
    title: "hyos.tech",
    card: "summary_large_image",
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  name: "hyos.tech",
  description: "Premium Web & Tech Agency — Design, Entwicklung und Conversion-Optimierung für ambitionierte Marken.",
  url: "https://hyos.tech",
  email: "hello@hyos.tech",
  priceRange: "$$",
  areaServed: "DE",
  serviceType: ["Webdesign", "Webentwicklung", "UI/UX Design", "SEO", "Conversion Optimierung"],
  knowsAbout: ["React", "Next.js", "TypeScript", "Tailwind CSS", "Framer Motion", "Web Performance"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de" className="scroll-smooth">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className={`${inter.variable} font-sans bg-background text-foreground`}>
        <CustomCursor />
        {children}
      </body>
    </html>
  );
}
