"""CSS de la pàgina Mostra l'entorn."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


ENVIRONMENT_CSS = """
<style>
    /* Subratllat pestanyes */
    [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Etiquetes entorn */
    .environment-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 0.55rem 0 0.25rem;
    }

    /* Etiqueta entorn */
    .environment-tag {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.78rem;
        border: 1px solid rgba(95, 84, 249, 0.18);
        border-radius: 999px;
        background: rgba(95, 84, 249, 0.10);
        color: #34415f;
        font-size: 0.84rem;
        font-weight: 700;
        line-height: 1;
    }

    /* Labels cerca entorn */
    div[data-testid="stTextInput"] > label,
    div[data-testid="stSelectbox"] > label {
        color: #31415f;
        font-size: 0.96rem;
        font-weight: 700;
        margin-bottom: 0.42rem;
    }

    /* Controls cerca entorn */
    div[data-testid="stTextInput"],
    div[data-testid="stSelectbox"] {
        width: 100%;
    }

    /* Caixa cerca entorn */
    div[data-testid="stTextInput"] [data-baseweb="input"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        width: 100% !important;
        min-height: 4.35rem;
        border: 1px solid rgba(207, 216, 238, 0.95) !important;
        border-radius: 1.35rem !important;
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
        color: #1f2d4d !important;
        box-sizing: border-box;
        overflow: hidden;
    }

    /* Fons controls cerca */
    div[data-testid="stTextInput"] [data-baseweb="input"] > div,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
        background: transparent !important;
    }

    /* Caixa input cerca */
    div[data-testid="stTextInput"] [data-baseweb="input"] > div {
        width: 100% !important;
    }

    /* Text input cerca */
    div[data-testid="stTextInput"] input {
        width: 100% !important;
        min-height: 4.35rem !important;
        height: 4.35rem !important;
        margin: 0 !important;
        padding: 0 1rem !important;
        font-size: 1rem;
        line-height: 1.25 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Text selector entorn */
    div[data-testid="stSelectbox"] [data-baseweb="select"] span,
    div[data-testid="stSelectbox"] [data-baseweb="select"] input,
    div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
        color: #1f2d4d !important;
    }

    /* Cursor selector entorn */
    div[data-testid="stSelectbox"] [data-baseweb="select"] input {
        caret-color: transparent !important;
    }

    /* Padding selector entorn */
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        padding-left: 0.1rem;
        padding-right: 0.1rem;
    }

    /* Graella metriques */
    .environment-metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.8rem;
        margin: 0.45rem 0 1rem;
    }

    /* Targeta metrica */
    .environment-metric-card {
        padding: 0.95rem 1rem;
        border: 1px solid rgba(207, 216, 238, 0.95);
        border-radius: 16px;
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        height: 100%;
        min-height: 9.2rem;
        margin-bottom: 0.8rem;
    }

    /* Label metrica */
    .environment-metric-label {
        margin-bottom: 0.38rem;
        color: #6c7693;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* Valor metrica */
    .environment-metric-value {
        color: #1f2d4d;
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: 1.36rem;
        font-weight: 800;
        line-height: 1.05;
    }

    /* Valor metrica ampla */
    .environment-metric-card--wide .environment-metric-value {
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        font-size: 1rem;
        line-height: 1.55;
        word-break: break-word;
    }

    /* Targeta metrica ampla */
    .environment-metric-card--wide {
        min-height: auto;
    }

    /* Targeta detall */
    .environment-detail-card {
        padding: 1rem 1.05rem;
        border: 1px solid rgba(207, 216, 238, 0.95);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
        margin-bottom: 0.85rem;
    }

    /* Titol detall */
    .environment-detail-title {
        margin-bottom: 0.8rem;
        color: #1f2d4d;
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: 1.1rem;
        font-weight: 800;
    }

    /* Llista detall */
    .environment-detail-list {
        display: grid;
        gap: 0.62rem;
    }

    /* Fila detall */
    .environment-detail-row {
        display: grid;
        grid-template-columns: minmax(130px, 170px) minmax(0, 1fr);
        align-items: start;
        gap: 1.15rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(220, 227, 242, 0.9);
    }

    /* Fila final detall */
    .environment-detail-row:last-child {
        padding-bottom: 0;
        border-bottom: none;
    }

    /* Label detall */
    .environment-detail-label {
        color: #6c7693;
        font-size: 0.82rem;
        font-weight: 600;
        line-height: 1.35;
    }

    /* Valor detall */
    .environment-detail-value {
        color: #1f2d4d;
        font-size: 0.86rem;
        font-weight: 650;
        text-align: right;
        line-height: 1.45;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    /* Graella bateria */
    .environment-battery-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.9rem;
        margin-top: 0.9rem;
    }

    /* Targeta bateria */
    .environment-battery-card {
        padding: 1rem 1.05rem;
        border: 1px solid rgba(207, 216, 238, 0.95);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
        height: 100%;
        margin-bottom: 0.9rem;
    }

    /* Nom bateria */
    .environment-battery-name {
        margin-bottom: 0.3rem;
        color: #1f2d4d;
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: 1.08rem;
        font-weight: 800;
    }

    /* Tipus bateria */
    .environment-battery-type {
        margin-bottom: 0.8rem;
        color: #5f54f9;
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* Llista bateria */
    .environment-battery-list {
        display: grid;
        gap: 0.45rem;
    }

    /* Grafic i visor 3D */
    [data-testid="stDeckGlJsonChart"],
    [data-testid="stPlotlyChart"] {
        border: 1px solid rgba(220, 227, 242, 0.95);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
        background: #ffffff;
    }
</style>
"""


def inject_environment_styles() -> None:
    """Injecteu el CSS específic de la pàgina per a la pàgina Mostra l'entorn."""
    inject_studio_theme(max_width=1240, hide_first_heading=True)
    st.markdown(ENVIRONMENT_CSS, unsafe_allow_html=True)
