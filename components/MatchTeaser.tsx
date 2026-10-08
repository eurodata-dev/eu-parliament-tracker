import Link from "next/link";
import { seatLayout, seatRadius } from "@/lib/hemicycle";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import styles from "./MatchTeaser.module.css";

const SEATS = seatLayout(720);
const DOT = seatRadius(720);
const COLORS = ["#e5484d", "#d9a23b", "#2fb36b", "#2c3f69"];

// fake result, just for the visual
function colour(i: number, angle: number) {
  const noise = Math.sin(i * 12.9898) * 43758.5453;
  const r = noise - Math.floor(noise);
  const lean = angle / Math.PI;
  if (r < 0.12) return COLORS[3];
  if (r < 0.12 + lean * 0.55) return COLORS[2];
  if (r < 0.55 + lean * 0.3) return COLORS[1];
  return COLORS[0];
}

export default function MatchTeaser({ t }: { t: Dictionary }) {
  return (
    <section className={styles.band}>
      <div className={`container ${styles.inner}`}>
        <div className={styles.text}>
          <p className="eyebrow">{t.nav.match}</p>
          <h2>{t.match.teaserTitle}</h2>
          <p>{t.match.teaserText}</p>
          <Link href="/match" className="button">
            {t.match.teaserCta} →
          </Link>
        </div>
        <Link href="/match" className={styles.chart} aria-label={t.match.teaserCta}>
          <svg viewBox="-1.04 -1.04 2.08 1.1" aria-hidden="true">
            {SEATS.map((p, i) => (
              <circle
                key={i}
                cx={p.x.toFixed(4)}
                cy={(-p.y).toFixed(4)}
                r={DOT.toFixed(4)}
                fill={colour(i, p.angle)}
              />
            ))}
          </svg>
        </Link>
      </div>
    </section>
  );
}
