"use client";

import { useState } from "react";
import styles from "./GroupShares.module.css";

export interface GroupShareRow {
  code: string;
  short: string;
  label: string;
  color: string;
  FOR: number;
  AGAINST: number;
  ABSTENTION: number;
  cast: number;
}

interface Props {
  rows: GroupShareRow[];
  t: { FOR: string; AGAINST: string; ABSTENTION: string; groups: string; all: string; none: string };
}

export default function GroupShares({ rows, t }: Props) {
  const [hidden, setHidden] = useState<Set<string>>(new Set());
  const visible = rows.filter((r) => !hidden.has(r.code));

  function toggle(code: string) {
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(code)) next.delete(code);
      else next.add(code);
      return next;
    });
  }

  return (
    <div>
      <div className={styles.toggles}>
        <span className={styles.label}>{t.groups}</span>
        <button type="button" onClick={() => setHidden(new Set())} aria-pressed={hidden.size === 0}>
          {t.all}
        </button>
        {rows.map((r) => (
          <button key={r.code} type="button" aria-pressed={!hidden.has(r.code)} onClick={() => toggle(r.code)} title={r.label}>
            <i style={{ background: r.color }} />
            {r.short}
          </button>
        ))}
      </div>

      {visible.length === 0 ? (
        <p className={styles.empty}>{t.none}</p>
      ) : (
        <ul className={styles.rows}>
          {visible.map((r) => (
            <li key={r.code}>
              <span className={styles.name} title={r.label}>
                <i style={{ background: r.color }} />
                {r.short}
              </span>
              <span className={styles.bar} aria-label={`${t.FOR} ${r.FOR}%, ${t.AGAINST} ${r.AGAINST}%, ${t.ABSTENTION} ${r.ABSTENTION}%`}>
                <span style={{ width: `${r.FOR}%`, background: "var(--for)" }} />
                <span style={{ width: `${r.AGAINST}%`, background: "var(--against)" }} />
                <span style={{ width: `${r.ABSTENTION}%`, background: "var(--abstain)" }} />
              </span>
              <span className={`${styles.pct} num`}>
                <b style={{ color: "var(--for)" }}>{r.FOR.toFixed(0)}%</b>
                <b style={{ color: "var(--against)" }}>{r.AGAINST.toFixed(0)}%</b>
                <b style={{ color: "var(--abstain)" }}>{r.ABSTENTION.toFixed(0)}%</b>
              </span>
            </li>
          ))}
        </ul>
      )}
      <p className={styles.legend}>
        <i style={{ background: "var(--for)" }} /> {t.FOR}
        <i style={{ background: "var(--against)" }} /> {t.AGAINST}
        <i style={{ background: "var(--abstain)" }} /> {t.ABSTENTION}
      </p>
    </div>
  );
}
