"""Càlculs de KPI per als resums de resultats de BEMS-RL Studio.

Aquest mòdul deriva mètriques operatives compactes a partir de les observacions
normalitzades: desviacions de confort, consum HVAC, cost energètic i resums de
temperatura de zona.
"""

import re

import pandas as pd

from backend.grafics.comfort_scope import comfort_scope_label, derive_occupied_mask
from backend.grafics.observation_columns import (
    HVAC_POWER_COLUMN,
    normalize_observation_columns,
)


def _normalize_name(s: str) -> str:
    """Normalitza els noms de zona perquè coincideixin amb les columnes de manera més tolerant."""
    s = (s or "").lower()
    s = s.replace(" ", "_").replace("-", "_")
    return re.sub(r"[^a-z0-9_]+", "", s)


def _pick_zone_temperature_series(
    obs: pd.DataFrame,
    selected_zone: str | None,
) -> pd.Series | None:
    """Retorna la sèrie de temperatura interior utilitzada per les targetes KPI."""
    zone_temp_cols = [c for c in obs.columns if c.endswith("_air_temperature")]
    if zone_temp_cols:
        if not selected_zone or selected_zone == "All":
            return obs[zone_temp_cols].mean(axis=1)

        target = _normalize_name(selected_zone)
        cand_map = {
            _normalize_name(c[:-len("_air_temperature")]): c for c in zone_temp_cols
        }
        col = cand_map.get(target)
        if col is not None:
            return pd.to_numeric(obs[col], errors="coerce")
        for key, col in cand_map.items():
            if target in key or key in target:
                return pd.to_numeric(obs[col], errors="coerce")
        return obs[zone_temp_cols].mean(axis=1)

    if "air_temperature" in obs.columns:
        return pd.to_numeric(obs["air_temperature"], errors="coerce")

    return None


def _temperature_violation_frame(obs: pd.DataFrame, comfort_config=None) -> pd.DataFrame | None:
    """Retorna les observacions amb una infracció de confort alineada per registre."""
    if "temp_violation" in obs.columns:
        result = obs.copy()
        result["temp_violation"] = pd.to_numeric(result["temp_violation"], errors="coerce")
        return result

    try:
        from backend.grafics.comfort import _ensure_temp_violation_column

        with_violation = _ensure_temp_violation_column(obs, comfort_config)
    except Exception:
        return None

    if "temp_violation" not in with_violation.columns:
        return None
    with_violation = with_violation.copy()
    with_violation["temp_violation"] = pd.to_numeric(
        with_violation["temp_violation"],
        errors="coerce",
    )
    return with_violation


def compute_kpis(
    obs: pd.DataFrame,
    cost_hourly: pd.DataFrame | None,
    selected_zone: str | None = None,
    comfort_scope: str = "all",
    comfort_config=None,
):
    """Calcula les targetes KPI mostrades al panell i exportades a PDF.

    Els KPI de temperatura respecten la zona seleccionada. HVAC i els KPI de costos segueixen sent globals.
    La desviació de confort es mostra amb una etiqueta d'abast explícita per a hores ocupades
    les recompenses no es comparen amb una mètrica de totes les hores per accident.
    """
    obs = normalize_observation_columns(obs)
    kpis: dict[str, float | None] = {}

    tin_series = _pick_zone_temperature_series(obs, selected_zone)
    if tin_series is not None:
        # Si l'usuari ha triat una zona, els KPI de temperatura han de parlar només
        # d'aquella zona, no de la mitjana global de l'edifici.
        kpis["Avg Temp Interior (C)"] = round(tin_series.mean(), 2)
        kpis["Max Temp Interior (C)"] = round(tin_series.max(), 2)
        kpis["Min Temp Interior (C)"] = round(tin_series.min(), 2)
    else:
        if "air_temperature" not in obs.columns:
            zone_temp_cols = [c for c in obs.columns if c.endswith("_air_temperature")]
            tmp = obs[zone_temp_cols].mean(axis=1) if zone_temp_cols else None
        else:
            tmp = obs["air_temperature"]
        if tmp is not None:
            tmp = pd.to_numeric(tmp, errors="coerce")
            kpis["Avg Temp Interior (C)"] = round(tmp.mean(), 2)
            kpis["Max Temp Interior (C)"] = round(tmp.max(), 2)
            kpis["Min Temp Interior (C)"] = round(tmp.min(), 2)
        else:
            kpis["Avg Temp Interior (C)"] = None
            kpis["Max Temp Interior (C)"] = None
            kpis["Min Temp Interior (C)"] = None

    if HVAC_POWER_COLUMN in obs.columns:
        hvac = pd.to_numeric(obs[HVAC_POWER_COLUMN], errors="coerce")
        kpis["Avg HVAC Power (kW)"] = round(hvac.mean() / 1000, 2)
    else:
        kpis["Avg HVAC Power (kW)"] = None

    if cost_hourly is not None and "energy_cost_eur" in cost_hourly.columns:
        energy_cost = pd.to_numeric(cost_hourly["energy_cost_eur"], errors="coerce")
        kpis["Avg Energy Cost (EUR/h)"] = round(energy_cost.mean(), 2)
    else:
        kpis["Avg Energy Cost (EUR/h)"] = None

    violation_frame = _temperature_violation_frame(obs, comfort_config)
    primary_label = comfort_scope_label(comfort_scope)

    if violation_frame is None:
        kpis[f"Avg Temp Violation ({primary_label}, C)"] = None
        return kpis

    violation = violation_frame["temp_violation"]
    occupied_mask = derive_occupied_mask(violation_frame)

    # En rewards amb ocupació, comparar totes les hores amb hores ocupades pot portar a
    # conclusions falses. Per això calculem l'abast principal i deixem l'altre com a context.
    scoped_values = violation
    if comfort_scope == "occupied" and occupied_mask is not None:
        scoped_values = violation.loc[occupied_mask]
    scoped_values = scoped_values.dropna()
    scoped_mean = scoped_values.mean() if not scoped_values.empty else None
    kpis[f"Avg Temp Violation ({primary_label}, C)"] = (
        round(scoped_mean, 2) if scoped_mean is not None else None
    )

    if occupied_mask is not None:
        all_values = violation.dropna()
        occupied_values = violation.loc[occupied_mask].dropna()
        all_mean = all_values.mean() if not all_values.empty else None
        occupied_mean = occupied_values.mean() if not occupied_values.empty else None
        kpis["Occupied Samples (%)"] = round(float(occupied_mask.mean()) * 100.0, 2)

        if comfort_scope == "occupied":
            kpis["Avg Temp Violation (All Hours, C)"] = (
                round(all_mean, 2) if all_mean is not None else None
            )
        else:
            kpis["Avg Temp Violation (Occupied Hours, C)"] = (
                round(occupied_mean, 2) if occupied_mean is not None else None
            )

    return kpis
