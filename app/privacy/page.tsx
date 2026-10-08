import type { Metadata } from "next";
import { getDictionary } from "@/lib/i18n/server";
import { privacyText } from "@/lib/i18n/privacy";
import { CONTACT_EMAIL } from "@/lib/mail";
import styles from "../listing.module.css";

export const metadata: Metadata = {
  title: "Privacy",
  description: "What EU Parliament Tracker stores about you, why, and how to have it deleted.",
  alternates: { canonical: "/privacy" },
};

export default async function PrivacyPage() {
  const { locale } = await getDictionary();
  const p = privacyText(locale);
  return (
    <div className="container">
      <header className={styles.head}>
        <h1>{p.title}</h1>
        <p>{p.updated}</p>
      </header>
      <div className={styles.legal}>
        {p.sections.map((s) => (
          <section key={s.h}>
            <h2>{s.h}</h2>
            <p>
              {s.p.split("{email}").map((part, i) => (
                <span key={i}>
                  {i > 0 && <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>}
                  {part}
                </span>
              ))}
            </p>
          </section>
        ))}
      </div>
    </div>
  );
}
