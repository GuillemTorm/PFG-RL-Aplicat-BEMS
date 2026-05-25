"""Lectura i anàlisi d'edificis per preparar la configuració dels entorns."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import gymnasium as gym
import numpy as np
from sinergym.envs.eplus_env import EplusEnv
from sinergym.utils.rewards import BaseReward

from backend.afegir_entorn_common import DEFAULT_TIME_VARIABLES
from backend.afegir_entorn_common import ActuatorOption, BuildingTrainingAnalysis
from backend.afegir_entorn_common import normalize_token, sanitize_identifier

class ProbeReward(BaseReward):
    """Reward nul usat només per inspeccionar handlers disponibles."""

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Executa l'objecte cridable."""
        return 0.0, {}


def load_building_json(building_path: Path) -> Dict[str, Any]:
    """Carrega i analitza un fitxer d'edifici de format epJSON en un diccionari.

    Paràmetres:
        building_path (Path): camí cap al fitxer epJSON.

    Retorna:
        Dict[str, Any]: el diccionari carregat que renderitza les dades de l'edifici.
    """
    with open(building_path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def extract_schedule_type_index(building_data: Dict[str, Any]) -> Dict[str, str]:
    """Extreu una assignació de noms d'objectes de planificació als seus respectius tipus de blocs de planificació.

    Paràmetres:
        building_data (Dict[str, Any]): les dades de l'edifici epJSON carregades.

    Retorna:
        Dict[str, str]: un diccionari que assigna noms de planificació als seus tipus de bloc d'objectes
        (e.g., 'Programació:Compact').
    """
    schedule_types: Dict[str, str] = {}
    for object_type, objects in building_data.items():
        if not object_type.startswith("Schedule:") or not isinstance(objects, dict):
            continue
        for schedule_name in objects.keys():
            schedule_types[schedule_name] = object_type
    return schedule_types


def resolve_schedule_name(
    schedule_types: Dict[str, str],
    schedule_name: str,
) -> Optional[str]:
    """Resol les referències de planificació amb noms d'estil EnergyPlus que no distingeixen entre majúscules i minúscules."""
    if not schedule_name:
        return None
    if schedule_name in schedule_types:
        return schedule_name

    target_casefold = schedule_name.casefold()
    for actual_name in schedule_types.keys():
        if actual_name.casefold() == target_casefold:
            return actual_name

    target_normalized = normalize_token(schedule_name)
    for actual_name in schedule_types.keys():
        if normalize_token(actual_name) == target_normalized:
            return actual_name

    return None


def _register_thermostat_candidate(
    detected: Dict[Tuple[str, str], Dict[str, Any]],
    schedule_types: Dict[str, str],
    schedule_name: str,
    category: str,
    zone_name: Optional[str],
) -> None:
    """Registra una planificació de termòstat com a entrada de controlador candidat si encara no s'ha fet un seguiment.

    Crea una nova entrada a `detected` per a la clau donada (categoria, schedule_name) si no hi ha,
    aleshores hi associa el nom de la zona.

    Paràmetres:
        detected (Dict): Registre de candidats acumulat clausurat per (categoria, schedule_name).
        schedule_types (Dict[str, str]): Mapeig de noms de planificació amb les seves cadenes del tipus de bloc.
        schedule_name (str): el nom del programa EnergyPlus per registrar-se.
        category (str): categoria de consigna, e.g. 'heating_setpoint' o 'cooling_setpoint'.
        zone_name (Optional[str]): Nom de la zona a associar amb aquest candidat.
    """
    resolved_schedule_name = resolve_schedule_name(schedule_types, schedule_name)
    if resolved_schedule_name is None:
        return
    key = (category, resolved_schedule_name)
    if key not in detected:
        detected[key] = {
            "category": category,
            "schedule_name": resolved_schedule_name,
            "zones": set(),
            "references": set(),
            "source_kind": "thermostat",
            "element_type": schedule_types[resolved_schedule_name],
        }
    if zone_name:
        detected[key]["zones"].add(zone_name)
        detected[key]["references"].add(zone_name)


def extract_thermostat_schedule_candidates(
    building_data: Dict[str, Any],
    schedule_types: Dict[str, str],
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Detecta programes de termòstat implícits basats en els punts de consigna Dual i Single del model.

    Paràmetres:
        building_data (Dict[str, Any]): les dades epJSON carregades.
        schedule_types (Dict[str, str]): una assignació de noms de planificació a tipus de bloc de planificació.

    Retorna:
        Tuple[List[str], List[Dict[str, Any]]]: una tupla que conté una llista de detectats
        zones del termòstat i una llista de diccionaris estructurats amb detalls dels actuadors candidats.
    """
    thermostat_controls = building_data.get("ZoneControl:Thermostat", {})
    dual_setpoints = building_data.get("ThermostatSetpoint:DualSetpoint", {})
    single_heating = building_data.get("ThermostatSetpoint:SingleHeating", {})
    single_cooling = building_data.get("ThermostatSetpoint:SingleCooling", {})

    thermostat_zones: List[str] = []
    detected: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for _, thermostat_spec in thermostat_controls.items():
        zone_name = thermostat_spec.get("zone_or_zonelist_name") or thermostat_spec.get("zone_name")
        if zone_name and zone_name not in thermostat_zones:
            thermostat_zones.append(zone_name)

        # EnergyPlus desa fins a cinc controls numerats per termòstat; cal revisar-los tots
        # perquè un mateix objecte pot combinar consignes Dual i Single.
        for control_index in range(1, 6):
            object_type = thermostat_spec.get(f"control_{control_index}_object_type")
            object_name = thermostat_spec.get(f"control_{control_index}_name")
            if not object_type or not object_name:
                continue

            if object_type == "ThermostatSetpoint:DualSetpoint":
                dual_spec = dual_setpoints.get(object_name, {})
                _register_thermostat_candidate(
                    detected,
                    schedule_types,
                    dual_spec.get("heating_setpoint_temperature_schedule_name", ""),
                    "heating_setpoint",
                    zone_name,
                )
                _register_thermostat_candidate(
                    detected,
                    schedule_types,
                    dual_spec.get("cooling_setpoint_temperature_schedule_name", ""),
                    "cooling_setpoint",
                    zone_name,
                )
            elif object_type == "ThermostatSetpoint:SingleHeating":
                single_spec = single_heating.get(object_name, {})
                _register_thermostat_candidate(
                    detected,
                    schedule_types,
                    single_spec.get("setpoint_temperature_schedule_name", ""),
                    "heating_setpoint",
                    zone_name,
                )
            elif object_type == "ThermostatSetpoint:SingleCooling":
                single_spec = single_cooling.get(object_name, {})
                _register_thermostat_candidate(
                    detected,
                    schedule_types,
                    single_spec.get("setpoint_temperature_schedule_name", ""),
                    "cooling_setpoint",
                    zone_name,
                )

    ordered_candidates: List[Dict[str, Any]] = []
    # Ordenem els candidats perquè la UI i els YAML generats siguin estables entre execucions.
    for key in sorted(detected.keys(), key=lambda item: (item[0], item[1].lower())):
        candidate = detected[key]
        ordered_candidates.append(
            {
                "schedule_name": candidate["schedule_name"],
                "category": candidate["category"],
                "zones": tuple(sorted(candidate["zones"])),
                "references": tuple(sorted(candidate["references"])),
                "source_kind": candidate["source_kind"],
                "element_type": candidate["element_type"],
            }
        )

    return thermostat_zones, ordered_candidates


def _collect_schedule_references_from_value(
    value: Any,
    schedule_types: Dict[str, str],
) -> List[str]:
    """Recolliu referències de calendari a partir del valor."""
    references: List[str] = []
    if isinstance(value, str):
        resolved_schedule_name = resolve_schedule_name(schedule_types, value)
        if resolved_schedule_name is not None:
            references.append(resolved_schedule_name)
    elif isinstance(value, dict):
        for nested_value in value.values():
            references.extend(_collect_schedule_references_from_value(nested_value, schedule_types))
    elif isinstance(value, list):
        for nested_value in value:
            references.extend(_collect_schedule_references_from_value(nested_value, schedule_types))
    return references


def extract_schedule_numeric_values(
    building_data: Dict[str, Any],
    schedule_types: Dict[str, str],
    schedule_name: str,
    visited: Optional[set[str]] = None,
) -> List[float]:
    """Extreu valors numèrics de planificació."""
    if visited is None:
        visited = set()

    # Les planificacions poden referenciar altres planificacions; aquest conjunt evita bucles
    # quan EnergyPlus encadena objectes Schedule:* de manera recursiva.
    resolved_schedule_name = resolve_schedule_name(schedule_types, schedule_name)
    if resolved_schedule_name is None:
        return []
    if resolved_schedule_name in visited:
        return []

    object_type = schedule_types.get(resolved_schedule_name)
    if object_type is None:
        return []

    schedule_objects = building_data.get(object_type, {})
    schedule_spec = schedule_objects.get(resolved_schedule_name)
    if not isinstance(schedule_spec, dict):
        return []

    visited.add(resolved_schedule_name)

    if object_type == "Schedule:Compact":
        values: List[float] = []
        for entry in schedule_spec.get("data", []):
            if not isinstance(entry, dict):
                continue
            field_value = entry.get("field")
            if isinstance(field_value, (int, float)) and not isinstance(field_value, bool):
                values.append(float(field_value))
        return values

    if object_type == "Schedule:Constant":
        values = []
        for key, value in schedule_spec.items():
            if key == "schedule_type_limits_name":
                continue
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                values.append(float(value))
        return values

    if object_type == "Schedule:Day:Hourly":
        values = []
        for key, value in schedule_spec.items():
            if key.lower().startswith("hour_") and isinstance(value, (int, float)) and not isinstance(value, bool):
                values.append(float(value))
        return values

    if object_type in {"Schedule:Year", "Schedule:Week:Daily", "Schedule:Week:Compact"}:
        values = []
        for nested_schedule_name in _collect_schedule_references_from_value(schedule_spec, schedule_types):
            values.extend(
                extract_schedule_numeric_values(
                    building_data,
                    schedule_types,
                    nested_schedule_name,
                    visited,
                )
            )
        return values

    return []


def extract_schedule_value_range(
    building_data: Dict[str, Any],
    schedule_types: Dict[str, str],
    schedule_name: str,
) -> Tuple[Optional[float], Optional[float]]:
    """Extreu l'interval de valors de la planificació."""
    values = extract_schedule_numeric_values(building_data, schedule_types, schedule_name)
    if not values:
        return None, None
    return min(values), max(values)


def summarize_references(prefix: str, references: Sequence[str]) -> str:
    """Summarize references."""
    cleaned = [reference for reference in references if reference]
    if not cleaned:
        return prefix
    if len(cleaned) == 1:
        return f"{prefix}: {cleaned[0]}"
    if len(cleaned) == 2:
        return f"{prefix}: {cleaned[0]}, {cleaned[1]}"
    return f"{prefix}: {cleaned[0]}, {cleaned[1]} +{len(cleaned) - 2}"


def extract_scheduled_hvac_controller_candidates(
    building_data: Dict[str, Any],
    schedule_types: Dict[str, str],
    excluded_schedule_names: Sequence[str],
) -> List[Dict[str, Any]]:
    """Identifica els punts de consigna programats i els gestors de disponibilitat a partir del model d'edifici que
    encara no es gestionen com a punts de consigna explícits del termòstat.

    Paràmetres:
        building_data (Dict[str, Any]): les dades epJSON carregades.
        schedule_types (Dict[str, str]): una assignació de noms de planificació a tipus de planificació.
        excluded_schedule_names (Sequence[str]): Noms de les planificacions per ignorar
        (normalment ja està assignat als termòstats).

    Retorna:
        List[Dict[str, Any]]: una llista de diccionaris genèrics HVAC candidats.
    """
    excluded = {normalize_token(name) for name in excluded_schedule_names}
    detected: Dict[Tuple[str, str], Dict[str, Any]] = {}

    scheduled_setpoints = building_data.get("SetpointManager:Scheduled", {})
    for _, manager_spec in scheduled_setpoints.items():
        if not isinstance(manager_spec, dict):
            continue

        schedule_name = resolve_schedule_name(schedule_types, manager_spec.get("schedule_name", ""))
        if schedule_name is None:
            continue
        if normalize_token(schedule_name) in excluded:
            continue
        if normalize_token(str(manager_spec.get("control_variable", ""))) != "temperature":
            continue

        # Aquests setpoints no pengen directament del termòstat, però també poden ser
        # bons actuadors RL si EnergyPlus els controla amb una schedule editable.
        key = ("scheduled_temperature_setpoint", schedule_name)
        if key not in detected:
            detected[key] = {
                "category": "scheduled_temperature_setpoint",
                "schedule_name": schedule_name,
                "zones": set(),
                "references": set(),
                "source_kind": "setpoint_manager",
                "element_type": schedule_types[schedule_name],
            }

        setpoint_target = manager_spec.get("setpoint_node_or_nodelist_name")
        if isinstance(setpoint_target, str) and setpoint_target:
            detected[key]["references"].add(setpoint_target)

    scheduled_availability = building_data.get("AvailabilityManager:Scheduled", {})
    for manager_name, manager_spec in scheduled_availability.items():
        if not isinstance(manager_spec, dict):
            continue

        schedule_name = resolve_schedule_name(schedule_types, manager_spec.get("schedule_name", ""))
        if schedule_name is None:
            continue
        if normalize_token(schedule_name) in excluded:
            continue

        key = ("availability", schedule_name)
        if key not in detected:
            detected[key] = {
                "category": "availability",
                "schedule_name": schedule_name,
                "zones": set(),
                "references": set(),
                "source_kind": "availability_manager",
                "element_type": schedule_types[schedule_name],
            }
        if manager_name:
            detected[key]["references"].add(manager_name)

    ordered_candidates: List[Dict[str, Any]] = []
    for key in sorted(detected.keys(), key=lambda item: (item[0], item[1].lower())):
        candidate = detected[key]
        ordered_candidates.append(
            {
                "schedule_name": candidate["schedule_name"],
                "category": candidate["category"],
                "zones": tuple(sorted(candidate["zones"])),
                "references": tuple(sorted(candidate["references"])),
                "source_kind": candidate["source_kind"],
                "element_type": candidate["element_type"],
            }
        )

    return ordered_candidates


def extract_storage_controller_candidates(
    building_data: Dict[str, Any],
    schedule_types: Dict[str, str],
    excluded_schedule_names: Sequence[str],
) -> List[Dict[str, Any]]:
    """Identifica els horaris de càrrega/descàrrega de la bateria que es poden exposar com a accions."""

    excluded = {normalize_token(name) for name in excluded_schedule_names}
    detected: Dict[Tuple[str, str], Dict[str, Any]] = {}

    controller_fields = (
        (
            "storage_charge_power_fraction_schedule_name",
            "battery_charge",
        ),
        (
            "storage_discharge_power_fraction_schedule_name",
            "battery_discharge",
        ),
    )

    for distribution_name, distribution_spec in building_data.get("ElectricLoadCenter:Distribution", {}).items():
        if not isinstance(distribution_spec, dict):
            continue

        # La distribució pot apuntar a un objecte Storage; guardem tots dos noms perquè
        # després la UI pugui explicar d'on surt cada actuador de bateria.
        storage_name = distribution_spec.get("electrical_storage_object_name")
        reference = distribution_name
        if storage_name:
            reference = f"{distribution_name} -> {storage_name}"

        for field_name, category in controller_fields:
            # EnergyPlus separa càrrega i descàrrega en camps diferents; els exposem com
            # actuadors diferents per no barrejar dues decisions físiques oposades.
            schedule_name = resolve_schedule_name(schedule_types, distribution_spec.get(field_name, ""))
            if schedule_name is None:
                continue
            if normalize_token(schedule_name) in excluded:
                continue

            key = (category, schedule_name)
            if key not in detected:
                detected[key] = {
                    "category": category,
                    "schedule_name": schedule_name,
                    "zones": set(),
                    "references": set(),
                    "source_kind": "electric_storage",
                    "element_type": schedule_types[schedule_name],
                }
            detected[key]["references"].add(reference)

    ordered_candidates: List[Dict[str, Any]] = []
    for key in sorted(detected.keys(), key=lambda item: (item[0], item[1].lower())):
        candidate = detected[key]
        ordered_candidates.append(
            {
                "schedule_name": candidate["schedule_name"],
                "category": candidate["category"],
                "zones": tuple(sorted(candidate["zones"])),
                "references": tuple(sorted(candidate["references"])),
                "source_kind": candidate["source_kind"],
                "element_type": candidate["element_type"],
            }
        )

    return ordered_candidates


def parse_available_handlers(available_data: str) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str]], List[str]]:
    """Analitzar els controladors disponibles."""
    actuators: List[Tuple[str, str, str]] = []
    variables: List[Tuple[str, str]] = []
    meters: List[str] = []

    reader = csv.reader(io.StringIO(available_data or ""))
    for row in reader:
        cleaned = [cell.strip().strip(";") for cell in row if cell is not None]
        if not cleaned:
            continue
        entry_type = cleaned[0]
        if entry_type == "Actuator" and len(cleaned) >= 4:
            actuators.append((cleaned[1], cleaned[2], cleaned[3]))
        elif entry_type == "OutputVariable" and len(cleaned) >= 3:
            variables.append((cleaned[1], cleaned[2]))
        elif entry_type == "OutputMeter" and len(cleaned) >= 2:
            meters.append(cleaned[1])

    return actuators, variables, meters


