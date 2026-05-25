"""Generació d'informes HTML i PDF per a les execucions de Studio completades.

El backend de l'informe comparteix els carregadors del panell de resultats i la figura Plotly
builders, després organitza els gràfics disponibles en un document estructurat. Figures
sense dades utilitzables es salten, de manera que els informes exportats reflecteixen els artefactes
produït realment per una tirada.
"""

from __future__ import annotations

import base64
import math
from dataclasses import dataclass
from datetime import datetime
from html import escape
from numbers import Number

import plotly.graph_objects as go

from backend.grafics.comfort_scope import comfort_scope_label
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
    make_setpoints_plot,
    make_setpoints_vs_indoor_plot,
)
from backend.grafics.figures_zones import filter_obs_by_zone
from backend.grafics.kpis import compute_kpis
from backend.resultats_backend import (
    DashboardData,
    add_comfort_percentage_kpi,
    has_action_figure_data,
    has_figure_data,
    load_dashboard_data,
    select_actions_for_obs,
    select_radiant_action_data,
)
from page_styles.reports import REPORT_HTML_CSS


@dataclass(frozen=True)
class ReportFigure:
    """Plotly gràfic més la secció d'informe on hauria d'aparèixer."""

    section: str
    title: str
    figure: go.Figure


def generate_report_bytes(
    progress_path: str,
    observations_path: str,
    agg_mode: str,
    season: str,
    comfort_scope: str,
    zone_str: str,
) -> tuple[bytes, str]:
    """Crea un informe que es pot descarregar per a una execució completada.

    La funció retorna PDF bytes quan ``pdfkit`` i ``wkhtmltopdf`` són
    disponible. Si la representació estàtica PDF no està disponible, retorna un informe HTML
    amb el mateix contingut perquè UI encara pugui oferir una exportació completa.
    """

    data = load_dashboard_data(progress_path, observations_path)
    selected_zone = None if zone_str in ("ALL", "") else zone_str
    zone_obs = filter_obs_by_zone(data.obs, selected_zone, data.yaml_cfg)
    action_data = select_actions_for_obs(data.actions, zone_obs)
    action_data = select_radiant_action_data(action_data, data)

    kpis = compute_kpis(
        obs=zone_obs,
        cost_hourly=data.metrics_dict.get("cost_hourly"),
        selected_zone=selected_zone,
        comfort_scope=comfort_scope,
        comfort_config=data.yaml_cfg,
    )
    kpis.pop("Avg Energy Cost (EUR/h)", None)
    add_comfort_percentage_kpi(kpis, zone_obs, data.yaml_cfg)

    figures = _build_report_figures(
        data=data,
        zone_obs=zone_obs,
        action_data=action_data,
        agg_mode=agg_mode,
        season=season,
        comfort_scope=comfort_scope,
    )
    return _render_report_document(
        data=data,
        kpis=kpis,
        figures=figures,
        agg_mode=agg_mode,
        season=season,
        selected_zone=selected_zone,
        comfort_scope=comfort_scope,
    )


