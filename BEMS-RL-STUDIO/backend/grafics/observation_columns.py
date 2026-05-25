"""Utilitats de normalització de columnes per a fitxers d'observació Sinergym.

Els entorns Sinergym i les configuracions personalitzades poden emetre comptadors equivalents
sota diferents noms o unitats. Aquest mòdul centralitza els àlies, HVAC energia
conversió i creació de columnes normalitzades perquè tots els gràfics llegeixin igual
camps canònics.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

HVAC_POWER_COLUMN = "HVAC_electricity_demand_rate"
ENERGY_COST_COLUMN = "energy_cost"
JOULES_PER_KWH = 3_600_000.0

HVAC_ENERGY_METER_COLUMNS = (
    "total_electricity_hvac",
    "total_electricity_HVAC",
    "Electricity:HVAC",
    "electricity_hvac",
)

DETAILED_HVAC_METER_COLUMNS = {
    "natural_gas_hvac": (
        "NaturalGas:HVAC",
        "natural_gas_hvac",
        "naturalgas_hvac",
    ),
    "heating_electricity": (
        "Heating:Electricity",
        "heating_electricity",
    ),
    "cooling_electricity": (
        "Cooling:Electricity",
        "cooling_electricity",
    ),
    "fans_electricity": (
        "Fans:Electricity",
        "fans_electricity",
    ),
    "pumps_electricity": (
        "Pumps:Electricity",
        "pumps_electricity",
    ),
    "heat_rejection_electricity": (
        "HeatRejection:Electricity",
        "heat_rejection_electricity",
    ),
    "humidifier_electricity": (
        "Humidifier:Electricity",
        "Humidification:Electricity",
        "humidifier_electricity",
        "humidification_electricity",
    ),
    "heat_recovery_electricity": (
        "HeatRecovery:Electricity",
        "heat_recovery_electricity",
    ),
}

DETAILED_HVAC_METER_LABELS = {
    "natural_gas_hvac": "Natural Gas HVAC",
    "heating_electricity": "Heating Electricity",
    "cooling_electricity": "Cooling Electricity",
    "fans_electricity": "Fans Electricity",
    "pumps_electricity": "Pumps Electricity",
    "heat_rejection_electricity": "Heat Rejection Electricity",
    "humidifier_electricity": "Humidifier Electricity",
    "heat_recovery_electricity": "Heat Recovery Electricity",
}

ELECTRIC_HVAC_METER_ALIASES = (
    "heating_electricity",
    "cooling_electricity",
    "fans_electricity",
    "pumps_electricity",
    "heat_rejection_electricity",
    "humidifier_electricity",
    "heat_recovery_electricity",
)

DETAILED_HVAC_METER_KWH_COLUMNS = {
    alias: f"{alias}_kwh"
    for alias in DETAILED_HVAC_METER_COLUMNS
}

FALLBACK_ELECTRICITY_METER_COLUMNS = (
    "total_electricity_facility",
    "total_electricity_building",
)

_COLUMN_ALIASES = {
    HVAC_POWER_COLUMN: (
        HVAC_POWER_COLUMN,
        "HVAC_elèctricity_demand_rate",
        "hvac_power",
        "HVAC_power",
        "hvac_load",
    ),
    ENERGY_COST_COLUMN: (
        ENERGY_COST_COLUMN,
        "electricity_cost",
        "elèctricity_cost",
    ),
}

_COLUMN_ALIASES.update(
    {
        canonical: (canonical, *aliases)
        for canonical, aliases in DETAILED_HVAC_METER_COLUMNS.items()
    }
)


def find_first_available_column(
    columns: Iterable[str], candidates: Iterable[str]
) -> str | None:
    """Retorna la primera columna disponible dins la llista de candidats."""
    available = set(columns)
    for candidate in candidates:
        if candidate in available:
            return candidate
    return None


def normalize_observation_columns(obs: pd.DataFrame) -> pd.DataFrame:
    """Normalitza les columnes d'observació."""
    normalized = obs.copy()
    for canonical, aliases in _COLUMN_ALIASES.items():
        if canonical in normalized.columns:
            continue
        alias = find_first_available_column(normalized.columns, aliases)
        if alias and alias != canonical:
            normalized[canonical] = normalized[alias]
    return normalized


def find_hvac_consumption_source(columns: Iterable[str]) -> tuple[str, str] | None:
    """Retorna la millor font de consum HVAC i el seu tipus d'unitat.

    EnergyPlus els comptadors informen l'energia per pas de temps en Joules, mentre que el
    La variable de sortida de la taxa de demanda informa de la potència en watts.
    """
    available = set(columns)
    lower_lookup = {column.lower(): column for column in columns}
    for column in HVAC_ENERGY_METER_COLUMNS:
        if column in available:
            return column, "joule"
        actual_column = lower_lookup.get(column.lower())
        if actual_column is not None:
            return actual_column, "joule"
    if HVAC_POWER_COLUMN in available:
        return HVAC_POWER_COLUMN, "watt"
    actual_power_column = lower_lookup.get(HVAC_POWER_COLUMN.lower())
    if actual_power_column is not None:
        return actual_power_column, "watt"
    for column in FALLBACK_ELECTRICITY_METER_COLUMNS:
        if column in available:
            return column, "joule"
        actual_column = lower_lookup.get(column.lower())
        if actual_column is not None:
            return actual_column, "joule"
    return None


def convert_hvac_source_to_kwh(
    values: pd.Series,
    unit_kind: str,
    timestep_hours: float | None = None,
) -> pd.Series:
    """Converteix la font de consum HVAC a kWh."""
    numeric = pd.to_numeric(values, errors="coerce")
    if unit_kind == "joule":
        return numeric / JOULES_PER_KWH
    if unit_kind == "watt":
        hours = 0.0 if timestep_hours is None else float(timestep_hours)
        return (numeric / 1000.0) * hours
    return numeric


def add_meter_kwh_columns(obs: pd.DataFrame) -> pd.DataFrame:
    """Afegeix columnes derivades de kWh per a les sortides conegudes del comptador EnergyPlus en Joules."""
    enriched = obs.copy()
    for meter_alias, kwh_column in DETAILED_HVAC_METER_KWH_COLUMNS.items():
        if meter_alias not in enriched.columns or kwh_column in enriched.columns:
            continue
        enriched[kwh_column] = convert_hvac_source_to_kwh(
            enriched[meter_alias],
            "joule",
        )
    return enriched
