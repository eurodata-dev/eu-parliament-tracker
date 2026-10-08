"use client";

import { useState } from "react";
import { AiSkeleton, Paragraphs } from "./AiNote";
import styles from "./AiNote.module.css";

type Labels = { generate: string; hint: string; retry: string; unavailable: string };
type State = { status: "idle" | "loading" | "failed" } | { status: "done"; text: string };

async function fetchSummary(url: string) {
  const res = await fetch(url).catch(() => null);
  const data = res?.ok ? await res.json().catch(() => null) : null;
  return data?.ok && typeof data.text === "string" ? (data.text as string) : null;
}

export default function AiGenerate({ url, labels, lines = 5 }: { url: string; labels: Labels; lines?: number }) {
  const [state, setState] = useState<State>({ status: "idle" });

  async function run() {
    setState({ status: "loading" });
    let text = await fetchSummary(url);
    if (!text) {
      // retry once, rate limit usually clears fast
      await new Promise((r) => setTimeout(r, 5000));
      text = await fetchSummary(url);
    }
    setState(text ? { status: "done", text } : { status: "failed" });
  }

  if (state.status === "done") return <Paragraphs text={state.text} />;
  if (state.status === "loading") return <AiSkeleton lines={lines} />;

  return (
    <div className={styles.prompt}>
      <p className={styles.hint}>{state.status === "failed" ? labels.unavailable : labels.hint}</p>
      <button type="button" className={`button ${styles.generate}`} onClick={run}>
        {state.status === "failed" ? labels.retry : labels.generate}
        <span aria-hidden="true">→</span>
      </button>
    </div>
  );
}
