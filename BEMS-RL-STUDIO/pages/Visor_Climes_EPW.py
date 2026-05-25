from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from page_components.ui_fragments import (
    render_copy_block,
    render_detail_list_card,
    render_hero,
    render_metric_card_grid,
)
from page_styles.visor_climes_epw import inject_epw_viewer_styles
from sidebar_nav import configure_studio_page

from backend import visor_epw_backend as epw_backend
from backend.epw_figures import (
    build_active_month_axis,
    build_annual_heatmap_figure,
    build_comfort_radiation_figure,
    build_daily_temperature_band_figure,
    build_focus_timeseries_figure,
    build_heatmap_figure,
    build_hourly_profile_figure,
    build_monthly_climate_figure,
    build_monthly_solar_figure,
    build_monthly_wind_rose_grid_figure,
    ui_text,
)
from backend.mapa_backend import render_location_map


PAGE_TITLE = "Visor de Climes EPW"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Selecciona un fitxer climàtic EPW i explora'n les sèries temporals, "
    "els patrons mensuals i els indicadors ambientals des d'un dashboard integrat."
)


PLOTLY_CHART_CONFIG = {"displayModeBar": False}


@dataclass(frozen=True)
class EpwDashboardState:
    """Dades preparades necessàries per representar les pestanyes del panell EPW."""

    selected_entry: dict[str, str]
    metadata: dict[str, object]
    full_metrics: dict[str, float]
    filtered_metrics: dict[str, float]
    month_tick_values: list[int]
    month_tick_labels: list[str]
    series_variable: str
    series_aggregation: str
    heatmap_variable: str
    secondary_heatmap_variable: str
    records_message: str
    monthly_frame: pd.DataFrame
    focus_series: pd.DataFrame
    daily_temperature: pd.DataFrame
    hourly_profile: pd.DataFrame
    heatmap_frame: pd.DataFrame
    radiation_heatmap_frame: pd.DataFrame
    annual_temperature_heatmap: pd.DataFrame
    annual_direct_radiation_heatmap: pd.DataFrame
    annual_wind_heatmap: pd.DataFrame
    annual_humidity_heatmap: pd.DataFrame
    comfort_radiation_frame: pd.DataFrame
    monthly_wind_rose_tables: dict[str, pd.DataFrame]
    download_frame: pd.DataFrame
    metric_cards: list[tuple[str, str]]


def format_number(value: float | int | None, *, decimals: int = 1, suffix: str = "") -> str:
    """Formata un valor numèric amb separadors catalans i un sufix opcional."""

    if value is None or pd.isna(value):
        return "-"
    if decimals == 0:
        return f"{int(round(float(value))):,}{suffix}".replace(",", ".")
    return (
        f"{float(value):,.{decimals}f}{suffix}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def data_frame_has_plot_values(
    data_frame: pd.DataFrame,
    columns: list[str] | None = None,
    *,
    require_non_zero: bool = False,
) -> bool:
    """Retorna si un DataFrame conté valors numèrics que val la pena dibuixar."""

    if data_frame.empty:
        return False

    if columns is None:
        values = data_frame
    else:
        available_columns = [column for column in columns if column in data_frame.columns]
        if not available_columns:
            return False
        values = data_frame[available_columns]

    numeric_values = values.select_dtypes(include="number")
    if numeric_values.empty:
        numeric_values = values.apply(pd.to_numeric, errors="coerce")

    valid_values = numeric_values.stack().dropna()
    if valid_values.empty:
        return False

    if require_non_zero:
        return bool((valid_values.abs() > 0).any())

    return True


def wind_rose_tables_have_plot_values(monthly_rose_tables: dict[str, pd.DataFrame]) -> bool:
    """Indica si almenys una taula mensual de roses dels vents conté freqüències de vent."""

    for rose_frame in monthly_rose_tables.values():
        if data_frame_has_plot_values(rose_frame, ["frequency_pct"], require_non_zero=True):
            return True
    return False


