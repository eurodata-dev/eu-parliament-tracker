import Link from "next/link";
import { byHemicycle, groupColor } from "@/lib/groups";
import { fill } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import type { Group, Member } from "@/lib/types";
import styles from "./GroupGuide.module.css";

export default function GroupGuide({ members, t }: { members: Member[]; t: Dictionary }) {
  const counts = new Map<string, { group: Group; seats: number }>();
  for (const m of members) {
    if (!m.group) continue;
    const entry = counts.get(m.group.code) ?? { group: m.group, seats: 0 };
    entry.seats++;
    counts.set(m.group.code, entry);
  }
  const groups = byHemicycle([...counts.values()], (g) => g.group.code);
  const total = groups.reduce((sum, g) => sum + g.seats, 0) || 1;
  const describe = t.groups as Record<string, string>;

  return (
    <section className="container section">
      <div className="section-head">
        <h2>{t.home.groupsTitle}</h2>
      </div>
      <p className={styles.lede}>{t.home.groupsLede}</p>

      <div className={styles.seats} role="img" aria-label={t.home.groupsTitle}>
        {groups.map((g) => (
          <span key={g.group.code} style={{ flex: g.seats, background: groupColor(g.group.code) }} title={g.group.label} />
        ))}
      </div>

      <ul className={styles.list}>
        {groups.map((g) => (
          <li key={g.group.code}>
            <Link href={`/meps?group=${g.group.code}`}>
              <i style={{ background: groupColor(g.group.code) }} />
              <span className={styles.name}>
                <b>{g.group.short_label}</b>
                <small>{g.group.label}</small>
              </span>
              <span className={styles.desc}>{describe[g.group.code] ?? ""}</span>
              <span className={`${styles.count} num`}>
                {fill(t.home.seats, { n: g.seats })}
                <small>{Math.round((g.seats / total) * 100)}%</small>
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
