import { aiEnabled, describeMember, explainTopic, explainTrends, explainVote } from "@/lib/ai";
import { getLocale } from "@/lib/i18n/server";
import { allow, clientKey } from "@/lib/rate-limit";

export const maxDuration = 60;

// called by the "generate" button. results are cached so only the first click costs a call
export async function GET(req: Request) {
  if (!aiEnabled()) return Response.json({ ok: false }, { status: 503 });
  if (!allow(clientKey(req), 12, 60_000)) return Response.json({ ok: false }, { status: 429 });

  const params = new URL(req.url).searchParams;
  const kind = params.get("kind");
  const id = params.get("id") ?? "";
  const locale = await getLocale();

  try {
    let text: string;
    if (kind === "vote" && /^\d+$/.test(id)) text = await explainVote(id, locale);
    else if (kind === "member" && /^\d+$/.test(id)) text = await describeMember(id, locale);
    else if (kind === "topic") text = await explainTopic(params.get("q") ?? "", params.get("topic") ?? "", locale);
    else if (kind === "trends") text = await explainTrends(id, locale);
    else return Response.json({ ok: false }, { status: 400 });
    return Response.json({ ok: true, text });
  } catch (err) {
    console.error(`summary failed (${kind})`, err);
    return Response.json({ ok: false }, { status: 502 });
  }
}
