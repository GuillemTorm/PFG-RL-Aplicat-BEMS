"""Figures de control i acció per a HVAC i terra radiant."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.grafics.style import pick_semantic_trace_color
from backend.grafics.time_utils import (
    _apply_mode_xaxis,
    _ensure_datetime_index,
    _mode_axis_config,
    _series_for_mode,
)


def _mean_series(base: pd.DataFrame, columns: list[str]) -> pd.Series:
    """Retorna la mitjana numèrica per files de les columnes seleccionades."""
    numeric = base[columns].apply(pd.to_numeric, errors="coerce")
    return numeric.mean(axis=1)


def _add_radiant_control_trace(
    fig: go.Figure,
    base: pd.DataFrame,
    series_name: str,
    label: str,
    secondary_y: bool,
    suffix: str,
    mode: str,
    season: str,
) -> None:
    """Afegeix un traça de control radiant a la figura."""
    data = _series_for_mode(base, series_name, mode, season)
    if data is None:
        return
    x_values, y_values, hover, trace_mode = data
    color = pick_semantic_trace_color(label)
    scatter_kwargs = dict(
        x=x_values,
        y=y_values,
        mode=trace_mode,
        name=label,
        line=dict(color=color, width=2.8, shape="hv" if mode in ("hour", "raw") else "linear"),
    )
    if "markers" in trace_mode:
        scatter_kwargs["marker"] = dict(color=color, size=6)
    if hover is not None:
        scatter_kwargs["hovertext"] = hover
        scatter_kwargs["hovertemplate"] = f"%{{hovertext}}<br>%{{y:.2f}} {suffix}<extra></extra>"
    else:
        scatter_kwargs["hovertemplate"] = f"%{{x}}<br>%{{y:.2f}} {suffix}<extra></extra>"
    fig.add_trace(go.Scatter(**scatter_kwargs), secondary_y=secondary_y)


def _pretty_action_name(column_name: str) -> str:
    """Retorna una etiqueta de visualització per a una columna d'acció."""
    return column_name.replace("_", " ").replace("radiant ", "radiant: ").title()


def _add_agent_action_trace(
    fig: go.Figure,
    base: pd.DataFrame,
    column: str,
    row: int,
    color: str,
    temp_columns: list[str],
    mode: str,
    season: str,
) -> None:
    """Afegeix una traça d'acció a la figura de diverses files."""
    data = _series_for_mode(base, column, mode, season)
    if data is None:
        return
    x_values, y_values, hover, trace_mode = data
    is_temp = column in temp_columns
    scatter_kwargs = dict(
        x=x_values,
        y=y_values,
        mode=trace_mode,
        name=_pretty_action_name(column),
        legendgroup="agent_actions",
        showlegend=False,
        line=dict(color=color, width=2.5, shape="hv" if mode in ("hour", "raw") else "linear"),
    )
    if "markers" in trace_mode:
        scatter_kwargs["marker"] = dict(color=color, size=6)
    suffix = " C" if is_temp else ""
    if hover is not None:
        scatter_kwargs["hovertext"] = hover
        scatter_kwargs["hovertemplate"] = f"%{{hovertext}}<br>%{{y:.2f}}{suffix}<extra></extra>"
    else:
        scatter_kwargs["hovertemplate"] = f"%{{x}}<br>%{{y:.2f}}{suffix}<extra></extra>"
    fig.add_trace(go.Scatter(**scatter_kwargs), row=row, col=1)


