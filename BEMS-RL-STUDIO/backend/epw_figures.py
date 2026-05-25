"""Plotly creadors de figures per al visor de clima EPW."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.visor_epw_backend import (
    DEG,
    DEG_C,
    EPW_VARIABLES,
    KWH_PER_M2,
    MID_DOT,
    MONTH_ORDER,
    WH_PER_M2,
    WIND_DIRECTION_LABELS,
    variable_label,
)

MONTH_TICK_POSITIONS = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]


def ui_text(value: object) -> str:
    """Retorna el text segur per a la pantalla, reparant el mojibake habitual de les metadades EPW."""

    text = "" if value is None else str(value)
    for _ in range(2):
        if not any(marker in text for marker in ("Ã", "Â", "â")):
            break
        try:
            repaired = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if repaired == text:
            break
        text = repaired
    return text


def build_active_month_axis(data_frame: pd.DataFrame) -> tuple[list[int], list[str]]:
    """Retorna les posicions de marca del mes que coincideixen amb les dades EPW visibles actualment."""

    month_frame = (
        data_frame[["month", "month_label", "day_of_year"]]
        .dropna(subset=["month", "day_of_year"])
        .sort_values(["month", "day_of_year"])
        .drop_duplicates(subset=["month"])
    )
    if month_frame.empty:
        return MONTH_TICK_POSITIONS, MONTH_ORDER

    tick_values = month_frame["day_of_year"].astype(int).tolist()
    tick_labels = month_frame["month_label"].astype(str).tolist()
    return tick_values, tick_labels


def apply_figure_style(fig: go.Figure, title: str, *, legend: bool = True, height: int = 400) -> go.Figure:
    """Aplica l'estil visual compartit a una figura Plotly."""

    top_margin = 82 if legend else 58
    fig.update_layout(
        title=dict(
            text=ui_text(title),
            x=0.02,
            xanchor="left",
            y=0.98,
            yanchor="top",
            font=dict(size=15),
        ),
        height=height,
        margin=dict(l=12, r=12, t=top_margin, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(247,249,254,0.75)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.78)",
        ),
        showlegend=legend,
        font=dict(family="Bahnschrift, Aptos, Segoe UI, sans-serif", color="#17233c"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(204, 214, 235, 0.55)", zeroline=False)
    return fig


def build_focus_timeseries_figure(series_frame: pd.DataFrame, variable_key: str, aggregation_label: str) -> go.Figure:
    """Crea la sèrie temporal agregada per a la variable EPW seleccionada."""

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series_frame["timestamp"],
            y=series_frame[variable_key],
            mode="lines",
            name=ui_text(variable_label(variable_key, aggregated=aggregation_label != "Hora")),
            line=dict(color=EPW_VARIABLES[variable_key]["color"], width=2.3),
            fill="tozeroy" if EPW_VARIABLES[variable_key]["aggregate"] == "sum" else None,
            fillcolor="rgba(95, 84, 249, 0.10)" if EPW_VARIABLES[variable_key]["aggregate"] == "sum" else None,
            connectgaps=False,
        )
    )
    fig.update_xaxes(title_text="Calendari EPW")
    return apply_figure_style(fig, f"S\u00e8rie temporal {MID_DOT} {aggregation_label}", height=390)


def build_monthly_climate_figure(monthly_frame: pd.DataFrame) -> go.Figure:
    """Crea la comparació mensual de temperatura i humitat."""

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=monthly_frame["month_label"],
            y=monthly_frame["dry_bulb_max"],
            mode="lines",
            line=dict(color="rgba(242, 107, 91, 0.18)", width=0.1),
            showlegend=False,
            hoverinfo="skip",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_frame["month_label"],
            y=monthly_frame["dry_bulb_min"],
            mode="lines",
            line=dict(color="rgba(242, 107, 91, 0.18)", width=0.1),
            fill="tonexty",
            fillcolor="rgba(242, 107, 91, 0.14)",
            name="Rang",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_frame["month_label"],
            y=monthly_frame["dry_bulb_mean"],
            mode="lines+markers",
            name="Temp. seca",
            line=dict(color="#f26b5b", width=2.5),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=monthly_frame["month_label"],
            y=monthly_frame["relative_humidity_mean"],
            name="Humitat",
            marker_color="rgba(79, 142, 247, 0.65)",
        ),
        secondary_y=True,
    )
    apply_figure_style(fig, "Climatologia mensual", height=380)
    fig.update_yaxes(title_text=f"Temperatura ({DEG_C})", secondary_y=False)
    fig.update_yaxes(title_text="Humitat relativa (%)", secondary_y=True)
    return fig


