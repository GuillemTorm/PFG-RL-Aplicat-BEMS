"""Recompenses, algorismes i creadors de càrrega útil de entrenament completa."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from backend.entrenar_agent_artifacts import build_training_ui_state
from backend.entrenar_agent_constants import (
    BATTERY_REWARDS,
    COST_REWARDS,
    DEFAULT_MINUTES_PER_STEP,
    MULTIZONE_REWARDS,
    REWARD_CLASSES,
)
from backend.entrenar_agent_env import (
    default_battery_variables,
    default_grid_energy_variables,
    get_training_meters_for_env,
    load_default_reward_variables,
)
from backend.common import filter_supported_kwargs
from backend.entrenar_agent_wrappers import (
    build_energy_cost_wrapper_reward_kwargs,
    build_wrapper_configs,
    build_wrapper_summary_rows,
)
from backend.sb3_utils import ALGOS


def build_multizone_temp_mapping(
    variables: Dict[str, Any], temp_vars: Sequence[str], pair_setpoints: bool = False
) -> Dict[str, Any]:
    """Prepara un mapa de temperatures i setpoints per zones."""
    # Les variables de Sinergym guarden el domini/zona a la segona posició. L'aprofitem
    # per emparellar cada temperatura amb els seus setpoints sense dependre només del nom.
    setpoint_vars = [key for key in variables if "setpoint" in key.lower()]
    heating_setpoints = [
        key for key in setpoint_vars if "htg" in key.lower() or "heating" in key.lower()
    ]
    cooling_setpoints = [
        key for key in setpoint_vars if "clg" in key.lower() or "cooling" in key.lower()
    ]
    temp_mapping: Dict[str, Any] = {}
    for temp_var in temp_vars:
        domain = variables[temp_var][1] if temp_var in variables else None
        matches = [
            setpoint_var
            for setpoint_var in setpoint_vars
            if domain and variables.get(setpoint_var, [None, None])[1] == domain
        ]
        if pair_setpoints:
            # Algunes rewards volen parella [calor, fred]. Si no trobem coincidència de zona,
            # fem fallback a la primera parella global disponible.
            heating_matches = [match for match in matches if match in heating_setpoints]
            cooling_matches = [match for match in matches if match in cooling_setpoints]
            if heating_matches and cooling_matches:
                temp_mapping[temp_var] = [heating_matches[0], cooling_matches[0]]
            elif matches:
                temp_mapping[temp_var] = matches[0]
            elif heating_setpoints and cooling_setpoints:
                temp_mapping[temp_var] = [heating_setpoints[0], cooling_setpoints[0]]
            elif setpoint_vars:
                temp_mapping[temp_var] = setpoint_vars[0]
        elif matches:
            temp_mapping[temp_var] = matches[0]
        elif len(setpoint_vars) == 1:
            temp_mapping[temp_var] = setpoint_vars[0]
    return temp_mapping


def build_multizone_occupancy_mapping(
    variables: Dict[str, Any], temp_vars: Sequence[str]
) -> Dict[str, str]:
    """Prepara un mapa d'ocupació per zones."""
    occupancy_vars = [
        key
        for key in variables
        if "occupant" in key.lower() or "occupancy" in key.lower()
    ]
    occupancy_mapping: Dict[str, str] = {}
    for temp_var in temp_vars:
        temp_meta = variables.get(temp_var)
        temp_domain = temp_meta[1] if isinstance(temp_meta, (list, tuple)) and len(temp_meta) > 1 else None
        matches = [
            occupancy_var
            for occupancy_var in occupancy_vars
            if temp_domain
            and isinstance(variables.get(occupancy_var), (list, tuple))
            and len(variables[occupancy_var]) > 1
            and variables[occupancy_var][1] == temp_domain
        ]
        if not matches:
            temp_prefix = temp_var.lower().replace("_air_temperature", "")
            matches = [
                occupancy_var
                for occupancy_var in occupancy_vars
                if occupancy_var.lower().startswith(temp_prefix)
            ]
        if matches:
            occupancy_mapping[temp_var] = matches[0]
    return occupancy_mapping


