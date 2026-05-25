"""Dades del quadre de comandament de la bateria, la xarxa i les tarifes."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from backend.grafics.column_utils import (
    _BATTERY_CHARGE_POWER_COLUMNS,
    _BATTERY_DISCHARGE_ENERGY_COLUMNS,
    _BATTERY_DISCHARGE_POWER_COLUMNS,
    _GRID_ENERGY_COLUMNS,
    _GRID_KWH_COLUMNS,
    _GRID_POWER_COLUMNS,
    _find_battery_state_column,
    _find_energy_price_column,
    _find_first_present_column,
)
from backend.grafics.energy_units import (
    _battery_state_display_series,
    _energy_price_series_eur_per_kwh,
    _energy_to_kwh,
)
from backend.grafics.plot_helpers import (
    add_energy_bar_trace,
    add_mode_scatter_trace,
    build_mode_scatter_trace,
    energy_axis_title,
)
from backend.grafics.style import STUDIO_CHART_COLORS, _apply_figure_theme
from backend.grafics.time_utils import (
    _apply_mode_xaxis,
    _auto_scale_series,
    _ensure_datetime_index,
    _infer_timestep_hours,
)


def _add_battery_power_trace(
    fig: go.Figure,
    base: pd.DataFrame,
    series: str | None,
    label: str,
    sign: int,
    mode: str,
    season: str,
    units: str,
) -> None:
    """Afegeix un rastre de càrrega o descàrrega a la figura de la bateria."""
    color = (
        STUDIO_CHART_COLORS["battery_charge"]
        if sign > 0
        else STUDIO_CHART_COLORS["battery_discharge"]
    )
    add_mode_scatter_trace(
        fig,
        base,
        series,
        mode,
        season,
        name=label,
        color=color,
        units=units,
        sign=sign,
        hovertemplate="%{hovertext}<br>%{y:.2f} " + units + "<extra></extra>",
    )


def _add_battery_grid_bar_trace(
    fig: go.Figure,
    base: pd.DataFrame,
    column: str,
    label: str,
    color: str,
    mode: str,
    season: str,
) -> None:
    """Afegeix una traça de la barra de bateria contra la xarxa per al mode d'agregació seleccionat."""
    add_energy_bar_trace(
        fig,
        base,
        column,
        label=label,
        color=color,
        mode=mode,
        season=season,
    )


def make_battery_power_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per a la bateria."""
    base = _ensure_datetime_index(obs).copy()
    fig = go.Figure()

    charge_power_col = _find_first_present_column(base.columns, _BATTERY_CHARGE_POWER_COLUMNS)
    discharge_power_col = _find_first_present_column(base.columns, _BATTERY_DISCHARGE_POWER_COLUMNS)
    state_col = _find_battery_state_column(base.columns)
    has_charge_p = charge_power_col is not None
    has_discharge_p = discharge_power_col is not None
    has_state = state_col is not None

    if not (has_charge_p or has_discharge_p or has_state):
        return go.Figure()

    scale_suffix = ""
    # Reserva: només tenim battery_charge_state → fem servir la diferència per pas
    if not (has_charge_p or has_discharge_p):
        s = pd.to_numeric(base[state_col], errors="coerce")
        d = s.diff().fillna(0.0)                # +: carrega, −: descarrega
        d, scale_suffix = _auto_scale_series(d) # millora llegibilitat
        base["__charge__"]    = d.clip(lower=0.0)        # ≥ 0
        base["__discharge__"] = -d.clip(upper=0.0)       # ≥ 0
        charge_col, discharge_col = "__charge__", "__discharge__"
        units = f"Δstate/step {scale_suffix}" if scale_suffix else "Δstate/step"
    else:
        charge_col = charge_power_col
        discharge_col = discharge_power_col
        units = "W"

    # Convenció del gràfic: càrrega positiva, descàrrega negativa
    _add_battery_power_trace(fig, base, charge_col, "Charge (+)", +1, mode, season, units)
    _add_battery_power_trace(fig, base, discharge_col, "Discharge (−)", -1, mode, season, units)

    # Eixos i línia y=0
    _apply_mode_xaxis(fig, mode)
    fig.update_yaxes(title=f"Battery Power ({units})")
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    fig.update_layout(title=f"Battery Charge/Discharge – {mode.capitalize()} ({season})")
    return fig



def make_battery_soc_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per a la bateria."""
    base = _ensure_datetime_index(obs).copy()
    fig = go.Figure()

    state_col = _find_battery_state_column(base.columns)
    if state_col is None:
        return go.Figure()

    s = pd.to_numeric(base[state_col], errors="coerce")
    if s.dropna().empty:
        return go.Figure()

    s, units, state_label = _battery_state_display_series(base, state_col)
    base["__soc__"] = s

    trace = build_mode_scatter_trace(
        base,
        "__soc__",
        mode,
        season,
        name=state_label,
        color=STUDIO_CHART_COLORS["battery"],
        units=units,
        line_width=2.0 if mode == "raw" else 2.4,
        hovertemplate="%{hovertext}<br>%{y:.4f} " + units + "<extra></extra>",
        meta="keep_color",
    )
    if trace is None:
        return go.Figure()
    fig.add_trace(trace)
    _apply_mode_xaxis(fig, mode)

    fig.update_yaxes(title=f"{state_label} ({units})")
    fig.update_layout(title=f"{state_label} – {mode.capitalize()} ({'All' if mode=='month' else season})")
    return fig

