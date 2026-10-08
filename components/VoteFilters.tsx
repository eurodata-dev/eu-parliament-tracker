"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import styles from "./VoteFilters.module.css";

interface Suggestion {
  id: string;
  title: string;
  date: string;
  result: "ADOPTED" | "REJECTED" | null;
}

interface Props {
  q: string;
  topic: string;
  from: string;
  to: string;
  topics: { code: string; label: string }[];
  t: {
    search: string;
    searchButton: string;
    topic: string;
    anyTopic: string;
    from: string;
    to: string;
    reset: string;
  };
}

export default function VoteFilters({ q, topic, from, to, topics, t }: Props) {
  const [value, setValue] = useState(q);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const query = value.trim();
    if (query.length < 2 || query === q) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      fetch(`/api/suggest?q=${encodeURIComponent(query)}`, { signal: controller.signal })
        .then((r) => r.json())
        .then((list: Suggestion[]) => {
          setSuggestions(list);
          setOpen(true);
        })
        .catch(() => {});
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [value, q]);

  useEffect(() => {
    function close(e: MouseEvent) {
      if (box.current && !box.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const filtered = Boolean(q || topic || from || to);

  return (
    <form className={styles.form} action="/votes">
      <div className={styles.search} ref={box}>
        <label htmlFor="q" className="visually-hidden">
          {t.search}
        </label>
        <input
          id="q"
          name="q"
          className="input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onFocus={() => setOpen(suggestions.length > 0)}
          onKeyDown={(e) => {
            if (e.key === "Escape") setOpen(false);
          }}
          placeholder={t.search}
          autoComplete="off"
        />
        {open && value.trim().length >= 2 && value.trim() !== q && suggestions.length > 0 && (
          <ul className={styles.suggestions}>
            {suggestions.map((s) => (
              <li key={s.id}>
                <Link href={`/votes/${s.id}`} onClick={() => setOpen(false)}>
                  <span>{s.title}</span>
                  <small className="num">{s.date}</small>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className={styles.row}>
        <label className={styles.field}>
          <span>{t.topic}</span>
          <select name="topic" className="input" defaultValue={topic}>
            <option value="">{t.anyTopic}</option>
            {topics.map((tp) => (
              <option key={tp.code} value={tp.code}>
                {tp.label}
              </option>
            ))}
          </select>
        </label>
        <label className={styles.field}>
          <span>{t.from}</span>
          <input type="date" name="from" className="input" defaultValue={from} min="2019-07-01" />
        </label>
        <label className={styles.field}>
          <span>{t.to}</span>
          <input type="date" name="to" className="input" defaultValue={to} min="2019-07-01" />
        </label>
        <div className={styles.actions}>
          <button className="button">{t.searchButton}</button>
          {filtered && (
            <Link href="/votes" className={styles.reset}>
              {t.reset}
            </Link>
          )}
        </div>
      </div>
    </form>
  );
}
