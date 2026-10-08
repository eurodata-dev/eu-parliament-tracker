import "server-only";
import { unstable_cache } from "next/cache";
import type { Locale } from "./i18n/config";
import { topicOverview, trends } from "./analysis";
import { getMember, getVote, getVotes, memberVotes } from "./htv";
import type { VoteDetail } from "./types";

const BASE_URL = process.env.GROQ_BASE_URL ?? "https://api.groq.com/openai/v1";
const MODEL = process.env.GROQ_MODEL ?? "openai/gpt-oss-120b";
const FAST_MODEL = process.env.GROQ_FAST_MODEL ?? "openai/gpt-oss-20b";
// each model has its own quota
const EXTRA_MODELS = (process.env.GROQ_EXTRA_MODELS ?? "qwen/qwen3.8-27b").split(",").filter(Boolean);

const LANGUAGE: Record<Locale, string> = {
  en: "English",
  fr: "French",
  de: "German",
  nl: "Dutch",
  es: "Spanish",
  it: "Italian",
};

export function aiEnabled() {
  return Boolean(process.env.GROQ_API_KEY);
}

type Message = { role: "system" | "user" | "assistant"; content: string };

interface CompletionOptions {
  model?: string;
  maxTokens?: number;
  json?: boolean;
  stream?: boolean;
}