def _grid_source_unit_kind(column_name: str) -> str:
    """Tipus d'unitat font de la xarxa."""
    label = column_name.lower()
    if "kwh" in label:
        return "kwh"
    if "energy" in label or "joule" in label:
        return "joule"
    if "rate" in label or "power" in label:
        return "watt"
    return "watt"


def make_energy_price_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura de Plotly per al preu de l'energia."""
    from backend.grafics.observation_columns import normalize_observation_columns

    base = _ensure_datetime_index(normalize_observation_columns(obs)).copy()
    price_col = _find_energy_price_column(base.columns)
    if price_col is None:
        return go.Figure()

    base["__energy_price_eur_per_kwh__"] = _energy_price_series_eur_per_kwh(base, price_col)
    price_col = "__energy_price_eur_per_kwh__"
    if base[price_col].dropna().empty:
        return go.Figure()

    trace = build_mode_scatter_trace(
        base,
        price_col,
        mode,
        season,
        name="Energy Price",
        color=STUDIO_CHART_COLORS["price"],
        units="EUR/kWh",
        line_width=2.4 if mode == "raw" else 2.8,
        hovertemplate="%{hovertext}<br>%{y:.4f} EUR/kWh<extra></extra>",
    )
    if trace is None:
        return go.Figure()

    fig = go.Figure(trace)
    _apply_mode_xaxis(fig, mode)
    fig.update_yaxes(title="Price (EUR/kWh)")
    fig.update_layout(title=f"Energy Price - {mode.capitalize()} ({season})")
    return fig