def _build_report_figures(
    data: DashboardData,
    zone_obs,
    action_data,
    agg_mode: str,
    season: str,
    comfort_scope: str,
) -> tuple[ReportFigure, ...]:
    """Prepara les figures incloses en un informe de resultats exportat."""

    # L'informe reutilitza les mateixes factories del dashboard per evitar que PDF i UI
    # expliquin històries diferents.
    comfort_mode = "raw" if agg_mode == "day" else agg_mode
    pivot = data.metrics_dict.get("pivot_consumption")
    action_fig = make_agent_actions_plot(action_data, agg_mode, season)
    if not has_action_figure_data(action_fig):
        action_fig = go.Figure()

    return (
        ReportFigure(
            "Confort i clima interior",
            "Confort (%)",
            make_comfort_compliance(
                zone_obs,
                comfort_mode,
                season,
                comfort_scope=comfort_scope,
                comfort_config=data.yaml_cfg,
            ),
        ),
        ReportFigure(
            "Confort i clima interior",
            "Temperatura interior vs exterior",
            make_indoor_temperature_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Confort i clima interior",
            "Humitat interior vs exterior",
            make_indoor_humidity_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Confort i clima interior",
            "Infraccions de confort",
            _fix_colors_for_visibility(
                make_violation_bars(
                    zone_obs,
                    agg_mode,
                    season,
                    comfort_scope=comfort_scope,
                    comfort_config=data.yaml_cfg,
                ),
                kind="violation",
                mode=agg_mode,
            ),
        ),
        ReportFigure(
            "Confort i clima interior",
            "Mapa de calor d'infraccions de confort (%)",
            make_violation_heatmap_percent(
                zone_obs,
                season=season,
                comfort_config=data.yaml_cfg,
            ),
        ),
        ReportFigure(
            "Confort i clima interior",
            "Temperatura per zona (mes x hora)",
            make_zone_temperature_heatmaps(
                zone_obs,
                season=season,
                agg="mean",
                max_cols=3,
            ),
        ),
        ReportFigure(
            "Consum i energia",
            "Consum HVAC (kWh)",
            _fix_colors_for_visibility(
                make_hvac_consumption_plot(zone_obs, agg_mode, season),
                kind="hvac",
                mode=agg_mode,
            ),
        ),
        ReportFigure(
            "Consum i energia",
            "Desglossament HVAC per meter (kWh)",
            make_hvac_meter_breakdown_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Consum i energia",
            "Preu energia (EUR/kWh)",
            make_energy_price_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Consum i energia",
            "Mapa de calor global (consum)",
            (
                make_heatmap(pivot, "Total HVAC Consumption (kWh)")
                if pivot is not None and not pivot.empty
                else go.Figure()
            ),
        ),
        ReportFigure(
            "Control HVAC",
            "Actuació tèrmica (setpoints)",
            make_setpoints_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Control HVAC",
            "Setpoints vs temperatura interior",
            make_setpoints_vs_indoor_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Control HVAC",
            "Control radiant",
            make_radiant_control_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure("Control HVAC", "Accions de l'agent", action_fig),
        ReportFigure(
            "Bateria i xarxa",
            "Càrrega/descàrrega bateria",
            make_battery_power_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Bateria i xarxa",
            "SOC bateria",
            make_battery_soc_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Bateria i xarxa",
            "Energia bateria vs xarxa",
            make_battery_vs_grid_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Bateria i xarxa",
            "Bateria vs preu energia",
            make_battery_charge_with_price_plot(zone_obs, agg_mode, season),
        ),
        ReportFigure(
            "Episodi",
            "Mètriques d'episodi",
            make_episode_metrics(data.progress),
        ),
    )


def _render_report_document(
    data: DashboardData,
    kpis: dict,
    figures: tuple[ReportFigure, ...],
    agg_mode: str,
    season: str,
    selected_zone: str | None,
    comfort_scope: str,
) -> tuple[bytes, str]:
    """Genera l'informe HTML i el converteix a PDF quan pdfkit està disponible."""

    # Muntem primer HTML complet: és fàcil de revisar al navegador i després pdfkit el pot
    # convertir sense haver de mantenir una plantilla paral·lela.
    zone_label = selected_zone if selected_zone else "Totes"
    scope_label = comfort_scope_label(comfort_scope)
    rendered_figures, chart_count, static_charts = _render_report_figures(figures)
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    timesteps_label = f"{data.timesteps_num:,}".replace(",", ".")

    html_parts: list[str] = [f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Sinergym Dashboard Report</title>
  {REPORT_HTML_CSS}
</head>
<body>
  <main class="report-shell">
  <section class="cover">
    <p class="eyebrow">BEMS-RL Studio · Informe de resultats</p>
    <h1>Resum {escape(data.run_mode)} - Sinergym</h1>
    <p class="subtitle">
      Informe generat automàticament amb els indicadors principals i tots els gràfics
      disponibles per a l'execució seleccionada.
    </p>
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">Entorn</div>
        <div class="summary-value">{escape(data.env_name)}</div>
      </div>
      <div class="summary-item">
        <div class="summary-label">Timesteps</div>
        <div class="summary-value">{timesteps_label}</div>
      </div>
      <div class="summary-item">
        <div class="summary-label">Model</div>
        <div class="summary-value">{escape(data.model_name)}</div>
      </div>
      <div class="summary-item">
        <div class="summary-label">Gràfics inclosos</div>
        <div class="summary-value">{chart_count}</div>
      </div>
    </div>
  </section>

  <section class="filter-strip">
    <div class="filter-item">
      <div class="filter-label">Generat</div>
      <div class="filter-value">{generated_at}</div>
    </div>
    <div class="filter-item">
      <div class="filter-label">Agregació</div>
      <div class="filter-value">{escape(agg_mode.upper())}</div>
    </div>
    <div class="filter-item">
      <div class="filter-label">Estació</div>
      <div class="filter-value">{escape(season)}</div>
    </div>
    <div class="filter-item">
      <div class="filter-label">Zona / confort</div>
      <div class="filter-value">{escape(zone_label)} · {escape(scope_label)}</div>
    </div>
  </section>

  <h2 class="block-title">Indicadors clau</h2>
  <div class="kpi-row">"""]

    for key, value in kpis.items():
        value_string = _format_kpi_value(key, value)
        html_parts.append(
            f'<div class="kpi"><div class="kpi-val">{escape(value_string)}</div>'
            f'<div class="kpi-lbl">{escape(key)}</div></div>'
        )

    html_parts.append("</div>")
    if rendered_figures:
        html_parts.extend(rendered_figures)
    else:
        html_parts.append(
            '<div class="empty-note">No hi ha gràfics amb dades disponibles per als filtres seleccionats.</div>'
        )
    html_parts.append("</main></body></html>")
    html = "\n".join(html_parts)

    if static_charts:
        try:
            import pdfkit

            options = {
                "page-size": "A4",
                "margin-top": "0.45in",
                "margin-right": "0.45in",
                "margin-bottom": "0.45in",
                "margin-left": "0.45in",
                "encoding": "UTF-8",
                "enable-local-file-access": None,
                "disable-smart-shrinking": None,
                "quiet": "",
            }
            return pdfkit.from_string(html, False, options=options), "pdf"
        except Exception:
            pass

    return html.encode("utf-8"), "html"


def _format_kpi_value(key: str, value) -> str:
    """Formata els valors KPI de manera coherent per a l'informe exportat."""

    if value is None:
        return "N/D"
    if isinstance(value, Number):
        numeric = float(value)
        if not math.isfinite(numeric):
            return "N/D"
        if key.strip().startswith("%"):
            return f"{numeric:.1f}%"
        return f"{numeric:.2f}"
    return str(value)


def _render_report_figures(
    figures: tuple[ReportFigure, ...],
) -> tuple[list[str], int, bool]:
    """Retorna fragments seccionats de HTML per a cada figura d'informe amb dades visibles."""

    rendered: list[str] = []
    current_section: str | None = None
    chart_count = 0
    static_charts = True
    plotlyjs_included = False

    for item in figures:
        if not has_figure_data(item.figure):
            continue

        chart_html, is_static, plotlyjs_used = _render_single_report_figure(
            item,
            include_plotlyjs=not plotlyjs_included,
        )
        if chart_html is None:
            continue

        if item.section != current_section:
            if current_section is not None:
                rendered.append("</section>")
            current_section = item.section
            rendered.append(
                f'<section class="report-section"><h2 class="section-heading">'
                f"{escape(item.section)}</h2>"
            )

        rendered.append(chart_html)
        chart_count += 1
        static_charts = static_charts and is_static
        plotlyjs_included = plotlyjs_included or plotlyjs_used

    if current_section is not None:
        rendered.append("</section>")

    return rendered, chart_count, static_charts


def _render_single_report_figure(
    item: ReportFigure,
    *,
    include_plotlyjs: bool,
) -> tuple[str | None, bool, bool]:
    """Converteix una figura a imatge estàtica o, si cal, a HTML interactiu."""

    export_fig = _prepare_export_figure(item.figure)
    try:
        image_bytes = export_fig.to_image(format="png", engine="kaleido", scale=2)
        image_b64 = base64.b64encode(image_bytes).decode()
        return (
            f'<div class="chart"><h3>{escape(item.title)}</h3>'
            f'<img alt="{escape(item.title)}" src="data:image/png;base64,{image_b64}"></div>',
            True,
            False,
        )
    except Exception:
        try:
            chart_html = export_fig.to_html(
                full_html=False,
                include_plotlyjs=True if include_plotlyjs else False,
                config={"displayModeBar": False, "responsive": True},
            )
            return (
                f'<div class="chart"><h3>{escape(item.title)}</h3>{chart_html}</div>',
                False,
                include_plotlyjs,
            )
        except Exception:
            return None, False, False


def _prepare_export_figure(fig: go.Figure) -> go.Figure:
    """Copia i normalitzeu una figura Plotly per a la representació d'informes."""

    export_fig = style_figure_semantics(go.Figure(fig))
    current_height = export_fig.layout.height
    try:
        height = int(current_height) if current_height else 520
    except (TypeError, ValueError):
        height = 520
    height = max(460, min(height, 980))
    export_fig.update_layout(
        width=1100,
        height=height,
        margin=dict(l=66, r=36, t=78, b=58),
        font=dict(size=13, color="#17233c"),
        title=dict(
            text=export_fig.layout.title.text,
            x=0.01,
            xanchor="left",
            font=dict(size=18, color="#17233c"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#d7deeb",
            borderwidth=1,
        ),
    )
    return export_fig
