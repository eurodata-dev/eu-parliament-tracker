import type { Locale } from "./i18n/config";

export function formatDate(iso: string, locale: Locale, opts: Intl.DateTimeFormatOptions = {}) {
  return new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "Europe/Brussels",
    ...opts,
  }).format(new Date(iso));
}

export function formatNumber(n: number, locale: Locale) {
  return new Intl.NumberFormat(locale).format(n);
}

export function percent(part: number, whole: number, locale: Locale) {
  if (!whole) return "–";
  return new Intl.NumberFormat(locale, { style: "percent", maximumFractionDigits: 0 }).format(part / whole);
}

export function age(dateOfBirth: string | null) {
  if (!dateOfBirth) return null;
  const born = new Date(dateOfBirth);
  const now = new Date();
  let years = now.getFullYear() - born.getFullYear();
  const m = now.getMonth() - born.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < born.getDate())) years--;
  return years;
}