async function request(messages: Message[], opts: CompletionOptions, model: string) {
  return fetch(`${BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${process.env.GROQ_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages,
      temperature: 0.5,
      max_completion_tokens: opts.maxTokens ?? 900,
      // gpt-oss and qwen don't take the same reasoning params
      ...(model.startsWith("openai/gpt-oss")
        ? { reasoning_effort: "low", include_reasoning: false }
        : { reasoning_effort: "none", reasoning_format: "hidden" }),
      stream: opts.stream ?? false,
      ...(opts.json ? { response_format: { type: "json_object" } } : {}),
    }),
    cache: "no-store",
  });
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// free tier = ~8k tokens/min per model. on 429 wait if retry-after is short, then try the next model
async function call(messages: Message[], opts: CompletionOptions = {}) {
  if (!aiEnabled()) throw new Error("GROQ_API_KEY is not set");
  const models = [...new Set([opts.model ?? MODEL, FAST_MODEL, ...EXTRA_MODELS])];
  let last = "";
  for (const model of models) {
    for (let attempt = 0; attempt < 2; attempt++) {
      const res = await request(messages, opts, model);
      if (res.ok) return res;
      last = `Groq ${res.status} (${model}): ${(await res.text()).slice(0, 200)}`;
      const wait = Number(res.headers.get("retry-after")) || 0;
      if (res.status === 429 && attempt === 0 && wait > 0 && wait <= 8) {
        await sleep(wait * 1000 + 250);
        continue;
      }
      break;
    }
  }
  throw new Error(last);
}

export async function complete(messages: Message[], opts: CompletionOptions = {}) {
  const res = await call(messages, opts);
  const data = await res.json();
  const text: string = data.choices?.[0]?.message?.content ?? "";
  if (!text.trim()) throw new Error("Empty completion");
  return text.trim();
}

export async function* completeStream(messages: Message[], opts: CompletionOptions = {}) {
  const res = await call(messages, { ...opts, stream: true });
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data:")) continue;
      const payload = line.slice(5).trim();
      if (payload === "[DONE]") return;
      try {
        const delta = JSON.parse(payload).choices?.[0]?.delta?.content;
        if (delta) yield delta as string;
      } catch {
        // partial or keep-alive line, ignore
      }
    }
  }
}

const PROCEDURES: Record<string, string> = {
  COD: "ordinary legislative procedure: this becomes binding EU law once the Council agrees too",
  CNS: "consultation procedure: the Parliament gives its opinion, the Council decides",
  APP: "consent procedure: the Parliament can only accept or reject the text as a whole",
  NLE: "non-legislative procedure, often approving an international agreement",
  INI: "own-initiative report: a non-binding position of the Parliament",
  RSP: "resolution on a topical subject: a non-binding political statement",
  BUD: "budgetary procedure",
  DEC: "budget discharge procedure",
  RPS: "objection to or approval of a Commission implementing measure",
  IMM: "decision on a member's parliamentary immunity",
};

function stripHtml(html: string) {
  return html
    .replace(/<li>/g, "- ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function tally(t: { FOR: number; AGAINST: number; ABSTENTION: number; DID_NOT_VOTE: number }) {
  return `${t.FOR} for, ${t.AGAINST} against, ${t.ABSTENTION} abstained, ${t.DID_NOT_VOTE} did not vote`;
}

// keep prompts short, TPM limit on free tier
function short(text: string, max: number) {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

export function describeVote(vote: VoteDetail, withGroups = true) {
  const lines = [
    `Title: ${short(vote.display_title, 200)}`,
    `Date: ${vote.timestamp.slice(0, 10)}`,
    vote.description && `What was put to the vote: ${vote.description}`,
    vote.amendment_subject && `Amendment: ${vote.amendment_subject}`,
    vote.procedure &&
      `Procedure: ${vote.procedure.reference} (${PROCEDURES[vote.procedure.type] ?? vote.procedure.type})`,
    vote.responsible_committees.length &&
      `Committee: ${vote.responsible_committees.map((c) => c.label).join(", ")}`,
    vote.topics.length && `Topics: ${vote.topics.map((t) => t.label).join(", ")}`,
    vote.geo_areas.length && `Countries concerned: ${vote.geo_areas.map((g) => g.label).join(", ")}`,
    `Result: ${vote.result ?? "unknown"}`,
    `Totals: ${tally(vote.stats.total)}`,
  ];
  if (withGroups) {
    lines.push(
      "By group (for/against/abstained/absent):",
      ...vote.stats.by_group.map(
        (g) => `- ${g.group.short_label}: ${g.stats.FOR}/${g.stats.AGAINST}/${g.stats.ABSTENTION}/${g.stats.DID_NOT_VOTE}`,
      ),
    );
  }
  if (vote.snippet?.text) {
    lines.push(`Press release key points: ${short(stripHtml(vote.snippet.text), 500)}`);
  }
  return lines.filter(Boolean).join("\n");
}

const VOICE = `You explain what happens in the European Parliament to people who don't follow politics closely. Write the way you'd explain it to a friend over a drink: relaxed, clear, a little personality, no jargon (or explain it in passing if you have to use it). But every fact must come from the record you are given.

Hard rules:
- Strictly neutral. Never say whether an outcome is good or bad, never guess at motives, never take a side.
- Do not invent anything that is not in the record: no quotes, no names, no figures, no background you aren't given.
- Plain text only: no headings, no bullet points, no markdown, no emojis, no em dashes.
- Use the groups' short names (EPP, S&D, Renew, Greens/EFA, ECR, PfE, The Left, ESN) and say "non-attached members" for NI.`;

export const explainVote = unstable_cache(
  async (id: string, locale: Locale) => {
    const vote = await getVote(id);
    return complete([
      { role: "system", content: VOICE },
      {
        role: "user",
        content: `Here is the record of a vote:

${describeVote(vote)}

Explain this vote in ${LANGUAGE[locale]}, in 110 to 170 words, as 2 or 3 short paragraphs separated by a blank line.
- Open with what it is actually about in everyday terms. Don't start with "The European Parliament voted".
- Say whether it passed and how comfortably, using the numbers.
- Say which groups backed it and which resisted.
- If the procedure is non-binding, say plainly that this is the Parliament's position, not a law. If it is binding legislation, say that too.
- Keep official titles short; you may paraphrase them.`,
      },
    ]);
  },
  ["vote-explainer-v1"],
  { revalidate: false, tags: ["ai"] },
);

export const weeklyBriefing = unstable_cache(
  async (session: string, ids: string[], locale: Locale) => {
    const votes = await Promise.all(ids.map(getVote));
    return complete(
      [
        { role: "system", content: VOICE },
        {
          role: "user",
          content: `These are the main roll-call votes from the European Parliament's plenary session ending ${session}:

${votes.map((v, i) => `[${i + 1}]\n${describeVote(v, false)}`).join("\n\n")}

Write "the week in Parliament" in ${LANGUAGE[locale]}: 120 to 180 words, 2 or 3 short paragraphs separated by a blank line.
Pick the three or four votes an ordinary person would care most about, or the ones that were closest, and say in a sentence or two what was decided and how clear the result was. Don't list everything. Don't use the bracketed numbers in your text. No intro like "This week the Parliament...", get straight into it.`,
        },
      ],
      { maxTokens: 1200 },
    );
  },
  ["weekly-briefing-v1"],
  { revalidate: 6 * 3600, tags: ["ai"] },
);

export const describeMember = unstable_cache(
  async (id: string, locale: Locale) => {
    const [member, { results: votes }] = await Promise.all([getMember(id), memberVotes(id, 1, 100)]);
    const counts = { FOR: 0, AGAINST: 0, ABSTENTION: 0, DID_NOT_VOTE: 0 };
    votes.forEach((v) => counts[v.position]++);
    const list = votes
      .filter((v) => v.position !== "DID_NOT_VOTE")
      .slice(0, 40)
      .map((v) => `- ${v.position === "ABSTENTION" ? "ABSTAINED" : v.position}: ${v.display_title}`)
      .join("\n");

    return complete([
      { role: "system", content: VOICE },
      {
        role: "user",
        content: `MEP: ${member.full_name}
Country: ${member.country.label}
Political group: ${member.group?.label ?? "non-attached"}
National party: ${member.national_party?.label ?? "unknown"}

Their positions in the last ${votes.length} plenary votes: ${tally(counts)}.
Votes they took part in, most recent first:
${list}

In ${LANGUAGE[locale]}, write 70 to 110 words describing how this MEP has been voting lately: which kinds of measures they tend to support, which they tend to oppose or abstain on, and their attendance stated as a plain fact. One or two short paragraphs. Describe patterns only, don't evaluate them, and don't claim anything about their opinions beyond what the votes show.`,
      },
    ]);
  },
  ["member-profile-v1"],
  { revalidate: 24 * 3600, tags: ["ai"] },
);

export async function searchTerms(question: string): Promise<string[]> {
  // short question = already a search query
  if (question.trim().split(/\s+/).length <= 4) return [question.trim()];
  try {
    const raw = await complete(
      [
        {
          role: "user",
          content: `A user asks about European Parliament votes: "${question}"

Give up to 3 short search queries (1 to 3 words each, in English, matching how EU legislation is titled) that would find the relevant votes in a keyword search. Return JSON: {"queries": ["..."]}`,
        },
      ],
      { model: FAST_MODEL, json: true, maxTokens: 300 },
    );
    const queries = JSON.parse(raw).queries;
    if (Array.isArray(queries) && queries.length) {
      return queries.filter((q): q is string => typeof q === "string" && q.trim().length > 1).slice(0, 3);
    }
  } catch {
    // fall through to the plain keyword version
  }
  return [keywords(question)];
}

const STOPWORDS = new Set(
  "a an the of on in to for and or how did does do what which who was were is are has have about vote voted votes mep meps parliament european eu groups group".split(
    " ",
  ),
);

function keywords(question: string) {
  return question
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s-]/gu, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2 && !STOPWORDS.has(w))
    .slice(0, 4)
    .join(" ");
}

