import { aiEnabled, answerStream, searchTerms } from "@/lib/ai";
import { getVote, searchVotes } from "@/lib/htv";
import { getLocale } from "@/lib/i18n/server";
import { allow, clientKey } from "@/lib/rate-limit";
import type { Locale } from "@/lib/i18n/config";
import type { VoteSummary } from "@/lib/types";

export const maxDuration = 60;

const MAX_SOURCES = 5;

// questions that ask for a judgement on someone get a fixed answer, the model is never asked
const JUDGEMENT =
  /\b(negati\w*|n[ée]gati\w*|bad|worst|evil|liar|racist\w*|fascis\w*|nazi\w*|criticis\w*|criticiz\w*|mauvais\w*|pire|menteur\w*|raciste\w*|schlecht\w*|schlimmst\w*|l[üu]gner\w*|slecht\w*|leugenaar\w*|malo|mala|peor|mentiroso|cattiv\w*|peggior\w*|bugiard\w*)\b/i;

const NEUTRAL: Record<Locale, string> = {
  en: "EU Parliament Tracker doesn't judge MEPs, parties or groups. It only shows how they voted, with the official numbers. Look up an MEP on the MEPs page to see their full voting record and make up your own mind.",
  fr: "EU Parliament Tracker ne porte aucun jugement sur les députés, les partis ou les groupes. Le site montre uniquement comment ils ont voté, avec les chiffres officiels. Cherchez un député sur la page Députés pour voir tous ses votes et vous faire votre propre avis.",
  de: "EU Parliament Tracker bewertet keine Abgeordneten, Parteien oder Fraktionen. Die Seite zeigt nur, wie sie abgestimmt haben, mit den offiziellen Zahlen. Auf der Seite Abgeordnete finden Sie das gesamte Abstimmungsverhalten und können sich selbst ein Bild machen.",
  nl: "EU Parliament Tracker oordeelt niet over Europarlementariërs, partijen of fracties. De site toont alleen hoe ze gestemd hebben, met de officiële cijfers. Zoek een Europarlementariër op de pagina Europarlementariërs om al zijn of haar stemmen te zien en vorm zelf een mening.",
  es: "EU Parliament Tracker no juzga a eurodiputados, partidos ni grupos. Solo muestra cómo han votado, con las cifras oficiales. Busca a un eurodiputado en la página Eurodiputados para ver todos sus votos y sacar tus propias conclusiones.",
  it: "EU Parliament Tracker non giudica eurodeputati, partiti o gruppi. Mostra solo come hanno votato, con i numeri ufficiali. Cerca un eurodeputato nella pagina Eurodeputati per vedere tutti i suoi voti e farti la tua idea.",
};

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
      if (JUDGEMENT.test(question)) {
        send(controller, { type: "text", value: NEUTRAL[locale] });
        return controller.close();
      }
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
