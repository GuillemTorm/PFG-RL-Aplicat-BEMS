"""Conversions d'energia, preu i unitats de bateria per als gràfics."""

from __future__ import annotations

import pandas as pd

from backend.grafics.time_utils import _auto_scale_series

def _energy_price_series_eur_per_kwh(df: pd.DataFrame, col: str) -> pd.Series:
    """Preu de l'energia sèrie eur per kwh."""
    price = pd.to_numeric(df[col], errors="coerce")
    label = col.lower()
    if "eur_per_kwh" in label or "price_eur_per_kwh" in label or "energy_price_kwh" in label:
        return price

    median_abs = price.abs().dropna().median()
    if pd.notna(median_abs) and median_abs > 5:
        return price / 1000.0
    return price


def _energy_to_kwh(values: pd.Series, unit_kind: str, timestep_hours: float | None = None) -> pd.Series:
    """Energy to kwh."""
    numeric = pd.to_numeric(values, errors="coerce")
    if unit_kind == "kwh":
        return numeric
    if unit_kind == "joule":
        return numeric / 3_600_000.0
    if unit_kind == "watt":
        hours = 0.0 if timestep_hours is None else float(timestep_hours)
        return (numeric / 1000.0) * hours
    return numeric


def _battery_state_display_series(
    base: pd.DataFrame,
    state_col: str,
) -> tuple[pd.Series, str, str]:
    """Retorna la sèrie de visualització, la unitat i l'etiqueta per a les sortides de l'estat de la bateria."""
    raw = pd.to_numeric(base[state_col], errors="coerce")
    label = state_col.lower()

    if label in {"storage_battery_charge_state"}:
        # EnergyPlus ElectricLoadCenter: Emmagatzematge: Informes de l'estat de càrrega de la bateria en Ah.
        return raw, "Ah", "Battery Charge State"

    if (
        "fraction" in label
        or "soc" in label
        or label in {"battery_state_of_charge", "state_of_charge"}
    ):
        finite = raw.dropna()
        if not finite.empty and finite.abs().max() <= 1.5:
            return raw * 100.0, "%", "Battery State of Charge"
        return raw, "%", "Battery State of Charge"

    if label in {"battery_charge_state", "storage_charge_state", "electric_storage_charge_state"}:
        # EnergyPlus ElectricLoadCenter: Emmagatzematge: estat de càrrega dels informes simples en J.
        return raw / 3_600_000.0, "kWh", "Battery Stored Energy"

    finite_abs = raw.abs().dropna()
    if not finite_abs.empty and finite_abs.median() > 1e5:
        return raw / 3_600_000.0, "kWh", "Battery Stored Energy"

    scaled, suffix = _auto_scale_series(raw)
    unit = f"raw {suffix}".strip() if suffix else "raw"
    return scaled, unit, "Battery State"
