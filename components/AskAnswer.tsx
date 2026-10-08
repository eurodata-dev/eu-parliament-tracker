"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { Paragraphs } from "./AiNote";
import styles from "./AskAnswer.module.css";

interface Source {
  id: string;
  title: string;
  date: string;
  result: "ADOPTED" | "REJECTED" | null;
}

type State =
  | { status: "loading" }
  | { status: "streaming" | "done"; text: string; sources: Source[] }
  | { status: "empty" | "error" | "busy" };

export default function AskAnswer({ question, t }: { question: string; t: Dictionary }) {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    let text = "";
    let sources: Source[] = [];

    (async () => {
      setState({ status: "loading" });
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      });
      if (res.status === 429) return setState({ status: "busy" });
      if (!res.ok || !res.body) return setState({ status: "error" });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line) continue;
          const event = JSON.parse(line);
          if (event.type === "sources") {
            sources = event.votes;
            if (!sources.length) return setState({ status: "empty" });
          } else if (event.type === "text") {
            text += event.value;
          } else if (event.type === "error") {
            return setState(text ? { status: "done", text, sources } : { status: "error" });
          }
        }
        setState({ status: "streaming", text, sources });
      }
      setState({ status: "done", text, sources });
    })().catch((err) => {
      if (err?.name !== "AbortError") setState({ status: "error" });
    });

    return () => controller.abort();
  }, [question]);

  if (state.status !== "streaming" && state.status !== "done") {
    const message = {
      loading: t.ask.reading,
      empty: t.ask.noMatch,
      busy: t.ask.busy,
      error: t.ask.error,
    }[state.status];
    return <p className={styles.status}>{message}</p>;
  }

  return (
    <div className={styles.answer}>
      <div className={styles.text}>
        <Paragraphs text={state.text || "…"} />
        {state.status === "streaming" && <span className={styles.caret} />}
      </div>
      <p className={styles.note}>{t.ai.note}</p>

      <h2 className="eyebrow">{t.ask.sources}</h2>
      <ol className={styles.sources}>
        {state.sources.map((s, i) => (
          <li key={s.id}>
            <span className="num">[{i + 1}]</span>
            <Link href={`/votes/${s.id}`}>{s.title}</Link>
            <span className={styles.when}>
              {s.date.slice(0, 10)}
              {s.result && (
                <b style={{ color: s.result === "ADOPTED" ? "var(--for)" : "var(--against)" }}>
                  {s.result === "ADOPTED" ? t.vote.adopted : t.vote.rejected}
                </b>
              )}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