def make_radiant_control_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per al control radiant."""
    base = _ensure_datetime_index(obs).copy()

    # Els noms dels sensors radiants varien molt entre models. Fem una detecció flexible
    # i després els reduïm a tres sèries llegibles: disponibilitat, entrada i sortida.
    lower_cols = {col: col.lower() for col in base.columns}
    availability_cols = [
        col
        for col, label in lower_cols.items()
        if "radiant" in label
        and ("availavility" in label or "availability" in label or "operation_mode" in label or "operation mode" in label)
    ]
    inlet_cols = [
        col
        for col, label in lower_cols.items()
        if "radiant" in label and "inlet" in label and "temperature" in label
    ]
    outlet_cols = [
        col
        for col, label in lower_cols.items()
        if "radiant" in label and "outlet" in label and "temperature" in label
    ]

    if not availability_cols and not inlet_cols and not outlet_cols:
        return go.Figure()

    if availability_cols:
        # Si hi ha més d'una zona radiant, la mitjana dona una lectura global del mode actiu.
        base["__radiant_availability_pct__"] = _mean_series(base, availability_cols) * 100.0
    if inlet_cols:
        base["__radiant_inlet_temp__"] = _mean_series(base, inlet_cols)
    if outlet_cols:
        base["__radiant_outlet_temp__"] = _mean_series(base, outlet_cols)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    _add_radiant_control_trace(fig, base, "__radiant_outlet_temp__", "Radiant Outlet Temp", False, "C", mode, season)
    _add_radiant_control_trace(fig, base, "__radiant_inlet_temp__", "Radiant Inlet Temp", False, "C", mode, season)
    _add_radiant_control_trace(fig, base, "__radiant_availability_pct__", "Radiant Operation Mode", True, "%", mode, season)

    _apply_mode_xaxis(fig, mode)

    fig.update_yaxes(title="Temperature (C)", secondary_y=False)
    fig.update_yaxes(title="Operation Mode (%)", range=[-5, 105], secondary_y=True)
    fig.update_layout(title=f"Radiant Control - {mode.capitalize()} ({season})")
    return fig


def make_agent_actions_plot(actions: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per a les accions de l'agent."""
    if actions is None or actions.empty:
        return go.Figure()

    time_columns = {"datetime", "timestamp", "month", "day_of_month", "hour", "time_elapsed(hours)"}
    base = _ensure_datetime_index(actions).copy().sort_index(kind="mergesort")
    action_columns = [col for col in base.columns if col not in time_columns]
    if not action_columns:
        return go.Figure()

    for col in action_columns:
        base[col] = pd.to_numeric(base[col], errors="coerce")

    temp_cols = [
        col
        for col in action_columns
        if "temperature" in col.lower() or "temp" in col.lower()
    ]
    binary_cols = [col for col in action_columns if col not in temp_cols]
    ordered_cols = temp_cols + binary_cols
    if not ordered_cols:
        return go.Figure()

    for col in temp_cols:
        valid = base[col].dropna()
        if not valid.empty and valid.min() >= 0 and valid.max() <= 20:
            # Alguns wrappers guarden deltes o consignes normalitzades; si totes cauen en
            # 0..20 les desplacem per representar-les com a consignes de temperatura llegibles.
            base[col] = base[col] + 25.0

    rows = len(ordered_cols)
    # Les accions de temperatura necessiten més alçada que les binàries, on només volem
    # veure si l'actuador està actiu o no.
    row_heights = [1.7 if col in temp_cols else 0.55 for col in ordered_cols]
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.018 if rows > 1 else 0.0,
        row_heights=row_heights,
        subplot_titles=[_pretty_action_name(col) for col in ordered_cols],
    )

    palette = ["#0f766e", "#7c3aed", "#2563eb", "#ea580c", "#16a34a", "#dc2626", "#0891b2", "#ca8a04"]
    for row, col in enumerate(ordered_cols, start=1):
        _add_agent_action_trace(fig, base, col, row, palette[(row - 1) % len(palette)], temp_cols, mode, season)

    x_axis_title, x_axis_kwargs = _mode_axis_config(mode)

    for row, col in enumerate(ordered_cols, start=1):
        fig.update_xaxes(**x_axis_kwargs, row=row, col=1)
        if col in temp_cols:
            fig.update_yaxes(title="C", row=row, col=1)
        else:
            if mode == "raw":
                fig.update_yaxes(
                    title="ON/OFF",
                    range=[-0.08, 1.08],
                    tickmode="array",
                    tickvals=[0, 1],
                    ticktext=["OFF", "ON"],
                    row=row,
                    col=1,
                )
            else:
                fig.update_yaxes(
                    title="ON fraction",
                    range=[-0.05, 1.05],
                    tickmode="array",
                    tickvals=[0, 0.5, 1],
                    row=row,
                    col=1,
                )
    fig.update_xaxes(title=x_axis_title, row=rows, col=1)
    figure_height = 260 + 120 * len(temp_cols) + 58 * len(binary_cols)
    fig.update_layout(
        title=f"Agent Actions - {mode.capitalize()} ({season})",
        height=max(360, figure_height),
        showlegend=False,
    )
    return fig
