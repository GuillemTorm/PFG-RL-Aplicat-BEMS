"""Controls de wrappers i registre per a la pàgina d'entrenament."""

from __future__ import annotations

import streamlit as st

from backend.entrenar_agent_constants import DEFAULT_FORECAST_COLUMNS, ENERGY_COST_DIR
from backend.entrenar_agent_env import list_files
from backend.entrenar_agent_session import (
    reset_widget_state_if_disabled,
    sanitize_multiselect_state,
    seed_discrete_incremental_widget_defaults,
    seed_incremental_widget_defaults,
    training_form_key,
)


def _checkbox_kwargs(field: str, default: bool = False, *, disabled: bool = False) -> dict:
    """Prepara els arguments comuns dels checkboxes del formulari d'entrenament."""
    key = training_form_key(field)
    kwargs = {"disabled": disabled, "key": key}
    if key not in st.session_state:
        kwargs["value"] = default
    return kwargs


def render_observation_wrappers(
    observation_variables: list[str],
    context_variables: list[str],
    candidate_temp_vars: list[str],
    candidate_setpoint_vars: list[str],
) -> dict:
    """Pinta els controls que modifiquen les observacions abans d'arribar a l'agent."""
    # Seccio wrappers observacio
    st.caption("OBSERVACIO")

    # Streamlit conserva valors antics encara que canviï l'entorn; sanejar-los aquí
    # evita que un multiselect apunti a variables que ja no existeixen.
    sanitize_multiselect_state("previous_variables", observation_variables, candidate_temp_vars[:1])
    sanitize_multiselect_state("weather_forecast_columns", DEFAULT_FORECAST_COLUMNS, list(DEFAULT_FORECAST_COLUMNS))
    sanitize_multiselect_state("delta_temp_variables", observation_variables, candidate_temp_vars)
    sanitize_multiselect_state("delta_setpoint_variables", observation_variables, candidate_setpoint_vars[:1])
    sanitize_multiselect_state("reduced_observations", observation_variables, [])

    # Checkbox datetime wrapper
    enable_datetime_wrapper = st.checkbox(
        "DatetimeWrapper",
        False,
        key=training_form_key("enable_datetime_wrapper"),
    )

    # Checkbox previous observation
    enable_previous_wrapper = st.checkbox(
        "PreviousObservationWrapper",
        False,
        key=training_form_key("enable_previous_wrapper"),
    )
    previous_variables = []
    if enable_previous_wrapper:
        # Selector variables pas anterior
        previous_variables = st.multiselect(
            "Variables pas anterior",
            observation_variables,
            default=candidate_temp_vars[:1],
            key=training_form_key("previous_variables"),
        )

    # Checkbox multi observacio
    enable_multi_obs_wrapper = st.checkbox(
        "MultiObsWrapper",
        False,
        key=training_form_key("enable_multi_obs_wrapper"),
    )
    multi_obs_n = 5
    multi_obs_flatten = True
    if enable_multi_obs_wrapper:
        # Slider observacions apilades
        multi_obs_n = st.slider(
            "Observacions apilades",
            2,
            12,
            5,
            key=training_form_key("multi_obs_n"),
        )
        # Checkbox aplanar observacio
        multi_obs_flatten = st.checkbox(
            "Aplanar observacio",
            True,
            key=training_form_key("multi_obs_flatten"),
        )

    # Checkbox normalitzar observacio
    enable_normalize_obs_wrapper = st.checkbox(
        "NormalizeObservation",
        False,
        key=training_form_key("enable_normalize_obs_wrapper"),
    )
    normalize_obs_auto = True
    normalize_obs_epsilon = 1e-8
    normalize_obs_mean = ""
    normalize_obs_var = ""
    if enable_normalize_obs_wrapper:
        # Checkbox actualitzar normalitzacio
        normalize_obs_auto = st.checkbox(
            "Actualitzacio automatica mean/var",
            True,
            key=training_form_key("normalize_obs_auto"),
        )
        # Input epsilon normalitzacio
        normalize_obs_epsilon = st.number_input(
            "epsilon",
            1e-10,
            1e-2,
            1e-8,
            format="%.10f",
            key=training_form_key("normalize_obs_epsilon"),
        )
        # Input ruta mean
        normalize_obs_mean = st.text_input(
            "Ruta mean.txt (opcional)",
            "",
            key=training_form_key("normalize_obs_mean"),
        )
        # Input ruta var
        normalize_obs_var = st.text_input(
            "Ruta var.txt (opcional)",
            "",
            key=training_form_key("normalize_obs_var"),
        )

    # Checkbox previsio clima
    enable_weather_forecast_wrapper = st.checkbox(
        "WeatherForecastingWrapper",
        False,
        key=training_form_key("enable_weather_forecast_wrapper"),
    )
    weather_forecast_n = 5
    weather_forecast_delta = 1
    weather_forecast_columns = list(DEFAULT_FORECAST_COLUMNS)
    if enable_weather_forecast_wrapper:
        # Slider mostres previsio
        weather_forecast_n = st.slider(
            "Mostres de previsi",
            1,
            24,
            5,
            key=training_form_key("weather_forecast_n"),
        )
        # Slider separacio previsio
        weather_forecast_delta = st.slider(
            "Separacio entre mostres",
            1,
            24,
            1,
            key=training_form_key("weather_forecast_delta"),
        )
        # Selector variables previsio
        weather_forecast_columns = st.multiselect(
            "Variables de previsi",
            DEFAULT_FORECAST_COLUMNS,
            default=DEFAULT_FORECAST_COLUMNS,
            key=training_form_key("weather_forecast_columns"),
        )

    # Checkbox delta temperatura
    enable_delta_temp_wrapper = st.checkbox(
        "DeltaTempWrapper",
        False,
        key=training_form_key("enable_delta_temp_wrapper"),
    )
    delta_temp_variables = []
    delta_setpoint_variables = []
    if enable_delta_temp_wrapper:
        # Selector variables temperatura
        delta_temp_variables = st.multiselect(
            "Variables temperatura",
            observation_variables,
            default=candidate_temp_vars,
            key=training_form_key("delta_temp_variables"),
        )
        # Selector variables setpoint
        delta_setpoint_variables = st.multiselect(
            "Variables setpoint",
            observation_variables,
            default=candidate_setpoint_vars[:1],
            key=training_form_key("delta_setpoint_variables"),
        )

    # Checkbox reduir observacions
    enable_reduce_obs_wrapper = st.checkbox(
        "ReduceObservationWrapper",
        False,
        key=training_form_key("enable_reduce_obs_wrapper"),
    )
    reduced_observations = []
    if enable_reduce_obs_wrapper:
        # Selector observacions excloses
        reduced_observations = st.multiselect(
            "Variables a excloure",
            observation_variables,
            default=[],
            key=training_form_key("reduced_observations"),
        )

    variability_disabled = not bool(context_variables)
    # Si l'entorn no exposa variables de context, el wrapper es desactiva i també netegem
    # l'estat antic perquè no torni a aparèixer marcat en una reexecució.
    reset_widget_state_if_disabled("enable_variability_context_wrapper", variability_disabled)
    # Checkbox variabilitat context
    enable_variability_context_wrapper = st.checkbox(
        "VariabilityContextWrapper",
        **_checkbox_kwargs("enable_variability_context_wrapper", disabled=variability_disabled),
    )
    variability_context_low = []
    variability_context_high = []
    variability_delta_value = 1.0
    variability_step_frequency_min = 96
    variability_step_frequency_max = 96 * 7
    if enable_variability_context_wrapper:
        # Seccio rang context
        st.caption("Rang de variabilitat del context")
        for context_variable in context_variables:
            # Inputs rang context
            low_col, high_col = st.columns(2)
            with low_col:
                variability_context_low.append(
                    # Input context minim
                    st.number_input(
                        f"{context_variable} min",
                        value=0.0,
                        key=training_form_key(f"variability_context_low_{context_variable}"),
                    )
                )
            with high_col:
                variability_context_high.append(
                    # Input context maxim
                    st.number_input(
                        f"{context_variable} max",
                        value=2.0,
                        key=training_form_key(f"variability_context_high_{context_variable}"),
                    )
                )
        # Input delta context
        variability_delta_value = st.number_input(
            "Delta context",
            min_value=0.01,
            value=1.0,
            step=0.1,
            key=training_form_key("variability_delta_value"),
        )
        # Inputs frequencia context
        freq_col1, freq_col2 = st.columns(2)
        with freq_col1:
            # Input frequencia minima
            variability_step_frequency_min = st.number_input(
                "Freq. min passos",
                min_value=1,
                value=96,
                step=1,
                key=training_form_key("variability_step_frequency_min"),
            )
        with freq_col2:
            # Input frequencia maxima
            variability_step_frequency_max = st.number_input(
                "Freq. max passos",
                min_value=2,
                value=96 * 7,
                step=1,
                key=training_form_key("variability_step_frequency_max"),
            )

    return {
        "enable_datetime_wrapper": enable_datetime_wrapper,
        "enable_previous_wrapper": enable_previous_wrapper,
        "previous_variables": previous_variables,
        "enable_multi_obs_wrapper": enable_multi_obs_wrapper,
        "multi_obs_n": multi_obs_n,
        "multi_obs_flatten": multi_obs_flatten,
        "enable_normalize_obs_wrapper": enable_normalize_obs_wrapper,
        "normalize_obs_auto": normalize_obs_auto,
        "normalize_obs_epsilon": normalize_obs_epsilon,
        "normalize_obs_mean": normalize_obs_mean,
        "normalize_obs_var": normalize_obs_var,
        "enable_weather_forecast_wrapper": enable_weather_forecast_wrapper,
        "weather_forecast_n": weather_forecast_n,
        "weather_forecast_delta": weather_forecast_delta,
        "weather_forecast_columns": weather_forecast_columns,
        "enable_delta_temp_wrapper": enable_delta_temp_wrapper,
        "delta_temp_variables": delta_temp_variables,
        "delta_setpoint_variables": delta_setpoint_variables,
        "enable_reduce_obs_wrapper": enable_reduce_obs_wrapper,
        "reduced_observations": reduced_observations,
        "enable_variability_context_wrapper": enable_variability_context_wrapper,
        "variability_context_low": variability_context_low,
        "variability_context_high": variability_context_high,
        "variability_delta_value": variability_delta_value,
        "variability_step_frequency_min": variability_step_frequency_min,
        "variability_step_frequency_max": variability_step_frequency_max,
    }


