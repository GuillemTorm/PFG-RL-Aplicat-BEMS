"""Dades d'entrada de confort tèrmic: temperatura, humitat i consignes."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from backend.grafics.column_utils import _ensure_air_temperature
from backend.grafics.plot_helpers import build_mode_scatter_trace
from backend.grafics.style import pick_semantic_trace_color
from backend.grafics.time_utils import (
    _apply_mode_xaxis,
    _canon_day_series,
    _ensure_datetime_index,
    _get_outdoor_temperature_series,
    _hour_series,
    _month_series,
    _raw_axis_data,
    filter_by_season,
)


def make_indoor_temperature_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Dibuixa la temperatura interior com a barres i l'exterior com una línia amb marcadors."""
    base = _ensure_datetime_index(_ensure_air_temperature(obs))
    out_series = _get_outdoor_temperature_series(base)

    _C_BAR = "rgba(79, 142, 247, 0.65)"   # blau EPW (igual que Humitat)
    _C_OUT = "#f26b5b"                     # salmó EPW (igual que Temp. seca)
    _C_OUT_EDGE = "#f26b5b"

    fig = go.Figure()
    if "air_temperature" not in base.columns:
        return go.Figure()

    if mode in ("hour", "month"):
        # Hora i mes són agregats; per això fem barres de mitjana interior i línia exterior
        # amb el mateix eix temporal.
        if mode == "hour":
            df = filter_by_season(base, season)
            grp = _hour_series(df)
            x_vals = list(range(24))
            x_title, tick_cfg = "Hour of Day", dict(tickmode="linear", dtick=1)
        else:
            df = base if season == "All" else filter_by_season(base, season)
            grp = _month_series(df)
            x_vals = list(range(1, 13))
            x_title, tick_cfg = "Month", dict(tickmode="linear", dtick=1)

        g_mean = df.groupby(grp)["air_temperature"].mean()
        y_in   = [g_mean.get(v, float("nan")) for v in x_vals]

        fig.add_trace(go.Bar(
            x=x_vals, y=y_in, name="Indoor Temp",
            marker_color=_C_BAR,
            meta="keep_color",
            hovertemplate="%{x}<br>Mitjana: %{y:.1f}°C<extra></extra>",
        ))
        if out_series is not None:
            g_out = df.groupby(grp)[out_series.name].mean()
            y_out = [g_out.get(v, float("nan")) for v in x_vals]
            fig.add_trace(go.Scatter(
                x=x_vals, y=y_out, mode="lines+markers", name="Outdoor Temp",
                line=dict(color=_C_OUT, width=2.5),
                marker=dict(color=_C_OUT, size=7, symbol="circle",
                            line=dict(color="white", width=1.5)),
                meta="keep_color",
                hovertemplate="%{x}<br>%{y:.1f}°C<extra></extra>",
            ))
        fig.update_xaxes(title=x_title, **tick_cfg)
        fig.update_layout(bargap=0.22)

    elif mode == "day":
        # La vista diària conserva la forma anual però redueix el soroll de cada timestep.
        df = filter_by_season(base, season)
        x_in, y_in, hover_in = _canon_day_series(df, "air_temperature")
        fig.add_trace(go.Scatter(
            x=x_in, y=y_in, mode="lines", name="Indoor Temp",
            line=dict(color="rgba(79, 142, 247, 0.9)", width=2),
            meta="keep_color",
            hovertext=hover_in,
            hovertemplate="%{hovertext}<br>%{y:.1f}°C<extra></extra>",
        ))
        if out_series is not None:
            x_out, y_out, hover_out = _canon_day_series(
                df.rename(columns={out_series.name: "_out"}), "_out"
            )
            fig.add_trace(go.Scatter(
                x=x_out, y=y_out, mode="lines", name="Outdoor Temp",
                line=dict(color=_C_OUT, width=2),
                meta="keep_color",
                hovertext=hover_out,
                hovertemplate="%{hovertext}<br>%{y:.1f}°C<extra></extra>",
            ))
        fig.update_xaxes(title="Day (1..365)", tickmode="linear", tick0=1, dtick=10)

    elif mode == "raw":
        # Raw manté el pas original de simulació, útil per revisar pics puntuals.
        df = filter_by_season(base, season)
        x_vals, y_in, hover_in = _raw_axis_data(df, "air_temperature")
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_in, mode="lines", name="Indoor Temp",
            line=dict(color="rgba(79, 142, 247, 0.9)", width=2.2, shape="spline"),
            meta="keep_color",
            hovertext=hover_in,
            hovertemplate="%{hovertext}<br>%{y:.1f}°C<extra></extra>",
        ))
        if out_series is not None:
            x_v2, y_out, hover_out = _raw_axis_data(
                df.rename(columns={out_series.name: "_out"}), "_out"
            )
            fig.add_trace(go.Scatter(
                x=x_v2, y=y_out, mode="lines", name="Outdoor Temp",
                line=dict(color=_C_OUT, width=1.8, shape="spline"),
                meta="keep_color",
                hovertext=hover_out,
                hovertemplate="%{hovertext}<br>%{y:.1f}°C<extra></extra>",
            ))
        fig.update_xaxes(title="Time (step)")

    fig.update_yaxes(title="Temperature (°C)")
    fig.update_layout(title=f"Indoor vs Outdoor Temperature – {mode.capitalize()} ({season})")
    return fig


