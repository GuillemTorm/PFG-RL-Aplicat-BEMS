"""Streamlit frontend per a la pàgina de resultats de BEMS-RL STUDIO."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from sidebar_nav import configure_studio_page

from backend.resultats_backend import (
    DashboardData,
    build_results_page_state,
    get_run_artifacts,
    load_dashboard_data,
)
from page_components.resultats_dashboard import render_inline_dashboard
from page_components.ui_fragments import render_hero
from page_styles.resultats import inject_results_page_styles


PAGE_TITLE = "Resultats"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Explora els resultats d'una execució RL, descarrega els CSV principals "
    "i obre el dashboard analític."
)

def build_download_filename(prefix: str, run_name: str) -> str:
    """Crea un nom de fitxer de descàrrega estable CSV per a una execució seleccionada."""

    sanitized_run_name = "".join(
        c if c.isalnum() or c in {"-", "_"} else "-" for c in run_name.strip()
    ).strip("-")
    if not sanitized_run_name:
        sanitized_run_name = "entrenament"
    return f"{prefix}-{sanitized_run_name}.csv"


def render_results_page() -> None:
    """Prepara la pàgina de resultats: selector d'execució, dashboard i downloads CSV."""

    configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
    inject_results_page_styles()

    base_dir = str(Path.cwd())
    render_hero("results-hero", "Analítica i exportació", PAGE_TITLE, INTRODUCTION_TEXT)

    # La cerca de runs i la validació dels CSV queden fora de la UI principal perquè
    # aquesta funció només decideixi què es mostra i quan es carrega el dashboard.
    page_state = build_results_page_state(base_dir)

    # Separador resultats
    st.markdown("<div class='studio-spacer-115'></div>", unsafe_allow_html=True)
    # Titol seleccio resultats
    st.markdown('<h2 class="section-title">Selecció</h2>', unsafe_allow_html=True)

    if page_state.warning_message:
        # Avís resultats
        st.warning(page_state.warning_message)
        st.stop()

    try:
        # Fila seleccio i dashboard
        selection_cols = st.columns([10, 1.15], gap="small", vertical_alignment="center")
    except TypeError:
        # Fila seleccio i dashboard
        selection_cols = st.columns([10, 1.15], gap="small")
    with selection_cols[0]:
        # Selector execucio
        selected_run = st.selectbox("Selecciona l'execució", page_state.run_dirs)

    run_artifacts = get_run_artifacts(selected_run.path)
    if run_artifacts.error_message:
        # Error artefactes resultats
        st.error(run_artifacts.error_message)
        st.stop()

    with selection_cols[1]:
        try:
            # Botó generar dashboard
            generate_requested = st.button(
                " ",
                icon=":material/insert_chart:",
                help="Generar Dashboard",
                key="generate_dashboard_button",
                width="stretch",
            )
        except TypeError:
            # Botó generar dashboard
            generate_requested = st.button(
                "◫",
                help="Generar Dashboard",
                key="generate_dashboard_button",
                width="stretch",
            )

    if generate_requested:
        with st.spinner("Carregant dades del dashboard..."):
            try:
                # Guardem el dashboard a session_state perquè no es torni a carregar en cada
                # interacció menor, com fer download d'un CSV o obrir una pestanya.
                dashboard_data = load_dashboard_data(
                    run_artifacts.progress_path,
                    run_artifacts.observations_path,
                )
                st.session_state["_inline_dashboard_data"] = dashboard_data
                st.session_state["_inline_dashboard_run_path"] = selected_run.path
            except Exception as exc:
                # Error carregar dashboard
                st.error(f"Error carregant el dashboard: {exc}")

    inline_data: DashboardData | None = st.session_state.get("_inline_dashboard_data")
    active_run_path: str | None = st.session_state.get("_inline_dashboard_run_path")

    if inline_data is not None and active_run_path == selected_run.path:
        # Dashboard resultats
        render_inline_dashboard(inline_data, page_state.run_dirs, selected_run.path)

    # Botons download CSV
    download_cols = st.columns(2, gap="large")
    with download_cols[0]:
        # Botó download entrenament
        st.download_button(
            "Descarregar dades d'entrenament",
            data=Path(run_artifacts.progress_path).read_bytes(),
            file_name=build_download_filename("entrenament", selected_run.name),
            mime="text/csv",
            width="stretch",
        )
    with download_cols[1]:
        # Botó download monitor
        st.download_button(
            "Descarregar dades monitor",
            data=Path(run_artifacts.observations_path).read_bytes(),
            file_name=build_download_filename("monitor", selected_run.name),
            mime="text/csv",
            width="stretch",
        )


render_results_page()
