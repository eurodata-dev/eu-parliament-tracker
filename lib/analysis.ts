import "server-only";
import { unstable_cache } from "next/cache";
import { byHemicycle } from "./groups";
import { getVotes, latestVotes, search } from "./htv";
import type { Group, Tally, VoteDetail } from "./types";
import { cast } from "./votes";

const empty = (): Tally => ({ FOR: 0, AGAINST: 0, ABSTENTION: 0, DID_NOT_VOTE: 0 });

function add(into: Tally, t: Tally) {
  into.FOR += t.FOR;
  into.AGAINST += t.AGAINST;
  into.ABSTENTION += t.ABSTENTION;
  into.DID_NOT_VOTE += t.DID_NOT_VOTE;
}

export function shares(t: Tally) {
  const total = cast(t) || 1;
  const pct = (n: number) => Math.round((n / total) * 1000) / 10;
  return { FOR: pct(t.FOR), AGAINST: pct(t.AGAINST), ABSTENTION: pct(t.ABSTENTION) };
}

export interface GroupAggregate {
  group: Group;
  tally: Tally;
  votes: number;
}

export function aggregateGroups(votes: VoteDetail[]): GroupAggregate[] {
  const map = new Map<string, GroupAggregate>();
  for (const vote of votes) {
    for (const { group, stats } of vote.stats.by_group) {
      const entry = map.get(group.code) ?? { group, tally: empty(), votes: 0 };
      add(entry.tally, stats);
      entry.votes++;
      map.set(group.code, entry);
    }
  }
  return byHemicycle([...map.values()], (g) => g.group.code);
}

export function aggregateTotal(votes: VoteDetail[]) {
  const total = empty();
  votes.forEach((v) => add(total, v.stats.total));
  return total;
}

export interface TopicOverview {
  count: number;
  adopted: number;
  rejected: number;
  first: string | null;
  last: string | null;
  total: Tally;
  groups: GroupAggregate[];
  ids: string[];
}

const OVERVIEW_SIZE = 20;

export const topicOverview = unstable_cache(
  async (q: string, topic: string): Promise<TopicOverview | null> => {
    const { results } = await search({ q, topic: topic || undefined, size: OVERVIEW_SIZE });
    if (!results.length) return null;
    const votes = await getVotes(results.map((v) => v.id));
    if (!votes.length) return null;
    const dates = votes.map((v) => v.timestamp).sort();
    return {
      count: votes.length,
      adopted: votes.filter((v) => v.result === "ADOPTED").length,
      rejected: votes.filter((v) => v.result === "REJECTED").length,
      first: dates[0] ?? null,
      last: dates[dates.length - 1] ?? null,
      total: aggregateTotal(votes),
      groups: aggregateGroups(votes),
      ids: votes.map((v) => v.id),
    };
  },
  ["topic-overview-v1"],
  { revalidate: 6 * 3600 },
);

// trends: last 30 days vs the votes before

const RECENT_DAYS = 30;
const BASELINE_SIZE = 120;
const MAX_RECENT = 80;

export interface GroupDrift {
  group: Group;
  before: ReturnType<typeof shares>;
  after: ReturnType<typeof shares>;
  delta: ReturnType<typeof shares>;
  change: number;
}

export interface TopicDrift {
  code: string;
  label: string;
  before: number;
  after: number;
  delta: number;
  votes: number;
}

export interface Trends {
  recentFrom: string;
  recentTo: string;
  baselineFrom: string;
  baselineTo: string;
  recentCount: number;
  baselineCount: number;
  groups: GroupDrift[];
  topics: TopicDrift[];
  polarizationBefore: number;
  polarizationAfter: number;
  mostChangedGroup: GroupDrift | null;
  mostChangedTopic: TopicDrift | null;
}

// avg distance of each group's FOR share from 50%
function polarization(groups: GroupAggregate[]) {
  const values = groups.filter((g) => cast(g.tally) > 0).map((g) => Math.abs(shares(g.tally).FOR - 50));
  if (!values.length) return 0;
  return Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 10) / 10;
}

