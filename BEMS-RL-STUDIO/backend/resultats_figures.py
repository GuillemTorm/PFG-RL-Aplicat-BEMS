"""Construcció compartida de figures per al dashboard i els informes de resultats."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go

from backend.grafics.battery import (
    make_battery_charge_with_price_plot,
    make_battery_power_plot,
    make_battery_soc_plot,
    make_battery_vs_grid_plot,
    make_energy_price_plot,
)
from backend.grafics.comfort import (
    _fix_colors_for_visibility,
    make_comfort_compliance,
    make_violation_bars,
    make_violation_single_line,
)
from backend.grafics.control import make_agent_actions_plot, make_radiant_control_plot
from backend.grafics.episode import make_episode_metrics
from backend.grafics.heatmaps import (
    make_heatmap,
    make_violation_heatmap_percent,
    make_zone_temperature_heatmaps,
)
from backend.grafics.hvac import make_hvac_consumption_plot, make_hvac_meter_breakdown_plot
from backend.grafics.style import style_figure_semantics
from backend.grafics.thermal import (
    make_indoor_humidity_plot,
    make_indoor_temperature_plot,
    make_setpoints_vs_indoor_plot,
)
from backend.resultats_backend import (
    DashboardData,
    apply_real_period_axis,
    has_action_figure_data,
    is_radiant_run,
    overlay_comparison_traces,
)


@dataclass(frozen=True)
class ReportFigure:
    """Gràfic Plotly més la secció d'informe on hauria d'aparèixer."""

    section: str
    title: str
    figure: go.Figure


CONTROL_FIGURE_KEYS = ("setpoints_vs_indoor", "radiant", "actions")
BATTERY_FIGURE_KEYS = (
    "battery_power",
    "battery_soc",
    "battery_vs_grid",
    "battery_charge_price",
)
REAL_AXIS_FIGURE_KEYS = (
    "indoor",
    "humidity",
    "setpoints_vs_indoor",
    "radiant",
    "actions",
    "hvac",
    "hvac_breakdown",
    "energy_price",
    "battery_power",
    "battery_soc",
    "battery_vs_grid",
    "battery_charge_price",
    "violation",
)
STYLE_FIGURE_KEYS = (
    "indoor",
    "humidity",
    "setpoints_vs_indoor",
    "radiant",
    "actions",
    "hvac",
    "energy_price",
    "battery_power",
    "battery_soc",
    "battery_vs_grid",
    "battery_charge_price",
    "violation",
    "zone_heatmap",
    "heatmap",
)
OVERLAY_FIGURE_KEYS = (
    "indoor",
    "humidity",
    "setpoints_vs_indoor",
    "radiant",
    "hvac",
    "hvac_breakdown",
    "energy_price",
    "battery_power",
    "battery_soc",
    "battery_vs_grid",
    "battery_charge_price",
    "violation",
)
AGGREGATE_OVERLAY_KEYS = ("comfort", "episode")

REPORT_FIGURE_SPECS = (
    ("comfort", "Confort i clima interior", "Confort (%)"),
    ("indoor", "Confort i clima interior", "Temperatura interior vs exterior"),
    ("humidity", "Confort i clima interior", "Humitat interior vs exterior"),
    ("violation", "Confort i clima interior", "Infraccions de confort"),
    (
        "violation_heatmap",
        "Confort i clima interior",
        "Mapa de calor d'infraccions de confort (%)",
    ),
    ("zone_heatmap", "Confort i clima interior", "Temperatura per zona (mes x hora)"),
    ("hvac", "Consum i energia", "Consum HVAC (kWh)"),
    ("hvac_breakdown", "Consum i energia", "Desglossament HVAC per meter (kWh)"),
    ("energy_price", "Consum i energia", "Preu energia (EUR/kWh)"),
    ("heatmap", "Consum i energia", "Mapa de calor global (consum)"),
    ("setpoints_vs_indoor", "Control HVAC", "Setpoints vs temperatura interior"),
    ("radiant", "Control HVAC", "Control radiant"),
    ("actions", "Control HVAC", "Accions de l'agent"),
    ("battery_power", "Bateria i xarxa", "Càrrega/descàrrega bateria"),
    ("battery_soc", "Bateria i xarxa", "SOC bateria"),
    ("battery_vs_grid", "Bateria i xarxa", "Energia bateria vs xarxa"),
    ("battery_charge_price", "Bateria i xarxa", "Bateria vs preu energia"),
    ("episode", "Episodi", "Mètriques d'episodi"),
)


def build_dashboard_figures(
    data: DashboardData,
    zobs: pd.DataFrame,
    action_data: pd.DataFrame,
    *,
    plot_mode: str,
    plot_season: str,
    comfort_scope: str,
    view_mode: str,
    real_period_kind: str,
) -> dict[str, go.Figure]:
    """Crea totes les figures Plotly utilitzades pel panell de resultats en línia."""

    comfort_mode = "raw" if plot_mode in ("day", "raw") else plot_mode
    hvac_raw_as_line = view_mode == "real" and real_period_kind == "month"

    figures: dict[str, go.Figure] = {
        "comfort": (
            make_comfort_compliance(
                zobs,
                comfort_mode,
                plot_season,
                comfort_scope=comfort_scope,
                comfort_config=data.yaml_cfg,
            )
            if view_mode == "aggregate"
            else go.Figure()
        ),
        "indoor": make_indoor_temperature_plot(zobs, plot_mode, plot_season),
        "humidity": make_indoor_humidity_plot(zobs, plot_mode, plot_season),
        "setpoints_vs_indoor": make_setpoints_vs_indoor_plot(zobs, plot_mode, plot_season),
        "radiant": make_radiant_control_plot(zobs, plot_mode, plot_season),
        "actions": make_agent_actions_plot(action_data, plot_mode, plot_season),
        "hvac": _fix_colors_for_visibility(
            make_hvac_consumption_plot(
                zobs,
                plot_mode,
                plot_season,
                raw_as_line=hvac_raw_as_line,
            ),
            kind="hvac",
            mode=plot_mode,
        ),
        "hvac_breakdown": make_hvac_meter_breakdown_plot(zobs, plot_mode, plot_season),
        "energy_price": make_energy_price_plot(zobs, plot_mode, plot_season),
        "battery_power": make_battery_power_plot(zobs, plot_mode, plot_season),
        "battery_soc": make_battery_soc_plot(zobs, plot_mode, plot_season),
        "battery_vs_grid": make_battery_vs_grid_plot(zobs, plot_mode, plot_season),
        "battery_charge_price": make_battery_charge_with_price_plot(zobs, plot_mode, plot_season),
        "zone_heatmap": go.Figure(),
        "heatmap": go.Figure(),
        "episode": make_episode_metrics(data.progress)
        if view_mode == "aggregate"
        else go.Figure(),
    }

    if not has_action_figure_data(figures["actions"]):
        figures["actions"] = go.Figure()

    if view_mode == "aggregate":
        figures["violation"] = _fix_colors_for_visibility(
            make_violation_bars(
                zobs,
                plot_mode,
                plot_season,
                comfort_scope=comfort_scope,
                comfort_config=data.yaml_cfg,
            ),
            kind="violation",
            mode=plot_mode,
        )
        figures["zone_heatmap"] = make_zone_temperature_heatmaps(
            zobs, season=plot_season, agg="mean", max_cols=3
        )
        pivot = data.metrics_dict.get("pivot_consumption")
        if pivot is not None and not pivot.empty:
            figures["heatmap"] = make_heatmap(pivot, "Total HVAC Consumption (kWh)")
    else:
        figures["violation"] = make_violation_single_line(
            zobs,
            plot_mode,
            plot_season,
            comfort_config=data.yaml_cfg,
        )
        for key in REAL_AXIS_FIGURE_KEYS:
            axis_data = action_data if key == "actions" else zobs
            figures[key] = apply_real_period_axis(figures[key], axis_data, real_period_kind)

    return figures


def overlay_dashboard_figures(
    figures: dict[str, go.Figure],
    comparison_figures: dict[str, go.Figure],
    *,
    data: DashboardData,
    view_mode: str,
) -> dict[str, go.Figure]:
    """Superposa traces de comparació a les figures actives del panell."""

    overlay_keys = list(OVERLAY_FIGURE_KEYS)
    if view_mode == "aggregate":
        overlay_keys.extend(AGGREGATE_OVERLAY_KEYS)
    if is_radiant_run(data):
        overlay_keys.append("actions")

    for key in overlay_keys:
        figures[key] = overlay_comparison_traces(figures[key], comparison_figures[key])
    return figures


def style_dashboard_figures(
    figures: dict[str, go.Figure],
    *,
    view_mode: str,
) -> dict[str, go.Figure]:
    """Aplica la semàntica comuna de Plotly a les figures del panell abans de representar-les."""

    styled = dict(figures)
    for key in STYLE_FIGURE_KEYS:
        styled[key] = style_figure_semantics(styled[key])
    if view_mode == "aggregate":
        styled["comfort"] = style_figure_semantics(styled["comfort"])
        styled["episode"] = style_figure_semantics(styled["episode"])
    return styled


def build_report_figures(
    data: DashboardData,
    zone_obs: pd.DataFrame,
    action_data: pd.DataFrame,
    *,
    agg_mode: str,
    season: str,
    comfort_scope: str,
) -> tuple[ReportFigure, ...]:
    """Prepara les figures incloses en un informe de resultats exportat."""

    figures = build_dashboard_figures(
        data,
        zone_obs,
        action_data,
        plot_mode=agg_mode,
        plot_season=season,
        comfort_scope=comfort_scope,
        view_mode="aggregate",
        real_period_kind="month",
    )
    figures["violation_heatmap"] = make_violation_heatmap_percent(
        zone_obs,
        season=season,
        comfort_config=data.yaml_cfg,
    )

    return tuple(
        ReportFigure(section, title, figures[key])
        for key, section, title in REPORT_FIGURE_SPECS
    )
