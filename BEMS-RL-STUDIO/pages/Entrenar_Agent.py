"""Pàgina d'entrenament de l'agent per a l'aplicació BEMS-RL-STUDIO.

Orquestra el flux complet d'entrenament: selecció de l'entorn, configuració de la
reward, wrappers, hiperparàmetres de l'agent i bucle incremental amb gràfics en directe.
"""

from __future__ import annotations

import streamlit as st

from sidebar_nav import configure_studio_page

from backend.entrenar_agent_constants import (
    POLICIES,
    REWARD_CLASSES,
    TRAINING_RESULT_KEY,
    TRAINING_RUNTIME_KEY,
)
from backend.entrenar_agent_env import get_env_metadata, list_registered_envs
from backend.entrenar_agent_rewards import assemble_training_payload
from backend.entrenar_agent_runtime import (
    clear_training_runtime,
    create_training_runtime,
    learn_training_chunk,
    save_training_artifacts,
)
from backend.sb3_utils import ALGOS
from backend.entrenar_agent_session import (
    TRAINING_WORKSPACE_KEY,
    normalize_training_range_state,
    selectbox_state_kwargs,
)
from backend.entrenar_agent_charts import (
    _get_workspace_from_runtime,
    render_live_training_charts,
)
from page_components.training_agent import render_agent_params_section
from page_components.training_rewards import render_reward_kwargs_section
from page_components.training_shared import (
    PAGE_LAYOUT,
    PAGE_TITLE,
    render_saved_training_library,
    render_training_hero,
    render_training_section,
)
from page_styles.training import inject_training_styles
from page_components.training_wrappers import render_wrappers_section


