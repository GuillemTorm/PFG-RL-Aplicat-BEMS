"""Sinergym Studio: vista per afegir entorns.

Aquesta vista gestiona la UI de Streamlit per carregar models d'edifici
EnergyPlus (.idf/.epJSON) i fitxers meteorològics (.epw), configurar els
actuadors HVAC i la variabilitat climàtica, i registrar un entorn Gym nou a
Sinergym mitjançant un fitxer YAML generat.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st
import yaml

from backend import afegir_entorn_backend as add_env_backend
from page_components.ui_fragments import render_card_header, render_hero, render_section_title
from page_styles.afegir_entorn import inject_add_environment_styles
from sidebar_nav import configure_studio_page


PAGE_TITLE = "Crear Nou Entorn"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Carrega un edifici i un únic clima, detecta controladors HVAC i bateria "
    "usables del model i configura l'espai d'accions abans de registrar el nou entorn."
)


def render_add_environment_hero() -> None:
    """Mostra la capçalera principal amb el mateix llenguatge visual de l'app."""

    render_hero("add-environment-hero", "CREACIÓ D'ENTORNS", PAGE_TITLE, INTRODUCTION_TEXT)


def render_weather_source_selector(target=st) -> str:
    """Mostra un control segmentat o un grup de ràdio per seleccionar la font meteorològica.

    Paràmetres:
        target: un contenidor Streamlit per vincular el widget. Per defecte a st.

    Retorna:
        str: El mode seleccionat ("Escollir existents" o "Pujar nous fitxers").
    """

    options = ["Escollir existents", "Pujar nous fitxers"]
    current_value = st.session_state.get("add_env_weather_mode", options[0])
    target.markdown('<div class="studio-segmented-pill-anchor"></div>', unsafe_allow_html=True)

    # Selector origen clima
    selected_value = target.segmented_control(
        "Origen del clima",
        options,
        default=current_value,
        key="add_env_weather_mode",
    )
    return selected_value or current_value


def format_current_schedule_range(option) -> str:
    """Formata l'interval numèric vàlid d'un actuador per mostrar-lo en funció de la seva planificació inicial.

    Paràmetres:
        option (ActuatorOption): l'opció de l'actuador detectada des del model.

    Retorna:
        str: una cadena preformatada que presenta l'interval numèric detectat.
    """
    if option.current_low is None or option.current_high is None:
        return "Sense resum automàtic"
    if option.category == "availability":
        if abs(option.current_low - option.current_high) < 1e-6:
            return f"{option.current_low:.0f}"
        return f"{option.current_low:.0f} – {option.current_high:.0f}"
    if abs(option.current_low - option.current_high) < 1e-6:
        return f"{option.current_low:.2f}"
    return f"{option.current_low:.2f} – {option.current_high:.2f}"


def render_controller_selection_table(
    title: str,
    options,
    *,
    default_selected: bool,
    key: str,
    empty_message: str,
):
    """Mostra una taula interactiva per incloure/excloure controladors HVAC.

    Paràmetres:
        title (str): l'encapçalament que es mostra a sobre de la taula.
        options (Sequence[ActuatorOption]): les opcions de l'actuador disponibles.
        default_selected (bool): Si True, les caselles de selecció estan marcades inicialment.
        key (str): clau única d'estat de sessió Streamlit per a l'editor de dades.
        empty_message (str): Text alternativa quan no hi ha opcions per mostrar.

    Retorna:
        List[str]: una llista de les cadenes `option_id` seleccionades.
    """
    if not options:
        # Text taula buida
        st.caption(empty_message)
        return []

    # Titol taula controladors
    st.markdown(f"**{title}**")
    selection_df = pd.DataFrame(
        [
            {
                "Afegir": default_selected,
                "Control": option.label,
                "Afecta": option.reference,
                "Programa actual": format_current_schedule_range(option),
            }
            for option in options
        ],
        index=[option.option_id for option in options],
    )
    # Editor seleccio controladors
    edited_selection_df = st.data_editor(
        selection_df,
        hide_index=True,
        width="stretch",
        key=key,
        disabled=["Control", "Afecta", "Programa actual"],
        column_config={
            "Afegir": st.column_config.CheckboxColumn("Incloure", width="small"),
            "Control": st.column_config.TextColumn("Controlador"),
            "Afecta": st.column_config.TextColumn("Afecta"),
            "Programa actual": st.column_config.TextColumn("Programa actual"),
        },
    )
    return [
        option_id
        for option_id, row in edited_selection_df.iterrows()
        if bool(row["Afegir"])
    ]


