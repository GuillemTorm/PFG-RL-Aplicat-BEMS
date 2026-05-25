from __future__ import annotations

from functools import partial
from html import escape
import queue
import threading
import time
import traceback

import streamlit as st
from page_components.ui_fragments import render_hero, render_runtime_progress, render_section_card
from page_styles.runtime_pages import inject_baseline_styles
from sidebar_nav import configure_studio_page

from backend.common import ONE_YEAR_STEPS
from backend.simular_entorn_backend import (
    describe_environment,
    list_environment_ids,
    run_baseline_simulation,
)


PAGE_TITLE = "Simular Entorn"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Executa un baseline dels entorns amb els schedules normals d'EnergyPlus, "
    "sense control RL, i compara'l amb execucions que ja teniu guardades."
)
def _key(name: str) -> str:
    """Key."""
    return f"baseline_{name}"

def empty_baseline_runtime() -> dict[str, object]:
    """Temps d'execució de base buit."""
    return {
        "running": False,
        "completed": False,
        "cancel_requested": False,
        "needs_full_rerun": False,
        "thread": None,
        "queue": None,
        "stop_event": None,
        "result": None,
        "error": None,
        "traceback": None,
        "env_id": None,
        "steps_target": 1,
        "latest_step": 0,
        "status": "",
        "started_at": None,
        "stopped_at": None,
        "frozen_elapsed_seconds": None,
    }


def ensure_baseline_runtime() -> dict[str, object]:
    """Assegureu-vos el temps d'execució de referència."""
    runtime_key = _key("runtime")
    if runtime_key not in st.session_state:
        st.session_state[runtime_key] = empty_baseline_runtime()
    return st.session_state[runtime_key]


def reset_baseline_runtime() -> dict[str, object]:
    """Restableix el temps d'execució de referència."""
    runtime = ensure_baseline_runtime()
    previous_thread = runtime.get("thread")
    if previous_thread is not None and getattr(previous_thread, "is_alive", lambda: False)():
        return runtime

    st.session_state[_key("runtime")] = empty_baseline_runtime()
    return st.session_state[_key("runtime")]


def drain_baseline_runtime(runtime: dict[str, object]) -> None:
    """Esgota el temps d'execució de la línia base."""
    event_queue = runtime.get("queue")
    if event_queue is None:
        return

    # El worker escriu esdeveniments en una cua i Streamlit els buida a cada rerun.
    # Així la simulació pot continuar en segon pla sense bloquejar la interfície.
    while True:
        try:
            event = event_queue.get_nowait()
        except queue.Empty:
            break

        event_type = str(event.get("type") or "")
        if event_type == "progress":
            runtime["latest_step"] = max(
                int(runtime.get("latest_step") or 0),
                int(event.get("step_number") or 0),
            )
            runtime["steps_target"] = max(
                int(runtime.get("steps_target") or 1),
                int(event.get("total_steps") or 1),
            )
            runtime["status"] = str(event.get("status") or runtime.get("status") or "")
        elif event_type == "result":
            runtime["result"] = event.get("result")
            result = runtime["result"]
            if result is not None and runtime.get("frozen_elapsed_seconds") is None:
                runtime["frozen_elapsed_seconds"] = float(getattr(result, "elapsed_seconds", 0.0))
            runtime["completed"] = True
            runtime["running"] = False
            runtime["needs_full_rerun"] = True
        elif event_type == "error":
            runtime["error"] = str(event.get("error") or "Error desconegut durant la simulacio.")
            runtime["traceback"] = event.get("traceback")
            runtime["completed"] = True
            runtime["running"] = False
            runtime["needs_full_rerun"] = True
        elif event_type == "finished":
            runtime["completed"] = True
            runtime["running"] = False
            runtime["thread"] = None
            runtime["needs_full_rerun"] = True

    thread = runtime.get("thread")
    if thread is not None and not thread.is_alive() and runtime.get("running"):
        runtime["running"] = False
        runtime["completed"] = True
        runtime["thread"] = None
        runtime["needs_full_rerun"] = True


