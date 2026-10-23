import Link from "next/link";
import { contextText, procedureCode } from "@/lib/i18n/context";
import type { Locale } from "@/lib/i18n/config";
import type { VoteDetail } from "@/lib/types";
import styles from "./VoteContext.module.css";

export default function VoteContext({ vote, locale }: { vote: VoteDetail; locale: Locale }) {
  const c = contextText(locale);
  const code = procedureCode(vote.procedure?.reference, vote.procedure?.type);
  const proc = code ? c.procedures[code] : undefined;

  return (
    <section className={`section ${styles.wrap}`}>
      <div className="section-head">
        <h2>{c.title}</h2>
      </div>

      <div className={styles.grid}>
        <div className={styles.main}>
          {proc ? (
            <>
              <p className={styles.label}>
                {c.type} <span className="num">{code}</span>
              </p>
              <h3>{proc.name}</h3>
              <p>{proc.what}</p>
              <p className={styles.label}>{c.next}</p>
              <p>{proc.next}</p>
            </>
          ) : (
            <p>{c.unknown}</p>
          )}
          {vote.procedure && (
            <a href={vote.procedure.url} target="_blank" rel="noopener" className="more-link">
              {c.file} ↗
            </a>
          )}
        </div>

        <div className={styles.side}>
          {vote.amendment_subject && (
            <div>
              <p className={styles.label}>{c.amendment}</p>
              <p>{c.amendmentText}</p>
            </div>
          )}
          <div>
            <p className={styles.label}>{c.passes}</p>
            <p>{c.passesText}</p>
          </div>
          <Link href="/methodology" className="more-link">
            {c.method} →
          </Link>
        </div>
      </div>
    </section>
  );
}