def render_building_upload_card() -> Any:
    """Mostra la targeta d'upload de l'edifici i retorna el fitxer penjat.

    Retorna:
        Any: l'objecte del fitxer carregat Streamlit o None si no s'ha carregat cap fitxer.
    """
    # Targeta upload edifici
    building_card = st.container(border=True)
    render_card_header(
        building_card,
        anchor_class="upload-card-shell-anchor",
        kicker="Edifici",
        title="Fitxer d'edifici",
        description="Puja un fitxer IDF o epJSON per preparar el model base.",
    )
    # Upload fitxer edifici
    return building_card.file_uploader(
        "Fitxer d'edifici",
        type=["idf", "epjson", "epJSON"],
        label_visibility="collapsed",
    )


def render_weather_upload_card() -> tuple[Path, Any]:
    """Mostra la targeta del fitxer meteorològic i torna el camí resolt al fitxer EPW seleccionat.

    Gestiona tant el selector de fitxers existents com els modes de càrrega de fitxers nous.
    Crida st.stop() si no hi ha cap fitxer meteorològic vàlid disponible o seleccionat.

    Retorna:
        tuple[Path, Any]: el camí del fitxer EPW seleccionat i el seu contenidor de la targeta Streamlit.
    """
    # Targeta fitxer clima
    climate_card = st.container(border=True)
    render_card_header(
        climate_card,
        anchor_class="upload-card-shell-anchor",
        kicker="Clima",
        title="Fitxer climàtic",
        description="Escull un .epw existent o puja'n un de nou per registrar l'entorn.",
    )
    mode_weather = render_weather_source_selector(climate_card)

    selected_weather_path = None

    if mode_weather == "Escollir existents":
        weather_files = sorted(weather_file.name for weather_file in add_env_backend.WEATHERS_DIR.glob("*.epw"))
        if not weather_files:
            # Error sense EPW
            st.error("No hi ha fitxers .epw disponibles al catàleg actual.")
            st.stop()
        with climate_card:
            # Selector fitxer clima
            selected_weather_name = st.selectbox(
                "Selecciona el fitxer de clima",
                weather_files,
                index=None,
                placeholder="Tria un fitxer climàtic...",
                key="add_env_existing_weather_file",
            )
        if selected_weather_name:
            selected_weather_path = add_env_backend.WEATHERS_DIR / selected_weather_name
    else:
        with climate_card:
            # upload fitxer clima
            uploaded_weather_file = st.file_uploader(
                "Puja un fitxer .epw",
                type=["epw"],
                key="weather_upload",
            )
        if uploaded_weather_file:
            weather_upload_token = (uploaded_weather_file.name, uploaded_weather_file.size)
            cached_weather_path = st.session_state.get("add_env_weather_path")
            cached_weather_file = Path(cached_weather_path) if cached_weather_path else None
            if (
                st.session_state.get("add_env_weather_token") != weather_upload_token
                or cached_weather_file is None
                or not cached_weather_file.exists()
            ):
                cached_weather_file = add_env_backend.WEATHERS_DIR / uploaded_weather_file.name
                add_env_backend.save_uploaded_bytes(cached_weather_file, uploaded_weather_file.read())
                st.session_state.add_env_weather_token = weather_upload_token
                st.session_state.add_env_weather_path = str(cached_weather_file)
            selected_weather_path = cached_weather_file
            with climate_card:
                # Missatge clima carregat
                st.success(f"Fitxer de clima carregat: {uploaded_weather_file.name}")

    if selected_weather_path is None:
        st.stop()

    return selected_weather_path, climate_card


