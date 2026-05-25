"""Temps d'execució d'avaluació asíncrona per a agents Studio entrenats.

L'avaluació es pot executar per a molts passos de simulació, de manera que aquest backend aïlla el
bucle d'execució, cua de progrés i estat de cancel·lació des de la pàgina Streamlit. Això
també centralitza la càrrega de models, la creació d'entorns i la validació de l'espai d'acció
de manera que el control i l'avaluació en directe segueixen el mateix contracte.
"""

from __future__ import annotations

import queue
import threading
import time
import traceback
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
import streamlit as st
from stable_baselines3.common.vec_env import VecEnvWrapper

import sinergym  # noqa: F401
from sinergym.utils.wrappers import CSVLogger, LoggerWrapper, NormalizeAction

from backend.model_metadata import (
    build_gym_kwargs_from_metadata,
    load_model_metadata,
    validate_action_spaces,
)
from backend.common import ONE_YEAR_STEPS
from backend.sb3_utils import (
    candidate_vecnorm,
    build_monitored_vec_env,
    env_id_from_meta_or_name,
    format_action_for_env,
    load_sb3_model_bytes,
    load_vecnormalize,
    scan_model_zips,
    should_apply_normalize_action,
)


EVALUATION_RUNTIME_STATE_KEY = "evaluation_runtime_state"


@dataclass(frozen=True)
class EvaluationResult:
    """Resum de resultats d'una execució d'un treballador d'avaluació."""
    elapsed_seconds: float
    cancelled: bool
    warnings: Tuple[str, ...] = ()


def push_evaluation_progress(
    event_queue: "queue.Queue[Dict[str, Any]]",
    job_config: Dict[str, Any],
    step_number: int,
    total_steps: int,
) -> None:
    """Envieu un esdeveniment de progrés d'avaluació a la cua d'execució."""
    push_evaluation_event(
        event_queue,
        {
            "type": "progress",
            "step_number": int(step_number or 0),
            "total_steps": int(total_steps or job_config["steps_target"]),
            "status": f"Passos: {int(step_number or 0)}/{int(total_steps or job_config['steps_target'])}",
        },
    )


def build_evaluation_env(
    env_id: str,
    gym_kwargs: Dict[str, Any],
    model_action_space: Any,
    wrapper_configs: Optional[List[Dict[str, Any]]],
) -> Any:
    """Crea un entorn embolicat per a una execució d'avaluació d'agent."""
    env = make_env(env_id, seed=0, gym_kwargs=gym_kwargs)
    env = apply_evaluation_action_contract(env, model_action_space, wrapper_configs)
    env = LoggerWrapper(env)
    env = CSVLogger(env)
    return env


def empty_evaluation_runtime() -> Dict[str, Any]:
    """Temps d'execució d'avaluació buit."""
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
        "model_path": None,
        "env_id": None,
        "steps_target": 1,
        "latest_step": 0,
        "status": "",
        "started_at": None,
    }


def ensure_evaluation_runtime() -> Dict[str, Any]:
    """Assegura el temps d'execució de l'avaluació."""
    if EVALUATION_RUNTIME_STATE_KEY not in st.session_state:
        st.session_state[EVALUATION_RUNTIME_STATE_KEY] = empty_evaluation_runtime()
    return st.session_state[EVALUATION_RUNTIME_STATE_KEY]


def reset_evaluation_runtime() -> Dict[str, Any]:
    """Restableix el temps d'execució de l'avaluació."""
    runtime = ensure_evaluation_runtime()
    previous_thread = runtime.get("thread")
    if previous_thread is not None and getattr(previous_thread, "is_alive", lambda: False)():
        return runtime

    st.session_state[EVALUATION_RUNTIME_STATE_KEY] = empty_evaluation_runtime()
    return st.session_state[EVALUATION_RUNTIME_STATE_KEY]


def push_evaluation_event(event_queue: "queue.Queue[Dict[str, Any]]", payload: Dict[str, Any]) -> None:
    """Esdeveniment d'avaluació push."""
    event_queue.put(dict(payload))


