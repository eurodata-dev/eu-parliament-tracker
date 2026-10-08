import "server-only";
import { cookies, headers } from "next/headers";
import { defaultLocale, isLocale, locales, type Locale } from "./config";
import en, { type Dictionary } from "./dictionaries/en";
import fr from "./dictionaries/fr";
import de from "./dictionaries/de";
import nl from "./dictionaries/nl";
import es from "./dictionaries/es";
import it from "./dictionaries/it";

const dictionaries = { en, fr, de, nl, es, it };

export const LOCALE_COOKIE = "lang";

export async function getLocale(): Promise<Locale> {
  const stored = (await cookies()).get(LOCALE_COOKIE)?.value;
  if (isLocale(stored)) return stored;

  const accept = (await headers()).get("accept-language") ?? "";
  for (const part of accept.split(",")) {
    const code = part.split(";")[0].trim().slice(0, 2).toLowerCase();
    if (isLocale(code)) return code;
  }
  return defaultLocale;
}

export async function getDictionary() {
  const locale = await getLocale();
  return { locale, t: dictionaries[locale] };
}

export function topicLabel(t: Dictionary, topic: { code: string; label: string }) {
  return (t.topics as Record<string, string>)[topic.code] ?? topic.label;
}

export { locales };