def render_weather_variability_section() -> tuple[Optional[Dict], bool]:
    """Mostra la configuració opcional de variabilitat meteorològica estocàstica.

    Retorna:
        tuple[Optional[Dict], bool]: configuració de la variabilitat del clima i si
        les variants estocàstiques estan habilitades.
    """
    render_section_title("Variabilitat climàtica opcional", "section-title", level=3)
    # Targeta variabilitat clima
    variability_card = st.container(border=True)
    variability_card.markdown('<div class="weather-variability-card-anchor"></div>', unsafe_allow_html=True)
    # Checkbox variants estocastiques
    enable_stochastic = variability_card.checkbox(
        "Generar també variants estocàstiques",
        value=True,
        help="Quan s'activa, es registren també entorns amb el sufix -continuous-stochastic-v1.",
    )

    if not enable_stochastic:
        return None, False

    default_sigma, default_mu, default_tau = add_env_backend.DEFAULT_WEATHER_VARIABILITY["Dry Bulb Temperature"]
    # Inputs variabilitat clima
    sigma_col, mu_col, tau_col = variability_card.columns(3)
    with sigma_col:
        # Input sigma clima
        sigma = st.number_input("Sigma", min_value=0.0, value=float(default_sigma), step=0.1)
    with mu_col:
        # Input mu clima
        mu = st.number_input("Mu", value=float(default_mu), step=0.1)
    with tau_col:
        # Input tau clima
        tau = st.number_input("Tau (hores)", min_value=0.1, value=float(default_tau), step=1.0)

    return {"Dry Bulb Temperature": [float(sigma), float(mu), float(tau)]}, True


@st.cache_data(show_spinner=False)
def load_weather_temperature_preview(
    weather_path: str,
    weather_mtime_ns: int,
    sigma: float,
    mu: float,
    tau: float,
) -> List[Dict[str, float]]:
    """Carrega les dades de previsualització meteorològica anual a la memòria cau per al fitxer EPW seleccionat.

    Paràmetres:
        weather_path (str): camí cap al fitxer meteorològic EPW.
        weather_mtime_ns (int): marca de temps de modificació de fitxers utilitzada com a clau d'invalidació de la memòria cau.
        sigma (float): paràmetre de desviació estàndard per al procés d'OU.
        mu (float): paràmetre mitjà per al procés d'OU.
        tau (float): paràmetre constant de temps per al procés d'OU.

    Retorna:
        List[Dict[str, float]]: registres de previsualització diaris preparats per a la traça.
    """

    del weather_mtime_ns
    return add_env_backend.build_weather_temperature_preview(Path(weather_path), sigma, mu, tau)


def render_weather_temperature_preview(
    selected_weather_path: Path,
    weather_variability: Optional[Dict],
) -> None:
    """Mostra la previsualització anual de la temperatura EPW per als canvis meteorològics estocàstics.

    Paràmetres:
        selected_weather_path (Path): fitxer EPW seleccionat o carregat actualment.
        weather_variability (Optional[Dict]): configuració activa de la variabilitat del clima.
    """

    if not weather_variability:
        return

    sigma, mu, tau = weather_variability["Dry Bulb Temperature"]
    try:
        weather_mtime_ns = selected_weather_path.stat().st_mtime_ns
    except OSError:
        weather_mtime_ns = 0

    preview_records = load_weather_temperature_preview(
        str(selected_weather_path),
        weather_mtime_ns,
        float(sigma),
        float(mu),
        float(tau),
    )
    if not preview_records:
        # Avís preview clima
        st.info("No s'ha pogut llegir la temperatura seca del fitxer EPW seleccionat.")
        return

    # Targeta previsualitzacio clima
    preview_card = st.container(border=True)
    render_card_header(
        preview_card,
        anchor_class="weather-preview-card-anchor",
        kicker="Clima modificat",
        title="Previsualització anual de temperatura",
    )
    # Grafic temperatura clima
    preview_card.plotly_chart(
        add_env_backend.build_weather_temperature_preview_figure(preview_records),
        width="stretch",
        config={"displayModeBar": False},
    )