def render_detail_card(
    metadata: dict[str, object],
    selected_entry: dict[str, str],
    total_records: int,
    filtered_records: int,
) -> None:
    """Mostra la targeta de metadades del fitxer EPW seleccionada a la UI de Streamlit."""

    detail_rows = [
        ("Fitxer", ui_text(metadata.get("file_name", "-"))),
        ("Ruta relativa", ui_text(selected_entry.get("relative_path", "-"))),
        ("Ciutat", ui_text(metadata.get("city", "-"))),
        ("País", ui_text(metadata.get("country", "-"))),
        ("Font", ui_text(metadata.get("source", "-"))),
        ("WMO", ui_text(metadata.get("wmo", "-"))),
        ("Latitud", format_number(metadata.get("latitude"), decimals=3)),
        ("Longitud", format_number(metadata.get("longitude"), decimals=3)),
        ("Fus horari", f"UTC {format_number(metadata.get('timezone'), decimals=1)}"),
        ("Elevació", f"{format_number(metadata.get('elevation_m'), decimals=0)} m"),
        ("Registres", f"{filtered_records:,} / {total_records:,}".replace(",", ".")),
        ("Classificació", ui_text(metadata.get("climate_family", "-"))),
    ]
    render_detail_list_card(
        title="Context del fitxer",
        rows=detail_rows,
        card_class="epw-detail-card",
        title_class="epw-card-title",
        list_class="epw-detail-list",
        row_class="epw-detail-row",
        label_class="epw-detail-label",
        value_class="epw-detail-value",
    )


def build_map_chart(metadata: dict[str, object]) -> None:
    """Dibuixa un mapa centrat a les coordenades de l'estació meteorològica EPW."""

    latitude = metadata.get("latitude")
    longitude = metadata.get("longitude")
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        # Avís mapa EPW
        st.info("Aquest fitxer EPW no té coordenades vàlides per mostrar al mapa.")
        return

    city = ui_text(metadata.get("city", "-"))
    country = ui_text(metadata.get("country", "-"))
    file_name = ui_text(metadata.get("file_name", "-"))
    render_location_map(
        latitude,
        longitude,
        zoom=4.5,
        color=(95, 84, 249, 220),
        radius=22000,
        tooltip_html=f"<b>{file_name}</b><br/>{city}, {country}",
    )


def configure_epw_dashboard_page() -> None:
    """Configura Chrome de la pàgina global i renderitza l'heroi EPW."""

    configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
    inject_epw_viewer_styles()
    render_hero("epw-hero", "Visualització climàtica", PAGE_TITLE, ui_text(INTRODUCTION_TEXT))


def select_epw_entry() -> tuple[dict[str, str], dict[str, object], pd.DataFrame]:
    """Mostra els controls de cerca i carrega el paquet EPW seleccionat."""

    weather_root = epw_backend.WEATHER_ROOT
    catalog = epw_backend.list_epw_catalog(str(weather_root))
    if not catalog:
        # Avís sense EPW
        st.warning(f"No s'han trobat fitxers EPW a `{weather_root}`.")
        st.stop()

    # Controls cerca EPW
    search_cols = st.columns([1.15, 2.1], gap="medium")
    with search_cols[0]:
        # Input cerca EPW
        search_query = st.text_input(
            "Cerca un fitxer EPW",
            placeholder="Ex: Granada, Lisboa, IWEC...",
        ).strip().lower()

    filtered_catalog = tuple(
        entry
        for entry in catalog
        if not search_query or search_query in entry["search_blob"]
    )
    if not filtered_catalog:
        # Avís filtre EPW buit
        st.warning("Cap fitxer EPW coincideix amb el filtre de cerca.")
        st.stop()

    entry_by_path = {entry["path"]: entry for entry in filtered_catalog}
    with search_cols[1]:
        # Selector fitxer EPW
        selected_path = st.selectbox(
            "Fitxer climàtic",
            list(entry_by_path),
            format_func=lambda option: ui_text(entry_by_path[option]["display_name"]),
        )

    bundle = epw_backend.load_epw_bundle(selected_path)
    return entry_by_path[selected_path], bundle["metadata"], bundle["data"]


def build_metric_card_values(filtered_metrics: dict[str, float]) -> list[tuple[str, str]]:
    """Crea valors de visualització per a les targetes EPW de resum KPI."""

    return [
        (
            "Temperatura mitjana",
            f"{format_number(filtered_metrics['mean_temp'], decimals=1)} {epw_backend.DEG_C}",
        ),
        (
            "Interval tèrmic",
            f"{format_number(filtered_metrics['min_temp'], decimals=1)} - "
            f"{format_number(filtered_metrics['max_temp'], decimals=1)} {epw_backend.DEG_C}",
        ),
        ("Humitat mitjana", f"{format_number(filtered_metrics['mean_rh'], decimals=1)} %"),
        ("Vent mitjà", f"{format_number(filtered_metrics['mean_wind'], decimals=2)} m/s"),
        (
            "GHI acumulada",
            f"{format_number(filtered_metrics['ghi_total_kwh_m2'], decimals=1)} {epw_backend.KWH_PER_M2}",
        ),
        ("Vent màxim", f"{format_number(filtered_metrics['max_wind'], decimals=2)} m/s"),
        (
            "DNI acumulada",
            f"{format_number(filtered_metrics['dni_total_kwh_m2'], decimals=1)} {epw_backend.KWH_PER_M2}",
        ),
        (
            "DHI acumulada",
            f"{format_number(filtered_metrics['dhi_total_kwh_m2'], decimals=1)} {epw_backend.KWH_PER_M2}",
        ),
    ]


