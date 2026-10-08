import type { Metadata } from "next";
import MepDirectory from "@/components/MepDirectory";
import { currentMembers } from "@/lib/htv";
import { fill } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/server";
import styles from "../listing.module.css";

export const metadata: Metadata = {
  title: "All MEPs and how they vote",
  description:
    "All 720 Members of the European Parliament: search by name, country or political group and see each MEP's voting record and attendance.",
  alternates: { canonical: "/meps" },
};

type Props = { searchParams: Promise<{ country?: string; group?: string }> };

export default async function MepsPage({ searchParams }: Props) {
  const { country = "", group = "" } = await searchParams;
  const [{ t }, members] = await Promise.all([getDictionary(), currentMembers()]);
  return (
    <div className="container">
      <header className={styles.head}>
        <h1>{t.meps.title}</h1>
        <p>{fill(t.meps.lede, { n: members.length })}</p>
      </header>
      <MepDirectory
        key={`${country}|${group}`}
        members={members}
        t={t.meps}
        initialCountry={country.slice(0, 3).toUpperCase()}
        initialGroup={group.slice(0, 12).toUpperCase()}
      />
    </div>
  );
}
