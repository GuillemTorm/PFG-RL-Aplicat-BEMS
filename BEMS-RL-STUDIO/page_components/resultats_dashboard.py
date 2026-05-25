"""Component del panell en línia per a la pàgina de resultats."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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
from backend.grafics.heatmaps import make_heatmap, make_zone_temperature_heatmaps
from backend.grafics.hvac import make_hvac_consumption_plot, make_hvac_meter_breakdown_plot
from backend.grafics.style import style_figure_semantics
from backend.grafics.thermal import (
    make_indoor_humidity_plot,
    make_indoor_temperature_plot,
    make_setpoints_plot,
    make_setpoints_vs_indoor_plot,
)
from backend.resultats_backend import (
    DashboardData,
    add_comfort_percentage_kpi,
    apply_real_period_axis,
    build_real_period_options,
    has_action_figure_data,
    has_figure_data,
    is_radiant_run,
    load_comparison_data,
    overlay_comparison_traces,
    select_actions_for_obs,
    select_radiant_action_data,
    slice_obs_for_real_period,
)
from backend.resultats_report_backend import generate_report_bytes
_AGG_LABELS = {
    "hour": "Horaria (0..23)",
    "day": "Diaria (1..365)",
    "month": "Mensual (1..12)",
    "raw": "Sense Agregació (Crua)",
}
_SEASON_LABELS = {
    "All": "Totes",
    "Winter": "Hivern (Des, Gen, Feb)",
    "Spring": "Primavera (Mar, Abr, Mai)",
    "Summer": "Estiu (Jun, Jul, Ago)",
    "Autumn": "Tardor (Set, Oct, Nov)",
}
_VIEW_MODE_LABELS = {
    "aggregate": "Mitjana / Agregat",
    "real": "Serie real",
}
_REAL_PERIOD_LABELS = {
    "day": "Un dia",
    "week": "Una setmana",
    "month": "Un mes",
}


class DashboardTabSpec(NamedTuple):
    """Declaració d'una pestanya del dashboard i les figures que conté."""

    label: str
    visibility_group: str
    copy_text: str
    figure_items: tuple[tuple[str, str], ...]


