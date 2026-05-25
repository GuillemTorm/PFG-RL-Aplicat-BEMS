"""Crea i valideu les configuracions de Sinergym des de l'entrada del formulari Studio.

Aquest mòdul és l'últim pas del flux Afegeix un entorn. Rep el
anàlisi d'edificis, variables seleccionades, comptadors, actuadors i paràmetres de recompensa,
després escriu una configuració YAML que es pot registrar com a Gymnasium
entorn.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import gymnasium as gym
import sinergym
import yaml
from sinergym.utils.common import convert_conf_to_env_parameters

from backend.afegir_entorn_analysis import find_available_meter, find_available_output_variable
from backend.afegir_entorn_common import (
    DEFAULT_TIME_VARIABLES,
    DETAILED_HVAC_METER_CANDIDATES,
    ENERGY_METER_CANDIDATES,
    ENERGY_VARIABLE_CANDIDATES,
    ENV_VALIDATION_TIMEOUT_SECONDS,
    STANDARD_WEATHER_VARIABLES,
    STANDARD_ZONE_VARIABLES,
)
from backend.afegir_entorn_common import (
    ActuatorOption,
    BuildingTrainingAnalysis,
    EnvironmentValidationResult,
)
from backend.afegir_entorn_common import sanitize_identifier, unique_identifier

def build_variable_output_names(base_name: str, keys: Sequence[str] | str) -> List[str]:
    """Retorna àlies de variable de sortida estables per a una o més claus EnergyPlus."""
    if isinstance(keys, str):
        return [base_name]
    return [f"{key.lower().replace(' ', '_')}_{base_name}" for key in keys]


def add_variable_spec(
    variables: Dict[str, Dict[str, Any]],
    available_output_variables: Sequence[Tuple[str, str]],
    canonical_variable_name: str,
    alias_name: str,
    keys: Sequence[str] | str,
) -> List[str]:
    """Afegeix una especificació variable."""
    requested_keys = [keys] if isinstance(keys, str) else list(keys)
    matched_keys: List[str] = []
    actual_variable_name = canonical_variable_name

    for requested_key in requested_keys:
        matched = find_available_output_variable(
            available_output_variables,
            canonical_variable_name,
            requested_key,
        )
        if matched is None:
            continue
        actual_variable_name, actual_key = matched
        matched_keys.append(actual_key)

    if not matched_keys:
        if isinstance(keys, str):
            variables[canonical_variable_name] = {
                "variable_names": alias_name,
                "keys": keys,
            }
            return [alias_name]

        variables[canonical_variable_name] = {
            "variable_names": alias_name,
            "keys": list(keys),
        }
        return build_variable_output_names(alias_name, list(keys))

    output_keys: Sequence[str] | str
    if len(matched_keys) == 1:
        output_keys = matched_keys[0]
    else:
        output_keys = matched_keys

    variables[actual_variable_name] = {
        "variable_names": alias_name,
        "keys": output_keys,
    }
    return build_variable_output_names(alias_name, output_keys)


def build_training_observation_config(
    analysis: BuildingTrainingAnalysis,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str], List[str], List[str]]:
    """Munta la configuració d'observacions d'entrenament."""
    variables: Dict[str, Dict[str, Any]] = {}
    meters: Dict[str, str] = {}

    # Primer afegim variables meteorològiques i de zona "normals"; són les que després
    # espera la UI encara que el fitxer EnergyPlus tingui noms llargs o lleugerament diferents.
    for variable_name, alias_name, variable_key in STANDARD_WEATHER_VARIABLES:
        add_variable_spec(
            variables,
            analysis.available_output_variables,
            variable_name,
            alias_name,
            variable_key,
        )

    temperature_variable_names: List[str] = []
    for variable_name, alias_name in STANDARD_ZONE_VARIABLES:
        generated_names = add_variable_spec(
            variables,
            analysis.available_output_variables,
            variable_name,
            alias_name,
            analysis.thermostat_zones,
        )
        if alias_name == "air_temperature":
            temperature_variable_names = generated_names

    energy_variable_names: List[str] = []
    for variable_name, alias_name, variable_key in ENERGY_VARIABLE_CANDIDATES:
        matched = find_available_output_variable(
            analysis.available_output_variables,
            variable_name,
            variable_key,
        )
        if matched is None and analysis.probe_success:
            continue

        add_variable_spec(
            variables,
            analysis.available_output_variables,
            variable_name,
            alias_name,
            variable_key,
        )
        energy_variable_names = [alias_name]
        break

    if not energy_variable_names:
        # Alguns models no publiquen energia HVAC com a output variable, però sí com a meter.
        # En aquest cas fem servir el meter equivalent i mantenim el mateix alias intern.
        for meter_name, alias_name in ENERGY_METER_CANDIDATES:
            matched_meter = find_available_meter(analysis.available_meters, meter_name)
            if matched_meter is None and analysis.probe_success:
                continue
            meters[matched_meter or meter_name] = alias_name
            energy_variable_names = [alias_name]
            break

    for meter_name, alias_name in DETAILED_HVAC_METER_CANDIDATES:
        # Els meters detallats no són obligatoris per entrenar, però si hi són donen
        # gràfics molt més útils al dashboard.
        matched_meter = find_available_meter(analysis.available_meters, meter_name)
        if matched_meter is None:
            continue
        meters.setdefault(matched_meter, alias_name)

    if not temperature_variable_names:
        raise ValueError(
            "No s'han pogut construir variables de temperatura de zona a partir dels termòstats detectats."
        )
    if not energy_variable_names:
        raise ValueError(
            "No s'ha detectat cap variable o meter energètic vàlid per construir la reward."
        )

    return variables, meters, temperature_variable_names, energy_variable_names


def build_variable_name_for_actuator(
    option: ActuatorOption,
    selected_options: Sequence[ActuatorOption],
    used_names: set[str],
) -> str:
    """Genera el nom de variable associat a un actuador."""
    heating_count = sum(item.category == "heating_setpoint" for item in selected_options)
    cooling_count = sum(item.category == "cooling_setpoint" for item in selected_options)

    # Si només hi ha una consigna de fred/calor mantenim noms simples. Amb més zones,
    # el nom ha de portar zona o schedule per no crear variables duplicades.
    if option.category == "heating_setpoint":
        if heating_count == 1:
            base_name = "Heating_Setpoint_RL"
        elif len(option.zones) == 1:
            base_name = f"heating_setpoint_{sanitize_identifier(option.zones[0], 'zone')}"
        else:
            base_name = f"heating_setpoint_{sanitize_identifier(option.actuator_key, 'schedule')}"
    elif option.category == "cooling_setpoint":
        if cooling_count == 1:
            base_name = "Cooling_Setpoint_RL"
        elif len(option.zones) == 1:
            base_name = f"cooling_setpoint_{sanitize_identifier(option.zones[0], 'zone')}"
        else:
            base_name = f"cooling_setpoint_{sanitize_identifier(option.actuator_key, 'schedule')}"
    elif option.category == "scheduled_temperature_setpoint":
        base_name = f"hvac_setpoint_{sanitize_identifier(option.actuator_key, 'schedule')}"
    elif option.category == "availability":
        base_name = f"hvac_availability_{sanitize_identifier(option.actuator_key, 'schedule')}"
    elif option.category == "battery_charge":
        base_name = "Battery_Charge_Rate_RL"
    elif option.category == "battery_discharge":
        base_name = "Battery_Discharge_Rate_RL"
    else:
        base_name = f"hvac_control_{sanitize_identifier(option.actuator_key, 'actuator')}"

    return unique_identifier(base_name, used_names)


def build_action_space_expression(bounds: Sequence[Tuple[float, float]]) -> str:
    """Construeix una expressió d'espai d'acció."""
    lows = ", ".join(f"{low:.4f}" for low, _ in bounds)
    highs = ", ".join(f"{high:.4f}" for _, high in bounds)
    return (
        "gym.spaces.Box("
        f"low=np.array([{lows}], dtype=np.float32), "
        f"high=np.array([{highs}], dtype=np.float32), "
        f"shape=({len(bounds)},), dtype=np.float32)"
    )


def build_environment_config(
    id_base: str,
    building_file_name: str,
    weather_profiles: Sequence[Dict[str, str]],
    analysis: BuildingTrainingAnalysis,
    selected_actuators: Sequence[ActuatorOption],
    actuator_bounds: Dict[str, Tuple[float, float]],
    weather_variability: Optional[Dict[str, Sequence[float]]] = None,
) -> Dict[str, Any]:
    """Construeix el diccionari de configuració de l'entorn arrel Sinergym YAML.

    Paràmetres:
        id_base (str): nom base per al registre de l'entorn.
        building_file_name (str): el nom del fitxer d'estructura.
        weather_profiles (Sequence[Dict[str, str]]): Llista de mapes meteorològics (fitxa i claus).
        analysis (BuildingTrainingAnalysis): propietats detectades.
        selected_actuators (Sequence[ActuatorOption]): actuadors seleccionats del UI.
        actuator_bounds (Dict[str, Tuple[float, float]]): els límits continus de cada actuador.
        weather_variability (Optional[Dict[str, Sequence[float]]]): Diccionari de variabilitat opcional.

    Retorna:
        Dict[str, Any]: La configuració totalment estructurada està preparada per escriure com a YAML.
    """
    variables, meters, temperature_variable_names, energy_variable_names = (
        build_training_observation_config(analysis)
    )

    # Ordenem actuadors perquè el Box tingui un ordre estable: calor, fred, bateria i resta.
    # Sense això, dos registres del mateix edifici podrien generar espais d'acció diferents.
    ordered_actuators = sorted(
        selected_actuators,
        key=lambda option: (
            {
                "heating_setpoint": 0,
                "cooling_setpoint": 1,
                "battery_charge": 2,
                "battery_discharge": 3,
            }.get(option.category, 4),
            option.label.lower(),
        ),
    )

    used_variable_names: set[str] = set()
    actuators: Dict[str, Dict[str, str]] = {}
    bounds: List[Tuple[float, float]] = []
    for option in ordered_actuators:
        # actuator_key apunta a l'objecte EnergyPlus real; variable_name és el nom curt que
        # veurà Sinergym i després el model RL.
        low, high = actuator_bounds[option.option_id]
        variable_name = build_variable_name_for_actuator(option, ordered_actuators, used_variable_names)
        actuators[option.actuator_key] = {
            "variable_name": variable_name,
            "element_type": option.element_type,
            "value_type": option.value_type,
        }
        bounds.append((low, high))

    env_cfg: Dict[str, Any] = {
        "id_base": id_base,
        "building_file": building_file_name,
        "weather_specification": {
            "weather_files": [profile["weather_file"] for profile in weather_profiles],
            "keys": [profile["key"] for profile in weather_profiles],
        },
        "building_config": None,
        "max_ep_store": 3,
        "time_variables": list(DEFAULT_TIME_VARIABLES),
        "variables": variables,
        "meters": meters,
        "actuators": actuators,
        "context": {},
        "action_space": build_action_space_expression(bounds),
        "reward": "sinergym.utils.rewards:LinearReward",
        "reward_kwargs": {
            "temperature_variables": temperature_variable_names,
            "energy_variables": energy_variable_names,
            "range_comfort_winter": [20.0, 23.5],
            "range_comfort_summer": [23.0, 26.0],
            "summer_start": [6, 1],
            "summer_final": [9, 30],
            "energy_weight": 0.5,
            "lambda_energy": 1e-4,
            "lambda_temperature": 1.0,
        },
    }

    if weather_variability:
        # Només escrivim weather_variability quan l'usuari l'ha configurat; deixar-ho buit
        # pot activar comportaments diferents en versions de Sinergym.
        env_cfg["weather_variability"] = weather_variability

    return env_cfg


def write_yaml_config(cfg_path: Path, env_cfg: Dict[str, Any]) -> Path:
    """Escriu el diccionari de configuració de l'entorn generat en un fitxer YAML.

    Paràmetres:
        cfg_path (Path): Camí al fitxer de sortida YAML.
        env_cfg (Dict[str, Any]): dades de configuració del diccionari.

    Retorna:
        Path: la ruta del fitxer de sortida confirmada.
    """
    with open(cfg_path, "w", encoding="utf-8") as file_handle:
        yaml.dump(env_cfg, file_handle, sort_keys=False, allow_unicode=True)
    return cfg_path


def register_environment_from_yaml(cfg_path: Path) -> None:
    """Registra o torna a registrar els entorns des d'una configuració Sinergym YAML mitjançant Gym.

    Paràmetres:
        cfg_path (Path): camí cap a la configuració vàlida Sinergym YAML.
    """
    with open(cfg_path, "r", encoding="utf-8") as yaml_conf:
        conf = yaml.safe_load(yaml_conf)

    configurations = convert_conf_to_env_parameters(conf)
    registry = gym.envs.registration.registry
    for env_id in configurations.keys():
        registry.pop(env_id, None)
        registry.pop(env_id.replace("continuous", "discrete"), None)

    sinergym.register_envs_from_yaml(str(cfg_path))


def build_registered_env_id(id_base: str, weather_key: str, stochastic: bool = False) -> str:
    """Crea l'ID de l'entorn del Gym canònic basat en les convencions de denominació Sinergym.

    Paràmetres:
        id_base (str): Nom base donat a l'element d'edifici.
        weather_key (str): descriptor breu de la cadena meteorològica.
        stochastic (bool, optional): si la variant pretén incloure variabilitat.

    Retorna:
        str: identificador d'entorn OpenAI Gym vàlid.
    """
    suffix = "-continuous-stochastic-v1" if stochastic else "-continuous-v1"
    return f"Eplus-{id_base}-{weather_key}{suffix}"


def validate_registered_environment(env_id: str, cfg_path: Optional[Path] = None) -> EnvironmentValidationResult:
    """Executa un subprocés aïllat per activar i validar que l'entorn es registra i passa correctament.

    Paràmetres:
        env_id (str): cadena d'ID d'entorn Gym.
        cfg_path (Optional[Path], optional): camí cap a yaml si és necessari per al registre diferit.

    Retorna:
        EnvironmentValidationResult: un dict de verificació estructural que indica la matriu d'observació i els espais.
    """
    validation_script = """