# Humitat interior amb humitat exterior de referència.
def make_indoor_humidity_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Dibuixa la humitat interior com a barres o línies i l'exterior amb marcadors."""
    base = _ensure_datetime_index(obs.copy())
    out_series = base["outdoor_humidity"] if "outdoor_humidity" in base.columns else None

    _C_IN_LINE = "rgba(0, 200, 255, 1.0)"
    _C_OUT_BAR = "rgba(15, 45, 120, 0.75)"

    fig = go.Figure()
    if "air_humidity" not in base.columns:
        return go.Figure()

    if mode in ("hour", "month"):
        # Igual que amb temperatura: agregats per hora/mes, amb humitat interior com a
        # línia principal i exterior com a referència.
        if mode == "hour":
            df = filter_by_season(base, season)
            grp = _hour_series(df)
            x_vals = list(range(24))
            x_title, tick_cfg = "Hour of Day", dict(tickmode="linear", dtick=1)
        else:
            df = base if season == "All" else filter_by_season(base, season)
            grp = _month_series(df)
            x_vals = list(range(1, 13))
            x_title, tick_cfg = "Month", dict(tickmode="linear", dtick=1)

        g_mean = df.groupby(grp)["air_humidity"].mean()
        y_in   = [g_mean.get(v, float("nan")) for v in x_vals]

        fig.add_trace(go.Scatter(
            x=x_vals, y=y_in, mode="lines+markers", name="Indoor Humidity",
            line=dict(color=_C_IN_LINE, width=2.5),
            marker=dict(color=_C_IN_LINE, size=7, symbol="circle",
                        line=dict(color="white", width=1.5)),
            meta="keep_color",
            hovertemplate="%{x}<br>Mitjana: %{y:.1f}%<extra></extra>",
        ))
        if out_series is not None:
            g_out = df.groupby(grp)[out_series.name].mean()
            y_out = [g_out.get(v, float("nan")) for v in x_vals]
            fig.add_trace(go.Bar(
                x=x_vals, y=y_out, name="Outdoor Humidity",
                marker_color=_C_OUT_BAR,
                meta="keep_color",
                hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>",
            ))
        fig.update_xaxes(title=x_title, **tick_cfg)
        fig.update_layout(bargap=0.22)

    elif mode == "day":
        df = filter_by_season(base, season)
        x_in, y_in, hover_in = _canon_day_series(df, "air_humidity")
        fig.add_trace(go.Scatter(
            x=x_in, y=y_in, mode="lines", name="Indoor Humidity",
            line=dict(color=_C_IN_LINE, width=2),
            meta="keep_color",
            hovertext=hover_in,
            hovertemplate="%{hovertext}<br>%{y:.1f}%<extra></extra>",
        ))
        if out_series is not None:
            x_out, y_out, hover_out = _canon_day_series(
                df.rename(columns={out_series.name: "_out"}), "_out"
            )
            fig.add_trace(go.Scatter(
                x=x_out, y=y_out, mode="lines", name="Outdoor Humidity",
                line=dict(color=_C_OUT_BAR, width=2),
                meta="keep_color",
                hovertext=hover_out,
                hovertemplate="%{hovertext}<br>%{y:.1f}%<extra></extra>",
            ))
        fig.update_xaxes(title="Day (1..365)", tickmode="linear", tick0=1, dtick=10)

    elif mode == "raw":
        # Raw és útil per detectar pics d'humitat que quedarien amagats en la mitjana.
        df = filter_by_season(base, season)
        x_vals, y_in, hover_in = _raw_axis_data(df, "air_humidity")
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_in, mode="lines", name="Indoor Humidity",
            line=dict(color=_C_IN_LINE, width=2.2, shape="spline"),
            meta="keep_color",
            hovertext=hover_in,
            hovertemplate="%{hovertext}<br>%{y:.1f}%<extra></extra>",
        ))
        if out_series is not None:
            x_v2, y_out, hover_out = _raw_axis_data(
                df.rename(columns={out_series.name: "_out"}), "_out"
            )
            fig.add_trace(go.Scatter(
                x=x_v2, y=y_out, mode="lines", name="Outdoor Humidity",
                line=dict(color=_C_OUT_BAR, width=1.8, shape="spline"),
                meta="keep_color",
                hovertext=hover_out,
                hovertemplate="%{hovertext}<br>%{y:.1f}%<extra></extra>",
            ))
        fig.update_xaxes(title="Time (step)")

    fig.update_yaxes(title="Humidity (%)")
    fig.update_layout(title=f"Indoor vs Outdoor Humidity – {mode.capitalize()} ({season})")
    return fig


