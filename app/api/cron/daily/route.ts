import { digestContent, digestHtml, digestSubject, isFresh, localeOf } from "@/lib/digest";
import { mailEnabled, sendMail, unsubscribeUrl } from "@/lib/mail";
import { listSubscribers, markDigestSent, pingDatabase, subscribersEnabled } from "@/lib/subscribers";

export const maxDuration = 60;

// vercel cron, daily. pings supabase + sends the digest on mondays (?send=1 to force)
export async function GET(req: Request) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) {
    return new Response("unauthorized", { status: 401 });
  }
  if (!subscribersEnabled()) return Response.json({ ok: false, reason: "no database" });

  const report: Record<string, unknown> = { database: await pingDatabase().catch(() => "error") };

  const force = new URL(req.url).searchParams.get("send") === "1";
  const monday = new Date().getUTCDay() === 1;
  if (!(monday || force)) return Response.json({ ok: true, ...report, digest: "not today" });
  if (!mailEnabled()) return Response.json({ ok: false, ...report, digest: "no RESEND_API_KEY" });

  const content = await digestContent();
  if (!content || (!force && !isFresh(content))) {
    return Response.json({ ok: true, ...report, digest: "no new session" });
  }

  // ?send=1&to=me@example.com sends a test to one address only
  const testTo = new URL(req.url).searchParams.get("to");
  const subscribers = testTo ? [{ email: testTo, language: "FR" }] : await listSubscribers();
  let sent = 0;
  const failed: string[] = [];

  for (const sub of subscribers) {
    if (!sub.email) continue;
    const locale = localeOf(sub.language);
    try {
      await sendMail({
        to: sub.email,
        subject: digestSubject(content, locale),
        html: await digestHtml(content, locale, sub.email),
        headers: {
          "List-Unsubscribe": `<${unsubscribeUrl(sub.email, true)}>`,
          "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
      });
      sent++;
    } catch (err) {
      console.error("digest failed for a subscriber", err);
      failed.push(sub.email);
    }
    // Resend allows a couple of requests per second on the free plan.
    await new Promise((r) => setTimeout(r, 600));
  }

  if (sent && !testTo) await markDigestSent();
  return Response.json({ ok: true, ...report, digest: { sent, failed: failed.length, total: subscribers.length } });
}
