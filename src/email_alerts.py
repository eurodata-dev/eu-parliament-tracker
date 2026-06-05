"""
email_alerts.py — Weekly digest email sender for EU Vote Tracker.

Fetches the top 5 most recent EP votes, sends a digest to all subscribers.
Run every Monday via GitHub Actions.

Required env vars:
    SUPABASE_URL, SUPABASE_KEY, RESEND_API_KEY, GROQ_API_KEY
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

for _c in [Path(__file__).parent.parent / ".env", Path(".env")]:
    if _c.exists():
        load_dotenv(_c)
        break

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SUPABASE_URL    = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY", "")
RESEND_API_KEY  = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL      = os.getenv("FROM_EMAIL", "EU Vote Tracker <onboarding@resend.dev>")
APP_URL         = os.getenv("APP_URL", "https://your-app.streamlit.app")

_WEEK_LABELS = {
    "EN": "Weekly Digest",
    "FR": "Résumé hebdomadaire",
    "ES": "Resumen semanal",
    "DE": "Wöchentliche Zusammenfassung",
    "IT": "Riepilogo settimanale",
}
_INTRO = {
    "EN": "Here are the most important votes in the European Parliament this week.",
    "FR": "Voici les votes les plus importants au Parlement européen cette semaine.",
    "ES": "Estos son los votos más importantes en el Parlamento Europeo esta semana.",
    "DE": "Hier sind die wichtigsten Abstimmungen im Europäischen Parlament dieser Woche.",
    "IT": "Ecco i voti più importanti al Parlamento Europeo questa settimana.",
}
_EXPLORE = {
    "EN": "Explore all votes",
    "FR": "Explorer tous les votes",
    "ES": "Explorar todos los votos",
    "DE": "Alle Abstimmungen erkunden",
    "IT": "Esplora tutti i voti",
}
_UNSUB = {
    "EN": "Unsubscribe",
    "FR": "Se désabonner",
    "ES": "Cancelar suscripción",
    "DE": "Abmelden",
    "IT": "Annulla iscrizione",
}
_PASSED = {
    "EN": "✅ Passed", "FR": "✅ Adopté", "ES": "✅ Aprobado",
    "DE": "✅ Angenommen", "IT": "✅ Approvato",
}
_REJECTED = {
    "EN": "❌ Rejected", "FR": "❌ Rejeté", "ES": "❌ Rechazado",
    "DE": "❌ Abgelehnt", "IT": "❌ Respinto",
}


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def _sb_headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def get_subscribers() -> list[dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Missing Supabase credentials")
        return []
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/subscribers",
        headers=_sb_headers(),
        params={"select": "email,language"},
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json()
    logger.error("Supabase read failed: %s %s", resp.status_code, resp.text[:200])
    return []


def add_subscriber(email: str, language: str = "EN") -> str:
    """Insert or reactivate a subscriber. Returns 'ok', 'exists', or 'error'."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return "error"
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/subscribers",
        headers={**_sb_headers(), "Prefer": "resolution=merge-duplicates,return=minimal"},
        json={"email": email, "language": language, "active": True},
        timeout=10,
    )
    if resp.status_code in (200, 201):
        return "ok"
    logger.error("Supabase insert failed: %s %s", resp.status_code, resp.text[:200])
    return "error"


def mark_sent() -> None:
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/subscribers",
        headers={**_sb_headers(), "Prefer": "return=minimal"},
        params={"active": "eq.true"},
        json={"last_digest_at": datetime.utcnow().isoformat()},
        timeout=10,
    )


# ---------------------------------------------------------------------------
# Vote data
# ---------------------------------------------------------------------------

