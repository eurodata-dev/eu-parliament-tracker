import { CONTACT_EMAIL, escapeHtml, mailEnabled, sendMail } from "@/lib/mail";
import { allow, clientKey } from "@/lib/rate-limit";

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export async function POST(req: Request) {
  if (!allow(clientKey(req), 3, 10 * 60_000)) return Response.json({ ok: false }, { status: 429 });

  const body = await req.json().catch(() => null);
  const name = typeof body?.name === "string" ? body.name.trim().slice(0, 120) : "";
  const email = typeof body?.email === "string" ? body.email.trim().slice(0, 200) : "";
  const message = typeof body?.message === "string" ? body.message.trim().slice(0, 5000) : "";
  // Hidden field that people never fill in, bots often do.
  if (body?.website) return Response.json({ ok: true });
  if (!EMAIL.test(email) || message.length < 5) return Response.json({ ok: false }, { status: 400 });
  if (!mailEnabled()) return Response.json({ ok: false }, { status: 503 });

  try {
    await sendMail({
      to: CONTACT_EMAIL,
      replyTo: email,
      subject: `[EU Parliament Tracker] Message from ${name || email}`,
      html: `<p><strong>From:</strong> ${escapeHtml(name || "(no name)")} &lt;${escapeHtml(email)}&gt;</p>
<p style="white-space:pre-wrap">${escapeHtml(message)}</p>`,
    });
    return Response.json({ ok: true });
  } catch (err) {
    console.error("contact failed", err);
    return Response.json({ ok: false }, { status: 502 });
  }
}
