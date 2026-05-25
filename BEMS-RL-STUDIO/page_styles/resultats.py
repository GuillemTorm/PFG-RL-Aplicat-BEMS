"""CSS de la pàgina de resultats."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


RESULTS_CSS = """
<style>
    /* Variables resultats */
    :root {
        --results-control-height: 5rem;
        --results-dashboard-button-size: 5rem;
    }

    /* Botó generar dashboard */
    div[class*="st-key-generate_dashboard_button"] {
        display: flex;
        height: var(--results-control-height) !important;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-top: 0 !important;
    }

    /* Icona botó dashboard */
    div[class*="st-key-generate_dashboard_button"] button {
        width: var(--results-dashboard-button-size) !important;
        min-width: var(--results-dashboard-button-size) !important;
        max-width: var(--results-dashboard-button-size) !important;
        height: var(--results-dashboard-button-size) !important;
        min-height: var(--results-dashboard-button-size) !important;
        aspect-ratio: 1 / 1 !important;
        padding: 0 !important;
        border-radius: 999px !important;
        border: none !important;
        background: linear-gradient(135deg, var(--studio-accent), var(--studio-accent-2)) !important;
        box-shadow: 0 16px 28px rgba(91, 85, 247, 0.24) !important;
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        gap: 0 !important;
    }

    /* Contingut botó dashboard */
    div[class*="st-key-generate_dashboard_button"] button > div {
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Text ocult botó dashboard */
    div[class*="st-key-generate_dashboard_button"] button [data-testid="stMarkdownContainer"] {
        display: none !important;
    }

    /* Paragraf botó dashboard */
    div[class*="st-key-generate_dashboard_button"] button p {
        margin: 0 !important;
        line-height: 0 !important;
    }

    /* Icona material dashboard */
    div[class*="st-key-generate_dashboard_button"] button [data-testid="stIconMaterial"],
    div[class*="st-key-generate_dashboard_button"] button svg {
        width: 1.65rem !important;
        height: 1.65rem !important;
        min-width: 1.65rem !important;
        min-height: 1.65rem !important;
        font-size: 1.65rem !important;
        margin: 0 !important;
    }

    /* Hover botó dashboard */
    div[class*="st-key-generate_dashboard_button"] button:hover {
        transform: translateY(-1px);
    }

    /* Botons informe */
    div[class*="st-key-btn_gen_report"],
    div[class*="st-key-btn_download_report"] {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        width: 100% !important;
        margin-top: 0 !important;
    }

    /* Botó generar informe */
    div[class*="st-key-btn_gen_report"] button,
    div[class*="st-key-btn_download_report"] button {
        width: 100% !important;
        min-width: 13.5rem !important;
        height: 3.05rem !important;
        min-height: 3.05rem !important;
        padding: 0 1.15rem !important;
        border-radius: 999px !important;
        border: none !important;
        background: linear-gradient(135deg, var(--studio-accent), var(--studio-accent-2)) !important;
        box-shadow: 0 14px 24px rgba(91, 85, 247, 0.22) !important;
        color: #ffffff !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.45rem !important;
        overflow: visible !important;
        white-space: nowrap !important;
    }

    /* Contingut botó informe */
    div[class*="st-key-btn_gen_report"] button > div,
    div[class*="st-key-btn_download_report"] button > div {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.45rem !important;
        width: auto !important;
    }

    /* Text contenidor informe */
    div[class*="st-key-btn_gen_report"] button [data-testid="stMarkdownContainer"],
    div[class*="st-key-btn_download_report"] button [data-testid="stMarkdownContainer"] {
        display: inline-flex !important;
        align-items: center !important;
        width: auto !important;
    }

    /* Text botó informe */
    div[class*="st-key-btn_gen_report"] button p,
    div[class*="st-key-btn_download_report"] button p {
        margin: 0 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
        font-weight: 800 !important;
    }

    /* Icona botó informe */
    div[class*="st-key-btn_gen_report"] button [data-testid="stIconMaterial"],
    div[class*="st-key-btn_gen_report"] button svg {
        width: 1.2rem !important;
        height: 1.2rem !important;
        min-width: 1.2rem !important;
        min-height: 1.2rem !important;
        font-size: 1.2rem !important;
    }

    /* Hover botó informe */
    div[class*="st-key-btn_gen_report"] button:hover,
    div[class*="st-key-btn_download_report"] button:hover {
        transform: translateY(-1px);
    }

    /* Grafic Plotly */
    [data-testid="stPlotlyChart"] {
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        overflow: hidden;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: var(--studio-shadow);
        padding: 0.3rem 0.35rem 0;
        margin-bottom: 0.6rem;
    }

    /* Selectors filtres */
    div[data-testid="stSelectbox"] {
        padding: 0.55rem 0.75rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 8px 18px rgba(18, 27, 49, 0.05);
        box-sizing: border-box;
        min-height: var(--results-control-height);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Caixa selector filtre */
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        min-height: 2.45rem !important;
    }

    /* Label selector filtre */
    div[data-testid="stSelectbox"] > label {
        color: var(--studio-text);
        font-size: 0.88rem;
        font-weight: 700;
    }

    /* Graella KPIs */
    .results-kpi-shell {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin-bottom: 1rem !important;
    }

    /* Targeta KPI */
    .results-kpi-card {
        padding: 1rem 1.05rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
        min-height: 110px;
        text-align: center;
        min-width: 0;
    }

    /* Label KPI */
    .results-kpi-label {
        color: #273a72;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.38rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Valor KPI */
    .results-kpi-value {
        color: var(--studio-text);
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: clamp(1.28rem, 1.8vw, 1.42rem);
        font-weight: 800;
        line-height: 1.04;
        overflow-wrap: anywhere;
    }

    /* Delta KPI */
    .results-kpi-delta {
        font-size: 0.72rem;
        font-weight: 700;
        margin-top: 5px;
    }

    /* Delta KPI positiu */
    .results-kpi-delta-good {
        color: #22c55e;
    }

    /* Delta KPI negatiu */
    .results-kpi-delta-bad {
        color: #ef4444;
    }

    /* Delta KPI neutre */
    .results-kpi-delta-neutral {
        color: #6b7280;
    }

    /* KPIs tablet */
    @media (max-width: 980px) {
        .results-kpi-shell {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    /* KPIs mobil */
    @media (max-width: 560px) {
        .results-kpi-shell {
            grid-template-columns: 1fr;
        }
    }

    /* Text pestanya */
    .results-tab-copy {
        margin-bottom: 0.85rem;
        color: var(--studio-text-soft);
        font-size: 0.94rem;
        line-height: 1.55;
    }

    /* Capçalera dashboard */
    .results-dashboard-header {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.25rem;
    }

    /* Etiqueta dashboard */
    .results-dashboard-tag {
        background: var(--studio-panel-soft);
        border: 1px solid var(--studio-line);
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.82rem;
        color: var(--studio-muted);
    }

    /* Valor etiqueta dashboard */
    .results-dashboard-tag strong {
        font-weight: 600;
        color: var(--studio-accent);
    }
</style>
"""


def inject_results_page_styles() -> None:
    """Injecteu el CSS específic de la pàgina per a la pàgina de resultats."""

    inject_studio_theme(max_width=1180, hide_first_heading=True)
    st.markdown(RESULTS_CSS, unsafe_allow_html=True)