def probe_available_handlers(building_path: Path, weather_path: Path) -> Tuple[bool, str, Optional[str]]:
    """Inicia un bucle mínim Sinergym per extreure exactament quins controladors EnergyPlus estan disponibles.

    Paràmetres:
        building_path (Path): camí cap al model d'edifici IDF o epJSON.
        weather_path (Path): camí cap al fitxer meteorològic EPW.

    Retorna:
        Tuple[bool, str, Optional[str]]: una tupla que conté un booleà d'èxit, un text csv de controladors sense processar i una cadena d'error si escau.
    """
    env: Optional[EplusEnv] = None
    try:
        env = EplusEnv(
            building_file=str(building_path),
            weather_files=str(weather_path),
            action_space=gym.spaces.Box(low=0, high=0, shape=(0,), dtype=np.float32),
            time_variables=DEFAULT_TIME_VARIABLES,
            variables={},
            meters={},
            actuators={},
            context={},
            reward=ProbeReward,
            reward_kwargs={},
            env_name=f"probe-{sanitize_identifier(building_path.stem, 'env')}",
            building_config={
                "runperiod": (1, 1, 1991, 1, 1, 1991),
                "timesteps_per_hour": 1,
            },
        )
        env.reset()
        return True, env.available_handlers or "", None
    except Exception as error:
        return False, "", str(error)
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                pass


