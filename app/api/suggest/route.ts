import { searchVotes } from "@/lib/htv";

export async function GET(req: Request) {
  const q = new URL(req.url).searchParams.get("q")?.trim().slice(0, 80) ?? "";
  if (q.length < 2) return Response.json([]);
  try {
    const { results } = await searchVotes(q, 1, 6);
    return Response.json(
      results.map((v) => ({ id: v.id, title: v.display_title, date: v.timestamp.slice(0, 10), result: v.result })),
      { headers: { "cache-control": "public, max-age=300" } },
    );
  } catch {
    return Response.json([]);
  }
}
