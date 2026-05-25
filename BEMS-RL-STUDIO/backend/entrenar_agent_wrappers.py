"""Configuració i aplicació de wrapper per a entorns d'entrenament."""

from __future__ import annotations

import csv
from typing import Any, Dict, List, Sequence

import numpy as np
from gymnasium import Wrapper
from gymnasium.spaces import Box

from backend.entrenar_agent_constants import FIXED_WRAPPER_ROWS
from backend.common import format_ui_value


class EnergyCostFileLogger(Wrapper):
    """Logger addicional (opcional) que escriu cost per pas en un CSV independent."""

    def __init__(self, env, filename="energy_cost_log.csv"):
        """Inicialitza la instància."""
        super().__init__(env)
        self.csvfile = open(filename, mode="w", newline="")
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(["step", "elèctricity_cost_eur_per_kwh", "energy_cost_eur"])
        self.step_count = 0

    def step(self, action):
        """Step."""
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.step_count += 1
        cost_per_kwh = info.get("elèctricity_cost", 0.0)
        energy_rate = info.get("HVAC_elèctricity_demand_rate", 0.0)
        cost_total = cost_per_kwh * energy_rate
        self.writer.writerow([self.step_count, cost_per_kwh, cost_total])
        return obs, reward, terminated, truncated, info

    def reset(self, **kwargs):
        """Restableix."""
        self.step_count = 0
        return self.env.reset(**kwargs)

    def close(self):
        """Close."""
        self.csvfile.close()
        if hasattr(self.env, "close"):
            self.env.close()


def wrapper_details(params: Dict[str, Any]) -> str:
    """Detalls del wrapper."""
    if not params:
        return "-"
    return "; ".join(f"{key}={format_ui_value(value)}" for key, value in params.items())


