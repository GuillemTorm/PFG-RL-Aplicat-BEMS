"""Pàgina per avaluar un agent SB3 entrenat en un entorn Sinergym.

Escaneja models, detecta l'entorn més probable i executa l'avaluació en segon pla
perquè la interfície continuï responent mentre EnergyPlus treballa.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st
from page_components.ui_fragments import (
    render_hero,
    render_info_panel,
    render_runtime_progress,
    render_section_title,
)
from page_styles.runtime_pages import inject_evaluation_styles
from sidebar_nav import configure_studio_page

from backend.avaluar_agent_backend import (
    ONE_YEAR_STEPS,
    load_model_metadata,
    load_sb3_model_bytes,
    consume_evaluation_runtime_rerun_flag,
    request_evaluation_stop,
    reset_evaluation_runtime,
    start_evaluation_run,
    sync_evaluation_runtime,
)
from backend.sb3_utils import (
    candidate_vecnorm,
    env_id_from_meta_or_name,
    scan_model_zips,
)
PAGE_TITLE = "Avaluar Agent"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Carrega un model entrenat, revisa la configuració detectada i executa una "
    "avaluació controlada sobre un entorn Sinergym."
)
def _key(s: str) -> str:
    """Key."""
    return f"eval_{s}"

def render_metadata_grid(cards: list[tuple[str, list[tuple[str, str]]]]) -> None:
    """Mostra un resum en graella amb targetes d'alçada uniforme."""

    cards_markup = ""
    for kicker, items in cards:
        items_markup = "".join(
            (
                '<div class="eval-meta-item">'
                f'<span class="eval-meta-label">{escape(label)}</span>'
                f'<span class="eval-meta-value">{escape(value)}</span>'
                "</div>"
            )
            for label, value in items
        )
        cards_markup += (
            '<section class="eval-meta-card">'
            f'<div class="eval-meta-kicker">{escape(kicker)}</div>'
            f"{items_markup}"
            "</section>"
        )

    # Graella configuracio detectada
    st.markdown(
        f'<div class="eval-meta-grid">{cards_markup}</div>',
        unsafe_allow_html=True,
    )


def render_evaluation_runtime(runtime: dict[str, object]) -> None:
    """Mostra el progrés i el resultat de l'avaluació activa."""

    render_section_title("Estat de l'avaluació")
    display_runtime = dict(runtime)
    if str(display_runtime.get("status") or "").strip().startswith("Passos:"):
        display_runtime["status"] = ""
    render_runtime_progress(display_runtime, progress_label="Progrés", freeze_from_result=True)

    if runtime.get("cancel_requested") and runtime.get("running"):
        # Avís cancel·lació avaluació
        st.warning("S'ha sol·licitat l'aturada. L'avaluació es tancarà al proper punt segur.")

    if runtime.get("error"):
        # Error runtime avaluació
        st.error(str(runtime.get("error")))
        if runtime.get("traceback"):
            with st.expander("Traceback intern", expanded=False):
                st.code(str(runtime.get("traceback")), language="text")
        return

    result = runtime.get("result")
    if result is None or runtime.get("running"):
        return

    for warn_msg in getattr(result, "warnings", ()):
        # Avís resultat avaluacio
        st.warning(warn_msg)

    if bool(getattr(result, "cancelled", False)):
        # Avís avaluacio cancel·lada
        st.warning(
            f"Avaluació cancel·lada per l'usuari després de {float(getattr(result, 'elapsed_seconds', 0.0)):.2f} s."
        )
    else:
        # Missatge avaluacio finalitzada
        st.success(
            f"Avaluació finalitzada en {float(getattr(result, 'elapsed_seconds', 0.0)):.2f} s."
        )


def render_evaluation_runtime_frame() -> None:
    """Manté sincronitzat el bloc d'estat amb el runtime en segon pla."""

    runtime = sync_evaluation_runtime()
    if runtime.get("running") or runtime.get("completed") or runtime.get("error") or runtime.get("result"):
        st.divider()
        render_evaluation_runtime(runtime)

    if consume_evaluation_runtime_rerun_flag(runtime):
        st.rerun()


render_evaluation_runtime_fragment = st.fragment(run_every="1s")(render_evaluation_runtime_frame)


configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
inject_evaluation_styles()

st.session_state.setdefault(_key("dirs"), ",".join([str(Path.cwd() / "models"), str(Path.cwd())]))
st.session_state.setdefault(_key("selected_idx"), 0)
st.session_state.setdefault(_key("deterministic"), True)
st.session_state.setdefault(_key("use_vecnorm"), True)
st.session_state.setdefault(_key("steps"), ONE_YEAR_STEPS)

render_hero("eval-hero", "Validació del model", PAGE_TITLE, INTRODUCTION_TEXT)

# Panells resum avaluacio
summary_col, scale_col = st.columns(2, gap="large")
with summary_col:
    render_info_panel(
        "eval-panel",
        "Avaluació controlada",
        "Objectiu",
        "Carrega un model SB3, detecta l'entorn probable i executa una passada completa amb seguiment de progrés.",
    )
    with scale_col:
        render_info_panel(
        "eval-panel",
        f"{ONE_YEAR_STEPS} passos per defecte",
        "Escala",
            "La configuració inicial parteix d'una avaluació equivalent a un any aproximat de simulació.",
        )

    # Separador localitzacio models
    st.markdown("<div class='studio-spacer-115'></div>", unsafe_allow_html=True)
