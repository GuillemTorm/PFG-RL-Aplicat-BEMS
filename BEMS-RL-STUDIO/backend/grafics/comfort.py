"""Compliment de la comoditat i xifres d'incompliment de la temperatura."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from backend.grafics.column_utils import _ensure_air_temperature
from backend.grafics.comfort_scope import comfort_scope_label, filter_by_comfort_scope
from backend.grafics.style import STUDIO_CHART_COLORS, _apply_figure_theme
from backend.grafics.time_utils import (
    _apply_mode_xaxis,
    _ensure_datetime_index,
    _month_series,
    _raw_axis_data,
    _seasonal_marker_colors,
    _series_for_mode,
    filter_by_season,
)

DEFAULT_WINTER_COMFORT_RANGE = (20.0, 23.5)
DEFAULT_SUMMER_COMFORT_RANGE = (23.0, 26.0)
DEFAULT_SUMMER_START = (6, 1)
DEFAULT_SUMMER_FINAL = (9, 30)


def _violation_marker(color=None) -> dict:
    """Retorna el marcador comú de barres de violació tèrmica."""
    return dict(
        color=color or STUDIO_CHART_COLORS["violation"],
        line=dict(color=STUDIO_CHART_COLORS["violation_edge"], width=0.8),
    )


def _add_violation_bar(fig: go.Figure, *, x, y, name: str, color=None) -> None:
    """Afegeix una barra de violació amb el mateix estil visual."""
    fig.add_bar(
        x=x,
        y=y,
        name=name,
        marker=_violation_marker(color),
        meta="keep_color",
    )


def _extract_reward_kwargs(config) -> dict:
    """Extreu kwargs de recompensa."""
    if not isinstance(config, dict):
        return {}
    if any(
        key in config
        for key in (
            "range_comfort_winter",
            "range_comfort_summer",
            "summer_start",
            "summer_final",
        )
    ):
        return config
    reward_kwargs = config.get("reward_kwargs")
    if isinstance(reward_kwargs, dict):
        return reward_kwargs
    training_config = config.get("training_config")
    if isinstance(training_config, dict):
        reward_kwargs = training_config.get("reward_kwargs")
        if isinstance(reward_kwargs, dict):
            return reward_kwargs
    for value in config.values():
        if isinstance(value, dict):
            nested = _extract_reward_kwargs(value)
            if nested:
                return nested
    return {}


def _coerce_pair(value, default_pair):
    """Converteix una parella de valors."""
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        try:
            return float(value[0]), float(value[1])
        except (TypeError, ValueError):
            pass
    return default_pair


def _coerce_month_day(value, default_pair):
    """Converteix una parella de mes i dia."""
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        try:
            return int(value[0]), int(value[1])
        except (TypeError, ValueError):
            pass
    return default_pair


def _comfort_bounds_from_reward_kwargs(df: pd.DataFrame, comfort_config=None):
    """Retorna els límits de comoditat de reward_kwargs. Els punts de consigna del termòstat són controls,
    no són criteris de confort, de manera que aquí no s'utilitzen intencionadament.
    """
    reward_kwargs = _extract_reward_kwargs(comfort_config)
    winter_lower, winter_upper = _coerce_pair(
        reward_kwargs.get("range_comfort_winter"),
        DEFAULT_WINTER_COMFORT_RANGE,
    )
    summer_lower, summer_upper = _coerce_pair(
        reward_kwargs.get("range_comfort_summer"),
        DEFAULT_SUMMER_COMFORT_RANGE,
    )
    summer_start = _coerce_month_day(
        reward_kwargs.get("summer_start"),
        DEFAULT_SUMMER_START,
    )
    summer_final = _coerce_month_day(
        reward_kwargs.get("summer_final"),
        DEFAULT_SUMMER_FINAL,
    )

    months = _month_series(df).astype(int)
    if "day_of_month" in df.columns:
        days = pd.to_numeric(df["day_of_month"], errors="coerce").fillna(1).astype(int)
    elif isinstance(df.index, pd.DatetimeIndex):
        days = pd.Series(df.index.day, index=df.index).astype(int)
    else:
        days = pd.Series(1, index=df.index)

    current = months * 100 + days
    start_code = summer_start[0] * 100 + summer_start[1]
    final_code = summer_final[0] * 100 + summer_final[1]
    if start_code <= final_code:
        is_summer = (current >= start_code) & (current <= final_code)
    else:
        is_summer = (current >= start_code) | (current <= final_code)

    lower = np.where(is_summer, summer_lower, winter_lower)
    upper = np.where(is_summer, summer_upper, winter_upper)
    return pd.Series(lower, index=df.index), pd.Series(upper, index=df.index)


def _categorize_comfort(df: pd.DataFrame, comfort_config=None) -> pd.DataFrame:
    """
    Afegeix:
      - air_temperature (si cal)
      - month/hour (si cal)
      - comfort_cat: 'Massa fred' | 'En confort' | 'Massa calor'
    """
    base = _ensure_datetime_index(df).copy()
    if "month" not in base.columns:
        base["month"] = base.index.month
    if "hour" not in base.columns:
        base["hour"] = base.index.hour

    base = _ensure_air_temperature(base)  # crea 'air_temperature' si no existeix
    lower, upper = _comfort_bounds_from_reward_kwargs(base, comfort_config)

    if "air_temperature" not in base.columns:
        if "temp_violation" in base.columns:
            violation = pd.to_numeric(base["temp_violation"], errors="coerce")
            valid = violation.notna()
            in_comfort = valid & (violation <= 1e-9)
            cat = pd.Series(pd.NA, index=base.index, dtype="object")
            cat.loc[in_comfort] = "En confort"
            cat.loc[valid & ~in_comfort] = "Massa calor"
            base["comfort_cat"] = pd.Categorical(
                cat,
                categories=["Massa fred", "En confort", "Massa calor"],
                ordered=True,
            )
            return base
        base["comfort_cat"] = pd.Categorical(
            [np.nan] * len(base),
            categories=["Massa fred", "En confort", "Massa calor"],
            ordered=True,
        )
        return base

    t_in = pd.to_numeric(base["air_temperature"], errors="coerce")
    lower = pd.to_numeric(lower, errors="coerce")
    upper = pd.to_numeric(upper, errors="coerce")
    if "temp_violation" in base.columns:
        violation = pd.to_numeric(base["temp_violation"], errors="coerce")
    else:
        violation = np.maximum(lower - t_in, 0) + np.maximum(t_in - upper, 0)
        base["temp_violation"] = violation

    valid = violation.notna()
    in_comfort = valid & (violation <= 1e-9)
    cold = valid & (~in_comfort) & (t_in < lower)
    cat = pd.Series(pd.NA, index=base.index, dtype="object")
    cat.loc[in_comfort] = "En confort"
    cat.loc[cold] = "Massa fred"
    cat.loc[valid & ~in_comfort & ~cold] = "Massa calor"
    base["comfort_cat"] = pd.Categorical(
        cat, categories=["Massa fred", "En confort", "Massa calor"], ordered=True
    )
    return base


def _ensure_temp_violation_column(df: pd.DataFrame, comfort_config=None) -> pd.DataFrame:
    """Assegura una columna `temp_violation` per pas de temps.

    Utilitza el valor del monitor quan existeix. En cas contrari, deriva la violació de
    reward_kwargs rangs de comoditat, tornant als rangs predeterminats de Sinergym.
    Els punts de consigna del termòstat són controls i no s'utilitzen intencionadament aquí.
    """
    base = _ensure_datetime_index(df).copy()
    if "month" not in base.columns:
        base["month"] = base.index.month
    if "hour" not in base.columns:
        base["hour"] = base.index.hour
    base = _ensure_air_temperature(base)

    if "temp_violation" in base.columns:
        base["temp_violation"] = pd.to_numeric(base["temp_violation"], errors="coerce")
        return base

    if "air_temperature" not in base.columns:
        base["temp_violation"] = np.nan
        return base

    lower, upper = _comfort_bounds_from_reward_kwargs(base, comfort_config)
    t_in = pd.to_numeric(base["air_temperature"], errors="coerce")
    lower = pd.to_numeric(lower, errors="coerce")
    upper = pd.to_numeric(upper, errors="coerce")
    base["temp_violation"] = np.maximum(lower - t_in, 0) + np.maximum(t_in - upper, 0)
    return base


# Gràfic del percentatge d'hores en confort.
def make_comfort_compliance(
    obs: pd.DataFrame,
    mode: str,
    season: str,
    comfort_scope: str = "all",
    comfort_config=None,
) -> go.Figure:
    """Crea el gràfic de percentatge d'hores dins el rang de confort."""
    scoped_obs = filter_by_comfort_scope(obs, comfort_scope)
    scope_label = comfort_scope_label(comfort_scope)
    df = _categorize_comfort(scoped_obs, comfort_config)

    # Només apliquem filtre d’estació quan té sentit
    if mode in ("raw", "hour", "day"):
        df = filter_by_season(df, season)

    categories = ["Massa fred", "En confort", "Massa calor"]
    colors_map = {
        "Massa fred": STUDIO_CHART_COLORS["comfort_cold"],
        "En confort": STUDIO_CHART_COLORS["comfort_ok"],
        "Massa calor": STUDIO_CHART_COLORS["comfort_hot"],
    }

    if df.empty:
        return go.Figure()

    if mode == "raw":
        counts = df["comfort_cat"].value_counts().reindex(categories).fillna(0)
        fig = px.pie(values=counts.values, names=counts.index, hole=0.45,
                     title=f"% d’hores en confort – Donut ({season} | {scope_label})",
                     color=counts.index, color_discrete_map=colors_map)
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#ffffff", width=2)))
        fig.update_layout(legend_title_text="")
        return _apply_figure_theme(fig)

    # Agreguem en barres apilades per veure el repartiment de confort.
    if mode == "hour":
        idx = df["hour"].astype(int); x_title="Hora del dia"; x_order=list(range(24))
    elif mode == "day":
        df = df.copy(); df["__day__"] = df.index.floor("D").astype(str)
        idx = df["__day__"]; x_title="Dia"; x_order=None
    elif mode == "month":
        # IMPORTANT: en month NO fem filtre per estació
        df = _categorize_comfort(scoped_obs, comfort_config).copy()
        df["__month__"] = df.index.month
        idx = df["__month__"].astype(int); x_title="Mes"; x_order=list(range(1,13))
    else:
        return make_comfort_compliance(
            scoped_obs,
            "raw",
            season,
            comfort_scope=comfort_scope,
            comfort_config=comfort_config,
        )

    tbl = pd.crosstab(idx, df["comfort_cat"])
    tbl = (tbl.div(tbl.sum(axis=1).replace(0, np.nan), axis=0) * 100).fillna(0.0)
    tbl = tbl.reindex(columns=categories, fill_value=0.0)
    if x_order is not None:
        tbl = tbl.reindex(index=x_order, fill_value=0.0)

    fig = go.Figure()
    for cat in categories:
        fig.add_bar(x=tbl.index, y=tbl[cat].values, name=cat, marker_color=colors_map[cat])

    fig.update_layout(
        barmode="stack",
        title=f"% d’hores en confort – {mode.capitalize()} ({'All' if mode=='month' else season} | {scope_label})",
        legend_title_text="",
    )
    fig.update_yaxes(title="% d’hores", range=[0, 100])
    fig.update_xaxes(title=x_title, tickmode="linear", dtick=1 if mode in ("hour","month") else None)
    return _apply_figure_theme(fig)