def build_wrapper_summary_rows(wrapper_configs: Sequence[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Prepara les files de resum dels wrappers seleccionats."""
    rows = [dict(row) for row in FIXED_WRAPPER_ROWS]
    for config in wrapper_configs:
        rows.append(
            {
                "Wrapper": config["name"],
                "Actiu": "Si",
                "Detall": wrapper_details(config.get("params", {})),
            }
        )
    return rows


def apply_training_wrappers(env: Any, wrapper_configs: Sequence[Dict[str, Any]]) -> Any:
    """Aplica wrappers d'entrenament."""
    # L'ordre ve guardat a la configuració i s'ha de respectar igual en training,
    # avaluació i interacció. Si es canvia, canvia també l'espai d'observació/acció.
    for wrapper_config in wrapper_configs:
        name = wrapper_config["name"]
        params = _normalize_wrapper_params(name, wrapper_config.get("params", {}))
        if name == "NormalizeAction":
            # NormalizeAction només té sentit en espais continus; així evitem embolicar
            # un Discrete per accident quan es reutilitza una configuració antiga.
            if isinstance(env.action_space, Box):
                from sinergym.utils.wrappers import NormalizeAction

                env = NormalizeAction(env, **params)
            continue
        from sinergym.utils.common import apply_wrappers_info

        env = apply_wrappers_info(env, {_wrapper_import_path(name): params})
    return env


def _normalize_wrapper_params(name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Converteix paràmetres serialitzats per la UI al format que espera Sinergym."""
    normalized = dict(params or {})
    if name == "VariabilityContextWrapper" and "context_space" not in normalized:
        normalized["context_space"] = Box(
            low=np.array(normalized.pop("context_low"), dtype=np.float32),
            high=np.array(normalized.pop("context_high"), dtype=np.float32),
            dtype=np.float32,
        )
        normalized["step_frequency_range"] = tuple(normalized["step_frequency_range"])
    return normalized


def _wrapper_import_path(name: str) -> str:
    """Retorna la ruta importable que consumeix ``sinergym.utils.common.apply_wrappers_info``."""
    if name == "EnergyCostFileLogger":
        return "backend.entrenar_agent_wrappers:EnergyCostFileLogger"
    return f"sinergym.utils.wrappers:{name}"


def build_energy_cost_wrapper_reward_kwargs(
    options: Dict[str, Any],
    temp_vars: Sequence[str],
    energy_vars: Sequence[str],
) -> Dict[str, Any]:
    """Munta els kwargs del wrapper de costos energètics."""
    return {
        "temperature_variables": list(temp_vars),
        "energy_variables": list(energy_vars),
        "energy_cost_variables": ["energy_cost"],
        "range_comfort_winter": tuple(options["range_winter"]),
        "range_comfort_summer": tuple(options["range_summer"]),
        "energy_weight": options["energy_weight"],
        "temperature_weight": options["temperature_weight"],
        "lambda_energy": options["lambda_energy"],
        "lambda_temperature": options["lambda_temperature"],
        "lambda_energy_cost": options["lambda_energy_cost"],
    }


def build_wrapper_configs(
    options: Dict[str, Any],
    energy_cost_reward_kwargs: Dict[str, Any] | None = None,
    recalculate_energy_cost_reward: bool = True,
) -> List[Dict[str, Any]]:
    """Munta la configuració dels wrappers d'entrenament."""
    # Aquesta llista és el contracte que després es desa amb el model. Per això guardem
    # noms i paràmetres simples, fàcils de reconstruir en avaluació.
    wrapper_configs: List[Dict[str, Any]] = []
    if options["enable_previous_wrapper"]:
        wrapper_configs.append(
            {
                "name": "PreviousObservationWrapper",
                "params": {"previous_variables": options["previous_variables"]},
            }
        )
    if options["enable_datetime_wrapper"]:
        wrapper_configs.append({"name": "DatetimeWrapper", "params": {}})
    if options["enable_weather_forecast_wrapper"]:
        wrapper_configs.append(
            {
                "name": "WeatherForecastingWrapper",
                "params": {
                    "n": options["weather_forecast_n"],
                    "delta": options["weather_forecast_delta"],
                    "columns": options["weather_forecast_columns"],
                },
            }
        )
    if options["use_energy_cost"]:
        energy_cost_params = {
            "energy_cost_data_path": options["energy_cost_path"],
            "recalculate_reward": recalculate_energy_cost_reward,
        }
        if energy_cost_reward_kwargs is not None:
            energy_cost_params["reward_kwargs"] = energy_cost_reward_kwargs
        wrapper_configs.append(
            {
                "name": "EnergyCostWrapper",
                "params": energy_cost_params,
            }
        )
    if options["enable_delta_temp_wrapper"]:
        wrapper_configs.append(
            {
                "name": "DeltaTempWrapper",
                "params": {
                    "temperature_variables": options["delta_temp_variables"],
                    "setpoint_variables": options["delta_setpoint_variables"],
                },
            }
        )
    if options["enable_reduce_obs_wrapper"]:
        wrapper_configs.append(
            {
                "name": "ReduceObservationWrapper",
                "params": {"obs_reduction": options["reduced_observations"]},
            }
        )
    if options["enable_multi_obs_wrapper"]:
        wrapper_configs.append(
            {
                "name": "MultiObsWrapper",
                "params": {"n": options["multi_obs_n"], "flatten": options["multi_obs_flatten"]},
            }
        )
    if options["enable_normalize_obs_wrapper"]:
        wrapper_configs.append(
            {
                "name": "NormalizeObservation",
                "params": {
                    "automatic_update": options["normalize_obs_auto"],
                    "epsilon": options["normalize_obs_epsilon"],
                    "mean": options["normalize_obs_mean"] or None,
                    "var": options["normalize_obs_var"] or None,
                },
            }
        )
    if options.get("enable_variability_context_wrapper"):
        # Els límits del context es guarden com a llistes perquè siguin serialitzables.
        # El Box es reconstrueix quan s'apliquen els wrappers.
        wrapper_configs.append(
            {
                "name": "VariabilityContextWrapper",
                "params": {
                    "context_low": list(options.get("variability_context_low") or []),
                    "context_high": list(options.get("variability_context_high") or []),
                    "delta_value": options.get("variability_delta_value", 1.0),
                    "step_frequency_range": (
                        options.get("variability_step_frequency_min", 96),
                        options.get("variability_step_frequency_max", 96 * 7),
                    ),
                },
            }
        )
    if options["enable_incremental_wrapper"]:
        wrapper_configs.append(
            {
                "name": "IncrementalWrapper",
                "params": {
                    "incremental_variables_definition": options["incremental_definition"],
                    "initial_values": options["incremental_initial_values"],
                },
            }
        )
    if options["enable_discrete_incremental_wrapper"]:
        wrapper_configs.append(
            {
                "name": "DiscreteIncrementalWrapper",
                "params": {
                    "initial_values": options["discrete_incremental_initial_values"],
                    "delta_temp": options["discrete_incremental_delta"],
                    "step_temp": options["discrete_incremental_step"],
                },
            }
        )
    if (
        options["enable_normalize_action"]
        and options.get("is_continuous", True)
        and not options["enable_incremental_wrapper"]
        and not options["enable_discrete_incremental_wrapper"]
    ):
        # Els wrappers incrementals ja redefineixen l'escala de l'acció; combinar-los amb
        # NormalizeAction fa que l'agent aprengui en una escala difícil d'interpretar.
        wrapper_configs.append(
            {
                "name": "NormalizeAction",
                "params": {"normalize_range": (-1.0, 1.0)},
            }
        )
    if options.get("enable_storage_smoothing_wrapper"):
        wrapper_configs.append(
            {
                "name": "OfficeGridStorageSmoothingActionConstraintsWrapper",
                "params": {},
            }
        )
    if options["use_file_logger"]:
        wrapper_configs.append(
            {
                "name": "EnergyCostFileLogger",
                "params": {"filename": options["file_logger_name"]},
            }
        )
    return wrapper_configs
