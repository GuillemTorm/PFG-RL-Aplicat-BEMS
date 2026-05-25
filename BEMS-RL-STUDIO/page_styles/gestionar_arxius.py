"""CSS de la pàgina Gestor de fitxers."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


GESTIONAR_ARXIUS_CSS = """
<style>
    /* Ruta explorador */
    .file-explorer-path {
        border: 1px solid var(--studio-line);
        border-radius: 16px;
        background: var(--studio-panel-soft);
        padding: 0.82rem 1rem;
        color: var(--studio-text);
        font-family: "Consolas", "Courier New", monospace;
        font-size: 0.92rem;
        overflow-wrap: anywhere;
    }

    /* Capçalera explorador */
    .file-explorer-header {
        color: var(--studio-muted);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0.45rem 0 0.15rem;
    }

    /* Cel·la explorador */
    .file-explorer-cell,
    .file-explorer-muted {
        min-height: 2.35rem;
        display: flex;
        align-items: center;
        font-size: 0.96rem;
    }

    /* Nom fitxer */
    .file-explorer-cell {
        color: var(--studio-text);
        font-weight: 600;
    }

    /* Bloc nom fitxer */
    .file-explorer-name {
        display: flex;
        align-items: flex-start;
        width: 100%;
        min-width: 0;
    }

    /* Cel·la icona */
    .file-explorer-icon-cell {
        min-height: 2.35rem;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding-top: 0.15rem;
    }

    /* Icona fitxer */
    .file-explorer-icon {
        font-size: 1.02rem;
        line-height: 1;
    }

    /* Label fitxer */
    .file-explorer-label {
        flex: 1;
        min-width: 0;
        line-height: 1.45;
        text-align: left;
        overflow-wrap: anywhere;
    }

    /* Text secundari fitxer */
    .file-explorer-muted {
        color: var(--studio-text-soft);
    }

    /* Resum seleccio */
    .file-explorer-selection {
        color: var(--studio-text-soft);
        font-size: 0.95rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        min-height: 3rem;
    }

    /* Botó carpeta */
    div[data-testid="stButton"] > button[kind="secondary"],
    div[data-testid="stButton"] > button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        color: var(--studio-text) !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
        width: 100% !important;
        min-height: auto !important;
        justify-content: flex-start !important;
        font-weight: 600 !important;
    }

    /* Text botó carpeta */
    div[data-testid="stButton"] > button[kind="secondary"] p,
    div[data-testid="stButton"] > button[data-testid="baseButton-secondary"] p {
        margin: 0 !important;
        width: 100% !important;
        text-align: left !important;
        white-space: normal !important;
        line-height: 1.45 !important;
    }

    /* Hover botó carpeta */
    div[data-testid="stButton"] > button[kind="secondary"]:hover,
    div[data-testid="stButton"] > button[data-testid="baseButton-secondary"]:hover {
        background: transparent !important;
        color: var(--studio-accent) !important;
        transform: none !important;
    }

    /* Upload fitxers */
    div[data-testid="stFileUploader"] {
        margin: 0.4rem 0 1rem 0;
    }

    /* Separador fila fitxer */
    .file-explorer-row-spacer {
        height: 0.38rem;
    }
</style>
"""


def inject_file_manager_styles() -> None:
    """Injecteu el CSS específic de la pàgina per a la pàgina Gestor de fitxers."""
    inject_studio_theme(max_width=1220)
    st.markdown(GESTIONAR_ARXIUS_CSS, unsafe_allow_html=True)