def train_tab() -> None:
    """Punt d'entrada a la pàgina d'entrenament.

    Orquestra totes les seccions UI en ordre:
    1. Inicialització de l'estat de la sessió.
    2. Entorn, algorisme i selecció de polítiques.
    3. Recompensa kwargs (pesos, rangs estacionals, comoditat).
    4. Selecció i configuració de wrappers (observació, acció, logs).
    5. Paràmetres de l'agent (taxa d'aprenentatge, n_steps, total_timesteps).
    6. Controls d'execució (inici/aturada).
    7. Cicle d'entrenament incremental amb gràfics en directe.
    """
    configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
    inject_training_styles()

    # Inicialització de l'estat de la sessió
    if "is_training" not in st.session_state:
        st.session_state.is_training = False
    if "stop_training" not in st.session_state:
        st.session_state.stop_training = False

    envs = list_registered_envs()
    normalize_training_range_state()
    render_training_hero()
    render_saved_training_library(envs)
    st.divider()

    # Secció 1: configuració de l'entorn
    render_training_section(
        "Configuracio d'entorn",
        "Seleccio base",
        "Defineix l'entorn, l'algorisme i la politica abans de construir la recompensa i els wrappers.",
    )
    # Selectors entorn i agent
    env_col1, env_col2 = st.columns(2)
    with env_col1:
        # Selector entorn
        env_id = st.selectbox(
            "Entorn",
            envs,
            **selectbox_state_kwargs("env_id", envs),
        )
        algo_options = list(ALGOS.keys())
        # Selector algorisme
        algo_name = st.selectbox(
            "Algorisme SB3",
            algo_options,
            **selectbox_state_kwargs("algo_name", algo_options),
        )
    with env_col2:
        # Selector politica
        policy_name = st.selectbox(
            "Politica SB3",
            POLICIES[algo_name],
            **selectbox_state_kwargs("policy_name", POLICIES[algo_name]),
        )
        reward_options = list(REWARD_CLASSES.keys())
        # Selector recompensa
        reward_name = st.selectbox(
            "Recompensa",
            reward_options,
            **selectbox_state_kwargs("reward_name", reward_options),
        )

    env_meta = get_env_metadata(env_id)
    spec                             = env_meta["spec"]
    variables                        = env_meta["variables"]
    observation_variables            = env_meta["observation_variables"]
    action_variables                 = env_meta["action_variables"]
    action_space                     = env_meta["action_space"]
    candidate_grid_energy_vars       = env_meta["candidate_grid_energy_vars"]
    candidate_battery_charge_vars    = env_meta["candidate_battery_charge_vars"]
    candidate_battery_discharge_vars = env_meta["candidate_battery_discharge_vars"]
    candidate_battery_loss_vars      = env_meta["candidate_battery_loss_vars"]

    # Secció 2: recompensa kwargs
    st.divider()
    render_training_section(
        "Reward kwargs",
        "Confort i energia",
        "Ajusta pesos, rangs estacionals i criteris de confort per construir la reward final.",
    )
    reward_kwargs_values = render_reward_kwargs_section(
        reward_name=reward_name,
        observation_variables=observation_variables,
        candidate_grid_energy_vars=candidate_grid_energy_vars,
        candidate_battery_charge_vars=candidate_battery_charge_vars,
        candidate_battery_discharge_vars=candidate_battery_discharge_vars,
        candidate_battery_loss_vars=candidate_battery_loss_vars,
    )

    # Secció 3: wrappers i logs
    st.divider()
    render_training_section(
        "Wrappers i logs",
        "Observacio i control",
        "Activa nomes els wrappers que necessites per enriquir l'observacio o restringir l'espai d'accions.",
    )
    wrapper_values = render_wrappers_section(
        env_meta=env_meta,
        observation_variables=observation_variables,
        action_variables=action_variables,
        action_space=action_space,
        context_variables=env_meta["context_variables"],
        candidate_temp_vars=env_meta["candidate_temp_vars"],
        candidate_setpoint_vars=env_meta["candidate_setpoint_vars"],
    )

    # Apartat 4: paràmetres de l'agent
    st.divider()
    render_training_section(
        "Parametres de l'agent",
        "Aprenentatge",
        "Configura el ritme d'aprenentatge, la mida dels blocs i el nombre total de timesteps.",
    )
    agent_params = render_agent_params_section(algo_name=algo_name)

    # Secció 5: controls d'execució
    st.divider()
    render_training_section(
        "Execucio",
        "Control",
        "Llança l'entrenament o atura'l de forma segura mantenint els artefactes guardats.",
    )
    # Botons control entrenament
    controls_col1, controls_col2 = st.columns(2)
    # Botó entrenar agent
    start_clicked = controls_col1.button(
        "Entrenar agent",
        disabled=st.session_state.is_training,
        width="stretch",
    )
    # Botó aturar entrenament
    stop_clicked = controls_col2.button(
        "Aturar entrenament",
        disabled=not st.session_state.is_training,
        width="stretch",
    )

    if start_clicked:
        clear_training_runtime()
        st.session_state.pop(TRAINING_RESULT_KEY, None)
        st.session_state.pop(TRAINING_WORKSPACE_KEY, None)
        st.session_state.is_training = True
        st.session_state.stop_training = False

    if stop_clicked and st.session_state.is_training:
        st.session_state.stop_training = True

    if not st.session_state.is_training:
        return

    # A partir d'aquí Streamlit reexecuta la pàgina moltes vegades. Si ja hi ha runtime,
    # no tornem a muntar payload ni entorn: només continuem el model que és a memòria.
    runtime = st.session_state.get(TRAINING_RUNTIME_KEY)
    runtime_ui_state = runtime.get("ui_state", {}) if runtime is not None else {}
    training_payload = (
        None
        if runtime is not None
        else assemble_training_payload({
            "spec":                              spec,
            "env_id":                            env_id,
            "algo_name":                         algo_name,
            "policy_name":                       policy_name,
            "reward_name":                       reward_name,
            "is_continuous":                     env_meta["is_continuous"],
            "is_discrete":                       env_meta["is_discrete"],
            "action_space_type":                 type(action_space).__name__,
            "building_name":                     env_meta["building_name"],
            "variables":                         variables,
            **reward_kwargs_values,
            **wrapper_values,
            **agent_params,
        })
    )

    if training_payload is not None:
        dropped_reward_kwargs = training_payload["dropped_reward_kwargs"]
        if dropped_reward_kwargs:
            # Avís reward kwargs ignorats
            st.warning(
                "La classe de reward carregada no admet alguns parametres i s'han omes. "
                f"Parametres ignorats: {', '.join(dropped_reward_kwargs)}."
            )

        dropped_algo_kwargs = training_payload.get("dropped_algo_kwargs", [])
        if dropped_algo_kwargs:
            # Avís SB3 kwargs ignorats
            st.info(
                "L'algorisme seleccionat no fa servir alguns parametres SB3 avancats: "
                f"{', '.join(dropped_algo_kwargs)}."
            )

        validation_errors = training_payload.get("validation_errors", [])
        if validation_errors:
            clear_training_runtime()
            st.session_state.is_training = False
            st.session_state.stop_training = False
            for message in validation_errors:
                # Error validacio entrenament
                st.error(message)
            return

        training_config = training_payload["training_config"]
    else:
        training_config = runtime["config"]

    if runtime is not None:
        runtime_config = runtime.get("config", {})
        linear_cost_rewards = {"LinearReward", "EnergyCostLinearReward"}
        # Si una run antiga porta EnergyCostWrapper amb una configuració que ja no quadra,
        # és més segur recrear el runtime que entrenar amb una reward recalculada a mitges.
        stale_energy_wrapper = any(
            wrapper.get("name") == "EnergyCostWrapper"
            and (
                "recalculate_reward" not in wrapper.get("params", {})
                or (
                    runtime_config.get("reward_name") not in linear_cost_rewards
                    and wrapper.get("params", {}).get("recalculate_reward", True)
                )
            )
            for wrapper in runtime_config.get("wrapper_configs", [])
        )
        # El runtime creat pel botó queda congelat entre reruns; els widgets poden canviar
        # visualment, però el model en curs ha de continuar amb la configuració inicial.
        if stale_energy_wrapper:
            clear_training_runtime()
            st.session_state.pop(TRAINING_WORKSPACE_KEY, None)
            runtime = None
    if runtime is None:
        runtime = create_training_runtime(
            training_config,
            ui_state=training_payload["ui_state"] if training_payload is not None else runtime_ui_state,
        )
        st.session_state[TRAINING_RUNTIME_KEY] = runtime

    if TRAINING_WORKSPACE_KEY not in st.session_state:
        workspace = _get_workspace_from_runtime(runtime)
        if workspace:
            st.session_state[TRAINING_WORKSPACE_KEY] = workspace

    active_config = runtime["config"]

    render_training_section(
        "Estat de l'entrenament",
        "Seguiment",
        "Visualitza el progres actual, l'entorn actiu i l'estat del proces abans de guardar el model.",
    )
    st.write(f"Entorn seleccionat: `{active_config['env_id']}`")
    st.write(f"Algorisme: `{active_config['algo_name']}`")
    st.write(f"Recompensa: `{active_config['reward_name']}`")

    # Barra progrés entrenament
    progress_bar    = st.progress(0.0)
    # Text estat entrenament
    training_status = st.empty()

    current_timesteps = int(runtime["model"].num_timesteps)
    total_timesteps   = int(active_config["timesteps_per_year"])
    frac              = min(current_timesteps / max(1, total_timesteps), 1.0)
    progress_bar.progress(frac)

    render_training_section(
        "Evolucio de l'entrenament",
        "Temps real",
        "Metriques per episodi actualitzades automaticament en completar-se cada episodi.",
    )
    render_live_training_charts()

    try:
        if st.session_state.stop_training:
            training_status.warning("Aturant l'entrenament i guardant l'estat actual...")
        elif current_timesteps >= total_timesteps:
            training_status.success("Entrenament completat. Guardant el model...")
        else:
            training_status.info(
                f"Entrenament en curs: {current_timesteps}/{total_timesteps} timesteps ({frac * 100:.1f}%)."
            )
            remaining_timesteps = max(1, total_timesteps - current_timesteps)
            next_chunk = min(max(1, int(runtime["chunk_timesteps"])), remaining_timesteps)
            # Entrenem en blocs petits perquè la UI respongui, actualitzi gràfics i pugui
            # aturar-se sense esperar tot un any de simulació.
            learn_training_chunk(runtime["model"], next_chunk)
            st.session_state[TRAINING_RUNTIME_KEY] = runtime
            st.rerun()

        st.session_state[TRAINING_RESULT_KEY] = save_training_artifacts(runtime)
        clear_training_runtime()
        st.session_state.is_training = False
        st.session_state.stop_training = False
        st.rerun()
    except Exception:
        clear_training_runtime()
        st.session_state.is_training = False
        st.session_state.stop_training = False
        raise


# Streamlit executa aquesta funció quan carrega la pàgina.

train_tab()
