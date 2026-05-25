"""Descobriment d'entorns i metadades per configurar entrenaments."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Sequence

import gymnasium as gym
import yaml
from gymnasium.spaces import Box

from backend.entrenar_agent_constants import DISCRETE_ACTION_SPACES
from backend.common import CFG_DIR, list_registered_env_ids


def list_registered_envs() -> List[str]:
    """Llista d'envs registrats."""
    return list_registered_env_ids()


def list_files(directory: Path, suffixes: Sequence[str]) -> List[str]:
    """Llista de fitxers."""
    if not directory.exists():
        return []
    return sorted(
        str(path)
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes
    )


def with_detailed_hvac_meters(meters: Dict[str, str] | None) -> Dict[str, str]:
    """Retorna només comptadors configurats.

    Inventar els metres HVAC predeterminats fa que EnergyPlus retorni els identificadors API no vàlids
    per a edificis que no els exposen, omplint eplusout.err amb errors `Severe getMeterValue`
    errors getMeterValue. Els comptadors detallats encara s'utilitzen quan es generen
    la configuració de l'entorn els va detectar explícitament.
    """
    return dict(meters or {})


def get_training_meters_for_env(env_id: str) -> Dict[str, str]:
    """Retorna els mesuradors d'entrenament per a env."""
    try:
        spec = gym.spec(env_id)
        env_kwargs = spec.kwargs or {}
        meters = env_kwargs.get("meters", {}) or {}
    except Exception:
        meters = {}
    return with_detailed_hvac_meters(meters)


def _effective_action_space_from_spec(spec: gym.envs.registration.EnvSpec, fallback: Any) -> Any:
    """Espai d'acció efectiu des de les especificacions."""
    for wrapper_spec in getattr(spec, "additional_wrappers", ()) or ():
        if getattr(wrapper_spec, "name", "") != "DiscretizeEnv":
            continue
        wrapper_kwargs = getattr(wrapper_spec, "kwargs", {}) or {}
        discrete_space = wrapper_kwargs.get("discrete_space")
        if discrete_space is not None:
            return discrete_space
    return fallback


def get_env_metadata(env_id: str) -> Dict[str, Any]:
    """Retorna les metadades de l'env."""
    spec = gym.spec(env_id)
    env_kwargs = dict(spec.kwargs or {})
    variables = env_kwargs.get("variables", {}) or {}
    meters = with_detailed_hvac_meters(env_kwargs.get("meters", {}) or {})
    env_kwargs["meters"] = meters
    actuators = env_kwargs.get("actuators", {}) or {}
    context = env_kwargs.get("context", {}) or {}
    time_variables = env_kwargs.get("time_variables", []) or []
    observation_variables = time_variables + list(variables.keys()) + list(meters.keys())
    action_variables = list(actuators.keys())
    context_variables = list(context.keys())
    base_action_space = env_kwargs.get("action_space")
    action_space = _effective_action_space_from_spec(spec, base_action_space)
    building_file = env_kwargs.get("building_file")
    building_name = os.path.basename(building_file) if building_file else ""
    return {
        "spec": spec,
        "env_kwargs": env_kwargs,
        "variables": variables,
        "meters": meters,
        "actuators": actuators,
        "context": context,
        "time_variables": time_variables,
        "observation_variables": observation_variables,
        "action_variables": action_variables,
        "context_variables": context_variables,
        "action_space": action_space,
        "base_action_space": base_action_space,
        "is_continuous": isinstance(action_space, Box),
        "is_discrete": isinstance(action_space, DISCRETE_ACTION_SPACES),
        "building_file": building_file,
        "building_name": building_name,
        "candidate_temp_vars": default_comfort_temperature_variables(observation_variables, variables),
        "candidate_energy_vars": [
            key for key in observation_variables if is_energy_variable(key, variables)
        ],
        "candidate_grid_energy_vars": default_grid_energy_variables(observation_variables),
        "candidate_battery_charge_vars": default_battery_variables(observation_variables, "charge"),
        "candidate_battery_discharge_vars": default_battery_variables(observation_variables, "discharge"),
        "candidate_battery_loss_vars": default_battery_variables(observation_variables, "loss"),
        "candidate_cost_vars": [key for key in observation_variables if ("cost" in key.lower() or "billing" in key.lower())],
        "candidate_setpoint_vars": [key for key in variables if "setpoint" in key.lower()],
    }


def is_comfort_temperature_variable(variable_name: str, variables: Dict[str, Any]) -> bool:
    """És variable la temperatura de confort."""
    variable_name_lower = str(variable_name).lower()
    if "temperature" not in variable_name_lower:
        return False
    if "outdoor" in variable_name_lower or "setpoint" in variable_name_lower:
        return False

    variable_meta = variables.get(variable_name)
    if isinstance(variable_meta, (list, tuple)):
        output_name = str(variable_meta[0]).lower() if len(variable_meta) > 0 else ""
        output_key = str(variable_meta[1]).lower() if len(variable_meta) > 1 else ""
        if "outdoor" in output_name:
            return False
        if output_key in {"environment", "site", "whole building"}:
            return False
        if "zone air temperature" in output_name:
            return True

    return "air_temperature" in variable_name_lower


def default_comfort_temperature_variables(
    variable_names: Sequence[str], variables: Dict[str, Any]
) -> List[str]:
    """Variables de temperatura de confort per defecte."""
    return [
        variable_name
        for variable_name in variable_names
        if variable_name in variables and is_comfort_temperature_variable(variable_name, variables)
    ]


