"""Cicle de vida d'execució per a sessions d'entrenament en directe."""

from __future__ import annotations

import copy
import json
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Dict, Sequence

import gymnasium as gym
import streamlit as st
from sinergym.utils.wrappers import CSVLogger, LoggerWrapper

from backend.entrenar_agent_artifacts import (
    append_detailed_meter_kwh_columns_in_workspace,
    build_training_artifact_paths,
    get_runtime_workspace_path,
)
from backend.entrenar_agent_constants import REWARD_CLASSES, TRAINING_RUNTIME_KEY
from backend.entrenar_agent_env import get_training_meters_for_env, with_detailed_hvac_meters
from backend.entrenar_agent_wrappers import apply_training_wrappers
from backend.sb3_utils import ALGOS, build_vecnormalize_env
from backend.training_scripts import build_training_eval_script, build_training_repro_script


def clear_training_runtime() -> None:
    """Neteja el temps d'execució de l'entrenament."""
    runtime = st.session_state.pop(TRAINING_RUNTIME_KEY, None)
    if not runtime:
        return

    workspace_path = get_runtime_workspace_path(runtime)
    vec = runtime.get("vec")
    if vec is not None:
        try:
            vec.envs[0].close()
        except Exception:
            try:
                vec.close()
            except Exception:
                pass

    append_detailed_meter_kwh_columns_in_workspace(workspace_path)


def learn_training_chunk(model: Any, timesteps: int) -> None:
    """Executa un bloc d'entrenament amb la inicialització incremental pròpia de SB3."""
    model.learn(total_timesteps=int(timesteps), reset_num_timesteps=False)


def save_training_artifacts(runtime: Dict[str, Any]) -> Dict[str, Any]:
    """Deseu els artefactes d'entrenament."""
    config = runtime["config"]
    artifact_dir = Path(runtime["artifact_dir"])
    artifact_dir.mkdir(parents=True, exist_ok=False)

    runtime["model"].save(str(runtime["save_path"]))
    runtime["vec"].save(str(runtime["vecnorm_path"]))

    result = {
        "artifact_name": runtime["artifact_name"],
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "artifact_dir": str(artifact_dir),
        "env_id": config["env_id"],
        "reward_name": config["reward_name"],
        "algo_name": config["algo_name"],
        "policy_name": config["policy_name"],
        "files": {
            "training_script": Path(runtime["training_script_path"]).name,
            "eval_script": Path(runtime["eval_script_path"]).name,
            "model": Path(runtime["save_path"]).name,
            "vecnorm": Path(runtime["vecnorm_path"]).name,
            "config": Path(runtime["config_path"]).name,
        },
        "ui_state": runtime.get("ui_state", {}),
        "training_config": config,
    }

    with open(runtime["config_path"], "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)

    with open(runtime["eval_script_path"], "w", encoding="utf-8") as handle:
        handle.write(build_training_eval_script(config))

    with open(runtime["training_script_path"], "w", encoding="utf-8") as handle:
        handle.write(build_training_repro_script(runtime["artifact_name"], config))

    return result


def build_training_env_instance(
    env_id: str,
    reward_name: str,
    reward_kwargs: Dict[str, Any],
    meters: Dict[str, str],
    wrapper_configs: Sequence[Dict[str, Any]],
) -> Any:
    """Crea una instància d'entorn embolicat per a l'entrenament en directe."""
    reward_cls = REWARD_CLASSES[reward_name]
    env = gym.make(env_id, meters=meters, reward=reward_cls, reward_kwargs=reward_kwargs)
    env = apply_training_wrappers(env, wrapper_configs)
    env = LoggerWrapper(env)
    env = CSVLogger(env)
    return env


def create_training_runtime(
    training_config: Dict[str, Any],
    ui_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Crea temps d'execució de la entrenament."""
    env_id = training_config["env_id"]
    reward_name = training_config["reward_name"]
    reward_kwargs = training_config["reward_kwargs"]
    meters = with_detailed_hvac_meters(training_config.get("meters") or get_training_meters_for_env(env_id))
    wrapper_configs = training_config["wrapper_configs"]
    algo_name = training_config["algo_name"]
    policy_name = training_config["policy_name"]
    learning_rate = training_config["learning_rate"]
    n_steps = training_config["n_steps"]
    timesteps_per_year = training_config["timesteps_per_year"]

    env_factory = partial(
        build_training_env_instance,
        env_id,
        reward_name,
        reward_kwargs,
        meters,
        wrapper_configs,
    )
    vec = build_vecnormalize_env(env_factory)

    model_cls = ALGOS[algo_name]
    algo_kwargs = dict(training_config.get("algo_kwargs") or {})
    algo_kwargs.setdefault("learning_rate", learning_rate)
    if algo_name in ["PPO", "A2C"] and n_steps is not None:
        algo_kwargs.setdefault("n_steps", n_steps)
    algo_kwargs["verbose"] = 0

    model = model_cls(policy_name, vec, **algo_kwargs)
    artifact_paths = build_training_artifact_paths(training_config)

    return {
        "model": model,
        "vec": vec,
        "config": training_config,
        "ui_state": copy.deepcopy(ui_state or {}),
        "artifact_name": artifact_paths["artifact_name"],
        "artifact_dir": artifact_paths["artifact_dir"],
        "save_path": artifact_paths["model_path"],
        "vecnorm_path": artifact_paths["vecnorm_path"],
        "eval_script_path": artifact_paths["eval_script_path"],
        "training_script_path": artifact_paths["training_script_path"],
        "config_path": artifact_paths["config_path"],
        "chunk_timesteps": int(algo_kwargs.get("n_steps") or n_steps) if algo_name in ["PPO", "A2C"] else min(512, timesteps_per_year),
    }
