"""Controls d'hiperparàmetres de l'agent per a la pàgina d'entrenament."""

from __future__ import annotations

import streamlit as st
from backend.entrenar_agent_session import training_form_key


def render_agent_params_section(algo_name: str) -> dict:
    """Mostra els widgets d'hiperparàmetres de l'agent i retorna els seus valors.

    Cobreix la taxa d'aprenentatge, n_steps, els passos de temps totals i tots els SB3 avançats
    paràmetres (batch_size, gamma, n_epochs, gae_lambda, clip_range,
    ent_coef, vf_coef, max_grad_norm).

    Retorna:
        Un dict amb tots els valors dels paràmetres d'agent recollits dels widgets.
    """
    # Els tres primers camps són els que més es toquen en proves ràpides; els avançats
    # queden agrupats perquè la pantalla no sembli una paret de paràmetres.
    # Inputs principals agent
    agent_col1, agent_col2, agent_col3 = st.columns(3)
    with agent_col1:
        # Input learning rate
        learning_rate = st.number_input(
            "learning_rate",
            1e-5,
            1e-2,
            3e-4,
            format="%.5f",
            key=training_form_key("learning_rate"),
        )
    with agent_col2:
        # Input passos rollout
        n_steps = st.number_input(
            "n_steps (PPO/A2C)",
            256,
            4096,
            2048,
            step=256,
            key=training_form_key("n_steps"),
        )
    with agent_col3:
        # Input timesteps totals
        timesteps_per_year = st.number_input(
            "total_timesteps",
            35040,
            10_000_000,
            35040,
            step=35040,
            key=training_form_key("timesteps_per_year"),
        )

    with st.container():
        # Seccio parametres avançats
        st.markdown("**Parametres SB3 avancats**")
        # Aquests valors tenen defaults raonables per PPO/A2C. Si un algorisme no els usa,
        # assemble_training_payload els filtra abans de crear el model.
        # Inputs SB3 avançats
        sb3_col1, sb3_col2, sb3_col3, sb3_col4 = st.columns(4)
        with sb3_col1:
            # Input batch size
            batch_size = st.number_input(
                "batch_size",
                8,
                8192,
                256,
                step=8,
                key=training_form_key("batch_size"),
            )
            # Input gamma
            gamma = st.number_input(
                "gamma",
                0.0,
                0.9999,
                0.995,
                step=0.0005,
                format="%.4f",
                key=training_form_key("gamma"),
            )
        with sb3_col2:
            # Input epochs PPO
            n_epochs = st.number_input(
                "n_epochs",
                1,
                50,
                10,
                step=1,
                key=training_form_key("n_epochs"),
            )
            # Input GAE lambda
            gae_lambda = st.number_input(
                "gae_lambda",
                0.0,
                1.0,
                0.95,
                step=0.01,
                format="%.2f",
                key=training_form_key("gae_lambda"),
            )
        with sb3_col3:
            # Input clip range
            clip_range = st.number_input(
                "clip_range",
                0.01,
                1.0,
                0.2,
                step=0.01,
                format="%.2f",
                key=training_form_key("clip_range"),
            )
            # Input entropy coef
            ent_coef = st.number_input(
                "ent_coef",
                0.0,
                1.0,
                0.005,
                step=0.001,
                format="%.4f",
                key=training_form_key("ent_coef"),
            )
        with sb3_col4:
            # Input value loss coef
            vf_coef = st.number_input(
                "vf_coef",
                0.0,
                2.0,
                0.5,
                step=0.05,
                format="%.2f",
                key=training_form_key("vf_coef"),
            )
            # Input gradient clipping
            max_grad_norm = st.number_input(
                "max_grad_norm",
                0.0,
                10.0,
                0.5,
                step=0.1,
                format="%.1f",
                key=training_form_key("max_grad_norm"),
            )

    return {
        "learning_rate":    learning_rate,
        "n_steps":          n_steps,
        "timesteps_per_year": timesteps_per_year,
        "batch_size":       batch_size,
        "gamma":            gamma,
        "n_epochs":         n_epochs,
        "gae_lambda":       gae_lambda,
        "clip_range":       clip_range,
        "ent_coef":         ent_coef,
        "vf_coef":          vf_coef,
        "max_grad_norm":    max_grad_norm,
    }


# ── Pàgina principal ──────────────────────────────── ────────────────────────────────