# Temperatures de consigna de calefacció i refrigeració.
def _with_global_setpoint_columns(base: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Afegeix consignes globals mitjanes quan les dades venen per zona."""
    htg_cols = [column for column in base.columns if "htg_setpoint" in column.lower()]
    clg_cols = [column for column in base.columns if "clg_setpoint" in column.lower()]

    if htg_cols and "htg_setpoint" not in base.columns:
        base["htg_setpoint"] = base[htg_cols].mean(axis=1)
    if clg_cols and "clg_setpoint" not in base.columns:
        base["clg_setpoint"] = base[clg_cols].mean(axis=1)
    return base, bool(htg_cols or clg_cols)


def _build_setpoint_trace(
    base: pd.DataFrame,
    series_name: str,
    label: str,
    line_style: dict,
    mode: str,
    season: str,
) -> go.Scatter | None:
    """Crea una traça relacionada amb el punt de consigna per al mode d'agregació seleccionat."""
    trace = build_mode_scatter_trace(
        base,
        series_name,
        mode,
        season,
        name=label,
        color=line_style["color"],
        units="°C",
        line_width=float(line_style.get("width", 2.4)),
        line_shape=line_style.get("shape"),
        hovertemplate="%{hovertext}<br>%{y:.2f}°C<extra></extra>",
    )
    return trace


def make_setpoints_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per als punts de consigna."""
    base = _ensure_datetime_index(obs).copy()

    base, has_setpoints = _with_global_setpoint_columns(base)
    if not has_setpoints:
        return go.Figure()

    fig = go.Figure()

    htg_color = pick_semantic_trace_color("Heating Setpoint")
    clg_color = pick_semantic_trace_color("Cooling Setpoint")
    htg_style = dict(color=htg_color, width=3.2, shape="hv" if mode in ("hour", "raw") else "linear")
    clg_style = dict(color=clg_color, width=3.2, shape="hv" if mode in ("hour", "raw") else "linear")
    tr1 = _build_setpoint_trace(base, "htg_setpoint", "Heating Setpoint", htg_style, mode, season)
    tr2 = _build_setpoint_trace(base, "clg_setpoint", "Cooling Setpoint", clg_style, mode, season)
    if tr1: fig.add_trace(tr1)
    if tr2: fig.add_trace(tr2)

    _apply_mode_xaxis(fig, mode)

    fig.update_yaxes(title="Temperature (°C)")
    fig.update_layout(title=f"Setpoints – {mode.capitalize()} ({season})")
    return fig


# Comparació entre consignes i temperatura interior.
def make_setpoints_vs_indoor_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per a punts de consigna vs interior."""
    base = _ensure_datetime_index(obs).copy()

    base, has_setpoints = _with_global_setpoint_columns(base)
    if not has_setpoints and "air_temperature" not in base.columns:
        return go.Figure()

    fig = go.Figure()

    htg_color = pick_semantic_trace_color("Heating Setpoint")
    clg_color = pick_semantic_trace_color("Cooling Setpoint")
    ind_color = pick_semantic_trace_color("indoor")

    htg_style = dict(color=htg_color, width=3.2, shape="hv" if mode in ("hour", "raw") else "linear")
    clg_style = dict(color=clg_color, width=3.2, shape="hv" if mode in ("hour", "raw") else "linear")
    ind_style = dict(color=ind_color, width=2.0, shape="spline" if mode == "raw" else "linear")

    tr1 = _build_setpoint_trace(base, "htg_setpoint", "Heating Setpoint", htg_style, mode, season)
    tr2 = _build_setpoint_trace(base, "clg_setpoint", "Cooling Setpoint", clg_style, mode, season)
    tr3 = _build_setpoint_trace(base, "air_temperature", "Indoor Temperature", ind_style, mode, season)

    if tr1: fig.add_trace(tr1)
    if tr2: fig.add_trace(tr2)
    if tr3: fig.add_trace(tr3)

    _apply_mode_xaxis(fig, mode)

    fig.update_yaxes(title="Temperature (°C)")
    fig.update_layout(title=f"Setpoints vs Indoor Temperature – {mode.capitalize()} ({season})")
    return fig
