import type { MetadataRoute } from "next";
import { currentMembers, latestVotes } from "@/lib/htv";
import { SITE_URL } from "@/lib/mail";

export const revalidate = 86400;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();
  const pages: MetadataRoute.Sitemap = [
    { url: SITE_URL, lastModified: now, changeFrequency: "daily", priority: 1 },
    { url: `${SITE_URL}/votes`, lastModified: now, changeFrequency: "daily", priority: 0.9 },
    { url: `${SITE_URL}/meps`, changeFrequency: "weekly", priority: 0.9 },
    { url: `${SITE_URL}/match`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${SITE_URL}/trends`, changeFrequency: "weekly", priority: 0.7 },
    { url: `${SITE_URL}/ask`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${SITE_URL}/about`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${SITE_URL}/contact`, changeFrequency: "yearly", priority: 0.3 },
    { url: `${SITE_URL}/privacy`, changeFrequency: "yearly", priority: 0.2 },
  ];

  const [votePages, members] = await Promise.all([
    Promise.all([1, 2, 3, 4, 5].map((p) => latestVotes(p, 100).catch(() => null))),
    currentMembers().catch(() => []),
  ]);

  const votes = votePages.flatMap((p) => p?.results ?? []).map((v) => ({
    url: `${SITE_URL}/votes/${v.id}`,
    lastModified: new Date(v.timestamp),
    changeFrequency: "yearly" as const,
    priority: 0.6,
  }));

  const meps = members.map((m) => ({
    url: `${SITE_URL}/meps/${m.id}`,
    changeFrequency: "weekly" as const,
    priority: 0.7,
  }));

  return [...pages, ...votes, ...meps];
}
