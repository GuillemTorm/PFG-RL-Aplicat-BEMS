"""Controls de configuració de recompenses per a la pàgina de entrenament."""

from __future__ import annotations

import streamlit as st

from backend.entrenar_agent_constants import COST_REWARDS, HOURLY_REWARDS, MULTIZONE_REWARDS
from backend.entrenar_agent_session import (
    BATTERY_REWARDS,
    sanitize_multiselect_state,
    selectbox_state_kwargs,
    training_form_key,
)


def render_reward_kwargs_section(
    reward_name: str,
    observation_variables: list[str],
    candidate_grid_energy_vars: list[str],
    candidate_battery_charge_vars: list[str],
    candidate_battery_discharge_vars: list[str],
    candidate_battery_loss_vars: list[str],
) -> dict:
    """Mostra tots els widgets de recompensa i retorna els valors recollits.

    Cobreix pesos d'energia/confort, rangs de confort estacionals, específics de la bateria
    paràmetres, paràmetres de recompensa de cost i configuració d'hores ocupades.

    Retorna:
        Un dict amb tots els kwargs de recompensa recollits dels widgets.
    """
    # Defaults de partida. Els ajustem després segons la reward escollida perquè una
    # bateria, un cost horari i una reward simple no tenen la mateixa escala.
    temperature_weight              = 0.4
    lambda_energy_cost              = 1.0
    comfort_threshold               = 0.5
    range_comfort_hours             = (9, 19)
    occupied_hours                  = (8, 18)
    occupied_discomfort_multiplier  = 20.0
    off_hours_energy_multiplier     = 5.0
    occupied_comfort_multiplier     = 2.0
    unoccupied_comfort_multiplier   = 0.3
    energy_cost_weight              = 0.20
    grid_energy_weight              = 0.2
    battery_cycle_weight            = 0.04
    battery_loss_weight             = 0.005
    simultaneous_battery_weight     = 0.005
    lambda_grid                     = 0.0001
    lambda_battery                  = 0.0001
    grid_energy_variables           = [v for v in candidate_grid_energy_vars if v in observation_variables]
    battery_charge_variables        = [v for v in candidate_battery_charge_vars if v in observation_variables]
    battery_discharge_variables     = [v for v in candidate_battery_discharge_vars if v in observation_variables]
    battery_loss_variables          = [v for v in candidate_battery_loss_vars if v in observation_variables]

    # Aquestes banderes fan que la funció sigui llarga, però mantenen la UI en una sola
    # passada: només es pinten els camps que realment necessita la reward seleccionada.
    occupied_reward_selected      = reward_name == "OccupiedHoursDiscomfortReward"
    battery_reward_selected       = reward_name in BATTERY_REWARDS
    new_battery_cost_selected     = reward_name == "MultizoneEnergyCostBatteryHVACReward"
    energy_weight_default         = 0.2 if (occupied_reward_selected or battery_reward_selected) else 0.5
    lambda_energy_default         = 0.001 if occupied_reward_selected else 0.0001
    temperature_weight_default    = 0.40 if new_battery_cost_selected else (0.55 if battery_reward_selected else 0.4)
    sanitize_multiselect_state("grid_energy_variables", observation_variables, grid_energy_variables)
    sanitize_multiselect_state("battery_charge_variables", observation_variables, battery_charge_variables)
    sanitize_multiselect_state("battery_discharge_variables", observation_variables, battery_discharge_variables)
    sanitize_multiselect_state("battery_loss_variables", observation_variables, battery_loss_variables)

    # Inputs pesos reward base
    _p1, _p2, _p3 = st.columns(3)
    with _p1:
        # Input pes energia
        energy_weight = st.number_input(
            "energy_weight",
            0.0,
            1.0,
            energy_weight_default,
            format="%.2f",
            key=training_form_key("energy_weight"),
        )
    with _p2:
        # Input lambda energia
        lambda_energy = st.number_input(
            "lambda_energy",
            0.0,
            10.0,
            lambda_energy_default,
            format="%.5f",
            key=training_form_key("lambda_energy"),
        )
    with _p3:
        # Input lambda temperatura
        lambda_temperature = st.number_input(
            "lambda_temperature",
            0.0,
            10.0,
            1.0,
            format="%.2f",
            key=training_form_key("lambda_temperature"),
        )

    if reward_name in COST_REWARDS:
        # Inputs reward cost
        _c1, _c2 = st.columns(2)
        with _c1:
            # Input pes temperatura
            temperature_weight = st.number_input(
                "temperature_weight",
                0.0,
                1.0,
                0.4,
                format="%.2f",
                key=training_form_key("temperature_weight"),
            )
        with _c2:
            # Input lambda cost energia
            lambda_energy_cost = st.number_input(
                "lambda_energy_cost",
                0.0,
                10.0,
                0.0001,
                format="%.5f",
                key=training_form_key("lambda_energy_cost"),
            )

    if reward_name in BATTERY_REWARDS:
        # En bateria és fàcil confondre potència de xarxa, càrrega i descàrrega. Per això
        # deixem els multiselect visibles i amb candidats ja filtrats per l'entorn actiu.
        # Inputs pesos bateria
        _b1, _b2, _b3 = st.columns(3)
        with _b1:
            # Input pes temperatura bateria
            temperature_weight = st.number_input(
                "temperature_weight",
                0.0,
                1.0,
                temperature_weight_default,
                format="%.2f",
                key=training_form_key("temperature_weight"),
            )
        with _b2:
            # Input pes xarxa
            grid_energy_weight = st.number_input(
                "grid_energy_weight",
                0.0,
                1.0,
                0.2,
                format="%.2f",
                key=training_form_key("grid_energy_weight"),
            )
        with _b3:
            # Input pes cicle bateria
            battery_cycle_weight = st.number_input(
                "battery_cycle_weight",
                0.0,
                1.0,
                0.04,
                format="%.3f",
                key=training_form_key("battery_cycle_weight"),
            )

        # Inputs penalitzacions bateria
        _b4, _b5, _b6 = st.columns(3)
        with _b4:
            # Input perdues bateria
            battery_loss_weight = st.number_input(
                "battery_loss_weight",
                0.0,
                1.0,
                0.005,
                format="%.3f",
                key=training_form_key("battery_loss_weight"),
            )
        with _b5:
            # Input simultaneitat bateria
            simultaneous_battery_weight = st.number_input(
                "simultaneous_battery_weight",
                0.0,
                1.0,
                0.005,
                format="%.3f",
                key=training_form_key("simultaneous_battery_weight"),
            )
        with _b6:
            # Input lambda xarxa
            lambda_grid = st.number_input(
                "lambda_grid",
                0.0,
                10.0,
                0.0001,
                format="%.5f",
                key=training_form_key("lambda_grid"),
            )

        # Input lambda bateria
        lambda_battery = st.number_input(
            "lambda_battery",
            0.0,
            10.0,
            0.0001,
            format="%.5f",
            key=training_form_key("lambda_battery"),
        )
        # Selector variables xarxa
        grid_energy_variables = st.multiselect(
            "Variables xarxa",
            observation_variables,
            default=grid_energy_variables,
            key=training_form_key("grid_energy_variables"),
        )
        # Selector variables carrega bateria
        battery_charge_variables = st.multiselect(
            "Variables carrega bateria",
            observation_variables,
            default=battery_charge_variables,
            key=training_form_key("battery_charge_variables"),
        )
        # Selector variables battery discharge
        battery_discharge_variables = st.multiselect(
            "Variables descarrega bateria",
            observation_variables,
            default=battery_discharge_variables,
            key=training_form_key("battery_discharge_variables"),
        )
        # Selector variables perdues bateria
        battery_loss_variables = st.multiselect(
            "Variables perdues bateria",
            observation_variables,
            default=battery_loss_variables,
            key=training_form_key("battery_loss_variables"),
        )

    if new_battery_cost_selected:
        # Aquesta reward barreja confort, cost econòmic i ocupació; separar el bloc evita
        # que aquests multiplicadors es vegin com a paràmetres genèrics de totes les rewards.
        # Seccio cost i ocupacio
        st.markdown("**Cost energetic i hores ocupades**")
        # Inputs cost i ocupacio
        _nc1, _nc2, _nc3 = st.columns(3)
        with _nc1:
            # Input pes cost energia
            energy_cost_weight = st.number_input(
                "energy_cost_weight", 0.0, 1.0, 0.20, format="%.2f",
                help="Pes del terme de cost economic (grid_kW * EUR/kWh).",
                key=training_form_key("energy_cost_weight"),
            )
        with _nc2:
            # Input escala cost energia
            lambda_energy_cost = st.number_input(
                "lambda_energy_cost", 0.0, 10.0, 1.0, format="%.4f",
                help="Escala del terme de cost economic.",
                key=training_form_key("lambda_energy_cost"),
            )
        with _nc3:
            # Slider hores ocupades
            occupied_hours = st.slider(
                "occupied_hours",
                0,
                23,
                (8, 18),
                key=training_form_key("occupied_hours"),
            )

        # Inputs multiplicadors confort
        _nm1, _nm2 = st.columns(2)
        with _nm1:
            # Input confort ocupat
            occupied_comfort_multiplier = st.number_input(
                "occupied_comfort_multiplier", 0.0, 20.0, 2.0, step=0.5, format="%.1f",
                help="Multiplicador del terme de confort durant hores ocupades.",
                key=training_form_key("occupied_comfort_multiplier"),
            )
        with _nm2:
            # Input confort no ocupat
            unoccupied_comfort_multiplier = st.number_input(
                "unoccupied_comfort_multiplier", 0.0, 5.0, 0.3, step=0.1, format="%.1f",
                help="Multiplicador del terme de confort fora d'hores ocupades.",
                key=training_form_key("unoccupied_comfort_multiplier"),
            )

    if reward_name in MULTIZONE_REWARDS:
        # Input llindar confort
        comfort_threshold = st.number_input(
            "comfort_threshold (C)",
            0.0,
            5.0,
            0.5,
            step=0.1,
            format="%.1f",
            key=training_form_key("comfort_threshold"),
        )

    if reward_name in HOURLY_REWARDS:
        # Slider hores confort
        range_comfort_hours = st.slider(
            "range_comfort_hours",
            0,
            23,
            (9, 19),
            key=training_form_key("range_comfort_hours"),
        )

    if reward_name == "OccupiedHoursDiscomfortReward":
        # Inputs reward ocupacio
        _o1, _o2, _o3 = st.columns(3)
        with _o1:
            # Slider hores ocupades
            occupied_hours = st.slider(
                "occupied_hours",
                0,
                23,
                (8, 18),
                key=training_form_key("occupied_hours"),
            )
        with _o2:
            # Input penalitzacio ocupada
            occupied_discomfort_multiplier = st.number_input(
                "occupied_discomfort_multiplier",
                min_value=1.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
                key=training_form_key("occupied_discomfort_multiplier"),
            )
        with _o3:
            # Input energia fora hores
            off_hours_energy_multiplier = st.number_input(
                "off_hours_energy_multiplier",
                min_value=1.0,
                max_value=100.0,
                value=5.0,
                step=0.5,
                key=training_form_key("off_hours_energy_multiplier"),
            )

    st.divider()
    _MONTHS = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Des"]
    # Les rewards de confort separen hivern i estiu; deixem la frontera editable perquè
    # el mateix edifici pot treballar amb climes molt diferents.
    # Slider rang confort hivern
    range_winter = st.slider(
        "range_comfort_winter",
        0.0,
        50.0,
        (20.0, 23.5),
        step=0.5,
        key=training_form_key("range_winter"),
    )
    # Slider rang confort estiu
    range_summer = st.slider(
        "range_comfort_summer",
        0.0,
        50.0,
        (23.0, 26.0),
        step=0.5,
        key=training_form_key("range_summer"),
    )

    st.divider()
    # Selectors mesos estiu
    _mc1, _mc2 = st.columns(2)
    with _mc1:
        month_options = list(range(1, 13))
        # Selector mes inici estiu
        summer_start_m = st.selectbox(
            "Inici estiu (mes)",
            month_options,
            format_func=lambda x: _MONTHS[x - 1],
            **selectbox_state_kwargs("summer_start_m", month_options, fallback=6),
        )
    with _mc2:
        # Selector mes final estiu
        summer_final_m = st.selectbox(
            "Final estiu (mes)",
            month_options,
            format_func=lambda x: _MONTHS[x - 1],
            **selectbox_state_kwargs("summer_final_m", month_options, fallback=9),
        )
    # Inputs dies estiu
    _dc1, _dc2 = st.columns(2)
    with _dc1:
        # Input dia inici estiu
        summer_start_d = st.number_input(
            "Dia inici",
            1,
            31,
            1,
            key=training_form_key("summer_start_d"),
        )
    with _dc2:
        # Input dia final estiu
        summer_final_d = st.number_input(
            "Dia final",
            1,
            31,
            30,
            key=training_form_key("summer_final_d"),
        )

    return {
        "energy_weight":                    energy_weight,
        "lambda_energy":                    lambda_energy,
        "lambda_temperature":               lambda_temperature,
        "temperature_weight":               temperature_weight,
        "lambda_energy_cost":               lambda_energy_cost,
        "comfort_threshold":                comfort_threshold,
        "range_comfort_hours":              range_comfort_hours,
        "occupied_hours":                   occupied_hours,
        "occupied_discomfort_multiplier":   occupied_discomfort_multiplier,
        "off_hours_energy_multiplier":      off_hours_energy_multiplier,
        "occupied_comfort_multiplier":      occupied_comfort_multiplier,
        "unoccupied_comfort_multiplier":    unoccupied_comfort_multiplier,
        "energy_cost_weight":               energy_cost_weight,
        "grid_energy_weight":               grid_energy_weight,
        "battery_cycle_weight":             battery_cycle_weight,
        "battery_loss_weight":              battery_loss_weight,
        "simultaneous_battery_weight":      simultaneous_battery_weight,
        "lambda_grid":                      lambda_grid,
        "lambda_battery":                   lambda_battery,
        "grid_energy_variables":            grid_energy_variables,
        "battery_charge_variables":         battery_charge_variables,
        "battery_discharge_variables":      battery_discharge_variables,
        "battery_loss_variables":           battery_loss_variables,
        "range_winter":                     range_winter,
        "range_summer":                     range_summer,
        "summer_start_m":                   summer_start_m,
        "summer_start_d":                   summer_start_d,
        "summer_final_m":                   summer_final_m,
        "summer_final_d":                   summer_final_d,
    }