def prepare_epw_dashboard_state(
    selected_entry: dict[str, str],
    metadata: dict[str, object],
    epw_data: pd.DataFrame,
) -> EpwDashboardState:
    """Crea totes les taules i etiquetes derivades necessàries per al panell EPW."""

    filtered_data = epw_data.copy()
    full_metrics = epw_backend.summarize_epw_metrics(epw_data)
    filtered_metrics = epw_backend.summarize_epw_metrics(filtered_data)
    month_tick_values, month_tick_labels = build_active_month_axis(filtered_data)

    series_variable = "dry_bulb_c"
    series_aggregation = "Dia"
    heatmap_variable = "dry_bulb_c"
    secondary_heatmap_variable = "direct_normal_radiation_wh_m2"
    records_message = (
        f"Mostrant {int(filtered_metrics['records']):,} registres de "
        f"{int(full_metrics['records']):,} sobre l'any EPW complet."
    ).replace(",", ".")

    return EpwDashboardState(
        selected_entry=selected_entry,
        metadata=metadata,
        full_metrics=full_metrics,
        filtered_metrics=filtered_metrics,
        month_tick_values=month_tick_values,
        month_tick_labels=month_tick_labels,
        series_variable=series_variable,
        series_aggregation=series_aggregation,
        heatmap_variable=heatmap_variable,
        secondary_heatmap_variable=secondary_heatmap_variable,
        records_message=records_message,
        monthly_frame=epw_backend.build_monthly_summary(filtered_data),
        focus_series=epw_backend.aggregate_epw_timeseries(
            filtered_data,
            series_variable,
            series_aggregation,
        ),
        daily_temperature=epw_backend.build_daily_temperature_profile(filtered_data),
        hourly_profile=epw_backend.build_hourly_profile(filtered_data),
        heatmap_frame=epw_backend.build_heatmap_table(filtered_data, heatmap_variable),
        radiation_heatmap_frame=epw_backend.build_heatmap_table(
            filtered_data,
            secondary_heatmap_variable,
        ),
        annual_temperature_heatmap=epw_backend.build_annual_hourly_heatmap_table(
            filtered_data,
            "dry_bulb_c",
        ),
        annual_direct_radiation_heatmap=epw_backend.build_annual_hourly_heatmap_table(
            filtered_data,
            "direct_normal_radiation_wh_m2",
        ),
        annual_wind_heatmap=epw_backend.build_annual_hourly_heatmap_table(
            filtered_data,
            "wind_speed_m_s",
        ),
        annual_humidity_heatmap=epw_backend.build_annual_hourly_heatmap_table(
            filtered_data,
            "relative_humidity_pct",
        ),
        comfort_radiation_frame=epw_backend.build_comfort_radiation_table(filtered_data, metadata),
        monthly_wind_rose_tables=epw_backend.build_monthly_wind_rose_tables(filtered_data),
        download_frame=epw_backend.build_download_frame(filtered_data),
        metric_cards=build_metric_card_values(filtered_metrics),
    )


def render_tab_intro(text: str) -> None:
    """Mostra un text breu al començament de cada pestanya EPW."""

    render_copy_block("epw-tab-copy", text, formatter=ui_text)


def render_annual_heatmap(
    frame: pd.DataFrame,
    variable_key: str,
    state: EpwDashboardState,
    empty_message: str,
    *,
    require_non_zero: bool = False,
) -> None:
    """Mostra un mapa de calor anual quan la taula d'origen té valors útils."""
    render_epw_chart(
        frame,
        None,
        lambda: build_annual_heatmap_figure(
            frame,
            variable_key,
            tick_values=state.month_tick_values,
            tick_labels=state.month_tick_labels,
        ),
        empty_message,
        require_non_zero=require_non_zero,
    )


def render_epw_chart(
    frame: pd.DataFrame,
    columns: list[str] | None,
    figure_builder,
    empty_message: str,
    *,
    require_non_zero: bool = False,
) -> None:
    """Mostra un gràfic EPW quan les dades tenen valors, o un avís si no."""
    if data_frame_has_plot_values(frame, columns, require_non_zero=require_non_zero):
        # Grafic EPW
        st.plotly_chart(
            figure_builder(),
            width="stretch",
            config=PLOTLY_CHART_CONFIG,
        )
    else:
        # Avís grafic EPW buit
        st.info(empty_message)


