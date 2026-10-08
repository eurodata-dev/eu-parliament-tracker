import "server-only";
import type { Member, MemberProfile, MemberVote, Page, VoteDetail, VoteSummary } from "./types";

// data: howtheyvote.eu (official EP roll-call votes, ODbL)
const API = process.env.HTV_API_URL ?? "https://howtheyvote.eu/api";

const MINUTE = 60;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

export class NotFound extends Error {}

async function get<T>(path: string, revalidate: number): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { accept: "application/json" },
    next: { revalidate },
  });
  if (res.status === 404) throw new NotFound(path);
  if (!res.ok) throw new Error(`HowTheyVote ${res.status} on ${path}`);
  return res.json() as Promise<T>;
}

export function photoUrl(path: string | null) {
  if (!path) return null;
  return path.startsWith("http") ? path : `https://howtheyvote.eu${path}`;
}

// The topic codes HowTheyVote attaches to votes. Labels are translated in the dictionaries.
export const TOPICS = [
  "biodiversity",
  "climate-and-environment",
  "climate-change",
  "consumer-protection",
  "digital",
  "economy-and-budget",
  "education-youth-and-culture",
  "energy",
  "enlargement",
  "food-and-agriculture",
  "foreign-affairs",
  "gender-equality",
  "health",
  "international-trade",
  "migration",
  "social-protection",
  "taxation",
  "workers-rights",
] as const;

interface SearchOptions {
  q?: string;
  topic?: string;
  sort?: "date" | "relevance";
  page?: number;
  size?: number;
}

export function search({ q = "", topic, sort = "relevance", page = 1, size = 20 }: SearchOptions) {
  const params = new URLSearchParams({ page: String(page), page_size: String(size) });
  if (q) params.set("q", q);
  if (topic) params.set("topics", topic);
  if (sort === "date" || !q) params.set("sort_by", "timestamp");
  return get<Page<VoteSummary>>(`/votes/search?${params}`, q ? HOUR : 15 * MINUTE);
}

export function latestVotes(page = 1, size = 20) {
  return search({ sort: "date", page, size });
}

export function searchVotes(q: string, page = 1, size = 20) {
  return search({ q, page, size });
}

export interface ListFilters {
  q?: string;
  topic?: string;
  from?: string;
  to?: string;
  page: number;
  size?: number;
}

const SCAN = 100;

// no date filter in the API -> binary search on date-sorted pages
export async function listVotes({ q, topic, from, to, page, size = 20 }: ListFilters): Promise<Page<VoteSummary>> {
  if (!from && !to) return search({ q, topic, page, size });

  const scan = (p: number) => search({ q, topic, sort: "date", page: p, size: SCAN });
  const first = await scan(1);
  const pages = Math.max(1, Math.ceil(Math.min(first.total, 500) / SCAN));
  const day = (v: VoteSummary) => v.timestamp.slice(0, 10);

  let start = 1;
  if (to && first.results.length && day(first.results[first.results.length - 1]) > to) {
    let lo = 2;
    let hi = pages;
    start = pages;
    while (lo <= hi) {
      const mid = Math.floor((lo + hi) / 2);
      const res = await scan(mid);
      const last = res.results[res.results.length - 1];
      if (last && day(last) <= to) {
        start = mid;
        hi = mid - 1;
      } else {
        lo = mid + 1;
      }
    }
  }

  const wanted = page * size + 1;
  const matches: VoteSummary[] = [];
  let reachedEnd = false;
  for (let p = start; p <= pages && matches.length < wanted; p++) {
    const res = p === 1 ? first : await scan(p);
    for (const vote of res.results) {
      if (to && day(vote) > to) continue;
      if (from && day(vote) < from) {
        reachedEnd = true;
        break;
      }
      matches.push(vote);
    }
    if (reachedEnd || !res.has_next) break;
  }

  const results = matches.slice((page - 1) * size, page * size);
  return {
    total: matches.length,
    page,
    page_size: size,
    has_prev: page > 1,
    has_next: matches.length > page * size,
    results,
  };
}

// a vote never changes after it's held
export async function getVote(id: string) {
  if (!/^\d+$/.test(id)) throw new NotFound(id);
  return get<VoteDetail>(`/votes/${id}`, 7 * DAY);
}

export async function getVotes(ids: string[], concurrency = 8) {
  const out: (VoteDetail | null)[] = new Array(ids.length).fill(null);
  let next = 0;
  async function worker() {
    while (next < ids.length) {
      const i = next++;
      out[i] = await getVote(ids[i]).catch(() => null);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, ids.length) }, worker));
  return out.filter((v): v is VoteDetail => v !== null);
}

export async function getMember(id: string) {
  if (!/^\d+$/.test(id)) throw new NotFound(id);
  return get<MemberProfile>(`/members/${id}`, DAY);
}

export function memberVotes(id: string, page = 1, size = 50) {
  return get<Page<MemberVote>>(`/members/${id}/votes?page=${page}&page_size=${size}`, HOUR);
}

// no MEP list endpoint, so take them from the latest roll-call
export async function currentMembers(): Promise<Member[]> {
  const { results } = await latestVotes(1, 1);
  if (!results.length) return [];
  const vote = await getVote(results[0].id);
  return vote.member_votes
    .map((mv) => mv.member)
    .sort((a, b) => a.last_name.localeCompare(b.last_name));
}