def get_top_votes(n: int = 5) -> list[dict]:
    data_dir = Path(__file__).parent.parent / "data"
    dfs = []
    # Try yearly parquets first (most recent 2 years)
    by_year = data_dir / "processed" / "by_year"
    if by_year.exists():
        yearly = sorted(by_year.glob("eu_votes_*.parquet"), reverse=True)[:2]
        for p in yearly:
            try:
                dfs.append(pd.read_parquet(p, engine="pyarrow"))
            except Exception:
                pass
    # Fallback: flat parquet or CSV
    if not dfs:
        for fallback in [
            data_dir / "processed" / "eu_votes_real.parquet",
            data_dir / "processed" / "eu_votes_real.csv",
        ]:
            if fallback.exists():
                dfs.append(pd.read_parquet(fallback) if fallback.suffix == ".parquet" else pd.read_csv(fallback))
                break
    # Recent live data
    recent_dir = data_dir / "recent"
    if recent_dir.exists():
        for f in sorted(recent_dir.glob("*.csv"), reverse=True)[:3]:
            try:
                dfs.append(pd.read_csv(f))
            except Exception:
                pass
    if not dfs:
        return []

    df = pd.concat(dfs, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    cutoff = datetime.now() - timedelta(days=7)
    recent = df[df["date"] >= cutoff]
    if recent.empty:
        recent = df.sort_values("date", ascending=False)

    top_topics = (
        recent.groupby("policy_topic")
        .agg(vote_count=("vote", "count"), date=("date", "max"))
        .reset_index()
        .sort_values("date", ascending=False)
        .head(n)
    )
    result = []
    for _, row in top_topics.iterrows():
        td = df[df["policy_topic"] == row["policy_topic"]]
        vc = td["vote"].value_counts()
        for_n     = int(vc.get("FOR", 0))
        against_n = int(vc.get("AGAINST", 0))
        total     = for_n + against_n + int(vc.get("ABSTAIN", 0))
        result.append({
            "topic":       row["policy_topic"],
            "date":        row["date"].strftime("%d %b %Y") if pd.notna(row["date"]) else "",
            "for_pct":     round(for_n / total * 100, 1) if total else 0,
            "against_pct": round(against_n / total * 100, 1) if total else 0,
            "passed":      for_n > against_n,
        })
    return result


# ---------------------------------------------------------------------------
# Email builder
# ---------------------------------------------------------------------------

def build_html(votes: list[dict], lang: str) -> str:
    week_label  = _WEEK_LABELS.get(lang, _WEEK_LABELS["EN"])
    intro       = _INTRO.get(lang, _INTRO["EN"])
    explore_lbl = _EXPLORE.get(lang, _EXPLORE["EN"])
    unsub_lbl   = _UNSUB.get(lang, _UNSUB["EN"])
    week_str    = datetime.now().strftime("W%V · %B %Y")

    blocks = ""
    for v in votes:
        verdict_color = "#166534" if v["passed"] else "#991b1b"
        verdict_bg    = "#dcfce7" if v["passed"] else "#fee2e2"
        verdict_txt   = _PASSED.get(lang, "✅ Passed") if v["passed"] else _REJECTED.get(lang, "❌ Rejected")
        topic_short   = v["topic"][:80] + "…" if len(v["topic"]) > 80 else v["topic"]
        blocks += f"""
        <div style="border:1px solid #e5e7eb;border-radius:8px;padding:16px;
                    margin-bottom:12px;background:#fafafa;">
          <div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:8px;">
            {topic_short}
          </div>
          <div style="margin-bottom:8px;">
            <span style="font-size:12px;color:#6b7280;">{v['date']}</span>
            &nbsp;
            <span style="font-size:12px;background:{verdict_bg};color:{verdict_color};
                         padding:2px 10px;border-radius:12px;font-weight:600;">
              {verdict_txt}
            </span>
          </div>
          <div style="background:#f3f4f6;border-radius:6px;padding:8px 12px;
                      font-size:13px;color:#374151;">
            🗳️ {v['for_pct']}% FOR &nbsp;·&nbsp; {v['against_pct']}% AGAINST
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f9fafb;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:600px;margin:32px auto;background:white;
              border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);">

    <div style="background:linear-gradient(135deg,#1e3a8a,#1d4ed8);
                padding:28px 32px;text-align:center;">
      <div style="font-size:28px;margin-bottom:6px;">🏛️</div>
      <div style="color:white;font-size:20px;font-weight:700;">EU Parliament Vote Tracker</div>
      <div style="color:#bfdbfe;font-size:13px;margin-top:4px;">
        {week_label} · {week_str}
      </div>
    </div>

    <div style="padding:24px 32px 16px;">
      <p style="color:#374151;font-size:15px;line-height:1.6;margin:0;">{intro}</p>
    </div>

    <div style="padding:0 32px 24px;">{blocks}</div>

    <div style="padding:0 32px 28px;text-align:center;">
      <a href="{APP_URL}"
         style="background:#2563eb;color:white;padding:12px 28px;border-radius:8px;
                text-decoration:none;font-weight:600;font-size:14px;display:inline-block;">
        🔍 {explore_lbl}
      </a>
    </div>

    <div style="background:#f9fafb;padding:16px 32px;
                border-top:1px solid #e5e7eb;text-align:center;">
      <p style="color:#9ca3af;font-size:12px;margin:0;">
        EU Parliament Vote Tracker &nbsp;·&nbsp;
        Data: European Parliament Open Data Portal
      </p>
    </div>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def send_digest() -> None:
    if not RESEND_API_KEY:
        logger.error("RESEND_API_KEY not set")
        sys.exit(1)

    subscribers = get_subscribers()
    if not subscribers:
        logger.info("No active subscribers — nothing to send")
        return

    logger.info("%d subscriber(s) found", len(subscribers))
    votes = get_top_votes(5)
    if not votes:
        logger.warning("No vote data — aborting")
        return
    logger.info("%d top votes prepared", len(votes))

    sent = 0
    for sub in subscribers:
        email = sub.get("email", "")
        lang  = sub.get("language", "EN")
        if not email:
            continue

        html    = build_html(votes, lang)
        subject = f"🏛️ EU Parliament {_WEEK_LABELS.get(lang,'Weekly Digest')} — {datetime.now().strftime('%d %b %Y')}"

        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}",
                         "Content-Type": "application/json"},
                json={"from": FROM_EMAIL, "to": [email], "subject": subject, "html": html},
                timeout=15,
            )
            if resp.status_code in (200, 201, 202):
                sent += 1
                logger.info("✓ %s", email)
            else:
                logger.warning("✗ %s → %s %s", email, resp.status_code, resp.text[:100])
        except Exception as exc:
            logger.warning("✗ %s → %s", email, exc)

    logger.info("Digest sent: %d / %d", sent, len(subscribers))
    if sent:
        mark_sent()


if __name__ == "__main__":
    send_digest()
