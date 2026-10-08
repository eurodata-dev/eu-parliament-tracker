import type { Metadata } from "next";
import Link from "next/link";
import { fill } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/server";
import { checkUnsubscribeToken } from "@/lib/mail";
import styles from "../status.module.css";

export const metadata: Metadata = { title: "Unsubscribe", robots: { index: false } };

type Props = { searchParams: Promise<{ email?: string; token?: string; done?: string }> };

// Removing happens on POST only: mail scanners open links in emails, and a GET
// that deletes would unsubscribe people without them ever clicking.
export default async function UnsubscribePage({ searchParams }: Props) {
  const { email = "", token = "", done } = await searchParams;
  const { t } = await getDictionary();
  const address = email.trim().toLowerCase();
  const valid = Boolean(address && token && checkUnsubscribeToken(address, token));

  let title = t.unsubscribe.failed;
  let lede = t.unsubscribe.failedLede;
  if (done === "1") {
    title = t.unsubscribe.done;
    lede = fill(t.unsubscribe.doneLede, { email: address });
  } else if (valid) {
    title = t.unsubscribe.confirm;
    lede = fill(t.unsubscribe.confirmLede, { email: address });
  }

  return (
    <div className={`container ${styles.page}`}>
      <p className="eyebrow">{t.footer.newsletter}</p>
      <h1>{title}</h1>
      <p>{lede}</p>
      {valid && done !== "1" ? (
        <form method="post" action="/api/unsubscribe">
          <input type="hidden" name="email" value={address} />
          <input type="hidden" name="token" value={token} />
          <input type="hidden" name="from" value="page" />
          <button className="button">{t.unsubscribe.button}</button>
        </form>
      ) : (
        <Link href="/" className="more-link">
          ← {t.errors.home}
        </Link>
      )}
    </div>
  );
}
