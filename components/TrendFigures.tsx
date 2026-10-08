import type { Trends } from "@/lib/analysis";
import { groupColor } from "@/lib/groups";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { topicLabel } from "@/lib/i18n/server";
import styles from "./TrendFigures.module.css";

function signed(n: number, unit = "") {
  return `${n > 0 ? "+" : n < 0 ? "−" : "±"}${Math.abs(n).toFixed(1)}${unit}`;
}

export default function TrendFigures({ data, t }: { data: Trends; t: Dictionary }) {
  const group = data.mostChangedGroup;
  const topic = data.mostChangedTopic;
  const pol = Math.round((data.polarizationAfter - data.polarizationBefore) * 10) / 10;
  const biggest = group
    ? (["FOR", "AGAINST", "ABSTENTION"] as const).reduce((a, b) =>
        Math.abs(group.delta[b]) > Math.abs(group.delta[a]) ? b : a,
      )
    : null;

  return (
    <dl className={styles.figures}>
      <div>
        <dt>{t.trends.mostGroup}</dt>
        <dd>
          {group ? (
            <>
              <span className={styles.big}>
                <i style={{ background: groupColor(group.group.code) }} />
                {group.group.short_label}
              </span>
              {biggest && (
                <span className={styles.detail}>
                  {t.vote[biggest]} <b className="num">{signed(group.delta[biggest], " pp")}</b>
                </span>
              )}
            </>
          ) : (
            "–"
          )}
        </dd>
      </div>
      <div>
        <dt>{t.trends.mostTopic}</dt>
        <dd>
          {topic ? (
            <>
              <span className={styles.big}>{topicLabel(t, topic)}</span>
              <span className={styles.detail}>
                {t.trends.support} <b className="num">{signed(topic.delta, " pp")}</b>
              </span>
            </>
          ) : (
            "–"
          )}
        </dd>
      </div>
      <div>
        <dt>{t.trends.polarization}</dt>
        <dd>
          <span className={`${styles.big} num`}>{signed(pol, " pp")}</span>
          <span className={styles.detail}>
            <span className="num">{data.polarizationBefore.toFixed(1)}</span> →{" "}
            <span className="num">{data.polarizationAfter.toFixed(1)}</span> ·{" "}
            {Math.abs(pol) < 1 ? t.trends.stable : pol > 0 ? t.trends.apart : t.trends.closer}
          </span>
        </dd>
      </div>
    </dl>
  );
}