def render_overview_tab(state: EpwDashboardState) -> None:
    """Mostra la pestanya de visió general de l'EPW a la UI de Streamlit."""

    render_tab_intro(
        "Resum executiu del fitxer seleccionat, amb indicadors clau, context i ubicació."
    )
    render_metric_card_grid(
        state.metric_cards,
        shell_class="section-card epw-metric-shell",
        card_class="epw-metric-card",
        label_class="epw-metric-label",
        value_class="epw-metric-value",
        formatter=ui_text,
        label_formatter=ui_text,
    )
    # Columnes resum EPW
    overview_cols = st.columns([1.18, 0.82], gap="large")
    with overview_cols[0]:
        render_detail_card(
            state.metadata,
            state.selected_entry,
            total_records=int(state.full_metrics["records"]),
            filtered_records=int(state.filtered_metrics["records"]),
        )
    with overview_cols[1]:
        # Titol mapa EPW
        st.markdown("<div class='epw-card-title'>Ubicació</div>", unsafe_allow_html=True)
        build_map_chart(state.metadata)


def render_climate_dashboard_tab(state: EpwDashboardState) -> None:
    """Mostra mapes de calor climàtics anuals i gràfics d'orientació/vents."""

    render_tab_intro(
        "Tauler visual anual per detectar patrons ràpids de temperatura, radiació, vent i humitat."
    )
    # Graella heatmaps EPW
    dashboard_heatmaps = st.columns(2, gap="medium")
    with dashboard_heatmaps[0]:
        render_annual_heatmap(
            state.annual_temperature_heatmap,
            "dry_bulb_c",
            state,
            "No hi ha prou dades de temperatura per construir el mapa anual.",
        )
        render_annual_heatmap(
            state.annual_direct_radiation_heatmap,
            "direct_normal_radiation_wh_m2",
            state,
            "No hi ha prou dades de radiació directa per construir el mapa anual.",
            require_non_zero=True,
        )

    with dashboard_heatmaps[1]:
        render_annual_heatmap(
            state.annual_wind_heatmap,
            "wind_speed_m_s",
            state,
            "No hi ha prou dades de vent per construir el mapa anual.",
            require_non_zero=True,
        )
        render_annual_heatmap(
            state.annual_humidity_heatmap,
            "relative_humidity_pct",
            state,
            "No hi ha prou dades d'humitat per construir el mapa anual.",
        )

    render_comfort_radiation_chart(state)
    render_monthly_wind_rose_chart(state)


def render_comfort_radiation_chart(state: EpwDashboardState) -> None:
    """Genera un gràfic de radiació orientat a la comoditat quan hi hagi prou dades a la UI de Streamlit."""

    if not data_frame_has_plot_values(
        state.comfort_radiation_frame,
        ["comfort_radiation_kwh_m2", "incident_radiation_kwh_m2"],
        require_non_zero=True,
    ):
        # Avís radiacio orientada
        st.info("No hi ha prou dades per estimar la radiació orientada d'aquest fitxer.")
        return

    # Grafic radiacio orientada
    st.plotly_chart(
        build_comfort_radiation_figure(state.comfort_radiation_frame),
        width="stretch",
        config=PLOTLY_CHART_CONFIG,
    )
    # Text radiacio orientada
    st.caption(
        "Estimació sobre façanes verticals a partir de la radiació EPW "
        f"i una banda de confort tèrmic de 18-24 {epw_backend.DEG_C}."
    )


def render_monthly_wind_rose_chart(state: EpwDashboardState) -> None:
    """Mostra les roses dels vents mensuals quan hi ha dades de vent suficients."""

    if wind_rose_tables_have_plot_values(state.monthly_wind_rose_tables):
        # Grafic rosa vents mensual
        st.plotly_chart(
            build_monthly_wind_rose_grid_figure(state.monthly_wind_rose_tables),
            width="stretch",
            config=PLOTLY_CHART_CONFIG,
        )
    else:
        # Avís rosa vents
        st.info("No hi ha prou dades de vent per construir les roses mensuals.")


