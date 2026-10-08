import { percent } from "@/lib/format";
import { byHemicycle, groupColor } from "@/lib/groups";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import type { VoteDetail } from "@/lib/types";
import { cast, cohesion, seats } from "@/lib/votes";
import TallyBar from "./TallyBar";
import styles from "./breakdown.module.css";

export default function GroupTable({ vote, locale, t }: { vote: VoteDetail; locale: Locale; t: Dictionary }) {
  const rows = byHemicycle(vote.stats.by_group, (g) => g.group.code);
  return (
    <div className={styles.table} role="table">
      <div className={`${styles.tr} ${styles.th}`} role="row">
        <span role="columnheader">{t.vote.group}</span>
        <span role="columnheader" className={styles.barCol} />
        <span role="columnheader" className={styles.n}>{t.vote.FOR}</span>
        <span role="columnheader" className={styles.n}>{t.vote.AGAINST}</span>
        <span role="columnheader" className={styles.n}>{t.vote.ABSTENTION}</span>
        <span role="columnheader" className={`${styles.n} ${styles.optional}`}>{t.vote.DID_NOT_VOTE}</span>
        <span role="columnheader" className={styles.n}>{t.vote.unity}</span>
      </div>
      {rows.map(({ group, stats }) => (
        <div className={styles.tr} role="row" key={group.code}>
          <span role="cell" className={styles.name} title={group.label}>
            <i style={{ background: groupColor(group.code) }} />
            {group.short_label}
            <small className="num">{seats(stats)}</small>
          </span>
          <span role="cell" className={styles.barCol}>
            <TallyBar tally={stats} height={10} />
          </span>
          <span role="cell" className={`${styles.n} num`}>{stats.FOR}</span>
          <span role="cell" className={`${styles.n} num`}>{stats.AGAINST}</span>
          <span role="cell" className={`${styles.n} num`}>{stats.ABSTENTION}</span>
          <span role="cell" className={`${styles.n} ${styles.optional} num muted`}>{stats.DID_NOT_VOTE}</span>
          <span role="cell" className={`${styles.n} num`}>
            {cast(stats) ? percent(cohesion(stats) * cast(stats), cast(stats), locale) : "–"}
          </span>
        </div>
      ))}
    </div>
  );
}