function topicShares(votes: VoteDetail[]) {
  const map = new Map<string, { label: string; tally: Tally; votes: number }>();
  for (const vote of votes) {
    for (const topic of vote.topics) {
      const entry = map.get(topic.code) ?? { label: topic.label, tally: empty(), votes: 0 };
      add(entry.tally, vote.stats.total);
      entry.votes++;
      map.set(topic.code, entry);
    }
  }
  return map;
}

async function collectIds() {
  const pages = await Promise.all([1, 2, 3].map((p) => latestVotes(p, 100)));
  const all = pages.flatMap((p) => p.results);
  if (!all.length) return null;
  const latest = new Date(all[0].timestamp).getTime();
  const cutoff = latest - RECENT_DAYS * 24 * 3600 * 1000;
  const recent = all.filter((v) => new Date(v.timestamp).getTime() >= cutoff).slice(0, MAX_RECENT);
  const baseline = all.filter((v) => new Date(v.timestamp).getTime() < cutoff).slice(0, BASELINE_SIZE);
  return { recent, baseline };
}

export const trends = unstable_cache(
  async (): Promise<Trends | null> => {
    const ids = await collectIds();
    if (!ids || !ids.recent.length || !ids.baseline.length) return null;

    const [recent, baseline] = await Promise.all([
      getVotes(ids.recent.map((v) => v.id)),
      getVotes(ids.baseline.map((v) => v.id)),
    ]);
    if (!recent.length || !baseline.length) return null;

    const before = aggregateGroups(baseline);
    const after = aggregateGroups(recent);
    const groups: GroupDrift[] = after
      .map((a) => {
        const b = before.find((x) => x.group.code === a.group.code);
        if (!b) return null;
        const sb = shares(b.tally);
        const sa = shares(a.tally);
        const delta = {
          FOR: Math.round((sa.FOR - sb.FOR) * 10) / 10,
          AGAINST: Math.round((sa.AGAINST - sb.AGAINST) * 10) / 10,
          ABSTENTION: Math.round((sa.ABSTENTION - sb.ABSTENTION) * 10) / 10,
        };
        const change = Math.round((Math.abs(delta.FOR) + Math.abs(delta.AGAINST) + Math.abs(delta.ABSTENTION)) * 10) / 10;
        return { group: a.group, before: sb, after: sa, delta, change };
      })
      .filter((g): g is GroupDrift => g !== null);

    const tb = topicShares(baseline);
    const ta = topicShares(recent);
    const topics: TopicDrift[] = [...ta.entries()]
      .filter(([code, a]) => tb.has(code) && a.votes >= 2 && tb.get(code)!.votes >= 2)
      .map(([code, a]) => {
        const b = tb.get(code)!;
        const sb = shares(b.tally).FOR;
        const sa = shares(a.tally).FOR;
        return { code, label: a.label, before: sb, after: sa, delta: Math.round((sa - sb) * 10) / 10, votes: a.votes };
      })
      .sort((x, y) => Math.abs(y.delta) - Math.abs(x.delta));

    const day = (v: VoteDetail) => v.timestamp.slice(0, 10);
    const sortedRecent = recent.map(day).sort();
    const sortedBase = baseline.map(day).sort();

    return {
      recentFrom: sortedRecent[0],
      recentTo: sortedRecent[sortedRecent.length - 1],
      baselineFrom: sortedBase[0],
      baselineTo: sortedBase[sortedBase.length - 1],
      recentCount: recent.length,
      baselineCount: baseline.length,
      groups,
      topics,
      polarizationBefore: polarization(before),
      polarizationAfter: polarization(after),
      mostChangedGroup: [...groups].sort((a, b) => b.change - a.change)[0] ?? null,
      mostChangedTopic: topics[0] ?? null,
    };
  },
  ["trends-v1"],
  { revalidate: 12 * 3600 },
);