def render_action_wrappers(
    env_meta: dict,
    action_variables: list[str],
    action_space,
) -> dict:
    """Pinta els controls que canvien com l'agent envia accions a l'entorn."""
    # Seccio wrappers accio
    st.caption("ACCIO")

    # Els wrappers incrementals només tenen sentit quan l'acció és contínua: converteixen
    # una ordre absoluta en canvis petits, més semblants a moure un termòstat real.
    sanitize_multiselect_state("incremental_variables", action_variables, action_variables[:1])
    # Checkbox incremental wrapper
    enable_incremental_wrapper = st.checkbox(
        "IncrementalWrapper",
        False,
        disabled=not env_meta["is_continuous"],
        key=training_form_key("enable_incremental_wrapper"),
    )
    incremental_variables = []
    incremental_definition = {}
    incremental_initial_values = []
    if enable_incremental_wrapper:
        seed_incremental_widget_defaults(action_variables)
        # Selector accions incrementals
        incremental_variables = st.multiselect(
            "Variables d'accio incrementals",
            action_variables,
            default=action_variables[:1],
            key=training_form_key("incremental_variables"),
        )
        for variable_name in incremental_variables:
            action_index = action_variables.index(variable_name)
            low_value = float(action_space.low[action_index])
            high_value = float(action_space.high[action_index])
            default_initial = float((low_value + high_value) / 2.0)
            # Titol variable incremental
            st.markdown(f"**{variable_name}**")
            # Inputs accio incremental
            init_col, delta_col, step_col = st.columns(3)
            with init_col:
                # Input valor inicial
                initial_value = st.number_input(
                    "Valor inicial",
                    value=default_initial,
                    key=training_form_key(f"incr_init_{variable_name}"),
                )
            with delta_col:
                # Input delta max
                delta_value = st.number_input(
                    "Delta max",
                    min_value=0.1,
                    value=max((high_value - low_value) / 4.0, 0.5),
                    step=0.1,
                    key=training_form_key(f"incr_delta_{variable_name}"),
                )
            with step_col:
                # Input pas incremental
                step_value = st.number_input(
                    "Pas",
                    min_value=0.1,
                    value=max((high_value - low_value) / 20.0, 0.1),
                    step=0.1,
                    key=training_form_key(f"incr_step_{variable_name}"),
                )
            incremental_definition[variable_name] = (delta_value, step_value)
            incremental_initial_values.append(initial_value)
        st.session_state[training_form_key("incremental_definition")] = incremental_definition
        st.session_state[training_form_key("incremental_initial_values")] = incremental_initial_values

    # Checkbox incremental discret
    enable_discrete_incremental_wrapper = st.checkbox(
        "DiscreteIncrementalWrapper",
        False,
        disabled=not env_meta["is_continuous"],
        key=training_form_key("enable_discrete_incremental_wrapper"),
    )
    discrete_incremental_initial_values = []
    discrete_incremental_delta = 2.0
    discrete_incremental_step = 0.5
    if enable_discrete_incremental_wrapper:
        seed_discrete_incremental_widget_defaults(action_variables)
        for action_index, variable_name in enumerate(action_variables):
            low_value = float(action_space.low[action_index])
            high_value = float(action_space.high[action_index])
            default_initial = float((low_value + high_value) / 2.0)
            discrete_incremental_initial_values.append(
                # Input valor inicial discret
                st.number_input(
                    f"Valor inicial {variable_name}",
                    value=default_initial,
                    key=training_form_key(f"disc_incr_init_{variable_name}"),
                )
            )
        # Input delta discret
        discrete_incremental_delta = st.number_input(
            "Delta discret max",
            min_value=0.1,
            value=2.0,
            step=0.1,
            key=training_form_key("discrete_incremental_delta"),
        )
        # Input pas discret
        discrete_incremental_step = st.number_input(
            "Pas discret",
            min_value=0.1,
            value=0.5,
            step=0.1,
            key=training_form_key("discrete_incremental_step"),
        )
        st.session_state[training_form_key("discrete_incremental_initial_values")] = (
            discrete_incremental_initial_values
        )

    normalize_action_disabled = (
        not env_meta["is_continuous"]
        or enable_incremental_wrapper
        or enable_discrete_incremental_wrapper
    )
    # NormalizeAction és còmode com a default en Box, però no el deixem conviure amb
    # wrappers incrementals perquè llavors l'escala de control queda doblement transformada.
    normalize_action_key = training_form_key("enable_normalize_action")
    normalize_action_seed_key = training_form_key("enable_normalize_action_default_seeded")
    reset_widget_state_if_disabled("enable_normalize_action", normalize_action_disabled)
    if normalize_action_disabled:
        st.session_state.pop(normalize_action_seed_key, None)
    elif (
        not st.session_state.get(normalize_action_seed_key)
        and normalize_action_key not in st.session_state
    ):
        st.session_state[normalize_action_key] = True
        st.session_state[normalize_action_seed_key] = True
    # Checkbox normalitzar accio
    enable_normalize_action = st.checkbox(
        "NormalizeAction",
        **_checkbox_kwargs(
            "enable_normalize_action",
            default=not normalize_action_disabled,
            disabled=normalize_action_disabled,
        ),
    )
    if normalize_action_disabled:
        enable_normalize_action = False

    storage_smoothing_disabled = env_meta.get("building_name") != "OfficeGridStorageSmoothing.epJSON"
    # Aquest wrapper està escrit per a un edifici concret amb bateria i restriccions de xarxa;
    # en la resta d'entorns el mostrem desactivat per evitar errors difícils d'entendre.
    reset_widget_state_if_disabled("enable_storage_smoothing_wrapper", storage_smoothing_disabled)
    # Checkbox storage smoothing
    enable_storage_smoothing_wrapper = st.checkbox(
        "OfficeGridStorageSmoothingActionConstraintsWrapper",
        **_checkbox_kwargs(
            "enable_storage_smoothing_wrapper",
            disabled=storage_smoothing_disabled,
        ),
    )

    return {
        "enable_incremental_wrapper": enable_incremental_wrapper,
        "incremental_variables": incremental_variables,
        "incremental_definition": incremental_definition,
        "incremental_initial_values": incremental_initial_values,
        "enable_discrete_incremental_wrapper": enable_discrete_incremental_wrapper,
        "discrete_incremental_initial_values": discrete_incremental_initial_values,
        "discrete_incremental_delta": discrete_incremental_delta,
        "discrete_incremental_step": discrete_incremental_step,
        "enable_normalize_action": enable_normalize_action,
        "enable_storage_smoothing_wrapper": enable_storage_smoothing_wrapper,
    }


