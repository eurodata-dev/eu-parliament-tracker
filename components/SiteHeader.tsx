import Link from "next/link";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import LanguageSelect from "./LanguageSelect";
import Logo from "./Logo";
import NavLinks from "./NavLinks";
import styles from "./SiteHeader.module.css";

export default function SiteHeader({ locale, t }: { locale: Locale; t: Dictionary }) {
  const links = [
    { href: "/votes", label: t.nav.votes },
    { href: "/meps", label: t.nav.meps },
    { href: "/match", label: t.nav.match },
    { href: "/trends", label: t.nav.trends },
    { href: "/ask", label: t.nav.ask },
    { href: "/about", label: t.nav.about },
  ];

  return (
    <header className={styles.header}>
      <div className={`container ${styles.inner}`}>
        <Link href="/" className={styles.mark}>
          <Logo size={28} />
          EU Parliament Tracker
        </Link>
        <NavLinks links={links} />
        <LanguageSelect locale={locale} label={t.footer.language} />
      </div>
    </header>
  );
}