def prepare_building_file(uploaded_file: Any) -> tuple[Path, Path]:
    """Desa, actualitza si cal i converteix el fitxer de construcció penjat a epJSON.

    Utilitza l'estat de la sessió per emmagatzemar el resultat a la memòria cau i evitar el processament redundant en les reexecucions.
    Crida st.stop() per errors irrecuperables.

    Paràmetres:
        uploaded_file: l'objecte de fitxer carregat Streamlit per al model d'edifici.

    Retorna:
        Tuple[Path, Path]: el camí desat en brut (tmp_path) i el camí final epJSON (building_path).
    """
    uploaded_token = (uploaded_file.name, uploaded_file.size)
    cached_tmp_path = st.session_state.get("add_env_tmp_path")
    cached_building_path = st.session_state.get("add_env_building_path")

    tmp_path = Path(cached_tmp_path) if cached_tmp_path else None
    building_path = Path(cached_building_path) if cached_building_path else None

    # Streamlit reexecuta la pàgina cada vegada que es toca un widget; aquest token evita
    # reconvertir el mateix fitxer una vegada i una altra.
    needs_prepare = (
        st.session_state.get("add_env_current_building_upload_token") != uploaded_token
        or tmp_path is None
        or building_path is None
        or not tmp_path.exists()
        or not building_path.exists()
    )

    if not needs_prepare:
        return Path(st.session_state["add_env_tmp_path"]), Path(st.session_state["add_env_building_path"])

    st.session_state.add_env_current_building_upload_token = uploaded_token
    tmp_path = add_env_backend.BUILDINGS_DIR / uploaded_file.name
    add_env_backend.save_uploaded_bytes(tmp_path, uploaded_file.read())

    if tmp_path.suffix.lower() == ".idf":
        with st.spinner("Escanejant i actualitzant l'arxiu IDF, si cal..."):
            detected_version = add_env_backend.detect_idf_version(tmp_path)
            if detected_version and add_env_backend.needs_idf_upgrade(detected_version):
                # EnergyPlus només converteix bé IDF de versions properes. Si el fitxer és
                # antic, el passem primer pels Transition tools oficials.
                updater_dir = add_env_backend.get_transition_updater_dir()
                if updater_dir is None:
                    with st.spinner("Descarregant les eines de transició d'EnergyPlus..."):
                        updater_dir = add_env_backend.download_transition_tools()

                if updater_dir is not None:
                    # Avís actualitzacio IDF
                    st.info(
                        "S'ha detectat un fitxer IDF antic "
                        f"({detected_version[0]}.{detected_version[1]}). "
                        "S'actualitzarà automàticament abans de convertir-lo."
                    )
                    try:
                        upgrade_result = add_env_backend.upgrade_idf_version(tmp_path, updater_dir)
                    except subprocess.TimeoutExpired:
                        # Error timeout actualitzacio
                        st.error(
                            "L'actualització automàtica de l'IDF ha superat el temps límit. "
                            "Revisa el fitxer o converteix-lo prèviament abans de continuar."
                        )
                        st.stop()
                    if upgrade_result.failed_transition_version is not None:
                        failed_major, failed_minor = upgrade_result.failed_transition_version
                        # Avís transicio fallida
                        st.warning(
                            "La transició automàtica ha fallat a la versió "
                            f"{failed_major}.{failed_minor}. Revisa l'IDF abans de continuar."
                        )
                    elif upgrade_result.upgraded and upgrade_result.final_version is not None:
                        # Missatge IDF actualitzat
                        st.success(
                            "L'arxiu s'ha actualitzat correctament a la versió "
                            f"{upgrade_result.final_version[0]}.{upgrade_result.final_version[1]}."
                        )

    with st.spinner("Convertint i preparant el model de l'edifici..."):
        try:
            # A partir d'aquí treballem sempre amb epJSON; simplifica l'anàlisi posterior
            # i evita duplicar parser per IDF i epJSON.
            building_path = (
                add_env_backend.convert_idf_to_epjson(tmp_path) if tmp_path.suffix.lower() == ".idf" else tmp_path
            )
        except FileNotFoundError:
            # Error EnergyPlus absent
            st.error("No s'ha trobat `energyplus`. Assegura't que està instal·lat i disponible al PATH.")
            st.stop()
        except subprocess.TimeoutExpired:
            # Error timeout conversio
            st.error(
                "La conversió o preparació del model ha superat el temps límit. "
                "Revisa el fitxer d'edifici o prova una conversió prèvia a epJSON."
            )
            st.stop()
        except Exception as error:
            # Error conversio edifici
            st.error(f"Error en la conversió amb EnergyPlus: {error}")
            st.stop()

    st.session_state.add_env_tmp_path = str(tmp_path)
    st.session_state.add_env_building_path = str(building_path)
    # Missatge edifici preparat
    st.success(f"Fitxer carregat i preparat correctament: {building_path.name}")
    return tmp_path, building_path


