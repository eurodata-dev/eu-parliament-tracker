import { aiEnabled } from "@/lib/ai";
import { shares, topicOverview } from "@/lib/analysis";
import { formatDate } from "@/lib/format";
import { groupColor } from "@/lib/groups";
import { fill, type Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { cast } from "@/lib/votes";
import AiGenerate from "./AiGenerate";
import AiNote, { AiSkeleton } from "./AiNote";
import GroupShares from "./GroupShares";
import TallyBar from "./TallyBar";
import styles from "./TopicOverview.module.css";


export default async function TopicOverview({
  q,
  topic,
  locale,
  t,
}: {
  q: string;
  topic: string;
  locale: Locale;
  t: Dictionary;
}) {
  const data = await topicOverview(q, topic).catch(() => null);
  if (!data) return null;

  const total = data.total;
  const pct = shares(total);
  const rows = data.groups
    .filter((g) => cast(g.tally) > 0)
    .map((g) => ({
      code: g.group.code,
      short: g.group.short_label,
      label: g.group.label,
      color: groupColor(g.group.code),
      cast: cast(g.tally),
      ...shares(g.tally),
    }));

  return (
    <section className={styles.box}>
      <header className={styles.head}>
        <p className="eyebrow">{fill(t.votes.overview, { n: data.count })}</p>
        {data.first && data.last && (
          <p className={styles.period}>
            {formatDate(data.first, locale)} – {formatDate(data.last, locale)}
          </p>
        )}
      </header>

      <div className={styles.grid}>
        <div>
          <dl className={styles.figures}>
            <div>
              <dt>{t.vote.adopted}</dt>
              <dd className="num" style={{ color: "var(--for)" }}>
                {data.adopted}
              </dd>
            </div>
            <div>
              <dt>{t.vote.rejected}</dt>
              <dd className="num" style={{ color: "var(--against)" }}>
                {data.rejected}
              </dd>
            </div>
            <div>
              <dt>{t.vote.FOR}</dt>
              <dd className="num">{pct.FOR.toFixed(0)}%</dd>
            </div>
            <div>
              <dt>{t.vote.AGAINST}</dt>
              <dd className="num">{pct.AGAINST.toFixed(0)}%</dd>
            </div>
          </dl>
          <TallyBar tally={total} castOnly height={8} />
          <p className={styles.note}>{t.votes.overviewNote}</p>

          <h3 className={styles.sub}>{t.vote.byGroup}</h3>
          <GroupShares
            rows={rows}
            t={{
              FOR: t.vote.FOR,
              AGAINST: t.vote.AGAINST,
              ABSTENTION: t.vote.ABSTENTION,
              groups: t.vote.group,
              all: t.vote.all,
              none: t.votes.noGroups,
            }}
          />
        </div>

        <AiNote title={t.votes.explain} note={t.ai.note} badge={t.ai.badge}>
          {aiEnabled() ? (
            <AiGenerate url={`/api/summary?${new URLSearchParams({ kind: "topic", q, topic })}`} labels={t.ai} lines={7} />
          ) : (
            <p className="muted">{t.ai.unavailable}</p>
          )}
        </AiNote>
      </div>
    </section>
  );
}

export function TopicOverviewSkeleton() {
  return (
    <section className={styles.box}>
      <AiSkeleton lines={6} />
    </section>
  );
}
