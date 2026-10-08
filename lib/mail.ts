import "server-only";
import { createHmac, timingSafeEqual } from "node:crypto";

export const SITE_URL = process.env.SITE_URL ?? "https://euparliamenttracker.com";
const FROM = process.env.FROM_EMAIL ?? "EU Parliament Tracker <onboarding@resend.dev>";
export const CONTACT_EMAIL = process.env.CONTACT_EMAIL ?? "elmas.burhan80@gmail.com";

export function mailEnabled() {
  return Boolean(process.env.RESEND_API_KEY);
}

interface Mail {
  to: string;
  subject: string;
  html: string;
  replyTo?: string;
  headers?: Record<string, string>;
}

export async function sendMail({ to, subject, html, replyTo, headers }: Mail) {
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      authorization: `Bearer ${process.env.RESEND_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from: FROM,
      to: [to],
      subject,
      html,
      ...(replyTo ? { reply_to: replyTo } : {}),
      ...(headers ? { headers } : {}),
    }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Resend ${res.status}: ${(await res.text()).slice(0, 200)}`);
}

const ENTITIES: Record<string, string> = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

export function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, (c) => ENTITIES[c]);
}

// signed links, so nobody can unsubscribe someone else
function secret() {
  return process.env.UNSUBSCRIBE_SECRET || process.env.SUPABASE_KEY || "dev";
}

export function unsubscribeToken(email: string) {
  return createHmac("sha256", secret()).update(email.toLowerCase()).digest("base64url").slice(0, 32);
}

export function checkUnsubscribeToken(email: string, token: string) {
  const expected = Buffer.from(unsubscribeToken(email));
  const given = Buffer.from(token);
  return expected.length === given.length && timingSafeEqual(expected, given);
}

export function unsubscribeUrl(email: string, oneClick = false) {
  const params = new URLSearchParams({ email, token: unsubscribeToken(email) });
  return `${SITE_URL}${oneClick ? "/api/unsubscribe" : "/unsubscribe"}?${params}`;
}