def _build_common_reward_kwargs(
    options: Dict[str, Any],
    temp_vars: Sequence[str],
    energy_vars: Sequence[str],
) -> Dict[str, Any]:
    """Crea els paràmetres compartits per les rewards lineals i de bateria."""
    return {
        "temperature_variables": list(temp_vars),
        "energy_variables": list(energy_vars),
        "range_comfort_winter": tuple(options["range_winter"]),
        "range_comfort_summer": tuple(options["range_summer"]),
        "summer_start": (options["summer_start_m"], options["summer_start_d"]),
        "summer_final": (options["summer_final_m"], options["summer_final_d"]),
        "energy_weight": options["energy_weight"],
        "lambda_energy": options["lambda_energy"],
        "lambda_temperature": options["lambda_temperature"],
    }


def _build_battery_reward_kwargs(
    options: Dict[str, Any],
    variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Crea la part comuna de les rewards que penalitzen xarxa i bateria."""
    available_variables = variables.keys()
    grid_energy_variables = (
        list(options["grid_energy_variables"])
        if "grid_energy_variables" in options
        else default_grid_energy_variables(available_variables)
    )
    battery_charge_variables = (
        list(options["battery_charge_variables"])
        if "battery_charge_variables" in options
        else default_battery_variables(available_variables, "charge")
    )
    battery_discharge_variables = (
        list(options["battery_discharge_variables"])
        if "battery_discharge_variables" in options
        else default_battery_variables(available_variables, "discharge")
    )
    battery_loss_variables = (
        list(options["battery_loss_variables"])
        if "battery_loss_variables" in options
        else default_battery_variables(available_variables, "loss")
    )

    return {
        "grid_energy_variables": grid_energy_variables,
        "battery_charge_variables": battery_charge_variables,
        "battery_discharge_variables": battery_discharge_variables,
        "battery_loss_variables": battery_loss_variables,
        "grid_energy_weight": options.get("grid_energy_weight", 0.2),
        "battery_cycle_weight": options.get("battery_cycle_weight", 0.04),
        "battery_loss_weight": options.get("battery_loss_weight", 0.005),
        "simultaneous_battery_weight": options.get("simultaneous_battery_weight", 0.005),
        "lambda_grid": options.get("lambda_grid", options["lambda_energy"]),
        "lambda_battery": options.get("lambda_battery", options["lambda_energy"]),
    }


def _build_multizone_base_kwargs(
    options: Dict[str, Any],
    energy_vars: Sequence[str],
    temp_mapping: Dict[str, Any],
) -> Dict[str, Any]:
    """Crea la base de kwargs que comparteixen les rewards multizona."""
    return {
        "energy_variables": list(energy_vars),
        "temperature_and_setpoints_conf": temp_mapping,
        "comfort_threshold": options["comfort_threshold"],
        "energy_weight": options["energy_weight"],
        "lambda_energy": options["lambda_energy"],
        "lambda_temperature": options["lambda_temperature"],
    }


def _add_energy_cost_file_kwargs(
    reward_kwargs: Dict[str, Any],
    options: Dict[str, Any],
    cost_vars: Sequence[str],
) -> None:
    """Afegeix cost horari i fitxer de preus quan la reward ho necessita."""
    reward_kwargs.update(
        {
            "lambda_energy_cost": options["lambda_energy_cost"],
            "energy_cost_variables": list(cost_vars),
            "energy_cost_path": options["energy_cost_path"],
            "seconds_per_step": DEFAULT_MINUTES_PER_STEP * 60,
        }
    )


def _build_single_zone_reward_kwargs(
    reward_name: str,
    options: Dict[str, Any],
    reward_common: Dict[str, Any],
    battery_kwargs: Dict[str, Any],
    temp_vars: Sequence[str],
    energy_vars: Sequence[str],
    cost_vars: Sequence[str],
) -> Dict[str, Any] | None:
    """Crea kwargs per rewards que treballen amb variables globals o monozona."""
    if reward_name == "EnergyCostLinearReward":
        reward_kwargs = dict(reward_common)
        reward_kwargs["energy_cost_variables"] = list(cost_vars)
        reward_kwargs["temperature_weight"] = options["temperature_weight"]
        reward_kwargs["lambda_energy_cost"] = options["lambda_energy_cost"]
        return reward_kwargs

    if reward_name == "BatteryHVACReward":
        reward_kwargs = dict(reward_common)
        reward_kwargs["temperature_weight"] = options["temperature_weight"]
        reward_kwargs.update(battery_kwargs)
        return reward_kwargs

    if reward_name == "HourlyLinearReward":
        return {
            "temperature_variables": list(temp_vars),
            "energy_variables": list(energy_vars),
            "range_comfort_winter": tuple(options["range_winter"]),
            "range_comfort_summer": tuple(options["range_summer"]),
            "summer_start": (options["summer_start_m"], options["summer_start_d"]),
            "summer_final": (options["summer_final_m"], options["summer_final_d"]),
            "lambda_energy": options["lambda_energy"],
            "lambda_temperature": options["lambda_temperature"],
            "range_comfort_hours": tuple(options["range_comfort_hours"]),
        }

    if reward_name == "EnergyCostHourlyReward":
        reward_kwargs = dict(reward_common)
        reward_kwargs["temperature_weight"] = options["temperature_weight"]
        reward_kwargs["range_comfort_hours"] = tuple(options["range_comfort_hours"])
        _add_energy_cost_file_kwargs(reward_kwargs, options, cost_vars)
        return reward_kwargs

    if reward_name == "OccupiedHoursDiscomfortReward":
        reward_kwargs = dict(reward_common)
        reward_kwargs["occupied_hours"] = tuple(options["occupied_hours"])
        reward_kwargs["occupied_discomfort_multiplier"] = options["occupied_discomfort_multiplier"]
        reward_kwargs["off_hours_energy_multiplier"] = options["off_hours_energy_multiplier"]
        return reward_kwargs

    return None


def _build_multizone_reward_kwargs(
    reward_name: str,
    options: Dict[str, Any],
    energy_vars: Sequence[str],
    cost_vars: Sequence[str],
    temp_mapping: Dict[str, Any],
    occupancy_mapping: Dict[str, str],
    battery_kwargs: Dict[str, Any],
) -> Dict[str, Any] | None:
    """Crea kwargs per rewards que separen temperatura i consignes per zona."""
    if reward_name == "MultiZoneReward":
        return _build_multizone_base_kwargs(options, energy_vars, temp_mapping)

    if reward_name == "OccupancyMultiZoneReward":
        reward_kwargs = _build_multizone_base_kwargs(options, energy_vars, temp_mapping)
        reward_kwargs["occupancy_variables_conf"] = occupancy_mapping
        reward_kwargs["occupancy_threshold"] = 0.0
        return reward_kwargs

    if reward_name == "MultiZoneHourlyReward":
        reward_kwargs = _build_multizone_base_kwargs(options, energy_vars, temp_mapping)
        reward_kwargs["default_energy_weight"] = reward_kwargs.pop("energy_weight")
        reward_kwargs["range_comfort_hours"] = tuple(options["range_comfort_hours"])
        return reward_kwargs

    if reward_name == "MultiZoneEnergyCostReward":
        reward_kwargs = _build_multizone_base_kwargs(options, energy_vars, temp_mapping)
        reward_kwargs["temperature_weight"] = options["temperature_weight"]
        _add_energy_cost_file_kwargs(reward_kwargs, options, cost_vars)
        return reward_kwargs

    if reward_name == "MultiZoneEnergyCostHourlyReward":
        reward_kwargs = _build_multizone_base_kwargs(options, energy_vars, temp_mapping)
        reward_kwargs["temperature_weight"] = options["temperature_weight"]
        reward_kwargs["range_comfort_hours"] = tuple(options["range_comfort_hours"])
        _add_energy_cost_file_kwargs(reward_kwargs, options, cost_vars)
        return reward_kwargs

    if reward_name == "MultiZoneBatteryHVACReward":
        reward_kwargs = _build_multizone_base_kwargs(options, energy_vars, temp_mapping)
        reward_kwargs["temperature_weight"] = options["temperature_weight"]
        reward_kwargs.update(battery_kwargs)
        return reward_kwargs

    if reward_name == "MultizoneEnergyCostBatteryHVACReward":
        reward_kwargs = _build_multizone_base_kwargs(options, energy_vars, temp_mapping)
        reward_kwargs["temperature_weight"] = options["temperature_weight"]
        reward_kwargs["lambda_energy_cost"] = options["lambda_energy_cost"]
        reward_kwargs["energy_cost_weight"] = options.get("energy_cost_weight", 0.20)
        reward_kwargs["energy_cost_variables"] = list(cost_vars)
        reward_kwargs["occupied_hours"] = tuple(options.get("occupied_hours", (8, 18)))
        reward_kwargs["occupied_comfort_multiplier"] = options.get("occupied_comfort_multiplier", 2.0)
        reward_kwargs["unoccupied_comfort_multiplier"] = options.get("unoccupied_comfort_multiplier", 0.3)
        reward_kwargs.update(battery_kwargs)
        return reward_kwargs

    return None


def build_reward_kwargs(
    options: Dict[str, Any],
    variables: Dict[str, Any],
    temp_vars: Sequence[str],
    energy_vars: Sequence[str],
    cost_vars: Sequence[str],
) -> Tuple[Dict[str, Any], Dict[str, str], List[str]]:
    """Munta els kwargs de recompensa a partir de la configuració."""
    reward_name = options["reward_name"]
    reward_common = _build_common_reward_kwargs(options, temp_vars, energy_vars)

    # Les rewards multizona volen un diccionari zona -> consignes. El construïm abans
    # de seleccionar la reward perquè també serveix per validar la configuració.
    temp_mapping = build_multizone_temp_mapping(
        variables,
        temp_vars,
        pair_setpoints=reward_name in ("MultiZoneBatteryHVACReward", "MultizoneEnergyCostBatteryHVACReward"),
    )
    occupancy_mapping = build_multizone_occupancy_mapping(variables, temp_vars)
    battery_kwargs = _build_battery_reward_kwargs(options, variables)

    reward_kwargs = _build_single_zone_reward_kwargs(
        reward_name=reward_name,
        options=options,
        reward_common=reward_common,
        battery_kwargs=battery_kwargs,
        temp_vars=temp_vars,
        energy_vars=energy_vars,
        cost_vars=cost_vars,
    )
    if reward_kwargs is None:
        reward_kwargs = _build_multizone_reward_kwargs(
            reward_name=reward_name,
            options=options,
            energy_vars=energy_vars,
            cost_vars=cost_vars,
            temp_mapping=temp_mapping,
            occupancy_mapping=occupancy_mapping,
            battery_kwargs=battery_kwargs,
        )
    if reward_kwargs is None:
        reward_kwargs = dict(reward_common)

    reward_cls = REWARD_CLASSES[reward_name]
    reward_kwargs, dropped_reward_kwargs = filter_supported_kwargs(reward_cls, reward_kwargs)
    return reward_kwargs, temp_mapping, dropped_reward_kwargs


def validate_training_configuration(
    options: Dict[str, Any], temp_mapping: Dict[str, str]
) -> List[str]:
    """Valida la recompensa, l'algorisme, l'espai d'acció i la compatibilitat dels wrappers."""
    validation_errors: List[str] = []
    reward_name = options["reward_name"]
    algo_name = options["algo_name"]
    action_space_type = options.get("action_space_type")

    # Primer descartem combinacions que SB3 no accepta, abans de crear entorns o models.
    if options.get("is_discrete") and algo_name in {"SAC", "TD3", "DDPG"}:
        validation_errors.append(
            f"{algo_name} nomes es pot entrenar amb espais d'accio continus. Fes servir PPO o A2C en aquest entorn."
        )
    if action_space_type in {"MultiDiscrete", "MultiBinary"} and algo_name == "DQN":
        validation_errors.append(
            "DQN nomes admet un Discrete simple; aquest entorn fa servir un espai d'accio multidiscret."
        )

    if reward_name in COST_REWARDS and (options["energy_weight"] + options["temperature_weight"] > 1.0):
        validation_errors.append("En rewards amb cost cal complir energy_weight + temperature_weight <= 1.")
    if reward_name in MULTIZONE_REWARDS and not temp_mapping:
        validation_errors.append(
            "No s'han pogut inferir setpoints compatibles per construir la reward multizona."
        )
    if reward_name in BATTERY_REWARDS:
        # Les rewards amb bateria necessiten com a mínim saber què entra de la xarxa
        # i alguna pista de càrrega o descàrrega; si no, la penalització queda buida.
        available_variables = list((options.get("variables") or {}).keys())
        grid_vars = (
            options["grid_energy_variables"]
            if "grid_energy_variables" in options
            else default_grid_energy_variables(available_variables)
        )
        charge_vars = (
            options["battery_charge_variables"]
            if "battery_charge_variables" in options
            else default_battery_variables(available_variables, "charge")
        )
        discharge_vars = (
            options["battery_discharge_variables"]
            if "battery_discharge_variables" in options
            else default_battery_variables(available_variables, "discharge")
        )
        if not grid_vars:
            validation_errors.append(
                "No s'han detectat variables de xarxa per a la reward amb bateria."
            )
        if not charge_vars and not discharge_vars:
            validation_errors.append(
                "No s'han detectat variables de càrrega o descàrrega de bateria."
            )
    # A partir d'aquí validem dependències entre wrappers. Són regles de UI, no errors
    # de Python: millor avisar amb missatges clars que deixar que falli al mig del training.
    if options["enable_previous_wrapper"] and not options["previous_variables"]:
        validation_errors.append("PreviousObservationWrapper requereix almenys una variable.")
    if options["enable_weather_forecast_wrapper"] and not options["weather_forecast_columns"]:
        validation_errors.append("WeatherForecastingWrapper requereix almenys una variable de previsió.")
    if options["enable_delta_temp_wrapper"] and (
        not options["delta_temp_variables"] or not options["delta_setpoint_variables"]
    ):
        validation_errors.append("DeltaTempWrapper requereix variables de temperatura i almenys un setpoint.")
    if options["enable_reduce_obs_wrapper"] and options["enable_datetime_wrapper"]:
        reserved_datetime_vars = {"month", "day_of_month", "hour"}
        invalid_reduction = reserved_datetime_vars.intersection(options["reduced_observations"])
        if invalid_reduction:
            validation_errors.append(
                "No pots reduir month/day_of_month/hour mentre DatetimeWrapper estigui actiu."
            )
    if options["enable_incremental_wrapper"] and not options["incremental_variables"]:
        validation_errors.append("IncrementalWrapper requereix almenys una variable d'acció.")
    if options["enable_incremental_wrapper"] and options["enable_discrete_incremental_wrapper"]:
        validation_errors.append("IncrementalWrapper i DiscreteIncrementalWrapper no es poden activar alhora.")
    if (
        options["enable_incremental_wrapper"] or options["enable_discrete_incremental_wrapper"]
    ) and options["enable_normalize_action"]:
        validation_errors.append("NormalizeAction no es pot combinar amb els wrappers incrementals en aquesta UI.")
    if options["enable_normalize_action"] and not options.get("is_continuous", True):
        validation_errors.append("NormalizeAction nomes es pot aplicar a entorns amb action_space continu.")
    if options.get("enable_variability_context_wrapper"):
        low_values = list(options.get("variability_context_low") or [])
        high_values = list(options.get("variability_context_high") or [])
        if not low_values or len(low_values) != len(high_values):
            validation_errors.append("VariabilityContextWrapper requereix limits min/max coherents.")
        if any(high <= low for low, high in zip(low_values, high_values)):
            validation_errors.append("A VariabilityContextWrapper cada maxim ha de ser superior al minim.")
        if options.get("variability_step_frequency_max", 0) <= options.get("variability_step_frequency_min", 0):
            validation_errors.append("La frequencia maxima del context ha de ser superior a la minima.")
    if (
        options.get("enable_storage_smoothing_wrapper")
        and options.get("building_name") != "OfficeGridStorageSmoothing.epJSON"
    ):
        validation_errors.append(
            "OfficeGridStorageSmoothingActionConstraintsWrapper nomes es valid per OfficeGridStorageSmoothing.epJSON."
        )

    return validation_errors


# Àlies compatibles enrere per a l'identificador públic amb accent anterior.
globals()["vàlidate_training_configuration"] = validate_training_configuration
globals()["vālidate_training_configuration"] = validate_training_configuration


def build_algo_kwargs(options: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Munta els kwargs de l'algorisme a partir de la configuració."""
    candidate_kwargs = {
        "learning_rate": options["learning_rate"],
        "n_steps": options.get("n_steps"),
        "batch_size": options.get("batch_size"),
        "n_epochs": options.get("n_epochs"),
        "gamma": options.get("gamma"),
        "gae_lambda": options.get("gae_lambda"),
        "clip_range": options.get("clip_range"),
        "ent_coef": options.get("ent_coef"),
        "vf_coef": options.get("vf_coef"),
        "max_grad_norm": options.get("max_grad_norm"),
    }
    candidate_kwargs = {
        key: value
        for key, value in candidate_kwargs.items()
        if value is not None
    }
    return filter_supported_kwargs(ALGOS[options["algo_name"]], candidate_kwargs)


def assemble_training_payload(options: Dict[str, Any]) -> Dict[str, Any]:
    """Munta tota la configuració d'entrenament a partir de la UI."""
    meters = get_training_meters_for_env(options["env_id"])
    variables, temp_vars, energy_vars, cost_vars = load_default_reward_variables(
        spec=options["spec"],
        env_id=options["env_id"],
        variables=options["variables"],
    )
    reward_kwargs, temp_mapping, dropped_reward_kwargs = build_reward_kwargs(
        options=options,
        variables=variables,
        temp_vars=temp_vars,
        energy_vars=energy_vars,
        cost_vars=cost_vars,
    )
    validation_errors = validate_training_configuration(options, temp_mapping)
    if not energy_vars:
        validation_errors.append(
            "No s'han pogut inferir variables d'energia per a la reward. Revisa la configuració de l'entorn."
        )
    if options["reward_name"] == "OccupancyMultiZoneReward":
        # Aquesta reward necessita ocupació per cada temperatura/zona. Si falta algun
        # mapa, millor fallar abans que entrenar amb una penalització incompleta.
        occupancy_mapping = reward_kwargs.get("occupancy_variables_conf") or {}
        missing_occupancy_mapping = [
            temp_var
            for temp_var in temp_mapping
            if temp_var not in occupancy_mapping
        ]
        if missing_occupancy_mapping:
            validation_errors.append(
                "No s'han pogut inferir variables d'ocupacio per a totes les zones: "
                + ", ".join(missing_occupancy_mapping)
            )
    energy_cost_wrapper_reward_kwargs = build_energy_cost_wrapper_reward_kwargs(
        options,
        temp_vars,
        energy_vars,
    )
    recalculate_energy_cost_reward = options["reward_name"] in {
        "LinearReward",
        "EnergyCostLinearReward",
    }
    # El wrapper de cost pot recalcular reward només en rewards lineals; en les altres,
    # el cost ja entra dins la pròpia classe de reward.
    wrapper_configs = build_wrapper_configs(
        options,
        energy_cost_reward_kwargs=energy_cost_wrapper_reward_kwargs,
        recalculate_energy_cost_reward=recalculate_energy_cost_reward,
    )
    wrapper_rows = build_wrapper_summary_rows(wrapper_configs)
    algo_kwargs, dropped_algo_kwargs = build_algo_kwargs(options)

    # Aquest dict és el que es desa amb l'artefacte. Ha de ser suficient per repetir,
    # avaluar o inspeccionar l'entrenament sense dependre de l'estat viu de Streamlit.
    training_config = {
        "env_id": options["env_id"],
        "algo_name": options["algo_name"],
        "policy_name": options["policy_name"],
        "reward_name": options["reward_name"],
        "reward_kwargs": reward_kwargs,
        "variables": variables,
        "meters": meters,
        "temp_vars": temp_vars,
        "energy_vars": energy_vars,
        "cost_vars": cost_vars,
        "wrapper_configs": wrapper_configs,
        "wrapper_rows": wrapper_rows,
        "learning_rate": options["learning_rate"],
        "n_steps": options["n_steps"],
        "batch_size": options.get("batch_size"),
        "n_epochs": options.get("n_epochs"),
        "gamma": options.get("gamma"),
        "gae_lambda": options.get("gae_lambda"),
        "clip_range": options.get("clip_range"),
        "ent_coef": options.get("ent_coef"),
        "vf_coef": options.get("vf_coef"),
        "max_grad_norm": options.get("max_grad_norm"),
        "algo_kwargs": algo_kwargs,
        "timesteps_per_year": options["timesteps_per_year"],
    }

    return {
        "dropped_reward_kwargs": dropped_reward_kwargs,
        "dropped_algo_kwargs": dropped_algo_kwargs,
        "ui_state": build_training_ui_state(options),
        "validation_errors": validation_errors,
        "training_config": training_config,
    }
