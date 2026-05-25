"""Simulacions de referència per a execucions no controlades o basades en regles.

La pàgina de simulació utilitza aquest backend per inspeccionar entorns registrats, executar
episodis de referència, capturen el progrés i persisteixen la mateixa forma d'artefacte esperada
pel panell de resultats. Això ofereix als usuaris una prova de referència abans de comparar
agents formats.
"""

from __future__ import annotations

import csv
import glob
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import gymnasium as gym
import numpy as np
from stable_baselines3.common.monitor import Monitor

from sinergym.utils.rewards import BaseReward
from sinergym.utils.wrappers import CSVLogger, LoggerWrapper

from backend.entrenar_agent_constants import DETAILED_HVAC_METERS, JOULES_PER_KWH
from backend.entrenar_agent_env import with_detailed_hvac_meters
from backend.common import list_registered_env_ids

NO_CONTROL_ACTION = np.empty((0,), dtype=np.float32)
BASELINE_TIMESTEPS_PER_HOUR = 4
BASELINE_STEP_MINUTES = 60.0 / BASELINE_TIMESTEPS_PER_HOUR


@dataclass(frozen=True)
class EnvironmentSummary:
    """Descripció compacta d'un entorn Sinergym registrat."""
    env_id: str
    env_name: str
    building_file: str
    weather_count: int
    variables_count: int
    meters_count: int
    actuators_count: int
    reward_name: str
    step_minutes: float | None


@dataclass(frozen=True)
class BaselineSimulationResult:
    """Sortides persistents i metadades d'estat per a una simulació de referència."""
    env_id: str
    run_path: str
    progress_path: str
    observations_path: str
    elapsed_seconds: float
    completed_steps: int
    cancelled: bool


class ScheduleBaselineReward(BaseReward):
    """Reward zero que conserva les mètriques físiques per comparar contra agents entrenats."""

    def __init__(
        self,
        temperature_variables: list[str] | None = None,
        energy_variables: list[str] | None = None,
        range_comfort_winter: tuple[float, float] = (20.0, 23.5),
        range_comfort_summer: tuple[float, float] = (23.0, 26.0),
        summer_start: tuple[int, int] = (6, 1),
        summer_final: tuple[int, int] = (9, 30),
    ) -> None:
        """Inicialitza la instància."""
        super().__init__()
        self.temperature_variables = list(temperature_variables or [])
        self.energy_variables = list(energy_variables or [])
        self.range_comfort_winter = tuple(range_comfort_winter)
        self.range_comfort_summer = tuple(range_comfort_summer)
        self.summer_start = tuple(summer_start)
        self.summer_final = tuple(summer_final)

    def __call__(self, obs_dict: dict[str, float]) -> tuple[float, dict[str, float]]:
        """Executa l'objecte cridable."""
        total_power_demand = self._compute_power_demand(obs_dict)
        total_temperature_violation = self._compute_temperature_violation(obs_dict)
        reward_terms = {
            "energy_term": 0.0,
            "comfort_term": 0.0,
            "energy_penalty": -total_power_demand,
            "comfort_penalty": -total_temperature_violation,
            "total_power_demand": total_power_demand,
            "total_temperature_violation": total_temperature_violation,
            "reward_weight": 0.0,
        }
        return 0.0, reward_terms

    def _compute_power_demand(self, obs_dict: dict[str, float]) -> float:
        """Calcula la demanda de potència."""
        total = 0.0
        for variable in self.energy_variables:
            value = obs_dict.get(variable)
            if value is None:
                continue
            try:
                total += float(value)
            except (TypeError, ValueError):
                continue
        return total

    def _compute_temperature_violation(self, obs_dict: dict[str, float]) -> float:
        """Calcula la violació de temperatura."""
        month = _safe_int(obs_dict.get("month"), default=1)
        day = _safe_int(obs_dict.get("day_of_month"), default=1)
        comfort_range = (
            self.range_comfort_summer
            if _is_within_summer((month, day), self.summer_start, self.summer_final)
            else self.range_comfort_winter
        )

        violation = 0.0
        for variable in self.temperature_variables:
            value = obs_dict.get(variable)
            if value is None:
                continue
            try:
                temperature = float(value)
            except (TypeError, ValueError):
                continue
            lower, upper = comfort_range
            violation += max(lower - temperature, 0.0) + max(temperature - upper, 0.0)
        return violation


def list_environment_ids() -> list[str]:
    """Retorna els entorns Sinergym que tenen sentit per a una línia de base de planificació."""

    return list_registered_env_ids(include_discrete=False)


def describe_environment(env_id: str) -> EnvironmentSummary:
    """Crea un resum compacte utilitzat per la interfície."""

    spec = gym.spec(env_id)
    kwargs = spec.kwargs or {}
    meters = with_detailed_hvac_meters(kwargs.get("meters") or {})
    weather_files = kwargs.get("weather_files") or []
    if isinstance(weather_files, str):
        weather_count = 1
    else:
        weather_count = len(weather_files)

    reward_cls = kwargs.get("reward")
    reward_name = getattr(reward_cls, "__name__", str(reward_cls))
    return EnvironmentSummary(
        env_id=env_id,
        env_name=str(kwargs.get("env_name") or env_id),
        building_file=str(kwargs.get("building_file") or ""),
        weather_count=weather_count,
        variables_count=len(kwargs.get("variables") or {}),
        meters_count=len(meters),
        actuators_count=len(kwargs.get("actuators") or {}),
        reward_name=reward_name,
        step_minutes=BASELINE_STEP_MINUTES,
    )


