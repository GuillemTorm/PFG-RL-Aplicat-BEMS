"""CSS de la pàgina d'interacció en directe."""

from __future__ import annotations

import streamlit as st

from page_styles.theme import inject_studio_theme


INTERACTION_CSS = """
<style>
    /* Hero control viu */
    .interaction-hero {
        padding: 1.45rem 1.65rem;
        background: #ffffff;
    }

    /* Text hero control viu */
    .interaction-hero .hero-copy {
        max-width: 58rem;
    }

    /* Targeta seccio control viu */
    .interaction-section-card {
        margin-bottom: 0.85rem;
        padding: 1rem 1.05rem;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
    }

    /* Text seccio control viu */
    .interaction-section-card .section-copy {
        max-width: 62rem;
        font-size: 0.94rem;
        line-height: 1.55;
    }

    /* Ancora targeta entorn */
    .interaction-env-card-anchor {
        display: none;
    }

    /* Targeta mode entorn */
    div[data-testid="stVerticalBlock"]:has(.studio-radio-card-anchor),
    div[data-testid="stVerticalBlock"]:has(.interaction-env-card-anchor) {
        width: 100%;
        height: 100%;
    }

    /* Columna mode entorn */
    div[data-testid="stColumn"]:has(.studio-radio-card-anchor),
    div[data-testid="stColumn"]:has(.interaction-env-card-anchor),
    div[data-testid="stColumn"]:has(.studio-radio-card-anchor) > div,
    div[data-testid="stColumn"]:has(.interaction-env-card-anchor) > div {
        min-width: 0;
        width: 100%;
    }

    /* Control mode entorn */
    div[data-testid="stColumn"]:has(.studio-radio-card-anchor) div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]),
    div[data-testid="stColumn"]:has(.interaction-env-card-anchor) div[data-testid="stElementContainer"]:has(div[data-testid="stTextInput"]) {
        width: 100% !important;
    }

    /* Widgets control viu */
    div[data-testid="stTextInput"],
    div[data-testid="stSelectbox"],
    div[data-testid="stRadio"],
    div[data-testid="stNumberInput"],
    div[data-testid="stSlider"],
    div[data-testid="stCheckbox"] {
        width: 100%;
        padding: 0.78rem 0.9rem 0.7rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 8px 18px rgba(18, 27, 49, 0.05);
        box-sizing: border-box;
    }

    /* Widgets alts */
    div[data-testid="stTextInput"],
    div[data-testid="stSelectbox"],
    div[data-testid="stRadio"] {
        min-height: 7rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Widgets compactes */
    div[data-testid="stNumberInput"],
    div[data-testid="stSlider"],
    div[data-testid="stCheckbox"] {
        min-height: 5.25rem;
    }

    /* Labels control viu */
    div[data-testid="stTextInput"] > label,
    div[data-testid="stSelectbox"] > label,
    div[data-testid="stRadio"] > label,
    div[data-testid="stNumberInput"] > label,
    div[data-testid="stSlider"] > label,
    div[data-testid="stCheckbox"] > label {
        color: var(--studio-text);
        font-size: 0.9rem;
        font-weight: 700;
    }

    /* Opcions radio */
    div[data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.5rem;
    }

    /* Opcio radio */
    div[data-testid="stRadio"] [role="radiogroup"] > label {
        margin: 0;
        padding: 0.22rem 0;
    }

    /* Text radio */
    div[data-testid="stRadio"] [role="radiogroup"] > label p {
        color: var(--studio-text);
        font-size: 0.96rem;
        line-height: 1.35;
    }

    /* Input intern */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        min-height: 2.8rem !important;
    }

    /* Formulari consulta */
    div[data-testid="stForm"] {
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: var(--studio-shadow);
        padding: 1rem 1.05rem 1.15rem;
    }

    /* Targeta metrica */
    div[data-testid="stMetric"] {
        min-height: 104px;
        padding: 0.95rem 1rem;
        border: 1px solid var(--studio-line);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        box-shadow: 0 10px 20px rgba(18, 27, 49, 0.05);
    }

    /* Label metrica */
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
        color: #273a72;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* Valor metrica */
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--studio-text);
        font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
        font-size: clamp(1.35rem, 2.1vw, 1.65rem);
        font-weight: 800;
        line-height: 1.05;
    }

    /* Delta metrica */
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-weight: 700;
    }

    /* Taula observacions */
    div[data-testid="stDataFrame"] {
        margin-top: 0.35rem;
    }

    /* Botons control viu */
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 3rem;
        padding: 0.78rem 1.2rem;
    }

    /* Botó avançar */
    div[class*="st-key-ix_agent_step_button"] button,
    div[class*="st-key-ix_manual_step_button"] button {
        width: 100%;
        justify-content: center;
    }

    /* Contenidor inicialitzar */
    div[class*="st-key-ix_initialize_button"] {
        display: flex;
        justify-content: flex-start;
    }

    /* Botó inicialitzar */
    div[class*="st-key-ix_initialize_button"] button {
        width: min(100%, 20rem) !important;
        justify-content: center;
    }

    /* Botó aturar */
    div[class*="st-key-btn_stop_test"] button,
    div[class*="st-key-ix_stop_live_button"] button {
        background: linear-gradient(135deg, #d65555, #e27373) !important;
        box-shadow: 0 12px 22px rgba(214, 85, 85, 0.22) !important;
    }

    /* Botó observacions aleatories */
    div[class*="st-key-ix_randomize_observations"] button {
        background: #ffffff !important;
        border: 1px solid rgba(95, 84, 249, 0.26) !important;
        color: var(--studio-accent) !important;
        box-shadow: 0 8px 18px rgba(18, 27, 49, 0.05) !important;
    }

    /* Pestanyes control viu */
    .stTabs [data-baseweb="tab-list"] {
        margin: 0.15rem 0 0.85rem;
    }

    /* Panell pestanya */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0.15rem;
    }

    /* Bloc codi accio */
    .stCodeBlock,
    pre {
        background: #f8faff !important;
    }

    /* Valor confort correcte */
    .comfort-value-good {
        color: green;
        font-weight: 700;
    }

    /* Valor confort moderat */
    .comfort-value-warn {
        color: orange;
        font-weight: 700;
    }

    /* Valor confort dolent */
    .comfort-value-bad {
        color: red;
        font-weight: 700;
    }

    /* Control viu responsive */
    @media (max-width: 900px) {
        div[data-testid="stTextInput"],
        div[data-testid="stSelectbox"],
        div[data-testid="stRadio"] {
            min-height: auto;
        }

        div[data-testid="stNumberInput"],
        div[data-testid="stSlider"],
        div[data-testid="stCheckbox"] {
            min-height: auto;
        }
    }
</style>
"""


def inject_interaction_styles() -> None:
    """Injecteu el CSS específic de la pàgina per a la pàgina d'interacció en directe."""
    inject_studio_theme(max_width=1260, hide_first_heading=True)
    st.markdown(INTERACTION_CSS, unsafe_allow_html=True)