def load_or_run_training_analysis(building_path: Path, weather_path: Path):
    """Retorna la memòria cau BuildingTrainingAnalysis o l'executa nova si les entrades han canviat.

    Paràmetres:
        building_path (Path): camí cap al model d'edifici epJSON.
        weather_path (Path): camí cap al fitxer meteorològic EPW.

    Retorna:
        BuildingTrainingAnalysis: Detectats termòstats, actuadors, variables i comptadors.
    """
    analysis_cache_key = (str(building_path.resolve()), str(weather_path.resolve()))
    if st.session_state.get("add_env_training_analysis_key") != analysis_cache_key:
        with st.spinner("Detectant termòstats i actuadors del model..."):
            st.session_state.add_env_training_analysis = add_env_backend.build_training_analysis(
                building_path,
                weather_path,
                probe_handlers=False,
            )
            st.session_state.add_env_training_analysis_key = analysis_cache_key
    return st.session_state.add_env_training_analysis


def render_environment_id_section(
    building_path: Path,
    weather_profiles: List[Dict],
    enable_stochastic: bool,
) -> str:
    """Mostra l'entrada d'ID base de l'entorn i previsualitza tots els ID que es registraran.

    Paràmetres:
        building_path (Path): S'utilitza per obtenir un nom base predeterminat de la base del fitxer.
        weather_profiles (List[Dict]): perfils meteorològics per calcular tots els ID generats.
        enable_stochastic (bool): si s'han d'incloure els ID de variants estocàstiques.

    Retorna:
        str: l'identificador de l'entorn base validat i netejat.
    """
    render_section_title("Configuració del nou entorn")

    with st.container(border=True):
        default_id_base = add_env_backend.sanitize_identifier(building_path.stem, "nou_entorn")
        # Input ID entorn
        id_base_input = st.text_input("**ID base de l'entorn**", value=default_id_base)
        id_base = add_env_backend.sanitize_identifier(id_base_input, default_id_base)
        if id_base != id_base_input:
            st.caption(f"L'identificador base es registrarà com a `{id_base}`.")

        generated_env_ids = [
            add_env_backend.build_registered_env_id(id_base, profile["key"])
            for profile in weather_profiles
        ]
        if enable_stochastic:
            generated_env_ids.extend(
                add_env_backend.build_registered_env_id(id_base, profile["key"], stochastic=True)
                for profile in weather_profiles
            )
        # Etiqueta IDs generats
        st.markdown(
            "<p class='add-env-generated-ids-label'>IDs que es registraran:</p>",
            unsafe_allow_html=True,
        )
        # Llista IDs generats
        st.code("\n".join(generated_env_ids), language="text")

    return id_base


