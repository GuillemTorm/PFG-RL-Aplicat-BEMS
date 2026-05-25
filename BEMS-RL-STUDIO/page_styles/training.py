"""CSS del flux d'entrenament."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


TRAINING_CSS = """
<style>
    /* Camp resum entrenament guardat */
    .training-saved-field {
        margin: 0.1rem 0 0.9rem;
    }

    /* Separador camps entrenament */
    .training-saved-field + .training-saved-field {
        padding-top: 0.78rem;
        border-top: 1px solid var(--studio-line);
    }

    /* Label resum entrenament */
    .training-saved-label {
        margin-bottom: 0.15rem;
        color: var(--studio-text-soft);
        font-size: 0.78rem;
    }

    /* Valor resum entrenament */
    .training-saved-value {
        color: var(--studio-text);
        font-size: 0.98rem;
        font-weight: 600;
        line-height: 1.35;
        overflow-wrap: anywhere;
    }

    /* Missatge espera grafics */
    .training-live-wait {
        padding: 0.75rem 1rem;
        border: 1px solid #e0e7ff;
        border-radius: 10px;
        background: #f8faff;
        color: #6366f1;
        font-size: 0.88rem;
    }

    /* Estat grafics en viu */
    .training-live-status {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.75rem;
    }

    /* Badge en viu */
    .training-live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.18rem 0.75rem;
        border: 1px solid #a7f3d0;
        border-radius: 999px;
        background: #ecfdf5;
        color: #059669;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
    }

    /* Punt en viu */
    .training-live-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
    }

    /* Comptador episodis */
    .training-live-count {
        color: var(--studio-text-soft);
        font-size: 0.85rem;
    }

    /* Text hero entrenament */
    .training-hero .hero-copy {
        max-width: 56rem;
    }

    /* Grafic entrenament en viu */
    .training-live-status + div[data-testid="stPlotlyChart"] {
        margin-top: 0.25rem;
    }
</style>
"""


def inject_training_styles() -> None:
    """Aplica el tema i el CSS del flux d'entrenament."""

    inject_studio_theme(max_width=1220)
    st.markdown(TRAINING_CSS, unsafe_allow_html=True)