def sync_baseline_runtime() -> dict[str, object]:
    """Sincronitza el temps d'execució de referència."""
    runtime = ensure_baseline_runtime()
    drain_baseline_runtime(runtime)
    return runtime


def consume_baseline_rerun_flag(runtime: dict[str, object] | None = None) -> bool:
    """Consumeix la bandera de repetició de la línia de base."""
    active_runtime = runtime if runtime is not None else ensure_baseline_runtime()
    if active_runtime.get("needs_full_rerun") and not active_runtime.get("running"):
        active_runtime["needs_full_rerun"] = False
        return True
    return False


def request_baseline_stop(runtime: dict[str, object] | None = None) -> bool:
    """Sol·licita l'aturada de la línia de base."""
    active_runtime = runtime if runtime is not None else ensure_baseline_runtime()
    if not active_runtime.get("running") or active_runtime.get("stop_event") is None:
        return False

    active_runtime["cancel_requested"] = True
    active_runtime["status"] = "Aturant simulacio..."
    active_runtime["stopped_at"] = time.time()
    started_at = active_runtime.get("started_at")
    if started_at:
        active_runtime["frozen_elapsed_seconds"] = max(0.0, float(active_runtime["stopped_at"]) - float(started_at))
    active_runtime["stop_event"].set()
    return True


def push_baseline_progress_event(
    event_queue: "queue.Queue[dict[str, object]]",
    job_config: dict[str, object],
    step_number: int,
    total_steps: int,
) -> None:
    """Envieu un esdeveniment de progrés de referència a la cua de temps d'execució de la pàgina."""
    event_queue.put(
        {
            "type": "progress",
            "step_number": int(step_number or 0),
            "total_steps": int(total_steps or job_config["steps_target"]),
            "status": f"Passos: {int(step_number or 0)}/{int(total_steps or job_config['steps_target'])}",
        }
    )