def render_controller_selection_section(analysis) -> tuple[dict, list]:
    """Mostra la detecció del controlador i retorna els ID dels actuadors seleccionats.

    Crida st.stop() si no hi ha actuadors disponibles o no n'hi ha cap seleccionat.

    Paràmetres:
        analysis (BuildingTrainingAnalysis): resultat de l'anàlisi de l'edifici detectat.

    Retorna:
        Tuple[dict, list]: les opcions completes de l'actuador en forma de diccionari i la llista d'ID d'opcions seleccionades.
    """
    render_section_title("Controladors detectats")

    detected_actuator_options = [
        *list(analysis.thermostat_actuators),
        *list(analysis.hvac_actuators),
    ]
    actuator_options = {option.option_id: option for option in detected_actuator_options}

    if not actuator_options:
        # Error sense controladors
        st.error(
            "No s'ha detectat cap controlador usable al model. "
            "Cal preparar prèviament l'edifici amb termòstats, setpoints, bateria o altres controls editables abans de registrar l'entorn."
        )
        st.stop()

    thermostat_options = list(analysis.thermostat_actuators)
    scheduled_setpoint_options = [
        option for option in analysis.hvac_actuators if option.category == "scheduled_temperature_setpoint"
    ]
    availability_options = [
        option for option in analysis.hvac_actuators if option.category == "availability"
    ]
    battery_options = [
        option for option in analysis.hvac_actuators if option.category in {"battery_charge", "battery_discharge"}
    ]

    # Separem els controladors per família perquè l'usuari pugui deixar fora actuadors
    # massa experimentals sense perdre els termòstats principals.
    # Resum controladors detectats
    st.caption(
        f"S'han detectat {len(detected_actuator_options)} controladors usables. "
        "Selecciona només els que vulguis incloure."
    )

    selected_actuator_ids = []
    selected_actuator_ids.extend(
        render_controller_selection_table(
            "Termòstats de zona",
            thermostat_options,
            default_selected=True,
            key="add_env_select_thermostats",
            empty_message="No s'han detectat termòstats de zona seleccionables.",
        )
    )
    selected_actuator_ids.extend(
        render_controller_selection_table(
            "Setpoints de sistema HVAC",
            scheduled_setpoint_options,
            default_selected=False,
            key="add_env_select_hvac_setpoints",
            empty_message="No s'han detectat setpoints HVAC programats addicionals.",
        )
    )
    selected_actuator_ids.extend(
        render_controller_selection_table(
            "Disponibilitat HVAC",
            availability_options,
            default_selected=False,
            key="add_env_select_hvac_availability",
            empty_message="No s'han detectat controls de disponibilitat HVAC.",
        )
    )
    selected_actuator_ids.extend(
        render_controller_selection_table(
            "Bateria",
            battery_options,
            default_selected=True,
            key="add_env_select_battery",
            empty_message="No s'han detectat controls de bateria.",
        )
    )

    selected_actuator_ids = list(dict.fromkeys(selected_actuator_ids))
    if not selected_actuator_ids:
        # Avís sense actuadors
        st.info("Selecciona com a mínim un controlador per poder definir l'espai d'accions.")
        st.stop()

    return actuator_options, selected_actuator_ids


