"""Pàgina de control en viu d'un entorn Sinergym.

Permet provar un model entrenat o aplicar accions manuals pas a pas.
"""

from html import escape
from pathlib import Path

import gymnasium as gym
import numpy as np
import pandas as pd
import streamlit as st
from page_components.ui_fragments import (
    build_metric_item,
    render_hero,
    render_kicker_section,
    render_metric_row,
)
from page_styles.interaccionar_agent import inject_interaction_styles
from sidebar_nav import configure_studio_page

from backend.interaccionar_agent_backend import (
    env_id_from_meta_or_name,
    extract_display_observation,
    extract_policy_test_defaults,
    find_matching_column,
    coerce_observation_values,
    get_model_observation_size,
    get_runtime_observation_variables,
    get_wrapper_variables,
    infer_unit,
    initialize_runtime,
    load_model_training_metadata,
    load_sb3_model_bytes,
    mode_requires_model,
    normalize_policy_observation,
    prepare_action_display,
    randomize_observation_values,
    run_environment_steps,
    scan_model_zips,
)


PAGE_TITLE = "Control en Viu"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = (
    "Configura un entorn Sinergym, carrega un model si cal i controla "
    "la simulació pas a pas amb l'agent o amb accions manuals."
)


def render_interaction_hero() -> None:
    """Mostra la introducció de la pàgina principal a la UI de Streamlit."""

    render_hero("interaction-hero", "Simulació i control", PAGE_TITLE, INTRODUCTION_TEXT)


def render_interaction_section(title: str, kicker: str, description: str) -> None:
    """Crea una capçalera visual compacta per a una secció de pàgina."""

    render_kicker_section("interaction-section-card", title, kicker, description)


# La configuració visual es fa al principi perquè qualsevol rerun mantingui el mateix marc.
configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
inject_interaction_styles()

render_interaction_hero()

# Inicialitzem les claus que Streamlit reutilitza entre reruns.
def init_session():
    """Inicialitzeu les claus de sessió utilitzades pel flux d'interacció en directe."""
    if "ix_running" not in st.session_state:
        st.session_state.ix_running = False
    if "ix_app_mode" not in st.session_state:
        st.session_state.ix_app_mode = None
    if "ix_env" not in st.session_state:
        st.session_state.ix_env = None
    if "ix_model" not in st.session_state:
        st.session_state.ix_model = None
    if "ix_obs" not in st.session_state:
        st.session_state.ix_obs = None
    if "ix_step" not in st.session_state:
        st.session_state.ix_step = 0
    if "ix_history" not in st.session_state:
        st.session_state.ix_history = []
    if "ix_reward" not in st.session_state:
        st.session_state.ix_reward = 0.0
    if "ix_info" not in st.session_state:
        st.session_state.ix_info = {}

init_session()


def stop_simulation():
    """Tanqueu l'entorn actiu i restabliu l'estat d'interacció en directe."""
    if st.session_state.ix_env is not None:
        try:
            st.session_state.ix_env.close()
        except Exception:
            pass
    st.session_state.ix_env = None
    st.session_state.ix_app_mode = None
    st.session_state.ix_model = None
    st.session_state.ix_obs = None
    st.session_state.ix_running = False
    st.session_state.ix_step = 0
    st.session_state.ix_history = []
    st.session_state.ix_reward = 0.0
    st.session_state.ix_info = {}
    st.session_state.pop("ix_observation_variables", None)
    st.session_state.pop("ix_model_observation_size", None)
    st.session_state.pop("ix_test_obs_vals", None)


def randomize_policy_test_observations(obs_vars: list[str]) -> None:
    """Substituïu les observacions de la prova de política per valors aleatoris per a les variables actives."""

    random_obs_values = randomize_observation_values(obs_vars)
    st.session_state.ix_test_obs_vals = coerce_observation_values(random_obs_values, len(obs_vars))