def build_monthly_solar_figure(monthly_frame: pd.DataFrame) -> go.Figure:
    """Crea el resum mensual de radiació solar acumulada."""

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly_frame["month_label"],
            y=monthly_frame["global_horizontal_radiation_kwh_m2"],
            name="GHI",
            marker_color="#f3a738",
        )
    )
    fig.add_trace(
        go.Bar(
            x=monthly_frame["month_label"],
            y=monthly_frame["direct_normal_radiation_kwh_m2"],
            name="DNI",
            marker_color="#ef7d57",
        )
    )
    fig.add_trace(
        go.Bar(
            x=monthly_frame["month_label"],
            y=monthly_frame["diffuse_horizontal_radiation_kwh_m2"],
            name="DHI",
            marker_color="#f9cb40",
        )
    )
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=KWH_PER_M2)
    return apply_figure_style(fig, "Radiaci\u00f3 solar mensual", height=380)


def build_daily_temperature_band_figure(daily_frame: pd.DataFrame) -> go.Figure:
    """Crea la banda diària de temperatura amb mínims, mitjanes i màxims."""

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_frame["date"],
            y=daily_frame["dry_bulb_max"],
            mode="lines",
            line=dict(color="rgba(242, 107, 91, 0.16)", width=0.1),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_frame["date"],
            y=daily_frame["dry_bulb_min"],
            mode="lines",
            line=dict(color="rgba(79, 142, 247, 0.16)", width=0.1),
            fill="tonexty",
            fillcolor="rgba(95, 84, 249, 0.16)",
            name="Rang diari",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_frame["date"],
            y=daily_frame["dry_bulb_mean"],
            mode="lines",
            name="Mitjana",
            line=dict(color="#5f54f9", width=2),
        )
    )
    fig.update_yaxes(title_text=DEG_C)
    return apply_figure_style(fig, "Banda di\u00e0ria de temperatura", height=360)


def build_hourly_profile_figure(hourly_frame: pd.DataFrame) -> go.Figure:
    """Crea el perfil horari mitjà de temperatura, punt de rosada i humitat."""

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=hourly_frame["hour_start"],
            y=hourly_frame["dry_bulb_mean"],
            mode="lines+markers",
            name="Temp.",
            line=dict(color="#f26b5b", width=2.4),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=hourly_frame["hour_start"],
            y=hourly_frame["dew_point_mean"],
            mode="lines",
            name="Rosada",
            line=dict(color="#ffb347", width=2, dash="dot"),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=hourly_frame["hour_start"],
            y=hourly_frame["relative_humidity_mean"],
            mode="lines",
            name="Humitat",
            line=dict(color="#4f8ef7", width=2.2),
        ),
        secondary_y=True,
    )
    apply_figure_style(fig, "Perfil horari mitj\u00e0", height=360)
    fig.update_xaxes(title_text="Hora del dia")
    fig.update_yaxes(title_text=f"Temperatura ({DEG_C})", secondary_y=False)
    fig.update_yaxes(title_text="Humitat relativa (%)", secondary_y=True)
    return fig


def build_heatmap_figure(heatmap_frame: pd.DataFrame, variable_key: str) -> go.Figure:
    """Crea un mapa de calor mes a hora per a la variable EPW seleccionada."""

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=heatmap_frame.values,
                x=[int(hour) for hour in heatmap_frame.columns],
                y=list(heatmap_frame.index),
                colorscale="Blues" if variable_key == "relative_humidity_pct" else "Turbo",
                colorbar=dict(title=ui_text(variable_label(variable_key))),
                hovertemplate="Mes %{y}<br>Hora %{x}:00<br>Valor %{z:.2f}<extra></extra>",
            )
        ]
    )
    fig.update_xaxes(title_text="Hora del dia")
    fig.update_yaxes(title_text="Mes")
    return apply_figure_style(
        fig,
        f"Mapa de calor {MID_DOT} {ui_text(EPW_VARIABLES[variable_key]['label'])}",
        legend=False,
        height=390,
    )


