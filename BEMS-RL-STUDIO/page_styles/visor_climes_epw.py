"""CSS de la pàgina de visualització del clima EPW."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


EPW_VIEWER_CSS = """
<style>
    /* Titol targeta EPW */
    .epw-card-title {
        margin-bottom: 0.7rem;
        color: var(--studio-text);
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: 1.08rem;
        font-weight: 800;
    }

    /* Titol global EPW */
    .epw-global-title {
        margin-bottom: 1rem;
        font-size: clamp(1.45rem, 2vw, 1.78rem);
    }

    /* Targeta metrica EPW */
    .epw-metric-card {
        padding: 1rem 1.05rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
        min-height: 110px;
    }

    /* Label metrica EPW */
    .epw-metric-label {
        color: var(--studio-muted);
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.38rem;
    }

    /* Valor metrica EPW */
    .epw-metric-value {
        color: var(--studio-text);
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: clamp(1.28rem, 1.8vw, 1.42rem);
        font-weight: 800;
        line-height: 1.04;
        overflow-wrap: anywhere;
    }

    /* Graella metriques EPW */
    .epw-metric-shell {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.85rem;
        margin-bottom: 1rem;
    }

    /* Targeta detall EPW */
    .epw-detail-card {
        padding: 1rem 1.05rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
    }

    /* Llista detall EPW */
    .epw-detail-list {
        display: grid;
        gap: 0.64rem;
    }

    /* Fila detall EPW */
    .epw-detail-row {
        display: grid;
        grid-template-columns: minmax(150px, 180px) minmax(0, 1fr);
        gap: 1rem;
        align-items: start;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(220, 227, 242, 0.9);
    }

    /* Fila final EPW */
    .epw-detail-row:last-child {
        padding-bottom: 0;
        border-bottom: none;
    }

    /* Label detall EPW */
    .epw-detail-label {
        color: var(--studio-muted);
        font-size: 0.82rem;
        font-weight: 700;
    }

    /* Valor detall EPW */
    .epw-detail-value {
        color: var(--studio-text);
        font-size: 0.9rem;
        font-weight: 600;
        text-align: right;
        overflow-wrap: anywhere;
    }

    /* Grafic Plotly EPW */
    [data-testid="stPlotlyChart"] {
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        overflow: hidden;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: var(--studio-shadow);
        padding: 0.3rem 0.35rem 0;
    }

    /* Mapa EPW */
    div[data-testid="stDeckGlJsonChart"] {
        border-radius: 18px;
        overflow: hidden;
        background: #101820;
    }

    /* Contingut mapa EPW */
    div[data-testid="stDeckGlJsonChart"] > div,
    div[data-testid="stDeckGlJsonChart"] iframe,
    div[data-testid="stDeckGlJsonChart"] canvas,
    div[data-testid="stDeckGlJsonChart"] .deckgl-wrapper,
    div[data-testid="stDeckGlJsonChart"] .mapboxgl-map {
        border-radius: inherit;
    }

    /* Labels selectors EPW */
    div[data-testid="stSelectbox"] > label,
    div[data-testid="stTextInput"] > label {
        color: var(--studio-text);
        font-size: 0.93rem;
        font-weight: 700;
    }

    /* Text pestanya EPW */
    .epw-tab-copy {
        margin-bottom: 0.75rem;
        color: var(--studio-text-soft);
        font-size: 0.94rem;
        line-height: 1.55;
    }

    /* Controls cerca EPW */
    div[data-testid="stTextInput"],
    div[data-testid="stSelectbox"] {
        padding: 0.88rem 0.95rem 0.7rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 8px 18px rgba(18, 27, 49, 0.05);
    }

    /* Caixa control EPW */
    div[data-testid="stTextInput"],
    div[data-testid="stSelectbox"] {
        box-sizing: border-box;
        min-height: 7.1rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
</style>
"""


def inject_epw_viewer_styles() -> None:
    """Injecteu el CSS específic de la pàgina per al visor EPW."""

    inject_studio_theme(max_width=1260, hide_first_heading=True)
    st.markdown(
        EPW_VIEWER_CSS,
        unsafe_allow_html=True,
    )
