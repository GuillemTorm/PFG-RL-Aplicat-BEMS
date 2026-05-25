"""Agrega les dades d'observació i progrés en mètriques preparades per a gràfics.

Les funcions aquí converteixen la sortida en brut Sinergym en mensual, per hora i
DataFrames orientats a la comoditat consumits pel panell de resultats, Plotly builders
i informes exportats.
"""

import numpy as np
import pandas as pd
from typing import Optional

from backend.grafics.observation_columns import (
    ENERGY_COST_COLUMN,
    HVAC_POWER_COLUMN,
    convert_hvac_source_to_kwh,
    find_hvac_consumption_source,
    normalize_observation_columns,
)
from backend.grafics.time_utils import _infer_timestep_hours, sanitize_observation_time_columns


def _price_to_eur_per_kwh(values: pd.Series) -> pd.Series:
    """Normalitza els valors dels preus de l'electricitat a EUR/kWh quan semblen ser EUR/MWh."""
    price = pd.to_numeric(values, errors="coerce")
    median_abs = price.abs().dropna().median()
    if pd.notna(median_abs) and median_abs > 5:
        return price / 1000.0
    return price


def compute_metrics(progress: pd.DataFrame, obs: pd.DataFrame, yaml_cfg: Optional[dict] = None) -> dict:
    """
    Calcula tots els DataFrames agregats per a figures,
    validant contra les dades disponibles i opcionalment el fitxer YAML.
    """
    obs = sanitize_observation_time_columns(normalize_observation_columns(obs.copy()))

    # Els CSV poden venir amb timestamp/datetime o amb columnes ja separades. Normalitzem
    # month/hour aquí perquè totes les figures de resultats puguin reutilitzar el mateix output.
    if 'month' not in obs.columns:
        if 'timestamp' in obs.columns:
            obs['timestamp'] = pd.to_datetime(obs['timestamp'])
            obs['month'] = obs['timestamp'].dt.month
        elif 'datetime' in obs.columns:
            obs['datetime'] = pd.to_datetime(obs['datetime'])
            obs['month'] = obs['datetime'].dt.month
        else:
            raise ValueError("La columna 'month' no existeix ni es pot derivar.")
    if 'hour' not in obs.columns:
        if 'timestamp' in obs.columns:
            obs['timestamp'] = pd.to_datetime(obs['timestamp'])
            obs['hour'] = obs['timestamp'].dt.hour
        elif 'datetime' in obs.columns:
            obs['datetime'] = pd.to_datetime(obs['datetime'])
            obs['hour'] = obs['datetime'].dt.hour
        else:
            raise ValueError("La columna 'hour' no existeix ni es pot derivar.")

    available = set(obs.columns)

    # Si el CSV és multizona i no porta air_temperature global, fem una mitjana simple
    # només com a fallback per a gràfics globals.
    if 'air_temperature' not in available:
        zone_temp_cols = [c for c in available if c.endswith('_air_temperature')]
        if zone_temp_cols:
            obs['air_temperature'] = obs[zone_temp_cols].mean(axis=1)
            available.add('air_temperature')

    if HVAC_POWER_COLUMN not in available:
        for cand in ('hvac_power', 'HVAC_power', 'hvac_load'):
            if cand in available:
                obs[HVAC_POWER_COLUMN] = obs[cand]
                available.add(HVAC_POWER_COLUMN)
                break

    if 'temp_violation' not in available and 'air_temperature' in available:
        from backend.grafics.comfort import _ensure_temp_violation_column

        obs = _ensure_temp_violation_column(obs, yaml_cfg)
        available.add('temp_violation')

    bins = 12
    if len(progress) > 0 and 'mean_reward' in progress.columns:
        # progress.csv no sempre té calendari real; repartim els punts en 12 blocs per
        # tenir una lectura mensual aproximada sense inventar dates.
        progress = progress.copy()
        progress['mean_reward'] = pd.to_numeric(progress['mean_reward'], errors='coerce')
        progress['month_bin'] = (np.arange(len(progress)) * bins // len(progress)) + 1
        monthly_reward = (
            progress.groupby('month_bin')['mean_reward']
                    .mean()
                    .reset_index(name='mean_reward')
        )
        monthly_reward['month'] = monthly_reward['month_bin'].astype(int)
    else:
        monthly_reward = pd.DataFrame({'month': range(1, bins + 1), 'mean_reward': [0] * bins})

    hourly_all = obs.groupby('hour').mean(numeric_only=True).reset_index()
    winter = obs[obs['month'].isin([12, 1, 2])].groupby('hour').mean(numeric_only=True).reset_index()
    summer = obs[obs['month'].isin([6, 7, 8])].groupby('hour').mean(numeric_only=True).reset_index()
    monthly_obs = (
        obs.groupby('month').mean(numeric_only=True)
           .reindex(index=range(1, 13), fill_value=0)
           .reset_index()
    )

    step_hours = _infer_timestep_hours(obs)
    hvac_source = find_hvac_consumption_source(obs.columns)
    if hvac_source is not None:
        # Aquí unifiquem W, J o meters ja en kWh. La resta del dashboard treballa sempre
        # amb aquesta columna normalitzada.
        hvac_col, hvac_unit = hvac_source
        obs["hvac_consumption_kwh"] = convert_hvac_source_to_kwh(
            obs[hvac_col],
            hvac_unit,
            step_hours,
        )
        available.add("hvac_consumption_kwh")

    cost_hourly = cost_monthly = None
    if ENERGY_COST_COLUMN in available and 'hvac_consumption_kwh' in available:
        obs['energy_price_kwh'] = _price_to_eur_per_kwh(obs[ENERGY_COST_COLUMN])
        obs['energy_cost_eur'] = obs['hvac_consumption_kwh'] * obs['energy_price_kwh']
        cost_hourly = obs.groupby('hour')['energy_cost_eur'].sum().reset_index()
        cost_monthly = (
            obs.groupby('month')['energy_cost_eur']
               .sum()
               .reindex(index=range(1, 13), fill_value=0)
               .reset_index()
        )

    violation_hourly = eps_winter = eps_summer = season_line = None
    if 'temp_violation' in available:
        # Separem hivern/estiu perquè les consignes de confort poden ser diferents i la
        # mitjana anual amagaria bastant el problema.
        violation_hourly = obs.groupby('hour')['temp_violation'].mean().reset_index(name='mean_violation')
        eps_winter = obs[obs['month'].isin([12, 1, 2])].groupby('hour')['temp_violation'].mean().reset_index(name='winter_violation')
        eps_summer = obs[obs['month'].isin([6, 7, 8])].groupby('hour')['temp_violation'].mean().reset_index(name='summer_violation')
        season_line = pd.merge(eps_winter, eps_summer, on='hour', how='outer').fillna(0)

    pivot_violation = None
    if 'temp_violation' in available:
        pivot_violation = (
            obs.groupby(['month', 'hour'])['temp_violation']
               .mean()
               .unstack(fill_value=0)
               .reindex(index=range(1, 13), fill_value=0)
        )

    pivot_consumption = None
    if 'hvac_consumption_kwh' in available:
        pivot_consumption = (
            obs.groupby(['month', 'hour'])['hvac_consumption_kwh']
               .sum()
               .unstack(fill_value=0)
               .reindex(index=range(1, 13), fill_value=0)
        )

    return {
        'monthly_reward': monthly_reward,
        'hourly_all': hourly_all,
        'winter': winter,
        'summer': summer,
        'monthly_obs': monthly_obs,
        'cost_hourly': cost_hourly,
        'cost_monthly': cost_monthly,
        'violation_hourly': violation_hourly,
        'eps_winter': eps_winter,
        'eps_summer': eps_summer,
        'season_line': season_line,
        'pivot_violation': pivot_violation,
        'pivot_consumption': pivot_consumption
    }
