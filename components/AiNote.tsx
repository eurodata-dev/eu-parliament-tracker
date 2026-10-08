import styles from "./AiNote.module.css";

export default function AiNote({
  title,
  note,
  badge,
  children,
  wide = false,
}: {
  title: string;
  note: string;
  badge: string;
  children: React.ReactNode;
  wide?: boolean;
}) {
  return (
    <section className={`${styles.box} ${wide ? styles.wide : ""}`}>
      <header className={styles.head}>
        <span className="eyebrow">{title}</span>
        <span className={styles.badge}>{badge}</span>
      </header>
      <div className={styles.text}>{children}</div>
      <p className={styles.note}>{note}</p>
    </section>
  );
}

export function Paragraphs({ text }: { text: string }) {
  return (
    <div className="prose">
      {text
        .split(/\n\s*\n/)
        .map((p) => p.replace(/\*\*/g, "").replace(/\s*—\s*/g, ", ").trim())
        .filter(Boolean)
        .map((p, i) => (
          <p key={i}>{p}</p>
        ))}
    </div>
  );
}

export function AiSkeleton({ lines = 5 }: { lines?: number }) {
  return (
    <div className={styles.skeleton} aria-hidden="true">
      {Array.from({ length: lines }, (_, i) => (
        <span key={i} style={{ width: i === lines - 1 ? "55%" : `${92 - (i % 3) * 6}%` }} />
      ))}
    </div>
  );
}
