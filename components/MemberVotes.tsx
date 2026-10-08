"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { groupColor } from "@/lib/groups";
import type { Position, VoteDetail } from "@/lib/types";
import { POSITIONS } from "@/lib/votes";
import styles from "./MemberVotes.module.css";

const PAGE = 60;

function normalize(s: string) {
  return s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
}

export default function MemberVotes({
  votes,
  t,
}: {
  votes: VoteDetail["member_votes"];
  t: Dictionary["vote"];
}) {
  const [filter, setFilter] = useState<Position | "ALL">("ALL");
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState(false);

  const counts = useMemo(() => {
    const c: Record<string, number> = { ALL: votes.length };
    POSITIONS.forEach((p) => (c[p] = votes.filter((v) => v.position === p).length));
    return c;
  }, [votes]);

  const shown = useMemo(() => {
    const q = normalize(query.trim());
    return votes.filter(
      (v) =>
        (filter === "ALL" || v.position === filter) &&
        (!q || normalize(`${v.member.full_name} ${v.member.country.label}`).includes(q)),
    );
  }, [votes, filter, query]);

  const visible = expanded || query ? shown : shown.slice(0, PAGE);

  return (
    <div>
      <div className={styles.controls}>
        <div className={styles.tabs} role="tablist">
          {(["ALL", ...POSITIONS] as const).map((p) => (
            <button
              key={p}
              role="tab"
              aria-selected={filter === p}
              data-position={p}
              onClick={() => setFilter(p)}
            >
              {p === "ALL" ? t.all : t[p]} <span className="num">{counts[p]}</span>
            </button>
          ))}
        </div>
        <input
          className={`input ${styles.search}`}
          type="search"
          placeholder={t.findMep}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label={t.findMep}
        />
      </div>

      {shown.length === 0 ? (
        <p className={styles.empty}>{t.nobody}</p>
      ) : (
        <ul className={styles.grid}>
          {visible.map(({ member, position }) => (
            <li key={member.id}>
              <Link href={`/meps/${member.id}`} className={styles.member}>
                <i data-position={position} title={t[position]} />
                <span className={styles.name}>
                  {member.first_name} <b>{member.last_name}</b>
                </span>
                <span className={styles.tag}>
                  <em style={{ background: groupColor(member.group?.code) }} />
                  {member.group?.short_label ?? "NI"} · {member.country.iso_alpha_2}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {!query && shown.length > PAGE && (
        <button className={styles.toggle} onClick={() => setExpanded(!expanded)}>
          {expanded ? t.showLess : t.seeAll.replace("{n}", String(shown.length))}
        </button>
      )}
    </div>
  );
}
