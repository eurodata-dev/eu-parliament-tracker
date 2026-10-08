import type { Metadata } from "next";
import AskAnswer from "@/components/AskAnswer";
import AskBox from "@/components/AskBox";
import { getDictionary } from "@/lib/i18n/server";
import styles from "../listing.module.css";

export const metadata: Metadata = {
  title: "Ask about European Parliament votes",
  description:
    "Ask a question in plain language about European Parliament votes and get an answer with links to the official roll-call records.",
  alternates: { canonical: "/ask" },
};

type Props = { searchParams: Promise<{ q?: string }> };

export default async function AskPage({ searchParams }: Props) {
  const question = ((await searchParams).q ?? "").trim().slice(0, 300);
  const { t } = await getDictionary();

  return (
    <div className="container">
      <header className={styles.head}>
        <h1>{t.ask.title}</h1>
        <p>{t.ask.lede}</p>
      </header>
      <AskBox key={question} t={t.ask} initial={question} showExamples={!question} />
      <div style={{ marginTop: 40 }}>
        {question ? <AskAnswer key={question} question={question} t={t} /> : null}
      </div>
    </div>
  );
}