import json
import sys

import gymnasium as gym
import sinergym

env_id = sys.argv[1]
cfg_path = sys.argv[2] if len(sys.argv) > 2 else None
if cfg_path:
    sinergym.register_envs_from_yaml(cfg_path)

env = gym.make(env_id)
try:
    observation = env.reset()[0]
    if hasattr(observation, "tolist"):
        observation = observation.tolist()
    payload = {
        "observation_space": repr(env.observation_space),
        "action_space": repr(env.action_space),
        "initial_observation": observation,
    }
    print(f"---JSON_START---\\n{json.dumps(payload)}\\n---JSON_END---")
finally:
    env.close()
"""

    try:
        result = subprocess.run(
            [sys.executable, "-", env_id, *( [str(cfg_path)] if cfg_path else [] )],
            input=validation_script,
            check=True,
            capture_output=True,
            text=True,
            timeout=ENV_VALIDATION_TIMEOUT_SECONDS,
        )
        match = re.search(r"---JSON_START---\n(.*?)\n---JSON_END---", result.stdout, re.DOTALL)
        if not match:
            raise RuntimeError(f"No s'ha trobat l'estructura de validació a l'output. Output obtingut:\n{result.stdout}\nErrors:\n{result.stderr}")

        payload = json.loads(match.group(1))
        return EnvironmentValidationResult(
            observation_space=payload["observation_space"],
            action_space=payload["action_space"],
            initial_observation=payload["initial_observation"],
        )
    except subprocess.TimeoutExpired as error:
        raise TimeoutError(
            "La validació de l'entorn ha superat el temps límit. "
            "Revisa la configuració del model o prova un edifici més lleuger."
        ) from error
    except subprocess.CalledProcessError as error:
        stderr = (error.stderr or "").strip()
        stdout = (error.stdout or "").strip()
        raise RuntimeError(stderr or stdout or "La validació ha fallat en arrencar l'entorn.") from error


def cleanup_failed_environment(cfg_path: Path, tmp_path: Path) -> List[Tuple[str, str]]:
    """Intenta eliminar les estructures de configuració no enllaçades o incorrectes com a resultat d'un registre fallit.

    Paràmetres:
        cfg_path (Path): Configuració interrompuda de YAML.
        tmp_path (Path): fitxer epJSON intermedi generat.

    Retorna:
        List[Tuple[str, str]]: Tuples de missatgeria de nivell de diagnòstic que mapegen quins recursos es van revertir.
    """
    messages: List[Tuple[str, str]] = []
    try:
        if cfg_path.exists():
            cfg_path.unlink()
            messages.append(("warning", "Fitxer de registre YAML revertit."))
        if tmp_path.suffix.lower() == ".idf":
            epjson_path = tmp_path.with_suffix(".epJSON")
            if epjson_path.exists():
                epjson_path.unlink()
                messages.append(("warning", "Fitxer estructural epJSON revertit."))
    except Exception as cleanup_error:
        messages.append(("error", f"Error eliminant fitxers: {cleanup_error}"))
    return messages
