import type { Metadata } from "next";
import { getDictionary } from "@/lib/i18n/server";
import { methodologyText } from "@/lib/i18n/methodology";
import styles from "../about/about.module.css";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "Where EU Parliament Tracker's data comes from, how often it is updated, how the numbers are calculated and how the AI summaries are written.",
  alternates: { canonical: "/methodology" },
};

export default async function MethodologyPage() {
  const { locale } = await getDictionary();
  const m = methodologyText(locale);
  return (
    <div className={`container ${styles.page}`}>
      <header className={styles.head}>
        <h1>{m.title}</h1>
        <p className={styles.lede}>{m.lede}</p>
        <p className={styles.updated}>{m.updated}</p>
      </header>

      <nav className={styles.toc}>
        {m.sections.map((s) => (
          <a key={s.id} href={`#${s.id}`}>
            {s.h}
          </a>
        ))}
      </nav>

      <div className={styles.sections}>
        {m.sections.map((s) => (
          <section key={s.id} id={s.id}>
            <h2>{s.h}</h2>
            <div className={styles.text}>
              {s.p.map((para) => (
                <p key={para}>{para}</p>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