def find_available_output_variable(
    available_variables: Sequence[Tuple[str, str]],
    variable_name: str,
    variable_key: str,
) -> Optional[Tuple[str, str]]:
    """Troba la variable de sortida disponible."""
    target_name = normalize_token(variable_name)
    target_key = normalize_token(variable_key)
    for actual_name, actual_key in available_variables:
        if normalize_token(actual_name) == target_name and normalize_token(actual_key) == target_key:
            return actual_name, actual_key
    return None


def find_available_meter(
    available_meters: Sequence[str],
    meter_name: str,
) -> Optional[str]:
    """Troba el comptador disponible."""
    target_name = normalize_token(meter_name)
    for actual_name in available_meters:
        if normalize_token(actual_name) == target_name:
            return actual_name
    return None


def default_bounds_for_category(
    category: str,
    actuator_key: str,
    current_low: Optional[float],
    current_high: Optional[float],
) -> Tuple[float, float]:
    """Límits per defecte per a la categoria."""
    if category == "heating_setpoint":
        return 15.0, 22.5
    if category == "cooling_setpoint":
        return 22.5, 30.0
    if category == "availability":
        return 0.0, 1.0
    if category in {"battery_charge", "battery_discharge"}:
        return 0.0, 1.0
    if category == "scheduled_temperature_setpoint":
        if current_low is not None and current_high is not None:
            if abs(current_high - current_low) < 1e-6:
                margin = max(1.0, abs(current_low) * 0.05)
                return float(current_low - margin), float(current_high + margin)
            margin = max(0.5, (current_high - current_low) * 0.1)
            return float(current_low - margin), float(current_high + margin)
        return 15.0, 80.0
    return 0.0, 1.0


