"""CSS de la barra lateral compartida de BEMS-RL Studio."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st


SIDEBAR_CSS = """
<style>
    /* Botons col·lapse sidebar */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"][aria-label*="sidebar" i],
    button[kind="header"][aria-label*="barra lateral" i] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Fons sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12192f 0%, #10162b 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.02);
    }

    /* Animacions sidebar */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] a,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        transition: none !important;
        animation: none !important;
    }

    /* Amplada sidebar */
    [data-testid="stSidebar"][aria-expanded="true"],
    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 18rem !important;
        max-width: 18rem !important;
        width: 18rem !important;
        transform: translateX(0) !important;
    }

    /* Amplada interior sidebar */
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child,
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 18rem !important;
        min-width: 18rem !important;
        max-width: 18rem !important;
        background: transparent;
        transform: translateX(0) !important;
    }

    /* Sidebar plegada */
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: 0 !important;
    }

    /* Contenidor sidebar */
    [data-testid="stSidebarContent"] {
        padding: 1rem 1rem 1.35rem;
        background: transparent;
    }

    /* Contingut usuari sidebar */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0;
    }

    /* Marca sidebar */
    [data-testid="stSidebar"] .studio-sidebar-brand {
        padding: 0.4rem 0.1rem 0.18rem;
        background: transparent;
        border: none;
        border-radius: 0;
        box-shadow: none;
    }

    /* Text marca sidebar */
    [data-testid="stSidebar"] .studio-sidebar-brand-title,
    [data-testid="stSidebar"] .studio-sidebar-brand-subtitle {
        color: #eef3ff;
        font-family: "Arial Narrow", "Aptos Narrow", "Bahnschrift SemiCondensed", sans-serif;
        font-weight: 800;
        letter-spacing: -0.045em;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] .studio-sidebar-brand-title {
        font-size: 2.22rem;
        line-height: 0.88;
    }

    [data-testid="stSidebar"] .studio-sidebar-brand-subtitle {
        margin-top: 0.06rem;
        font-size: 1.4rem;
        line-height: 0.92;
    }

    /* Separador sidebar */
    [data-testid="stSidebar"] .studio-sidebar-divider {
        height: 1px;
        margin: 1rem -1rem 1.08rem;
        background: rgba(255, 255, 255, 0.08);
    }

    /* Titol seccio sidebar */
    [data-testid="stSidebar"] .studio-sidebar-section {
        margin-top: 1.15rem;
        margin-bottom: 0.15rem;
        color: rgba(123, 113, 255, 0.96);
        font-family: "Consolas", "Bahnschrift", monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    /* Text seccio sidebar */
    [data-testid="stSidebar"] .studio-sidebar-section-copy {
        margin-bottom: 0.58rem;
        color: rgba(238, 243, 255, 0.60);
        font-size: 0.79rem;
        line-height: 1.34;
    }

    /* Espai enllaç sidebar */
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] {
        margin-bottom: 0.16rem;
    }

    /* Enllaç sidebar */
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] a,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        display: flex;
        align-items: center;
        min-height: 2.85rem;
        padding: 0.28rem 0.58rem;
        border-radius: 16px;
        border: 1px solid transparent;
        background: transparent;
        text-decoration: none !important;
    }

    /* Hover enllaç sidebar */
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] a:hover,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
        background: rgba(255, 255, 255, 0.045);
        border-color: rgba(255, 255, 255, 0.05);
    }

    /* Pagina activa sidebar */
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] a[aria-current="page"],
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
        background: linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.085) 0%,
            rgba(255, 255, 255, 0.06) 100%
        );
        border-color: rgba(255, 255, 255, 0.08);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    /* Text enllaç sidebar */
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] p,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
        color: #eef3ff !important;
        font-size: 0.98rem;
        font-weight: 700;
        letter-spacing: 0.005em;
    }

    /* Icona enllaç sidebar */
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] svg,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] svg {
        width: 1.1rem;
        height: 1.1rem;
        color: rgba(255, 255, 255, 0.68);
    }

    /* Icona pagina activa */
    [data-testid="stSidebar"] [data-testid="stPageLinkContainer"] a[aria-current="page"] svg,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] svg {
        color: #eef3ff;
    }

    /* Sidebar responsive */
    @media (max-width: 900px) {
        [data-testid="stSidebar"][aria-expanded="true"],
        [data-testid="stSidebar"][aria-expanded="false"] {
            min-width: 15.5rem !important;
            max-width: 15.5rem !important;
            width: 15.5rem !important;
        }

        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child,
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 15.5rem !important;
            min-width: 15.5rem !important;
            max-width: 15.5rem !important;
        }

        [data-testid="stSidebar"][aria-expanded="false"] + div,
        [data-testid="stSidebar"][aria-expanded="false"] ~ section {
            margin-left: 15.5rem !important;
        }

        [data-testid="stSidebarContent"] {
            padding: 0.9rem 0.8rem 1.1rem;
        }

        [data-testid="stSidebar"] .studio-sidebar-brand-title {
            font-size: 1.9rem;
        }

        [data-testid="stSidebar"] .studio-sidebar-brand-subtitle {
            font-size: 1.2rem;
        }
    }
</style>
"""


def inject_sidebar_shell_styles() -> None:
    """Injecta el CSS de la barra lateral aviat per reduir parpellejos en rerender."""

    st.markdown(dedent(SIDEBAR_CSS), unsafe_allow_html=True)
