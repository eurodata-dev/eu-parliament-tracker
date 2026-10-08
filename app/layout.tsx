import type { Metadata, Viewport } from "next";
import "@fontsource-variable/source-serif-4";
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-sans/500.css";
import "@fontsource/ibm-plex-sans/600.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import "./globals.css";
import Analytics from "@/components/Analytics";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import { getDictionary } from "@/lib/i18n/server";

export const metadata: Metadata = {
  metadataBase: new URL("https://euparliamenttracker.com"),
  title: {
    default: "EU Parliament Tracker",
    template: "%s · EU Parliament Tracker",
  },
  description:
    "Every roll-call vote in the European Parliament, with the numbers behind it and a plain-language explanation of what was decided. See how every MEP and political group votes.",
  applicationName: "EU Parliament Tracker",
  authors: [{ name: "Burhan Elmas" }],
  creator: "Burhan Elmas",
  alternates: { canonical: "/" },
  openGraph: {
    siteName: "EU Parliament Tracker",
    type: "website",
    url: "/",
  },
  twitter: { card: "summary_large_image" },
  formatDetection: { telephone: false },
};

const STRUCTURED_DATA = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "EU Parliament Tracker",
  url: "https://euparliamenttracker.com",
  description: "Every roll-call vote in the European Parliament, explained in plain language.",
  inLanguage: ["en", "fr", "de", "nl", "es", "it"],
  creator: { "@type": "Person", name: "Burhan Elmas" },
  potentialAction: {
    "@type": "SearchAction",
    target: { "@type": "EntryPoint", urlTemplate: "https://euparliamenttracker.com/votes?q={search_term_string}" },
    "query-input": "required name=search_term_string",
  },
};

export const viewport: Viewport = {
  themeColor: "#0f1b3d",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const { locale, t } = await getDictionary();
  return (
    <html lang={locale}>
      <body>
        <SiteHeader locale={locale} t={t} />
        <main>{children}</main>
        <SiteFooter locale={locale} t={t} />
        <Analytics />
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(STRUCTURED_DATA) }} />
      </body>
    </html>
  );
}
