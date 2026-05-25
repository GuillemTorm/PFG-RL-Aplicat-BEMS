"""Navegació lateral compartida de BEMS-RL STUDIO."""

from __future__ import annotations

import streamlit as st
from page_styles.sidebar import inject_sidebar_shell_styles


APP_NAME = "BEMS-RL STUDIO"

SIDEBAR_SECTIONS: tuple[tuple[str, str, tuple[tuple[str, str, str], ...]], ...] = (
    (
        "ENTORNS I AGENTS",
        "Configura, entrena i analitza",
        (
            ("Inici.py", "Inici", ":material/space_dashboard:"),
            ("pages/Afegir_Entorn.py", "Crear Entorn", ":material/home_work:"),
            ("pages/Mostrar_Entorn.py", "Mostrar Entorn", ":material/apartment:"),
            ("pages/Entrenar_Agent.py", "Entrenar Agent", ":material/model_training:"),
            ("pages/Resultats.py", "Resultats", ":material/insights:"),
            ("pages/Simular_Entorn.py", "Simular Entorn", ":material/play_circle:"),
            ("pages/Avaluar_Agent.py", "Avaluar Agent", ":material/fact_check:"),
            ("pages/Interaccionar_amb_l'Agent.py", "Control en Viu", ":material/joystick:"),
        ),
    ),
    (
        "GESTIÓ",
        "Organitza i inspecciona els fitxers del projecte",
        (
            ("pages/Gestionar_Arxius.py", "Arxius", ":material/folder_open:"),
            ("pages/Visor_Climes_EPW.py", "Visor EPW", ":material/cloud:"),
        ),
    ),
    (
        "SUPORT",
        "Guies i ajuda",
        (
            ("pages/Ajuda.py", "Centre d'Ajuda", ":material/support_agent:"),
        ),
    ),
)


def configure_studio_page(page_title: str, *, layout: str = "wide") -> None:
    """Configura una pàgina i renderitza la barra lateral compartida."""

    browser_title = page_title if page_title.upper().startswith(APP_NAME) else f"{APP_NAME} - {page_title}"
    st.set_page_config(
        page_title=browser_title,
        page_icon=":material/neurology:",
        layout=layout,
        initial_sidebar_state="expanded",
    )
    render_studio_sidebar()


def render_studio_sidebar() -> None:
    """Mostra la navegació personalitzada de la barra lateral de Streamlit."""

    inject_sidebar_shell_styles()

    with st.sidebar:
        # Marca de la barra lateral
        st.markdown(
            """
            <div class="studio-sidebar-brand">
                <div class="studio-sidebar-brand-title">BEMS-RL</div>
                <div class="studio-sidebar-brand-subtitle">STUDIO</div>
            </div>
            <div class="studio-sidebar-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        for section_title, section_copy, items in SIDEBAR_SECTIONS:
            _render_section_header(section_title, section_copy)
            for page_path, label, icon in items:
                # Enllaç de pàgina a la barra lateral
                st.page_link(page_path, label=label, icon=icon)


def _render_section_header(title: str, copy_text: str) -> None:
    """Crea la capçalera de la secció."""
    # Capçalera de secció de la barra lateral
    st.markdown(
        f"""
        <div class="studio-sidebar-section">{title}</div>
        <div class="studio-sidebar-section-copy">{copy_text}</div>
        """,
        unsafe_allow_html=True,
    )
