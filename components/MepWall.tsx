import Image from "next/image";
import Link from "next/link";
import { groupColor } from "@/lib/groups";
import { photoUrl } from "@/lib/htv";
import { fill } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import type { Member } from "@/lib/types";
import CountryPicker from "./CountryPicker";
import styles from "./MepWall.module.css";

const SHOWN = 36;

// FNV hash -> different faces every day
function hash(s: string) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
  return h >>> 0;
}

export default function MepWall({
  members,
  countries,
  t,
}: {
  members: Member[];
  countries: { code: string; label: string }[];
  t: Dictionary;
}) {
  const day = new Date().toISOString().slice(0, 10);
  const faces = members
    .filter((m) => m.thumb_url || m.photo_url)
    .map((m) => ({ m, k: hash(`${day}:${m.id}`) }))
    .sort((a, b) => a.k - b.k)
    .slice(0, SHOWN)
    .map(({ m }) => m);

  if (faces.length < 12) return null;

  return (
    <section className={`container section ${styles.wrap}`}>
      <div className={styles.head}>
        <div>
          <h2>{fill(t.home.wallTitle, { n: members.length })}</h2>
          <p className={styles.lede}>{t.home.wallLede}</p>
        </div>
        <div className={styles.actions}>
          <CountryPicker countries={countries} label={t.home.pickCountry} />
          <Link href="/meps" className="more-link">
            {fill(t.home.wallAll, { n: members.length })} →
          </Link>
        </div>
      </div>

      <ul className={styles.wall}>
        {faces.map((m) => {
          const src = photoUrl(m.thumb_url ?? m.photo_url);
          return (
            <li key={m.id}>
              <Link href={`/meps/${m.id}`} className={styles.face} title={m.full_name}>
                {src && <Image src={src} alt="" width={104} height={130} unoptimized loading="lazy" />}
                <span className={styles.stripe} style={{ background: groupColor(m.group?.code) }} />
                <span className={styles.name}>
                  <b>{m.first_name} {m.last_name}</b>
                  <small>
                    {m.group?.short_label ?? "NI"} · {m.country.iso_alpha_2}
                  </small>
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
