"""Detecció de columnes disponibles per construir les figures del panell."""

from __future__ import annotations

import pandas as pd

def _ensure_air_temperature(df: pd.DataFrame) -> pd.DataFrame:
    """Assegura 'air_temperature'; si no hi és, fa la mitjana de columnes *_air_temperature."""
    dfc = df.copy()
    if "air_temperature" not in dfc.columns:
        zone_cols = [c for c in dfc.columns if c.endswith("_air_temperature")]
        if zone_cols:
            dfc["air_temperature"] = dfc[zone_cols].mean(axis=1)
    return dfc


def _find_first_present_column(columns, candidates) -> str | None:
    """Troba la primera columna disponible."""
    available = set(columns)
    for candidate in candidates:
        if candidate in available:
            return candidate

    lower_lookup = {str(column).lower(): column for column in columns}
    for candidate in candidates:
        actual = lower_lookup.get(str(candidate).lower())
        if actual is not None:
            return actual
    return None


_BATTERY_STATE_COLUMNS = (
    "battery_charge_state",
    "storage_charge_state",
    "electric_storage_charge_state",
    "storage_battery_charge_state",
    "storage_battery_charge_fraction",
    "battery_charge_fraction",
    "battery_state_of_charge",
    "storage_battery_soc",
    "battery_soc",
    "state_of_charge",
)

_BATTERY_CHARGE_POWER_COLUMNS = (
    "storage_charge_power",
    "battery_charge_power",
    "battery_charge_rate",
)

_BATTERY_DISCHARGE_POWER_COLUMNS = (
    "storage_discharge_power",
    "battery_discharge_power",
    "battery_discharge_rate",
)

_BATTERY_DISCHARGE_ENERGY_COLUMNS = (
    "storage_discharge_energy",
    "battery_discharge_energy",
)

_GRID_POWER_COLUMNS = (
    "facility_net_purchased_electricity_rate",
    "facility_total_purchased_electricity_rate",
    "net_electricity_purchased",
    "grid_electricity_rate",
)

_GRID_ENERGY_COLUMNS = (
    "facility_net_purchased_electricity_energy",
    "facility_total_purchased_electricity_energy",
    "net_purchased_electricity_energy",
    "total_purchased_electricity_energy",
)

_GRID_KWH_COLUMNS = (
    "facility_net_purchased_electricity_kwh",
    "facility_total_purchased_electricity_kwh",
    "net_purchased_electricity_kwh",
    "total_purchased_electricity_kwh",
)

_ENERGY_PRICE_COLUMNS = (
    "energy_cost",
    "electricity_cost",
    "elèctricity_cost",
    "price_eur_per_kwh",
    "energy_price_kwh",
    "energy_cost_eur_per_kwh",
    "electricity_cost_eur_per_kwh",
)


def _find_battery_state_column(columns) -> str | None:
    """Cerca la columna d'estat de la bateria."""
    return _find_first_present_column(columns, _BATTERY_STATE_COLUMNS)


def _find_energy_price_column(columns) -> str | None:
    """Busca la columna del preu de l'energia."""
    return _find_first_present_column(columns, _ENERGY_PRICE_COLUMNS)
