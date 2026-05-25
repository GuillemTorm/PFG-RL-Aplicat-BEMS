"""HVAC xifres de consum i avaria del comptador."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from backend.grafics.plot_helpers import (
    add_energy_bar_trace,
    energy_axis_title,
    energy_series_for_mode,
    raw_hourly_total_series,
)
from backend.grafics.style import STUDIO_CHART_COLORS, _alpha_color, _apply_figure_theme
from backend.grafics.time_utils import (
    _canon_day_total_series,
    _ensure_datetime_index,
    _infer_timestep_hours,
    _raw_axis_data,
    filter_by_season,
)


def _with_hvac_consumption_kwh(df: pd.DataFrame, hvac_col: str, unit_kind: str) -> pd.DataFrame:
    """Afegeix una columna temporal amb el consum HVAC per timestep en kWh."""
    from backend.grafics.observation_columns import convert_hvac_source_to_kwh

    base = df.copy()
    base["__hvac_consumption_kwh__"] = convert_hvac_source_to_kwh(
        base[hvac_col],
        unit_kind,
        _infer_timestep_hours(base),
    )
    return base


def make_hvac_consumption_plot(
    obs: pd.DataFrame,
    mode: str,
    season: str,
    *,
    raw_as_rate: bool = False,
    raw_as_line: bool = False,
) -> go.Figure:
    """Crea una figura Plotly per al consum de climatització."""
    from backend.grafics.observation_columns import (
        HVAC_POWER_COLUMN,
        find_hvac_consumption_source,
        normalize_observation_columns,
    )

    base = _ensure_datetime_index(normalize_observation_columns(obs))

    fig = go.Figure()
    hvac_source = find_hvac_consumption_source(base.columns)
    if hvac_source is None:
        return go.Figure()
    hvac_col, hvac_unit = hvac_source

    if raw_as_rate and mode == "raw" and hvac_unit == "watt":
        # En mode interactiu a vegades volem veure potència instantània, no energia per pas.
        # Si la font és W, podem mostrar-la directament com kW.
        df = filter_by_season(base, season)
        if df.empty:
            return go.Figure()
        x_vals, y_vals, hover = _raw_axis_data(df, HVAC_POWER_COLUMN)
        y_kw = (pd.Series(y_vals, dtype=float) / 1000.0).tolist()
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_kw,
                mode="lines",
                name="HVAC Demand Rate",
                line=dict(color=STUDIO_CHART_COLORS["consumption"], width=2.0),
                hovertext=hover,
                hovertemplate="%{hovertext}<br>%{y:.2f} kW<extra></extra>",
            )
        )
        fig.update_xaxes(title="Time (step)")
        fig.update_yaxes(title="Demand Rate (kW)")
        fig.update_layout(title=f"HVAC Demand Rate - {mode.capitalize()} ({season})")
        return fig

    base = _with_hvac_consumption_kwh(base, hvac_col, hvac_unit)
    energy_col = "__hvac_consumption_kwh__"

    if mode == "hour":
        add_energy_bar_trace(
            fig,
            base,
            energy_col,
            label="HVAC Consumption",
            color=STUDIO_CHART_COLORS["consumption"],
            mode=mode,
            season=season,
        )
        fig.update_xaxes(title="Hour of Day", tickmode="linear", dtick=1)
        y_axis_title = energy_axis_title(mode)

    elif mode == "day":
        series_data = energy_series_for_mode(base, energy_col, mode, season)
        if series_data is None:
            return go.Figure()
        x_vals, y_vals, hover = series_data
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                name="HVAC Consumption",
                line=dict(color=STUDIO_CHART_COLORS["consumption"], width=2.4),
                hovertext=hover,
                hovertemplate="%{hovertext}<br>%{y:.2f} kWh<extra></extra>",
            )
        )
        fig.update_xaxes(title="Day (1..365)", range=[1, 365], tickmode="linear", tick0=1, dtick=10)
        y_axis_title = energy_axis_title(mode)

    elif mode == "month":
        add_energy_bar_trace(
            fig,
            base,
            energy_col,
            label="HVAC Consumption",
            color=STUDIO_CHART_COLORS["consumption"],
            mode=mode,
            season=season,
        )
        fig.update_xaxes(title="Month", tickmode="linear", dtick=1)
        y_axis_title = energy_axis_title(mode)

    elif mode == "raw":
        # La vista raw es reagrupa a hores perquè els CSV de simulació poden tenir pas de
        # 15 minuts i una barra per timestep seria massa sorollosa.
        df = filter_by_season(base, season)
        if df.empty:
            return go.Figure()
        x_vals, y_vals, hover = raw_hourly_total_series(df, energy_col)
        if not y_vals:
            return go.Figure()

        if raw_as_line:
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode="lines",
                    name="HVAC Consumption",
                    line=dict(color=STUDIO_CHART_COLORS["consumption"], width=2.2),
                    meta="keep_color",
                    hovertext=hover,
                    hovertemplate="%{hovertext}<br>%{y:.2f} kWh<extra></extra>",
                )
            )
        else:
            fig.add_trace(go.Bar(
                x=x_vals,
                y=y_vals,
                name="HVAC Consumption",
                marker_color=STUDIO_CHART_COLORS["consumption"],
                hovertext=hover,
                hovertemplate="%{hovertext}<br>%{y:.2f} kWh<extra></extra>",
            ))
        fig.update_xaxes(title="Time (hour)")
        y_axis_title = energy_axis_title(mode, raw_title="Hourly Consumption (kWh)")
    else:
        y_axis_title = "Consumption (kWh)"

    fig.update_yaxes(title=y_axis_title)
    fig.update_layout(title=f"HVAC Consumption - {mode.capitalize()} ({season})")
    return fig


# Desglossament del consum HVAC per meters disponibles.

def make_hvac_meter_breakdown_plot(
    obs: pd.DataFrame,
    mode: str,
    season: str,
) -> go.Figure:
    """Crea una figura Plotly per a l'avaria del comptador de climatització."""
    from backend.grafics.observation_columns import (
        DETAILED_HVAC_METER_KWH_COLUMNS,
        DETAILED_HVAC_METER_LABELS,
        ELECTRIC_HVAC_METER_ALIASES,
        HVAC_ENERGY_METER_COLUMNS,
        HVAC_POWER_COLUMN,
        add_meter_kwh_columns,
        convert_hvac_source_to_kwh,
        find_hvac_consumption_source,
        normalize_observation_columns,
    )

    base = _ensure_datetime_index(add_meter_kwh_columns(normalize_observation_columns(obs)))
    meter_series = []
    # Alguns IDF només tenen el total HVAC i altres exposen meters separats per fans,
    # pumps, heating, cooling, etc. Afegim només les sèries que realment tenen energia.
    for meter_alias, kwh_column in DETAILED_HVAC_METER_KWH_COLUMNS.items():
        if kwh_column not in base.columns:
            continue
        numeric_values = pd.to_numeric(base[kwh_column], errors="coerce")
        if not numeric_values.dropna().abs().gt(1e-12).any():
            continue
        meter_series.append(
            (
                kwh_column,
                DETAILED_HVAC_METER_LABELS.get(meter_alias, meter_alias),
            )
        )
    fig = go.Figure()
    colors = {
        "Natural Gas HVAC": "#92400e",
        "Heating Electricity": STUDIO_CHART_COLORS["heating"],
        "Cooling Electricity": STUDIO_CHART_COLORS["cooling"],
        "Fans Electricity": STUDIO_CHART_COLORS["neutral"],
        "Pumps Electricity": "#0891b2",
        "Heat Rejection Electricity": "#f97316",
        "Humidifier Electricity": "#7c3aed",
        "Heat Recovery Electricity": "#16a34a",
        "Other / Unmetered HVAC Electricity": STUDIO_CHART_COLORS["consumption_muted"],
    }
    electric_detail_columns = [
        DETAILED_HVAC_METER_KWH_COLUMNS[meter_alias]
        for meter_alias in ELECTRIC_HVAC_METER_ALIASES
        if DETAILED_HVAC_METER_KWH_COLUMNS.get(meter_alias) in base.columns
    ]

    hvac_source = find_hvac_consumption_source(base.columns)
    if hvac_source is not None:
        hvac_col, hvac_unit = hvac_source
        hvac_col_is_total_electric = (
            hvac_col in HVAC_ENERGY_METER_COLUMNS
            or hvac_col.lower() in {column.lower() for column in HVAC_ENERGY_METER_COLUMNS}
            or hvac_col == HVAC_POWER_COLUMN
        )
        if hvac_col_is_total_electric:
            # Quan tenim total elèctric i també submeters, el "Other" és el residu.
            # Això ajuda a detectar consum HVAC que EnergyPlus no ha separat per categoria.
            base["__hvac_total_electricity_kwh__"] = convert_hvac_source_to_kwh(
                base[hvac_col],
                hvac_unit,
                _infer_timestep_hours(base),
            )
            if electric_detail_columns:
                electric_detail_sum = pd.DataFrame(
                    {
                        column: pd.to_numeric(base[column], errors="coerce")
                        for column in electric_detail_columns
                    },
                    index=base.index,
                ).sum(axis=1, min_count=1).fillna(0.0)
            else:
                electric_detail_sum = pd.Series(0.0, index=base.index)
            base["__other_hvac_electricity_kwh__"] = (
                pd.to_numeric(base["__hvac_total_electricity_kwh__"], errors="coerce")
                - electric_detail_sum
            ).clip(lower=0.0)
            if (
                base["__other_hvac_electricity_kwh__"]
                .dropna()
                .abs()
                .gt(1e-9)
                .any()
            ):
                meter_series.append(
                    (
                        "__other_hvac_electricity_kwh__",
                        "Other / Unmetered HVAC Electricity",
                    )
                )

    if not meter_series:
        return go.Figure()

    if mode == "hour":
        # Per hora fem mitjana entre dies: és millor per veure patrons típics que no pas
        # sumar tot l'any en una sola barra enorme.
        for kwh_column, label in meter_series:
            add_energy_bar_trace(
                fig,
                base,
                kwh_column,
                label=label,
                color=colors.get(label, STUDIO_CHART_COLORS["neutral"]),
                mode=mode,
                season=season,
            )
        fig.update_xaxes(title="Hour of Day", tickmode="linear", dtick=1)
        y_axis_title = energy_axis_title(mode)

    elif mode == "day":
        # En vista diària interessa més la proporció entre meters que la sèrie completa,
        # per això fem un donut amb el consum diari mitjà.
        df = filter_by_season(base, season)
        if df.empty:
            return go.Figure()
        labels = []
        values = []
        marker_colors = []
        for kwh_column, label in meter_series:
            _, y_vals, _ = _canon_day_total_series(df, kwh_column)
            daily_mean = pd.to_numeric(pd.Series(y_vals), errors="coerce").dropna().mean()
            if pd.isna(daily_mean) or daily_mean <= 1e-12:
                continue
            labels.append(label)
            values.append(float(daily_mean))
            marker_colors.append(colors.get(label, STUDIO_CHART_COLORS["neutral"]))

        if not values:
            return go.Figure()

        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.42,
                marker=dict(colors=marker_colors, line=dict(color="#ffffff", width=2)),
                textinfo="percent+label",
                hovertemplate="%{label}<br>Mean daily consumption %{value:.2f} kWh<extra></extra>",
            )
        )
        fig.update_layout(
            title=f"HVAC Meter Breakdown - Mean Daily Share ({season})",
            showlegend=True,
        )
        return _apply_figure_theme(fig)

    elif mode == "month":
        # En mesos agrupem per any i mes abans de fer la mitjana, així dos anys simulats
        # no queden barrejats com si fossin un únic mes gegant.
        for kwh_column, label in meter_series:
            add_energy_bar_trace(
                fig,
                base,
                kwh_column,
                label=label,
                color=colors.get(label, STUDIO_CHART_COLORS["neutral"]),
                mode=mode,
                season=season,
            )
        fig.update_xaxes(title="Month", tickmode="linear", dtick=1)
        y_axis_title = energy_axis_title(mode)

    elif mode == "raw":
        df = filter_by_season(base, season)
        if df.empty:
            return go.Figure()
        for kwh_column, label in meter_series:
            x_vals, y_vals, hover = _raw_axis_data(df, kwh_column)
            color = colors.get(label, STUDIO_CHART_COLORS["neutral"])
            fig.add_trace(
                go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode="lines",
                    name=label,
                    line=dict(color=color, width=1.8),
                    fillcolor=_alpha_color(color, 0.42),
                    stackgroup="hvac_meter_breakdown",
                    hovertext=hover,
                    hovertemplate="%{hovertext}<br>%{y:.4f} kWh<extra></extra>",
                )
            )
        fig.update_xaxes(title="Time (step)")
        y_axis_title = "Consumption per Timestep (kWh)"
    else:
        y_axis_title = "Consumption (kWh)"

    fig.update_yaxes(title=y_axis_title)
    fig.update_layout(
        title=f"HVAC Meter Breakdown - {mode.capitalize()} ({season})",
        barmode="group",
        bargap=0.18,
        bargroupgap=0.08,
    )
    return _apply_figure_theme(fig)
