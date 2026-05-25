"""Gestió de l'estat de sessió per a la pàgina d'entrenament de l'agent."""

from __future__ import annotations

import streamlit as st

from backend.entrenar_agent_constants import TRAINING_RUNTIME_KEY
from backend.entrenar_agent_runtime import clear_training_runtime

BATTERY_REWARDS = {
    "BatteryHVACReward",
    "MultiZoneBatteryHVACReward",
    "MultizoneEnergyCostBatteryHVACReward",
}
TRAINING_WORKSPACE_KEY = "training_live_workspace_path"
TRAINING_FORM_PREFIX = "training_form_"
TRAINING_SAVED_RUN_KEY = "training_saved_run"
TRAINING_LOADED_ARTIFACT_KEY = "training_loaded_artifact"
TRAINING_RANGE_FIELDS = {
    "range_winter",
    "range_summer",
    "range_comfort_hours",
    "occupied_hours",
}


def training_form_key(field: str) -> str:
    """Retorna la clau d'estat de sessió per a un camp de formulari d'entrenament."""
    return f"{TRAINING_FORM_PREFIX}{field}"


def reset_widget_state_if_disabled(field: str, disabled: bool, value=False) -> None:
    """Restableix l'estat de sessió d'un widget quan està desactivat."""
    if disabled:
        st.session_state[training_form_key(field)] = value


def ensure_select_state(field: str, options: list[str], fallback: str | None = None) -> str:
    """Assegureu-vos que un camp de casella de selecció tingui un valor vàlid en estat de sessió.

    Si el valor actual no es troba a les opcions, se substitueix per una alternativa (si és vàlid)
    o per la primera opció.
    """
    key = training_form_key(field)
    if not options:
        st.session_state[key] = ""
        return ""

    current_value = st.session_state.get(key)
    if current_value not in options:
        st.session_state[key] = fallback if fallback in options else options[0]
    return st.session_state[key]


def selectbox_state_kwargs(field: str, options: list, fallback=None) -> dict:
    """Retorna kwargs per a selectbox sense duplicar valor per defecte i session_state."""
    key = training_form_key(field)
    current_value = st.session_state.get(key)
    if current_value in options:
        return {"key": key}

    if key in st.session_state:
        st.session_state.pop(key, None)

    if fallback in options:
        index = options.index(fallback)
    else:
        index = 0
    return {"index": index, "key": key}


def sanitize_multiselect_state(
    field: str,
    options: list[str],
    fallback: list[str] | None = None,
) -> None:
    """Elimina valors obsolets d'un camp de selecció múltiple en estat de sessió.

    Els valors que ja no estan presents a les opcions s'eliminen. Si el resultat és
    buit i es proporciona una alternativa, s'utilitzen elements de reserva vàlids.
    """
    key = training_form_key(field)
    current_value = st.session_state.get(key)
    if current_value is None:
        return

    if not isinstance(current_value, (list, tuple, set)):
        current_value = fallback or []

    sanitized = [item for item in current_value if item in options]
    if not sanitized and fallback is not None:
        sanitized = [item for item in fallback if item in options]
    st.session_state[key] = sanitized


def normalize_training_range_state() -> None:
    """Converteix els camps d'interval codificats per llista en tuples en estat de sessió.

    Streamlit serialitza les tuples lliscants com a llistes quan es restaura l'estat de la sessió
    d'una carrera guardada; aquesta funció els torna a convertir en tuples de manera que
    ``st.slider`` no genera cap desajust de tipus.
    """
    for field in TRAINING_RANGE_FIELDS:
        key = training_form_key(field)
        value = st.session_state.get(key)
        if isinstance(value, list) and len(value) == 2:
            st.session_state[key] = tuple(value)


def clear_incremental_widget_state() -> None:
    """Elimina totes les claus del widget incremental dinàmic de l'estat de sessió.

    Les claus s'identifiquen pel seu patró de prefix, que és generat per
    ``training_form_key`` per a cada widget incremental per variable.
    """
    dynamic_prefixes = (
        training_form_key("incr_init_"),
        training_form_key("incr_delta_"),
        training_form_key("incr_step_"),
        training_form_key("disc_incr_init_"),
    )
    for session_key in list(st.session_state.keys()):
        if session_key.startswith(dynamic_prefixes):
            st.session_state.pop(session_key, None)


def apply_saved_training_ui_state(ui_state: dict, envs: list[str]) -> None:
    """Restaura un estat d'entrenament desat anteriorment UI a l'estat de sessió.

    Primer esborra totes les claus del widget incrementals i després escriu cada camp des de
    ``ui_state``, converteix els camps d'interval en tuples i restableix l'entrenament
    temps d'execució perquè la configuració carregada tingui efecte a la següent execució.
    """
    clear_incremental_widget_state()
    for field, value in (ui_state or {}).items():
        normalized_value = tuple(value) if field in TRAINING_RANGE_FIELDS and isinstance(value, list) else value
        st.session_state[training_form_key(field)] = normalized_value

    ensure_select_state("env_id", envs)
    clear_training_runtime()
    st.session_state.is_training = False
    st.session_state.stop_training = False
    st.session_state.pop(TRAINING_RUNTIME_KEY, None)
    st.session_state.pop(TRAINING_WORKSPACE_KEY, None)


def seed_incremental_widget_defaults(selected_variables: list[str]) -> None:
    """Emplena els widgets incrementals per variable des de l'estat desat.

    Només escriu a claus d'estat de sessió que encara no existeixen, de manera que
    Els valors dels widgets en directe mai es sobreescriuen en tornar a renderitzar.
    """
    stored_variables = st.session_state.get(training_form_key("incremental_variables"), []) or []
    stored_initial_values = st.session_state.get(training_form_key("incremental_initial_values"), []) or []
    stored_definition = st.session_state.get(training_form_key("incremental_definition"), {}) or {}
    initial_values_map = {
        variable_name: stored_initial_values[index]
        for index, variable_name in enumerate(stored_variables)
        if index < len(stored_initial_values)
    }

    for variable_name in selected_variables:
        init_key = training_form_key(f"incr_init_{variable_name}")
        delta_key = training_form_key(f"incr_delta_{variable_name}")
        step_key = training_form_key(f"incr_step_{variable_name}")
        if init_key not in st.session_state and variable_name in initial_values_map:
            st.session_state[init_key] = initial_values_map[variable_name]

        definition_values = stored_definition.get(variable_name)
        if isinstance(definition_values, (list, tuple)) and len(definition_values) == 2:
            if delta_key not in st.session_state:
                st.session_state[delta_key] = definition_values[0]
            if step_key not in st.session_state:
                st.session_state[step_key] = definition_values[1]


def seed_discrete_incremental_widget_defaults(action_variables: list[str]) -> None:
    """Emplena els widgets incrementals discrets per variable des de l'estat desat.

    Només escriu a claus d'estat de sessió que encara no existeixen.
    """
    stored_initial_values = st.session_state.get(
        training_form_key("discrete_incremental_initial_values"),
        [],
    ) or []
    for action_index, variable_name in enumerate(action_variables):
        widget_key = training_form_key(f"disc_incr_init_{variable_name}")
        if widget_key not in st.session_state and action_index < len(stored_initial_values):
            st.session_state[widget_key] = stored_initial_values[action_index]
