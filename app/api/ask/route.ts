import { aiEnabled, answerStream, searchTerms } from "@/lib/ai";
import { getVote, searchVotes } from "@/lib/htv";
import { getLocale } from "@/lib/i18n/server";
import { allow, clientKey } from "@/lib/rate-limit";
import type { VoteSummary } from "@/lib/types";

export const maxDuration = 60;

const MAX_SOURCES = 5;

export async function POST(req: Request) {
  if (!aiEnabled()) return Response.json({ error: "disabled" }, { status: 503 });
  if (!allow(clientKey(req), 8, 60_000)) return Response.json({ error: "slow down" }, { status: 429 });

  const body = await req.json().catch(() => null);
  const question = typeof body?.question === "string" ? body.question.trim().slice(0, 300) : "";
  if (question.length < 3) return Response.json({ error: "empty question" }, { status: 400 });

  const locale = await getLocale();
  const encoder = new TextEncoder();
  const send = (controller: ReadableStreamDefaultController, event: object) =>
    controller.enqueue(encoder.encode(JSON.stringify(event) + "\n"));

  const stream = new ReadableStream({
    async start(controller) {
      try {
        const terms = await searchTerms(question);
        const pages = await Promise.all(terms.map((q) => searchVotes(q, 1, 8).catch(() => null)));

        // Interleave the result lists so each search term gets a fair share.
        const seen = new Map<string, VoteSummary>();
        for (let i = 0; i < 8 && seen.size < MAX_SOURCES; i++) {
          for (const page of pages) {
            const vote = page?.results[i];
            if (vote && !seen.has(vote.id) && seen.size < MAX_SOURCES) seen.set(vote.id, vote);
          }
        }

        const votes = (await Promise.all([...seen.keys()].map((id) => getVote(id).catch(() => null)))).filter(
          (v) => v !== null,
        );
        send(controller, {
          type: "sources",
          votes: votes.map((v) => ({ id: v.id, title: v.display_title, date: v.timestamp, result: v.result })),
        });
        if (!votes.length) return controller.close();

        for await (const chunk of answerStream(question, votes, locale)) {
          send(controller, { type: "text", value: chunk });
        }
      } catch (err) {
        console.error("ask failed", err);
        send(controller, { type: "error" });
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { "content-type": "application/x-ndjson; charset=utf-8", "cache-control": "no-store" },
  });
}