def run_baseline_simulation(
    env_id: str,
    steps_target: int,
    seed: int | None,
    should_stop: Callable[[], bool],
    on_progress: Callable[[int, int], None],
) -> BaselineSimulationResult:
    """Executa una línia de base sense control utilitzant els planificacions per defecte d'EnergyPlus."""

    env = _make_baseline_env(env_id)
    workspace_path = ""
    completed_steps = 0
    cancelled = False
    start_time = time.time()

    try:
        env.reset(seed=seed)
        workspace_path = str(env.get_wrapper_attr("workspace_path"))

        for step_number in range(steps_target):
            if should_stop():
                cancelled = True
                break

            _, _, terminated, truncated, _ = env.step(NO_CONTROL_ACTION)
            completed_steps = step_number + 1

            if terminated or truncated:
                env.reset()

            if completed_steps % 200 == 0 or completed_steps == steps_target:
                on_progress(completed_steps, steps_target)
    finally:
        try:
            env.close()
        except Exception:
            pass

    progress_path, observations_path = _resolve_run_artifacts(workspace_path)
    _append_detailed_meter_kwh_columns(observations_path)
    return BaselineSimulationResult(
        env_id=env_id,
        run_path=workspace_path,
        progress_path=progress_path,
        observations_path=observations_path,
        elapsed_seconds=time.time() - start_time,
        completed_steps=completed_steps,
        cancelled=cancelled,
    )


def _make_baseline_env(env_id: str):
    """Crea l'entorn de baseline."""
    env_summary = describe_environment(env_id)
    spec = gym.spec(env_id)
    spec_kwargs = dict(spec.kwargs or {})
    baseline_reward_kwargs = _build_baseline_reward_kwargs(spec_kwargs)
    baseline_name = f"{env_summary.env_name}-baseline"
    building_config = dict(spec_kwargs.get("building_config") or {})
    building_config["timesteps_per_hour"] = BASELINE_TIMESTEPS_PER_HOUR
    meters = with_detailed_hvac_meters(spec_kwargs.get("meters") or {})
    env = gym.make(
        env_id,
        action_space=gym.spaces.Box(low=0.0, high=0.0, shape=(0,), dtype=np.float32),
        actuators={},
        building_config=building_config,
        env_name=baseline_name,
        meters=meters,
        reward=ScheduleBaselineReward,
        reward_kwargs=baseline_reward_kwargs,
    )
    env = LoggerWrapper(env)
    env = CSVLogger(env)
    env = Monitor(env)
    return env


def _resolve_run_artifacts(run_path: str) -> tuple[str, str]:
    """Retorna les sortides principals CSV de l'execució que acaba d'acabar."""

    progress_path = str(Path(run_path) / "progress.csv")
    observation_files = sorted(
        glob.glob(os.path.join(run_path, "**", "observations.csv"), recursive=True),
        key=os.path.getmtime,
        reverse=True,
    )
    observations_path = observation_files[0] if observation_files else ""
    return progress_path, observations_path


def _append_detailed_meter_kwh_columns(observations_path: str) -> None:
    """Afegeix columnes detallades del comptador de kWh."""
    if not observations_path or not os.path.exists(observations_path):
        return

    with open(observations_path, "r", newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames or not rows:
        return

    # Els meters detallats de Sinergym poden quedar en joules al CSV; afegim *_kwh una
    # sola vegada perquè el dashboard posterior no faci la conversió repetida.
    derived_columns = {
        alias: f"{alias}_kwh"
        for alias in DETAILED_HVAC_METERS
        if alias in fieldnames and f"{alias}_kwh" not in fieldnames
    }
    if not derived_columns:
        return

    for row in rows:
        for source_column, target_column in derived_columns.items():
            try:
                row[target_column] = str(float(row.get(source_column, "")) / JOULES_PER_KWH)
            except (TypeError, ValueError):
                row[target_column] = ""

    output_fields = fieldnames + list(derived_columns.values())
    with open(observations_path, "w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)


def _build_baseline_reward_kwargs(env_kwargs: dict) -> dict[str, object]:
    """Crea kwargs de recompensa de referència."""
    reward_kwargs = dict(env_kwargs.get("reward_kwargs") or {})
    variables = env_kwargs.get("variables") or {}
    meters = env_kwargs.get("meters") or {}

    # La baseline no optimitza res, però igualment necessita variables de confort i energia
    # perquè els gràfics comparatius surtin amb les mateixes mètriques que un agent.
    temperature_variables = reward_kwargs.get("temperature_variables")
    if not temperature_variables:
        temperature_variables = [
            name for name in variables.keys()
            if "air_temperature" in name.lower()
        ]

    energy_variables = reward_kwargs.get("energy_variables")
    if not energy_variables:
        energy_candidates = list(variables.keys()) + list(meters.keys())
        energy_variables = [
            name for name in energy_candidates
            if any(token in name.lower() for token in ("hvac", "electric", "power", "demand", "energy"))
        ]

    return {
        "temperature_variables": list(temperature_variables or []),
        "energy_variables": list(energy_variables or []),
        "range_comfort_winter": tuple(reward_kwargs.get("range_comfort_winter") or (20.0, 23.5)),
        "range_comfort_summer": tuple(reward_kwargs.get("range_comfort_summer") or (23.0, 26.0)),
        "summer_start": tuple(reward_kwargs.get("summer_start") or (6, 1)),
        "summer_final": tuple(reward_kwargs.get("summer_final") or (9, 30)),
    }


def _safe_int(value: object, *, default: int) -> int:
    """Safe int."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _is_within_summer(current: tuple[int, int], start: tuple[int, int], end: tuple[int, int]) -> bool:
    """Is within summer."""
    return start <= current <= end
