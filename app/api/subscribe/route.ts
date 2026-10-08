import { isLocale } from "@/lib/i18n/config";
import { allow, clientKey } from "@/lib/rate-limit";
import { addSubscriber, subscribersEnabled } from "@/lib/subscribers";

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export async function POST(req: Request) {
  if (!allow(clientKey(req), 5, 10 * 60_000)) return Response.json({ ok: false }, { status: 429 });

  const body = await req.json().catch(() => null);
  const email = typeof body?.email === "string" ? body.email.trim().toLowerCase() : "";
  if (!EMAIL.test(email) || email.length > 200) return Response.json({ ok: false }, { status: 400 });
  if (!subscribersEnabled()) return Response.json({ ok: false }, { status: 503 });

  // stored upper case (EN, FR...), that is what the digest expects
  const language = (isLocale(body?.language) ? body.language : "en").toUpperCase();

  try {
    await addSubscriber(email, language);
    return Response.json({ ok: true });
  } catch (err) {
    console.error("subscribe failed", err);
    return Response.json({ ok: false }, { status: 502 });
  }
}