def make_battery_vs_grid_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per a la bateria i la xarxa."""
    base = _ensure_datetime_index(obs).copy()

    discharge_power_col = _find_first_present_column(base.columns, _BATTERY_DISCHARGE_POWER_COLUMNS)
    discharge_energy_col = _find_first_present_column(base.columns, _BATTERY_DISCHARGE_ENERGY_COLUMNS)
    grid_col = _find_first_present_column(
        base.columns,
        _GRID_POWER_COLUMNS + _GRID_ENERGY_COLUMNS + _GRID_KWH_COLUMNS,
    )

    if discharge_power_col is None and discharge_energy_col is None and grid_col is None:
        return go.Figure()

    ts_hours = _infer_timestep_hours(base)

    if discharge_power_col is not None:
        bat_w = pd.to_numeric(base[discharge_power_col], errors="coerce").clip(lower=0.0)
        base["__bat_kwh__"] = _energy_to_kwh(bat_w, "watt", ts_hours)
    elif discharge_energy_col is not None:
        base["__bat_kwh__"] = _energy_to_kwh(
            pd.to_numeric(base[discharge_energy_col], errors="coerce").clip(lower=0.0),
            "joule",
        )
    if grid_col is not None:
        grid_kind = _grid_source_unit_kind(grid_col)
        grid_values = pd.to_numeric(base[grid_col], errors="coerce").clip(lower=0.0)
        base["__grid_kwh__"] = _energy_to_kwh(grid_values, grid_kind, ts_hours)

    bat_color = STUDIO_CHART_COLORS["battery_charge"]
    grid_color = "#eab308"
    fig = go.Figure()

    _add_battery_grid_bar_trace(fig, base, "__bat_kwh__", "Energia Bateria", bat_color, mode, season)
    _add_battery_grid_bar_trace(fig, base, "__grid_kwh__", "Compra Xarxa", grid_color, mode, season)

    _apply_mode_xaxis(fig, mode)
    y_title = energy_axis_title(mode)

    fig.update_layout(barmode="group")

    fig.update_yaxes(title=y_title)
    fig.update_layout(title=f"Energia Bateria vs Xarxa - {mode.capitalize()} ({season})")
    return fig


# Gràfic de càrrega/descarrega de bateria amb preu d'energia.

def make_battery_charge_with_price_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure:
    """Crea una figura Plotly per a la càrrega de la bateria amb el preu."""
    from plotly.subplots import make_subplots as _make_subplots
    from backend.grafics.observation_columns import normalize_observation_columns

    base = _ensure_datetime_index(normalize_observation_columns(obs)).copy()

    # Detectem les columnes de bateria que existeixen en aquest CSV.
    charge_col = _find_first_present_column(base.columns, _BATTERY_CHARGE_POWER_COLUMNS)
    discharge_col = _find_first_present_column(base.columns, _BATTERY_DISCHARGE_POWER_COLUMNS)
    state_col = _find_battery_state_column(base.columns)
    has_bat = charge_col is not None or discharge_col is not None or state_col is not None

    # El preu pot venir amb noms diferents segons el wrapper utilitzat.
    price_col_raw = _find_energy_price_column(base.columns)
    has_price = price_col_raw is not None

    if not has_bat and not has_price:
        return go.Figure()

    # Si només tenim l'estat de càrrega, estimem càrrega/descarrega amb la diferència.
    units = "W"
    if has_bat:
        if charge_col is None and discharge_col is None:
            s = pd.to_numeric(base[state_col], errors="coerce")
            d = s.diff().fillna(0.0)
            d, _sfx = _auto_scale_series(d)
            base["__charge__"] = d.clip(lower=0.0)
            base["__discharge__"] = -d.clip(upper=0.0)
            charge_col, discharge_col = "__charge__", "__discharge__"
            units = f"Δstate/step {_sfx}".strip() if _sfx else "Δstate/step"

    # Normalitzem el preu a EUR/kWh perquè l'eix sigui comparable entre runs.
    price_col = "__price__"
    if has_price:
        base[price_col] = _energy_price_series_eur_per_kwh(base, price_col_raw)
        if base[price_col].dropna().empty:
            has_price = False

    # Posem la bateria a l'eix principal i el preu a l'eix secundari.
    fig = _make_subplots(specs=[[{"secondary_y": True}]])

    bat_charge_color = STUDIO_CHART_COLORS["battery_charge"]
    bat_discharge_color = STUDIO_CHART_COLORS["battery_discharge"]
    price_color = STUDIO_CHART_COLORS["price"]

    # Carrega (eix primari)
    if has_bat:
        charge_trace = build_mode_scatter_trace(
            base,
            charge_col,
            mode,
            season,
            name=f"Carrega (+) [{units}]",
            color=bat_charge_color,
            units=units,
            sign=+1,
            line_width=2.6,
            hovertemplate="%{hovertext}<br>Carrega: %{y:.2f} " + units + "<extra></extra>",
            plain_hovertemplate="Carrega: %{y:.2f} " + units + "<extra></extra>",
        )
        if charge_trace is not None:
            fig.add_trace(
                charge_trace,
                secondary_y=False,
            )

        # Descarrega (eix primari, valors negatius)
        discharge_trace = build_mode_scatter_trace(
            base,
            discharge_col,
            mode,
            season,
            name=f"Descarrega (-) [{units}]",
            color=bat_discharge_color,
            units=units,
            sign=-1,
            line_width=2.6,
            fill="tozeroy",
            fillcolor="rgba(234,88,12,0.10)",  # battery_discharge amb alpha
            hovertemplate="%{hovertext}<br>Descarrega: %{y:.2f} " + units + "<extra></extra>",
            plain_hovertemplate="Descarrega: %{y:.2f} " + units + "<extra></extra>",
        )
        if discharge_trace is not None:
            fig.add_trace(
                discharge_trace,
                secondary_y=False,
            )

        fig.add_hline(y=0, line_dash="dash", line_color=STUDIO_CHART_COLORS["neutral_soft"],
                      line_width=1.2)

    # Preu (eix secundari)
    price_trace = (
        build_mode_scatter_trace(
            base,
            price_col,
            mode,
            season,
            name="Preu Energia (EUR/kWh)",
            color=price_color,
            units="EUR/kWh",
            line_width=2.2,
            marker_size=5,
            hovertemplate="%{hovertext}<br>Preu: %{y:.4f} EUR/kWh<extra></extra>",
            plain_hovertemplate="Preu: %{y:.4f} EUR/kWh<extra></extra>",
        )
        if has_price
        else None
    )
    if price_trace is not None:
        fig.add_trace(
            price_trace,
            secondary_y=True,
        )

    # Ajustem els eixos segons l'agregació escollida.
    x_titles = {"hour": "Hour of Day", "day": "Day (1..365)", "month": "Month", "raw": "Time (step)"}
    x_dticks = {"hour": 1, "month": 1}
    fig.update_xaxes(title_text=x_titles.get(mode, ""), tickmode="linear" if mode in x_dticks else None,
                     dtick=x_dticks.get(mode))
    fig.update_yaxes(title_text=f"Potencia Bateria ({units})", secondary_y=False,
                     zeroline=True, zerolinecolor=STUDIO_CHART_COLORS["neutral_soft"])
    fig.update_yaxes(title_text="Preu Energia (EUR/kWh)", secondary_y=True,
                     showgrid=False)

    fig.update_layout(
        title=f"Carrega/Descarrega Bateria vs Preu Energia – {mode.capitalize()} ({season})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return _apply_figure_theme(fig)