def apply_live_action_step(
    vec_env: object,
    core_env: object,
    action_to_take: object,
    action_source: str = "",
    repeat_n: int = 1,
) -> None:
    """Avançar la simulació en directe i mantenir l'estat d'observació resultant."""

    try:
        with st.spinner(f"Simulant els propers {repeat_n} pas(sos) EnergyPlus ({action_source})..."):
            result = run_environment_steps(
                vec_env=vec_env,
                core_env=core_env,
                action_to_take=action_to_take,
                current_step=st.session_state.ix_step,
                repeat_n=repeat_n,
                obs_vars=st.session_state.get("ix_observation_variables"),
            )

            st.session_state.ix_obs = result["next_obs"]
            st.session_state.ix_reward = result["reward"]
            st.session_state.ix_info = result["info_dict"]
            st.session_state.ix_history.extend(result["history_entries"])
            st.session_state.ix_observation_variables = get_runtime_observation_variables(
                core_env=core_env,
                obs=result["next_obs"],
                model_obj=st.session_state.ix_model,
                vec_env=vec_env,
            )

            if result["history_entries"]:
                st.session_state.ix_step = result["history_entries"][-1]["pas"]

            if result["episode_finished"]:
                # Avís episodi reiniciat
                st.warning("Episodi acabat (Terminated / Truncated). L'entorn s'ha reiniciat.")
                st.session_state.ix_obs = result["reset_obs"]
                st.session_state.ix_step = 0
                st.session_state.ix_history = []

    except Exception as exc:
        # Error aplicar accio
        st.error(f"Error aplicant l'acció: {exc}")


def _calendar_or_reward_metric(curr: dict, prev: dict | None, core_env: object) -> dict:
    """Prepara la mètrica de calendari o recompensa quan el temps no és disponible."""
    month_col = find_matching_column(curr, ["month"])
    day_col = find_matching_column(curr, ["day_of_month", "day"])
    if month_col and day_col:
        month = int(curr[month_col])
        day = int(curr[day_col])
        month_labels = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Des"]
        season = "Hivern" if month in [12, 1, 2] else "Primavera" if month in [3, 4, 5] else "Estiu" if month in [6, 7, 8] else "Tardor"
        timestep_mins = "Desconegut"
        try:
            if hasattr(core_env, "get_wrapper_attr"):
                timestep_mins = getattr(core_env.unwrapped, "timestep", 15)
        except Exception:
            pass
        return {
            "label": f"Calendari (Pas: {timestep_mins} min)",
            "value": f"{day} {month_labels[month - 1] if 1 <= month <= 12 else month}",
            "delta": season,
            "delta_color": "off",
        }

    value = curr.get("reward", 0.0)
    previous = prev.get("reward", value) if prev else value
    return {
        "label": "Recompensa Agent",
        "value": f"{value:.2f}",
        "delta": f"{value - previous:+.2f}",
        "delta_color": "normal",
    }


