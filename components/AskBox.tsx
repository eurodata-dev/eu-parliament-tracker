"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import styles from "./AskBox.module.css";

interface Props {
  t: { label: string; placeholder: string; button: string; try: string; examples: string[] };
  initial?: string;
  showExamples?: boolean;
}

export default function AskBox({ t, initial = "", showExamples = true }: Props) {
  const router = useRouter();
  const [value, setValue] = useState(initial);

  function go(question: string) {
    const q = question.trim();
    if (q) router.push(`/ask?q=${encodeURIComponent(q)}`);
  }

  return (
    <div className={styles.wrap}>
      <form
        className={styles.form}
        onSubmit={(e) => {
          e.preventDefault();
          go(value);
        }}
      >
        <label htmlFor="ask" className="visually-hidden">
          {t.label}
        </label>
        <input
          id="ask"
          className={styles.input}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={t.placeholder}
          maxLength={300}
          autoComplete="off"
        />
        <button className={`button ${styles.button}`}>{t.button}</button>
      </form>
      {showExamples && (
        <div className={styles.examples}>
          <span>{t.try}</span>
          {t.examples.map((ex) => (
            <button key={ex} type="button" onClick={() => go(ex)}>
              {ex}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
