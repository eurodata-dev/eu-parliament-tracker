import Link from "next/link";
import { formatDate } from "@/lib/format";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import type { VoteDetail } from "@/lib/types";
import { POSITIONS, POSITION_COLOR } from "@/lib/votes";
import Hemicycle from "./Hemicycle";
import ResultTag from "./ResultTag";
import styles from "./FeaturedVote.module.css";

export default function FeaturedVote({ vote, locale, t }: { vote: VoteDetail; locale: Locale; t: Dictionary }) {
  const total = vote.stats.total;
  return (
    <section className={`container section ${styles.wrap}`}>
      <div className={styles.text}>
        <p className="eyebrow">{t.home.closest}</p>
        <h2>
          <Link href={`/votes/${vote.id}`}>{vote.display_title}</Link>
        </h2>
        <p className={styles.lede}>{t.home.closestLede}</p>
        <div className={styles.meta}>
          <ResultTag result={vote.result} labels={t.vote} />
          <time dateTime={vote.timestamp}>{formatDate(vote.timestamp, locale, { month: "long" })}</time>
        </div>
        <ul className={styles.numbers}>
          {POSITIONS.map((p) => (
            <li key={p}>
              <i style={{ background: POSITION_COLOR[p] }} />
              <span>{t.vote[p]}</span>
              <b className="num">{total[p]}</b>
            </li>
          ))}
        </ul>
        <Link href={`/votes/${vote.id}`} className="button">
          {t.home.seeEveryMep} →
        </Link>
      </div>
      <Link href={`/votes/${vote.id}`} className={styles.chart} aria-label={vote.display_title}>
        <Hemicycle vote={vote} label={`${total.FOR} ${t.vote.FOR}, ${total.AGAINST} ${t.vote.AGAINST}`} />
      </Link>
    </section>
  );
}
