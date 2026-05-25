"""Pàgina de visualització d'entorns Sinergym.

Mostra la geometria 3D, el clima, la configuració i els actius energètics
associats a l'entorn seleccionat.
"""

from html import escape
from typing import Any, Dict, List, Tuple

import gymnasium as gym
import numpy as np
import pandas as pd
import streamlit as st
from page_components.ui_fragments import render_hero, render_section_title
from sidebar_nav import configure_studio_page

from backend.mapa_backend import render_location_map
from backend.mostrar_entorn_backend import (
    _format_ui_value,
    _reward_summary_frames,
    _sequence_to_df,
    _tuple_mapping_to_df,
    load_environment_assets,
    parse_epw_metadata_and_temperature,
    summarize_pv,
)
from backend.common import BUILDINGS_DIR, WEATHERS_DIR
from backend.common import list_registered_env_ids
from backend.viewer_3d_backend import plot_3d_model
from page_styles.mostrar_entorn import inject_environment_styles


PAGE_TITLE = "Mostrar Entorn"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Consulta els entorns registrats, explora la geometria de l'edifici "
    "i revisa configuració, clima i actius energètics des d'una sola pàgina."
)


def render_environment_hero() -> None:
    """Munta el bloc principal de la pàgina."""

    render_hero("environment-hero", "Visualització d'entorns", PAGE_TITLE, INTRODUCTION_TEXT)


def render_environment_section(title: str, kicker: str, description: str) -> None:
    """Mostra la capçalera visual d'una secció."""

    render_section_title(title)


def describe_environment_tags(env_name: str) -> List[str]:
    """Resumeix propietats de l'entorn en etiquetes curtes."""

    tags: List[str] = []
    lower_name = env_name.lower()
    if "continuous" in lower_name:
        tags.append("Accions continues")
    if "discrete" in lower_name:
        tags.append("Accions discretes")
    if "stochastic" in lower_name:
        tags.append("Entorn aleatori")
    if "mixed" in lower_name:
        tags.append("Accions mixtes")
    if "hot" in lower_name:
        tags.append("Clima calid")
    if "cool" in lower_name:
        tags.append("Clima moderat")
    if "cold" in lower_name:
        tags.append("Clima fred")
    return tags


def render_environment_tags(tags: List[str]) -> None:
    """Mostra propietats detectades en format d'etiqueta."""

    if not tags:
        return
    tags_html = "".join(f'<span class="environment-tag">{escape(tag)}</span>' for tag in tags)
    # Etiquetes entorn
    st.markdown(f'<div class="environment-tags">{tags_html}</div>', unsafe_allow_html=True)


