"use client";

import { useState } from "react";
import styles from "./ContactForm.module.css";

type Status = "idle" | "sending" | "done" | "error" | "invalid";

interface Props {
  t: { name: string; email: string; message: string; placeholder: string; send: string; ok: string; err: string; invalid: string };
}

export default function ContactForm({ t }: Props) {
  const [status, setStatus] = useState<Status>("idle");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget));
    if (!String(data.email).includes("@") || String(data.message).trim().length < 5) {
      setStatus("invalid");
      return;
    }
    setStatus("sending");
    const res = await fetch("/api/contact", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(data),
    }).catch(() => null);
    setStatus(res?.ok ? "done" : "error");
  }

  if (status === "done") return <p className={styles.done}>{t.ok}</p>;

  return (
    <form className={styles.form} onSubmit={onSubmit} noValidate>
      <label>
        <span>{t.name}</span>
        <input className="input" name="name" autoComplete="name" maxLength={120} />
      </label>
      <label>
        <span>{t.email}</span>
        <input className="input" name="email" type="email" autoComplete="email" required maxLength={200} />
      </label>
      <label>
        <span>{t.message}</span>
        <textarea className="input" name="message" rows={7} required maxLength={5000} placeholder={t.placeholder} />
      </label>
      <input type="text" name="website" tabIndex={-1} autoComplete="off" className={styles.trap} aria-hidden="true" />
      <div className={styles.actions}>
        <button className="button" disabled={status === "sending"}>
          {t.send}
        </button>
        {status === "error" && <p className={styles.error}>{t.err}</p>}
        {status === "invalid" && <p className={styles.error}>{t.invalid}</p>}
      </div>
    </form>
  );
}
