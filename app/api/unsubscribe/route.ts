import { checkUnsubscribeToken } from "@/lib/mail";
import { removeSubscriber } from "@/lib/subscribers";

// Handles both the button on /unsubscribe and one-click unsubscribe from mail
// clients (RFC 8058), which POST to the URL in the List-Unsubscribe header.
export async function POST(req: Request) {
  const url = new URL(req.url);
  const form = await req.formData().catch(() => null);
  const email = String(form?.get("email") ?? url.searchParams.get("email") ?? "").trim().toLowerCase();
  const token = String(form?.get("token") ?? url.searchParams.get("token") ?? "");
  const fromPage = form?.get("from") === "page";
  const back = (query = "") => Response.redirect(new URL(`/unsubscribe${query}`, req.url), 303);

  if (!email || !token || !checkUnsubscribeToken(email, token)) {
    return fromPage ? back() : new Response("invalid", { status: 400 });
  }

  try {
    await removeSubscriber(email);
  } catch (err) {
    console.error("unsubscribe failed", err);
    return fromPage ? back() : new Response("error", { status: 502 });
  }

  return fromPage ? back(`?${new URLSearchParams({ email, done: "1" })}`) : new Response("ok");
}