def baseline_worker(
    job_config: dict[str, object],
    event_queue: "queue.Queue[dict[str, object]]",
    stop_event: threading.Event,
) -> None:
    """Executa la simulació baseline en segon pla."""
    try:
        result = run_baseline_simulation(
            env_id=str(job_config["env_id"]),
            steps_target=int(job_config["steps_target"]),
            seed=int(job_config["seed"]) if job_config.get("seed") is not None else None,
            should_stop=stop_event.is_set,
            on_progress=partial(push_baseline_progress_event, event_queue, job_config),
        )
        event_queue.put({"type": "result", "result": result})
    except Exception as exc:
        event_queue.put(
            {
                "type": "error",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        event_queue.put({"type": "finished"})


def start_baseline_run(request: dict[str, object]) -> dict[str, object]:
    """Inicia l'execució de la línia de base."""
    runtime = reset_baseline_runtime()
    response: dict[str, object] = {
        "started": False,
        "errors": [],
        "runtime": runtime,
    }

    if runtime.get("running"):
        response["errors"].append("Ja hi ha una simulacio en curs.")
        return response

    env_id = str(request.get("env_id") or "").strip()
    if not env_id:
        response["errors"].append("Selecciona un entorn valid abans d'iniciar la simulacio.")
        return response

    if env_id not in list_environment_ids():
        response["errors"].append("L'entorn seleccionat no esta registrat a Sinergym.")
        return response

    event_queue: "queue.Queue[dict[str, object]]" = queue.Queue()
    stop_event = threading.Event()
    job_config = {
        "env_id": env_id,
        "steps_target": int(request.get("steps_target") or ONE_YEAR_STEPS),
        "seed": int(request.get("seed")) if request.get("seed") is not None else None,
    }
    worker_thread = threading.Thread(
        target=baseline_worker,
        args=(job_config, event_queue, stop_event),
        daemon=True,
    )

    runtime.update(
        {
            "running": True,
            "completed": False,
            "cancel_requested": False,
            "needs_full_rerun": False,
            "thread": worker_thread,
            "queue": event_queue,
            "stop_event": stop_event,
            "result": None,
            "error": None,
            "traceback": None,
            "env_id": env_id,
            "steps_target": int(job_config["steps_target"]),
            "latest_step": 0,
            "status": "Inicialitzant simulacio baseline...",
            "started_at": time.time(),
            "stopped_at": None,
            "frozen_elapsed_seconds": None,
        }
    )
    worker_thread.start()

    response["started"] = True
    response["runtime"] = runtime
    return response


def render_environment_summary(env_id: str) -> None:
    """Mostra el resum de l'entorn a la UI de Streamlit."""
    summary = describe_environment(env_id)
    step_text = f"{summary.step_minutes:g} min" if summary.step_minutes else "No disponible"

    # Metriques resum entorn
    info_cols = st.columns(4)
    with info_cols[0]:
        # Metrica variables observades
        st.metric("Variables observades", summary.variables_count)
    with info_cols[1]:
        # Metrica meters
        st.metric("Meters", summary.meters_count)
    with info_cols[2]:
        # Metrica actuadors RL
        st.metric("Actuadors RL", summary.actuators_count)
    with info_cols[3]:
        # Metrica pas simulacio
        st.metric("Pas de simulacio", step_text)

    # Etiquetes fitxers baseline
    st.markdown(
        (
            '<div class="baseline-chip-row">'
            f'<span class="baseline-chip"><strong>Building</strong> {escape(summary.building_file or "No disponible")}</span>'
            f'<span class="baseline-chip"><strong>Weathers</strong> {summary.weather_count}</span>'
            f'<span class="baseline-chip"><strong>Mode</strong> schedules EnergyPlus</span>'
            f'<span class="baseline-chip"><strong>Resolucio</strong> pas fix de {step_text}</span>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_completed_baseline(runtime: dict[str, object]) -> None:
    """Mostra la secció de referència completada a la UI de Streamlit."""
    result = runtime.get("result")
    if result is None or runtime.get("running"):
        return

    if bool(getattr(result, "cancelled", False)):
        # Avís baseline cancel·lat
        st.warning(
            f"Simulacio aturada manualment despres de {float(getattr(result, 'elapsed_seconds', 0.0)):.2f} s "
            f"i {int(getattr(result, 'completed_steps', 0) or 0)} passos."
        )
    else:
        # Missatge baseline finalitzat
        st.success(
            f"Simulacio finalitzada en {float(getattr(result, 'elapsed_seconds', 0.0)):.2f} s "
            f"i {int(getattr(result, 'completed_steps', 0) or 0)} passos."
        )

    run_path = getattr(result, "run_path", "")
    if run_path:
        # Text ruta baseline
        st.caption(f"Run guardada a: {run_path}")
    # Enllaç resultats baseline
    st.page_link("pages/Resultats.py", label="Veure resultats a Resultats", icon=":material/insights:")


def render_baseline_runtime(runtime: dict[str, object]) -> None:
    """Mostra la secció de temps d'execució de la línia de base a la UI de Streamlit."""
    render_section_card(
        "Estat de la simulacio",
        "Segueix el progres del baseline i obre les visualitzacions quan la run estigui llesta.",
        title_class="section-title",
        card_class="section-card",
    )
    render_runtime_progress(runtime, progress_label="Progres", freeze_from_result=True)

    if runtime.get("cancel_requested") and runtime.get("running"):
        # Avís aturada baseline
        st.warning("S'ha demanat l'aturada. La simulacio es tancara al proper punt segur.")

    if runtime.get("error"):
        # Error runtime baseline
        st.error(str(runtime.get("error")))
        if runtime.get("traceback"):
            # Acordio traceback baseline
            with st.expander("Traceback intern", expanded=False):
                st.code(str(runtime.get("traceback")), language="text")
        return

    render_completed_baseline(runtime)


def render_baseline_runtime_frame() -> None:
    """Mostra el marc de runtime del baseline a la UI de Streamlit."""
    runtime = sync_baseline_runtime()
    if runtime.get("running") or runtime.get("completed") or runtime.get("error") or runtime.get("result"):
        st.divider()
        render_baseline_runtime(runtime)

    if consume_baseline_rerun_flag(runtime):
        st.rerun()


render_baseline_runtime_fragment = st.fragment(run_every="1s")(render_baseline_runtime_frame)


configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
inject_baseline_styles()

environment_ids = list_environment_ids()
if not environment_ids:
    # Error sense entorns baseline
    st.error("No hi ha entorns Sinergym registrats disponibles per executar un baseline.")
    st.stop()

st.session_state.setdefault(_key("selected_env"), environment_ids[0])
st.session_state.setdefault(_key("steps"), ONE_YEAR_STEPS)
st.session_state.setdefault(_key("seed"), 0)

render_hero("results-hero", "Simulacio baseline", PAGE_TITLE, INTRODUCTION_TEXT)

runtime = sync_baseline_runtime()
controls_disabled = bool(runtime.get("running"))

# Separador baseline
st.markdown("<div class='studio-spacer-115'></div>", unsafe_allow_html=True)
# Titol configuracio baseline
st.markdown('<h2 class="section-title">Configuracio del baseline</h2>', unsafe_allow_html=True)

# Selector entorn baseline
selected_env = st.selectbox(
    "Entorn Sinergym",
    options=environment_ids,
    index=environment_ids.index(st.session_state[_key("selected_env")]) if st.session_state[_key("selected_env")] in environment_ids else 0,
    disabled=controls_disabled,
)
st.session_state[_key("selected_env")] = selected_env

render_environment_summary(selected_env)

# Inputs configuracio baseline
config_cols = st.columns(2, gap="medium")
with config_cols[0]:
    # Input limit passos
    steps_limit = st.number_input(
        "Limit de passos",
        min_value=1,
        max_value=5_000_000,
        value=int(st.session_state[_key("steps")]),
        step=35040,
        disabled=controls_disabled,
    )
with config_cols[1]:
    # Input seed baseline
    seed_value = st.number_input(
        "Seed inicial",
        min_value=0,
        max_value=999_999,
        value=int(st.session_state[_key("seed")]),
        step=1,
        disabled=controls_disabled,
    )

# Nota recomanacio passos
st.markdown(
    f'<div class="baseline-inline-note">Recomanacio: usa {ONE_YEAR_STEPS} passos per generar una passada anual comparable amb una run d\'agent.</div>',
    unsafe_allow_html=True,
)

st.divider()
# Titol control baseline
st.markdown('<h2 class="section-title">Control</h2>', unsafe_allow_html=True)

# Botons control baseline
run_cols = st.columns(2, gap="medium")
with run_cols[0]:
    # Botó iniciar baseline
    start_requested = st.button(
        "Iniciar simulacio baseline",
        type="primary",
        width="stretch",
        disabled=controls_disabled,
    )
with run_cols[1]:
    # Botó cancel·lar baseline
    cancel_requested = st.button(
        "Cancelar",
        width="stretch",
        disabled=not bool(runtime.get("running")),
    )

if cancel_requested and request_baseline_stop(runtime):
    st.rerun()

if start_requested:
    start_result = start_baseline_run(
        {
            "env_id": selected_env,
            "steps_target": int(steps_limit),
            "seed": int(seed_value),
        }
    )
    for error in start_result.get("errors") or []:
        # Error inici baseline
        st.error(str(error))
    if start_result.get("started"):
        st.rerun()

render_baseline_runtime_fragment()