export function answerStream(question: string, votes: VoteDetail[], locale: Locale) {
  return completeStream(
    [
      { role: "system", content: VOICE },
      {
        role: "user",
        content: `Someone asked: "${question}"

The only information you have is these vote records, numbered:

${votes.map((v, i) => `[${i + 1}]\n${describeVote(v, i < 3)}`).join("\n\n")}

Answer in ${LANGUAGE[locale]}, in 80 to 200 words, in short paragraphs separated by a blank line.
- Base everything on the records above and cite them inline like [1] or [2].
- If several votes are relevant, connect them in a sentence or two instead of describing each one.
- If the records don't actually answer the question, say so honestly in one or two sentences and mention the closest thing you found.`,
      },
    ],
    { maxTokens: 1200 },
  );
}

export const explainTopic = unstable_cache(
  async (q: string, topic: string, locale: Locale) => {
    const overview = await topicOverview(q, topic);
    if (!overview) throw new Error("no votes for topic");
    const votes = await getVotes(overview.ids.slice(0, 12));
    const groups = overview.groups
      .map((g) => `- ${g.group.short_label}: ${tally(g.tally)} (summed over ${g.votes} votes)`)
      .join("\n");

    return complete(
      [
        { role: "system", content: VOICE },
        {
          role: "user",
          content: `Someone searched for "${[q, topic].filter(Boolean).join(" / ")}". These are the ${overview.count} most relevant plenary votes (${overview.adopted} adopted, ${overview.rejected} rejected), between ${overview.first?.slice(0, 10)} and ${overview.last?.slice(0, 10)}.

Summed over all of them, the political groups voted like this:
${groups}

The most relevant votes:
${votes.map((v, i) => `[${i + 1}]\n${describeVote(v, false)}`).join("\n\n")}

In ${LANGUAGE[locale]}, in 130 to 190 words and 2 or 3 short paragraphs separated by a blank line, explain what the Parliament has been deciding on this subject: the main things that were voted on, how consistent the outcomes were, and which groups usually supported or opposed. Mention concrete votes in passing, without the bracketed numbers. Stay descriptive.`,
        },
      ],
      { maxTokens: 1200 },
    );
  },
  ["topic-explainer-v1"],
  { revalidate: 24 * 3600, tags: ["ai"] },
);

