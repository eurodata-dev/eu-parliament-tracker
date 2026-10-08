"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { groupColor, groupOrder } from "@/lib/groups";
import { seatLayout, seatRadius } from "@/lib/hemicycle";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import type { MatchData, MatchMember } from "@/lib/match";
import styles from "./MatchQuiz.module.css";

type Answer = "F" | "A" | "B" | null;
type Labels = Dictionary["match"];

const MIN_ANSWERS = 3;

function fill(text: string, values: Record<string, string | number>) {
  return text.replace(/\{(\w+)\}/g, (_, k) => String(values[k] ?? ""));
}

// same = 1, abstain vs for/against = 0.5, opposite = 0
function agreement(member: MatchMember, answers: Answer[]) {
  let points = 0;
  let compared = 0;
  answers.forEach((a, i) => {
    const m = member.votes[i];
    if (!a || m === "." || m === undefined) return;
    compared++;
    if (a === m) points += 1;
    else if (a === "B" || m === "B") points += 0.5;
  });
  return { score: compared ? points / compared : null, compared };
}

function scale(score: number) {
  const stops = [
    [229, 72, 77],
    [217, 162, 59],
    [47, 179, 107],
  ];
  const t = Math.max(0, Math.min(1, score)) * 2;
  const [a, b] = t < 1 ? [stops[0], stops[1]] : [stops[1], stops[2]];
  const k = t < 1 ? t : t - 1;
  return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * k)).join(",")})`;
}

const pct = (n: number) => Math.round(n * 100);

export default function MatchQuiz({
  data,
  t,
  topics,
  dateLocale,
}: {
  data: MatchData;
  t: Labels;
  topics: Record<string, string>;
  dateLocale: string;
}) {
  const { questions } = data;
  const [answers, setAnswers] = useState<Answer[]>(() => questions.map(() => null));
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);
  const answered = answers.filter(Boolean).length;

  function answer(a: Answer) {
    const next = [...answers];
    next[step] = a;
    setAnswers(next);
    if (step < questions.length - 1) setStep(step + 1);
    else setDone(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function restart() {
    setAnswers(questions.map(() => null));
    setStep(0);
    setDone(false);
  }

  if (done && answered >= MIN_ANSWERS) {
    return <Results data={data} answers={answers} t={t} onRestart={restart} />;
  }

  const q = questions[step];
  return (
    <div className={styles.quiz}>
      <div className={styles.progress}>
        <span className="eyebrow">{fill(t.question, { i: step + 1, n: questions.length })}</span>
        <div className={styles.bar}>
          <span style={{ width: `${(step / questions.length) * 100}%` }} />
        </div>
      </div>

      <article className={styles.card} key={q.id}>
        <div className={styles.meta}>
          <time dateTime={q.date}>
            {new Date(q.date).toLocaleDateString(dateLocale, { day: "numeric", month: "long", year: "numeric" })}
          </time>
          {q.topic && topics[q.topic] && <span className="chip">{topics[q.topic]}</span>}
        </div>
        <h2>{q.title}</h2>
        {q.summary && <p className={styles.summary}>{q.summary}</p>}
        <Link href={`/votes/${q.id}`} target="_blank" className="more-link">
          {t.readMore} ↗
        </Link>

        <div className={styles.choices}>
          <button type="button" data-choice="F" onClick={() => answer("F")}>
            {t.FOR}
          </button>
          <button type="button" data-choice="A" onClick={() => answer("A")}>
            {t.AGAINST}
          </button>
          <button type="button" data-choice="B" onClick={() => answer("B")}>
            {t.ABSTENTION}
          </button>
        </div>

        <div className={styles.secondary}>
          <button type="button" onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}>
            ← {t.back}
          </button>
          <button type="button" onClick={() => answer(null)}>
            {t.skip} →
          </button>
        </div>
      </article>

      {done && answered < MIN_ANSWERS && (
        <p className={styles.warning}>
          {fill(t.minAnswers, { n: MIN_ANSWERS })}{" "}
          <button type="button" onClick={restart}>
            {t.again}
          </button>
        </p>
      )}
    </div>
  );
}

function Results({
  data,
  answers,
  t,
  onRestart,
}: {
  data: MatchData;
  answers: Answer[];
  t: Labels;
  onRestart: () => void;
}) {
  const { questions, members } = data;
  const answered = answers.filter(Boolean).length;
  const [country, setCountry] = useState("");
  const [lit, setLit] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const id = requestAnimationFrame(() => setLit(true));
    return () => cancelAnimationFrame(id);
  }, []);

  const scored = useMemo(() => {
    const need = Math.max(2, Math.ceil(answered * 0.6));
    return members.map((m) => {
      const { score, compared } = agreement(m, answers);
      return { ...m, score: compared >= need ? score : null };
    });
  }, [members, answers, answered]);

  const groups = useMemo(() => {
    const map = new Map<string, { code: string; label: string; total: number; n: number; seats: number }>();
    for (const m of scored) {
      const g = map.get(m.group) ?? { code: m.group, label: m.groupLabel, total: 0, n: 0, seats: 0 };
      g.seats++;
      if (m.score !== null) {
        g.total += m.score;
        g.n++;
      }
      map.set(m.group, g);
    }
    return [...map.values()]
      .filter((g) => g.n > 0)
      .map((g) => ({ ...g, score: g.total / g.n }))
      .sort((a, b) => b.score - a.score);
  }, [scored]);

  const seats = useMemo(
    () =>
      [...scored].sort(
        (a, b) => groupOrder(a.group) - groupOrder(b.group) || (b.score ?? -1) - (a.score ?? -1),
      ),
    [scored],
  );
  const layout = useMemo(() => seatLayout(seats.length), [seats.length]);
  const dot = seatRadius(seats.length);

  const countries = useMemo(
    () =>
      [...new Map(members.map((m) => [m.country, m.countryLabel])).entries()].sort((a, b) =>
        a[1].localeCompare(b[1]),
      ),
    [members],
  );

  const closest = scored
    .filter((m) => m.score !== null && (!country || m.country === country))
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
    .slice(0, 8);

  const top = groups[0];
  const shareText = top ? fill(t.shareText, { n: pct(top.score), group: top.label }) : t.title;
  const url = typeof window === "undefined" ? "" : `${window.location.origin}/match`;
  const enc = encodeURIComponent;

  async function copy() {
    try {
      await navigator.clipboard.writeText(`${shareText} ${url}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  }

  return (
    <div className={styles.results}>
      {top && (
        <header className={styles.verdict}>
          <p className="eyebrow">{t.resultsTitle}</p>
          <h2>
            {t.closestGroup} <span style={{ color: groupColor(top.code) }}>{top.label}</span>
          </h2>
          <p className={styles.big}>
            <b className="num">{pct(top.score)}%</b> {t.agreementWord}
          </p>
        </header>
      )}

      <section className={styles.chamber}>
        <p className="eyebrow">{t.chamberTitle}</p>
        <svg viewBox="-1.04 -1.04 2.08 1.1" role="img" aria-label={t.chamberTitle}>
          {layout.map((p, i) => {
            const m = seats[i];
            return (
              <circle
                key={m.id}
                cx={p.x.toFixed(4)}
                cy={(-p.y).toFixed(4)}
                r={dot.toFixed(4)}
                fill={lit && m.score !== null ? scale(m.score) : "var(--absent)"}
                style={{ transitionDelay: `${Math.round(i * 2.2)}ms` }}
              >
                <title>
                  {m.name} · {m.groupLabel} · {m.score === null ? "–" : `${pct(m.score)}%`}
                </title>
              </circle>
            );
          })}
        </svg>
        <div className={styles.legend}>
          <span>{t.legendLow}</span>
          <i />
          <span>{t.legendHigh}</span>
        </div>
      </section>

      <div className={styles.columns}>
        <section>
          <h3>{t.groupsTitle}</h3>
          <ul className={styles.groups}>
            {groups.map((g) => (
              <li key={g.code}>
                <span className={styles.gname}>
                  <i style={{ background: groupColor(g.code) }} />
                  {g.label}
                </span>
                <span className={styles.gbar}>
                  <span style={{ width: `${pct(g.score)}%`, background: groupColor(g.code) }} />
                </span>
                <b className="num">{pct(g.score)}%</b>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <div className={styles.mepsHead}>
            <h3>{t.mepsTitle}</h3>
            <select className="input" value={country} onChange={(e) => setCountry(e.target.value)} aria-label={t.country}>
              <option value="">{t.allCountries}</option>
              {countries.map(([code, label]) => (
                <option key={code} value={code}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <ol className={styles.meps}>
            {closest.map((m) => (
              <li key={m.id}>
                <Link href={`/meps/${m.id}`}>
                  <span className={styles.photo}>
                    {m.photo && <Image src={m.photo} alt="" width={52} height={65} unoptimized />}
                  </span>
                  <span className={styles.who}>
                    <b>{m.name}</b>
                    <small>
                      <i style={{ background: groupColor(m.group) }} />
                      {m.groupLabel} · {m.countryLabel}
                    </small>
                  </span>
                  <b className="num" style={{ color: scale(m.score ?? 0) }}>
                    {pct(m.score ?? 0)}%
                  </b>
                </Link>
              </li>
            ))}
          </ol>
        </section>
      </div>

      <section className={styles.answers}>
        <h3>{t.answersTitle}</h3>
        <ul>
          {questions.map((q, i) => {
            const a = answers[i];
            return (
              <li key={q.id}>
                <Link href={`/votes/${q.id}`}>{q.title}</Link>
                <span className={styles.pair}>
                  <span>
                    {t.you}: <b data-choice={a ?? ""}>{a === "F" ? t.FOR : a === "A" ? t.AGAINST : a === "B" ? t.ABSTENTION : "–"}</b>
                  </span>
                  <span>
                    {t.parliament}: <b data-choice={q.adopted ? "F" : "A"}>{q.adopted ? t.adopted : t.rejected}</b>{" "}
                    <small className="num">
                      {q.for}–{q.against}
                    </small>
                  </span>
                </span>
              </li>
            );
          })}
        </ul>
      </section>

      <section className={styles.share}>
        <p>{shareText}</p>
        <div>
          <button type="button" className="chip" onClick={copy}>
            {copied ? t.copied : t.copy}
          </button>
          <a className="chip" target="_blank" rel="noopener noreferrer" href={`https://www.linkedin.com/sharing/share-offsite/?url=${enc(url)}`}>
            LinkedIn
          </a>
          <a className="chip" target="_blank" rel="noopener noreferrer" href={`https://x.com/intent/post?text=${enc(shareText)}&url=${enc(url)}`}>
            X
          </a>
          <a className="chip" target="_blank" rel="noopener noreferrer" href={`https://wa.me/?text=${enc(`${shareText} ${url}`)}`}>
            WhatsApp
          </a>
        </div>
        <button type="button" className="button" onClick={onRestart}>
          {t.again}
        </button>
      </section>

      <p className={styles.note}>{fill(t.note, { n: questions.length })}</p>
    </div>
  );
}
