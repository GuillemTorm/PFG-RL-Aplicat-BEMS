"""Tema visual compartit per donar coherència a les pàgines de BEMS-RL STUDIO."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st


PYDECK_TOOLTIP_STYLES = {
    "location": {"backgroundColor": "#17233c", "color": "white"},
    "multipoint": {"backgroundColor": "#14213d", "color": "white"},
}


def build_pydeck_tooltip(tooltip_html: str, *, variant: str = "location") -> dict[str, object]:
    """Prepara la configuració visual dels tooltips de mapes pydeck."""

    tooltip_style = PYDECK_TOOLTIP_STYLES.get(variant, PYDECK_TOOLTIP_STYLES["location"])
    return {"html": tooltip_html, "style": dict(tooltip_style)}


def inject_studio_theme(*, max_width: int = 1220, hide_first_heading: bool = False) -> None:
    """Injecteu el tema compartit Streamlit utilitzat a BEMS-RL STUDIO."""

    # Aquest tema és global i toca selectors interns de Streamlit. Per això es concentra
    # en una sola funció: si Streamlit canvia HTML, només cal revisar aquest fitxer.
    hide_heading_css = ""
    if hide_first_heading:
        hide_heading_css = """
            .main .block-container > div[data-testid="stHeadingWithActionElements"]:first-of-type {
                display: none;
            }
        """

    st.markdown(
        dedent(
            f"""
            <style>
                /* Variables tema */
                :root {{
                    --studio-shell: #eff2f8;
                    --studio-shell-deep: #e7ecf6;
                    --studio-panel: #ffffff;
                    --studio-panel-soft: #f7f9fe;
                    --studio-line: #dce3f2;
                    --studio-line-strong: #ccd6eb;
                    --studio-text: #17233c;
                    --studio-text-soft: #56617c;
                    --studio-muted: #7b86a2;
                    --studio-sidebar: #12192f;
                    --studio-sidebar-line: rgba(255, 255, 255, 0.08);
                    --studio-sidebar-text: #eef3ff;
                    --studio-sidebar-muted: rgba(238, 243, 255, 0.60);
                    --studio-accent: #5f54f9;
                    --studio-accent-2: #7b71ff;
                    --studio-accent-soft: rgba(95, 84, 249, 0.12);
                    --studio-warning: #d17b45;
                    --studio-shadow: 0 18px 34px rgba(18, 27, 49, 0.08);
                }}

                /* Font global */
                html,
                body,
                [class*="css"] {{
                    font-family: "Bahnschrift", "Aptos", "Segoe UI Variable Text", sans-serif;
                }}

                /* Fons aplicacio */
                [data-testid="stAppViewContainer"] {{
                    background: linear-gradient(180deg, var(--studio-shell) 0%, #f5f7fc 100%);
                    color: var(--studio-text);
                }}

                /* Capçalera Streamlit */
                header[data-testid="stHeader"] {{
                    background: var(--studio-shell) !important;
                    border-bottom: none !important;
                    box-shadow: none !important;
                }}

                /* Elements natius ocults */
                div[data-testid="stDecoration"],
                div[data-testid="stStatusWidget"],
                #MainMenu,
                footer {{
                    display: none !important;
                }}

                /* Barra superior Streamlit: necessària per reobrir la sidebar quan està plegada. */
                div[data-testid="stToolbar"] {{
                    display: flex !important;
                    visibility: visible !important;
                    pointer-events: auto !important;
                }}

                div[data-testid="stToolbarActions"],
                div[data-testid="stAppDeployButton"],
                span[data-testid="stMainMenu"] {{
                    display: none !important;
                }}

                /* Contenidor pagina */
                .main .block-container {{
                    max-width: {max_width}px;
                    padding-top: 1.25rem;
                    padding-bottom: 2.5rem;
                }}

                {hide_heading_css}

                /* Hero pagina */
                [class*="-hero"] {{
                    width: 100%;
                    margin-bottom: 1.15rem;
                    padding: 1.5rem 1.8rem;
                    border: 1px solid var(--studio-line);
                    border-radius: 18px;
                    background: var(--studio-panel);
                    box-shadow: 0 8px 18px rgba(18, 27, 49, 0.04);
                }}

                /* Targetes i panells */
                [class*="-panel"],
                [class*="-section-card"],
                .footer-card,
                .artifact-card,
                .resources-card,
                .section-card {{
                    border: 1px solid var(--studio-line);
                    border-radius: 18px;
                    background: var(--studio-panel);
                    box-shadow: var(--studio-shadow);
                    padding: 1.15rem 1.2rem;
                }}

                /* Panell generic */
                [class*="-panel"] {{
                    min-height: 10rem;
                }}

                /* Kicker seccio */
                .hero-kicker,
                .panel-kicker,
                .artifact-kicker,
                .section-kicker,
                .feature-kicker {{
                    display: inline-block;
                    margin-bottom: 0.65rem;
                    color: var(--studio-accent);
                    font-family: "Consolas", "Bahnschrift", monospace;
                    font-size: 0.72rem;
                    font-weight: 700;
                    letter-spacing: 0.14em;
                    text-transform: uppercase;
                }}

                /* Titols UI */
                .hero-title,
                .panel-title,
                .section-title,
                .artifact-title,
                .footer-title,
                .page-section-title {{
                    margin: 0;
                    color: var(--studio-text);
                    font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
                    letter-spacing: -0.02em;
                }}

                /* Titol hero */
                .hero-title {{
                    font-size: clamp(2rem, 3vw, 3rem);
                    line-height: 1.03;
                }}

                /* Titol targeta */
                .panel-title,
                .artifact-title,
                .footer-title {{
                    font-size: 1.28rem;
                    margin-bottom: 0.42rem;
                }}

                /* Titol seccio */
                .page-section-title,
                .section-title {{
                    margin: 1.8rem 0 0.85rem;
                    font-size: 1.6rem;
                }}

                /* Text descriptiu */
                .hero-copy,
                .panel-copy,
                .artifact-copy,
                .section-copy,
                .feature-copy,
                .footer-copy {{
                    color: var(--studio-text-soft);
                    font-size: 0.97rem;
                    line-height: 1.68;
                }}

                /* Text hero */
                .hero-copy {{
                    max-width: 52rem;
                    margin-top: 0.75rem;
                }}

                /* Fons targeta */
                .footer-card,
                .artifact-card,
                .resources-card,
                .section-card {{
                    background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
                }}

                /* Codi targeta */
                .artifact-copy code {{
                    white-space: pre-wrap;
                }}

                /* Targeta amb marge inferior */
                .section-card-spaced {{
                    margin-bottom: 0.85rem;
                }}

                /* Separadors verticals */
                .studio-spacer-045 {{ height: 0.45rem; }}
                .studio-spacer-070 {{ height: 0.7rem; }}
                .studio-spacer-075 {{ height: 0.75rem; }}
                .studio-spacer-100 {{ height: 1rem; }}
                .studio-spacer-115 {{ height: 1.15rem; }}
                .studio-spacer-125 {{ height: 1.25rem; }}

                /* Estat correcte */
                .status-ok {{
                    border-left: 4px solid var(--studio-accent);
                }}

                /* Estat avis */
                .status-warning {{
                    border-left: 4px solid var(--studio-warning);
                }}

                /* Widgets formulari */
                div[data-testid="stTextInput"],
                div[data-testid="stSelectbox"],
                div[data-testid="stMultiSelect"],
                div[data-testid="stNumberInput"],
                div[data-testid="stTextArea"],
                div[data-testid="stDateInput"],
                div[data-testid="stCheckbox"],
                div[data-testid="stRadio"],
                div[data-testid="stSlider"],
                div[data-testid="stFileUploader"] {{
                    border-radius: 16px;
                    border: 1px solid transparent;
                    background: transparent;
                    padding: 0;
                }}

                /* Camps entrada */
                div[data-baseweb="input"] > div,
                div[data-baseweb="select"] > div,
                textarea,
                input {{
                    min-height: 3rem;
                    border-radius: 14px !important;
                    border-color: var(--studio-line-strong) !important;
                    background: #ffffff !important;
                    box-shadow: inset 0 1px 2px rgba(18, 27, 49, 0.03);
                }}

                /* Selector BaseWeb */
                div[data-baseweb="select"] > div {{
                    height: 3rem !important;
                    max-height: 3rem !important;
                }}

                /* Etiqueta multiselect */
                div[data-baseweb="tag"] {{
                    background: var(--studio-accent-soft) !important;
                    border-radius: 999px !important;
                    color: var(--studio-text) !important;
                }}

                /* Botons principals */
                div[data-testid="stButton"] > button,
                div[data-testid="stDownloadButton"] > button {{
                    border-radius: 999px;
                    border: none;
                    background: linear-gradient(135deg, var(--studio-accent), var(--studio-accent-2));
                    color: #ffffff;
                    font-weight: 700;
                    padding: 0.78rem 1.35rem;
                    box-shadow: 0 12px 22px rgba(91, 85, 247, 0.24);
                }}

                /* Hover botons */
                div[data-testid="stButton"] > button:hover,
                div[data-testid="stDownloadButton"] > button:hover {{
                    background: linear-gradient(135deg, #5149ec, #7067ff);
                    color: #ffffff;
                    transform: translateY(-1px);
                }}

                /* Control segmentat */
                div[data-testid="stSegmentedControl"] {{
                    margin-bottom: 0.4rem;
                }}

                /* Grup segmentat */
                div[data-testid="stSegmentedControl"] [role="radiogroup"],
                div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] {{
                    gap: 0.85rem;
                    background: transparent !important;
                    border-bottom: 1px solid var(--studio-line);
                    border-radius: 0;
                    padding: 0 0 0.45rem;
                    flex-wrap: wrap;
                }}

                /* Botó segmentat */
                div[data-testid="stSegmentedControl"] button {{
                    padding: 0.42rem 0.88rem !important;
                    border: none !important;
                    border-radius: 0.9rem !important;
                    background: transparent !important;
                    color: var(--studio-muted) !important;
                    font-weight: 700 !important;
                    box-shadow: none !important;
                }}

                /* Hover segmentat */
                div[data-testid="stSegmentedControl"] button:hover {{
                    color: var(--studio-text) !important;
                    background: rgba(95, 84, 249, 0.07) !important;
                    transform: none;
                }}

                /* Segment actiu */
                div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
                div[data-testid="stSegmentedControl"] button[data-selected="true"] {{
                    background: rgba(95, 84, 249, 0.11) !important;
                    color: var(--studio-accent) !important;
                }}

                /* Ancores radio */
                .studio-radio-card-anchor,
                .studio-segmented-pill-anchor {{
                    display: none;
                }}

                /* Label radio card */
                div[data-testid="stVerticalBlock"]:has(.studio-radio-card-anchor) [data-testid="stWidgetLabel"] p,
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) [data-testid="stWidgetLabel"] p {{
                    color: var(--studio-text);
                    font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
                    font-size: 1.08rem;
                    font-weight: 500;
                    line-height: 1.25;
                }}

                /* Opcions radio card */
                div[data-testid="stVerticalBlock"]:has(.studio-radio-card-anchor) div[data-testid="stRadio"] [role="radiogroup"] {{
                    gap: 0.72rem;
                }}

                /* Label opcio radio */
                div[data-testid="stVerticalBlock"]:has(.studio-radio-card-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label {{
                    align-items: center;
                    padding: 0.05rem 0;
                }}

                /* Icona opcio radio */
                div[data-testid="stVerticalBlock"]:has(.studio-radio-card-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {{
                    transform: scale(1.16);
                    transform-origin: left center;
                }}

                /* Text opcio radio */
                div[data-testid="stVerticalBlock"]:has(.studio-radio-card-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label p {{
                    color: var(--studio-text) !important;
                    font-size: 1.15rem;
                    font-weight: 500;
                    line-height: 1.35;
                }}

                /* Segment pill */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"],
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] {{
                    margin-bottom: 0.25rem;
                }}

                /* Grup segment pill */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] [role="radiogroup"],
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] [data-baseweb="button-group"],
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] [role="radiogroup"] {{
                    gap: 0 !important;
                    width: min(100%, 460px);
                    border: 1px solid var(--studio-accent);
                    border-radius: 1rem !important;
                    background: rgba(255, 255, 255, 0.92) !important;
                    padding: 0 !important;
                    overflow: hidden;
                    box-shadow: none !important;
                }}

                /* Botó segment pill */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] button,
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label {{
                    flex: 1 1 0;
                    min-height: 3.3rem;
                    margin: 0 !important;
                    padding: 0.8rem 1.15rem !important;
                    border: none !important;
                    border-radius: 0 !important;
                    background: transparent !important;
                    color: var(--studio-text) !important;
                    font-size: 1.02rem !important;
                    font-weight: 500 !important;
                    box-shadow: none !important;
                    justify-content: center;
                }}

                /* Separador segment pill */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] button + button,
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label + label {{
                    border-left: 1px solid rgba(95, 84, 249, 0.32) !important;
                }}

                /* Hover segment pill */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] button:hover {{
                    background: rgba(95, 84, 249, 0.06) !important;
                    color: var(--studio-accent) !important;
                    transform: none;
                }}

                /* Segment pill actiu */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] button[data-selected="true"],
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {{
                    background: rgba(95, 84, 249, 0.14) !important;
                    color: var(--studio-accent) !important;
                }}

                /* Icona radio pill */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {{
                    display: none;
                }}

                /* Text segment pill */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label p,
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stSegmentedControl"] button p {{
                    margin: 0;
                }}

                /* Text pill actiu */
                div[data-testid="stVerticalBlock"]:has(.studio-segmented-pill-anchor) div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) p {{
                    color: var(--studio-accent) !important;
                }}

                /* Acordio */
                [data-testid="stExpander"] {{
                    border: 1px solid var(--studio-line);
                    border-radius: 18px;
                    background: var(--studio-panel);
                    box-shadow: var(--studio-shadow);
                    overflow: hidden;
                    margin-bottom: 0.9rem;
                }}

                /* Capçalera acordio */
                [data-testid="stExpander"] details summary {{
                    background: var(--studio-panel-soft);
                    border-bottom: 1px solid var(--studio-line);
                    padding-top: 0.2rem;
                    padding-bottom: 0.2rem;
                }}

                /* Text acordio */
                [data-testid="stExpander"] details summary p {{
                    color: var(--studio-text);
                    font-family: "Bahnschrift SemiCondensed", "Trebuchet MS", sans-serif;
                    font-size: 1.02rem;
                }}

                /* Pestanyes */
                .stTabs [data-baseweb="tab-list"] {{
                    gap: 0.85rem;
                    background: transparent;
                    border-bottom: 1px solid var(--studio-line);
                    border-radius: 0;
                    padding: 0 0 0.45rem;
                }}

                /* Pestanya */
                .stTabs [data-baseweb="tab"] {{
                    padding: 0.42rem 0.88rem;
                    border-radius: 0.9rem;
                    color: var(--studio-muted);
                    font-weight: 700;
                    line-height: 1.2;
                }}

                /* Pestanya activa */
                .stTabs [aria-selected="true"] {{
                    background: rgba(95, 84, 249, 0.11);
                    color: var(--studio-accent) !important;
                }}

                /* Taula dades */
                div[data-testid="stDataFrame"] {{
                    border: 1px solid var(--studio-line);
                    border-radius: 18px;
                    overflow: hidden;
                    background: #ffffff;
                    box-shadow: var(--studio-shadow);
                }}

                /* Alerta */
                div[data-testid="stAlert"] {{
                    border-radius: 16px;
                    border: 1px solid var(--studio-line);
                }}

                /* Bloc codi */
                .stCodeBlock,
                pre {{
                    border-radius: 16px !important;
                    border: 1px solid var(--studio-line) !important;
                    background: #f7f9ff !important;
                }}

                /* Tema responsive */
                @media (max-width: 900px) {{
                    .main .block-container {{
                        padding-top: 1rem;
                    }}

                    [class*="-hero"] {{
                        padding: 1.15rem 1.1rem;
                    }}

                    [class*="-panel"],
                    [class*="-section-card"],
                    .footer-card,
                    .artifact-card,
                    .resources-card,
                    .section-card {{
                        padding: 1rem;
                    }}
                }}
            </style>
            """
        ),
        unsafe_allow_html=True,
    )