def render_action_space_section(actuator_options: dict, selected_actuator_ids: List[str]) -> dict:
    """Mostra l'editor de límits de l'espai d'acció i retorna els límits validats.

    Crida a st.stop() si algun actuador té un límit no vàlid (mínim >= màxim).

    Paràmetres:
        actuator_options (dict): Dict complet dels objectes ActuatorOption disponibles per ID.
        selected_actuator_ids (List[str]): ID dels actuadors seleccionats per l'usuari.

    Retorna:
        dict: Mapeig de option_id a tuples flotants (baix, alt).
    """
    render_section_title("Espai d'accions")

    selected_actuator_options = [actuator_options[option_id] for option_id in selected_actuator_ids]
    controls_df = pd.DataFrame(
        [
            {
                "Control": option.label,
                "Afecta": option.reference,
                "Programa actual": format_current_schedule_range(option),
                "Mínim": float(option.default_low),
                "Màxim": float(option.default_high),
            }
            for option in selected_actuator_options
        ],
        index=[option.option_id for option in selected_actuator_options],
    )
    # Editor rangs accions
    edited_controls_df = st.data_editor(
        controls_df,
        hide_index=True,
        width="stretch",
        key="add_env_actuator_bounds_editor",
        disabled=["Control", "Afecta", "Programa actual"],
        column_config={
            "Control": st.column_config.TextColumn("Controlador"),
            "Afecta": st.column_config.TextColumn("Afecta"),
            "Programa actual": st.column_config.TextColumn("Programa actual"),
            "Mínim": st.column_config.NumberColumn("Mínim", step=0.5, format="%.2f"),
            "Màxim": st.column_config.NumberColumn("Màxim", step=0.5, format="%.2f"),
        },
    )

    actuator_bounds = {}
    bounds_are_valid = True
    for option_id, row in edited_controls_df.iterrows():
        low_value = float(row["Mínim"])
        high_value = float(row["Màxim"])
        if low_value >= high_value:
            bounds_are_valid = False
        actuator_bounds[option_id] = (low_value, high_value)

    if not bounds_are_valid:
        # Error rangs accio
        st.error("Cada actuador ha de tenir un límit mínim estrictament inferior al màxim.")
        st.stop()

    return actuator_bounds


def render_registration_section(
    id_base: str,
    building_path: Path,
    tmp_path: Path,
    weather_profiles: List[Dict],
    analysis,
    actuator_options: dict,
    selected_actuator_ids: List[str],
    actuator_bounds: dict,
    weather_variability: Optional[Dict],
) -> None:
    """Gestiona el botó de registre, la creació i la validació de l'entorn.

    En cas d'èxit, mostra el YAML generat i executa una simulació de validació ràpida.
    En cas d'error, reverteix els fitxers escrits parcialment i mostra els detalls de l'error.

    Paràmetres:
        id_base (str): identificador de base netejat per al entorn.
        building_path (Path): Camí al fitxer de construcció epJSON preparat.
        tmp_path (Path): camí cap al fitxer de construcció original penjat.
        weather_profiles (List[Dict]): llista de perfils meteorològics utilitzat per a la generació de la configuració.
        analysis (BuildingTrainingAnalysis): resultat de l'anàlisi de l'edifici detectat.
        actuator_options (dict): totes les opcions de l'actuador detectades teclejades per option_id.
        selected_actuator_ids (List[str]): ID dels actuadors seleccionats per l'usuari.
        actuator_bounds (dict): Mapeig de option_id a tuples de lligat (baix, alt).
        weather_variability (Optional[Dict]): configuració de la variabilitat del clima estocàstic, o None.
    """
    render_section_title("Creació i registre")

    # Botó crear entorn
    if not st.button("Crear entorn automàticament"):
        return

    cfg_path = add_env_backend.CFG_DIR / f"{id_base}.yaml"
    selected_actuator_objects = [actuator_options[option_id] for option_id in selected_actuator_ids]

    try:
        # Primer escrivim i registrem l'entorn. Si qualsevol pas falla, netegem el YAML
        # i el fitxer temporal per no deixar configuracions mig creades.
        env_cfg = add_env_backend.build_environment_config(
            id_base=id_base,
            building_file_name=building_path.name,
            weather_profiles=weather_profiles,
            analysis=analysis,
            selected_actuators=selected_actuator_objects,
            actuator_bounds=actuator_bounds,
            weather_variability=weather_variability,
        )
        add_env_backend.write_yaml_config(cfg_path, env_cfg)
        add_env_backend.register_environment_from_yaml(cfg_path)
    except Exception as error:
        # Error registre entorn
        st.error(f"No s'ha pogut construir o registrar l'entorn: {error}")
        cleanup_messages = add_env_backend.cleanup_failed_environment(cfg_path, tmp_path)
        for level, message in cleanup_messages:
            if level == "warning":
                # Avís neteja entorn
                st.warning(message)
            else:
                # Error neteja entorn
                st.error(message)
        st.stop()

    # Missatge entorn creat
    st.success(f"Entorn creat i registrat correctament: {id_base}")
    with st.expander("Veure el YAML generat"):
        # YAML generat
        st.code(yaml.dump(env_cfg, sort_keys=False, allow_unicode=True), language="yaml")

    validation_env_id = add_env_backend.build_registered_env_id(id_base, weather_profiles[0]["key"])
    try:
        # La validació curta és una prova de fum: si falla aquí, fallaria després en training.
        with st.spinner(f"Muntant l'entorn {validation_env_id} per validar la configuració..."):
            add_env_backend.validate_registered_environment(validation_env_id, cfg_path)
    except Exception as error:
        # Error validacio entorn
        st.error(f"No s'ha pogut validar l'entorn registrat. Es revertirà la configuració: {error}")
        cleanup_messages = add_env_backend.cleanup_failed_environment(cfg_path, tmp_path)
        for level, message in cleanup_messages:
            if level == "warning":
                # Avís rollback entorn
                st.warning(message)
            else:
                # Error rollback entorn
                st.error(message)
        st.stop()

    # Missatge validacio correcta
    st.success(
        "S'ha realitzat una validació ràpida de simulació amb l'entorn registrat procedimentalment de Sinergym. "
        "La configuració d'accions i observacions s'ha validat correctament."
    )