# Flux de configuració abans de crear l'entorn.
if not st.session_state.ix_running:
    # Selecció del mode
    # Controls mode i entorn
    col_mode, col_env = st.columns([1, 1.35], gap="small")
    col_mode.markdown('<div class="studio-radio-card-anchor"></div>', unsafe_allow_html=True)
    col_env.markdown('<div class="interaction-env-card-anchor"></div>', unsafe_allow_html=True)
    # Selector mode funcionament
    use_agent = col_mode.radio(
        "Mode de Funcionament",
        [
            "Simulació en Temps Real interactiva",
            "Avaluació Manual Estàtica (Sense Simulació)",
        ],
        index=0,
    )

    # Si cal model, primer mirem el metadata del .zip; és més fiable que deduir l'entorn pel nom.
    selected_env_id = ""
    model_path = None

    if mode_requires_model(use_agent):
        model_scan_dirs = ",".join([str(Path.cwd() / "models"), str(Path.cwd())])
        df_models = scan_model_zips(model_scan_dirs)

        if not df_models.empty:
            options = list(range(len(df_models)))
            # Selector model entrenat
            idx = st.selectbox(
                "Selecciona el model entrenat (.zip)",
                options=options,
                format_func=lambda i: str(df_models.iloc[i]["stem"])
            )
            row = df_models.iloc[idx]
            model_path = Path(row["path"])

            with open(model_path, "rb") as fh:
                _, meta = load_sb3_model_bytes(fh.read(), device="cpu")

            training_metadata = load_model_training_metadata(model_path)
            suggested_env = training_metadata.get("env_id") or env_id_from_meta_or_name(meta, row["stem"])
            # Input entorn detectat
            selected_env_id = col_env.text_input("ID Entorn Sinergym", value=suggested_env or "")
        else:
            # Avís models no trobats
            st.warning("No s'han trobat models .zip")
            # Input entorn manual
            selected_env_id = col_env.text_input("ID Entorn Sinergym", value="Eplus-5zone-hot-continuous-v1")
    else:
        # En mode manual no hi ha model, però igualment cal un env_id vàlid per crear l'entorn.
        # Input entorn manual
        selected_env_id = col_env.text_input("ID Entorn Sinergym", value="Eplus-5zone-hot-continuous-v1")

    st.divider()
    init_text = "Inicialitzar Entorn i Simulació" if "Simulació" in use_agent else "Carregar Agent (Sense Simular)"
    # Botó inicialitzar entorn
    if st.button(
        init_text,
        key="ix_initialize_button",
        type="primary",
        disabled=not selected_env_id,
        width="stretch",
    ):
        with st.spinner("Creant l'entorn EnergyPlus i inicialitzant..."):
            try:
                venv, core_env, model_obj, obs, init_warnings = initialize_runtime(
                    selected_env_id=selected_env_id,
                    mode_label=use_agent,
                    model_path=model_path,
                )
                for warn_msg in init_warnings:
                    # Avís inicialitzacio
                    st.warning(warn_msg)

                st.session_state.ix_env = venv
                st.session_state.ix_core_env = core_env
                st.session_state.ix_model = model_obj
                st.session_state.ix_obs = obs
                st.session_state.ix_observation_variables = get_runtime_observation_variables(
                    core_env=core_env,
                    obs=obs,
                    model_obj=model_obj,
                    vec_env=venv,
                )
                st.session_state.ix_model_observation_size = get_model_observation_size(model_obj)
                st.session_state.ix_running = True
                st.session_state.ix_app_mode = use_agent
                st.session_state.ix_step = 0
                st.session_state.ix_reward = 0.0
                st.session_state.ix_history = []
                st.session_state.ix_info = {}
                st.rerun()

            except Exception as e:
                # Error inicialitzacio
                st.error(f"Error inicialitzant: {e}")
                stop_simulation()


