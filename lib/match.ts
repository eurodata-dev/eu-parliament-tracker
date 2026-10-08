import "server-only";
import { unstable_cache } from "next/cache";
import { currentMembers, getVotes, latestVotes, photoUrl } from "./htv";
import type { Position, VoteDetail } from "./types";

export const QUESTIONS = 10;

// 1 char per vote to keep the payload small
const CODE: Record<Position, string> = { FOR: "F", AGAINST: "A", ABSTENTION: "B", DID_NOT_VOTE: "." };

export interface MatchQuestion {
  id: string;
  title: string;
  date: string;
  topic: string | null;
  summary: string | null;
  adopted: boolean;
  for: number;
  against: number;
}

export interface MatchMember {
  id: number;
  name: string;
  group: string;
  groupLabel: string;
  country: string;
  countryLabel: string;
  photo: string | null;
  votes: string;
}

export interface MatchData {
  questions: MatchQuestion[];
  members: MatchMember[];
}

function firstSentences(html: string, max = 240) {
  const text = html
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  const stop = cut.lastIndexOf(". ");
  return stop > 80 ? cut.slice(0, stop + 1) : `${cut.slice(0, cut.lastIndexOf(" "))}…`;
}

// close votes only, a unanimous vote tells you nothing
function pick(votes: VoteDetail[], minSide: number) {
  const seen = new Set<string>();
  const perTopic = new Map<string, number>();
  const ranked = votes
    .filter((v) => !v.amendment_subject && v.stats.total.FOR + v.stats.total.AGAINST >= 450)
    .filter((v) => Math.min(v.stats.total.FOR, v.stats.total.AGAINST) >= minSide)
    .map((v) => {
      const { FOR, AGAINST } = v.stats.total;
      return { v, score: 1 - Math.abs(FOR - AGAINST) / (FOR + AGAINST) };
    })
    .sort((a, b) => b.score - a.score);

  const chosen: VoteDetail[] = [];
  for (const { v } of ranked) {
    const key = v.display_title.toLowerCase();
    const topic = v.topics[0]?.code ?? "other";
    if (seen.has(key) || (perTopic.get(topic) ?? 0) >= 2) continue;
    seen.add(key);
    perTopic.set(topic, (perTopic.get(topic) ?? 0) + 1);
    chosen.push(v);
    if (chosen.length === QUESTIONS) break;
  }
  return chosen;
}

export const matchData = unstable_cache(
  async (): Promise<MatchData> => {
    const pages = await Promise.all([1, 2].map((p) => latestVotes(p, 100)));
    const details = await getVotes(pages.flatMap((p) => p.results).map((v) => v.id));

    let chosen = pick(details, 120);
    if (chosen.length < 6) chosen = pick(details, 40);
    chosen.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

    const positions = chosen.map((v) => new Map(v.member_votes.map((mv) => [mv.member.id, mv.position])));
    const members = (await currentMembers()).map((m) => ({
      id: m.id,
      name: `${m.first_name} ${m.last_name}`,
      group: m.group?.code ?? "NI",
      groupLabel: m.group?.short_label ?? "NI",
      country: m.country.code,
      countryLabel: m.country.label,
      photo: photoUrl(m.thumb_url ?? m.photo_url),
      votes: positions.map((p) => CODE[p.get(m.id) ?? "DID_NOT_VOTE"]).join(""),
    }));

    return {
      questions: chosen.map((v) => ({
        id: v.id,
        title: v.display_title,
        date: v.timestamp,
        topic: v.topics[0]?.code ?? null,
        summary: v.snippet?.text ? firstSentences(v.snippet.text) : null,
        adopted: v.result === "ADOPTED",
        for: v.stats.total.FOR,
        against: v.stats.total.AGAINST,
      })),
      members,
    };
  },
  ["match-data"],
  { revalidate: 12 * 60 * 60 },
);