# Gràfic de violació de confort en barres.
def make_violation_bars(
    obs: pd.DataFrame,
    mode: str,
    season: str,
    comfort_scope: str = "all",
    comfort_config=None,
) -> go.Figure:
    """Crea el gràfic de barres de desviació de confort."""
    scoped_obs = filter_by_comfort_scope(obs, comfort_scope)
    scope_label = comfort_scope_label(comfort_scope)
    base = _ensure_temp_violation_column(scoped_obs, comfort_config)

    fig = go.Figure()

    if mode == "hour":
        df = filter_by_season(base, season)
        g = df.groupby(df.index.hour)["temp_violation"].mean()
        x_vals = list(range(24))
        y_vals = [g.get(h, float("nan")) for h in x_vals]
        _add_violation_bar(fig, x=x_vals, y=y_vals, name="Mitjana horària")
        fig.update_xaxes(title="Hora del dia", tickmode="linear", dtick=1)

    elif mode == "day":
        df = filter_by_season(base, season)
        g = df.groupby(df.index.floor("D"))["temp_violation"].mean()
        fig.add_scatter(
            x=g.index.astype(str), y=g.values, name="Mitjana diària",
            mode="lines",
            line=dict(color=STUDIO_CHART_COLORS["violation"], width=2),
            meta="keep_color"
        )
        fig.update_xaxes(title="Dia")

    elif mode == "month":
        df = base.copy()  # ressaltem amb estació via colors, no filtrem
        g = df.groupby(df.index.month)["temp_violation"].mean()
        x_vals = list(range(1, 12 + 1))
        y_vals = [g.get(m, float("nan")) for m in x_vals]
        c_viol = STUDIO_CHART_COLORS["violation"]
        marker_colors = _seasonal_marker_colors(x_vals, season, active_color=c_viol)
        _add_violation_bar(fig, x=x_vals, y=y_vals, name="Mitjana mensual", color=marker_colors)
        fig.update_xaxes(title="Mes", tickmode="linear", dtick=1)

    elif mode == "raw":
        df = filter_by_season(base, season)
        _add_violation_bar(fig, x=np.arange(len(df)), y=df["temp_violation"].values, name="Registres")
        fig.update_xaxes(title="Time (step)")

    fig.update_yaxes(title="Temperature Violation (°C)")
    fig.update_layout(
        title=f"Temperature Violation (Bars) – {mode.capitalize()} ({season} | {scope_label})"
    )
    return fig