render_section_title("Localització de models")
dirs_text = st.session_state[_key("dirs")]
df_models = scan_model_zips(dirs_text)
runtime = sync_evaluation_runtime()
controls_disabled = bool(runtime.get("running"))

if df_models.empty:
    # Avís models no trobats
    st.info("No s'han trobat models .zip als directoris indicats.")
    st.stop()

options = list(range(len(df_models)))
# Selector model entrenat
idx = st.selectbox(
    "Selecciona el model entrenat (.zip)",
    options=options,
    format_func=lambda i: str(df_models.iloc[i]["stem"]),
    index=min(st.session_state[_key("selected_idx")], len(df_models) - 1),
    disabled=controls_disabled,
)
st.session_state[_key("selected_idx")] = idx

row = df_models.iloc[idx]
model_path = Path(row["path"])
zip_stem = row["stem"]

with open(model_path, "rb") as fh:
    model_tmp, meta = load_sb3_model_bytes(fh.read(), device="cpu")

algo_name = type(model_tmp).__name__
policy_name = type(getattr(model_tmp, "policy", object())).__name__

model_metadata = load_model_metadata(model_path)
env_id_guess = model_metadata.get("env_id") or env_id_from_meta_or_name(meta, zip_stem)
vecnorm_path = candidate_vecnorm(model_path)
wrapper_configs = model_metadata.get("wrapper_configs", [])
wrapper_names = [
    str(wrapper.get("name"))
    for wrapper in wrapper_configs
    if isinstance(wrapper, dict) and wrapper.get("name")
]
wrappers_label = ", ".join(wrapper_names) if wrapper_names else "Cap (metadades no trobades)"

render_section_title("Configuració detectada")
render_metadata_grid(
    [
        (
            "Model",
            [
                ("Agent", zip_stem),
                ("Algorisme", algo_name),
            ],
        ),
        (
            "Configuració",
            [
                ("Política", policy_name),
                ("VecNormalize", vecnorm_path.name if vecnorm_path else "No"),
            ],
        ),
        (
            "Context",
            [
                ("Entorn detectat", env_id_guess or "No detectat"),
                ("Wrappers d'entrenament", wrappers_label),
                ("Observacions esperades", str(getattr(model_tmp.observation_space, "shape", ("?",))[0])),
            ],
        ),
    ]
)

st.divider()

render_section_title("Paràmetres d'avaluació")
env_id = env_id_guess or ""
# Controls opcions avaluacio
col_b, col_c = st.columns(2)
with col_b:
    # Checkbox mode deterministic
    st.checkbox(
        "Deterministic",
        key=_key("deterministic"),
        value=st.session_state[_key("deterministic")],
        disabled=controls_disabled,
    )
with col_c:
    # Checkbox VecNormalize
    st.checkbox(
        "Usar VecNormalize si hi és",
        key=_key("use_vecnorm"),
        value=bool(vecnorm_path),
        disabled=controls_disabled,
    )

# Input limit passos
steps_limit = st.number_input(
    "Límit de passos (per defecte 35040)",
    min_value=1,
    max_value=5_000_000,
    value=st.session_state[_key("steps")],
    step=35040,
    disabled=controls_disabled,
)

if not wrapper_configs:
    # Avís wrappers no trobats
    st.info(
        "No s'han trobat metadades de wrappers per aquest model. "
        "L'avaluació inferirà automàticament l'espai d'accions a partir del model i de l'entorn seleccionat."
    )

st.divider()

render_section_title("Control")
# Botons control avaluacio
col_run, col_cancel, col_reset = st.columns(3, gap="medium")
with col_run:
    # Botó iniciar avaluacio
    start_requested = st.button(
        "Iniciar avaluació",
        type="primary",
        width="stretch",
        disabled=controls_disabled or not env_id,
    )
with col_cancel:
    # Botó cancel·lar avaluacio
    cancel_requested = st.button(
        "Cancel·lar",
        width="stretch",
        disabled=not bool(runtime.get("running")),
    )
with col_reset:
    # Botó netejar estat
    reset_requested = st.button(
        "Netejar estat",
        width="stretch",
        disabled=not bool(runtime.get("completed") or runtime.get("error")),
    )

if cancel_requested and request_evaluation_stop(runtime):
    st.rerun()

if reset_requested:
    reset_evaluation_runtime()
    st.rerun()

if start_requested:
    start_result = start_evaluation_run(
        {
            "model_path": model_path,
            "env_id": env_id,
            "use_vecnorm": bool(st.session_state[_key("use_vecnorm")]),
            "vecnorm_path": vecnorm_path,
            "steps_target": int(steps_limit),
            "deterministic": bool(st.session_state[_key("deterministic")]),
            "wrapper_configs": wrapper_configs,
        }
    )
    for error in start_result.get("errors") or []:
        # Error inici avaluacio
        st.error(str(error))
    if start_result.get("started"):
        st.rerun()

render_evaluation_runtime_fragment()