def render_energy_logging_wrappers(
    energy_cost_files: list[str],
    initial_energy_cost_path: str,
    initial_file_logger_name: str,
) -> dict:
    """Pinta els controls de cost energètic i de fitxer de registre."""
    # Seccio energia i logs
    st.caption("ENERGIA I LOGS")

    energy_cost_path = initial_energy_cost_path
    file_logger_name = initial_file_logger_name

    # Checkbox energy cost
    use_energy_cost = st.checkbox(
        "EnergyCostWrapper",
        False,
        key=training_form_key("use_energy_cost"),
    )
    if use_energy_cost:
        if energy_cost_files:
            # Selector fitxer cost
            selected_energy_cost = st.selectbox(
                "Fitxer cost",
                energy_cost_files,
                index=energy_cost_files.index(energy_cost_path) if energy_cost_path in energy_cost_files else 0,
            )
            energy_cost_path = selected_energy_cost
        # Input ruta cost energia
        energy_cost_path = st.text_input(
            "Ruta fitxer cost",
            energy_cost_path,
            key=training_form_key("energy_cost_path"),
        )

    # Checkbox file logger
    use_file_logger = st.checkbox(
        "EnergyCostFileLogger",
        False,
        key=training_form_key("use_file_logger"),
    )
    if use_file_logger:
        # Input nom log energia
        file_logger_name = st.text_input(
            "Nom fitxer registre",
            "energy_cost_log.csv",
            key=training_form_key("file_logger_name"),
        )

    return {
        "energy_cost_path": energy_cost_path,
        "file_logger_name": file_logger_name,
        "use_energy_cost": use_energy_cost,
        "use_file_logger": use_file_logger,
    }


