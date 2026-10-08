# EU Parliament Tracker

Source of [euparliamenttracker.com](https://euparliamenttracker.com): every roll-call vote in the European Parliament, how each group, country and MEP voted, and a short plain-language explanation of what was decided.

## What's in it

- **Votes**: search by subject, filter by topic and date, and see everything that matches added up (how each group voted across all of them, plus a written overview).
- **Vote pages**: result, hemicycle, group and country breakdowns, every MEP's vote, the Parliament's press summary, official documents, share links.
- **MEPs**: directory with filters, and a profile per MEP with attendance and voting history.
- **Match** (`/match`): answer 10 recent contested votes and see which MEPs and groups vote like you, on a hemicycle seat by seat.
- **Trends**: the last 30 days of votes compared with the months before: which group moved, which topics, polarization.
- **Ask**: questions in plain language, answered from the vote records with sources.
- **Weekly email**: sign-up form, signed unsubscribe links, sent every Monday after a plenary week.
- Six languages: English, French, German, Dutch, Spanish, Italian.

## How it works

- **Data** comes live from the [HowTheyVote.eu](https://howtheyvote.eu) API, which republishes the Parliament's official roll-call records under the ODbL (`lib/htv.ts`). Lists are cached for 15 minutes, finished votes for a week.
- **Summaries** use an LLM through the Groq API (`lib/ai.ts`). The model only gets the official record as input, and the output is cached per vote and language.
- **Aggregations** (topic overviews, trends) are in `lib/analysis.ts`.
- **Email** goes through Resend (`lib/mail.ts`, `lib/digest.ts`); subscribers live in Supabase (`lib/subscribers.ts`).
- A daily Vercel cron (`vercel.json` → `/api/cron/daily`) keeps the Supabase project awake and sends the digest on Mondays.

Built with Next.js 16 (App Router), TypeScript and plain CSS modules. No UI framework.

## Running it locally

```bash
npm install
cp .env.example .env.local   # then fill in the keys
npm run dev
```

Open http://localhost:3000.

## Environment variables

| Name | Needed for |
| --- | --- |
| `GROQ_API_KEY` | AI summaries and the Ask page. Without it the site still works, summaries are just hidden. |
| `SUPABASE_URL`, `SUPABASE_KEY` | Newsletter sign-up and the weekly email |
| `RESEND_API_KEY`, `FROM_EMAIL` | Weekly email and contact form. Sending to other people needs a verified domain in Resend. |
| `CONTACT_EMAIL` | Where contact form messages go |
| `CRON_SECRET` | Protects `/api/cron/daily`. Vercel sends it automatically to cron jobs. |
| `UNSUBSCRIBE_SECRET` | Signs unsubscribe links |
| `NEXT_PUBLIC_GA_ID` | Optional Google Analytics |
| `GROQ_MODEL`, `HTV_API_URL` | Optional overrides |

To test the weekly email by hand: `curl -H "Authorization: Bearer $CRON_SECRET" "https://euparliamenttracker.com/api/cron/daily?send=1"`.

## Project layout

```
app/            routes (home, votes, meps, match, trends, ask, about, contact) and API routes
components/     UI pieces, each with its own CSS module
lib/htv.ts      HowTheyVote API client
lib/analysis.ts topic overviews and trends
lib/match.ts    question picking for /match
lib/ai.ts       prompts and Groq calls
lib/i18n/       dictionaries and locale detection
```

## Credits

Built by Burhan Elmas.


Vote data © HowTheyVote.eu contributors, ODbL. MEP photos and press summaries © European Union, source: European Parliament.
