import "server-only";

// supabase REST, table subscribers (email, language, last_digest_at)

function config() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_KEY;
  if (!url || !key) throw new Error("Supabase is not configured");
  // new supabase keys (sb_secret_..., sb_publishable_...) are not JWTs and must not go in Authorization
  const headers: Record<string, string> = { apikey: key, "content-type": "application/json" };
  if (key.startsWith("eyJ")) headers.authorization = `Bearer ${key}`;
  return { url: `${url.replace(/\/+$/, "")}/rest/v1/subscribers`, headers };
}

export function subscribersEnabled() {
  return Boolean(process.env.SUPABASE_URL && process.env.SUPABASE_KEY);
}

export async function addSubscriber(email: string, language: string) {
  const { url, headers } = config();
  // upsert on email, needs a unique constraint on subscribers.email
  const res = await fetch(`${url}?on_conflict=email`, {
    method: "POST",
    headers: { ...headers, prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify({ email, language }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Supabase ${res.status}: ${(await res.text()).slice(0, 200)}`);
}

export async function removeSubscriber(email: string) {
  const { url, headers } = config();
  const res = await fetch(`${url}?email=eq.${encodeURIComponent(email)}`, {
    method: "DELETE",
    headers: { ...headers, prefer: "return=minimal" },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Supabase ${res.status}: ${(await res.text()).slice(0, 200)}`);
}

export async function listSubscribers(): Promise<{ email: string; language: string | null }[]> {
  const { url, headers } = config();
  const res = await fetch(`${url}?select=email,language`, { headers, cache: "no-store" });
  if (!res.ok) throw new Error(`Supabase ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return res.json();
}

export async function markDigestSent() {
  const { url, headers } = config();
  await fetch(`${url}?email=not.is.null`, {
    method: "PATCH",
    headers: { ...headers, prefer: "return=minimal" },
    body: JSON.stringify({ last_digest_at: new Date().toISOString() }),
    cache: "no-store",
  }).catch(() => {});
}

// cheap read so supabase free tier doesn't pause the project
export async function pingDatabase() {
  const { url, headers } = config();
  const res = await fetch(`${url}?select=email&limit=1`, { headers, cache: "no-store" });
  return res.status;
}
