import type { Metadata } from "next";
import Link from "next/link";
import RichText from "@/components/RichText";
import { getDictionary } from "@/lib/i18n/server";
import styles from "./about.module.css";

export const metadata: Metadata = {
  title: "About",
  description:
    "EU Parliament Tracker is an independent project by Burhan Elmas that makes European Parliament votes easy to follow: data sources, method and story.",
  alternates: { canonical: "/about" },
};

const STACK = [
  "Next.js 16",
  "TypeScript",
  "React 19",
  "HowTheyVote.eu API",
  "Groq · GPT-OSS 120B",
  "Supabase",
  "Resend",
  "Vercel",
];

export default async function AboutPage() {
  const { t } = await getDictionary();
  const a = t.about;
  return (
    <div className={`container ${styles.page}`}>
      <header className={styles.head}>
        <p className="eyebrow">{a.tagline}</p>
        <h1>{a.title}</h1>
        <div className={styles.profile}>
          <div>
            <strong>Burhan Elmas</strong>
            <span>{a.role}</span>
            <p>{a.bio}</p>
          </div>
        </div>
      </header>

      <div className={styles.sections}>
        {a.story.map((s) => (
          <section key={s.h}>
            <h2>{s.h}</h2>
            <div className={styles.text}>
              <RichText text={s.p} />
            </div>
          </section>
        ))}

        <section>
          <h2>{a.dataTitle}</h2>
          <div className={styles.text}>
            <RichText text={a.data} />
          </div>
        </section>

        <section>
          <h2>{a.stackTitle}</h2>
          <div>
            <ul className={styles.stack}>
              {STACK.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
            <p className={styles.stackNote}>{a.stackNote}</p>
          </div>
        </section>
      </div>

      <div className={styles.cta}>
        <Link href="/contact" className="button">
          {a.cta}
        </Link>
      </div>
    </div>
  );
}
