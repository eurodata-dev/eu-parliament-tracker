"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";
import { groupColor } from "@/lib/groups";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { fill } from "@/lib/i18n/config";
import type { Member } from "@/lib/types";
import styles from "./MepDirectory.module.css";

function normalize(s: string) {
  return s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
}

function photo(path: string | null) {
  return path ? `https://howtheyvote.eu${path}` : null;
}

export default function MepDirectory({
  members,
  t,
  initialCountry = "",
  initialGroup = "",
}: {
  members: Member[];
  t: Dictionary["meps"];
  initialCountry?: string;
  initialGroup?: string;
}) {
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState(initialCountry);
  const [group, setGroup] = useState(initialGroup);

  const countries = useMemo(
    () =>
      [...new Map(members.map((m) => [m.country.code, m.country])).values()].sort((a, b) =>
        a.label.localeCompare(b.label),
      ),
    [members],
  );
  const groups = useMemo(
    () =>
      [...new Map(members.filter((m) => m.group).map((m) => [m.group!.code, m.group!])).values()].sort(
        (a, b) => a.short_label.localeCompare(b.short_label),
      ),
    [members],
  );

  const shown = useMemo(() => {
    const q = normalize(query.trim());
    return members.filter(
      (m) =>
        (!country || m.country.code === country) &&
        (!group || m.group?.code === group) &&
        (!q || normalize(`${m.full_name} ${m.national_party?.label ?? ""}`).includes(q)),
    );
  }, [members, query, country, group]);

  return (
    <div>
      <div className={styles.filters}>
        <input
          className="input"
          type="search"
          placeholder={t.search}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label={t.search}
        />
        <select className="input" value={country} onChange={(e) => setCountry(e.target.value)} aria-label={t.anyCountry}>
          <option value="">{t.anyCountry}</option>
          {countries.map((c) => (
            <option key={c.code} value={c.code}>
              {c.label}
            </option>
          ))}
        </select>
        <select className="input" value={group} onChange={(e) => setGroup(e.target.value)} aria-label={t.anyGroup}>
          <option value="">{t.anyGroup}</option>
          {groups.map((g) => (
            <option key={g.code} value={g.code}>
              {g.short_label} · {g.label}
            </option>
          ))}
        </select>
      </div>
      <p className={styles.count}>{fill(t.count, { n: shown.length })}</p>

      {shown.length === 0 ? (
        <p className={styles.empty}>{t.none}</p>
      ) : (
        <ul className={styles.grid}>
          {shown.map((m) => {
            const src = photo(m.thumb_url);
            return (
              <li key={m.id}>
                <Link href={`/meps/${m.id}`} className={styles.card}>
                  <div className={styles.photo}>
                    {src && <Image src={src} alt="" width={104} height={130} unoptimized loading="lazy" />}
                  </div>
                  <div className={styles.info}>
                    <span className={styles.first}>{m.first_name}</span>
                    <span className={styles.last}>{m.last_name}</span>
                    <span className={styles.tag}>
                      <i style={{ background: groupColor(m.group?.code) }} />
                      {m.group?.short_label ?? "NI"}
                      <span>· {m.country.label}</span>
                    </span>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