def main() -> None:
    """Punt d'entrada a la pàgina Afegir Entorn Streamlit.

    Organitza el flux complet de la pàgina: estils, heroi, càrregues de fitxers, processament d'edificis,
    detecció d'actuadors, configuració de l'espai d'acció i registre de l'entorn.
    """
    configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
    inject_add_environment_styles()
    render_add_environment_hero()

    render_section_title("Pujar fitxers")
    # Columnes upload fitxers
    building_column, climate_column = st.columns([1, 1.35], gap="large")
    with building_column:
        uploaded_file = render_building_upload_card()
    with climate_column:
        selected_weather_path, climate_card = render_weather_upload_card()

    selected_weather_paths = [selected_weather_path]
    weather_profile_suggestions = add_env_backend.build_weather_profile_suggestions(selected_weather_paths)
    with climate_card:
        # Text clima suggerit
        st.caption(weather_profile_suggestions[0].climate_label)
    weather_profiles = [
        {"key": suggestion.suggested_key, "weather_file": suggestion.file_name}
        for suggestion in weather_profile_suggestions
    ]

    weather_variability, enable_stochastic = render_weather_variability_section()
    render_weather_temperature_preview(selected_weather_path, weather_variability)

    if not uploaded_file:
        # Avís upload edifici
        st.info("Puja un fitxer d'edifici per continuar amb la detecció de termòstats i actuadors.")
        st.stop()

    tmp_path, building_path = prepare_building_file(uploaded_file)
    analysis = load_or_run_training_analysis(building_path, selected_weather_paths[0])

    if not analysis.thermostat_zones:
        # Error sense termostats
        st.error(
            "No s'han detectat zones amb termòstat. Aquesta alta automàtica està pensada per edificis amb heating/cooling setpoints configurables."
        )
        st.stop()

    id_base = render_environment_id_section(building_path, weather_profiles, enable_stochastic)
    actuator_options, selected_actuator_ids = render_controller_selection_section(analysis)
    actuator_bounds = render_action_space_section(actuator_options, selected_actuator_ids)

    render_registration_section(
        id_base=id_base,
        building_path=building_path,
        tmp_path=tmp_path,
        weather_profiles=weather_profiles,
        analysis=analysis,
        actuator_options=actuator_options,
        selected_actuator_ids=selected_actuator_ids,
        actuator_bounds=actuator_bounds,
        weather_variability=weather_variability,
    )


main()
