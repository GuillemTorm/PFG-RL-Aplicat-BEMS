"""Pàgina inicial de BEMS-RL STUDIO."""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output

import streamlit as st

from page_styles.inici import inject_home_styles
from sidebar_nav import configure_studio_page


PAGE_TITLE = "BEMS-RL STUDIO"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Benvingut a BEMS-RL STUDIO, una interfície gràfica per treballar "
    "amb Reinforcement Learning en simulacions energètiques d'edificis."
)
NAVIGATION_HINT = "Utilitza el menú lateral per accedir a cada secció."
RESOURCES_DIR = Path(__file__).resolve().parent / "resources"
ENERGYPLUS_LOGO_PATH = RESOURCES_DIR / "energyplus-logo.png"


@st.cache_data(show_spinner=False)
def get_energyplus_logo_data_uri() -> str:
    """Carrega el logo d'EnergyPlus com a data URI per incrustar-lo a la UI."""

    if not ENERGYPLUS_LOGO_PATH.exists():
        return ""

    encoded_logo = base64.b64encode(ENERGYPLUS_LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded_logo}"


@st.cache_data(show_spinner=False)
def detect_energyplus_status() -> tuple[bool, str]:
    """Retorna si EnergyPlus està disponible i el missatge per mostrar a la UI."""

    try:
        version = check_output(["energyplus", "--version"], stderr=STDOUT).decode("utf-8").strip()
    except (CalledProcessError, FileNotFoundError, OSError):
        return (
            False,
            "No s'ha detectat una instal·lació d'EnergyPlus al sistema operatiu o no està disponible al PATH.",
        )

    if not version:
        return False, "EnergyPlus respon sense versió. Revisa la instal·lació del motor."

    return True, f"Motor actiu detectat: {version}"


def render_hero() -> None:
    """Mostra el bloc principal de presentació."""

    # Hero home
    st.markdown(
        f"""
        <section class="home-hero">
            <div class="hero-kicker">Plataforma de simulació energètica</div>
            <h1 class="hero-title">{escape(PAGE_TITLE)}</h1>
            <div class="hero-copy">{escape(INTRODUCTION_TEXT)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_status_panel(energyplus_available: bool, energyplus_message: str) -> None:
    """Mostra l'estat d'EnergyPlus amb una targeta visual."""

    status_title = "EnergyPlus detectat" if energyplus_available else "EnergyPlus no disponible"
    status_class = "status-ok" if energyplus_available else "status-warning"
    logo_data_uri = get_energyplus_logo_data_uri()
    logo_html = ""
    if logo_data_uri:
        logo_html = f'<img class="status-logo" src="{logo_data_uri}" alt="EnergyPlus logo">'

    # Targeta estat EnergyPlus
    st.markdown(
        f"""
        <section class="home-panel home-top-panel status-shell {status_class}">
            {logo_html}
            <div class="panel-kicker">Entorn de simulació</div>
            <div class="panel-title">{escape(status_title)}</div>
            <div class="panel-copy status-copy">{escape(energyplus_message)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_navigation_panel() -> None:
    """Dibuixa la pista de navegació lateral."""

    # Targeta navegacio home
    st.markdown(
        f"""
        <section class="home-panel home-top-panel">
            <div class="panel-kicker">Navegació</div>
            <div class="panel-title">Començar a treballar</div>
            <div class="panel-copy">{escape(NAVIGATION_HINT)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_organization_footer() -> None:
    """Afegeix el bloc informatiu final."""

    # Targeta peu projecte
    st.markdown(
        """
        <section class="footer-card">
            <div class="panel-kicker">Projecte</div>
            <div class="footer-title">Desenvolupat per SUNO</div>
            <div class="footer-copy">
                Aquest projecte ha estat desenvolupat per
                <a href="https://www.suno.cat/" target="_blank">SUNO</a>,
                una empresa pionera en simulació energètica d'edificis,
                optimització de sistemes i integració de solucions
                d'intel·ligència artificial.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_home_page() -> None:
    """Munta la pàgina inicial."""

    configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
    inject_home_styles()
    energyplus_available, energyplus_message = detect_energyplus_status()

    render_hero()

    # Columnes estat i navegacio
    status_col, navigation_col = st.columns(2, gap="large")
    with status_col:
        render_status_panel(energyplus_available, energyplus_message)
    with navigation_col:
        render_navigation_panel()

    render_organization_footer()


render_home_page()