def evaluation_worker(
    job_config: Dict[str, Any],
    event_queue: "queue.Queue[Dict[str, Any]]",
    stop_event: threading.Event,
) -> None:
    """Executa l'avaluació en segon pla."""
    try:
        result = run_agent_evaluation(
            model_path=job_config["model_path"],
            env_id=job_config["env_id"],
            use_vecnorm=bool(job_config["use_vecnorm"]),
            vecnorm_path=job_config["vecnorm_path"],
            steps_target=int(job_config["steps_target"]),
            deterministic=bool(job_config["deterministic"]),
            should_stop=stop_event.is_set,
            on_progress=partial(push_evaluation_progress, event_queue, job_config),
            override_wrapper_configs=job_config.get("wrapper_configs") or None,
        )
        push_evaluation_event(event_queue, {"type": "result", "result": result})
    except Exception as exc:
        push_evaluation_event(
            event_queue,
            {
                "type": "error",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    finally:
        push_evaluation_event(event_queue, {"type": "finished"})


def drain_evaluation_runtime(runtime: Dict[str, Any]) -> None:
    """Temps d'execució de l'avaluació del buidatge."""
    event_queue = runtime.get("queue")
    if event_queue is None:
        return

    # La UI consulta aquest runtime sovint; buidem la cua sencera en cada passada perquè
    # no quedin esdeveniments antics fent saltar el progrés enrere.
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
            runtime["completed"] = True
            runtime["running"] = False
            runtime["needs_full_rerun"] = True
        elif event_type == "error":
            runtime["error"] = str(event.get("error") or "Error desconegut durant l'avaluació.")
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


def sync_evaluation_runtime() -> Dict[str, Any]:
    """Sincronitza el temps d'execució de l'avaluació."""
    runtime = ensure_evaluation_runtime()
    drain_evaluation_runtime(runtime)
    return runtime


def consume_evaluation_runtime_rerun_flag(runtime: Optional[Dict[str, Any]] = None) -> bool:
    """Indicador de reexecució del clima d'execució de l'avaluació."""
    active_runtime = runtime if runtime is not None else ensure_evaluation_runtime()
    if active_runtime.get("needs_full_rerun") and not active_runtime.get("running"):
        active_runtime["needs_full_rerun"] = False
        return True
    return False


def request_evaluation_stop(runtime: Optional[Dict[str, Any]] = None) -> bool:
    """Sol·licitar l'aturada de l'avaluació."""
    active_runtime = runtime if runtime is not None else ensure_evaluation_runtime()
    if not active_runtime.get("running") or active_runtime.get("stop_event") is None:
        return False

    active_runtime["cancel_requested"] = True
    active_runtime["status"] = "Aturant avaluació..."
    active_runtime["stop_event"].set()
    return True


def start_evaluation_run(request: Dict[str, Any]) -> Dict[str, Any]:
    """Iniciar l'execució d'avaluació."""
    runtime = reset_evaluation_runtime()
    response: Dict[str, Any] = {
        "started": False,
        "errors": [],
        "runtime": runtime,
    }

    if runtime.get("running"):
        response["errors"].append("Ja hi ha una avaluació en curs.")
        return response

    model_path = Path(request.get("model_path") or "")
    env_id = str(request.get("env_id") or "").strip()
    vecnorm_path = request.get("vecnorm_path")

    if not model_path.exists():
        response["errors"].append("No s'ha trobat el model seleccionat.")
        return response
    if not env_id:
        response["errors"].append("No s'ha pogut determinar un env_id vàlid.")
        return response

    event_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()
    stop_event = threading.Event()
    job_config = {
        "model_path": model_path,
        "env_id": env_id,
        "use_vecnorm": bool(request.get("use_vecnorm")),
        "vecnorm_path": Path(vecnorm_path) if vecnorm_path else None,
        "steps_target": int(request.get("steps_target") or ONE_YEAR_STEPS),
        "deterministic": bool(request.get("deterministic", True)),
        "wrapper_configs": list(request.get("wrapper_configs") or []),
    }
    worker_thread = threading.Thread(
        target=evaluation_worker,
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
            "model_path": str(model_path),
            "env_id": env_id,
            "steps_target": int(job_config["steps_target"]),
            "latest_step": 0,
            "status": "Inicialitzant avaluació...",
            "started_at": time.time(),
        }
    )
    worker_thread.start()

    response["started"] = True
    response["runtime"] = runtime
    return response


def apply_evaluation_action_contract(
    env: gym.Env,
    model_action_space: Any,
    wrapper_configs: List[Dict[str, Any]],
) -> gym.Env:
    """Aplica contracte d'acció d'avaluació."""
    from backend.entrenar_agent_wrappers import apply_training_wrappers

    if wrapper_configs:
        return apply_training_wrappers(env, wrapper_configs)
    if should_apply_normalize_action(model_action_space, env.action_space):
        return NormalizeAction(env)
    return env


def validate_action_contract(model_action_space: Any, env_action_space: Any, metadata: Dict[str, Any]) -> None:
    """Validació del contracte d'actuació."""
    validate_action_spaces(model_action_space, env_action_space, metadata)


def make_env(env_id: str, seed: int = 0, gym_kwargs: Optional[Dict[str, Any]] = None) -> gym.Env:
    """Crea l'entorn utilitzat durant l'avaluació."""
    env = gym.make(env_id, **(gym_kwargs or {}))
    env.reset(seed=seed)
    return env


def run_agent_evaluation(
    model_path: Path,
    env_id: str,
    use_vecnorm: bool,
    vecnorm_path: Optional[Path],
    steps_target: int,
    deterministic: bool,
    should_stop: Callable[[], bool],
    on_progress: Callable[[int, int], None],
    override_wrapper_configs: Optional[List[Dict[str, Any]]] = None,
) -> EvaluationResult:
    """Executa l'avaluació i retorna el resum d'execució."""

    with open(model_path, "rb") as file_handle:
        model, _ = load_sb3_model_bytes(file_handle.read(), device="cpu")

    metadata = load_model_metadata(model_path)
    if override_wrapper_configs is not None:
        wrapper_configs = override_wrapper_configs
    else:
        wrapper_configs = metadata.get("wrapper_configs", [])
    model_action_space = getattr(model, "action_space", None)

    gym_kwargs = build_gym_kwargs_from_metadata(metadata)

    env_factory = partial(build_evaluation_env, env_id, gym_kwargs, model_action_space, wrapper_configs)

    eval_warnings: List[str] = []

    venv = None
    if use_vecnorm and vecnorm_path and vecnorm_path.exists():
        # VecNormalize s'ha d'enganxar al mateix tipus d'entorn amb què es va entrenar.
        # Si no encaixa, seguim sense normalització però deixem l'avís visible.
        try:
            venv = load_vecnormalize(str(vecnorm_path), env_factory)
        except ValueError as exc:
            eval_warnings.append(
                f"VecNormalize no aplicat: {exc} "
                "Continuant sense normalitzacio d'observacions; les prediccions poden ser menys precises."
            )
    if venv is None:
        venv = build_monitored_vec_env(env_factory)

    try:
        validate_action_contract(model_action_space, venv.action_space, metadata)
    except ValueError as exc:
        eval_warnings.append(f"Avis de contracte d'accions: {exc}")

    model_obs_shape = getattr(getattr(model, "observation_space", None), "shape", None)
    env_obs_shape = getattr(getattr(venv, "observation_space", None), "shape", None)
    if model_obs_shape and env_obs_shape and tuple(model_obs_shape) != tuple(env_obs_shape):
        # Aquest error és millor aturar-lo aquí: si les observacions no tenen la mateixa
        # forma, el model podria predir accions aparentment vàlides però sense sentit.
        model_size = int(np.prod(model_obs_shape))
        env_size = int(np.prod(env_obs_shape))
        raise ValueError(
            f"L'espai d'observacions del model ({model_size} variables, forma {model_obs_shape}) "
            f"no coincideix amb l'entorn seleccionat ({env_size} variables, forma {env_obs_shape}). "
            "Assegura't d'avaluar el model amb el mateix entorn i configuracio de wrappers amb que va ser entrenat."
        )

    cancelled = False
    start_time = time.time()
    obs = venv.reset()

    try:
        for step_number in range(steps_target):
            if should_stop():
                cancelled = True
                break

            action, _ = model.predict(obs, deterministic=deterministic)
            formatted_action = format_action_for_env(action, venv)

            next_obs, rewards, dones, infos = venv.step(formatted_action)
            obs = next_obs

            if bool(np.array(dones).reshape(-1)[0]):
                # Alguns entorns acaben episodi abans dels passos demanats; reiniciem per
                # mantenir l'avaluació viva fins al límit triat per l'usuari.
                obs = venv.reset()

            if (step_number + 1) % 200 == 0 or (step_number + 1) == steps_target:
                on_progress(step_number + 1, steps_target)
    finally:
        try:
            base = venv
            if isinstance(base, VecEnvWrapper):
                base = base.venv
            if hasattr(base, "envs") and base.envs:
                base.envs[0].close()
        except Exception:
            pass

    return EvaluationResult(
        elapsed_seconds=time.time() - start_time,
        cancelled=cancelled,
        warnings=tuple(eval_warnings),
    )
