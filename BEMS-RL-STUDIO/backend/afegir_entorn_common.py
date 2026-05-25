"""Constants, tipus i helpers compartits pel flux d'afegir entorns."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional, Tuple


FALLBACK_UPDATER_DIR = Path("/workspaces/sinergym/IDFVersionUpdater")
TRANSITION_DOWNLOAD_URL = (
    "https://github.com/NREL/EnergyPlus/releases/download/v24.1.0/"
    "EnergyPlus-24.1.0-9d7789a3ac-Linux-Ubuntu22.04-x86_64.tar.gz"
)
TARGET_EPLUS_VERSION = (24, 1)
ENERGYPLUS_SUBPROCESS_TIMEOUT_SECONDS = 300
ENV_VALIDATION_TIMEOUT_SECONDS = 180

DEFAULT_TIME_VARIABLES = ["month", "day_of_month", "hour"]
DEFAULT_WEATHER_VARIABILITY = {
    "Dry Bulb Temperature": [1.0, 0.0, 24.0],
}
STANDARD_WEATHER_VARIABLES = (
    ("Site Outdoor Air DryBulb Temperature", "outdoor_temperature", "Environment"),
    ("Site Outdoor Air Relative Humidity", "outdoor_humidity", "Environment"),
    ("Site Wind Speed", "wind_speed", "Environment"),
    ("Site Wind Direction", "wind_direction", "Environment"),
    ("Site Diffuse Solar Radiation Rate per Area", "diffuse_solar_radiation", "Environment"),
    ("Site Direct Solar Radiation Rate per Area", "direct_solar_radiation", "Environment"),
)
STANDARD_ZONE_VARIABLES = (
    ("Zone Thermostat Heating Setpoint Temperature", "htg_setpoint"),
    ("Zone Thermostat Cooling Setpoint Temperature", "clg_setpoint"),
    ("Zone Air Temperature", "air_temperature"),
    ("Zone Air Relative Humidity", "air_humidity"),
    ("Zone People Occupant Count", "people_occupant"),
)
ENERGY_VARIABLE_CANDIDATES = (
    ("Facility Total HVAC Electricity Demand Rate", "HVAC_electricity_demand_rate", "Whole Building"),
    ("Facility Total Electricity Demand Rate", "facility_electricity_demand_rate", "Whole Building"),
)
ENERGY_METER_CANDIDATES = (
    ("Electricity:HVAC", "total_electricity_hvac"),
    ("Electricity:Facility", "total_electricity_facility"),
    ("Electricity:Building", "total_electricity_building"),
)
DETAILED_HVAC_METER_CANDIDATES = (
    ("NaturalGas:HVAC", "natural_gas_hvac"),
    ("Heating:Electricity", "heating_electricity"),
    ("Cooling:Electricity", "cooling_electricity"),
    ("Fans:Electricity", "fans_electricity"),
    ("Pumps:Electricity", "pumps_electricity"),
    ("HeatRejection:Electricity", "heat_rejection_electricity"),
    ("Humidifier:Electricity", "humidifier_electricity"),
    ("HeatRecovery:Electricity", "heat_recovery_electricity"),
)


@dataclass(frozen=True)
class UpgradeResult:
    """Resultat d'un intent d'actualitzar una IDF a la versio suportada."""
    upgraded: bool
    final_version: Optional[Tuple[int, int]]
    failed_transition_version: Optional[Tuple[int, int]] = None


@dataclass(frozen=True)
class EnvironmentValidationResult:
    """Espais i observacio inicial retornats en validar un entorn registrat."""
    observation_space: object
    action_space: object
    initial_observation: object


@dataclass(frozen=True)
class ActuatorOption:
    """Opcio d'actuador candidata detectada en un model EnergyPlus."""
    option_id: str
    actuator_key: str
    element_type: str
    value_type: str
    label: str
    reference: str
    category: str
    zones: Tuple[str, ...]
    current_low: Optional[float]
    current_high: Optional[float]
    default_low: float
    default_high: float


@dataclass(frozen=True)
class BuildingTrainingAnalysis:
    """Resultat agregat de l'analisi d'un edifici per entrenament RL."""
    thermostat_zones: Tuple[str, ...]
    thermostat_actuators: Tuple[ActuatorOption, ...]
    hvac_actuators: Tuple[ActuatorOption, ...]
    available_output_variables: Tuple[Tuple[str, str], ...]
    available_meters: Tuple[str, ...]
    probe_success: bool
    probe_error: Optional[str] = None


def save_uploaded_bytes(target_path: Path, content: bytes) -> Path:
    """Desa bytes pujats per Streamlit a disc i retorna la ruta."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "wb") as file_handle:
        file_handle.write(content)
    return target_path


def sanitize_identifier(raw_value: str, fallback: str) -> str:
    """Neteja una cadena per utilitzar-la com a identificador segur."""
    sanitized = re.sub(r"[^a-zA-Z0-9]+", "_", (raw_value or "").strip().lower()).strip("_")
    return sanitized or fallback


def normalize_token(value: str) -> str:
    """Normalitza una cadena per fer comparacions flexibles."""
    normalized = (value or "").lower()
    normalized = normalized.replace("drybulb", "dry bulb")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def unique_identifier(base: str, used: set[str]) -> str:
    """Genera un identificador únic afegint un sufix incremental si cal."""
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate
