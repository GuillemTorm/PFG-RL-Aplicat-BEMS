"""Helpers Plotly comuns per als gràfics agregats del dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from backend.grafics.time_utils import (
    _canon_day_total_series,
    _hour_series,
    _infer_timestep_hours,
    _month_series,
    _raw_axis_data,
    _seasonal_marker_colors,
    _series_for_mode,
    filter_by_season,
)


def build_mode_scatter_trace(
    base: pd.DataFrame,
    column: str | None,
    mode: str,
    season: str,
    *,
    name: str,
    color: str,
    units: str = "",
    sign: float = 1.0,
    line_width: float = 2.4,
    marker_size: int = 6,
    trace_mode: str | None = None,
    hovertemplate: str | None = None,
    plain_hovertemplate: str | None = None,
    line_shape: str | None = None,
    fill: str | None = None,
    fillcolor: str | None = None,
    meta: str | None = None,
) -> go.Scatter | None:
    """Crea una traça scatter usant la mateixa agregació temporal que la resta de gràfics."""
    if column is None:
        return None
    data = _series_for_mode(base, column, mode, season, sign=sign)
    if data is None:
        return None

    x_values, y_values, hover, inferred_mode = data
    selected_mode = trace_mode or inferred_mode
    marker_color = (
        _seasonal_marker_colors(x_values, season, active_color=color)
        if mode == "month"
        else color
    )
    line = dict(color=color, width=line_width)
    if line_shape is not None:
        line["shape"] = line_shape

    trace = go.Scatter(
        x=x_values,
        y=y_values,
        mode=selected_mode,
        name=name,
        line=line,
        marker=dict(color=marker_color, size=marker_size),
        fill=fill,
        fillcolor=fillcolor,
        meta=meta,
    )
    if hover is not None:
        trace.hovertext = hover
        trace.hovertemplate = hovertemplate or _default_hovertemplate(units)
    elif plain_hovertemplate is not None or hovertemplate is not None:
        trace.hovertemplate = plain_hovertemplate or hovertemplate
    return trace


def add_mode_scatter_trace(
    fig: go.Figure,
    base: pd.DataFrame,
    column: str | None,
    mode: str,
    season: str,
    **kwargs,
) -> go.Scatter | None:
    """Afegeix una traça scatter agregada a una figura si la columna existeix."""
    trace = build_mode_scatter_trace(base, column, mode, season, **kwargs)
    if trace is not None:
        fig.add_trace(trace)
    return trace


def energy_series_for_mode(
    base: pd.DataFrame,
    column: str,
    mode: str,
    season: str,
    *,
    raw_hourly: bool = False,
) -> tuple[list, list, list | None] | None:
    """Retorna sèries d'energia kWh amb sumes coherents per mode temporal."""
    if column not in base.columns:
        return None

    if mode == "hour":
        df = filter_by_season(base, season)
        if df.empty:
            return None
        day_keys = pd.Index(df.index.floor("D"), name="day")
        hour_keys = pd.Index(_hour_series(df), name="hour")
        slots = df.groupby([day_keys, hour_keys])[column].sum()
        grouped = slots.groupby(level="hour").mean()
        x_values = list(range(24))
        return x_values, [grouped.get(hour, float("nan")) for hour in x_values], None

    if mode == "day":
        df = filter_by_season(base, season)
        if df.empty:
            return None
        return _canon_day_total_series(df, column)

    if mode == "month":
        df = base if season == "All" else filter_by_season(base, season)
        if df.empty:
            return None
        if isinstance(df.index, pd.DatetimeIndex):
            monthly = df.groupby([df.index.year, df.index.month])[column].sum()
            grouped = monthly.groupby(level=1).mean()
        else:
            grouped = df.groupby(_month_series(df))[column].sum()
        x_values = list(range(1, 13))
        return x_values, [grouped.get(month, float("nan")) for month in x_values], None

    if mode == "raw":
        df = filter_by_season(base, season)
        if df.empty:
            return None
        return raw_hourly_total_series(df, column) if raw_hourly else _raw_axis_data(df, column)

    return None


def add_energy_bar_trace(
    fig: go.Figure,
    base: pd.DataFrame,
    column: str,
    *,
    label: str,
    color: str,
    mode: str,
    season: str,
    hover_units: str = "kWh",
    raw_hourly: bool = False,
) -> go.Bar | None:
    """Afegeix barres d'energia agregades amb hover homogeni."""
    data = energy_series_for_mode(base, column, mode, season, raw_hourly=raw_hourly)
    if data is None:
        return None

    x_values, y_values, hover = data
    marker_color = (
        _seasonal_marker_colors(x_values, season, active_color=color)
        if mode == "month"
        else color
    )
    trace = go.Bar(
        x=x_values,
        y=y_values,
        name=label,
        marker=dict(color=marker_color, line=dict(color=color, width=0.5)),
    )
    if hover is not None:
        trace.hovertext = hover
        decimals = 4 if mode == "raw" and not raw_hourly else 2
        trace.hovertemplate = (
            f"%{{hovertext}}<br>%{{y:.{decimals}f}} {hover_units}<extra></extra>"
        )
    fig.add_trace(trace)
    return trace


def raw_hourly_total_series(df: pd.DataFrame, column: str) -> tuple[list, list, list]:
    """Agrupa una sèrie raw en totals horaris per evitar gràfics de barres massa densos."""
    values = pd.to_numeric(df[column], errors="coerce")

    if isinstance(df.index, pd.DatetimeIndex):
        hourly = values.resample("h").sum(min_count=1).dropna()
        x_values = list(range(1, len(hourly) + 1))
        hover = [stamp.strftime("%m-%d %H:00") for stamp in hourly.index]
        return x_values, hourly.to_list(), hover

    timestep_hours = _infer_timestep_hours(df)
    steps_per_hour = max(1, int(round(1.0 / timestep_hours))) if timestep_hours > 0 else 4
    groups = np.arange(len(values)) // steps_per_hour
    hourly = values.groupby(groups).sum(min_count=1).dropna()
    x_values = (hourly.index.to_numpy(dtype=int) + 1).tolist()
    hover = [f"Hour {hour}" for hour in x_values]
    return x_values, hourly.to_list(), hover


def energy_axis_title(mode: str, *, raw_title: str = "Consumption per Timestep (kWh)") -> str:
    """Retorna el títol Y habitual per a gràfics de consum energètic."""
    return {
        "hour": "Mean Hourly Consumption (kWh)",
        "day": "Daily Consumption (kWh)",
        "month": "Monthly Consumption (kWh)",
        "raw": raw_title,
    }.get(mode, "Consumption (kWh)")


def _default_hovertemplate(units: str) -> str:
    """Construeix el tooltip Plotly per defecte amb unitats opcionals."""
    if not units:
        return "%{hovertext}<br>%{y:.2f}<extra></extra>"
    return f"%{{hovertext}}<br>%{{y:.2f}} {units}<extra></extra>"
