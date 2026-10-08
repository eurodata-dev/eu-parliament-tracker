import Link from "next/link";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import Logo from "./Logo";
import SubscribeForm from "./SubscribeForm";
import styles from "./SiteFooter.module.css";

export default function SiteFooter({ locale, t }: { locale: Locale; t: Dictionary }) {
  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.grid}`}>
        <div className={styles.about}>
          <Link href="/" className={styles.mark}>
            <Logo size={22} />
            EU Parliament Tracker
          </Link>
          <p>{t.footer.independent}</p>
          <p className={styles.small}>
            {t.footer.data}{" "}
            <a href="https://howtheyvote.eu" target="_blank" rel="noopener">
              howtheyvote.eu
            </a>
          </p>
        </div>

        <div>
          <h2 className={styles.title}>{t.footer.newsletter}</h2>
          <p className={styles.small}>{t.footer.newsletterLede}</p>
          <SubscribeForm locale={locale} t={t.footer} />
          <p className={styles.consent}>
            {t.footer.consent} <Link href="/privacy">{t.footer.privacy}</Link>
          </p>
        </div>

        <nav className={styles.links}>
          <Link href="/votes">{t.nav.votes}</Link>
          <Link href="/meps">{t.nav.meps}</Link>
          <Link href="/trends">{t.nav.trends}</Link>
          <Link href="/ask">{t.nav.ask}</Link>
          <Link href="/about">{t.nav.about}</Link>
          <Link href="/contact">{t.nav.contact}</Link>
          <Link href="/privacy">{t.footer.privacy}</Link>
        </nav>
      </div>
      <div className="container">
        <div className={styles.bottom}>
          <span>© {new Date().getFullYear()} EU Parliament Tracker</span>
          <span>Built by Burhan Elmas</span>
        </div>
      </div>
    </footer>
  );
}
