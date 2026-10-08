import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import AiGenerate from "@/components/AiGenerate";
import AiNote from "@/components/AiNote";
import Pagination from "@/components/Pagination";
import TallyBar from "@/components/TallyBar";
import VoteList from "@/components/VoteList";
import { aiEnabled } from "@/lib/ai";
import { age, percent } from "@/lib/format";
import { groupColor } from "@/lib/groups";
import { currentMembers, getMember, memberVotes, NotFound, photoUrl } from "@/lib/htv";
import { fill } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { getDictionary } from "@/lib/i18n/server";
import type { Member, Tally } from "@/lib/types";
import { POSITIONS, POSITION_COLOR } from "@/lib/votes";
import styles from "./mep.module.css";

type Props = { params: Promise<{ id: string }>; searchParams: Promise<{ page?: string }> };

const SAMPLE = 100;
const PER_PAGE = 25;

async function load(id: string) {
  try {
    return await getMember(id);
  } catch (err) {
    if (err instanceof NotFound) notFound();
    throw err;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const member = await load((await params).id);
  const name = `${member.first_name} ${member.last_name}`;
  const photo = photoUrl(member.photo_url);
  return {
    title: `${name}: voting record`,
    description: `How ${name} (${member.group?.short_label ?? "NI"}, ${member.country.label}) votes in the European Parliament: attendance, positions and every roll-call vote.`,
    alternates: { canonical: `/meps/${member.id}` },
    openGraph: photo ? { images: [{ url: photo, alt: name }] } : undefined,
  };
}


export default async function MepPage({ params, searchParams }: Props) {
  const { id } = await params;
  const page = Math.max(1, Math.min(200, Number((await searchParams).page) || 1));
  const [member, { locale, t }, sample, history] = await Promise.all([
    load(id),
    getDictionary(),
    memberVotes(id, 1, SAMPLE),
    memberVotes(id, page, PER_PAGE),
  ]);

  const counts: Tally = { FOR: 0, AGAINST: 0, ABSTENTION: 0, DID_NOT_VOTE: 0 };
  sample.results.forEach((v) => counts[v.position]++);
  const n = sample.results.length;
  const photo = photoUrl(member.photo_url);
  const years = age(member.date_of_birth);
  const person = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: `${member.first_name} ${member.last_name}`,
    jobTitle: "Member of the European Parliament",
    nationality: member.country.label,
    image: photo ?? undefined,
    memberOf: [
      { "@type": "GovernmentOrganization", name: "European Parliament" },
      ...(member.group ? [{ "@type": "Organization", name: member.group.label }] : []),
    ],
  };

  return (
    <article className="container">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(person) }} />
      <header className={styles.head}>
        <div className={styles.photo}>
          {photo && <Image src={photo} alt={`${member.first_name} ${member.last_name}`} width={180} height={225} unoptimized priority />}
        </div>
        <div>
          <nav className={styles.crumbs}>
            <Link href="/meps">{t.nav.meps}</Link>
          </nav>
          <h1>
            <span>{member.first_name}</span> {member.last_name}
          </h1>
          <p className={styles.group}>
            <i style={{ background: groupColor(member.group?.code) }} />
            {member.group?.label ?? t.mep.noGroup}
          </p>
          <dl className={styles.facts}>
            <div>
              <dt>{t.vote.country}</dt>
              <dd>{member.country.label}</dd>
            </div>
            {member.national_party && (
              <div>
                <dt>{t.mep.party}</dt>
                <dd>
                  {member.national_party.label}
                  {member.national_party.short_label !== member.national_party.label && (
                    <span className="muted"> ({member.national_party.short_label})</span>
                  )}
                </dd>
              </div>
            )}
            {years && (
              <div>
                <dt>{t.mep.age}</dt>
                <dd className="num">{years}</dd>
              </div>
            )}
            {member.terms?.length > 0 && (
              <div>
                <dt>{t.mep.terms}</dt>
                <dd className="num">{member.terms.join(", ")}</dd>
              </div>
            )}
          </dl>
          <p className={styles.links}>
            {member.email && <a href={`mailto:${member.email}`}>{t.mep.email}</a>}
            {member.twitter && (
              <a href={member.twitter} target="_blank" rel="noopener">
                X / Twitter ↗
              </a>
            )}
            {member.facebook && (
              <a href={member.facebook} target="_blank" rel="noopener">
                Facebook ↗
              </a>
            )}
            <a href={`https://www.europarl.europa.eu/meps/en/${member.id}`} target="_blank" rel="noopener">
              europarl.europa.eu ↗
            </a>
          </p>
        </div>
      </header>

      <div className={styles.top}>
        <AiNote title={t.ai.inNutshell} note={t.ai.note} badge={t.ai.badge}>
          {aiEnabled() && n > 0 ? (
            <AiGenerate url={`/api/summary?kind=member&id=${id}`} labels={t.ai} lines={4} />
          ) : (
            <p className="muted">{t.ai.unavailable}</p>
          )}
        </AiNote>

        <div className={styles.record}>
          <h2 className="eyebrow">{t.mep.record}</h2>
          <div className={styles.attendance}>
            <span className="num">{percent(n - counts.DID_NOT_VOTE, n, locale)}</span>
            <span>{t.mep.attendance}</span>
          </div>
          <TallyBar tally={counts} height={10} />
          <ul className={styles.legend}>
            {POSITIONS.map((p) => (
              <li key={p}>
                <i style={{ background: POSITION_COLOR[p] }} />
                {t.vote[p]}
                <b className="num">{counts[p]}</b>
              </li>
            ))}
          </ul>
          <p className={styles.small}>{fill(t.mep.basedOn, { n })}</p>
        </div>
      </div>

      <section className="section">
        <div className="section-head">
          <h2>{t.mep.recent}</h2>
        </div>
        <VoteList votes={history.results} locale={locale} t={t} showPosition />
        <Pagination
          page={page}
          hasPrev={history.has_prev}
          hasNext={history.has_next}
          href={(p) => (p > 1 ? `/meps/${id}?page=${p}` : `/meps/${id}`)}
          labels={t.votes}
        />
      </section>

      <Suspense fallback={null}>
        <SameCountry member={member} t={t} />
      </Suspense>
    </article>
  );
}

async function SameCountry({ member, t }: { member: Member; t: Dictionary }) {
  const others = (await currentMembers().catch(() => [] as Member[])).filter(
    (m) => m.country.code === member.country.code && m.id !== member.id,
  );
  if (!others.length) return null;
  return (
    <section className="section">
      <div className="section-head">
        <h2>{fill(t.mep.sameCountry, { country: member.country.label })}</h2>
        <Link href={`/meps?country=${member.country.code}`} className="more-link">
          {fill(t.mep.allFrom, { n: others.length + 1 })} →
        </Link>
      </div>
      <ul className={styles.others}>
        {others.slice(0, 12).map((m) => (
          <li key={m.id}>
            <Link href={`/meps/${m.id}`}>
              <i style={{ background: groupColor(m.group?.code) }} />
              <span>
                {m.first_name} <b>{m.last_name}</b>
              </span>
              <small>{m.group?.short_label ?? t.mep.noGroup}</small>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