def build_actuator_label(category: str) -> str:
    """Crea una etiqueta llegible per a una categoria d'actuador."""
    if category == "heating_setpoint":
        return "Setpoint de calefacció"
    if category == "cooling_setpoint":
        return "Setpoint de refrigeració"
    if category == "availability":
        return "Disponibilitat HVAC"
    if category == "scheduled_temperature_setpoint":
        return "Setpoint de sistema HVAC"
    if category == "battery_charge":
        return "Càrrega de bateria"
    if category == "battery_discharge":
        return "Descàrrega de bateria"
    return "Control HVAC"


def _build_actuator_option(
    candidate: Dict[str, Any],
    building_data: Dict[str, Any],
    schedule_types: Dict[str, str],
) -> ActuatorOption:
    """Construeix un ActuatorOption escrit a partir d'un diccionari candidat en brut.

    Extreu l'interval de valors de la planificació de les dades de l'edifici i calcula sensiblement
    límits d'acció per defecte basats en la categoria de l'actuador.

    Paràmetres:
        candidate (Dict[str, Any]): Dicte de candidat en brut que conté schedule_name, categoria,
            zones, referències, camps element_type i source_kind.
        building_data (Dict[str, Any]): dades completes de l'edifici epJSON per a l'extracció de l'interval de planificació.
        schedule_types (Dict[str, str]): Assignació de noms de planificació a tipus de blocs de planificació.

    Retorna:
        ActuatorOption: una opció d'actuador estructurada i immutable preparada per a la representació de UI i
            configuració de l'entorn.
    """
    schedule_name = candidate["schedule_name"]
    category = candidate["category"]
    zones = tuple(candidate["zones"])
    references = tuple(candidate["references"])
    current_low, current_high = extract_schedule_value_range(
        building_data,
        schedule_types,
        schedule_name,
    )
    default_low, default_high = default_bounds_for_category(
        category,
        schedule_name,
        current_low,
        current_high,
    )
    if category in {"heating_setpoint", "cooling_setpoint"}:
        reference = summarize_references("Zones", zones)
    elif category == "scheduled_temperature_setpoint":
        reference = summarize_references("Nodes", references)
    elif category in {"battery_charge", "battery_discharge"}:
        reference = summarize_references("Bateria", references)
    else:
        reference = summarize_references("Sistemes", references)

    return ActuatorOption(
        option_id=f'{candidate["element_type"]}|Schedule Value|{schedule_name}',
        actuator_key=schedule_name,
        element_type=candidate["element_type"],
        value_type="Schedule Value",
        label=build_actuator_label(category),
        reference=reference,
        category=category,
        zones=zones,
        current_low=current_low,
        current_high=current_high,
        default_low=default_low,
        default_high=default_high,
    )


