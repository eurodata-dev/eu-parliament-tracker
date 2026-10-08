import type { Tally } from "@/lib/types";
import { POSITIONS, POSITION_COLOR } from "@/lib/votes";
import styles from "./votes.module.css";

interface Props {
  tally: Tally;
  castOnly?: boolean;
  height?: number;
  label?: string;
}

export default function TallyBar({ tally, castOnly = false, height = 6, label }: Props) {
  const parts = POSITIONS.filter((p) => !(castOnly && p === "DID_NOT_VOTE"));
  const total = parts.reduce((sum, p) => sum + tally[p], 0) || 1;
  return (
    <div className={styles.bar} style={{ height }} role="img" aria-label={label}>
      {parts.map((p) =>
        tally[p] ? (
          <span key={p} style={{ width: `${(tally[p] / total) * 100}%`, background: POSITION_COLOR[p] }} />
        ) : null,
      )}
    </div>
  );
}
