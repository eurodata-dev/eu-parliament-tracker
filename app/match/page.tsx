import type { Metadata } from "next";
import { Suspense } from "react";
import { AiSkeleton } from "@/components/AiNote";
import MatchQuiz from "@/components/MatchQuiz";
import { fill } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { getDictionary } from "@/lib/i18n/server";
import { matchData } from "@/lib/match";
import styles from "../listing.module.css";

export async function generateMetadata(): Promise<Metadata> {
  const { t } = await getDictionary();
  return {
    title: t.match.title,
    description: t.match.metaDescription,
    alternates: { canonical: "/match" },
  };
}

async function Quiz({ locale, t }: { locale: string; t: Dictionary }) {
  const data = await matchData().catch((err) => {
    console.error("match data failed", err);
    return null;
  });
  if (!data || data.questions.length < 5) return <p className="muted">{t.errors.failed}</p>;
  return (
    <>
      <p className={styles.lede}>{fill(t.match.lede, { n: data.questions.length, m: data.members.length })}</p>
      <MatchQuiz data={data} t={t.match} topics={t.topics} dateLocale={locale} />
    </>
  );
}

export default async function MatchPage() {
  const { locale, t } = await getDictionary();
  return (
    <div className="container">
      <header className={styles.head}>
        <h1>{t.match.title}</h1>
      </header>
      <Suspense fallback={<AiSkeleton lines={6} />}>
        <Quiz locale={locale} t={t} />
      </Suspense>
    </div>
  );
}