def render_wrappers_section(
    env_meta: dict,
    observation_variables: list[str],
    action_variables: list[str],
    action_space,
    context_variables: list[str],
    candidate_temp_vars: list[str],
    candidate_setpoint_vars: list[str],
) -> dict:
    """Agrupa els controls de wrappers i retorna una configuració plana per al backend."""
    energy_cost_files = list_files(ENERGY_COST_DIR, {".csv"})
    default_energy_cost_path = (
        energy_cost_files[0] if energy_cost_files
        else str(ENERGY_COST_DIR / "PVPC_active_energy_billing_Iberian_Peninsula_2023.csv")
    )
    default_file_logger_name = "energy_cost_log.csv"
    initial_energy_cost_path = st.session_state.get(
        training_form_key("energy_cost_path"),
        default_energy_cost_path,
    )
    initial_file_logger_name = st.session_state.get(
        training_form_key("file_logger_name"),
        default_file_logger_name,
    )

    # Columnes wrappers observacio accio
    observation_column, action_column = st.columns(2)
    with observation_column:
        observation_wrapper_values = render_observation_wrappers(
            observation_variables=observation_variables,
            context_variables=context_variables,
            candidate_temp_vars=candidate_temp_vars,
            candidate_setpoint_vars=candidate_setpoint_vars,
        )
    with action_column:
        action_wrapper_values = render_action_wrappers(
            env_meta=env_meta,
            action_variables=action_variables,
            action_space=action_space,
        )
        energy_logging_values = render_energy_logging_wrappers(
            energy_cost_files=energy_cost_files,
            initial_energy_cost_path=initial_energy_cost_path,
            initial_file_logger_name=initial_file_logger_name,
        )

    # Es retorna un diccionari pla perquè el muntatge final de training pugui barrejar
    # reward, wrappers i paràmetres de l'agent sense dependre de l'ordre visual de la pàgina.
    return {
        **energy_logging_values,
        **observation_wrapper_values,
        **action_wrapper_values,
    }
