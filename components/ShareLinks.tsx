"use client";

import { useState } from "react";
import styles from "./ShareLinks.module.css";

export default function ShareLinks({ path, title, t }: { path: string; title: string; t: { label: string; copy: string; copied: string } }) {
  const [copied, setCopied] = useState(false);
  const url = `https://euparliamenttracker.com${path}`;
  const encoded = encodeURIComponent(url);

  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard blocked, nothing useful to do
    }
  }

  return (
    <div className={styles.share}>
      <span>{t.label}</span>
      <button type="button" onClick={copy}>
        {copied ? t.copied : t.copy}
      </button>
      <a href={`https://www.linkedin.com/sharing/share-offsite/?url=${encoded}`} target="_blank" rel="noopener">
        LinkedIn
      </a>
      <a
        href={`https://x.com/intent/post?url=${encoded}&text=${encodeURIComponent(title)}`}
        target="_blank"
        rel="noopener"
      >
        X
      </a>
      <a href={`https://wa.me/?text=${encodeURIComponent(`${title} ${url}`)}`} target="_blank" rel="noopener">
        WhatsApp
      </a>
    </div>
  );
}
