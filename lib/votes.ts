import type { Position, Tally, VoteSummary } from "./types";

const DAY = 24 * 3600 * 1000;

// plenary = mon-thu, so 4 days from the latest vote = same session (newest first)
export function lastSession<T extends VoteSummary>(votes: T[]) {
  if (!votes.length) return [];
  const last = new Date(votes[0].timestamp).getTime();
  return votes.filter((v) => last - new Date(v.timestamp).getTime() < 4 * DAY);
}

export const POSITIONS: Position[] = ["FOR", "AGAINST", "ABSTENTION", "DID_NOT_VOTE"];

export const POSITION_COLOR: Record<Position, string> = {
  FOR: "var(--for)",
  AGAINST: "var(--against)",
  ABSTENTION: "var(--abstain)",
  DID_NOT_VOTE: "var(--absent)",
};

export function cast(t: Tally) {
  return t.FOR + t.AGAINST + t.ABSTENTION;
}

export function seats(t: Tally) {
  return cast(t) + t.DID_NOT_VOTE;
}

// share of cast votes on the majority side (0-1)
export function cohesion(t: Tally) {
  const total = cast(t);
  if (!total) return 0;
  return Math.max(t.FOR, t.AGAINST, t.ABSTENTION) / total;
}

export function majority(t: Tally): Position | null {
  if (!cast(t)) return null;
  const order: Position[] = ["FOR", "AGAINST", "ABSTENTION"];
  return order.reduce((best, p) => (t[p] > t[best] ? p : best), "FOR");
}

export function margin(t: Tally) {
  return t.FOR - t.AGAINST;
}
