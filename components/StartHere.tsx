import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import CountryPicker from "./CountryPicker";
import styles from "./StartHere.module.css";

function Icon({ kind }: { kind: "week" | "people" | "topics" }) {
  const common = { width: 28, height: 28, viewBox: "0 0 28 28", fill: "none", stroke: "currentColor", strokeWidth: 1.6 };
  if (kind === "week") {
    return (
      <svg {...common} aria-hidden="true">
        <path d="M3 22a11 11 0 0 1 22 0" />
        <path d="M8 22a6 6 0 0 1 12 0" />
        <path d="M14 11v-4M5.6 14.6 2.8 11.8M22.4 14.6l2.8-2.8" />
      </svg>
    );
  }
  if (kind === "people") {
    return (
      <svg {...common} aria-hidden="true">
        <circle cx="10" cy="9" r="4" />
        <path d="M2.5 24c.6-4.4 3.8-7 7.5-7s6.9 2.6 7.5 7" />
        <circle cx="20" cy="10" r="3" />
        <path d="M19 17.2c3.4.1 6 2.4 6.5 6.8" />
      </svg>
    );
  }
  return (
    <svg {...common} aria-hidden="true">
      <rect x="3" y="3" width="9" height="9" />
      <rect x="16" y="3" width="9" height="9" />
      <rect x="3" y="16" width="9" height="9" />
      <rect x="16" y="16" width="9" height="9" />
    </svg>
  );
}

export default function StartHere({
  t,
  countries,
}: {
  t: Dictionary;
  countries: { code: string; label: string }[];
}) {
  return (
    <section className={`container ${styles.wrap}`}>
      <h2 className="eyebrow">{t.home.startTitle}</h2>
      <div className={styles.cards}>
        <a href="#week" className={styles.card}>
          <Icon kind="week" />
          <h3>{t.home.startWeek}</h3>
          <p>{t.home.startWeekText}</p>
          <span className={styles.go}>→</span>
        </a>
        <div className={styles.card}>
          <Icon kind="people" />
          <h3>{t.home.startMeps}</h3>
          <p>{t.home.startMepsText}</p>
          <CountryPicker countries={countries} label={t.home.pickCountry} />
        </div>
        <a href="#topics" className={styles.card}>
          <Icon kind="topics" />
          <h3>{t.home.startTopics}</h3>
          <p>{t.home.startTopicsText}</p>
          <span className={styles.go}>→</span>
        </a>
      </div>
    </section>
  );
}
