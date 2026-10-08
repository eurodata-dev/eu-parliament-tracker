import Link from "next/link";
import { formatNumber } from "@/lib/format";
import { search, TOPICS } from "@/lib/htv";
import { fill, type Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import TopicIcon from "./TopicIcon";
import styles from "./TopicGrid.module.css";

export default async function TopicGrid({ locale, t }: { locale: Locale; t: Dictionary }) {
  const counts = await Promise.all(
    TOPICS.map((code) =>
      search({ topic: code, size: 1 })
        .then((p) => p.total)
        .catch(() => 0),
    ),
  );
  const topics = TOPICS.map((code, i) => ({ code, label: t.topics[code], count: counts[i] }))
    .filter((tp) => tp.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, 11);

  return (
    <section id="topics" className="container section">
      <div className="section-head">
        <h2>{t.home.topicsTitle}</h2>
        <Link href="/votes" className="more-link">
          {t.home.allVotes} →
        </Link>
      </div>
      <ul className={styles.grid}>
        {topics.map((tp) => (
          <li key={tp.code}>
            <Link href={`/votes?topic=${tp.code}`} className={styles.tile}>
              <TopicIcon code={tp.code} />
              <span className={styles.label}>{tp.label}</span>
              <span className={styles.count}>
                {fill(t.home.topicVotes, { n: tp.count >= 500 ? "500+" : formatNumber(tp.count, locale) })}
              </span>
            </Link>
          </li>
        ))}
        <li>
          <Link href="/votes" className={`${styles.tile} ${styles.all}`}>
            <span className={styles.label}>{t.home.topicsAll}</span>
            <span className={styles.count}>→</span>
          </Link>
        </li>
      </ul>
    </section>
  );
}
