import type { Metadata } from "next";
import ContactForm from "@/components/ContactForm";
import { getDictionary } from "@/lib/i18n/server";
import { CONTACT_EMAIL } from "@/lib/mail";
import styles from "./contact.module.css";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Questions, suggestions, press or partnership ideas about EU Parliament Tracker.",
  alternates: { canonical: "/contact" },
};

export default async function ContactPage() {
  const { t } = await getDictionary();
  return (
    <div className="container">
      <header className={styles.head}>
        <h1>{t.contact.title}</h1>
        <p>{t.contact.subtitle}</p>
      </header>
      <div className={styles.grid}>
        <ContactForm t={t.contact} />
        <aside className={styles.aside}>
          <p className="eyebrow">{t.contact.direct}</p>
          <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>
          <p className={styles.who}>Burhan Elmas · Belgium</p>
        </aside>
      </div>
    </div>
  );
}
