"""CSS de la pàgina inicial."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


HOME_CSS = """
<style>
    /* Hero home */
    .home-hero {
        margin-bottom: 1.8rem;
    }

    /* Panell superior home */
    .home-top-panel {
        min-height: 15rem;
        padding: 1.35rem 1.4rem;
    }

    /* Kicker panells home */
    .home-panel .panel-kicker,
    .footer-card .panel-kicker {
        margin-bottom: 0.82rem;
    }

    /* Titols panells home */
    .home-panel .panel-title,
    .footer-card .footer-title {
        margin-bottom: 0.62rem;
    }

    /* Targeta estat EnergyPlus */
    .status-shell {
        position: relative;
        padding-right: 7rem;
    }

    /* Logo EnergyPlus */
    .status-logo {
        position: absolute;
        bottom: 1.25rem;
        right: 1.4rem;
        width: 4.9rem;
        height: auto;
        object-fit: contain;
        opacity: 0.97;
    }

    /* Text estat EnergyPlus */
    .status-copy {
        margin-top: 0.85rem;
    }

    /* Targeta peu home */
    .footer-card {
        margin-top: 3.1rem;
        padding: 1.5rem 1.6rem;
    }

    /* Home responsive */
    @media (max-width: 900px) {
        .status-shell {
            padding-right: 5.4rem;
        }

        .status-logo {
            bottom: 1rem;
            right: 1.05rem;
            width: 4rem;
        }

        .home-hero {
            margin-bottom: 1.35rem;
        }

        .home-top-panel {
            padding: 1.2rem 1.1rem;
        }

        .footer-card {
            padding: 1.15rem 1.1rem;
        }

        .footer-card {
            margin-top: 2.2rem;
        }
    }
</style>
"""


def inject_home_styles() -> None:
    """Aplica l'estil visual específic de la pàgina inicial."""

    inject_studio_theme(max_width=1180)
    st.markdown(HOME_CSS, unsafe_allow_html=True)