# Flux d'interacció quan l'entorn ja està creat.
else:
    venv = st.session_state.ix_env
    core_env = st.session_state.get("ix_core_env", venv)
    model = st.session_state.ix_model
    obs = st.session_state.ix_obs
    app_mode = st.session_state.get("ix_app_mode", "")

    # En aquest mode només consultem la política: no avancem EnergyPlus.
    if app_mode and "Avaluació" in app_mode:
        # Avís mode estatic
        st.info("Avaluació Manual Estàtica. Aquest mode no avança el rellotge del simulador, simplement mostra què faria l'agent donat qualsevol input de l'edifici.")
        render_interaction_section(
            "Avaluació estàtica",
            "Consulta de política",
            "Construeix una observació numèrica i comprova quina acció retornaria el model sense avancar el simulador.",
        )
        # Capçalera consulta estatica
        cols_hdr = st.columns([4, 1])
        # Botó aturar consulta
        if cols_hdr[1].button(
            "Aturar i Sortir",
            key="btn_stop_test",
            type="primary",
            width="stretch",
        ):
            stop_simulation()
            st.rerun()

        st.subheader("Simulació numèrica: observacions")
        obs_vars = st.session_state.get("ix_observation_variables") or get_runtime_observation_variables(
            core_env=core_env,
            obs=obs,
            model_obj=model,
            vec_env=venv,
        )
        expected_obs_size = st.session_state.get("ix_model_observation_size") or get_model_observation_size(model)

        # Agafem una observació real com a punt de partida perquè la consulta estàtica no
        # comenci amb zeros que no tindrien sentit físic.
        if "ix_test_obs_vals" not in st.session_state or len(st.session_state.ix_test_obs_vals) != len(obs_vars):
            default_obs_values = extract_policy_test_defaults(
                obs=obs,
                info_dict=st.session_state.get("ix_info", {}),
                obs_vars=obs_vars,
                vec_env=venv,
                core_env=core_env,
            )
            st.session_state.ix_test_obs_vals = coerce_observation_values(default_obs_values, len(obs_vars))

        # Botó observacions aleatories
        st.button(
            "Generar observacions aleatòries",
            key="ix_randomize_observations",
            on_click=randomize_policy_test_observations,
            args=(obs_vars,),
        )

        custom_obs = []

        # El formulari evita reexecutar la predicció cada vegada que es toca un input numèric.
        # Formulari consulta politica
        with st.form("form_policy_test"):
            # Graella inputs observacio
            grid = st.columns(3)
            for i, var_name in enumerate(obs_vars):
                val_d = float(st.session_state.ix_test_obs_vals[i]) if i < len(st.session_state.ix_test_obs_vals) else 0.0
                unit = infer_unit(var_name)
                label = f"{var_name} ({unit})" if unit else var_name

                with grid[i % 3]:
                    # Input valor observacio
                    val = st.number_input(label, value=val_d, format="%.3f")
                    custom_obs.append(val)

            # Botó consultar agent
            submitted = st.form_submit_button("Consultar Decisió de l'Agent", type="primary")

        if submitted:
            st.divider()
            if model is None:
                # Error sense model
                st.error("No hi ha model carregat!")
            else:
                custom_obs = coerce_observation_values(custom_obs, expected_obs_size)
                norm_obs = normalize_policy_observation(custom_obs, core_env, venv, expected_obs_size)

                # Predim amb l'observació normalitzada igual que durant l'entrenament.
                action, state = model.predict(norm_obs, deterministic=True)

                # Desnormalitzem l'acció només per ensenyar-la; al simulador li passarem
                # sempre el format que espera el VecEnv.
                action_display = prepare_action_display(action, venv, core_env)

                action_vars = get_wrapper_variables(core_env, "action_variables")

                st.subheader("Resposta immediata de la xarxa neuronal")

                # Metriques accio agent
                acts_c = st.columns(max(len(action_vars), 1))
                if len(action_vars) > 0 and len(action_vars) == getattr(action_display, 'size', -1):
                    for i, act_n in enumerate(action_vars):
                        with acts_c[i]:
                            unit_a = infer_unit(act_n)
                            val_str = f"{action_display[i]:.2f} {unit_a}" if unit_a else f"{action_display[i]:.2f}"
                            # Metrica accio agent
                            st.metric(f"Acció '{act_n}'", val_str)
                else:
                    st.write(action_display)

                # Text accio crua
                st.caption(f"L'acció crua normalitzada retornada per la xarxa era: `{action}`. Si el model conté `NormalizeAction`, es tradueix als llindars de Sinergym a dalt.")

        # Interrompre execució aquí perquè no es pinti el mode dinàmic abaix
        st.stop()

    # Missatge simulacio activa
    st.success("Simulació en curs amb el motor d'**EnergyPlus real**. Esperant interacció pas a pas.")

    render_interaction_section(
        "Simulació activa",
        "Temps real",
        "Consulta l'estat actual de l'entorn, aplica accions amb l'agent o manualment i segueix els indicadors principals sense alterar el flux existent.",
    )

    # Resum ràpid de l'estat actual.
    # Metriques estat simulacio
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pas Actual", st.session_state.ix_step)
    col2.metric("Última Recompensa", f"{st.session_state.ix_reward:.3f}")
    # Botó aturar simulacio
    if col4.button("Aturar i Tancar", key="ix_stop_live_button", width="stretch"):
        stop_simulation()
        st.rerun()

    st.divider()

    # Bloc d'observacions actuals.
    st.subheader("Observació actual")

    obs_vars = st.session_state.get("ix_observation_variables") or get_runtime_observation_variables(
        core_env=core_env,
        obs=obs,
        model_obj=model,
        vec_env=venv,
    )
    _, display_obs = extract_display_observation(
        obs=obs,
        info_dict=st.session_state.get("ix_info", {}),
        obs_vars=obs_vars,
        vec_env=venv,
    )

    if len(obs_vars) == len(display_obs):
        # Crea un DataFrame agradable
        df_obs = pd.DataFrame({"Variable": obs_vars, "Valor Original": display_obs})
        # Arrodonim una mica per que no sigui massa brut
        df_obs["Valor Original"] = df_obs["Valor Original"].apply(lambda x: round(x, 4) if isinstance(x, (int, float)) else x)
        # Taula observacio actual
        st.dataframe(df_obs, width="stretch", hide_index=True)
    else:
        st.write(display_obs)

    st.divider()

    # Selecció de l'acció a aplicar al pas següent.
    st.subheader("Acció")

    # Pestanyes accio agent/manual
    tab_agent, tab_manual = st.tabs(["Agent", "Control Manual"])

    with tab_agent:
        if model is None:
            # Avís sense model actiu
            st.info("No hi ha cap model carregat en aquest moment. Fes servir el mode manual o atura i carrega'n un.")
        else:
            # Input passos agent
            n_steps = st.number_input("Quants passos vols avançar d'un cop?", min_value=1, max_value=1000, value=1, step=1, key="n_agent")
            # Botó avançar agent
            if st.button(
                f"Avançar {n_steps} pas(sos) amb l'Agent",
                key="ix_agent_step_button",
                type="primary",
                width="stretch",
            ):
                try:
                    with st.spinner(f"L'agent està simulant {n_steps} passos..."):
                        for _ in range(n_steps):
                            current_obs = st.session_state.ix_obs
                            act, _ = model.predict(current_obs, deterministic=True)
                            apply_live_action_step(venv, core_env, act, "Agent", repeat_n=1)
                except Exception as e:
                    # Error avançar agent
                    st.error(str(e))
                st.rerun()

    with tab_manual:
        st.write("Selecciona manualment els valors. L'espai d'accions es detecta automàticament des de l'entorn actiu.")

        # Recuperem les variables exposades pels wrappers, no només l'action_space cru.
        action_vars = get_wrapper_variables(core_env, "action_variables")
        action_space = getattr(venv, "action_space", getattr(core_env, "action_space", None))

        user_action = []

        if isinstance(action_space, gym.spaces.Box):
            # Accions contínues: un slider per dimensió.
            action_dim = int(np.prod(action_space.shape))
            lows = np.asarray(action_space.low, dtype=np.float32).reshape(-1)
            highs = np.asarray(action_space.high, dtype=np.float32).reshape(-1)
            for i in range(action_dim):
                v_name = action_vars[i] if len(action_vars) > i else f"Acció_{i}"
                v_low = float(lows[i])
                v_high = float(highs[i])

                # Alguns espais declaren límits infinits; els acotem per poder pintar sliders.
                if v_low == -np.inf: v_low = -100.0
                if v_high == np.inf: v_high = 100.0

                # Slider accio continua
                val = st.slider(v_name, min_value=v_low, max_value=v_high, value=(v_low+v_high)/2, step=0.1)
                user_action.append(val)

        elif isinstance(action_space, gym.spaces.Discrete):
            # Acció discreta simple: un enter entre 0 i n-1.
            st.write(f"L'espai d'acció és Discret ({action_space.n} possibilitats).")
            # Input accio discreta
            val = st.number_input("Selecciona Acció", min_value=0, max_value=int(action_space.n)-1, step=1)
            user_action.append(val)

        elif isinstance(action_space, gym.spaces.MultiDiscrete):
            nvec = np.asarray(action_space.nvec, dtype=np.int64).reshape(-1)
            st.write(f"L'espai d'acció és MultiDiscrete ({len(nvec)} dimensions).")
            for i, n_value in enumerate(nvec):
                v_name = action_vars[i] if len(action_vars) > i else f"Acció_{i}"
                # Input accio multidiscreta
                val = st.number_input(
                    v_name,
                    min_value=0,
                    max_value=max(int(n_value) - 1, 0),
                    value=0,
                    step=1,
                    key=f"manual_multidiscrete_{i}",
                )
                user_action.append(val)

        elif isinstance(action_space, gym.spaces.MultiBinary):
            action_dim = int(np.prod(action_space.shape))
            st.write(f"L'espai d'acció és MultiBinary ({action_dim} dimensions).")
            for i in range(action_dim):
                v_name = action_vars[i] if len(action_vars) > i else f"Acció_{i}"
                # Checkbox accio binaria
                val = st.checkbox(v_name, value=False, key=f"manual_multibinary_{i}")
                user_action.append(1 if val else 0)

        else:
            # Avís espai accio no suportat
            st.warning("Espai d'acció no suportat actualment per la inserció dinàmica manual.")

        # Input passos manuals
        n_steps_mod = st.number_input("Quants passos (repetint l'acció) vols avançar d'un cop?", min_value=1, max_value=1000, value=1, step=1, key="n_manual")

        # Botó avançar manual
        if st.button(
            f"Avançar {n_steps_mod} pas(sos) (Manual)",
            key="ix_manual_step_button",
            width="stretch",
        ):
            if isinstance(action_space, (gym.spaces.Box, gym.spaces.Discrete, gym.spaces.MultiDiscrete, gym.spaces.MultiBinary)):
                apply_live_action_step(venv, core_env, user_action, "Manual", repeat_n=n_steps_mod)
                st.rerun()

    # Resum ràpid de KPIs del pas actual.
    if len(st.session_state.ix_history) > 0:
        st.divider()
        st.subheader("Estat actual")

        # Agafem només els dos últims passos per poder calcular deltes sense carregar
        # tot l'històric a cada rerun.
        history_len = len(st.session_state.ix_history)
        curr = st.session_state.ix_history[-1]
        prev = st.session_state.ix_history[-2] if history_len > 1 else None

        heat_col = find_matching_column(curr, ['heating', 'htg_setpoint'])
        cool_col = find_matching_column(curr, ['cooling', 'clg_setpoint'])
        in_temp_col = find_matching_column(curr, ['air_temperature', 'indoor_temperature'])
        out_temp_col = find_matching_column(curr, ['outdoor_temperature', 'site_outdoor_air_drybulb_temperature'])
        power_col = find_matching_column(curr, ['demand_rate', 'power', 'hvac_elèctricity_demand'])

        # Primera fila: què ha decidit l'actuador i com canvia respecte al pas anterior.
        # Metriques accions actuador
        st.markdown("##### Accions de l'actuador")
        render_metric_row(
            [
                build_metric_item(
                    curr,
                    prev,
                    heat_col,
                    label="Setpt. Calor (°C)",
                    value_format=lambda value: f"{value:.1f}°C",
                    delta_format=lambda delta: f"{delta:+.1f}°C",
                    delta_color="normal",
                    empty_message="Sense Setpoint de Calor",
                ),
                build_metric_item(
                    curr,
                    prev,
                    cool_col,
                    label="Setpt. Fred (°C)",
                    value_format=lambda value: f"{value:.1f}°C",
                    delta_format=lambda delta: f"{delta:+.1f}°C",
                    delta_color="inverse",
                    empty_message="Sense Setpoint de Fred",
                ),
                _calendar_or_reward_metric(curr, prev, core_env),
            ]
        )


        # Separador dashboard
        st.markdown("<div class='studio-spacer-100'></div>", unsafe_allow_html=True)

        # Segona fila: estat sensorial mínim per entendre si l'acció tenia sentit.
        # Metriques sensors
        st.markdown("##### Sensors (observacions)")
        render_metric_row(
            [
                build_metric_item(
                    curr,
                    prev,
                    in_temp_col,
                    label="Temp. Interior T1",
                    value_format=lambda value: f"{value:.1f}°C",
                    delta_format=lambda delta: f"{delta:+.2f}°C",
                    empty_message="Sense T. Interior",
                ),
                build_metric_item(
                    curr,
                    prev,
                    out_temp_col,
                    label="Meteo. exterior",
                    value_format=lambda value: f"{value:.1f}°C",
                    delta_format=lambda delta: f"{delta:+.1f}°C",
                    empty_message="Sense T. Exterior",
                ),
                build_metric_item(
                    curr,
                    prev,
                    power_col,
                    label="Consum HVAC (Act/Rate)",
                    value_format=lambda value: f"{value / 1000:.2f} kW",
                    delta_format=lambda delta: f"{delta / 1000:+.2f} kW",
                    delta_color="inverse",
                    empty_message="Sense Consum Electric",
                ),
            ]
        )


        # Separador confort
        st.markdown("<div class='studio-spacer-100'></div>", unsafe_allow_html=True)

        # Tercera fila: confort calculat amb el rang actiu de la reward.
        # Bloc estat confort
        st.markdown("##### Estat de Confort")

        # Columnes confort PMV
        comfort_col1, comfort_col2 = st.columns(2)

        with comfort_col1:
            if in_temp_col:
                current_temp = curr[in_temp_col]
                # Busquem els rangs a la reward activa. Si no hi són, fem servir valors típics
                # per poder donar feedback sense rebentar la simulació.
                if hasattr(core_env, 'get_wrapper_attr'):
                    # Sinergym acostuma a guardar aquests rangs dins reward_kwargs.
                    is_summer = False
                    try:
                        # Inferència simple de temporada a partir del mes actual.
                        month_col = find_matching_column(curr, ['month'])
                        if month_col and curr[month_col] >= 6 and curr[month_col] <= 9:
                            is_summer = True
                    except: pass

                    try:
                        # Depèn de la reward concreta, per això el fallback és intencionat.
                        cfg = core_env.get_wrapper_attr('reward_kwargs') if hasattr(core_env, 'get_wrapper_attr') else {}
                        r_comfort_winter = cfg.get('range_comfort_winter', (20.0, 23.5))
                        r_comfort_summer = cfg.get('range_comfort_summer', (23.0, 26.0))
                    except:
                        r_comfort_winter = (20.0, 23.5)
                        r_comfort_summer = (23.0, 26.0)

                    active_range = r_comfort_summer if is_summer else r_comfort_winter

                    if active_range[0] <= current_temp <= active_range[1]:
                        # Missatge confort correcte
                        st.markdown(
                            (
                                "<div style='padding:0.78rem 1rem;border-radius:8px;"
                                "background:#f0fdf4;color:#166534;font-weight:700;'>"
                                f"Dins el Rang de Confort ({active_range[0]}°C a {active_range[1]}°C)"
                                "</div>"
                            ),
                            unsafe_allow_html=True,
                        )
                    elif current_temp < active_range[0]:
                        # Error confort fred
                        st.markdown(
                            (
                                "<div style='padding:0.78rem 1rem;border-radius:8px;"
                                "background:#eff6ff;color:#1d4ed8;font-weight:700;'>"
                                f"Massa Fred (Objectiu: {active_range[0]}°C a {active_range[1]}°C)"
                                "</div>"
                            ),
                            unsafe_allow_html=True,
                        )
                    else:
                        # Error confort calor
                        st.markdown(
                            (
                                "<div style='padding:0.78rem 1rem;border-radius:8px;"
                                "background:#fef2f2;color:#b91c1c;font-weight:700;'>"
                                f"Massa Calor (Objectiu: {active_range[0]}°C a {active_range[1]}°C)"
                                "</div>"
                            ),
                            unsafe_allow_html=True,
                        )
            else:
                # Avís confort no calculable
                st.info("No es pot calcular el confort (Sense Temperatura Interior)")

        with comfort_col2:
            pmv_col = find_matching_column(curr, ['pmv'])
            ppd_col = find_matching_column(curr, ['ppd'])

            if pmv_col and ppd_col:
                val_pmv = curr[pmv_col]
                val_ppd = curr[ppd_col]

                # PMV Ideal: 0 (Rang -0.5 a +0.5). PPD Ideal: < 10%
                pmv_class = (
                    "comfort-value-good"
                    if -0.5 <= val_pmv <= 0.5
                    else "comfort-value-warn"
                    if -1.0 <= val_pmv <= 1.0
                    else "comfort-value-bad"
                )
                ppd_class = (
                    "comfort-value-good"
                    if val_ppd <= 10.0
                    else "comfort-value-warn"
                    if val_ppd <= 20.0
                    else "comfort-value-bad"
                )


                # Text PMV
                st.markdown(
                    f"**Vot Mitjà (PMV):** <span class='{pmv_class}'>{val_pmv:.2f}</span>",
                    unsafe_allow_html=True,
                )
                # Text PPD
                st.markdown(
                    f"**Insatisfacció (PPD):** <span class='{ppd_class}'>{val_ppd:.1f}%</span>",
                    unsafe_allow_html=True,
                )
