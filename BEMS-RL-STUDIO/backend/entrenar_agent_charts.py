"""Gràfics d'entrenament en directe per a la pàgina d'entrenament de l'agent."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from backend.entrenar_agent_session import TRAINING_WORKSPACE_KEY
from backend.grafics.data_loader import _repair_power_metrics_from_progress
from backend.grafics.episode import make_episode_metrics


def _get_workspace_from_runtime(runtime: dict) -> str | None:
    """Extreu el workspace_path del VecEnv actiu.

    Intenta tres estratègies per ordre de preferència:
    1. ``VecEnv.get_attr`` (travessa la cadena de wrappers Gymnasium).
    2. ``model.env.get_attr`` (accés directe a l'entorn intern del model).
    3. Exploració de CWD per trobar directoris que coincideixin amb ``{env_id}-res*`` (retrocés).

    Retorna:
        Camí absolut a l'espai de treball com a cadena, o ``None`` si no
        l'estratègia té èxit.
    """
    # Estratègia 1: via VecEnv.get_attr
    try:
        paths = runtime["vec"].get_attr("workspace_path")
        if paths and paths[0]:
            return str(paths[0])
    except Exception:
        pass

    # Estratègia 2: via model.env
    try:
        paths = runtime["model"].env.get_attr("workspace_path")
        if paths and paths[0]:
            return str(paths[0])
    except Exception:
        pass

    # Estratègia 3: directori més recent a CWD que coincideix amb env_id
    try:
        env_id = runtime["config"]["env_id"]
        cwd = Path(os.getcwd())
        candidates = sorted(
            [d for d in cwd.iterdir() if d.is_dir() and d.name.startswith(f"{env_id}-res")],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return str(candidates[0])
    except Exception:
        pass

    return None


def render_live_training_charts() -> None:
    """Mostra els gràfics d'evolució per episodi llegint ``progress.csv``.

    Llegeix ``progress.csv`` de l'espai de treball actiu i en mostra tres
    subgràfics (recompensa, infracció de temperatura i demanda d'energia). Si no
    l'episodi encara s'ha completat, es mostra un missatge d'espera.
    """
    workspace_str = st.session_state.get(TRAINING_WORKSPACE_KEY)

    if not workspace_str:
        st.caption("Esperant la inicialitzacio del workspace...")
        return

    progress_path = Path(workspace_str) / "progress.csv"
    if not progress_path.exists():
        st.markdown(
            """
            <div class="training-live-wait">
                Els grafics apareixeran en completar-se el primer episodi.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    try:
        progress = pd.read_csv(progress_path)
    except Exception:
        return

    if progress.empty:
        return

    try:
        progress = _repair_power_metrics_from_progress(progress)
    except Exception:
        pass

    n_episodes = len(progress)
    st.markdown(
        f"""
        <div class="training-live-status">
            <span class="training-live-badge">
                <span class="training-live-dot"></span>
                EN VIU
            </span>
            <span class="training-live-count">
                {n_episodes} episodi{"s" if n_episodes != 1 else ""} completat{"s" if n_episodes != 1 else ""}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = make_episode_metrics(progress)

    # Paleta de colors per a cada subgràfic
    _TRACE_COLORS = [
        "#6366f1",  # recompensa -> indigo
        "#f59e0b",  # violation  -> amber
        "#10b981",  # power      -> green
    ]
    _FILL_COLORS = [
        "rgba(99,102,241,0.08)",
        "rgba(245,158,11,0.08)",
        "rgba(16,185,129,0.08)",
    ]

    # Estil cada traça: color, amplada, marcadors i àrea de farciment
    for i, trace in enumerate(fig.data):
        trace.update(
            line=dict(color=_TRACE_COLORS[i], width=2.5),
            marker=dict(
                color="#ffffff",
                size=8,
                line=dict(color=_TRACE_COLORS[i], width=2),
            ),
            fill="tozeroy",
            fillcolor=_FILL_COLORS[i],
        )

    # Distribució manual de dominis amb prou espai per als títols de subgràfics
    row_domains = [
        [0.69, 1.00],
        [0.34, 0.60],
        [0.00, 0.25],
    ]

    # Propietats d'eix comuns
    _axis_style = dict(
        showgrid=True,
        gridcolor="rgba(0,0,0,0.05)",
        gridwidth=1,
        zeroline=False,
        linecolor="rgba(0,0,0,0.12)",
        linewidth=1,
        tickfont=dict(size=11, color="#64748b"),
        title_font=dict(size=11, color="#94a3b8"),
    )

    fig.update_layout(
        title_text="",
        height=680,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,255,0.6)",
        margin=dict(t=30, b=20, l=50, r=10),
        font=dict(size=12, color="#334155"),
        yaxis=dict(domain=row_domains[0], **_axis_style),
        yaxis2=dict(domain=row_domains[1], **_axis_style),
        yaxis3=dict(domain=row_domains[2], **_axis_style),
        xaxis=dict(title_text="", **_axis_style),
        xaxis2=dict(title_text="", **_axis_style),
        xaxis3=dict(title_text="Episodi", **_axis_style),
    )

    # Encoixinat de l'eix X perquè els marcadors dels extrems no es retallin
    x_pad = 0.5
    x_min = float(progress["episode_num"].min()) if "episode_num" in progress.columns else 1.0
    x_max = float(progress["episode_num"].max()) if "episode_num" in progress.columns else float(len(progress))
    fig.update_xaxes(range=[x_min - x_pad, x_max + x_pad])

    # Reposicionar i estilitzar les anotacions del títol del subgràfic
    for i, annotation in enumerate(fig.layout.annotations):
        annotation.update(
            y=row_domains[i][1],
            yanchor="bottom",
            font=dict(size=12, color="#475569", family="sans-serif"),
        )

    st.plotly_chart(fig, width="stretch", key="live_training_chart")
