"""Constants de pàgina d'entrenament compartides i components de capçalera reutilitzables."""

from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from backend.entrenar_agent_artifacts import list_saved_training_runs
from backend.entrenar_agent_constants import TRAINING_RESULT_KEY
from backend.entrenar_agent_session import (
    TRAINING_LOADED_ARTIFACT_KEY,
    TRAINING_SAVED_RUN_KEY,
    apply_saved_training_ui_state,
)
from page_styles.training import inject_training_styles

PAGE_TITLE = "Entrenar model RL"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Configura l'entorn, la reward, els wrappers i els parametres de l'agent "
    "per llançar entrenaments SB3 amb una presentacio mes clara i ordenada."
)

# ── Components de renderització ───────────────────────────────────────────────


def render_training_hero() -> None:
    """Mostra el bloc de capçalera principal de la pàgina a la UI de Streamlit."""
    # Hero entrenament
    st.markdown(
        f"""
        <section class="training-hero">
            <div class="hero-kicker">Entrenament i configuracio</div>
            <h1 class="hero-title">{escape(PAGE_TITLE)}</h1>
            <div class="hero-copy">{escape(INTRODUCTION_TEXT)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_training_section(title: str, kicker: str, description: str) -> None:
    """Crea la capçalera visual d'una secció de pàgina a la UI de Streamlit."""
    # Titol seccio entrenament
    st.markdown(f'<h2 class="page-section-title">{escape(title)}</h2>', unsafe_allow_html=True)


def format_saved_training_label(run: dict) -> str:
    """Retorna una etiqueta llegible per persones per a una cursa d'entrenament desada."""
    created_at = run.get("created_at") or "-"
    env_id = run.get("env_id") or "-"
    reward_name = run.get("reward_name") or "-"
    return f"{run.get('artifact_name', 'training')} | {env_id} | {reward_name} | {created_at}"


def render_saved_training_field(label: str, value: object) -> None:
    """Mostra un únic camp etiquetat dins de la biblioteca de entrenament desada."""
    # Camp entrenament guardat
    st.markdown(
        f"""
        <div class="training-saved-field">
            <div class="training-saved-label">{escape(label)}</div>
            <div class="training-saved-value">{escape(str(value or "-"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_saved_training_library(envs: list[str]) -> None:
    """Mostra la biblioteca d'entrenaments desats amb controls d'upload i download."""
    render_training_section(
        "Scripts guardats",
        "Historial",
        "Recarrega configuracions anteriors i descarrega l'script literal de cada experiment.",
    )

    saved_runs = list_saved_training_runs()
    last_saved_run = st.session_state.get(TRAINING_RESULT_KEY)
    if last_saved_run:
        # Missatge entrenament guardat
        st.success(f"S'ha guardat l'entrenament `{last_saved_run.get('artifact_name', 'training')}`.")

    if not saved_runs:
        # Avís biblioteca buida
        st.info("Encara no hi ha scripts d'entrenament guardats.")
        return

    # Fem servir artifact_name com a clau estable: és el que també apareix al nom del model
    # i evita confondre runs amb el mateix entorn però configuracions diferents.
    run_map = {run["artifact_name"]: run for run in saved_runs if run.get("artifact_name")}
    run_names = list(run_map.keys())
    selected_run_name = st.session_state.get(TRAINING_SAVED_RUN_KEY)
    if selected_run_name not in run_map and run_names:
        st.session_state[TRAINING_SAVED_RUN_KEY] = run_names[0]

    # Selector entrenament guardat
    selected_run_name = st.selectbox(
        "Entrenament guardat",
        run_names,
        key=TRAINING_SAVED_RUN_KEY,
        format_func=lambda name: format_saved_training_label(run_map[name]),
    )
    selected_run = run_map[selected_run_name]

    # Camps resum entrenament
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        render_saved_training_field("Entorn", selected_run.get("env_id", "-"))
    with info_col2:
        render_saved_training_field("Reward", selected_run.get("reward_name", "-"))

    script_path = Path(selected_run.get("training_script_path", ""))
    # Botons entrenament guardat
    controls_col1, controls_col2 = st.columns(2)
    # Botó carregar configuracio
    if controls_col1.button("Carregar configuracio", width="stretch"):
        ui_state = selected_run.get("ui_state") or {}
        if not ui_state:
            # Avís configuracio absent
            st.warning("Aquest entrenament no te una configuracio recarregable.")
        else:
            # Recarregar només toca l'estat dels widgets; l'entrenament encara no comença
            # fins que l'usuari prem el botó principal.
            apply_saved_training_ui_state(ui_state, envs)
            st.session_state[TRAINING_LOADED_ARTIFACT_KEY] = selected_run.get("artifact_name")
            st.rerun()

    if script_path.is_file():
        # Botó download script
        controls_col2.download_button(
            "Descarregar script",
            data=script_path.read_bytes(),
            file_name=script_path.name,
            mime="text/x-python",
            width="stretch",
        )
    else:
        # Avís script absent
        controls_col2.warning("No s'ha trobat el fitxer .py d'aquest entrenament.")

    loaded_artifact = st.session_state.get(TRAINING_LOADED_ARTIFACT_KEY)
    if loaded_artifact:
        # Missatge configuracio carregada
        st.info(f"Configuracio carregada a la UI: `{loaded_artifact}`")
