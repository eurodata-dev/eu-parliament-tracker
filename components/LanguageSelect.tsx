"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import { setLocale } from "@/app/actions";
import { localeNames, locales, type Locale } from "@/lib/i18n/config";
import styles from "./SiteHeader.module.css";

export default function LanguageSelect({ locale, label }: { locale: Locale; label: string }) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  return (
    <label className={styles.lang}>
      <span className="visually-hidden">{label}</span>
      <select
        value={locale}
        disabled={pending}
        onChange={(e) => {
          const next = e.target.value;
          startTransition(async () => {
            await setLocale(next);
            router.refresh();
          });
        }}
      >
        {locales.map((code) => (
          <option key={code} value={code} title={localeNames[code]}>
            {code.toUpperCase()}
          </option>
        ))}
      </select>
    </label>
  );
}