def build_training_analysis(
    building_path: Path,
    weather_path: Path,
    probe_handlers: bool = False,
) -> BuildingTrainingAnalysis:
    """Realitza una anàlisi completa d'un model d'edifici per extreure controladors HVAC entrenables.

    Paràmetres:
        building_path (Path): camí cap al model d'edifici.
        weather_path (Path): Camí al fitxer meteorològic per resoldre les restriccions de l'entorn.
        probe_handlers (bool, optional): Si True, un entorn de sonda Sinergym s'executa exactament
            determinar els components de sortida. El valor predeterminat és False.

    Retorna:
        BuildingTrainingAnalysis: una classe de dades estructurada que conté resultats de detecció per
        termòstats, variables, comptadors i actuadors.
    """
    building_data = load_building_json(building_path)
    schedule_types = extract_schedule_type_index(building_data)
    thermostat_zones, thermostat_candidates = extract_thermostat_schedule_candidates(
        building_data,
        schedule_types,
    )
    thermostat_schedule_names = [
        candidate["schedule_name"]
        for candidate in thermostat_candidates
    ]
    hvac_schedule_candidates = extract_scheduled_hvac_controller_candidates(
        building_data,
        schedule_types,
        thermostat_schedule_names,
    )
    storage_schedule_candidates = extract_storage_controller_candidates(
        building_data,
        schedule_types,
        thermostat_schedule_names,
    )

    if probe_handlers:
        probe_success, available_raw, probe_error = probe_available_handlers(building_path, weather_path)
    else:
        probe_success, available_raw, probe_error = False, "", None
    _, available_output_variables, available_meters = parse_available_handlers(available_raw)

    thermostat_actuators: List[ActuatorOption] = []
    used_schedule_keys: set[str] = set()
    for candidate in thermostat_candidates:
        option = _build_actuator_option(candidate, building_data, schedule_types)
        thermostat_actuators.append(option)
        used_schedule_keys.add(normalize_token(option.actuator_key))

    hvac_actuators: List[ActuatorOption] = []
    for candidate in [*hvac_schedule_candidates, *storage_schedule_candidates]:
        normalized_key = normalize_token(candidate["schedule_name"])
        if normalized_key in used_schedule_keys:
            continue
        hvac_actuators.append(_build_actuator_option(candidate, building_data, schedule_types))
        used_schedule_keys.add(normalized_key)

    return BuildingTrainingAnalysis(
        thermostat_zones=tuple(thermostat_zones),
        thermostat_actuators=tuple(thermostat_actuators),
        hvac_actuators=tuple(hvac_actuators),
        available_output_variables=tuple(available_output_variables),
        available_meters=tuple(available_meters),
        probe_success=probe_success,
        probe_error=probe_error,
    )
