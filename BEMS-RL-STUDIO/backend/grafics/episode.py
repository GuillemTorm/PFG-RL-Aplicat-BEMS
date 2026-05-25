"""Xifres del quadre de comandament a nivell d'episodi."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.grafics.style import STUDIO_CHART_COLORS, _apply_figure_theme

def _resolve_episode_mean_power(progress: pd.DataFrame) -> pd.Series | None:
    """Resol la potència mitjana de l'episodi."""
    mean_power = None
    if "mean_power_demand" in progress.columns:
        mean_power = pd.to_numeric(progress["mean_power_demand"], errors="coerce")

    if mean_power is None:
        mean_power = pd.Series(np.nan, index=progress.index, dtype=float)

    derived_mean = None
    if (
        "cumulative_power_demand" in progress.columns
        and "length(timesteps)" in progress.columns
    ):
        derived_mean = (
            pd.to_numeric(progress["cumulative_power_demand"], errors="coerce")
            / pd.to_numeric(progress["length(timesteps)"], errors="coerce").replace(0, np.nan)
        )

    if derived_mean is not None:
        replace_mask = mean_power.isna() | (
            (mean_power == 0) & derived_mean.notna() & (derived_mean != 0)
        )
        mean_power = mean_power.copy()
        mean_power.loc[replace_mask] = derived_mean.loc[replace_mask]

    if mean_power.isna().all():
        return None

    return mean_power

# Mètriques d'episodi.
def make_episode_metrics(progress: pd.DataFrame) -> go.Figure:
    """Mètriques d'episodi amb 3 subtrames:
      1) Recompensa
      2) Violació de la temperatura
      3) Demanda mitjana de potència
    """
    x = progress["episode_num"] if "episode_num" in progress.columns else (progress.index + 1)
    episode_vals = x.tolist()
    episode_ticks = [str(v) for v in episode_vals]

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=[
            "Reward per Episode",
            "Average Temperature Violation (°C)",
            "Mean Power Demand per Episode (W)",
        ],
    )

    if "mean_reward" in progress.columns:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=progress["mean_reward"],
                mode="lines+markers",
                name="Reward",
                line=dict(color=STUDIO_CHART_COLORS["reward"], width=3),
                marker=dict(color=STUDIO_CHART_COLORS["reward"], size=7),
            ),
            row=1,
            col=1,
        )

    if "mean_temperature_violation" in progress.columns:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=progress["mean_temperature_violation"],
                mode="lines+markers",
                name="Violation",
                line=dict(color=STUDIO_CHART_COLORS["violation"], width=3),
                marker=dict(color=STUDIO_CHART_COLORS["violation"], size=7),
            ),
            row=2, col=1,
        )

    power_series = _resolve_episode_mean_power(progress)
    if power_series is not None:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=power_series,
                mode="lines+markers",
                name="Mean Power",
                line=dict(color=STUDIO_CHART_COLORS["consumption"], width=3),
                marker=dict(color=STUDIO_CHART_COLORS["consumption"], size=7),
            ),
            row=3, col=1,
        )

    for r in range(1, 4):
        fig.update_xaxes(
            row=r, col=1,
            title_text="Episode",
            tickmode="array",
            tickvals=episode_vals,
            ticktext=episode_ticks,
        )

    fig.update_layout(height=850, title_text="Episode Metrics", showlegend=False)
    return _apply_figure_theme(fig)
