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
    initial_sidebar_state="collapsed",
)

st.markdown('<meta name="google-site-verification" content="ymZ5DtlnckmG4aJ3DT4_OAbB1vsTcUXJpOoklHcXO58" />', unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

/* ── Design tokens ── */
:root {
  --bg:          #F4F6FB;
  --bg2:         #E9ECF5;
  --surface:     #FFFFFF;
  --navy:        #0F1B3D;
  --navy-soft:   #334155;
  --navy-faint:  #64748B;
  --blue:        #2563EB;
  --blue-deep:   #1D4ED8;
  --blue-pale:   #EFF6FF;
  --line:        rgba(15,27,61,0.09);
  --line-soft:   rgba(15,27,61,0.05);
  --sh-sm:  0 1px 3px rgba(15,27,61,0.05), 0 4px 16px rgba(15,27,61,0.06);
  --sh-md:  0 8px 28px rgba(15,27,61,0.09), 0 2px 6px rgba(15,27,61,0.04);
  --sh-lg:  0 24px 64px rgba(15,27,61,0.14), 0 8px 24px rgba(15,27,61,0.08);
  --radius: 18px;
  --ease:   cubic-bezier(0.22,0.61,0.36,1);
}

/* ── Streamlit chrome hide ── */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
.stDeployButton {display:none;}
[data-testid="stToolbarActions"] {display:none !important;}
[data-testid="stStatusWidget"]   {display:none !important;}
header[data-testid="stHeader"]   {background:transparent !important;border-bottom:none !important;}
[data-testid="stDecoration"]     {display:none;}
[data-testid="manage-app-button"]{display:none !important;}
[class*="viewerBadge"]           {display:none !important;}
[class*="ViewerBadge"]           {display:none !important;}
a[href*="streamlit.io"]          {display:none !important;}
a[href*="share.streamlit"]       {display:none !important;}
iframe:not([title])              {display:none !important;}
iframe[src*="streamlit"]         {display:none !important;}
iframe[src*="badge"]             {display:none !important;}

/* ── Global base ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', system-ui, sans-serif !important;
    background: var(--bg) !important;
    color: var(--navy) !important;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main .block-container {
    background: var(--bg) !important;
    padding-top: 2rem !important;
}
h1, h2, h3, h4, .stTitle {
    font-family: 'Sora', sans-serif !important;
    color: var(--navy) !important;
    letter-spacing: -0.02em;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
/* Text elements in sidebar — light colored */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] .stTitle,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stCaption {
    color: #e2e8f0 !important;
}
/* Sidebar buttons — translucent on dark bg, light text */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.1) !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.2) !important;
    border-color: rgba(255,255,255,0.32) !important;
    transform: none !important;
    color: white !important;
}
/* Multiselect tags in sidebar */
[data-testid="stSidebar"] [data-testid="stMultiSelectTag"] {
    background: rgba(37,99,235,0.7) !important;
    color: white !important;
}
/* Date input in sidebar */
[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important;
    border-color: rgba(255,255,255,0.15) !important;
}

/* ── Sidebar toggle button ── */
@keyframes menu-pulse {
    0%,100% { box-shadow: 0 4px 20px rgba(37,99,235,0.55), 0 0 0 4px rgba(37,99,235,0.14); }
    50%      { box-shadow: 0 4px 28px rgba(37,99,235,0.8),  0 0 0 8px rgba(37,99,235,0.07); }
}
[data-testid="collapsedControl"] {
    display: flex !important;
    align-items: center !important;
    z-index: 9999 !important;
}
[data-testid="collapsedControl"] button,
[data-testid="collapsedControl"] > button {
    width: 3rem !important;
    height: 3rem !important;
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    color: white !important;
    border-radius: 50% !important;
    border: 3px solid rgba(255,255,255,0.3) !important;
    box-shadow: 0 4px 20px rgba(37,99,235,0.55), 0 0 0 4px rgba(37,99,235,0.14) !important;
    animation: menu-pulse 2.5s ease-in-out infinite !important;
    opacity: 1 !important;
}
[data-testid="collapsedControl"] svg {
    color: white !important;
    stroke: white !important;
    width: 1.3rem !important;
    height: 1.3rem !important;
}
@media (max-width: 768px) {
    [data-testid="collapsedControl"] {
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
    }
    [data-testid="collapsedControl"] button,
    [data-testid="collapsedControl"] > button {
        width: 4rem !important;
        height: 4rem !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
        border: 3px solid rgba(255,255,255,0.4) !important;
        box-shadow: 0 6px 24px rgba(37,99,235,0.75), 0 0 0 7px rgba(37,99,235,0.2) !important;
    }
    [data-testid="collapsedControl"] svg {
        width: 1.7rem !important;
        height: 1.7rem !important;
    }
    .main .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 4rem !important;
    }
    .result-card .pct { font-size: 1.3rem !important; font-weight: 800 !important; }
    .result-card .label { font-size: 0.65rem !important; }
    .topic-bar { font-size: 0.88rem !important; }
    .ai-card { font-size: 0.84rem !important; }
}

/* ── Hero ── */
.eu-hero {
    position: relative;
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 2rem;
    padding: 3rem 2.5rem 2.5rem;
    background: linear-gradient(145deg, #0F1B3D 0%, #1D4ED8 60%, #1E40AF 100%);
}
.hero-grid-overlay {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
    background-size: 52px 52px;
    -webkit-mask-image: radial-gradient(ellipse 80% 70% at 60% 30%, #000 0%, transparent 80%);
    mask-image:         radial-gradient(ellipse 80% 70% at 60% 30%, #000 0%, transparent 80%);
}
.hero-blob-1 {
    position: absolute;
    width: 500px; height: 500px;
    top: -180px; right: -120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(96,165,250,0.35) 0%, transparent 65%);
    filter: blur(50px);
    animation: blob-float1 18s ease-in-out infinite;
}
.hero-blob-2 {
    position: absolute;
    width: 380px; height: 380px;
    bottom: -160px; left: -100px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(147,197,253,0.25) 0%, transparent 70%);
    filter: blur(40px);
    animation: blob-float2 22s ease-in-out infinite;
}
@keyframes blob-float1 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-28px,32px)} }
@keyframes blob-float2 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(26px,-24px)} }
.hero-inner { position: relative; z-index: 1; }
.hero-eyebrow {
    display: inline-block;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.9);
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    padding: 0.4em 1em;
    border-radius: 999px;
    margin-bottom: 1.1rem;
    backdrop-filter: blur(4px);
}
.hero-title {
    font-family: 'Sora', sans-serif !important;
    font-size: clamp(2rem, 4.5vw, 3.4rem) !important;
    font-weight: 800 !important;
    color: white !important;
    line-height: 1.1 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 0.9rem !important;
}
.hero-title .accent { color: #93C5FD; display: block; }
.hero-sub {
    font-size: clamp(0.95rem, 1.8vw, 1.1rem);
    color: rgba(255,255,255,0.78);
    max-width: 580px;
    line-height: 1.7;
    margin-bottom: 1.5rem;
}
.hero-stats {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1rem 1.5rem;
}
.hero-stat { display: flex; align-items: baseline; gap: 0.35em; }
.hero-stat-num {
    font-family: 'Sora', sans-serif;
    font-weight: 800;
    font-size: 1.5rem;
    color: white;
}
.hero-stat-label { font-size: 0.82rem; color: rgba(255,255,255,0.6); }
.hero-stat-sep { color: rgba(255,255,255,0.25); font-size: 1.2rem; }

/* ── Search bar ── */
.stTextInput > div > div > input {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    border: 2px solid var(--line) !important;
    border-radius: 14px !important;
    background: var(--surface) !important;
    color: var(--navy) !important;
    padding: 0.85rem 1.2rem !important;
    box-shadow: var(--sh-sm) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 4px rgba(37,99,235,0.1), var(--sh-sm) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--navy-faint) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    border-radius: 10px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    background: var(--surface) !important;
    color: var(--navy-soft) !important;
    border: 1.5px solid var(--line) !important;
    box-shadow: var(--sh-sm) !important;
    transition: all 0.2s var(--ease) !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: var(--blue-pale) !important;
    border-color: var(--blue) !important;
    color: var(--blue-deep) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--sh-md) !important;
}
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--blue) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 0 6px 18px rgba(37,99,235,0.3) !important;
}
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: var(--blue-deep) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 26px rgba(37,99,235,0.38) !important;
}

