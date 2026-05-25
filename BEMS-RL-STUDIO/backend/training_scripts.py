"""Scripts d'ajuda reproduïbles per a execucions BEMS-RL desades."""

from __future__ import annotations

from pprint import pformat
from typing import Any, Dict


def build_training_eval_script(training_config: Dict[str, Any]) -> str:
    """Crea un script breu d'avaluació al costat de la sessió d'entrenament."""
    lines = [
        "# Script d'avaluacio autogenerat (no s'executa automaticament)",
        "# Entorn i recompensa amb la mateixa configuracio que l'entrenament.",
        "",
        f"env_id = {training_config['env_id']!r}",
        f"meters = {pformat(training_config.get('meters', {}), sort_dicts=False)}",
        f"reward_name = {training_config['reward_name']!r}",
        f"reward_kwargs = {pformat(training_config['reward_kwargs'], sort_dicts=False)}",
        f"wrapper_configs = {pformat(training_config.get('wrapper_configs', []), sort_dicts=False)}",
        "",
    ]
    return "\n".join(lines)


def build_training_repro_script(
    artifact_name: str,
    training_config: Dict[str, Any],
) -> str:
    """Crea un script autònom que pugui reproduir una configuració d'entrenament desada."""
    config_literal = pformat(training_config, sort_dicts=False, width=100)
    # Retornem el fitxer complet com a string perquè l'artefacte guardat sigui executable
    # fora de Streamlit, amb la mateixa configuració que s'ha fet servir a la UI.
    return f'''"""Script d'entrenament reproduible autogenerat per BEMS-RL-STUDIO."""

import csv
from pathlib import Path

import gymnasium as gym
import numpy as np
from gymnasium import Wrapper
from gymnasium.spaces import Box
from stable_baselines3 import A2C, DDPG, DQN, PPO, SAC, TD3
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
import sinergym.utils.rewards as reward_module
import sinergym.utils.wrappers as wrapper_module


TRAINING_NAME = {artifact_name!r}
TRAINING_CONFIG = {config_literal}
ALGOS = {{"PPO": PPO, "A2C": A2C, "DQN": DQN, "SAC": SAC, "TD3": TD3, "DDPG": DDPG}}
DETAILED_HVAC_METERS = {{
    "natural_gas_hvac": "NaturalGas:HVAC",
    "heating_electricity": "Heating:Electricity",
    "cooling_electricity": "Cooling:Electricity",
    "fans_electricity": "Fans:Electricity",
    "pumps_electricity": "Pumps:Electricity",
    "heat_rejection_electricity": "HeatRejection:Electricity",
    "humidifier_electricity": "Humidifier:Electricity",
    "heat_recovery_electricity": "HeatRecovery:Electricity",
}}
JOULES_PER_KWH = 3_600_000.0


class EnergyCostFileLogger(Wrapper):
    def __init__(self, env, filename="energy_cost_log.csv"):
        super().__init__(env)
        self.csvfile = open(filename, mode="w", newline="")
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(["step", "electricity_cost_eur_per_kwh", "energy_cost_eur"])
        self.step_count = 0

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.step_count += 1
        cost_per_kwh = info.get("electricity_cost", 0.0)
        energy_rate = info.get("HVAC_electricity_demand_rate", 0.0)
        self.writer.writerow([self.step_count, cost_per_kwh, cost_per_kwh * energy_rate])
        return obs, reward, terminated, truncated, info

    def reset(self, **kwargs):
        self.step_count = 0
        return self.env.reset(**kwargs)

    def close(self):
        self.csvfile.close()
        if hasattr(self.env, "close"):
            self.env.close()


def get_reward_class(name):
    reward_cls = getattr(reward_module, name, None)
    if reward_cls is None:
        raise ImportError(
            f"La reward '{{name}}' no existeix a sinergym.utils.rewards en aquesta instal-lacio."
        )
    return reward_cls


def get_wrapper_class(name):
    if name == "EnergyCostFileLogger":
        return EnergyCostFileLogger
    wrapper_cls = getattr(wrapper_module, name, None)
    if wrapper_cls is None:
        raise ImportError(
            f"El wrapper '{{name}}' no existeix a sinergym.utils.wrappers en aquesta instal-lacio."
        )
    return wrapper_cls


def apply_training_wrappers(env, wrapper_configs):
    for wrapper_config in wrapper_configs:
        name = wrapper_config["name"]
        params = wrapper_config.get("params", {{}})
        wrapper_cls = get_wrapper_class(name)
        if name == "PreviousObservationWrapper":
            env = wrapper_cls(env, **params)
        elif name == "DatetimeWrapper":
            env = wrapper_cls(env)
        elif name == "WeatherForecastingWrapper":
            env = wrapper_cls(env, **params)
        elif name == "EnergyCostWrapper":
            env = wrapper_cls(env, **params)
        elif name == "DeltaTempWrapper":
            env = wrapper_cls(env, **params)
        elif name == "ReduceObservationWrapper":
            env = wrapper_cls(env, **params)
        elif name == "MultiObsWrapper":
            env = wrapper_cls(env, **params)
        elif name == "NormalizeObservation":
            env = wrapper_cls(env, **params)
        elif name == "VariabilityContextWrapper":
            context_space = Box(
                low=np.array(params["context_low"], dtype=np.float32),
                high=np.array(params["context_high"], dtype=np.float32),
                dtype=np.float32,
            )
            env = wrapper_cls(
                env,
                context_space=context_space,
                delta_value=params["delta_value"],
                step_frequency_range=tuple(params["step_frequency_range"]),
            )
        elif name == "OfficeGridStorageSmoothingActionConstraintsWrapper":
            env = wrapper_cls(env)
        elif name == "IncrementalWrapper":
            env = wrapper_cls(env, **params)
        elif name == "DiscreteIncrementalWrapper":
            env = wrapper_cls(env, **params)
        elif name == "NormalizeAction" and isinstance(env.action_space, Box):
            env = wrapper_cls(env, **params)
        elif name == "EnergyCostFileLogger":
            env = wrapper_cls(env, **params)
    return env


def with_detailed_hvac_meters(meters):
    return dict(meters or {{}})


def get_training_meters():
    configured_meters = TRAINING_CONFIG.get("meters")
    if configured_meters is not None:
        return with_detailed_hvac_meters(configured_meters)

    try:
        spec = gym.spec(TRAINING_CONFIG["env_id"])
        meters = (spec.kwargs or {{}}).get("meters", {{}}) or {{}}
    except Exception:
        meters = {{}}
    return with_detailed_hvac_meters(meters)


def make_env():
    reward_cls = get_reward_class(TRAINING_CONFIG["reward_name"])
    meters = get_training_meters()
    env = gym.make(
        TRAINING_CONFIG["env_id"],
        meters=meters,
        reward=reward_cls,
        reward_kwargs=TRAINING_CONFIG["reward_kwargs"],
    )
    env = apply_training_wrappers(env, TRAINING_CONFIG.get("wrapper_configs", []))
    env = get_wrapper_class("LoggerWrapper")(env)
    env = get_wrapper_class("CSVLogger")(env)
    return env


def get_workspace_path(vec):
    try:
        paths = vec.get_attr("workspace_path")
        if paths and paths[0]:
            return str(paths[0])
    except Exception:
        pass
    return None


def append_detailed_meter_kwh_columns(observations_path):
    observations_file = Path(observations_path) if observations_path else None
    if observations_file is None or not observations_file.is_file():
        return

    with open(observations_file, "r", newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames or not rows:
        return

    source_columns = {{}}
    for alias, meter_name in DETAILED_HVAC_METERS.items():
        target_column = alias + "_kwh"
        if target_column in fieldnames:
            continue
        if alias in fieldnames:
            source_columns[alias] = alias
        elif meter_name in fieldnames:
            source_columns[alias] = meter_name

    if not source_columns:
        return

    derived_columns = {{source_alias: source_alias + "_kwh" for source_alias in source_columns}}
    for row in rows:
        for source_alias, source_column in source_columns.items():
            target_column = derived_columns[source_alias]
            try:
                row[target_column] = str(float(row.get(source_column, "")) / JOULES_PER_KWH)
            except (TypeError, ValueError):
                row[target_column] = ""

    output_fields = fieldnames + list(derived_columns.values())
    with open(observations_file, "w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)


def append_detailed_meter_kwh_columns_in_workspace(workspace_path):
    if not workspace_path:
        return

    workspace = Path(workspace_path)
    if not workspace.is_dir():
        return

    for observations_file in workspace.rglob("observations.csv"):
        try:
            append_detailed_meter_kwh_columns(observations_file)
        except Exception:
            continue


def main() -> None:
    artifact_dir = Path(__file__).resolve().parent
    vec = make_vec_env(make_env, n_envs=1)
    vec = VecNormalize(vec, norm_obs=True, norm_reward=True)
    workspace_path = None

    try:
        algo_cls = ALGOS[TRAINING_CONFIG["algo_name"]]
        algo_kwargs = dict(TRAINING_CONFIG.get("algo_kwargs") or {{}})
        algo_kwargs.setdefault("learning_rate", TRAINING_CONFIG["learning_rate"])
        if TRAINING_CONFIG["algo_name"] in {{"PPO", "A2C"}} and TRAINING_CONFIG.get("n_steps") is not None:
            algo_kwargs.setdefault("n_steps", TRAINING_CONFIG["n_steps"])
        algo_kwargs["verbose"] = 1

        model = algo_cls(TRAINING_CONFIG["policy_name"], vec, **algo_kwargs)
        model.learn(total_timesteps=TRAINING_CONFIG["timesteps_per_year"])
        model.save(str(artifact_dir / f"{{TRAINING_NAME}}.zip"))
        vec.save(str(artifact_dir / f"{{TRAINING_NAME}}_vecnorm.pkl"))
        workspace_path = get_workspace_path(vec)
    finally:
        if workspace_path is None:
            workspace_path = get_workspace_path(vec)
        vec.close()
        append_detailed_meter_kwh_columns_in_workspace(workspace_path)


if __name__ == "__main__":
    main()
'''
