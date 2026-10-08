"use client";

import { useEffect } from "react";
import styles from "./status.module.css";

// client component, no dictionary here
const TEXT: Record<string, [string, string, string]> = {
  en: ["The voting data couldn't be loaded.", "The data source might be briefly unavailable. Try again in a moment.", "Try again"],
  fr: ["Les données de vote n'ont pas pu être chargées.", "La source de données est peut-être momentanément indisponible. Réessayez dans un instant.", "Réessayer"],
  de: ["Die Abstimmungsdaten konnten nicht geladen werden.", "Die Datenquelle ist vielleicht kurz nicht erreichbar. Versuchen Sie es gleich noch einmal.", "Erneut versuchen"],
  nl: ["De stemgegevens konden niet geladen worden.", "De gegevensbron is misschien even onbereikbaar. Probeer het zo meteen opnieuw.", "Opnieuw proberen"],
  es: ["No se pudieron cargar los datos de votación.", "Puede que la fuente de datos no esté disponible un momento. Inténtalo de nuevo enseguida.", "Reintentar"],
  it: ["Non è stato possibile caricare i dati di voto.", "La fonte dei dati potrebbe essere momentaneamente non disponibile. Riprova tra poco.", "Riprova"],
};

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  const lang = typeof document !== "undefined" ? document.documentElement.lang : "en";
  const [title, lede, retry] = TEXT[lang] ?? TEXT.en;

  return (
    <div className={`container ${styles.page}`}>
      <p className="eyebrow">Error</p>
      <h1>{title}</h1>
      <p>{lede}</p>
      <button className="button" onClick={reset}>
        {retry}
      </button>
    </div>
  );
}
