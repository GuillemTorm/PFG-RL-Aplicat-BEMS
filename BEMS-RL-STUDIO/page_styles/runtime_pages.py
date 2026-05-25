"""CSS compartit per a les pàgines de simulació i avaluació."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


EVALUATION_CSS = """
<style>
    /* Graella metadades model */
    .eval-meta-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1.15rem;
        align-items: stretch;
    }

    /* Targeta metadades model */
    .eval-meta-card {
        height: 100%;
        padding: 1.05rem 1.1rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 10px 22px rgba(18, 27, 49, 0.05);
    }

    /* Etiqueta targeta metadades */
    .eval-meta-kicker {
        display: inline-block;
        margin-bottom: 0.7rem;
        color: var(--studio-accent);
        font-family: "Consolas", "Bahnschrift", monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    /* Fila metadades model */
    .eval-meta-item + .eval-meta-item {
        margin-top: 0.95rem;
        padding-top: 0.95rem;
        border-top: 1px solid rgba(220, 227, 242, 0.85);
    }

    /* Label metadades model */
    .eval-meta-label {
        display: block;
        color: var(--studio-muted);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Valor metadades model */
    .eval-meta-value {
        display: block;
        margin-top: 0.22rem;
        color: var(--studio-text);
        font-size: 0.96rem;
        font-weight: 600;
        line-height: 1.42;
        word-break: break-word;
    }

    @media (max-width: 900px) {
        .eval-meta-grid {
            grid-template-columns: 1fr;
        }

        .eval-meta-card {
            padding: 0.95rem 1rem;
        }

        .eval-meta-value {
            font-size: 0.97rem;
        }
    }
</style>
"""


BASELINE_CSS = """
<style>
    /* Fila etiquetes baseline */
    .baseline-chip-row {
        display:flex;
        flex-wrap:wrap;
        gap:0.5rem;
        margin-top:0.25rem;
    }

    /* Etiqueta resum baseline */
    .baseline-chip {
        background:var(--studio-panel-soft);
        border:1px solid var(--studio-line);
        border-radius:999px;
        padding:0.38rem 0.78rem;
        font-size:0.84rem;
        color:var(--studio-text-soft);
    }

    /* Text destacat etiqueta baseline */
    .baseline-chip strong {
        color:var(--studio-accent);
        font-weight:700;
    }

    /* Nota configuracio baseline */
    .baseline-inline-note {
        color:var(--studio-muted);
        font-size:0.9rem;
        margin-top:0.35rem;
    }
</style>
"""


def inject_evaluation_styles() -> None:
    """Injecta el tema i CSS específic de la pàgina d'avaluació."""

    inject_studio_theme(max_width=1180)
    st.markdown(EVALUATION_CSS, unsafe_allow_html=True)


def inject_baseline_styles() -> None:
    """Injecta el tema i CSS específic de la pàgina de baseline."""

    inject_studio_theme(max_width=1180)
    st.markdown(BASELINE_CSS, unsafe_allow_html=True)