CONTROL_FIGURE_KEYS = ("setpoints", "setpoints_vs_indoor", "radiant", "actions")
BATTERY_FIGURE_KEYS = (
    "battery_power",
    "battery_soc",
    "battery_vs_grid",
    "battery_charge_price",
)
REAL_AXIS_FIGURE_KEYS = (
    "indoor",
    "humidity",
    "setpoints",
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
    "setpoints",
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
    "setpoints",
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
DASHBOARD_TAB_SPECS = (
    DashboardTabSpec(
        "Temperatura",
        "always",
        "Temperatura interior i exterior, percentatge d'hores en confort, infraccions tèrmiques "
        "i distribució de temperatura per zona i hora.",
        (
            ("comfort", "aggregate"),
            ("indoor", "always"),
            ("humidity", "always"),
            ("violation", "always"),
            ("zone_heatmap", "aggregate"),
        ),
    ),
    DashboardTabSpec(
        "Consum i Potència",
        "always",
        "Consum HVAC agregat, desglosament per meter, preu de l'energia i mapa de calor global "
        "del consum al llarg de l'any.",
        (
            ("hvac", "always"),
            ("hvac_breakdown", "always"),
            ("energy_price", "always"),
            ("heatmap", "aggregate"),
        ),
    ),
    DashboardTabSpec(
        "Control HVAC",
        "control",
        "Setpoints tèrmics, actuació del control radiant i accions que l'agent RL ha aplicat "
        "al sistema HVAC.",
        tuple((key, "always") for key in CONTROL_FIGURE_KEYS),
    ),
    DashboardTabSpec(
        "Bateria",
        "battery",
        "Cicles de càrrega i descàrrega, estat de càrrega (SOC), interacció amb la xarxa "
        "elèctrica i correlació amb el preu de l'energia.",
        tuple((key, "always") for key in BATTERY_FIGURE_KEYS),
    ),
    DashboardTabSpec(
        "Episodi",
        "always",
        "Mètriques de rendiment acumulades per episodi d'entrenament o avaluació.",
        (("episode", "aggregate"),),
    ),
)


def _file_signature(path: str) -> tuple[str, int, int]:
    """Retorna una signatura de memòria cau estable per a la ruta d'un fitxer."""

    file_path = Path(path)
    try:
        stat = file_path.stat()
    except OSError:
        return str(file_path), -1, -1
    return str(file_path), int(stat.st_mtime_ns), int(stat.st_size)


def _run_data_signature(progress_path: str, observations_path: str) -> tuple[object, ...]:
    """Retorna les entrades de memòria cau que canvien cada vegada que canvien les dades d'execució seleccionades."""

    run_dir = Path(progress_path).parent
    yaml_signatures = []
    try:
        yaml_signatures = [
            _file_signature(str(path))
            for path in sorted(run_dir.glob("*.yaml"))
        ]
    except OSError:
        yaml_signatures = []
    return (
        _file_signature(progress_path),
        _file_signature(observations_path),
        tuple(yaml_signatures),
    )


def _load_comparison_data_cached(run_path: str) -> DashboardData | None:
    """Carrega una comparació i la desa a la memòria cau de sessió."""

    cache_key = f"_comp_data_{hash(run_path)}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    data = load_comparison_data(run_path)
    if data is None:
        return None

    st.session_state[cache_key] = data
    return data

@st.cache_data(show_spinner="Generant informe...", max_entries=10)
def _cached_report_bytes(
    progress_path: str,
    observations_path: str,
    agg_mode: str,
    season: str,
    comfort_scope: str,
    zone_str: str,
    data_signature: tuple[object, ...],
) -> tuple[bytes, str]:
    """Retorna bytes d'informes a la memòria cau per als filtres del panell seleccionats."""

    return generate_report_bytes(
        progress_path=progress_path,
        observations_path=observations_path,
        agg_mode=agg_mode,
        season=season,
        comfort_scope=comfort_scope,
        zone_str=zone_str,
    )


def _plot_if_available(fig: go.Figure | None) -> None:
    """Mostra un gràfic Plotly només quan conté traces visibles."""

    if has_figure_data(fig):
        # Grafic dashboard
        st.plotly_chart(fig, width="stretch")


def _dashboard_tab_is_visible(spec: DashboardTabSpec, figures: dict[str, go.Figure]) -> bool:
    """Decideix si una pestanya té dades suficients per aparèixer al dashboard."""
    if spec.visibility_group == "control":
        return any(has_figure_data(figures[key]) for key in CONTROL_FIGURE_KEYS)
    if spec.visibility_group == "battery":
        return any(has_figure_data(figures[key]) for key in BATTERY_FIGURE_KEYS)
    return True


def _render_dashboard_tab_content(
    spec: DashboardTabSpec,
    figures: dict[str, go.Figure],
    *,
    view_mode: str,
) -> None:
    """Pinta el contingut d'una pestanya de resultats segons la seva especificació."""
    # Text pestanya dashboard
    st.markdown(
        f"<div class='results-tab-copy'>{escape(spec.copy_text)}</div>",
        unsafe_allow_html=True,
    )
    if spec.label == "Episodi":
        if view_mode == "aggregate" and has_figure_data(figures["episode"]):
            # Grafic episodi
            st.plotly_chart(figures["episode"], width="stretch")
            return
        # Avís episodi agregat
        st.info("Les mètriques d'episodi només estan disponibles en mode agregat.")
        return

    for key, mode_rule in spec.figure_items:
        if mode_rule == "aggregate" and view_mode != "aggregate":
            continue
        _plot_if_available(figures[key])


def _render_report_export(
    report_action_slot,
    data: DashboardData,
    *,
    plot_mode: str,
    plot_season: str,
    comfort_scope: str,
    zone_val: str | None,
) -> None:
    """Mostra els controls de generació i baixada d'informes."""

    with report_action_slot.container():
        zone_str = zone_val if zone_val else "ALL"
        data_signature = _run_data_signature(data.progress_path, data.observations_path)
        report_key = (
            data.progress_path,
            data.observations_path,
            plot_mode,
            plot_season,
            comfort_scope,
            zone_str,
            data_signature,
        )
        if st.session_state.get("_report_cache_key") != report_key:
            st.session_state.pop("_report_cache", None)
            st.session_state["_report_cache_key"] = report_key

        if "_report_cache" not in st.session_state:
            # Botó generar informe
            if st.button(
                "Generar informe",
                icon=":material/summarize:",
                key="btn_gen_report",
                width="stretch",
            ):
                with st.spinner("Generant informe..."):
                    st.session_state["_report_cache"] = _cached_report_bytes(
                        data.progress_path,
                        data.observations_path,
                        plot_mode,
                        plot_season,
                        comfort_scope,
                        zone_str,
                        data_signature,
                    )
                st.rerun()
            return

        report_bytes, report_ext = st.session_state["_report_cache"]
        mime = "application/pdf" if report_ext == "pdf" else "text/html"
        # Botó download informe
        st.download_button(
            f"Descarregar informe (.{report_ext})",
            data=report_bytes,
            file_name=f"Sinergym_Report_{data.env_name}_{plot_season}.{report_ext}",
            mime=mime,
            key="btn_download_report",
            width="stretch",
        )


def _render_dashboard_tabs(figures: dict[str, go.Figure], *, view_mode: str) -> None:
    """Mostra els gràfics de resultats amb la mateixa estructura de pestanyes del panell."""

    active_specs = [
        spec for spec in DASHBOARD_TAB_SPECS if _dashboard_tab_is_visible(spec, figures)
    ]
    # Pestanyes dashboard
    active_tabs = st.tabs([spec.label for spec in active_specs])
    for tab, spec in zip(active_tabs, active_specs):
        with tab:
            _render_dashboard_tab_content(
                spec,
                figures,
                view_mode=view_mode,
            )


def _build_dashboard_figures(
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

    # Generem totes les figures en un sol lloc perquè la comparació pugui aplicar el mateix
    # tractament a la run principal i a la run de referència.
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
        "setpoints": make_setpoints_plot(zobs, plot_mode, plot_season),
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


def _overlay_dashboard_figures(
    figures: dict[str, go.Figure],
    comparison_figures: dict[str, go.Figure],
    *,
    data: DashboardData,
    view_mode: str,
) -> dict[str, go.Figure]:
    """Superposeu traces de comparació a les xifres actives del panell."""

    overlay_keys = list(OVERLAY_FIGURE_KEYS)
    if view_mode == "aggregate":
        overlay_keys.extend(AGGREGATE_OVERLAY_KEYS)
    if is_radiant_run(data):
        overlay_keys.append("actions")

    for key in overlay_keys:
        figures[key] = overlay_comparison_traces(figures[key], comparison_figures[key])
    return figures


def _style_dashboard_figures(
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


_KPI_HIGHER_IS_BETTER = frozenset({"% Hores en Confort"})


def _kpi_delta_color(key: str) -> str:
    """Retorna el mode de color delta utilitzat per les targetes de comparació KPI."""
    if key in _KPI_HIGHER_IS_BETTER:
        return "normal"
    key_lower = key.lower()
    if "hvac" in key_lower or "violation" in key_lower:
        return "inverse"
    return "off"


def _render_kpis(kpis: dict, comp_kpis: dict | None) -> None:
    """Pinta les targetes KPI amb deltes de comparació opcionals."""
    kpi_items = [(k, v) for k, v in kpis.items()]
    if not kpi_items:
        return

    cards: list[str] = []
    for k, v in kpi_items:
        if v is None:
            val_str = "N/D"
        elif isinstance(v, float) and k.startswith("%"):
            val_str = f"{v:.1f}%"
        elif isinstance(v, (int, float)):
            val_str = f"{float(v):.2f}"
        else:
            val_str = str(v)

        delta_html = ""
        if comp_kpis is not None and k in comp_kpis:
            # El signe bo del delta depèn del KPI: menys cost o violació és millor,
            # però més confort pot ser positiu. _kpi_delta_color encapsula aquesta regla.
            cv = comp_kpis[k]
            if (
                isinstance(v, (int, float)) and isinstance(cv, (int, float))
                and v is not None and cv is not None
            ):
                delta = round(float(v) - float(cv), 2)
                color_hint = _kpi_delta_color(k)
                if color_hint == "inverse":
                    is_good = delta < 0
                elif color_hint == "normal":
                    is_good = delta > 0
                else:
                    is_good = None
                if delta == 0:
                    delta_class = "results-kpi-delta-neutral"
                    arrow = ""
                elif is_good is None:
                    delta_class = "results-kpi-delta-neutral"
                    arrow = "▲" if delta > 0 else "▼"
                elif is_good:
                    delta_class = "results-kpi-delta-good"
                    arrow = "▲" if delta > 0 else "▼"
                else:
                    delta_class = "results-kpi-delta-bad"
                    arrow = "▲" if delta > 0 else "▼"
                sign = "+" if delta > 0 else ""
                delta_html = (
                    f'<div class="results-kpi-delta {delta_class}">'
                    f'{arrow} {sign}{delta:.2f}</div>'
                )

        k_esc = escape(k)
        v_esc = escape(val_str)
        cards.append(
            f'<div class="results-kpi-card">'
            f'<div class="results-kpi-label" title="{k_esc}">{k_esc}</div>'
            f'<div class="results-kpi-value">{v_esc}</div>'
            f'{delta_html}'
            f'</div>'
        )

    # Targetes KPI
    st.markdown(
        '<section class="section-card results-kpi-shell">' + "".join(cards) + "</section>",
        unsafe_allow_html=True,
    )

def render_inline_dashboard(
    data: DashboardData,
    all_run_dirs: tuple,
    current_run_path: str,
) -> None:
    """Mostra el panell en línia complet per a una execució carregada a la UI de Streamlit."""

    from backend.grafics.figures_zones import filter_obs_by_zone
    from backend.grafics.kpis import compute_kpis

    # Separador dashboard
    st.markdown("---")

    # --- Capçalera del panell ---
    try:
        # Capçalera dashboard
        head_cols = st.columns([8, 2], gap="small", vertical_alignment="center")
    except TypeError:
        # Capçalera dashboard
        head_cols = st.columns([8, 2], gap="small")
    with head_cols[0]:
        # Titol dashboard
        st.markdown('<h2 class="section-title">Dashboard</h2>', unsafe_allow_html=True)
    with head_cols[1]:
        report_action_slot = st.empty()

    # Etiquetes resum dashboard
    st.markdown(
        f"""
        <div class="results-dashboard-header">
          <span class="results-dashboard-tag">
            <strong>Entorn</strong>&nbsp; {escape(data.env_name)}
          </span>
          <span class="results-dashboard-tag">
            <strong>Timesteps</strong>&nbsp; {data.timesteps_num:,}
          </span>
          <span class="results-dashboard-tag">
            <strong>Model</strong>&nbsp; {escape(data.model_name)}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Separador selector comparacio
    st.markdown("<div class='studio-spacer-075'></div>", unsafe_allow_html=True)

    # --- Selector de comparació ---
    comp_options = [("", "Cap (sense comparació)")] + [
        (r.path, str(r)) for r in all_run_dirs if r.path != current_run_path
    ]
    # Selector execucio comparacio
    comp_path = st.selectbox(
        "Execució de referència per a comparació",
        options=[p for p, _ in comp_options],
        format_func=lambda x: dict(comp_options).get(x, x),
        key="dash_comp_run",
    )

    comp_data: DashboardData | None = None
    if comp_path:
        with st.spinner("Carregant run de comparació..."):
            comp_data = _load_comparison_data_cached(comp_path)
        if comp_data is None:
            # Avís comparacio no carregada
            st.warning("No s'han pogut carregar les dades de la run de referència.")

    # Separador KPIs dashboard
    st.markdown("<div class='studio-spacer-075'></div>", unsafe_allow_html=True)

    # Llegim els filtres des de session_state abans de pintar els widgets. Així els KPI
    # surten a dalt de tot, però sempre calculats amb l'última selecció real de l'usuari.
    view_mode = st.session_state.get("dash_view_mode", "aggregate")
    agg_mode = "hour"
    season = "All"
    real_period_kind = st.session_state.get("dash_real_period_kind", "day")
    if real_period_kind not in _REAL_PERIOD_LABELS:
        real_period_kind = "month"
        st.session_state["dash_real_period_kind"] = real_period_kind
    real_period_value = ""
    real_period_label = None

    if view_mode == "aggregate":
        agg_mode = st.session_state.get("dash_agg_mode", "hour")
        season = st.session_state.get("dash_season", "All")
    else:
        agg_mode = "raw"
        real_period_value = st.session_state.get(
            f"dash_real_period_value_{real_period_kind}", ""
        )
        if not real_period_value:
            _period_opts = build_real_period_options(data.obs, real_period_kind)
            real_period_value = _period_opts[0][0] if _period_opts else ""

    _default_comfort_scope = (
        data.comfort_scope_options[0]["value"] if data.comfort_scope_options else "all"
    )
    comfort_scope = st.session_state.get("dash_comfort_scope", _default_comfort_scope)
    zone_val = st.session_state.get("dash_zone", "ALL")

    sel_zone = None if (not data.has_zones or zone_val == "ALL") else zone_val
    zobs = filter_obs_by_zone(data.obs, sel_zone, data.yaml_cfg)
    if view_mode == "real":
        zobs, real_period_label = slice_obs_for_real_period(
            zobs,
            real_period_kind,
            real_period_value,
        )
        if zobs.empty:
            # Avís periode real buit
            st.warning("No hi ha dades reals disponibles per al període seleccionat.")
            return
        # Text periode real
        st.caption(f"Comparant dades reals del període: {real_period_label}")
    action_data = select_actions_for_obs(data.actions, zobs)
    action_data = select_radiant_action_data(action_data, data)

    # KPI principals del període i la zona actius.
    kpis = compute_kpis(
        obs=zobs,
        cost_hourly=data.metrics_dict.get("cost_hourly"),
        selected_zone=sel_zone,
        comfort_scope=comfort_scope,
        comfort_config=data.yaml_cfg,
    )
    kpis.pop("Avg Energy Cost (EUR/h)", None)

    add_comfort_percentage_kpi(kpis, zobs, data.yaml_cfg)

    comp_kpis: dict | None = None
    comp_sel_zone = None
    comp_zobs = None
    comp_action_data = pd.DataFrame()
    if comp_data is not None:
        # La comparació intenta aplicar exactament el mateix filtre temporal i de zona.
        # Si la run de referència no té aquell any concret, fem fallback per mes/dia equivalent.
        comp_sel_zone = sel_zone if comp_data.has_zones else None
        comp_zobs = filter_obs_by_zone(comp_data.obs, comp_sel_zone, comp_data.yaml_cfg)
        if view_mode == "real":
            comp_zobs, comp_period_label = slice_obs_for_real_period(
                comp_zobs,
                real_period_kind,
                real_period_value,
                allow_fallback=True,
            )
            if comp_zobs.empty:
                # Avís referencia buida
                st.warning("La run de referència no té dades per al període real seleccionat.")
                comp_data = None
            elif comp_period_label and comp_period_label != real_period_label:
                # Text periode referencia
                st.caption(f"La referència s'ha alineat amb el període: {comp_period_label}")
        if comp_data is None:
            comp_zobs = None
        else:
            comp_action_data = select_actions_for_obs(comp_data.actions, comp_zobs)
            comp_action_data = select_radiant_action_data(comp_action_data, comp_data)
            comp_kpis = compute_kpis(
                obs=comp_zobs,
                cost_hourly=comp_data.metrics_dict.get("cost_hourly"),
                selected_zone=comp_sel_zone,
                comfort_scope=comfort_scope,
                comfort_config=comp_data.yaml_cfg,
            )
            comp_kpis.pop("Avg Energy Cost (EUR/h)", None)
            add_comfort_percentage_kpi(comp_kpis, comp_zobs, comp_data.yaml_cfg)
            # Text delta comparacio
            st.caption(
                f"Delta = execucio actual - referencia ({dict(comp_options).get(comp_path, comp_path)})"
            )

    # Pintem els KPI abans dels filtres: és una decisió de lectura, no de càlcul.
    _render_kpis(kpis, comp_kpis)

    # Separador filtres dashboard
    st.markdown("<div class='studio-spacer-075'></div>", unsafe_allow_html=True)

    # Els filtres es pinten sota els KPI perquè el panell funcioni com un resum primer
    # i com una eina d'exploració just després.
    # Filtres dashboard
    filter_cols = st.columns(5, gap="small")
    with filter_cols[0]:
        # Selector vista temporal
        st.selectbox(
            "Vista Temporal",
            options=list(_VIEW_MODE_LABELS.keys()),
            format_func=lambda x: _VIEW_MODE_LABELS[x],
            key="dash_view_mode",
        )
    with filter_cols[1]:
        if view_mode == "aggregate":
            # Selector agregacio temporal
            st.selectbox(
                "Agregació Temporal",
                options=["hour", "day", "month"],
                format_func=lambda x: _AGG_LABELS[x],
                key="dash_agg_mode",
            )
        else:
            # Selector periode real
            st.selectbox(
                "Període Real",
                options=list(_REAL_PERIOD_LABELS.keys()),
                format_func=lambda x: _REAL_PERIOD_LABELS[x],
                key="dash_real_period_kind",
            )
    with filter_cols[2]:
        if view_mode == "aggregate":
            # Selector estacio
            st.selectbox(
                "Filtrar per Estació",
                options=list(_SEASON_LABELS.keys()),
                format_func=lambda x: _SEASON_LABELS[x],
                key="dash_season",
            )
        else:
            real_period_options = build_real_period_options(data.obs, real_period_kind)
            if real_period_options:
                option_map = dict(real_period_options)
                # Selector valor periode
                st.selectbox(
                    "Selecciona el Període",
                    options=[value for value, _ in real_period_options],
                    format_func=lambda x: option_map.get(x, x),
                    key=f"dash_real_period_value_{real_period_kind}",
                )
            else:
                # Selector periode buit
                st.selectbox(
                    "Selecciona el Període",
                    options=["Sense dades disponibles"],
                    disabled=True,
                    key=f"dash_real_period_empty_{real_period_kind}",
                )
    with filter_cols[3]:
        scope_labels = {opt["value"]: opt["label"] for opt in data.comfort_scope_options}
        # Selector ambit confort
        st.selectbox(
            "Ambit de Confort",
            options=[opt["value"] for opt in data.comfort_scope_options],
            format_func=lambda x: scope_labels[x],
            key="dash_comfort_scope",
        )
    with filter_cols[4]:
        if data.has_zones:
            zone_labels = {opt["value"]: opt["label"] for opt in data.all_zone_options}
            # Selector zona
            st.selectbox(
                "Zona",
                options=[opt["value"] for opt in data.all_zone_options],
                format_func=lambda x: zone_labels[x],
                key="dash_zone",
            )
        else:
            # Selector zona global
            st.selectbox(
                "Zona",
                options=["Global (Totes)"],
                key="dash_zone",
                disabled=True,
            )

    # Separador grafics dashboard
    st.markdown("<div class='studio-spacer-100'></div>", unsafe_allow_html=True)

    # --- Construeix totes les figures del panell ---
    plot_mode = agg_mode
    plot_season = season
    figures = _build_dashboard_figures(
        data,
        zobs,
        action_data,
        plot_mode=plot_mode,
        plot_season=plot_season,
        comfort_scope=comfort_scope,
        view_mode=view_mode,
        real_period_kind=real_period_kind,
    )

    if comp_data is not None and comp_zobs is not None:
        comp_action_data = select_radiant_action_data(comp_action_data, comp_data)
        comparison_figures = _build_dashboard_figures(
            comp_data,
            comp_zobs,
            comp_action_data,
            plot_mode=plot_mode,
            plot_season=plot_season,
            comfort_scope=comfort_scope,
            view_mode=view_mode,
            real_period_kind=real_period_kind,
        )
        figures = _overlay_dashboard_figures(
            figures,
            comparison_figures,
            data=data,
            view_mode=view_mode,
        )

    figures = _style_dashboard_figures(figures, view_mode=view_mode)

    _render_report_export(
        report_action_slot,
        data,
        plot_mode=plot_mode,
        plot_season=plot_season,
        comfort_scope=comfort_scope,
        zone_val=zone_val,
    )

    _render_dashboard_tabs(figures, view_mode=view_mode)