def is_energy_variable(variable_name: str, variables: Dict[str, Any]) -> bool:
    """És l'energia variable."""
    variable_name_lower = str(variable_name).lower()
    if any(
        token in variable_name_lower
        for token in ("energy", "electricity", "elèctricity", "power", "hvac", "demand")
    ):
        return True

    variable_meta = variables.get(variable_name)
    if isinstance(variable_meta, (list, tuple)):
        output_name = str(variable_meta[0]).lower() if len(variable_meta) > 0 else ""
        output_key = str(variable_meta[1]).lower() if len(variable_meta) > 1 else ""
        if any(
            token in output_name
            for token in ("electricity", "power", "demand rate", "hvac")
        ):
            return True
        if any(token in output_key for token in ("whole building", "hvac")):
            return True

    return False


def default_grid_energy_variables(variable_names: Sequence[str]) -> List[str]:
    """Variables d'energia de xarxa per defecte."""
    available = list(variable_names)
    preferred = [
        "facility_net_purchased_electricity_rate",
        "facility_total_purchased_electricity_rate",
        "facility_total_electricity_demand_rate",
        "facility_total_building_electricity_demand_rate",
    ]
    for variable_name in preferred:
        if variable_name in available:
            return [variable_name]
    return [
        variable_name
        for variable_name in available
        if "purchased" in variable_name.lower() or "grid" in variable_name.lower()
    ][:1]


def default_battery_variables(variable_names: Sequence[str], kind: str) -> List[str]:
    """Variables per defecte de la bateria."""
    available = list(variable_names)
    kind_tokens = {
        "charge": ("storage_charge_power", "battery_charge"),
        "discharge": ("storage_discharge_power", "battery_discharge"),
        "loss": ("storage_thermal_loss_rate", "battery_loss"),
    }
    tokens = kind_tokens.get(kind, ())
    matches = [
        variable_name
        for variable_name in available
        if any(token in variable_name.lower() for token in tokens)
    ]
    if matches:
        return matches[:1]

    fallback_tokens = {
        "charge": ("charge",),
        "discharge": ("discharge",),
        "loss": ("loss", "thermal"),
    }.get(kind, ())
    return [
        variable_name
        for variable_name in available
        if "storage" in variable_name.lower()
        and any(token in variable_name.lower() for token in fallback_tokens)
    ][:1]


def load_default_reward_variables(
    spec: Any, env_id: str, variables: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[str], List[str], List[str]]:
    """Carrega les variables de recompensa predeterminades."""
    resolved_variables = variables
    try:
        env_kwargs = dict(getattr(spec, "kwargs", {}) or {})
        meters = env_kwargs.get("meters", {}) or {}
        available_observation_names = list(dict.fromkeys([*variables.keys(), *meters.keys()]))

        spec_reward_cfg = (
            env_kwargs.get("reward_kwargs")
            if isinstance(env_kwargs.get("reward_kwargs"), dict)
            else {}
        )
        temp_vars: List[str] = list(spec_reward_cfg.get("temperature_variables") or [])
        energy_vars: List[str] = list(spec_reward_cfg.get("energy_variables") or [])
        cost_vars: List[str] = list(spec_reward_cfg.get("energy_cost_variables") or [])

        building_file = env_kwargs.get("building_file")
        base_name = os.path.splitext(os.path.basename(building_file))[0] if building_file else env_id
        cfg_file = CFG_DIR / f"{base_name}.yaml"

        if os.path.isfile(cfg_file) and not (temp_vars and energy_vars):
            # Preferim la configuració oficial de Sinergym quan existeix; porta els noms
            # de variables que l'entorn espera per defecte.
            with open(cfg_file, "r", encoding="utf-8") as cfg_handle:
                cfg = yaml.safe_load(cfg_handle) or {}
            reward_cfg = cfg.get("reward_kwargs", {}) if isinstance(cfg.get("reward_kwargs"), dict) else {}
            temp_vars = temp_vars or (
                reward_cfg.get("temperature_variables")
                or cfg.get("temperature_variables")
                or []
            )
            energy_vars = energy_vars or (
                reward_cfg.get("energy_variables")
                or cfg.get("energy_variables")
                or []
            )
            cost_vars = cost_vars or (
                reward_cfg.get("energy_cost_variables")
                or cfg.get("energy_cost_variables")
                or []
            )

        if not temp_vars:
            # Si el YAML no ajuda, fem una inferència prudent a partir dels noms de variables.
            temp_vars = default_comfort_temperature_variables(variables.keys(), variables)
        if not energy_vars:
            energy_vars = [
                key
                for key in available_observation_names
                if is_energy_variable(key, variables)
            ]
        if not cost_vars:
            cost_vars = [
                key
                for key in available_observation_names
                if "cost" in key.lower() or "billing" in key.lower()
            ]

        temp_vars = [value for value in temp_vars if value in variables]
        available_observation_set = set(available_observation_names)
        energy_vars = [value for value in energy_vars if value in available_observation_set]
        cost_vars = [value for value in cost_vars if value in available_observation_set]
        # Tornem a sanejar temperatures per evitar setpoints o variables globals que hagin
        # entrat per heurística però no siguin temperatura interior real.
        sanitized_temp_vars = default_comfort_temperature_variables(temp_vars, variables)
        if sanitized_temp_vars:
            temp_vars = sanitized_temp_vars
        return resolved_variables, temp_vars, energy_vars, cost_vars
    except Exception:
        return {}, [], [], []