def render_metric_card(label: str, value: str, variant: str = "") -> None:
    """Crea una targeta compacta amb una metrica o text curt."""

    extra_class = f" environment-metric-card--{variant}" if variant else ""
    # Targeta metrica entorn
    st.markdown(
        (
            f'<div class="environment-metric-card{extra_class}">'
            f'<div class="environment-metric-label">{escape(label)}</div>'
            f'<div class="environment-metric-value">{escape(value)}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_metric_cards(items: List[Tuple[str, str]], columns: int = 2, wide_first: bool = False) -> None:
    """Distribueix targetes compactes en files estables."""

    if not items:
        return

    remaining_items = items
    if wide_first:
        first_label, first_value = remaining_items[0]
        render_metric_card(first_label, first_value, variant="wide")
        remaining_items = remaining_items[1:]

    column_count = max(1, columns)
    for start in range(0, len(remaining_items), column_count):
        row_items = remaining_items[start : start + column_count]
        # Fila targetes metriques
        row_columns = st.columns(len(row_items), gap="small")
        for column, (label, value) in zip(row_columns, row_items):
            with column:
                render_metric_card(label, value)


def render_detail_card(title: str, rows: List[Tuple[str, str]]) -> None:
    """Crea una targeta compacta de detall."""

    rows_html = "".join(
        (
            '<div class="environment-detail-row">'
            f'<div class="environment-detail-label">{escape(str(label))}</div>'
            f'<div class="environment-detail-value">{escape(str(value))}</div>'
            '</div>'
        )
        for label, value in rows
    )
    card_parts = ['<div class="environment-detail-card">']
    if title:
        card_parts.append(f'<div class="environment-detail-title">{escape(title)}</div>')
    card_parts.append(f'<div class="environment-detail-list">{rows_html}</div>')
    card_parts.append('</div>')
    # Targeta detall entorn
    st.markdown("".join(card_parts), unsafe_allow_html=True)


def render_battery_cards(storage_list: List[dict]) -> None:
    """Mostra les bateries detectades com a targetes visuals."""

    for start in range(0, len(storage_list), 2):
        row_items = storage_list[start : start + 2]
        # Fila targetes bateria
        row_columns = st.columns(len(row_items), gap="small")
        for item_index, (column, storage) in enumerate(zip(row_columns, row_items), start=start + 1):
            rows = [
                ("Capacitat util", f"{_format_ui_value(storage.get('energy_kwh'))} kWh"),
                ("Carrega maxima", f"{_format_ui_value(storage.get('p_charge_kw'))} kW"),
                ("Descarrega maxima", f"{_format_ui_value(storage.get('p_discharge_kw'))} kW"),
                ("Rendiment", _format_ui_value(storage.get('eff_roundtrip'))),
            ]
            display_name = "Bateria" if len(storage_list) == 1 else f"Bateria {item_index}"
            rows_html = "".join(
                (
                    '<div class="environment-detail-row">'
                    f'<div class="environment-detail-label">{escape(label)}</div>'
                    f'<div class="environment-detail-value">{escape(value)}</div>'
                    "</div>"
                )
                for label, value in rows
            )
            with column:
                # Targeta bateria
                st.markdown(
                    (
                        '<div class="environment-battery-card">'
                        f'<div class="environment-battery-name">{escape(display_name)}</div>'
                        f'<div class="environment-battery-type">{escape(_format_ui_value(storage.get("type")))}</div>'
                        f'<div class="environment-battery-list">{rows_html}</div>'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )


def _reward_label(reward_value: Any) -> str:
    """Retorna una etiqueta llegible per al reward configurat."""

    return getattr(reward_value, '__name__', _format_ui_value(reward_value))


def render_basic_config(spec: gym.envs.registration.EnvSpec, kwargs: Dict[str, Any]) -> None:
    """Omple la secció de configuració bàsica a la UI de Streamlit."""
    # Seccio configuracio general
    st.markdown("#### Configuració general")
    render_detail_card(
        "",
        [
            ("ID", _format_ui_value(spec.id)),
            ("Entry point", _format_ui_value(spec.entry_point)),
            ("Fitxer edifici", _format_ui_value(kwargs.get('building_file'))),
            ("Reward", _reward_label(kwargs.get('reward'))),
        ],
    )


def render_action_space_summary(action_space: Any) -> None:
    """Resumeix l'espai d'acció a la UI de Streamlit."""
    if action_space is None:
        st.code('-', language=None)
        return

    if isinstance(action_space, gym.spaces.Box):
        low = np.asarray(action_space.low, dtype=float).reshape(-1)
        high = np.asarray(action_space.high, dtype=float).reshape(-1)
        bounds_df = pd.DataFrame([
            {
                'Dimensió': index + 1,
                'Min': round(float(low_value), 3),
                'Max': round(float(high_value), 3),
            }
            for index, (low_value, high_value) in enumerate(zip(low, high))
        ])
        # Taula rangs accio
        st.dataframe(bounds_df, hide_index=True, width="stretch", height=min(220, 35 * len(bounds_df) + 38))
        return

    if isinstance(action_space, gym.spaces.Discrete):
        render_detail_card(
            "",
            [
                ("Tipus", "Discret"),
                ("Accions possibles", str(int(action_space.n))),
            ],
        )
        return

    if isinstance(action_space, gym.spaces.MultiDiscrete):
        nvec = np.asarray(action_space.nvec).reshape(-1)
        dims_df = pd.DataFrame([
            {
                'Dimensió': index + 1,
                'Tipus': 'MultiDiscrete',
                'Valors possibles': int(values),
            }
            for index, values in enumerate(nvec)
        ])
        # Taula accions multidiscretes
        st.dataframe(dims_df, hide_index=True, width="stretch", height=min(220, 35 * len(dims_df) + 38))
        return

    if isinstance(action_space, gym.spaces.MultiBinary):
        render_detail_card(
            "",
            [
                ("Tipus", "MultiBinary"),
                ("Bits", str(int(np.prod(action_space.shape)))),
            ],
        )
        return

    st.code(_format_ui_value(action_space), language=None)


def _actuators_mapping_df(actuators: Dict[str, Any]) -> pd.DataFrame:
    """Construeix un resum llegible del mapatge entre dimensions i actuadors."""

    rows = []
    for index, (actuator_key, metadata) in enumerate((actuators or {}).items(), start=1):
        if isinstance(metadata, dict):
            rows.append(
                {
                    'Dimensió': index,
                    'Actuador': actuator_key,
                    'Tipus objecte': _format_ui_value(metadata.get('element_type')),
                    'Camp de control': _format_ui_value(metadata.get('value_type')),
                    'Variable RL': _format_ui_value(metadata.get('variable_name')),
                }
            )
        else:
            rows.append(
                {
                    'Dimensió': index,
                    'Actuador': actuator_key,
                    'Tipus objecte': _format_ui_value(metadata),
                    'Camp de control': '-',
                    'Variable RL': '-',
                }
            )
    return pd.DataFrame(rows)


def render_kwargs_overview(kwargs: Dict[str, Any]) -> None:
    """Secció de visió general de renderització de kwargs a la UI de Streamlit."""
    # Els kwargs de Sinergym barregen variables, actuadors, reward i camps interns.
    # Els separem en pestanyes perquè sigui revisable sense llegir el JSON sencer.
    # Pestanyes kwargs entorn
    tab_obs, tab_control, tab_reward, tab_misc, tab_raw = st.tabs([
        'Variables', 'Control', 'Reward', 'Extra', 'JSON brut'
    ])

    with tab_obs:
        time_df = _sequence_to_df(kwargs.get('time_variables', []), 'Variable temporal')
        if not time_df.empty:
            # Taula variables temporals
            st.markdown('**Variables temporals**')
            st.dataframe(time_df, hide_index=True, width="stretch")

        variables_df = _tuple_mapping_to_df(kwargs.get('variables', {}), ["Variable d'EnergyPlus", "Ambit"])
        if not variables_df.empty:
            # Taula variables observades
            st.markdown('**Variables observades**')
            st.dataframe(variables_df, hide_index=True, width="stretch", height=320)
        else:
            st.info('No hi ha variables definides per aquest entorn.')

        meters_df = pd.DataFrame(
            [{'Alias': alias, 'Meter': meter} for alias, meter in (kwargs.get('meters') or {}).items()]
        )
        if not meters_df.empty:
            # Taula meters
            st.markdown('**Meters**')
            st.dataframe(meters_df, hide_index=True, width="stretch")

    with tab_control:
        # Seccio espai accio
        st.markdown("**Espai d'acció**")
        render_action_space_summary(kwargs.get('action_space'))
        st.caption("Cada dimensió correspon, en aquest ordre, als actuadors definits a continuació.")

        actuators_df = _actuators_mapping_df(kwargs.get('actuators', {}))
        if not actuators_df.empty:
            # Taula actuadors
            st.markdown('**Actuadors**')
            st.dataframe(actuators_df, hide_index=True, width="stretch", height=260)
        else:
            st.info('No hi ha actuadors configurats.')

    with tab_reward:
        scalar_reward_df, grouped_reward_df = _reward_summary_frames(kwargs.get('reward_kwargs') or {})
        if not scalar_reward_df.empty:
            # Taula reward simple
            st.markdown('**Paràmetres simples**')
            st.dataframe(scalar_reward_df, hide_index=True, width="stretch")
        if not grouped_reward_df.empty:
            # Taula reward agrupada
            st.markdown('**Paràmetres agrupats**')
            st.dataframe(grouped_reward_df, hide_index=True, width="stretch")
        if scalar_reward_df.empty and grouped_reward_df.empty:
            st.info('No hi ha reward kwargs definits.')

    with tab_misc:
        weather_rows = []
        for variable_name, values in (kwargs.get('weather_variability') or {}).items():
            # La variabilitat pot arribar com a escalar o com a tuple sigma/mu/període.
            # Normalitzem la forma només per mostrar-la en taula.
            if isinstance(values, (list, tuple)):
                sigma = values[0] if len(values) > 0 else '-'
                mu = values[1] if len(values) > 1 else '-'
                period = values[2] if len(values) > 2 else '-'
            else:
                sigma = values
                mu = '-'
                period = '-'
            weather_rows.append({
                'Variable': variable_name,
                'Sigma': _format_ui_value(sigma),
                'Mu': _format_ui_value(mu),
                'Periode': _format_ui_value(period),
            })
        weather_df = pd.DataFrame(weather_rows)
        if not weather_df.empty:
            # Taula variabilitat clima
            st.markdown('**Variabilitat meteorològica**')
            st.dataframe(weather_df, hide_index=True, width="stretch")

        misc_df = pd.DataFrame([
            {'Clau': 'building_config', 'Valor': _format_ui_value(kwargs.get('building_config'))},
            {'Clau': 'context', 'Valor': _format_ui_value(kwargs.get('context'))},
            {'Clau': 'initial_context', 'Valor': _format_ui_value(kwargs.get('initial_context'))},
        ])
        # Taula camps extra
        st.markdown('**Altres camps**')
        st.dataframe(misc_df, hide_index=True, width="stretch")

    with tab_raw:
        # JSON brut kwargs
        st.json(kwargs)


def render_3d_viewer(
    records: List[dict],
    zones: List[str],
    types: List[str],
    z_clip_range: Tuple[float, float],
    pv_list: List[dict],
    name_index: Dict[str, int],
) -> None:
    """Mostra el visor de geometria de l'edifici en 3D.

    Mostra la figura 3D interactiva Plotly. Totes les superfícies es mostren amb
    per defecte amb tots els tipus i zones visibles.
    """
    if records:
        vis_types = {surface_type: True for surface_type in types}
        if pv_list:
            vis_types["PV"] = True
        vis_zones = {zone: True for zone in zones}
        fig3d = plot_3d_model(
            records=records,
            visible_types=vis_types,
            visible_zones=vis_zones,
            z_clip=z_clip_range,
            pv_list=pv_list,
            name_index=name_index,
        )
        # Visor 3D edifici
        st.plotly_chart(fig3d, width="stretch")
        st.caption("Passeu el cursor per veure zona, area i orientacio. Aspecte data i model recentrat.")
    else:
        st.warning("No s'han trobat superficies amb coordenades.")


def render_environment_page() -> None:
    """Munta la pàgina amb la presentació visual actualitzada."""

    configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
    inject_environment_styles()

    render_environment_hero()
    all_envs = list_registered_env_ids()
    render_environment_section(
        "Selecció de l'entorn",
        "Catàleg",
        "Filtra els entorns registrats i tria quin vols obrir abans de veure la representació geomètrica i les dades de configuració.",
    )

    # Controls cerca entorn
    search_col, select_col = st.columns(2, gap="large")
    with search_col:
        # Input cerca entorn
        search_query = st.text_input("Cerca un entorn per nom", placeholder="Ex: warehouse, hot, continuous...")

    filtered_envs = [env_name for env_name in all_envs if search_query.lower() in env_name.lower()] if search_query else all_envs
    with select_col:
        # Selector entorn
        env_selected = st.selectbox(
            "Selecciona un entorn",
            filtered_envs if filtered_envs else ["Cap coincidència"],
            disabled=not filtered_envs,
        )

    # Text entorns filtrats
    st.caption(f"{len(filtered_envs)} entorns disponibles amb el filtre actual.")
    if not filtered_envs:
        # Avís entorn no trobat
        st.warning("No s'ha trobat cap entorn amb aquest filtre.")
        return

    render_environment_tags(describe_environment_tags(env_selected))

    try:
        spec = gym.spec(env_selected)
        kwargs = spec.kwargs
        bfile = kwargs.get("building_file")

        weather_file = None
        if "weather_files" in kwargs:
            raw = kwargs["weather_files"]
            weather_file = raw if isinstance(raw, str) else raw[0]
        elif "weather" in kwargs:
            wf = kwargs["weather"].get("weather_files", [])
            weather_file = wf if isinstance(wf, str) else (wf[0] if wf else None)

        render_environment_section(
            "Visualització de l'edifici",
            "Geometria",
            "La pàgina mostra la geometria 3D de l'edifici amb totes les superfícies visibles.",
        )

        records = []
        name_index = {}
        pv_list = []
        storage_list = []
        z_clip_range = (0.0, 0.0)
        zones: List[str] = []
        types: List[str] = []

        if bfile and (BUILDINGS_DIR / bfile).exists():
            with st.spinner("Carregant dades de l'entorn..."):
                # load_environment_assets centralitza el parseig pesat de l'IDF/epJSON.
                # La pàgina només decideix què es mostra i amb quins filtres.
                ep_path = str(BUILDINGS_DIR / bfile)
                assets = load_environment_assets(ep_path)
                records = assets["records"]
                zones = assets["zones"]
                types = assets["types"]
                z_clip_range = assets["z_clip_range"]
                name_index = assets["name_index"]
                pv_list = assets["pv"]
                storage_list = assets["storage"]

            render_3d_viewer(records, zones, types, z_clip_range, pv_list, name_index)
        else:
            # Avís visor no disponible
            st.info("No disponible per a aquest format o falta el fitxer d'edifici.")

        render_environment_section(
            "Configuració i dades associades",
            "Context tècnic",
            "Reuneix la configuració base de l'entorn, els paràmetres exposats per Sinergym i la informació del fitxer meteorològic associat.",
        )
        # Columnes configuracio entorn
        col1, col2 = st.columns(2)

        with col1:
            # Targeta configuracio base
            render_basic_config(spec, kwargs)

            weather_loaded = False
            if weather_file:
                wpath = WEATHERS_DIR / weather_file
                if wpath.exists():
                    weather_loaded = True
                    loc, avg_temp, cz = parse_epw_metadata_and_temperature(str(wpath))
                    # Seccio clima localitzacio
                    st.markdown("### Clima i localització")
                    st.caption("Resum del fitxer meteorològic actiu i ubicació aproximada de l'entorn.")
                    render_detail_card(
                        "Informació general",
                        [
                            ("Fitxer clima", weather_file),
                            ("Temp. mitjana", f"{avg_temp:.2f} C"),
                            ("Zona climàtica", str(cz)),
                            ("Ciutat", f"{loc['city']}, {loc['country']}"),
                            ("Coordenades", f"{loc['latitude']:.3f}, {loc['longitude']:.3f}"),
                        ],
                    )
                    # Text resum clima
                    st.caption("Ubicació aproximada")
                    # Mapa ubicacio clima
                    render_location_map(
                        loc["latitude"],
                        loc["longitude"],
                        zoom=4,
                        color=(255, 0, 0, 220),
                        radius=15000,
                    )

            if not weather_loaded:
                # Avís clima no disponible
                st.info("No hi ha cap fitxer de clima disponible per mostrar en aquesta configuració.")

            # Separador clima energia
            st.markdown("<div class='studio-spacer-070'></div>", unsafe_allow_html=True)
            # Seccio solar bateria
            st.markdown("### Solar i bateria")
            st.caption("Actius energètics detectats a partir de la geometria i dels objectes associats.")

            if pv_list:
                pv_summary = summarize_pv(records, name_index, pv_list)
                surface_names = pv_summary["surfaces_with_pv"]
                # Mostrem només unes quantes superfícies perquè alguns models tenen molts
                # panells i la targeta quedaria il·legible.
                surface_preview = ", ".join(surface_names[:4]) if surface_names else "Sense coincidencies"
                if len(surface_names) > 4:
                    surface_preview += f" +{len(surface_names) - 4} mes"
                # Targeta panells fotovoltaics
                render_detail_card(
                    "Panells fotovoltaics",
                    [
                        ("Generadors PV", str(pv_summary["count"])),
                        ("Cares actives", str(len(surface_names))),
                        ("Area aprox.", "0 m2" if pv_summary["area_m2"] is None else f"{pv_summary['area_m2']:.2f} m2"),
                        ("Tilt mig", "0 deg" if pv_summary["avg_tilt"] is None else f"{pv_summary['avg_tilt']:.0f} deg"),
                        ("Azimut mig", "0 deg" if pv_summary["avg_azimuth"] is None else f"{pv_summary['avg_azimuth']:.0f} deg"),
                        ("Superficies", surface_preview),
                    ],
                )
            else:
                # Avís sense panells PV
                st.info("No s'han detectat panells fotovoltaics associats a superficies.")

            if storage_list:
                # Targetes bateria
                render_battery_cards(storage_list)
            else:
                # Avís sense bateria
                st.info("No s'han detectat objectes de bateria.")

        with col2:
            # Taules kwargs entorn
            render_kwargs_overview(kwargs)

    except Exception as error:
        st.error(f"Error carregant l'entorn: {error}")


render_environment_page()
st.stop()
