import { groupOrder } from "@/lib/groups";
import { seatLayout, seatRadius } from "@/lib/hemicycle";
import type { Position, VoteDetail } from "@/lib/types";
import { POSITION_COLOR } from "@/lib/votes";

const POS_ORDER: Record<Position, number> = { FOR: 0, ABSTENTION: 1, AGAINST: 2, DID_NOT_VOTE: 3 };

export default function Hemicycle({ vote, label }: { vote: VoteDetail; label: string }) {
  const members = [...vote.member_votes].sort(
    (a, b) =>
      groupOrder(a.member.group?.code) - groupOrder(b.member.group?.code) ||
      POS_ORDER[a.position] - POS_ORDER[b.position],
  );
  const points = seatLayout(members.length);
  const dot = seatRadius(members.length);

  return (
    <svg viewBox="-1.04 -1.04 2.08 1.1" role="img" aria-label={label} style={{ width: "100%", height: "auto", display: "block" }}>
      {points.map((p, i) => (
        <circle
          key={i}
          cx={p.x.toFixed(4)}
          cy={(-p.y).toFixed(4)}
          r={dot.toFixed(4)}
          fill={POSITION_COLOR[members[i].position]}
        />
      ))}
    </svg>
  );
}
