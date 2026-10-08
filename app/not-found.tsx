import Link from "next/link";
import { getDictionary } from "@/lib/i18n/server";
import styles from "./status.module.css";

export default async function NotFound() {
  const { t } = await getDictionary();
  return (
    <div className={`container ${styles.page}`}>
      <p className="eyebrow">404</p>
      <h1>{t.errors.notFound}</h1>
      <p>{t.errors.notFoundLede}</p>
      <Link href="/" className="more-link">
        ← {t.errors.home}
      </Link>
    </div>
  );
}
