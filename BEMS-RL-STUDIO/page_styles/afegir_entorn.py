"""CSS de la pàgina Afegeix un entorn."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


AFEGIR_ENTORN_CSS = """
<style>
    /* Ancora targeta upload */
    .upload-card-shell-anchor {
        display: none;
    }

    /* Targeta upload fitxers */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-card-shell-anchor) {
        border-radius: 18px !important;
        border: 1px solid var(--studio-line) !important;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%) !important;
        box-shadow: var(--studio-shadow) !important;
        margin-bottom: 0.95rem;
        min-height: 22.8rem;
        padding: 1rem 1.05rem 0.95rem !important;
        gap: 1rem;
    }

    /* Ancores targetes clima */
    .weather-variability-card-anchor,
    .weather-preview-card-anchor {
        display: none;
    }

    /* Targeta variabilitat clima */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.weather-variability-card-anchor),
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.weather-preview-card-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.weather-variability-card-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.weather-preview-card-anchor) {
        border-radius: 18px !important;
        border: 1px solid var(--studio-line) !important;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%) !important;
        box-shadow: var(--studio-shadow) !important;
        margin: 0.55rem 0 1.25rem;
        padding: 1.25rem 1.45rem 0.85rem !important;
    }

    /* Espai targetes clima */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.weather-variability-card-anchor),
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.weather-preview-card-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.weather-variability-card-anchor) > div[data-testid="stVerticalBlock"],
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.weather-preview-card-anchor) > div[data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }

    /* Espai targeta upload */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-card-shell-anchor) > div[data-testid="stVerticalBlock"] {
        gap: 1rem;
    }

    /* Kicker targeta upload */
    .upload-card-kicker {
        display: inline-block;
        margin-bottom: 0.55rem;
        color: var(--studio-accent);
        font-family: "Consolas", "Bahnschrift", monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    /* Titol targeta upload */
    .upload-card-title {
        margin: 0 0 0.2rem 0;
        color: var(--studio-text);
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: 1.16rem;
        font-weight: 800;
    }

    /* Text targeta upload */
    .upload-card-copy {
        color: var(--studio-text-soft);
        font-size: 0.94rem;
        line-height: 1.55;
        margin-bottom: 0.7rem;
    }

    /* Grafic clima */
    [data-testid="stPlotlyChart"] {
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        overflow: hidden;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: var(--studio-shadow);
        padding: 0.3rem 0.35rem 0;
    }

    /* Inputs variabilitat */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.weather-variability-card-anchor) div[data-testid="stNumberInput"],
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.weather-variability-card-anchor) div[data-testid="stNumberInput"] {
        padding: 0.88rem 0.95rem 0.72rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 8px 18px rgba(18, 27, 49, 0.05);
    }

    /* Checkbox variabilitat */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.weather-variability-card-anchor) div[data-testid="stCheckbox"],
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.weather-variability-card-anchor) div[data-testid="stCheckbox"] {
        margin-bottom: 0.3rem;
    }

    /* Labels formulari */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.weather-variability-card-anchor) div[data-testid="stNumberInput"] > label,
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) div[data-testid="stSelectbox"] > label,
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) div[data-testid="stSegmentedControl"] > label,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.weather-variability-card-anchor) div[data-testid="stNumberInput"] > label,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-card-shell-anchor) div[data-testid="stSelectbox"] > label,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.upload-card-shell-anchor) div[data-testid="stSegmentedControl"] > label {
        color: var(--studio-text);
        font-size: 0.9rem;
        font-weight: 700;
    }

    /* Widgets targeta upload */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) [data-testid="stFileUploader"],
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) [data-testid="stSegmentedControl"],
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) [data-testid="stSelectbox"],
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) [data-testid="stAlert"],
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) [data-testid="stCaptionContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stFileUploader"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSegmentedControl"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stAlert"],
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] {
        margin-top: 0;
        margin-bottom: 0;
    }

    /* Peu targeta upload */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has(.upload-card-shell-anchor) [data-testid="stCaptionContainer"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] p {
        margin-top: 0.5rem;
    }

    /* Label IDs generats */
    .add-env-generated-ids-label {
        margin-bottom: 0.2rem;
        color: var(--text-color);
        font-size: 0.875rem;
        font-weight: 600;
    }
</style>
"""


def inject_add_environment_styles() -> None:
    """Injecteu el CSS específic de la pàgina per a la pàgina Afegeix un entorn."""
    inject_studio_theme(max_width=1260, hide_first_heading=True)
    st.markdown(AFEGIR_ENTORN_CSS, unsafe_allow_html=True)