/* ── Topic bar ── */
.topic-bar {
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 4px solid var(--blue);
    padding: 1rem 1.4rem;
    border-radius: var(--radius);
    margin-bottom: 1.5rem;
    font-size: 1.02rem;
    line-height: 1.5;
    box-shadow: var(--sh-sm);
}

/* ── Verdict badges ── */
.verdict-passed    { background:#dcfce7; color:#15803d; padding:5px 16px; border-radius:999px; font-weight:700; font-size:0.9rem; display:inline-block; margin-top:0.8rem; letter-spacing:0.02em; }
.verdict-rejected  { background:#fee2e2; color:#b91c1c; padding:5px 16px; border-radius:999px; font-weight:700; font-size:0.9rem; display:inline-block; margin-top:0.8rem; letter-spacing:0.02em; }
.verdict-contested { background:#fef9c3; color:#854d0e; padding:5px 16px; border-radius:999px; font-weight:700; font-size:0.9rem; display:inline-block; margin-top:0.8rem; letter-spacing:0.02em; }

/* ── Result cards ── */
.result-card {
    text-align: center;
    padding: 1.4rem 1rem;
    border-radius: var(--radius);
    background: var(--surface);
    border: 1px solid var(--line-soft);
    box-shadow: var(--sh-sm);
    transition: transform 0.2s var(--ease), box-shadow 0.2s;
}
.result-card:hover { transform: translateY(-3px); box-shadow: var(--sh-md); }
.result-card .icon { font-size: 1.8rem; margin-bottom: 0.3rem; }
.result-card .pct  { font-family: 'Sora', sans-serif; font-size: 2.6rem; font-weight: 800; line-height: 1.1; color: var(--navy); }
.result-card .label{ font-size: 0.88rem; color: var(--navy-faint); margin-top: 0.3rem; font-weight: 500; }

/* ── AI card ── */
.ai-card {
    background: var(--blue-pale);
    border: 1px solid #BFDBFE;
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-top: 0.5rem;
    white-space: pre-wrap;
    font-size: 0.95rem;
    line-height: 1.75;
    box-shadow: var(--sh-sm);
    color: var(--navy);
}

/* ── Search hint ── */
.search-hint { text-align: center; color: var(--navy-faint); font-size: 0.8rem; margin-top: 0.4rem; }

/* ── Homepage banner ── */
.home-banner {
    background: linear-gradient(145deg, #0F1B3D 0%, #1D4ED8 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    color: white;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: var(--sh-lg);
}
.home-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255,255,255,0.07) 1.5px, transparent 1.6px);
    background-size: 24px 24px;
}
.home-banner-inner { position: relative; z-index: 1; }
.home-banner-icon  { font-size: 2.5rem; margin-bottom: 0.5rem; }
.home-banner-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(1.3rem, 3vw, 1.8rem);
    font-weight: 800;
    margin-bottom: 0.7rem;
    letter-spacing: -0.02em;
}
.home-banner-body {
    font-size: clamp(0.9rem, 1.5vw, 1rem);
    opacity: 0.85;
    line-height: 1.7;
    max-width: 600px;
    margin: 0 auto;
}

/* ── Latest votes list ── */
.vote-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface);
    border: 1px solid var(--line-soft);
    border-radius: 12px;
    margin-bottom: 0.45rem;
    box-shadow: var(--sh-sm);
    transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
    cursor: pointer;
}
.vote-row:hover { transform: translateX(4px); border-color: var(--blue); box-shadow: var(--sh-md); }

/* ── Language picker ── */
.lang-label {
    text-align: right;
    font-size: 0.7rem;
    color: var(--navy-faint);
    margin-bottom: 2px;
    margin-top: 0.2rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-family: 'Sora', sans-serif;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--line-soft);
    border-radius: var(--radius);
    padding: 1rem 1.2rem !important;
    box-shadow: var(--sh-sm);
}
[data-testid="stMetricLabel"] { font-family: 'Inter', sans-serif; color: var(--navy-faint) !important; font-size: 0.82rem !important; }
[data-testid="stMetricValue"] { font-family: 'Sora', sans-serif !important; color: var(--navy) !important; font-weight: 700 !important; }

