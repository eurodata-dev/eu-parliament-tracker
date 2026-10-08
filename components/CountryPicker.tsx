"use client";

import { useRouter } from "next/navigation";
import styles from "./StartHere.module.css";

export default function CountryPicker({
  countries,
  label,
}: {
  countries: { code: string; label: string }[];
  label: string;
}) {
  const router = useRouter();
  return (
    <select
      className={`input ${styles.select}`}
      defaultValue=""
      aria-label={label}
      onChange={(e) => e.target.value && router.push(`/meps?country=${e.target.value}`)}
    >
      <option value="" disabled>
        {label}
      </option>
      {countries.map((c) => (
        <option key={c.code} value={c.code}>
          {c.label}
        </option>
      ))}
    </select>
  );
}