export const explainTrends = unstable_cache(
  async (key: string, locale: Locale) => {
    const data = await trends();
    if (!data) throw new Error("no trend data");
    const groups = data.groups
      .map(
        (g) =>
          `- ${g.group.short_label}: for ${g.before.FOR}% -> ${g.after.FOR}%, against ${g.before.AGAINST}% -> ${g.after.AGAINST}%, abstained ${g.before.ABSTENTION}% -> ${g.after.ABSTENTION}%`,
      )
      .join("\n");
    const topics = data.topics
      .slice(0, 6)
      .map((t) => `- ${t.label}: support ${t.before}% -> ${t.after}% (${t.votes} recent votes)`)
      .join("\n");

    return complete([
      { role: "system", content: VOICE },
      {
        role: "user",
        content: `Comparison of European Parliament roll-call votes: the last 30 days (${data.recentCount} votes, ${data.recentFrom} to ${data.recentTo}) against the ${data.baselineCount} votes before that (${data.baselineFrom} to ${data.baselineTo}). Shares are of votes cast.

By group:
${groups}

By topic, share of all MEPs voting for:
${topics}

Polarization (average distance of each group's "for" share from 50%): ${data.polarizationBefore} -> ${data.polarizationAfter}.

In ${LANGUAGE[locale]}, in 110 to 160 words and 2 short paragraphs separated by a blank line, explain what changed: which group shifted most and in which direction, which topics saw support move, and whether groups are drifting apart or closer. Point out that a different mix of subjects on the agenda explains a lot of this, so these are shifts in recorded votes, not necessarily changes of opinion.`,
      },
    ]);
  },
  ["trends-explainer-v1"],
  { revalidate: 12 * 3600, tags: ["ai"] },
);
