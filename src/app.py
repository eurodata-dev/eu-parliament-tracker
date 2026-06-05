import os
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from eu_api import fetch_all_votes
from analysis_agent import analyze_policy, generate_ai_insight
from eu_dataset_loader import get_eu_votes
from recent_data_loader import load_recent_votes
from political_comparison_engine import compare_behavior, compute_group_behavior
from political_ai_explainer import explain_political_changes

st.set_page_config(
    page_title="EU Parliament Vote Tracker",
    page_icon="\U0001f1ea\U0001f1fa",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stButton > button {
        border-radius: 20px; font-size: 0.82rem; padding: 0.25rem 0.85rem;
        background-color: #f3f4f6; color: #374151; border: 1px solid #e5e7eb;
        transition: all 0.15s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .stButton > button:hover { background-color: #dbeafe; border-color: #3b82f6; color: #1d4ed8; }
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #2563eb !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-size: 1rem !important; padding: 0.5rem 2rem !important;
    }
    [data-testid="stSidebar"] .stButton > button { border-radius: 6px; }
    .topic-bar { background: #f8fafc; border-left: 4px solid #2563eb; padding: 12px 20px;
        border-radius: 4px; margin-bottom: 1.5rem; font-size: 1.05rem; line-height: 1.5; }
    .verdict-passed    { background:#dcfce7; color:#166534; padding:5px 16px; border-radius:20px; font-weight:600; font-size:0.95rem; display:inline-block; margin-top:0.8rem; }
    .verdict-rejected  { background:#fee2e2; color:#991b1b; padding:5px 16px; border-radius:20px; font-weight:600; font-size:0.95rem; display:inline-block; margin-top:0.8rem; }
    .verdict-contested { background:#fef9c3; color:#854d0e; padding:5px 16px; border-radius:20px; font-weight:600; font-size:0.95rem; display:inline-block; margin-top:0.8rem; }
    .result-card { text-align:center; padding:1.2rem 1rem; border-radius:10px; }
    .result-card .icon { font-size:2rem; }
    .result-card .pct  { font-size:2.6rem; font-weight:800; line-height:1.1; }
    .result-card .label{ font-size:0.9rem; color:#6b7280; margin-top:0.2rem; }
    .ai-card { background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:1.2rem 1.5rem; margin-top:0.5rem; white-space:pre-wrap; font-size:0.92rem; }
    .search-hint { text-align:center; color:#9ca3af; font-size:0.82rem; margin-top:0.3rem; }
    /* Language picker — top right */
    div[data-testid="stSelectbox"][id="lang-picker"] > div > div {
        border: 2px solid #2563eb !important;
        border-radius: 20px !important;
        background: #eff6ff !important;
        font-size: 0.9rem !important;
        padding: 0 0.4rem !important;
    }
    .lang-label {
        text-align: right;
        font-size: 0.72rem;
        color: #6b7280;
        margin-bottom: 2px;
        margin-top: 0.2rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")
_DEMO_ROW_LIMIT = 5000
_DATA_DIR = Path(__file__).parent.parent / "data"

_SYNONYMS: dict[str, list[str]] = {
    "AI":   ["artificial intelligence", "intelligence artificielle"],
    "EP":   ["european parliament"],
    "DSA":  ["digital services"],
    "GDPR": ["data protection"],
}

# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------
_TR: dict[str, dict[str, str]] = {
    "EN": {
        "lang_label":        "Language",
        "home":              "\U0001f3e0 Home",
        "home_help":         "Back to homepage",
        "filters":           "Filters",
        "date_range":        "Date range",
        "select_all":        "Select all",
        "clear_all":         "Clear all",
        "refresh":           "\U0001f504 Refresh live data",
        "refresh_help":      "Fetches the latest votes from the EU Parliament API (~15 seconds)",
        "refreshing":        "Fetching latest EP votes... (~15 seconds)",
        "refreshed":         "Live data refreshed!",
        "refresh_failed":    "Fetch failed",
        "votes_loaded":      "votes loaded",
        "live_included":     "\U0001f7e2 Live data included",
        "title":             "EU Parliament Vote Tracker",
        "subtitle":          "Search {n:,} votes from the European Parliament (2019-2026)",
        "placeholder":       "Search any topic — e.g. AI, Ukraine, climate, pharma...",
        "search_hint":       "Type a topic to see matching votes &nbsp;·&nbsp; Use 2-letter uppercase for abbreviations (AI, EP...)",
        "no_results":        "No matching topics found.",
        "see_all_combined":  "\U0001f50d See all {n} topics combined — {v:,} votes",
        "see_all_list":      "\U0001f4cb See all {n} matching topics",
        "n_match_pick":      "{n} topics match — pick one, or use the button above to combine all:",
        "all_topics_label":  "All topics matching '{q}'",
        "how_voted":         "How did parties vote?",
        "vote_breakdown":    "Vote breakdown by political group",
        "no_vote_data":      "No voting data for this topic.",
        "overall_result":    "Overall result",
        "for_label":         "FOR",
        "against_label":     "AGAINST",
        "abstain_label":     "ABSTAIN",
        "passed":            "Motion passed",
        "rejected":          "Motion rejected",
        "tied":              "Tied result",
        "ai_section":        "AI Analysis",
        "ai_button":         "Generate AI Analysis",
        "ai_spinning":       "Generating AI analysis... (usually 3-5 seconds)",
        "ai_no_data":        "No voting data available for AI analysis.",
        "ai_no_key":         "AI Analysis not configured. Add your free Groq API key to `.env` — get one at [console.groq.com](https://console.groq.com).",
        "ai_bad_key":        "Invalid Groq API key. Check `GROQ_API_KEY` in your `.env` file.",
        "ai_rate_limit":     "Groq rate limit reached. Wait a few seconds and try again.",
        "ai_timeout":        "AI request timed out. Try again.",
        "ai_error":          "AI service temporarily unavailable. Try again in a moment.",
        "latest_title":      "Latest Votes in the European Parliament",
        "latest_caption":    "The 15 most recent legislative topics voted on — click any to explore.",
        "recent_changes":    "Recent Political Changes",
        "recent_caption":    "Compares voting behavior from the last 30 days against the full historical dataset.",
        "hist_insight":      "Historical Insight",
        "recent_analysis":   "Recent Change Analysis",
        "most_chg_group":    "Most Changed Group",
        "most_chg_topic":    "Most Changed Topic",
        "polarization":      "Polarization Change",
        "ai_summary":        "AI Summary",
        "recent_failed":     "Could not compute recent changes",
        "across_topics":     " across {n} legislative topics",
        "lang_name":         "English",
        "subscribe_title":   "📬 Get the weekly digest",
        "subscribe_body":    "Every Monday: the 5 most important EU votes, explained in plain language.",
        "subscribe_placeholder": "your@email.com",
        "subscribe_btn":     "Subscribe — it's free",
        "subscribe_ok":      "✅ You're subscribed! First digest arrives next Monday.",
        "subscribe_exists":  "✅ You're already subscribed.",
        "subscribe_err":     "Something went wrong. Try again.",
        "subscribe_invalid": "Please enter a valid email address.",
        "onboard_title":     "What is this?",
        "onboard_body":      "Every law that shapes Europe passes through the EU Parliament — here you can see exactly how each political group voted, and get a plain-language AI explanation of what it means. No political expertise required.",
        "try_example":       "✨ Try an example:",
        "about_tool_title":  "About this tool",
        "about_tool_body":   "Built to make EU democracy accessible to everyone — not just experts. Search any legislative topic and get an instant breakdown of how each political group voted, plus an AI explanation in plain language.",
        "about_data_title":  "Data sources",
        "about_transparency":"All voting data is public record. No editorial bias — the app shows raw vote counts and lets you draw your own conclusions.",
        "about_transp_title":"Transparency",
    },
    "FR": {
        "lang_label":        "Langue",
        "home":              "\U0001f3e0 Accueil",
        "home_help":         "Retour à la page d'accueil",
        "filters":           "Filtres",
        "date_range":        "Période",
        "select_all":        "Tout sélectionner",
        "clear_all":         "Tout effacer",
        "refresh":           "\U0001f504 Actualiser les données",
        "refresh_help":      "Récupère les derniers votes du Parlement européen (~15 secondes)",
        "refreshing":        "Récupération des votes... (~15 secondes)",
        "refreshed":         "Données actualisées !",
        "refresh_failed":    "Échec de la mise à jour",
        "votes_loaded":      "votes chargés",
        "live_included":     "\U0001f7e2 Données en direct incluses",
        "title":             "Suivi des votes du Parlement européen",
        "subtitle":          "Recherchez parmi {n:,} votes du Parlement européen (2019-2026)",
        "placeholder":       "Rechercher un sujet — ex. IA, Ukraine, climat, pharma...",
        "search_hint":       "Tapez un sujet pour voir les votes correspondants &nbsp;·&nbsp; Utilisez des majuscules pour les abbréviations (IA, EP...)",
        "no_results":        "Aucun sujet trouvé.",
        "see_all_combined":  "\U0001f50d Voir les {n} sujets combinés — {v:,} votes",
        "see_all_list":      "\U0001f4cb Voir les {n} sujets correspondants",
        "n_match_pick":      "{n} sujets correspondent — choisissez-en un ou combinez-les :",
        "all_topics_label":  "Tous les sujets correspondant à '{q}'",
        "how_voted":         "Comment les partis ont-ils voté ?",
        "vote_breakdown":    "Répartition des votes par groupe politique",
        "no_vote_data":      "Aucune donnée de vote pour ce sujet.",
        "overall_result":    "Résultat global",
        "for_label":         "POUR",
        "against_label":     "CONTRE",
        "abstain_label":     "ABSTENTION",
        "passed":            "Motion adoptée",
        "rejected":          "Motion rejetée",
        "tied":              "Résultat égal",
        "ai_section":        "Analyse IA",
        "ai_button":         "Générer l'analyse IA",
        "ai_spinning":       "Génération de l'analyse... (3-5 secondes)",
        "ai_no_data":        "Aucune donnée disponible pour l'analyse IA.",
        "ai_no_key":         "Analyse IA non configurée. Ajoutez votre clé Groq gratuite dans `.env` — obtenez-en une sur [console.groq.com](https://console.groq.com).",
        "ai_bad_key":        "Clé Groq invalide. Vérifiez `GROQ_API_KEY` dans votre fichier `.env`.",
        "ai_rate_limit":     "Limite Groq atteinte. Réessayez dans quelques secondes.",
        "ai_timeout":        "Requête IA expirée. Réessayez.",
        "ai_error":          "Service IA temporairement indisponible. Réessayez dans un moment.",
        "latest_title":      "Derniers votes au Parlement européen",
        "latest_caption":    "Les 15 sujets législatifs les plus récents — cliquez pour explorer.",
        "recent_changes":    "Changements politiques récents",
        "recent_caption":    "Compare le comportement de vote des 30 derniers jours avec l'historique complet.",
        "hist_insight":      "Historique",
        "recent_analysis":   "Analyse des changements récents",
        "most_chg_group":    "Groupe le plus changé",
        "most_chg_topic":    "Sujet le plus changé",
        "polarization":      "Changement de polarisation",
        "ai_summary":        "Résumé IA",
        "recent_failed":     "Impossible de calculer les changements récents",
        "across_topics":     " sur {n} sujets législatifs",
        "lang_name":         "French",
        "subscribe_title":   "📬 Recevez le résumé hebdomadaire",
        "subscribe_body":    "Chaque lundi : les 5 votes les plus importants de l'UE, expliqués simplement.",
        "subscribe_placeholder": "votre@email.com",
        "subscribe_btn":     "S'abonner — c'est gratuit",
        "subscribe_ok":      "✅ Vous êtes abonné(e) ! Premier résumé lundi prochain.",
        "subscribe_exists":  "✅ Vous êtes déjà abonné(e).",
        "subscribe_err":     "Une erreur est survenue. Réessayez.",
        "subscribe_invalid": "Veuillez entrer une adresse email valide.",
        "onboard_title":     "C'est quoi ?",
        "onboard_body":      "Chaque loi qui façonne l'Europe passe par le Parlement européen — ici, vous pouvez voir exactement comment chaque groupe politique a voté, et obtenir une explication simple grâce à l'IA. Aucune expertise politique requise.",
        "try_example":       "✨ Essayez un exemple :",
        "about_tool_title":  "À propos",
        "about_tool_body":   "Conçu pour rendre la démocratie européenne accessible à tous — pas seulement aux experts. Recherchez n'importe quel sujet législatif et obtenez une analyse instantanée des votes, avec une explication en langage clair.",
        "about_data_title":  "Sources de données",
        "about_transparency":"Toutes les données de vote sont publiques. Aucun biais éditorial — l'application affiche les chiffres bruts et vous laisse tirer vos propres conclusions.",
        "about_transp_title":"Transparence",
    },
    "ES": {
        "lang_label":        "Idioma",
        "home":              "\U0001f3e0 Inicio",
        "home_help":         "Volver a la página principal",
        "filters":           "Filtros",
        "date_range":        "Periodo",
        "select_all":        "Seleccionar todo",
        "clear_all":         "Borrar todo",
        "refresh":           "\U0001f504 Actualizar datos",
        "refresh_help":      "Obtiene los últimos votos del Parlamento Europeo (~15 segundos)",
        "refreshing":        "Obteniendo los últimos votos... (~15 segundos)",
        "refreshed":         "¡Datos actualizados!",
        "refresh_failed":    "Error al actualizar",
        "votes_loaded":      "votos cargados",
        "live_included":     "\U0001f7e2 Datos en directo incluidos",
        "title":             "Seguimiento de votos del Parlamento Europeo",
        "subtitle":          "Busca entre {n:,} votos del Parlamento Europeo (2019-2026)",
        "placeholder":       "Busca cualquier tema — ej. IA, Ucrania, clima, pharma...",
        "search_hint":       "Escribe un tema para ver los votos &nbsp;·&nbsp; Usa mayúsculas para abreviaturas (IA, EP...)",
        "no_results":        "No se encontraron temas.",
        "see_all_combined":  "\U0001f50d Ver los {n} temas combinados — {v:,} votos",
        "see_all_list":      "\U0001f4cb Ver los {n} temas encontrados",
        "n_match_pick":      "{n} temas coinciden — elige uno o combina todos:",
        "all_topics_label":  "Todos los temas que coinciden con '{q}'",
        "how_voted":         "¿Cómo votaron los partidos?",
        "vote_breakdown":    "Distribución de votos por grupo político",
        "no_vote_data":      "No hay datos de voto para este tema.",
        "overall_result":    "Resultado global",
        "for_label":         "A FAVOR",
        "against_label":     "EN CONTRA",
        "abstain_label":     "ABSTENCIÓN",
        "passed":            "Moción aprobada",
        "rejected":          "Moción rechazada",
        "tied":              "Resultado empatado",
        "ai_section":        "Análisis IA",
        "ai_button":         "Generar análisis IA",
        "ai_spinning":       "Generando el análisis... (3-5 segundos)",
        "ai_no_data":        "No hay datos disponibles para el análisis IA.",
        "ai_no_key":         "Análisis IA no configurado. Añade tu clave Groq gratuita en `.env`.",
        "ai_bad_key":        "Clave Groq inválida. Verifica `GROQ_API_KEY` en tu archivo `.env`.",
        "ai_rate_limit":     "Límite de Groq alcanzado. Espera unos segundos.",
        "ai_timeout":        "Tiempo de espera agotado. Inténtalo de nuevo.",
        "ai_error":          "Servicio IA temporalmente no disponible. Inténtalo en un momento.",
        "latest_title":      "Últimos votos en el Parlamento Europeo",
        "latest_caption":    "Los 15 temas legislativos más recientes — haz clic para explorar.",
        "recent_changes":    "Cambios políticos recientes",
        "recent_caption":    "Compara el comportamiento de voto de los últimos 30 días con el historial completo.",
        "hist_insight":      "Historial",
        "recent_analysis":   "Análisis de cambios recientes",
        "most_chg_group":    "Grupo más cambiado",
        "most_chg_topic":    "Tema más cambiado",
        "polarization":      "Cambio de polarización",
        "ai_summary":        "Resumen IA",
        "recent_failed":     "No se pudieron calcular los cambios recientes",
        "across_topics":     " en {n} temas legislativos",
        "lang_name":         "Spanish",
        "subscribe_title":   "📬 Recibe el resumen semanal",
        "subscribe_body":    "Cada lunes: los 5 votos más importantes de la UE, explicados en claro.",
        "subscribe_placeholder": "tu@email.com",
        "subscribe_btn":     "Suscribirse — es gratis",
        "subscribe_ok":      "✅ ¡Suscrito/a! El primer resumen llega el próximo lunes.",
        "subscribe_exists":  "✅ Ya estás suscrito/a.",
        "subscribe_err":     "Algo salió mal. Inténtalo de nuevo.",
        "subscribe_invalid": "Por favor, introduce una dirección de email válida.",
        "onboard_title":     "¿Qué es esto?",
        "onboard_body":      "Cada ley que da forma a Europa pasa por el Parlamento Europeo — aquí puedes ver exactamente cómo votó cada grupo político y obtener una explicación en lenguaje sencillo gracias a la IA. No se requiere experiencia política.",
        "try_example":       "✨ Prueba un ejemplo:",
        "about_tool_title":  "Acerca de",
        "about_tool_body":   "Creado para hacer la democracia europea accesible a todos, no solo a los expertos. Busca cualquier tema legislativo y obtén un análisis instantáneo de los votos con una explicación clara.",
        "about_data_title":  "Fuentes de datos",
        "about_transparency":"Todos los datos de votación son de dominio público. Sin sesgo editorial — la app muestra los recuentos brutos y te deja sacar tus propias conclusiones.",
        "about_transp_title":"Transparencia",
    },
    "DE": {
        "lang_label":        "Sprache",
        "home":              "\U0001f3e0 Startseite",
        "home_help":         "Zurück zur Startseite",
        "filters":           "Filter",
        "date_range":        "Zeitraum",
        "select_all":        "Alle auswählen",
        "clear_all":         "Alle abwählen",
        "refresh":           "\U0001f504 Daten aktualisieren",
        "refresh_help":      "Neueste Abstimmungen des EU-Parlaments abrufen (~15 Sekunden)",
        "refreshing":        "Neueste Abstimmungen werden geladen... (~15 Sekunden)",
        "refreshed":         "Daten aktualisiert!",
        "refresh_failed":    "Aktualisierung fehlgeschlagen",
        "votes_loaded":      "Abstimmungen geladen",
        "live_included":     "\U0001f7e2 Live-Daten enthalten",
        "title":             "EU-Parlament Abstimmungsmonitor",
        "subtitle":          "{n:,} Abstimmungen des Europäischen Parlaments durchsuchen (2019-2026)",
        "placeholder":       "Thema suchen — z.B. KI, Ukraine, Klima, Pharma...",
        "search_hint":       "Thema eingeben, um Abstimmungen zu sehen &nbsp;·&nbsp; Großbuchstaben für Abkürzungen (KI, EP...)",
        "no_results":        "Keine passenden Themen gefunden.",
        "see_all_combined":  "\U0001f50d Alle {n} Themen kombiniert — {v:,} Abstimmungen",
        "see_all_list":      "\U0001f4cb Alle {n} passenden Themen anzeigen",
        "n_match_pick":      "{n} Themen gefunden — eines auswählen oder alle kombinieren:",
        "all_topics_label":  "Alle Themen zu '{q}'",
        "how_voted":         "Wie haben die Fraktionen abgestimmt?",
        "vote_breakdown":    "Abstimmungsverteilung nach politischer Fraktion",
        "no_vote_data":      "Keine Abstimmungsdaten für dieses Thema.",
        "overall_result":    "Gesamtergebnis",
        "for_label":         "DAFÜR",
        "against_label":     "DAGEGEN",
        "abstain_label":     "ENTHALTUNG",
        "passed":            "Antrag angenommen",
        "rejected":          "Antrag abgelehnt",
        "tied":              "Unentschieden",
        "ai_section":        "KI-Analyse",
        "ai_button":         "KI-Analyse generieren",
        "ai_spinning":       "KI-Analyse wird erstellt... (3-5 Sekunden)",
        "ai_no_data":        "Keine Daten für die KI-Analyse verfügbar.",
        "ai_no_key":         "KI-Analyse nicht konfiguriert. Füge deinen kostenlosen Groq-Schlüssel in `.env` ein.",
        "ai_bad_key":        "Ungültiger Groq-Schlüssel. Überprüfe `GROQ_API_KEY` in deiner `.env`-Datei.",
        "ai_rate_limit":     "Groq-Limit erreicht. Warte ein paar Sekunden.",
        "ai_timeout":        "KI-Anfrage abgelaufen. Erneut versuchen.",
        "ai_error":          "KI-Dienst vorübergehend nicht verfügbar. Später erneut versuchen.",
        "latest_title":      "Neueste Abstimmungen im EU-Parlament",
        "latest_caption":    "Die 15 neuesten Gesetzgebungsthemen — klicken zum Erkunden.",
        "recent_changes":    "Aktuelle politische Veränderungen",
        "recent_caption":    "Vergleicht das Abstimmungsverhalten der letzten 30 Tage mit dem historischen Datensatz.",
        "hist_insight":      "Historischer Überblick",
        "recent_analysis":   "Analyse aktueller Veränderungen",
        "most_chg_group":    "Meistveränderte Fraktion",
        "most_chg_topic":    "Meistverändertes Thema",
        "polarization":      "Polarisierungsänderung",
        "ai_summary":        "KI-Zusammenfassung",
        "recent_failed":     "Veränderungen konnten nicht berechnet werden",
        "across_topics":     " über {n} Gesetzgebungsthemen",
        "lang_name":         "German",
        "subscribe_title":   "📬 Wöchentliche Zusammenfassung erhalten",
        "subscribe_body":    "Jeden Montag: die 5 wichtigsten EU-Abstimmungen, einfach erklärt.",
        "subscribe_placeholder": "deine@email.com",
        "subscribe_btn":     "Abonnieren — kostenlos",
        "subscribe_ok":      "✅ Abonniert! Die erste Zusammenfassung kommt nächsten Montag.",
        "subscribe_exists":  "✅ Du bist bereits abonniert.",
        "subscribe_err":     "Etwas ist schiefgelaufen. Versuche es erneut.",
        "subscribe_invalid": "Bitte gib eine gültige E-Mail-Adresse ein.",
        "onboard_title":     "Was ist das hier?",
        "onboard_body":      "Jedes Gesetz, das Europa prägt, durchläuft das EU-Parlament — hier siehst du genau, wie jede politische Fraktion abgestimmt hat, und bekommst eine verständliche KI-Erklärung dazu. Kein politisches Vorwissen erforderlich.",
        "try_example":       "✨ Beispiel ausprobieren:",
        "about_tool_title":  "Über dieses Tool",
        "about_tool_body":   "Entwickelt, um die EU-Demokratie für alle zugänglich zu machen — nicht nur für Experten. Suche nach einem Gesetzgebungsthema und erhalte sofort eine Abstimmungsanalyse mit einer klaren Erklärung.",
        "about_data_title":  "Datenquellen",
        "about_transparency":"Alle Abstimmungsdaten sind öffentlich zugänglich. Kein redaktioneller Bias — die App zeigt rohe Stimmauszählungen und lässt dich eigene Schlüsse ziehen.",
        "about_transp_title":"Transparenz",
    },
    "IT": {
        "lang_label":        "Lingua",
        "home":              "\U0001f3e0 Home",
        "home_help":         "Torna alla pagina principale",
        "filters":           "Filtri",
        "date_range":        "Periodo",
        "select_all":        "Seleziona tutto",
        "clear_all":         "Deseleziona tutto",
        "refresh":           "\U0001f504 Aggiorna dati",
        "refresh_help":      "Recupera gli ultimi voti del Parlamento Europeo (~15 secondi)",
        "refreshing":        "Recupero degli ultimi voti... (~15 secondi)",
        "refreshed":         "Dati aggiornati!",
        "refresh_failed":    "Aggiornamento fallito",
        "votes_loaded":      "voti caricati",
        "live_included":     "\U0001f7e2 Dati in tempo reale inclusi",
        "title":             "Monitor dei voti del Parlamento Europeo",
        "subtitle":          "Cerca tra {n:,} voti del Parlamento Europeo (2019-2026)",
        "placeholder":       "Cerca un argomento — es. IA, Ucraina, clima, farmaci...",
        "search_hint":       "Digita un argomento per vedere i voti &nbsp;·&nbsp; Usa maiuscole per le abbreviazioni (IA, EP...)",
        "no_results":        "Nessun argomento trovato.",
        "see_all_combined":  "\U0001f50d Vedi tutti i {n} argomenti combinati — {v:,} voti",
        "see_all_list":      "\U0001f4cb Vedi tutti i {n} argomenti corrispondenti",
        "n_match_pick":      "{n} argomenti corrispondenti — sceglierne uno o combinarli tutti:",
        "all_topics_label":  "Tutti gli argomenti corrispondenti a '{q}'",
        "how_voted":         "Come hanno votato i gruppi politici?",
        "vote_breakdown":    "Distribuzione dei voti per gruppo politico",
        "no_vote_data":      "Nessun dato di voto per questo argomento.",
        "overall_result":    "Risultato complessivo",
        "for_label":         "A FAVORE",
        "against_label":     "CONTRARIO",
        "abstain_label":     "ASTENUTO",
        "passed":            "Mozione approvata",
        "rejected":          "Mozione respinta",
        "tied":              "Risultato in parità",
        "ai_section":        "Analisi IA",
        "ai_button":         "Genera analisi IA",
        "ai_spinning":       "Generazione analisi in corso... (3-5 secondi)",
        "ai_no_data":        "Nessun dato disponibile per l'analisi IA.",
        "ai_no_key":         "Analisi IA non configurata. Aggiungi la tua chiave Groq gratuita in `.env`.",
        "ai_bad_key":        "Chiave Groq non valida. Verifica `GROQ_API_KEY` nel file `.env`.",
        "ai_rate_limit":     "Limite Groq raggiunto. Riprova tra qualche secondo.",
        "ai_timeout":        "Richiesta IA scaduta. Riprova.",
        "ai_error":          "Servizio IA temporaneamente non disponibile. Riprova tra un momento.",
        "latest_title":      "Ultimi voti al Parlamento Europeo",
        "latest_caption":    "I 15 argomenti legislativi più recenti — clicca per esplorare.",
        "recent_changes":    "Cambiamenti politici recenti",
        "recent_caption":    "Confronta il comportamento di voto degli ultimi 30 giorni con lo storico completo.",
        "hist_insight":      "Storico",
        "recent_analysis":   "Analisi dei cambiamenti recenti",
        "most_chg_group":    "Gruppo più cambiato",
        "most_chg_topic":    "Argomento più cambiato",
        "polarization":      "Variazione della polarizzazione",
        "ai_summary":        "Riepilogo IA",
        "recent_failed":     "Impossibile calcolare i cambiamenti recenti",
        "across_topics":     " su {n} argomenti legislativi",
        "lang_name":         "Italian",
        "subscribe_title":   "📬 Ricevi il riepilogo settimanale",
        "subscribe_body":    "Ogni lunedì: i 5 voti più importanti dell'UE, spiegati in chiaro.",
        "subscribe_placeholder": "tua@email.com",
        "subscribe_btn":     "Iscriviti — è gratuito",
        "subscribe_ok":      "✅ Iscritto/a! Il primo riepilogo arriva lunedì prossimo.",
        "subscribe_exists":  "✅ Sei già iscritto/a.",
        "subscribe_err":     "Qualcosa è andato storto. Riprova.",
        "subscribe_invalid": "Inserisci un indirizzo email valido.",
        "onboard_title":     "Cos'è questo?",
        "onboard_body":      "Ogni legge che dà forma all'Europa passa attraverso il Parlamento Europeo — qui puoi vedere esattamente come ha votato ogni gruppo politico e ottenere una spiegazione in linguaggio semplice grazie all'IA. Nessuna competenza politica richiesta.",
        "try_example":       "✨ Prova un esempio:",
        "about_tool_title":  "Informazioni",
        "about_tool_body":   "Creato per rendere la democrazia europea accessibile a tutti, non solo agli esperti. Cerca qualsiasi argomento legislativo e ottieni un'analisi istantanea dei voti con una spiegazione chiara.",
        "about_data_title":  "Fonti dei dati",
        "about_transparency":"Tutti i dati di voto sono di pubblico dominio. Nessun pregiudizio editoriale — l'app mostra i conteggi grezzi e ti lascia trarre le tue conclusioni.",
        "about_transp_title":"Trasparenza",
    },
}

_LANG_OPTIONS = {
    "🇬🇧 English":  "EN",
    "🇫🇷 Français": "FR",
    "🇪🇸 Español":  "ES",
    "🇩🇪 Deutsch":  "DE",
    "🇮🇹 Italiano": "IT",
}

# Render language picker at top-right BEFORE sidebar so t() calls work everywhere
_sp, _lang_col = st.columns([5, 1])
with _lang_col:
    st.markdown('<p class="lang-label">🌐 Language</p>', unsafe_allow_html=True)
    lang_display = st.selectbox(
        "language",
        options=list(_LANG_OPTIONS.keys()),
        index=list(_LANG_OPTIONS.keys()).index(
            next((k for k, v in _LANG_OPTIONS.items() if v == st.session_state.get("lang", "EN")), "🇬🇧 English")
        ),
        key="lang_display",
        label_visibility="collapsed",
    )
st.session_state["lang"] = _LANG_OPTIONS[lang_display]

def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("lang", "EN")
    text = _TR.get(lang, _TR["EN"]).get(key, _TR["EN"].get(key, key))
    return text.format(**kwargs) if kwargs else text


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _preload(years: tuple = (2024, 2025, 2026)):
    _votes = get_eu_votes(years=list(years))
    if DEMO_MODE and len(_votes) > _DEMO_ROW_LIMIT:
        _votes = _votes.tail(_DEMO_ROW_LIMIT).reset_index(drop=True)
    _historical = _votes  # same dataset, used for historical comparisons
    if DEMO_MODE and len(_historical) > _DEMO_ROW_LIMIT:
        _historical = _historical.tail(_DEMO_ROW_LIMIT).reset_index(drop=True)
    _recent = load_recent_votes(30)
    _has_recent = not _recent.empty
    _g_behavior = compute_group_behavior(_historical) if not _historical.empty else pd.DataFrame()
    _comparison = compare_behavior(_historical, _recent) if _has_recent else {}
    _topic_index = (
        _votes.groupby("policy_topic")
        .agg(n=("vote", "count"), min_date=("date", "min"), max_date=("date", "max"))
        .reset_index()
        .sort_values("n", ascending=False)
        .reset_index(drop=True)
    )
    _latest_15 = (
        _votes.dropna(subset=["policy_topic", "date"])
        .sort_values("date", ascending=False)
        .drop_duplicates(subset=["policy_topic"])
        .head(15)[["policy_topic", "date"]]
        .reset_index(drop=True)
    )
    return _votes, _historical, _recent, _g_behavior, _comparison, _has_recent, _topic_index, _latest_15


def _search_topics(topic_index: pd.DataFrame, query: str) -> pd.DataFrame:
    q = query.strip()
    if len(q) <= 1:
        return topic_index.iloc[:0]

    # 2-char uppercase only (abbreviations like "AI", "EP")
    if len(q) == 2:
        if q != q.upper():
            return topic_index.iloc[:0]
        pattern = r'\b' + re.escape(q) + r'\b'
        mask = topic_index["policy_topic"].str.contains(pattern, case=True, na=False, regex=True)
        for syn in _SYNONYMS.get(q.upper(), []):
            syn_pat = r'\b' + re.escape(syn) + r'\b'
            mask = mask | topic_index["policy_topic"].str.contains(syn_pat, case=False, na=False, regex=True)
        return topic_index[mask]

    tokens = q.split()

    if len(tokens) == 1:
        # Single word: word-boundary match
        pattern = r'\b' + re.escape(q) + r'\b'
        mask = topic_index["policy_topic"].str.contains(pattern, case=False, na=False, regex=True)
        for syn in _SYNONYMS.get(q.upper(), []):
            syn_pat = r'\b' + re.escape(syn) + r'\b'
            mask = mask | topic_index["policy_topic"].str.contains(syn_pat, case=False, na=False, regex=True)
        return topic_index[mask]

    # Multi-word query: each token must appear somewhere in the topic (AND logic)
    # This handles "AI act" matching "Regulation on artificial intelligence (AI Act)"
    topics_lower = topic_index["policy_topic"].str.lower()
    mask = pd.Series([True] * len(topic_index), index=topic_index.index)
    for token in tokens:
        token_l = token.lower()
        # Expand abbreviations per token
        token_syns = _SYNONYMS.get(token.upper(), [token_l])
        if token_l not in token_syns:
            token_syns = [token_l] + list(token_syns)
        token_mask = pd.Series([False] * len(topic_index), index=topic_index.index)
        for syn in token_syns:
            token_mask = token_mask | topics_lower.str.contains(re.escape(syn), na=False, regex=True)
        mask = mask & token_mask
    return topic_index[mask]


def _get_suggestions(topic_index: pd.DataFrame, query: str) -> list[tuple[str, int]]:
    matched = _search_topics(topic_index, query)
    if matched.empty:
        return []
    q_lower = query.lower()
    starts = matched[matched["policy_topic"].str.lower().str.startswith(q_lower)]
    others = matched[~matched["policy_topic"].str.lower().str.startswith(q_lower)]
    ranked = pd.concat([starts, others]).head(15)
    return [(row["policy_topic"], int(row["n"])) for _, row in ranked.iterrows()]


from eu_dataset_loader import get_available_years as _get_available_years
_available_years = _get_available_years() or list(range(2019, 2027))
_default_years   = tuple(sorted(_available_years)[-3:])
_selected_years  = tuple(st.session_state.get("selected_years", _default_years))
votes_df, _hist_df, _recent_df, _group_behavior, _comparison, _has_recent, _topic_index, _latest_15 = _preload(years=_selected_years)

# ---------------------------------------------------------------------------
# Unsubscribe handler
# ---------------------------------------------------------------------------
_unsub_email = st.query_params.get("unsubscribe", "")
if _unsub_email:
    try:
        from email_alerts import remove_subscriber as _remove_subscriber
        _result = _remove_subscriber(_unsub_email.strip().lower())
        if _result == "ok":
            st.success(f"✅ {_unsub_email} a été désabonné(e).")
        else:
            st.warning("Une erreur s'est produite. Contactez-nous si le problème persiste.")
    except Exception:
        st.warning("Désabonnement temporairement indisponible.")
    st.query_params.clear()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("EU Parliament")
    st.caption("Vote Tracker")

    if st.button(t("home"), use_container_width=True, help=t("home_help")):
        st.session_state.pop("main_search", None)
        st.session_state.pop("_combined_mode", None)
        st.query_params.clear()
        st.rerun()
    st.divider()

    parquet_exists  = (_DATA_DIR / "processed" / "eu_votes_real.parquet").exists()
    real_csv_exists = (_DATA_DIR / "processed" / "eu_votes_real.csv").exists()
    sample_exists   = (_DATA_DIR / "raw" / "eu_votes_sample.csv").exists()
    live_files      = list((_DATA_DIR / "recent").glob("*.csv")) if (_DATA_DIR / "recent").exists() else []

    if parquet_exists:
        st.success(f"\U0001f4e6 {len(votes_df):,} {t('votes_loaded')}")
    elif real_csv_exists:
        st.info(f"\U0001f4c4 {len(votes_df):,} {t('votes_loaded')} (CSV)")
    elif sample_exists:
        st.warning(f"\U0001f52c Sample data")
    else:
        st.warning(f"⚡ {len(votes_df):,} {t('votes_loaded')} (fallback)")

    if live_files:
        st.success(t("live_included"))

    st.divider()
    st.subheader(t("filters"))

    # Year selector — reloads data for selected years
    _yr_selection = st.multiselect(
        "📅 Years", options=_available_years,
        default=list(_selected_years),
        key="year_picker",
    )
    if _yr_selection and tuple(sorted(_yr_selection)) != _selected_years:
        st.session_state["selected_years"] = tuple(sorted(_yr_selection))
        st.rerun()

    valid_dates = votes_df["date"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        date_range = st.date_input(t("date_range"), value=(min_date, max_date), min_value=min_date, max_value=max_date)
    else:
        date_range = None

    all_groups = sorted(votes_df["political_group"].dropna().unique().tolist())
    _g1, _g2 = st.columns(2)
    if _g1.button(t("select_all"), use_container_width=True):
        st.session_state["group_filter"] = all_groups
        st.rerun()
    if _g2.button(t("clear_all"), use_container_width=True):
        st.session_state["group_filter"] = []
        st.rerun()
    selected_groups = st.multiselect(
        "Political groups", options=all_groups, default=all_groups,
        key="group_filter", label_visibility="collapsed",
    )
    if not selected_groups:
        st.warning(t("select_all") + "...")

    st.divider()

    if st.button(t("refresh"), use_container_width=True, help=t("refresh_help")):
        with st.spinner(t("refreshing")):
            try:
                import ep_live_fetcher
                ep_live_fetcher.run()
                _preload.clear()
                st.success(t("refreshed"))
                st.rerun()
            except Exception as exc:
                st.error(f"{t('refresh_failed')}: {exc}")

# ---------------------------------------------------------------------------
# Filters (lazy — applied only when a topic is selected)
# ---------------------------------------------------------------------------

_date_start = pd.Timestamp(date_range[0]) if date_range and len(date_range) == 2 else None
_date_end   = (pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)) if date_range and len(date_range) == 2 else None
_groups_active = set(selected_groups) if selected_groups and set(selected_groups) != set(all_groups) else None

def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if _date_start and _date_end:
        df = df[(df["date"] >= _date_start) & (df["date"] < _date_end)]
    if _groups_active:
        df = df[df["political_group"].isin(_groups_active)]
    return df

# ---------------------------------------------------------------------------
# Search state
# ---------------------------------------------------------------------------

# ── Deep-link: load topic from URL ?q=... on first visit ────────────────────
if "main_search" not in st.session_state:
    _url_q = st.query_params.get("q", "")
    if _url_q:
        st.session_state["main_search"] = _url_q

if "search_override" in st.session_state:
    _override = st.session_state.pop("search_override")
    if _override.startswith("__ALL__:"):
        default_val = _override[len("__ALL__:"):]
        st.session_state["_combined_mode"] = default_val
    else:
        default_val = _override
        st.session_state.pop("_combined_mode", None)
    st.session_state["main_search"] = default_val
else:
    default_val = st.session_state.get("main_search", "")
    if default_val != st.session_state.get("_combined_mode", ""):
        st.session_state.pop("_combined_mode", None)

# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------

st.title(t("title"))
st.markdown(
    f"<p style='color:#6b7280;font-size:1.05rem;margin-top:-0.5rem;'>"
    f"{t('subtitle', n=len(votes_df))}</p>",
    unsafe_allow_html=True,
)

if DEMO_MODE:
    st.info("**Demo Mode** — dataset capped at 5,000 rows.")

_, search_col, _ = st.columns([1, 4, 1])
with search_col:
    query = st.text_input(
        "Search", value=default_val, key="main_search",
        placeholder=t("placeholder"),
        label_visibility="collapsed",
    )
    st.markdown(
        f'<p class="search-hint">{t("search_hint")}</p>',
        unsafe_allow_html=True,
    )

    matched_index = _search_topics(_topic_index, query) if query else _topic_index.iloc[:0]
    all_matching  = matched_index["policy_topic"].tolist()
    suggestions   = _get_suggestions(_topic_index, query) if query else []

    if suggestions:
        if len(all_matching) > 1:
            total_v = int(matched_index["n"].sum())
            btn_col, _ = st.columns([3, 1])
            with btn_col:
                if st.button(t("see_all_combined", n=len(all_matching), v=total_v),
                             key="pill_all", use_container_width=True):
                    st.session_state["search_override"] = "__ALL__:" + query
                    st.rerun()

        for row_start in range(0, len(suggestions), 3):
            row = suggestions[row_start : row_start + 3]
            pill_cols = st.columns(len(row))
            for i, (topic_name, vote_n) in enumerate(row):
                display = (topic_name[:50] + "..." if len(topic_name) > 50 else topic_name)
                if pill_cols[i].button(f"{display} · {vote_n:,}", key=f"pill_{row_start}_{i}", use_container_width=True):
                    st.session_state["search_override"] = topic_name
                    st.rerun()
        if len(all_matching) > 15:
            with st.expander(t("see_all_list", n=len(all_matching))):
                for _, row_data in matched_index.iterrows():
                    tn = str(row_data["policy_topic"])
                    n  = int(row_data["n"])
                    display_full = (tn[:80] + "...") if len(tn) > 80 else tn
                    if st.button(f"{display_full} · {n:,} votes", key=f"full_{hash(tn)}", use_container_width=True):
                        st.session_state["search_override"] = tn
                        st.rerun()
    elif query and (len(query) >= 3 or (len(query) == 2 and query == query.upper())):
        st.markdown(f'<p style="color:#9ca3af;font-size:0.85rem;text-align:center;">{t("no_results")}</p>', unsafe_allow_html=True)

topic = None
combined_mode = st.session_state.get("_combined_mode") == query

if query:
    if combined_mode:
        topic = t("all_topics_label", q=query)
    else:
        exact = _topic_index[_topic_index["policy_topic"] == query]
        if not exact.empty:
            topic = query
        elif len(all_matching) == 1:
            topic = all_matching[0]
        elif len(all_matching) > 1:
            topic = st.selectbox(t("n_match_pick", n=len(all_matching)), all_matching)

# ---------------------------------------------------------------------------
# Topic view
# ---------------------------------------------------------------------------

if topic:
    if combined_mode:
        matching_names = set(all_matching)
        topic_df = _apply_filters(votes_df[votes_df["policy_topic"].isin(matching_names)])
    else:
        topic_df = _apply_filters(votes_df[votes_df["policy_topic"] == topic])

    t_dates = topic_df["date"].dropna()
    d_range_str = f"{t_dates.min().strftime('%b %Y')} - {t_dates.max().strftime('%b %Y')}" if not t_dates.empty else "-"
    n_topics_str = t("across_topics", n=topic_df["policy_topic"].nunique()) if combined_mode else ""

    # Update URL so the page is shareable
    st.query_params["q"] = query

    _share_url = f"?q={query.replace(' ', '+')}"
    st.markdown(
        f'<div class="topic-bar"><strong>{topic}</strong><br>'
        f'<span style="color:#6b7280;font-size:0.9rem;">{len(topic_df):,} votes{n_topics_str} &nbsp;·&nbsp; {d_range_str}</span>'
        f'&nbsp;&nbsp;<a href="{_share_url}" style="font-size:0.78rem;color:#2563eb;text-decoration:none;" '
        f'title="Copy link to share this vote analysis">🔗 Share</a></div>',
        unsafe_allow_html=True,
    )

    st.subheader(t("how_voted"))
    group_votes = (
        topic_df.groupby(["political_group", "vote"]).size()
        .unstack(fill_value=0).reindex(columns=["FOR", "AGAINST", "ABSTAIN"], fill_value=0)
    )
    if not group_votes.empty:
        group_votes["Total"] = group_votes.sum(axis=1)
        for col in ("FOR", "AGAINST", "ABSTAIN"):
            group_votes[f"{col}_%"] = (group_votes[col] / group_votes["Total"].replace(0, 1) * 100).round(1)
        plot_df = group_votes.sort_values("FOR_%", ascending=True).reset_index()
        fig = px.bar(
            plot_df, y="political_group", x=["FOR_%", "AGAINST_%", "ABSTAIN_%"],
            orientation="h", barmode="stack",
            color_discrete_map={"FOR_%": "#2563eb", "AGAINST_%": "#ef4444", "ABSTAIN_%": "#d1d5db"},
            title=t("vote_breakdown"),
        )
        lbl = {"FOR_%": t("for_label"), "AGAINST_%": t("against_label"), "ABSTAIN_%": t("abstain_label")}
        for trace in fig.data:
            trace.name = lbl.get(trace.name, trace.name)
            trace.hovertemplate = "%{y}: %{x:.1f}%<extra>" + trace.name + "</extra>"
        fig.update_layout(
            xaxis_title="", yaxis_title="", legend_title_text="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=20, t=55, b=10),
            height=max(300, len(plot_df) * 40 + 90), title_font_size=14,
        )
        fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=True, gridcolor="#f3f4f6", zeroline=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t("no_vote_data"))

    st.divider()
    st.subheader(t("overall_result"))

    vote_counts = topic_df["vote"].value_counts()
    total_v = len(topic_df)
    for_n    = int(vote_counts.get("FOR", 0))
    against_n = int(vote_counts.get("AGAINST", 0))
    abstain_n = int(vote_counts.get("ABSTAIN", 0))
    for_pct     = round(for_n    / total_v * 100, 1) if total_v else 0.0
    against_pct = round(against_n / total_v * 100, 1) if total_v else 0.0
    abstain_pct = round(abstain_n / total_v * 100, 1) if total_v else 0.0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="result-card" style="background:#eff6ff;"><div class="icon">✅</div><div class="pct" style="color:#2563eb;">{for_pct:.1f}%</div><div class="label">{t("for_label")} — {for_n:,} votes</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="result-card" style="background:#fff1f2;"><div class="icon">❌</div><div class="pct" style="color:#ef4444;">{against_pct:.1f}%</div><div class="label">{t("against_label")} — {against_n:,} votes</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="result-card" style="background:#f9fafb;"><div class="icon">○</div><div class="pct" style="color:#6b7280;">{abstain_pct:.1f}%</div><div class="label">{t("abstain_label")} — {abstain_n:,} votes</div></div>', unsafe_allow_html=True)

    if for_n > against_n:
        verdict_html = f'<span class="verdict-passed">{t("passed")}</span>'
    elif for_n == against_n:
        verdict_html = f'<span class="verdict-contested">{t("tied")}</span>'
    else:
        verdict_html = f'<span class="verdict-rejected">{t("rejected")}</span>'
    st.markdown(f'<div style="margin-top:1rem;">{verdict_html}</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader(t("ai_section"))

    if DEMO_MODE:
        st.info("AI Analysis is disabled in Demo Mode.")
    else:
        _cache_key = f"__ai_{hash(topic)}_{st.session_state.get('lang','EN')}"
        if st.button(t("ai_button"), type="primary"):
            from analysis_agent import build_summary
            topic_summary = build_summary(topic_df)
            if not topic_summary:
                st.warning(t("ai_no_data"))
            else:
                if _cache_key in st.session_state:
                    insight = st.session_state[_cache_key]
                else:
                    with st.spinner(t("ai_spinning")):
                        insight = generate_ai_insight(topic_summary, topic, lang=t("lang_name"))
                    st.session_state[_cache_key] = insight
                _errors = {
                    "NO_KEY":     t("ai_no_key"),
                    "BAD_KEY":    t("ai_bad_key"),
                    "RATE_LIMIT": t("ai_rate_limit"),
                    "TIMEOUT":    t("ai_timeout"),
                    "API_ERROR":  t("ai_error"),
                }
                if insight in _errors:
                    st.warning(_errors[insight])
                else:
                    st.markdown(f'<div class="ai-card">{insight}</div>', unsafe_allow_html=True)
        elif _cache_key in st.session_state:
            insight = st.session_state[_cache_key]
            _errors = {"NO_KEY", "BAD_KEY", "RATE_LIMIT", "TIMEOUT", "API_ERROR"}
            if insight not in _errors:
                st.markdown(f'<div class="ai-card">{insight}</div>', unsafe_allow_html=True)

    st.divider()

# ---------------------------------------------------------------------------
# Homepage — latest 15 votes
# ---------------------------------------------------------------------------

if not query:
    # ── Hero banner ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1e3a8a 0%,#1d4ed8 50%,#0369a1 100%);
                border-radius:16px;padding:2.5rem 2rem 2rem 2rem;
                margin-bottom:1.8rem;color:white;text-align:center;">
        <div style="font-size:2.8rem;margin-bottom:0.4rem;">🏛️</div>
        <div style="font-size:1.6rem;font-weight:800;margin-bottom:0.7rem;letter-spacing:-0.02em;">
            {t("onboard_title")}
        </div>
        <div style="font-size:1rem;opacity:0.88;line-height:1.65;max-width:640px;margin:0 auto;">
            {t("onboard_body")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick-start examples ─────────────────────────────────────────────────
    st.markdown(
        f"<p style='color:#6b7280;font-size:0.9rem;font-weight:600;margin-bottom:0.5rem;'>"
        f"{t('try_example')}</p>",
        unsafe_allow_html=True,
    )
    _examples = ["AI Act", "Ukraine", "Climate", "Migration", "Digital Services Act"]
    _ex_cols = st.columns(len(_examples))
    for _i, _ex in enumerate(_examples):
        if _ex_cols[_i].button(_ex, key=f"ex_{_ex}", use_container_width=True):
            st.session_state["search_override"] = _ex
            st.rerun()

    st.divider()
    st.subheader(t("latest_title"))
    st.caption(t("latest_caption"))

    for _, row_data in _latest_15.iterrows():
        tn = row_data["policy_topic"]
        d  = row_data["date"]
        date_str = d.strftime("%d %b %Y") if pd.notna(d) else ""
        display_t = (tn[:90] + "...") if len(tn) > 90 else tn
        col_btn, col_date = st.columns([5, 1])
        with col_btn:
            if st.button(f"\U0001f5f3 {display_t}", key=f"recent_{hash(tn)}", use_container_width=True):
                st.session_state["search_override"] = tn
                st.rerun()
        with col_date:
            st.markdown(f"<p style='color:#9ca3af;font-size:0.8rem;text-align:right;margin-top:0.5rem;'>{date_str}</p>", unsafe_allow_html=True)

    st.divider()

# ---------------------------------------------------------------------------
# Recent political changes
# ---------------------------------------------------------------------------

if _has_recent:
    st.header(t("recent_changes"))
    st.caption(t("recent_caption"))

    st.subheader(t("hist_insight"))
    if not _group_behavior.empty:
        st.dataframe(_group_behavior.set_index("political_group"), use_container_width=True)

    st.subheader(t("recent_analysis"))
    if not _recent_df.empty and _comparison:
        try:
            summary = _comparison.get("summary", {})
            mc_group  = summary.get("most_changed_group") or "-"
            mc_topic  = summary.get("most_changed_topic") or "-"
            pol_change = summary.get("overall_polarization_change")
            pol_label  = f"{pol_change:+.1f} pp" if pol_change is not None else "-"
            pol_color  = "normal" if pol_change is None or abs(pol_change) < 1.0 else ("inverse" if pol_change > 0 else "normal")
            m1, m2, m3 = st.columns(3)
            m1.metric(t("most_chg_group"), mc_group)
            m2.metric(t("most_chg_topic"), mc_topic)
            m3.metric(t("polarization"), pol_label, delta=pol_label, delta_color=pol_color)
            st.subheader(t("ai_summary"))
            if DEMO_MODE:
                st.info("AI Summary disabled in Demo Mode.")
            else:
                explanation = explain_political_changes(_comparison)
                st.write(explanation)
        except Exception as exc:
            st.warning(f"{t('recent_failed')}: {exc}")
    st.divider()

# ── Newsletter subscription ──────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="color:#6b7280;font-size:0.82rem;line-height:1.7;">
    <strong style="color:#374151;">{t("about_tool_title")}</strong><br>
    {t("about_tool_body")}<br><br>
    <strong style="color:#374151;">{t("about_data_title")}</strong><br>
    🏛️ <a href="https://data.europarl.europa.eu" target="_blank" style="color:#2563eb;">EU Parliament Open Data Portal</a> — official roll-call votes 2019–2026<br>
    🔴 <a href="https://howtheyvote.eu" target="_blank" style="color:#2563eb;">HowTheyVote.eu</a> — live vote feed (last 30 days)<br>
    🤖 AI analysis powered by <a href="https://groq.com" target="_blank" style="color:#2563eb;">Groq</a> (Llama 3.1)<br><br>
    <strong style="color:#374151;">{t("about_transp_title")}</strong><br>
    {t("about_transparency")}
</div>
""", unsafe_allow_html=True)
