"use client";

import { useState } from "react";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import styles from "./SiteFooter.module.css";

type Status = "idle" | "sending" | "done" | "error";

export default function SubscribeForm({ locale, t }: { locale: Locale; t: Dictionary["footer"] }) {
  const [status, setStatus] = useState<Status>("idle");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const email = new FormData(e.currentTarget).get("email");
    setStatus("sending");
    const res = await fetch("/api/subscribe", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email, language: locale }),
    }).catch(() => null);
    setStatus(res?.ok ? "done" : "error");
  }

  if (status === "done") return <p className={styles.notice}>{t.subscribed}</p>;

  return (
    <form className={styles.form} onSubmit={onSubmit}>
      <label className="visually-hidden" htmlFor="newsletter-email">
        {t.email}
      </label>
      <input
        id="newsletter-email"
        className="input"
        type="email"
        name="email"
        required
        placeholder={t.email}
        autoComplete="email"
      />
      <button className="button" disabled={status === "sending"}>
        {t.subscribe}
      </button>
      {status === "error" && <p className={styles.error}>{t.subscribeError}</p>}
    </form>
  );
}