def render_series_tab(state: EpwDashboardState) -> None:
    """Mostra la pestanya de sèries temporals EPW a la UI de Streamlit."""

    render_tab_intro(
        "Evolució temporal anual de la temperatura, amb suport de rangs diaris i perfil horari mitjà."
    )
    render_epw_chart(
        state.focus_series,
        [state.series_variable],
        lambda: build_focus_timeseries_figure(
            state.focus_series,
            state.series_variable,
            state.series_aggregation,
        ),
        "No hi ha prou dades de temperatura per construir la sèrie temporal.",
    )

    # Columnes series EPW
    series_cols = st.columns(2, gap="medium")
    with series_cols[0]:
        render_epw_chart(
            state.daily_temperature,
            ["dry_bulb_min", "dry_bulb_mean", "dry_bulb_max"],
            lambda: build_daily_temperature_band_figure(state.daily_temperature),
            "No hi ha prou dades per construir la banda diària de temperatura.",
        )

    with series_cols[1]:
        render_epw_chart(
            state.hourly_profile,
            ["dry_bulb_mean", "dew_point_mean", "relative_humidity_mean"],
            lambda: build_hourly_profile_figure(state.hourly_profile),
            "No hi ha prou dades per construir el perfil horari mitjà.",
        )


def render_patterns_tab(state: EpwDashboardState) -> None:
    """Mostra els patrons climàtics mensuals i intradia."""

    render_tab_intro("Comparatives mensuals i patrons intradiaris del fitxer climàtic.")
    # Columnes patrons mensuals
    pattern_cols_monthly = st.columns(2, gap="medium")
    with pattern_cols_monthly[0]:
        render_epw_chart(
            state.monthly_frame,
            ["dry_bulb_mean", "dry_bulb_min", "dry_bulb_max", "relative_humidity_mean"],
            lambda: build_monthly_climate_figure(state.monthly_frame),
            "No hi ha prou dades climàtiques mensuals per construir aquest gràfic.",
        )

    with pattern_cols_monthly[1]:
        render_epw_chart(
            state.monthly_frame,
            [
                "global_horizontal_radiation_kwh_m2",
                "direct_normal_radiation_kwh_m2",
                "diffuse_horizontal_radiation_kwh_m2",
            ],
            lambda: build_monthly_solar_figure(state.monthly_frame),
            "No hi ha prou dades de radiació mensual per construir aquest gràfic.",
            require_non_zero=True,
        )

    render_pattern_heatmaps(state)


def render_pattern_heatmaps(state: EpwDashboardState) -> None:
    """Mostra els heatmaps de la pestanya de patrons."""

    # Columnes heatmaps patrons
    pattern_cols_heatmaps = st.columns(2, gap="medium")
    with pattern_cols_heatmaps[0]:
        render_epw_chart(
            state.heatmap_frame,
            None,
            lambda: build_heatmap_figure(state.heatmap_frame, state.heatmap_variable),
            "No hi ha prou dades de temperatura per construir el mapa de calor.",
        )

    with pattern_cols_heatmaps[1]:
        render_epw_chart(
            state.radiation_heatmap_frame,
            None,
            lambda: build_heatmap_figure(
                state.radiation_heatmap_frame,
                state.secondary_heatmap_variable,
            ),
            "No hi ha prou dades de radiació directa per construir el mapa de calor.",
            require_non_zero=True,
        )


def render_epw_tabs(state: EpwDashboardState) -> None:
    """Munta totes les pestanyes del panell EPW."""

    # Pestanyes visor EPW
    tab_overview, tab_dashboard, tab_series, tab_patterns = st.tabs(
        ["Resum", "Tauler climàtic", "Sèries", "Patrons"]
    )
    with tab_overview:
        render_overview_tab(state)
    with tab_dashboard:
        render_climate_dashboard_tab(state)
    with tab_series:
        render_series_tab(state)
    with tab_patterns:
        render_patterns_tab(state)


def render_epw_download(state: EpwDashboardState) -> None:
    """Mostra els controls de baixada CSV per al fitxer EPW seleccionat."""

    # Separador download EPW
    st.markdown("<div class='studio-spacer-125'></div>", unsafe_allow_html=True)
    # Botó download EPW
    st.download_button(
        "Descarregar dades del fitxer (CSV)",
        data=state.download_frame.to_csv(index=False).encode("utf-8"),
        file_name=f"{state.metadata.get('stem', 'clima')}_complet.csv",
        mime="text/csv",
        width="stretch",
        type="primary",
    )
    # Text registres EPW
    st.caption(state.records_message)


def render_epw_dashboard() -> None:
    """Mostra el flux complet del visor EPW a la UI de Streamlit."""

    configure_epw_dashboard_page()
    selected_entry, metadata, epw_data = select_epw_entry()
    # Titol lectura global
    st.markdown(
        "<div class='epw-card-title epw-global-title'>Lectura global del fitxer</div>",
        unsafe_allow_html=True,
    )
    state = prepare_epw_dashboard_state(selected_entry, metadata, epw_data)
    render_epw_tabs(state)
    render_epw_download(state)


render_epw_dashboard()