/* ── Dividers ── */
hr { border-color: var(--line) !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* ── Reveal animation ── */
@keyframes fade-up { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
.fade-up { animation: fade-up 0.55s var(--ease) both; }
</style>
<script>
(function() {
    var HIDE = [
        '[data-testid="stStatusWidget"]',
        '[data-testid="manage-app-button"]',
        '[class*="viewerBadge"]',
        '[class*="ViewerBadge"]',
        'a[href*="streamlit.io"]',
        'iframe[src*="badge"]'
    ];
    function hideAll() {
        HIDE.forEach(function(sel) {
            try {
                document.querySelectorAll(sel).forEach(function(el) {
                    el.style.setProperty("display", "none", "important");
                    el.style.setProperty("visibility", "hidden", "important");
                });
            } catch(e) {}
        });
    }
    hideAll();
    var obs = new MutationObserver(hideAll);
    obs.observe(document.documentElement, {childList: true, subtree: true});
})();
</script>
""", unsafe_allow_html=True)

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")
_DEMO_ROW_LIMIT = 5000
_DATA_DIR = Path(__file__).parent.parent / "data"

_SYNONYMS: dict[str, list[str]] = {
    # English abbreviations
    "AI":   ["artificial intelligence", "intelligence artificielle"],
    "EP":   ["european parliament"],
    "DSA":  ["digital services"],
    "GDPR": ["data protection"],
    "NATO": ["north atlantic", "defence alliance"],
    # French
    # Countries
    "MEXIQUE": ["mexico"], "MEXIKO": ["mexico"],
    "ALLEMAGNE": ["germany"],
    "CHINE": ["china"],
    "RUSSIE": ["russia"],
    "TURQUIE": ["turkey"],
    "POLOGNE": ["poland"],
    "HONGRIE": ["hungary"],
    "ISRAËL": ["israel"], "ISRAEL": ["israel"],
    "SYRIE": ["syria"],
    "INDE": ["india"],
    "JAPON": ["japan"],
    "CORÉE": ["korea"], "COREE": ["korea"],
    "ÉTATS-UNIS": ["united states"], "ETATS-UNIS": ["united states"],
    "ROYAUME-UNI": ["united kingdom"],
    "IRAN": ["iran"],
    "LIBYE": ["libya"],
    "MAROC": ["morocco"],
    "TUNISIE": ["tunisia"],
    "ALGÉRIE": ["algeria"], "ALGERIE": ["algeria"],
    "ÉGYPTE": ["egypt"], "EGYPTE": ["egypt"],
    "LIBAN": ["lebanon"],
    "SERBIE": ["serbia"],
    "MOLDAVIE": ["moldova"],
    "GÉORGIE": ["georgia"], "GEORGIE": ["georgia"],
    "BIÉLORUSSIE": ["belarus"], "BIELORUSSIE": ["belarus"],
    # Topics
    "CLIMAT": ["climate"], "CLIMATIQUE": ["climate"], "CLIMATIQUES": ["climate"],
    "MIGRATION": ["migration"], "MIGRATIONS": ["migration"],
    "IMMIGRATION": ["migration"],
    "RÉFUGIÉS": ["refugees"], "REFUGIES": ["refugees"],
    "ARTIFICIELLE": ["artificial"],
    "ÉNERGIE": ["energy"], "ENERGIES": ["energy"],
    "ÉNERGÉTIQUE": ["energy"], "ÉNERGÉTIQUES": ["energy"],
    "DÉFENSE": ["defence", "defense"],
    "SÉCURITÉ": ["security"], "SECURITE": ["security"],
    "SANTÉ": ["health"], "SANTE": ["health"],
    "COMMERCE": ["trade"],
    "NUMÉRIQUE": ["digital"], "NUMERIQUE": ["digital"],
    "GUERRE": ["war"],
    "PAIX": ["peace"],
    "PHARMACIE": ["pharmaceutical"],
    "PHARMACEUTIQUE": ["pharmaceutical", "pharma"],
    "TRANSPORT": ["transport"],
    "PÊCHE": ["fisheries"], "PECHE": ["fisheries"],
    "AGRICULTURE": ["agriculture"],
    "ÉLECTIONS": ["elections"], "ELECTIONS": ["elections"],
    "DROITS": ["rights"],
    "FORÊT": ["forest", "deforestation"], "FORET": ["forest"],
    "NUCLÉAIRE": ["nuclear"], "NUCLEAIRE": ["nuclear"],
    # Spanish
    "ALEMANIA": ["germany"],
    "RUSIA": ["russia"],
    "TURQUÍA": ["turkey"], "TURQUIA": ["turkey"],
    "POLONIA": ["poland"],
    "HUNGRÍA": ["hungary"], "HUNGRIA": ["hungary"],
    "INDIA": ["india"],
    "JAPÓN": ["japan"], "JAPON": ["japan"],
    "COREA": ["korea"],
    "SIRIA": ["syria"],
    "REINO": ["kingdom"],
    "CLIMA": ["climate"], "CLIMÁTICO": ["climate"], "CLIMATICO": ["climate"],
    "DEFENSA": ["defence", "defense"],
    "SEGURIDAD": ["security"],
    "ARTIFICIAL": ["artificial"],
    "ENERGÍA": ["energy"], "ENERGIA": ["energy"],
    "SALUD": ["health"],
    "GUERRA": ["war"],
    "PAZ": ["peace"],
    "DIGITAL": ["digital"],
    "COMERCIO": ["trade"],
    "PRESUPUESTO": ["budget"],
    "PESCA": ["fisheries"],
    "NUCLEAR": ["nuclear"],
    "DERECHOS": ["rights"],
    "REFUGIADOS": ["refugees"],
    "MARRUECOS": ["morocco"],
    "LIBANO": ["lebanon"], "LÍBANO": ["lebanon"],
    # German
    "DEUTSCHLAND": ["germany"],
    "RUSSLAND": ["russia"],
    "TÜRKEI": ["turkey"], "TURKEI": ["turkey"],
    "KLIMA": ["climate"], "KLIMAWANDEL": ["climate change", "climate"],
    "VERTEIDIGUNG": ["defence", "defense"],
    "SICHERHEIT": ["security"],
    "KÜNSTLICHE": ["artificial"], "KUNSTLICHE": ["artificial"],
    "GESUNDHEIT": ["health"],
    "HANDEL": ["trade"],
    "HAUSHALT": ["budget"],
    "KRIEG": ["war"],
    "FRIEDEN": ["peace"],
    "VEREINIGTE": ["united"],
    "KÖNIGREICH": ["kingdom"], "KONIGREICH": ["kingdom"],
    "DIGITALE": ["digital"], "DIGITALISIERUNG": ["digital"],
    "FISCHEREI": ["fisheries"],
    "KERNKRAFT": ["nuclear"], "KERNENERGIE": ["nuclear"],
    "RECHTE": ["rights"],
    "FLÜCHTLINGE": ["refugees"], "FLUCHTLINGE": ["refugees"],
    "MAROKKO": ["morocco"],
    # Italian
    "GERMANIA": ["germany"],
    "CINA": ["china"],
    "TURCHIA": ["turkey"],
    "UNGHERIA": ["hungary"],
    "DIFESA": ["defence", "defense"],
    "SICUREZZA": ["security"],
    "ARTIFICIALE": ["artificial"],
    "SALUTE": ["health"],
    "BILANCIO": ["budget"],
    "PACE": ["peace"],
    "PESCA": ["fisheries"],
    "NUCLEARE": ["nuclear"],
    "DIRITTI": ["rights"],
    "RIFUGIATI": ["refugees"],
    "MAROCCO": ["morocco"],
    "LIBANO": ["lebanon"],
}

# Translations
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
        "see_all_help":      "Combines all matching topics into one view so you can see the Parliament's overall position on this theme — not just one specific law.",
        "combined_note":     "📊 You are viewing **{n} topics combined**. This shows the Parliament's overall voting pattern on this theme across all related laws. To see a specific law, search again and pick one topic.",
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
        "aggregate_note":    "⚠️ These figures aggregate all recorded votes linked to this topic (multiple readings, amendments). Individual vote breakdowns may differ from other sources.",
        "ai_hint":           "Get a plain-language explanation of what this vote was about, who supported it and why — generated by AI in seconds.",
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
        "about_nav":         "👤 About",
        "contact_nav":       "✉️ Contact",
        "about_tagline":     "The story behind this project",
        "about_profile_bio": "Passionate about making European democracy legible for everyone",
        "about_why_title":   "Why I built this",
        "about_why_body":    "Like many young Europeans, I care deeply about the EU. But every time I tried to understand what was actually happening in the Parliament — what was being voted on, who stood for what — I hit the same wall.\n\nThere are resources out there — and some are genuinely excellent. But they're largely built for specialists, researchers, and political journalists. For a curious person who simply wants to understand a vote, the barrier to entry is still too high.\n\nThe EU Parliament publishes every single vote as open data. The information is *there* — but making it truly accessible requires more than just publishing it.\n\n**That gap is what I set out to close.**",
        "about_what_title":  "What this is",
        "about_what_body":   "EU Parliament Vote Tracker combines data from two sources: the **European Parliament's official Open Data Portal** for the full historical record, and **HowTheyVote.eu** for the most recent live votes — a project whose existence made this much easier to build.\n\nSearch any legislative topic. See instantly how each political group voted. And then — the part I'm most proud of — get an **AI explanation that actually makes sense**.\n\nNot a dry summary, not jargon swapped for different jargon. The AI reads the raw vote data and explains in plain language: *what this issue was actually about*, *which political families supported or opposed it and why*, and *what it means in practice for people living in Europe*. Think of it as having a knowledgeable friend walk you through it over coffee.\n\nNo editorial bias. No political agenda. Just democracy — made legible.\n\nThe project is fully open source. **My goal: make EU democracy as easy to follow as a sports score.**",
        "about_matters_title":"Why it matters",
        "about_matters_body":"Democracy works better when citizens understand it. 450 million people are affected by decisions made in this building every week, and most of them have no idea what's being debated.\n\nThis project started as a personal learning exercise and grew into something I genuinely believe in. Months of work in my spare time — because I think accessible democracy is worth building.",
        "about_hope_title":  "What I'm hoping for",
        "about_hope_body":   "If you work at an EU institution, a think tank, a civic tech organization, or a media outlet — or if you simply share the conviction that *transparency is not optional in a democracy* — I would genuinely love to hear from you.\n\nThis is just the beginning. There is so much more this could become.",
        "about_stack_1":     "Real EP open data",
        "about_stack_2":     "AI explanations",
        "about_stack_3":     "5 languages",
        "about_cta":         "✉️ Get in touch",
        "contact_page_title":"Get in Touch",
        "contact_subtitle":  "Questions, suggestions, partnership ideas — all welcome.",
        "contact_name_label":"Your name (optional)",
        "contact_email_label":"Your email address",
        "contact_msg_label": "Your message",
        "contact_send_btn":  "Send message",
        "contact_ok":        "✅ Message sent! I'll get back to you soon.",
        "contact_err":       "Something went wrong. Try again or email me directly.",
        "contact_invalid":   "Please enter a valid email address and a message.",
        "contact_direct":    "Or reach me directly:",
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
        "see_all_help":      "Regroupe tous les sujets correspondants en une seule vue pour montrer la position globale du Parlement sur ce thème — pas seulement une loi précise.",
        "combined_note":     "📊 Vous visualisez **{n} sujets combinés**. Cela montre le comportement de vote global du Parlement sur ce thème, toutes lois confondues. Pour voir une loi spécifique, faites une nouvelle recherche et choisissez un seul sujet.",
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
        "aggregate_note":    "⚠️ Ces chiffres agrègent tous les votes enregistrés sur ce sujet (plusieurs lectures, amendements). Les résultats par vote individuel peuvent différer d'autres sources.",
        "ai_hint":           "Obtenez une explication en langage simple sur ce vote, qui l'a soutenu et pourquoi — générée par IA en quelques secondes.",
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
        "about_nav":         "👤 À propos",
        "contact_nav":       "✉️ Contact",
        "about_tagline":     "L'histoire derrière ce projet",
        "about_profile_bio": "Passionné par l'accessibilité de la démocratie européenne pour tous",
        "about_why_title":   "Pourquoi j'ai créé ça",
        "about_why_body":    "Comme beaucoup de jeunes Européens, je m'intéresse profondément à l'UE. Mais chaque fois que j'essayais de comprendre ce qui se passait vraiment au Parlement — ce qui était voté, qui défendait quoi — je me heurtais au même mur.\n\nIl existe des ressources, et certaines sont vraiment excellentes. Mais elles sont en grande partie conçues pour les spécialistes, chercheurs et journalistes politiques. Pour quelqu'un qui veut simplement comprendre un vote, la barrière reste trop haute.\n\nLe Parlement européen publie chaque vote en données ouvertes. L'information *existe* — mais la rendre vraiment accessible nécessite plus que de la publier.\n\n**C'est ce fossé que j'ai voulu combler.**",
        "about_what_title":  "Ce que c'est",
        "about_what_body":   "EU Parliament Vote Tracker combine des données de deux sources : le **portail Open Data officiel du Parlement européen** pour l'historique complet, et **HowTheyVote.eu** pour les votes les plus récents — un projet dont l'existence a rendu tout cela bien plus facile à construire.\n\nRecherchez n'importe quel sujet législatif. Voyez instantanément comment chaque groupe politique a voté. Et ensuite — la partie dont je suis le plus fier — obtenez une **explication IA qui a vraiment du sens**.\n\nPas un résumé aride, pas du jargon remplacé par d'autre jargon. L'IA lit les données de vote et explique en langage clair : *de quoi il s'agissait réellement*, *quelles familles politiques ont soutenu ou s'y sont opposées et pourquoi*, et *ce que cela signifie concrètement pour les gens qui vivent en Europe*. Comme si un ami bien informé vous l'expliquait autour d'un café.\n\nAucun biais éditorial. Aucun agenda politique. Juste la démocratie — rendue lisible.\n\nLe projet est entièrement open source. **Mon objectif : rendre la démocratie européenne aussi facile à suivre qu'un score sportif.**",
        "about_matters_title":"Pourquoi c'est important",
        "about_matters_body":"La démocratie fonctionne mieux quand les citoyens la comprennent. 450 millions de personnes sont concernées par les décisions prises dans ce bâtiment chaque semaine, et la plupart ne savent pas ce qui y est débattu.\n\nCe projet a commencé comme un exercice personnel d'apprentissage et est devenu quelque chose en lequel je crois vraiment. Des mois de travail pendant mes heures libres — parce que je pense qu'une démocratie accessible vaut la peine d'être construite.",
        "about_hope_title":  "Ce que j'espère",
        "about_hope_body":   "Si vous travaillez dans une institution européenne, un think tank, une organisation de civic tech ou un média — ou si vous partagez simplement la conviction que *la transparence n'est pas optionnelle en démocratie* — je serais vraiment ravi d'échanger avec vous.\n\nC'est seulement un début. Il y a tellement plus que cela pourrait devenir.",
        "about_stack_1":     "Données ouvertes du PE",
        "about_stack_2":     "Explications IA",
        "about_stack_3":     "5 langues",
        "about_cta":         "✉️ Me contacter",
        "contact_page_title":"Contactez-moi",
        "contact_subtitle":  "Questions, suggestions, idées de collaboration — tout est bienvenu.",
        "contact_name_label":"Votre nom (optionnel)",
        "contact_email_label":"Votre adresse email",
        "contact_msg_label": "Votre message",
        "contact_send_btn":  "Envoyer",
        "contact_ok":        "✅ Message envoyé ! Je vous répondrai bientôt.",
        "contact_err":       "Une erreur est survenue. Réessayez ou contactez-moi directement.",
        "contact_invalid":   "Veuillez entrer une adresse email valide et un message.",
        "contact_direct":    "Ou contactez-moi directement :",
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
        "see_all_help":      "Combina todos los temas relacionados en una sola vista para mostrar la posición general del Parlamento sobre este tema, no solo una ley específica.",
        "combined_note":     "📊 Estás viendo **{n} temas combinados**. Esto muestra el patrón de votación general del Parlamento sobre este tema en todas las leyes relacionadas. Para ver una ley específica, busca de nuevo y elige un solo tema.",
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
        "aggregate_note":    "⚠️ Estas cifras agregan todos los votos registrados sobre este tema (varias lecturas, enmiendas). Los desglosados individuales pueden diferir de otras fuentes.",
        "ai_hint":           "Obtenga una explicación en lenguaje sencillo sobre esta votación, quién la apoyó y por qué — generada por IA en segundos.",
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
        "about_nav":         "👤 Acerca de",
        "contact_nav":       "✉️ Contacto",
        "about_tagline":     "La historia detrás de este proyecto",
        "about_profile_bio": "Apasionado por hacer la democracia europea accesible para todos",
        "about_why_title":   "Por qué lo construí",
        "about_why_body":    "Como muchos jóvenes europeos, me preocupa profundamente la UE. Pero cada vez que intentaba entender lo que realmente ocurría en el Parlamento — qué se votaba, quién defendía qué — chocaba con el mismo muro.\n\nExisten recursos, y algunos son realmente excelentes. Pero están diseñados principalmente para especialistas, investigadores y periodistas políticos. Para alguien que simplemente quiere entender un voto, la barrera de entrada sigue siendo demasiado alta.\n\nEl Parlamento Europeo publica cada voto como datos abiertos. La información *existe* — pero hacerla verdaderamente accesible requiere más que publicarla.\n\n**Esa brecha es lo que me propuse cerrar.**",
        "about_what_title":  "Qué es esto",
        "about_what_body":   "EU Parliament Vote Tracker combina datos de dos fuentes: el **portal de Datos Abiertos oficial del Parlamento Europeo** para el registro histórico completo, y **HowTheyVote.eu** para los votos más recientes — un proyecto cuya existencia hizo esto mucho más fácil de construir.\n\nBusca cualquier tema legislativo. Ve al instante cómo votó cada grupo político. Y luego — la parte de la que más me enorgullezco — obtén una **explicación de IA que realmente tiene sentido**.\n\nNi un resumen seco, ni jerga reemplazada por más jerga. La IA lee los datos del voto y explica en lenguaje sencillo: *de qué trataba realmente este asunto*, *qué familias políticas lo apoyaron o se opusieron y por qué*, y *qué significa en la práctica para las personas que viven en Europa*. Como si un amigo bien informado te lo explicara tomando un café.\n\nSin sesgo editorial. Sin agenda política. Solo democracia — hecha legible.\n\nEl proyecto es completamente open source. **Mi objetivo: hacer que seguir la democracia europea sea tan fácil como ver un marcador deportivo.**",
        "about_matters_title":"Por qué importa",
        "about_matters_body":"La democracia funciona mejor cuando los ciudadanos la entienden. 450 millones de personas se ven afectadas por decisiones tomadas en este edificio cada semana, y la mayoría no sabe qué se debate.\n\nEste proyecto empezó como un ejercicio personal de aprendizaje y se convirtió en algo en lo que realmente creo. Meses de trabajo en mi tiempo libre — porque creo que una democracia accesible vale la pena construirse.",
        "about_hope_title":  "Lo que espero",
        "about_hope_body":   "Si trabajas en una institución europea, un think tank, una organización de tecnología cívica o un medio de comunicación — o si simplemente compartes la convicción de que *la transparencia no es opcional en una democracia* — me encantaría hablar contigo.\n\nEsto es solo el comienzo. Hay mucho más en lo que esto podría convertirse.",
        "about_stack_1":     "Datos abiertos del PE",
        "about_stack_2":     "Explicaciones IA",
        "about_stack_3":     "5 idiomas",
        "about_cta":         "✉️ Contactar",
        "contact_page_title":"Ponte en contacto",
        "contact_subtitle":  "Preguntas, sugerencias, ideas de colaboración — todo es bienvenido.",
        "contact_name_label":"Tu nombre (opcional)",
        "contact_email_label":"Tu dirección de email",
        "contact_msg_label": "Tu mensaje",
        "contact_send_btn":  "Enviar mensaje",
        "contact_ok":        "✅ ¡Mensaje enviado! Te responderé pronto.",
        "contact_err":       "Algo salió mal. Inténtalo de nuevo o escríbeme directamente.",
        "contact_invalid":   "Por favor, introduce un email válido y un mensaje.",
        "contact_direct":    "O escríbeme directamente:",
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
        "see_all_help":      "Fasst alle passenden Themen in einer Ansicht zusammen, um die allgemeine Haltung des Parlaments zu diesem Thema zu zeigen — nicht nur ein bestimmtes Gesetz.",
        "combined_note":     "📊 Sie sehen **{n} kombinierte Themen**. Dies zeigt das allgemeine Abstimmungsverhalten des Parlaments über alle zugehörigen Gesetze. Um ein bestimmtes Gesetz zu sehen, suchen Sie erneut und wählen Sie ein Thema.",
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
        "aggregate_note":    "⚠️ Diese Zahlen aggregieren alle erfassten Abstimmungen zu diesem Thema (mehrere Lesungen, Änderungsanträge). Einzelne Abstimmungsaufschlüsselungen können von anderen Quellen abweichen.",
        "ai_hint":           "Erhalten Sie eine einfache Erklärung dieser Abstimmung, wer sie unterstützt hat und warum — in Sekunden von KI generiert.",
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
        "about_nav":         "👤 Über uns",
        "contact_nav":       "✉️ Kontakt",
        "about_tagline":     "Die Geschichte hinter diesem Projekt",
        "about_profile_bio": "Leidenschaftlich daran interessiert, die europäische Demokratie für alle zugänglich zu machen",
        "about_why_title":   "Warum ich das gebaut habe",
        "about_why_body":    "Wie viele junge Europäer liegt mir die EU sehr am Herzen. Aber jedes Mal, wenn ich versuchte zu verstehen, was wirklich im Parlament passierte — was abgestimmt wurde, wer wofür stand — stieß ich auf dieselbe Wand.\n\nEs gibt Ressourcen — und einige sind wirklich ausgezeichnet. Aber sie sind größtenteils für Spezialisten, Forscher und politische Journalisten konzipiert. Für eine neugierige Person, die einen Abstimmungsvorgang einfach verstehen möchte, ist die Einstiegshürde immer noch zu hoch.\n\nDas EU-Parlament veröffentlicht jede Abstimmung als offene Daten. Die Information ist *da* — aber sie wirklich zugänglich zu machen erfordert mehr als nur zu veröffentlichen.\n\n**Diese Lücke wollte ich schließen.**",
        "about_what_title":  "Was das ist",
        "about_what_body":   "EU Parliament Vote Tracker kombiniert Daten aus zwei Quellen: dem **offiziellen Open-Data-Portal des EU-Parlaments** für die vollständige historische Aufzeichnung und **HowTheyVote.eu** für die aktuellsten Live-Abstimmungen — ein Projekt, dessen Existenz vieles einfacher gemacht hat.\n\nSuche nach jedem Gesetzgebungsthema. Sieh sofort, wie jede politische Fraktion abgestimmt hat. Und dann — das ist der Teil, auf den ich am stolzesten bin — erhalte eine **KI-Erklärung, die wirklich Sinn ergibt**.\n\nKeine trockene Zusammenfassung, kein Fachjargon ersetzt durch anderen Fachjargon. Die KI liest die Abstimmungsdaten und erklärt in einfacher Sprache: *worum es bei diesem Thema wirklich ging*, *welche politischen Familien es unterstützt oder abgelehnt haben und warum*, und *was es in der Praxis für die Menschen in Europa bedeutet*. Wie wenn ein gut informierter Freund es dir bei einem Kaffee erklärt.\n\nKein redaktioneller Bias. Keine politische Agenda. Nur Demokratie — lesbar gemacht.\n\nDas Projekt ist vollständig open source. **Mein Ziel: EU-Demokratie so einfach verfolgbar machen wie ein Sportergebnis.**",
        "about_matters_title":"Warum es wichtig ist",
        "about_matters_body":"Demokratie funktioniert besser, wenn Bürgerinnen und Bürger sie verstehen. 450 Millionen Menschen sind jede Woche von Entscheidungen in diesem Gebäude betroffen, und die meisten wissen nicht, was dort debattiert wird.\n\nDieses Projekt begann als persönliche Lernübung und wurde zu etwas, an das ich wirklich glaube. Monate Arbeit in meiner Freizeit — weil ich denke, dass zugängliche Demokratie es wert ist, gebaut zu werden.",
        "about_hope_title":  "Was ich mir erhoffe",
        "about_hope_body":   "Wenn du bei einer EU-Institution, einem Think Tank, einer Civic-Tech-Organisation oder einem Medienunternehmen arbeitest — oder wenn du einfach die Überzeugung teilst, dass *Transparenz in einer Demokratie nicht optional ist* — würde ich mich wirklich freuen, von dir zu hören.\n\nDas ist erst der Anfang. Es gibt so viel mehr, was daraus werden könnte.",
        "about_stack_1":     "Offene EP-Daten",
        "about_stack_2":     "KI-Erklärungen",
        "about_stack_3":     "5 Sprachen",
        "about_cta":         "✉️ Kontakt aufnehmen",
        "contact_page_title":"Kontakt aufnehmen",
        "contact_subtitle":  "Fragen, Vorschläge, Kooperationsideen — alles willkommen.",
        "contact_name_label":"Dein Name (optional)",
        "contact_email_label":"Deine E-Mail-Adresse",
        "contact_msg_label": "Deine Nachricht",
        "contact_send_btn":  "Nachricht senden",
        "contact_ok":        "✅ Nachricht gesendet! Ich melde mich bald.",
        "contact_err":       "Etwas ist schiefgelaufen. Versuche es erneut oder kontaktiere mich direkt.",
        "contact_invalid":   "Bitte gib eine gültige E-Mail-Adresse und eine Nachricht ein.",
        "contact_direct":    "Oder direkt kontaktieren:",
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
        "see_all_help":      "Combina tutti gli argomenti corrispondenti in un'unica vista per mostrare la posizione generale del Parlamento su questo tema, non solo una legge specifica.",
        "combined_note":     "📊 Stai visualizzando **{n} argomenti combinati**. Questo mostra il comportamento di voto generale del Parlamento su questo tema per tutte le leggi correlate. Per vedere una legge specifica, cerca di nuovo e scegli un solo argomento.",
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
        "aggregate_note":    "⚠️ Queste cifre aggregano tutti i voti registrati su questo argomento (più letture, emendamenti). I dettagli per singolo voto possono differire da altre fonti.",
        "ai_hint":           "Ottieni una spiegazione in linguaggio semplice su questa votazione, chi l'ha sostenuta e perché — generata dall'IA in pochi secondi.",
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
        "about_nav":         "👤 Chi siamo",
        "contact_nav":       "✉️ Contatti",
        "about_tagline":     "La storia dietro questo progetto",
        "about_profile_bio": "Appassionato nel rendere la democrazia europea comprensibile a tutti",
        "about_why_title":   "Perché l'ho costruito",
        "about_why_body":    "Come molti giovani europei, mi importa profondamente dell'UE. Ma ogni volta che cercavo di capire cosa stesse davvero succedendo nel Parlamento — cosa veniva votato, chi difendeva cosa — mi scontravo con lo stesso muro.\n\nEsistono risorse — e alcune sono davvero eccellenti. Ma sono progettate principalmente per specialisti, ricercatori e giornalisti politici. Per una persona curiosa che vuole semplicemente capire un voto, la barriera è ancora troppo alta.\n\nIl Parlamento Europeo pubblica ogni singolo voto come dati aperti. L'informazione *c'è* — ma renderla veramente accessibile richiede più che pubblicarla.\n\n**Quel divario è quello che ho voluto colmare.**",
        "about_what_title":  "Cos'è questo",
        "about_what_body":   "EU Parliament Vote Tracker combina dati da due fonti: il **portale Open Data ufficiale del Parlamento Europeo** per il registro storico completo, e **HowTheyVote.eu** per i voti più recenti — un progetto la cui esistenza ha reso tutto questo molto più facile da costruire.\n\nCerca qualsiasi argomento legislativo. Vedi istantaneamente come ha votato ogni gruppo politico. E poi — la parte di cui sono più orgoglioso — ottieni una **spiegazione IA che ha davvero senso**.\n\nNon un riassunto arido, non gergo sostituito da altro gergo. L'IA legge i dati del voto e spiega in linguaggio semplice: *di cosa si trattava realmente*, *quali famiglie politiche l'hanno sostenuto o vi si sono opposte e perché*, e *cosa significa in pratica per le persone che vivono in Europa*. Come se un amico ben informato te lo spiegasse davanti a un caffè.\n\nNessun pregiudizio editoriale. Nessuna agenda politica. Solo democrazia — resa leggibile.\n\nIl progetto è completamente open source. **Il mio obiettivo: rendere la democrazia europea facile da seguire come un risultato sportivo.**",
        "about_matters_title":"Perché è importante",
        "about_matters_body":"La democrazia funziona meglio quando i cittadini la capiscono. 450 milioni di persone sono influenzate ogni settimana da decisioni prese in questo edificio, e la maggior parte non sa cosa viene dibattuto.\n\nQuesto progetto è iniziato come un esercizio personale di apprendimento ed è diventato qualcosa in cui credo davvero. Mesi di lavoro nel mio tempo libero — perché penso che una democrazia accessibile valga la pena di essere costruita.",
        "about_hope_title":  "Cosa spero",
        "about_hope_body":   "Se lavori in un'istituzione europea, un think tank, un'organizzazione di civic tech o un'organizzazione mediatica — o se semplicemente condividi la convinzione che *la trasparenza non sia opzionale in una democrazia* — mi farebbe davvero piacere sentirti.\n\nQuesto è solo l'inizio. C'è molto di più in cui questo potrebbe trasformarsi.",
        "about_stack_1":     "Dati aperti del PE",
        "about_stack_2":     "Spiegazioni IA",
        "about_stack_3":     "5 lingue",
        "about_cta":         "✉️ Contattami",
        "contact_page_title":"Contattaci",
        "contact_subtitle":  "Domande, suggerimenti, idee di collaborazione — tutto è benvenuto.",
        "contact_name_label":"Il tuo nome (opzionale)",
        "contact_email_label":"Il tuo indirizzo email",
        "contact_msg_label": "Il tuo messaggio",
        "contact_send_btn":  "Invia messaggio",
        "contact_ok":        "✅ Messaggio inviato! Ti risponderò presto.",
        "contact_err":       "Qualcosa è andato storto. Riprova o contattami direttamente.",
        "contact_invalid":   "Inserisci un indirizzo email valido e un messaggio.",
        "contact_direct":    "Oppure contattami direttamente:",
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
spacer, lang_col = st.columns([5, 1])
with lang_col:
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
new_lang = _LANG_OPTIONS[lang_display]
if st.session_state.get("lang") != new_lang:
    # Clear cached AI summaries so they regenerate in the new language
    for k in list(st.session_state.keys()):
        if k.startswith("__ai_"):
            del st.session_state[k]
st.session_state["lang"] = new_lang

def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("lang", "EN")
    text = _TR.get(lang, _TR["EN"]).get(key, _TR["EN"].get(key, key))
    return text.format(**kwargs) if kwargs else text


# Data loading

@st.cache_data(show_spinner=False)
def _preload(years: tuple = (2024, 2025, 2026)):
    # loading everything upfront so the UI stays snappy
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
    # AND first, OR fallback — feels more natural than pure OR
    q = query.strip()
    if len(q) <= 1:
        return topic_index.iloc[:0]

    topics_lower = topic_index["policy_topic"].str.lower()

    def _tmask(token: str) -> "pd.Series[bool]":
        """Mask for topics that contain this token (or its synonyms), using prefix-boundary match."""
        syns: list[str] = list(_SYNONYMS.get(token.upper(), []))
        if token.lower() not in [s.lower() for s in syns]:
            syns = [token] + syns
        m = pd.Series(False, index=topic_index.index)
        for s in syns:
            m = m | topics_lower.str.contains(r'\b' + re.escape(s.lower()), na=False, regex=True)
        return m

    # 2-char uppercase abbreviations (AI, EP, DSA …) — user typed them capitalised on purpose
    if len(q) == 2 and q == q.upper() and q.isalpha():
        return topic_index[_tmask(q)]

    # Tokenise; skip stop-words and single characters
    _STOP = {"the", "of", "on", "in", "at", "a", "an", "to", "and", "or", "for",
             "by", "with", "from", "how", "is", "are", "was", "were", "be"}
    tokens = [t for t in q.lower().split() if len(t) >= 2 and t not in _STOP]
    if not tokens:
        return topic_index.iloc[:0]

    # Strict AND: every token must match
    and_mask = pd.Series(True, index=topic_index.index)
    for tok in tokens:
        and_mask = and_mask & _tmask(tok)

    if and_mask.any():
        return topic_index[and_mask]

    # ── OR fallback (multi-token only): rank by number of matching tokens ───
    if len(tokens) >= 2:
        scores = pd.Series(0, index=topic_index.index, dtype=int)
        or_mask = pd.Series(False, index=topic_index.index)
        for tok in tokens:
            tm = _tmask(tok)
            scores += tm.astype(int)
            or_mask |= tm
        matched = topic_index[or_mask].copy()
        # topics where more tokens hit come first; break ties by vote count
        sort_key = -scores[or_mask].values * 100_000 - matched["n"].values
        return matched.iloc[sort_key.argsort()]

    return topic_index.iloc[:0]


def _get_suggestions(topic_index: pd.DataFrame, query: str) -> list[tuple[str, int]]:
    matched = _search_topics(topic_index, query)
    if matched.empty:
        return []
    q_lower = query.lower()
    # Exact-start matches surface first; the rest keep _search_topics order (relevance)
    starts = matched[matched["policy_topic"].str.lower().str.startswith(q_lower)]
    others = matched[~matched["policy_topic"].str.lower().str.startswith(q_lower)]
    ranked = pd.concat([starts, others]).head(15)
    return [(row["policy_topic"], int(row["n"])) for _, row in ranked.iterrows()]


from eu_dataset_loader import get_available_years as _get_available_years
_available_years = _get_available_years() or list(range(2019, 2027))
_selected_years  = tuple(sorted(_available_years))  # always load all years
votes_df, _hist_df, _recent_df, _group_behavior, _comparison, _has_recent, _topic_index, _latest_15 = _preload(years=_selected_years)

# Unsubscribe handler
unsub_email = st.query_params.get("unsubscribe", "")
if unsub_email:
    try:
        from email_alerts import remove_subscriber as remove_subscriber
        result = remove_subscriber(unsub_email.strip().lower())
        if result == "ok":
            st.success(f"✅ {unsub_email} a été désabonné(e).")
        else:
            st.warning("Une erreur s'est produite. Contactez-nous si le problème persiste.")
    except Exception:
        st.warning("Désabonnement temporairement indisponible.")
    st.query_params.clear()

# Sidebar

with st.sidebar:
    st.title("EU Parliament")
    st.caption("Vote Tracker")

    if st.button(t("home"), use_container_width=True, help=t("home_help")):
        st.session_state.pop("main_search", None)
        st.session_state.pop("_combined_mode", None)
        st.session_state["page"] = "home"
        st.query_params.clear()
        st.rerun()
    _nav_c1, _nav_c2 = st.columns(2)
    if _nav_c1.button(t("about_nav"), use_container_width=True):
        st.session_state["page"] = "about"
        st.rerun()
    if _nav_c2.button(t("contact_nav"), use_container_width=True):
        st.session_state["page"] = "contact"
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

    valid_dates = votes_df["date"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        date_range = st.date_input(t("date_range"), value=(min_date, max_date), min_value=min_date, max_value=max_date, format="DD/MM/YYYY")
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

# Filters (lazy — applied only when a topic is selected)

date_start = pd.Timestamp(date_range[0]) if date_range and len(date_range) == 2 else None
date_end   = (pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)) if date_range and len(date_range) == 2 else None
active_groups = set(selected_groups) if selected_groups and set(selected_groups) != set(all_groups) else None

def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if date_start and date_end:
        df = df[(df["date"] >= date_start) & (df["date"] < date_end)]
    if active_groups:
        df = df[df["political_group"].isin(active_groups)]
    return df

# Page routing — About / Contact rendered here; st.stop() skips home content
page = st.session_state.get("page", "home")
_contact_email = st.secrets.get("CONTACT_EMAIL", os.getenv("CONTACT_EMAIL", "elmas.burhan80@gmail.com"))

if page == "about":
    st.markdown(f"""
<div style="max-width:720px;margin:0 auto;">
<div style="background:linear-gradient(135deg,#1e3a8a,#1d4ed8);border-radius:16px;
            padding:2.5rem 2rem;color:white;text-align:center;margin-bottom:2rem;">
  <div style="font-size:2.5rem;margin-bottom:0.5rem;">🏛️</div>
  <div style="font-size:1.6rem;font-weight:800;letter-spacing:-0.02em;">EU Parliament Vote Tracker</div>
  <div style="opacity:0.8;font-size:1rem;margin-top:0.5rem;">{t("about_tagline")}</div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="max-width:720px;margin:0 auto;">
<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;
            padding:1.5rem;margin-bottom:2rem;display:flex;align-items:center;gap:1.2rem;">
  <div style="font-size:3.5rem;flex-shrink:0;">👨‍💻</div>
  <div>
    <div style="font-weight:700;font-size:1.15rem;color:#1e3a8a;">Burhan</div>
    <div style="color:#2563eb;font-size:0.9rem;margin-top:0.1rem;">AI &amp; Data Engineer · Belgium</div>
    <div style="color:#6b7280;font-size:0.85rem;margin-top:0.3rem;">{t("about_profile_bio")}</div>
  </div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### {t('about_why_title')}")
    st.markdown(t("about_why_body"))
    st.markdown(f"### {t('about_what_title')}")
    st.markdown(t("about_what_body"))
    st.markdown(f"### {t('about_matters_title')}")
    st.markdown(t("about_matters_body"))
    st.markdown(f"### {t('about_hope_title')}")
    st.markdown(t("about_hope_body"))

    _cols = st.columns([1, 1, 1])
    with _cols[0]:
        st.markdown(f"""<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
        padding:1rem;text-align:center;">
        <div style="font-size:1.5rem;">🏛️</div>
        <div style="font-weight:600;font-size:0.85rem;color:#166534;margin-top:0.3rem;">{t("about_stack_1")}</div>
        <div style="font-size:0.75rem;color:#6b7280;margin-top:0.2rem;">10M+ votes, 2019–2026</div>
        </div>""", unsafe_allow_html=True)
    with _cols[1]:
        st.markdown(f"""<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;
        padding:1rem;text-align:center;">
        <div style="font-size:1.5rem;">🤖</div>
        <div style="font-weight:600;font-size:0.85rem;color:#1e3a8a;margin-top:0.3rem;">{t("about_stack_2")}</div>
        <div style="font-size:0.75rem;color:#6b7280;margin-top:0.2rem;">Llama 3.1 via Groq</div>
        </div>""", unsafe_allow_html=True)
    with _cols[2]:
        st.markdown(f"""<div style="background:#faf5ff;border:1px solid #e9d5ff;border-radius:10px;
        padding:1rem;text-align:center;">
        <div style="font-size:1.5rem;">🌍</div>
        <div style="font-weight:600;font-size:0.85rem;color:#6b21a8;margin-top:0.3rem;">{t("about_stack_3")}</div>
        <div style="font-size:0.75rem;color:#6b7280;margin-top:0.2rem;">EN · FR · ES · DE · IT</div>
        </div>""", unsafe_allow_html=True)

    # Tech stack — show the real engineering behind this
    st.markdown("---")
    st.markdown("""
<div style="background:#0f172a;color:#e2e8f0;border-radius:14px;padding:1.5rem 1.8rem;margin-bottom:1.5rem;">
  <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.12em;color:#94a3b8;margin-bottom:1rem;">
    ⚙️ Built from scratch — real engineering, real code
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:0.6rem;margin-bottom:1rem;">
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">🐍 Python 3.11</span>
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">🐼 Pandas + Parquet</span>
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">📊 Plotly</span>
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">🤖 LLaMA 3.1 · Groq API</span>
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">🗄️ Supabase</span>
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">📧 Resend API</span>
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">🔄 GitHub Actions</span>
    <span style="background:#1e293b;border:1px solid #334155;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.8rem;">🌐 REST APIs</span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:1.5rem;font-size:0.85rem;color:#94a3b8;border-top:1px solid #1e293b;padding-top:0.9rem;">
    <span>📁 <strong style="color:#e2e8f0;">3,000+</strong> lines of code</span>
    <span>🗳️ <strong style="color:#e2e8f0;">10M+</strong> votes processed</span>
    <span>⚡ <strong style="color:#e2e8f0;">Custom</strong> data pipeline</span>
    <span>🔎 <strong style="color:#e2e8f0;">Multilingual</strong> semantic search</span>
    <span>📬 <strong style="color:#e2e8f0;">Automated</strong> weekly digest</span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button(t("about_cta"), type="primary"):
        st.session_state["page"] = "contact"
        st.rerun()
    st.stop()

elif page == "contact":
    st.markdown(f"## {t('contact_page_title')}")
    st.caption(t("contact_subtitle"))
    st.markdown("---")

    _c1, _c2 = st.columns([2, 1])
    with _c1:
        _ct_name  = st.text_input(t("contact_name_label"),  key="ct_name",  placeholder="e.g. Marie Dupont")
        _ct_email = st.text_input(t("contact_email_label"), key="ct_email", placeholder="marie@example.com")
        _ct_msg   = st.text_area( t("contact_msg_label"),   key="ct_msg",   height=180,
                                  placeholder="I work at the European Commission and I'd love to discuss...")
        if st.button(t("contact_send_btn"), type="primary", key="ct_send"):
            _e = _ct_email.strip()
            _m = _ct_msg.strip()
            if not _e or "@" not in _e or not _m:
                st.warning(t("contact_invalid"))
            else:
                try:
                    import requests as _rq
                    _rk = st.secrets.get("RESEND_API_KEY", os.getenv("RESEND_API_KEY", ""))
                    _fe = st.secrets.get("FROM_EMAIL", os.getenv("FROM_EMAIL", "EU Vote Tracker <onboarding@resend.dev>"))
                    if not _rk:
                        st.error(t("contact_err"))
                    else:
                        _subj = f"[EU Vote Tracker] Message from {_ct_name or _e}"
                        _html_body = f"""<p><strong>From:</strong> {_ct_name or '(no name)'} &lt;{_e}&gt;</p>
<p><strong>Message:</strong></p><p style="white-space:pre-wrap;">{_m}</p>"""
                        _resp = _rq.post(
                            "https://api.resend.com/emails",
                            headers={"Authorization": f"Bearer {_rk}", "Content-Type": "application/json"},
                            json={"from": _fe, "to": [_contact_email],
                                  "reply_to": _e, "subject": _subj, "html": _html_body},
                            timeout=15,
                        )
                        if _resp.status_code in (200, 201, 202):
                            st.success(t("contact_ok"))
                        else:
                            st.error(t("contact_err"))
                except Exception:
                    st.error(t("contact_err"))

    with _c2:
        st.markdown(f"""
<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:1.2rem;margin-top:1.8rem;">
  <div style="font-weight:600;color:#374151;font-size:0.9rem;margin-bottom:0.6rem;">
    {t('contact_direct')}
  </div>
  <div style="font-size:0.85rem;color:#2563eb;">
    📧 <a href="mailto:{_contact_email}" style="color:#2563eb;">{_contact_email}</a>
  </div>
  <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.8rem;">
    Burhan — AI &amp; Data Engineer<br>Belgium 🇧🇪
  </div>
</div>""", unsafe_allow_html=True)

    st.stop()

# Search state  (only needed on home page, but harmless to run always)

# Deep-link: load topic from URL ?q=... on first visit
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

# Main UI

st.markdown(f"""
<div class="eu-hero fade-up">
  <div class="hero-blob-1"></div>
  <div class="hero-blob-2"></div>
  <div class="hero-grid-overlay"></div>
  <div class="hero-inner">
    <div class="hero-eyebrow">🏛️ EU Parliament · 2019–2026</div>
    <h1 class="hero-title">
      {t("title")}
      <span class="accent">{t("onboard_title")}</span>
    </h1>
    <p class="hero-sub">{t("onboard_body")}</p>
    <div class="hero-stats">
      <div class="hero-stat">
        <span class="hero-stat-num">{len(votes_df):,}</span>
        <span class="hero-stat-label">{t("votes_loaded")}</span>
      </div>
      <span class="hero-stat-sep">·</span>
      <div class="hero-stat">
        <span class="hero-stat-num">5</span>
        <span class="hero-stat-label">languages</span>
      </div>
      <span class="hero-stat-sep">·</span>
      <div class="hero-stat">
        <span class="hero-stat-num">AI</span>
        <span class="hero-stat-label">powered</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if DEMO_MODE:
    st.info("**Demo Mode** — dataset capped at 5,000 rows.")

_, search_col, _ = st.columns([0.5, 9, 0.5])
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
                             key="pill_all", use_container_width=True,
                             help=t("see_all_help")):
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

# Topic view

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

    if combined_mode:
        st.info(t("combined_note", n=len(all_matching)))

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
        # Abbreviate long political group names for readability on mobile
        _GROUP_SHORT = {
            "Group of the European People's Party (Christian Democrats)": "EPP",
            "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament": "S&D",
            "Group of the Progressive Alliance of Socialists and Democrats": "S&D",
            "Renew Europe Group": "Renew Europe",
            "Group of the Greens/European Free Alliance": "Greens/EFA",
            "European Conservatives and Reformists Group": "ECR",
            "Identity and Democracy Group": "ID",
            "The Left group in the European Parliament - GUE/NGL": "GUE/NGL",
            "Non-attached Members": "Non-attached (NI)",
            "Europe of Sovereign Nations Group": "ESN",
            "Patriots for Europe Group": "Patriots",
            "European People's Party Group": "EPP",
        }
        plot_df = group_votes.sort_values("FOR_%", ascending=True).reset_index()
        plot_df["group_label"] = plot_df["political_group"].apply(
            lambda g: _GROUP_SHORT.get(g, g[:30] + "…" if len(g) > 30 else g)
        )
        fig = px.bar(
            plot_df, y="group_label", x=["FOR_%", "AGAINST_%", "ABSTAIN_%"],
            orientation="h", barmode="stack",
            color_discrete_map={"FOR_%": "#2563eb", "AGAINST_%": "#ef4444", "ABSTAIN_%": "#d1d5db"},
            title=t("vote_breakdown"),
        )
        lbl = {"FOR_%": t("for_label"), "AGAINST_%": t("against_label"), "ABSTAIN_%": t("abstain_label")}
        for trace in fig.data:
            trace.name = lbl.get(trace.name, trace.name)
            trace.hovertemplate = "%{customdata}: %{x:.1f}%<extra>" + trace.name + "</extra>"
            trace.customdata = plot_df["political_group"].values
        fig.update_layout(
            xaxis_title="", yaxis_title="", legend_title_text="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=10, t=55, b=10),
            height=max(280, len(plot_df) * 42 + 90),
            title_font_size=14,
        )
        fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=True, gridcolor="#f3f4f6", zeroline=False)
        fig.update_yaxes(showgrid=False, automargin=True, tickfont=dict(size=11))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
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
    st.caption(t("aggregate_note"))

    st.divider()
    st.subheader(t("ai_section"))
    st.caption(t("ai_hint"))

    if DEMO_MODE:
        st.info("AI Analysis is disabled in Demo Mode.")
    else:
        cache_key = f"__ai_{hash(topic)}_{st.session_state.get('lang','EN')}"
        if st.button(t("ai_button"), type="primary"):
            from analysis_agent import build_summary
            topic_summary = build_summary(topic_df)
            if not topic_summary:
                st.warning(t("ai_no_data"))
            else:
                if cache_key in st.session_state:
                    insight = st.session_state[cache_key]
                else:
                    with st.spinner(t("ai_spinning")):
                        insight = generate_ai_insight(topic_summary, topic, lang=t("lang_name"))
                    st.session_state[cache_key] = insight
                error_map = {
                    "NO_KEY":     t("ai_no_key"),
                    "BAD_KEY":    t("ai_bad_key"),
                    "RATE_LIMIT": t("ai_rate_limit"),
                    "TIMEOUT":    t("ai_timeout"),
                    "API_ERROR":  t("ai_error"),
                }
                if insight in error_map:
                    st.warning(error_map[insight])
                else:
                    st.markdown(f'<div class="ai-card">{insight}</div>', unsafe_allow_html=True)
        elif cache_key in st.session_state:
            insight = st.session_state[cache_key]
            error_map = {"NO_KEY", "BAD_KEY", "RATE_LIMIT", "TIMEOUT", "API_ERROR"}
            if insight not in error_map:
                st.markdown(f'<div class="ai-card">{insight}</div>', unsafe_allow_html=True)

    st.divider()

# Homepage — latest 15 votes

if not query:
    # Quick-start examples
    st.markdown(
        f"<p style='color:#6b7280;font-size:0.9rem;font-weight:600;margin-bottom:0.5rem;'>"
        f"{t('try_example')}</p>",
        unsafe_allow_html=True,
    )
    examples = ["AI Act", "Ukraine", "Climate", "Migration", "Digital Services Act"]
    for row_start in range(0, len(examples), 3):
        row = examples[row_start : row_start + 3]
        ex_cols = st.columns(len(row))
        for i, ex in enumerate(row):
            if ex_cols[i].button(ex, key=f"ex_{ex}", use_container_width=True):
                st.session_state["search_override"] = ex
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

    # Recent political changes (homepage only)
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
                mc_group_display = (mc_group[:28] + "…") if len(mc_group) > 28 else mc_group
                mc_topic_display = (mc_topic[:28] + "…") if len(mc_topic) > 28 else mc_topic
                m1, m2, m3 = st.columns(3)
                m1.metric(t("most_chg_group"), mc_group_display, help=mc_group)
                m2.metric(t("most_chg_topic"), mc_topic_display, help=mc_topic)
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

# Newsletter subscription (shown on every page)
st.divider()
st.markdown(f"### {t('subscribe_title')}")
st.caption(t("subscribe_body"))
sub_col, _ = st.columns([2, 1])
with sub_col:
    sub_email = st.text_input(
        "email_sub", label_visibility="collapsed",
        placeholder=t("subscribe_placeholder"), key="sub_email_input",
    )
    if st.button(t("subscribe_btn"), type="primary", key="sub_btn"):
        email = sub_email.strip().lower()
        if not email or "@" not in email:
            st.warning(t("subscribe_invalid"))
        else:
            try:
                import requests as req_lib
                sb_url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
                sb_key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
                if not sb_url or not sb_key:
                    st.error(t("subscribe_err"))
                else:
                    resp = req_lib.post(
                        f"{sb_url}/rest/v1/subscribers",
                        headers={
                            "apikey": sb_key,
                            "Authorization": f"Bearer {sb_key}",
                            "Content-Type": "application/json",
                            "Prefer": "resolution=merge-duplicates,return=minimal",
                        },
                        json={"email": email, "language": st.session_state.get("lang", "EN")},
                        timeout=10,
                    )
                    if resp.status_code in (200, 201):
                        st.success(t("subscribe_ok"))
                    else:
                        st.error(t("subscribe_err"))
            except Exception:
                st.error(t("subscribe_err"))