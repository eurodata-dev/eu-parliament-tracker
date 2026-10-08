import "server-only";
import { aiEnabled, weeklyBriefing } from "./ai";
import { formatDate } from "./format";
import { getVotes, latestVotes } from "./htv";
import { isLocale, type Locale } from "./i18n/config";
import en from "./i18n/dictionaries/en";
import fr from "./i18n/dictionaries/fr";
import de from "./i18n/dictionaries/de";
import nl from "./i18n/dictionaries/nl";
import es from "./i18n/dictionaries/es";
import it from "./i18n/dictionaries/it";
import { escapeHtml, SITE_URL, unsubscribeUrl } from "./mail";
import type { VoteDetail } from "./types";
import { cast, lastSession } from "./votes";

const dictionaries = { en, fr, de, nl, es, it };

export function localeOf(language: string | null): Locale {
  const code = (language ?? "en").toLowerCase();
  return isLocale(code) ? code : "en";
}

export interface DigestContent {
  session: string;
  votes: VoteDetail[];
}

export async function digestContent(): Promise<DigestContent | null> {
  const { results } = await latestVotes(1, 60);
  const session = lastSession(results);
  if (!session.length) return null;
  const votes = await getVotes(session.slice(0, 20).map((v) => v.id));
  votes.sort((a, b) => cast(b.stats.total) - cast(a.stats.total));
  return { session: session[0].timestamp, votes: votes.slice(0, 8) };
}

export function isFresh(content: DigestContent, days = 8) {
  return Date.now() - new Date(content.session).getTime() < days * 24 * 3600 * 1000;
}

export async function digestHtml(content: DigestContent, locale: Locale, email: string) {
  const t = dictionaries[locale];
  let briefing = "";
  if (aiEnabled()) {
    try {
      const ids = content.votes.map((v) => v.id);
      briefing = await weeklyBriefing(content.session.slice(0, 10), ids, locale);
    } catch (err) {
      console.error("digest briefing failed", err);
    }
  }

  const rows = content.votes
    .map((v) => {
      const total = v.stats.total;
      const n = cast(total) || 1;
      const pct = (x: number) => Math.round((x / n) * 100);
      const adopted = v.result === "ADOPTED";
      const color = adopted ? "#2fb36b" : "#e5484d";
      return `
<tr><td style="padding:16px 0;border-bottom:1px solid #1e3a6e">
  <a href="${SITE_URL}/votes/${v.id}" style="color:#f2f4f9;text-decoration:none;font-family:Georgia,serif;font-size:17px;line-height:1.35">${escapeHtml(v.display_title)}</a>
  <div style="margin-top:8px;font-family:Menlo,Consolas,monospace;font-size:12px;color:#8899bb">
    <span style="display:inline-block;padding:2px 7px;border:1px solid ${color};color:${color};letter-spacing:1px">${escapeHtml(adopted ? t.vote.adopted : t.vote.rejected).toUpperCase()}</span>
    &nbsp; <span style="color:#2fb36b">${pct(total.FOR)}% ${escapeHtml(t.vote.FOR)}</span>
    &nbsp;·&nbsp; <span style="color:#e5484d">${pct(total.AGAINST)}% ${escapeHtml(t.vote.AGAINST)}</span>
    &nbsp;·&nbsp; <span style="color:#d9a23b">${pct(total.ABSTENTION)}% ${escapeHtml(t.vote.ABSTENTION)}</span>
  </div>
</td></tr>`;
    })
    .join("");

  const paragraphs = briefing
    .split(/\n\s*\n/)
    .map((p) => p.replace(/\*\*/g, "").trim())
    .filter(Boolean)
    .map((p) => `<p style="margin:0 0 14px">${escapeHtml(p)}</p>`)
    .join("");

  const date = formatDate(content.session, locale, { month: "long" });
  const unsubscribe = escapeHtml(unsubscribeUrl(email));

  return `<!doctype html>
<html lang="${locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0b1531">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0b1531"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#0f1b3d;border:1px solid #1e3a6e">
<tr><td style="padding:26px 32px;border-bottom:1px solid #1e3a6e">
  <div style="font-family:Menlo,Consolas,monospace;font-size:12px;letter-spacing:3px;color:#d9a23b">EU PARLIAMENT TRACKER</div>
  <div style="margin-top:10px;font-family:Georgia,serif;font-size:26px;line-height:1.2;color:#f2f4f9">${escapeHtml(t.email.title)}</div>
  <div style="margin-top:6px;font-family:Arial,sans-serif;font-size:13px;color:#8899bb">${escapeHtml(t.home.briefingSession.replace("{date}", date))}</div>
</td></tr>
${
  paragraphs
    ? `<tr><td style="padding:24px 32px 10px;font-family:Georgia,serif;font-size:16px;line-height:1.6;color:#e1e6f0;border-left:3px solid #2563eb">${paragraphs}
<div style="font-family:Arial,sans-serif;font-size:11px;color:#56698f">${escapeHtml(t.ai.note)}</div></td></tr>`
    : `<tr><td style="padding:24px 32px 6px;font-family:Arial,sans-serif;font-size:15px;line-height:1.6;color:#c9d1e3">${escapeHtml(t.email.intro)}</td></tr>`
}
<tr><td style="padding:10px 32px 0">
  <div style="font-family:Menlo,Consolas,monospace;font-size:11px;letter-spacing:2px;color:#8899bb;padding:14px 0 4px">${escapeHtml(t.email.votesTitle).toUpperCase()}</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">${rows}</table>
</td></tr>
<tr><td style="padding:26px 32px">
  <a href="${SITE_URL}/votes" style="display:inline-block;padding:12px 22px;background:#2563eb;color:#ffffff;font-family:Arial,sans-serif;font-size:14px;font-weight:bold;text-decoration:none">${escapeHtml(t.email.explore)} →</a>
</td></tr>
<tr><td style="padding:18px 32px;border-top:1px solid #1e3a6e;font-family:Arial,sans-serif;font-size:12px;line-height:1.6;color:#56698f">
  ${escapeHtml(t.email.why)}<br>
  <a href="${unsubscribe}" style="color:#7fa6ff">${escapeHtml(t.email.unsubscribe)}</a>
  &nbsp;·&nbsp; ${escapeHtml(t.footer.data)}
</td></tr>
</table>
</td></tr></table>
</body></html>`;
}

export function digestSubject(content: DigestContent, locale: Locale) {
  const t = dictionaries[locale];
  return `${t.email.title} · ${formatDate(content.session, locale, { month: "long" })}`;
}