def _fix_colors_for_visibility(fig, *, kind: str, mode: str):
    """
    Aplica colors/contorns més marcats a barres en 'daily' i 'raw'.
    kind: 'violation' | 'hvac' | qualsevol altre (ignora).
    """
    if mode not in ("day", "raw"):
        return fig

    try:
        for tr in getattr(fig, "data", []):
            if getattr(tr, "type", "") != "bar":
                continue
            default_color = "#1f2937" if kind == "violation" else "#264653"
            color = getattr(getattr(tr, "marker", None), "color", None)
            if color is None or (isinstance(color, str) and color.lower() in {
                "lightgray", "#d3d3d3", "rgb(211,211,211)", "rgba(211,211,211,1.0)"
            }):
                tr.marker.color = default_color
            tr.marker.line = dict(color="rgba(0,0,0,0.25)", width=0.4)
            tr.opacity = 0.95
    except Exception:
        pass
    return fig


# Línia única de violació de temperatura amb els filtres actius.
def make_violation_single_line(
    obs: pd.DataFrame,
    mode: str,
    season: str,
    comfort_config=None,
) -> go.Figure:
    """Crea la línia de desviació de temperatura."""
    base = _ensure_temp_violation_column(obs, comfort_config)

    fig = go.Figure()
    violation_color = STUDIO_CHART_COLORS["violation"]

    if mode in ("hour", "day", "month"):
        data = _series_for_mode(base, "temp_violation", mode, season)
        if data is not None:
            x_vals, y_vals, hover, trace_mode = data
            marker_colors = (
                _seasonal_marker_colors(x_vals, season, active_color=violation_color, muted_color="#7f7f7f")
                if mode == "month"
                else violation_color
            )
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers" if mode in ("hour", "day", "month") else trace_mode,
                name={"hour": "Hourly Mean", "day": "Daily Mean", "month": "Monthly Mean"}[mode],
                line=dict(color=violation_color, width=2.6),
                marker=dict(color=marker_colors, size=6),
                meta="keep_color",
                hovertext=hover,
                hovertemplate=(
                    "%{hovertext}<br>%{y:.2f}°C<extra></extra>"
                    if hover is not None
                    else None
                ),
            ))
        _apply_mode_xaxis(fig, mode)

    elif mode == "raw":
        # En raw dibuixem primer tot l'any i, si hi ha filtre de temporada, el ressaltem
        # a sobre per no perdre el context.
        df_all = filter_by_season(base, "All")
        x_all, y_all, hover_all = _raw_axis_data(df_all, "temp_violation")
        fig.add_trace(go.Scatter(x=x_all, y=y_all, mode="lines", name="All Records",
                                 line=dict(color=violation_color, width=1.8), meta="keep_color", opacity=0.92,
                                 hovertext=hover_all, hovertemplate="%{hovertext}<br>%{y:.2f}°C<extra></extra>"))
        if season != "All":
            df_season = filter_by_season(base, season)
            if not df_season.empty:
                x_s, y_s, hover_s = _raw_axis_data(df_season, "temp_violation")
                fig.add_trace(go.Scatter(x=x_s, y=y_s, mode="lines",
                                         name=f"{season} Records", line=dict(color=violation_color, width=2.4), meta="keep_color",
                                         hovertext=hover_s, hovertemplate="%{hovertext}<br>%{y:.2f}°C<extra></extra>"))
        fig.update_xaxes(title="Time (step)")

    fig.update_yaxes(title="Temperature Violation (°C)")
    fig.update_layout(title=f"Temperature Violation – {mode.capitalize()} ({season})")
    return fig
