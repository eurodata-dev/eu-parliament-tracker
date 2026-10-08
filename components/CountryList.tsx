import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import type { VoteDetail } from "@/lib/types";
import TallyBar from "./TallyBar";
import styles from "./breakdown.module.css";

const VISIBLE = 10;

function Row({ c }: { c: VoteDetail["stats"]["by_country"][number] }) {
  return (
    <li className={styles.country}>
      <span className={styles.cname}>
        <span className="num muted">{c.country.iso_alpha_2}</span> {c.country.label}
      </span>
      <TallyBar tally={c.stats} castOnly height={8} />
      <span className="num">
        <b style={{ color: "var(--for)" }}>{c.stats.FOR}</b>–<b style={{ color: "var(--against)" }}>{c.stats.AGAINST}</b>–
        <b style={{ color: "var(--abstain)" }}>{c.stats.ABSTENTION}</b>
      </span>
    </li>
  );
}

export default function CountryList({ vote, t }: { vote: VoteDetail; t: Dictionary }) {
  const countries = vote.stats.by_country;
  return (
    <div>
      <ul className={styles.countries}>
        {countries.slice(0, VISIBLE).map((c) => (
          <Row key={c.country.code} c={c} />
        ))}
      </ul>
      {countries.length > VISIBLE && (
        <details className={styles.more}>
          <summary>{t.vote.seeAll.replace("{n}", String(countries.length))}</summary>
          <ul className={styles.countries}>
            {countries.slice(VISIBLE).map((c) => (
              <Row key={c.country.code} c={c} />
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