def build_annual_heatmap_figure(
    heatmap_frame: pd.DataFrame,
    variable_key: str,
    *,
    tick_values: list[int] | None = None,
    tick_labels: list[str] | None = None,
) -> go.Figure:
    """Crea un mapa de calor anual hora a dia per a l'escaneig a escala del panell."""

    title_map = {
        "dry_bulb_c": f"Temperature ({DEG_C})",
        "direct_normal_radiation_wh_m2": f"Direct Radiation ({WH_PER_M2})",
        "wind_speed_m_s": "Wind Speed (m/s)",
        "relative_humidity_pct": "Relative Humidity (%)",
    }
    color_scale_map = {
        "dry_bulb_c": "RdBu_r",
        "direct_normal_radiation_wh_m2": "YlOrRd",
        "wind_speed_m_s": "Greens",
        "relative_humidity_pct": "Blues",
    }

    # Redueix l'escala a quantils robusts perquè els valors atípics aïllats no aplanin el mapa de calor.
    numeric_values = pd.DataFrame(heatmap_frame).to_numpy(dtype=float)
    flattened = pd.Series(numeric_values.reshape(-1)).dropna()
    if flattened.empty:
        return go.Figure()

    zmin = float(flattened.quantile(0.02))
    zmax = float(flattened.quantile(0.98))
    if variable_key == "dry_bulb_c":
        bound = max(abs(zmin), abs(zmax), 1.0)
        zmin = -bound
        zmax = bound
    elif zmin == zmax:
        zmin -= 1.0
        zmax += 1.0

    x_values = [int(column) for column in heatmap_frame.columns]
    fig = go.Figure(
        data=[
            go.Heatmap(
                z=heatmap_frame.values,
                x=x_values,
                y=list(heatmap_frame.index),
                zmin=zmin,
                zmax=zmax,
                colorscale=color_scale_map.get(variable_key, "Turbo"),
                colorbar=dict(title=ui_text(EPW_VARIABLES[variable_key]["unit"]), len=0.78, thickness=11),
                hovertemplate="Dia %{x}<br>Hora %{y}:00<br>Valor %{z:.2f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=ui_text(title_map.get(variable_key, variable_label(variable_key))),
        height=220,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(247,249,254,0.75)",
        font=dict(family="Bahnschrift, Aptos, Segoe UI, sans-serif", color="#17233c"),
    )
    fig.update_xaxes(
        tickmode="array",
        tickvals=tick_values or MONTH_TICK_POSITIONS,
        ticktext=tick_labels or MONTH_ORDER,
        showgrid=False,
        zeroline=False,
        range=[min(x_values), max(x_values)] if x_values else None,
    )
    fig.update_yaxes(
        title_text="Hora",
        tickmode="array",
        tickvals=[0, 6, 12, 18, 23],
        showgrid=False,
        zeroline=False,
        autorange="reversed",
    )
    return fig


def build_comfort_radiation_figure(radiation_frame: pd.DataFrame) -> go.Figure:
    """Crea el mapa polar de radiació amb efectes de confort per orientació."""

    if radiation_frame.empty:
        return go.Figure()

    ordered_frame = radiation_frame.sort_values(["radius_start", "theta_deg"]).reset_index(drop=True)
    band_order = list(dict.fromkeys(ordered_frame["altitude_band"].tolist()))
    # La gamma simètrica separa els efectes positius i negatius sobre el confort.
    max_abs = max(
        abs(float(ordered_frame["comfort_radiation_kwh_m2"].min())),
        abs(float(ordered_frame["comfort_radiation_kwh_m2"].max())),
        1.0,
    )

    fig = go.Figure()
    for band_index, altitude_band in enumerate(band_order):
        # Cada banda es dibuixa com un segment polar anular a l'altitud solar corresponent.
        band_frame = ordered_frame[ordered_frame["altitude_band"] == altitude_band]
        fig.add_trace(
            go.Barpolar(
                r=band_frame["radius_size"],
                theta=band_frame["theta_deg"],
                base=band_frame["radius_start"],
                width=[22.5] * len(band_frame),
                marker=dict(
                    color=band_frame["comfort_radiation_kwh_m2"],
                    colorscale=[[0.0, "#1f9d55"], [0.5, "#f4ddaf"], [1.0, "#d94d41"]],
                    cmin=-max_abs,
                    cmax=max_abs,
                    showscale=band_index == len(band_order) - 1,
                    colorbar=dict(title=KWH_PER_M2, len=0.78, thickness=11),
                ),
                customdata=list(
                    zip(
                        band_frame["altitude_band"],
                        band_frame["comfort_radiation_kwh_m2"],
                        band_frame["incident_radiation_kwh_m2"],
                    )
                ),
                hovertemplate=(
                    "%{theta}<br>"
                    "Banda solar %{customdata[0]}<br>"
                    f"Balanç de confort %{{customdata[1]:.1f}} {KWH_PER_M2}<br>"
                    f"Radiació captada %{{customdata[2]:.1f}} {KWH_PER_M2}<extra></extra>"
                ),
                opacity=0.94,
                showlegend=False,
            )
        )

    fig.update_layout(
        title=f"Benefit/Harm Radiation ({KWH_PER_M2})",
        height=390,
        margin=dict(l=10, r=10, t=46, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Bahnschrift, Aptos, Segoe UI, sans-serif", color="#17233c"),
        polar=dict(
            bgcolor="rgba(247,249,254,0.75)",
            radialaxis=dict(
                range=[0, 90],
                tickmode="array",
                tickvals=[15, 30, 45, 60, 75, 90],
                ticktext=[f"15{DEG}", f"30{DEG}", f"45{DEG}", f"60{DEG}", f"75{DEG}", f"90{DEG}"],
                gridcolor="rgba(204,214,235,0.45)",
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickmode="array",
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
            ),
        ),
    )
    return fig


def build_monthly_wind_rose_grid_figure(monthly_rose_tables: dict[str, pd.DataFrame]) -> go.Figure:
    """Construeix una graella compacta de roses dels vents mensuals."""

    month_items = list(monthly_rose_tables.items())
    if not month_items:
        return go.Figure()

    max_frequency = max(
        (float(frame["frequency_pct"].max()) for _, frame in month_items if not frame.empty),
        default=1.0,
    )
    max_speed = max((float(frame["mean_speed"].max()) for _, frame in month_items if not frame.empty), default=1.0)
    if max_frequency <= 0:
        max_frequency = 1.0
    if max_speed <= 0:
        max_speed = 1.0

    # Fem una graella màxima de quatre columnes perquè els dotze mesos càpiguen sense
    # convertir cada rosa del vent en una miniatura il·legible.
    columns = min(4, max(1, len(month_items)))
    rows = max(1, math.ceil(len(month_items) / columns))
    specs = [[{"type": "polar"} for _ in range(columns)] for _ in range(rows)]
    subplot_titles = [month_label for month_label, _ in month_items]
    empty_slots = rows * columns - len(subplot_titles)
    if empty_slots > 0:
        subplot_titles.extend([""] * empty_slots)

    fig = make_subplots(
        rows=rows,
        cols=columns,
        specs=specs,
        subplot_titles=subplot_titles,
        horizontal_spacing=0.05,
        vertical_spacing=0.12,
    )

    for month_index, (month_label, rose_frame) in enumerate(month_items):
        row = month_index // columns + 1
        col = month_index % columns + 1
        ordered_frame = rose_frame.copy()
        # Ordenem les direccions manualment; si no, Plotly les podria ordenar alfabèticament.
        ordered_frame["direction"] = pd.Categorical(
            ordered_frame["direction"],
            categories=list(WIND_DIRECTION_LABELS),
            ordered=True,
        )
        ordered_frame = ordered_frame.sort_values("direction")

        fig.add_trace(
            go.Barpolar(
                r=ordered_frame["frequency_pct"],
                theta=ordered_frame["direction"].astype(str),
                marker=dict(
                    color=ordered_frame["mean_speed"],
                    colorscale="Turbo",
                    cmin=0.0,
                    cmax=max_speed,
                    showscale=month_index == len(month_items) - 1,
                    colorbar=dict(title="m/s", len=0.44, thickness=10, y=0.18),
                ),
                opacity=0.9,
                hovertemplate=(
                    f"{month_label}<br>"
                    "%{theta}<br>"
                    "Freq. %{r:.1f}%<br>"
                    "Vent mitjà %{marker.color:.2f} m/s<extra></extra>"
                ),
                showlegend=False,
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        title="Wind Rose",
        height=245 * rows + 105,
        margin=dict(l=10, r=10, t=70, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Bahnschrift, Aptos, Segoe UI, sans-serif", color="#17233c"),
    )
    fig.update_annotations(
        font=dict(size=11, color="#17233c"),
        yshift=14,
    )

    for polar_index in range(1, len(month_items) + 1):
        polar_name = "polar" if polar_index == 1 else f"polar{polar_index}"
        fig.layout[polar_name].update(
            bgcolor="rgba(247,249,254,0.75)",
            radialaxis=dict(
                range=[0, max_frequency],
                showticklabels=False,
                ticks="",
                gridcolor="rgba(204,214,235,0.35)",
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickmode="array",
                tickvals=[0, 90, 180, 270],
                ticktext=["N", "E", "S", "W"],
                tickfont=dict(size=8),
            ),
        )

    return fig
