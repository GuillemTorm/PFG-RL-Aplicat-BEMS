"""Xifres de mapes de calor per als resums del panell global i de zona."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.grafics.column_utils import _ensure_air_temperature
from backend.grafics.comfort import _comfort_bounds_from_reward_kwargs
from backend.grafics.time_utils import _ensure_datetime_index, filter_by_season

def make_heatmap(pivot_df: pd.DataFrame, label: str) -> go.Figure:
    """Mapa de calor genèric donat un dataframe pivotat (Mes × Hora)."""
    if pivot_df is None or pivot_df.empty:
        return go.Figure()

    fig = px.imshow(
        pivot_df, origin="lower",
        labels={"x": "Hora", "y": "Mes", "color": label},
        aspect="auto", color_continuous_scale="Viridis",
    )
    fig.update_layout(title=f"Mapa de calor {label} (Mes x Hora)")
    return fig


def make_violation_heatmap_percent(
    obs: pd.DataFrame,
    season: str = "All",
    comfort_config=None,
) -> go.Figure:
    """
    Mapa de calor (Mes x Hora) amb el % de timesteps en violacio de confort.
      - Usa temp_violation si existeix; si no, reward_kwargs o defaults.
      - Respecta filtre d'estació via months (Winter/Spring/Summer/Autumn/All).
      - Escala de color 0..100 (%).
    """
    # Preparem les columnes temporals que necessita el mapa.
    base = _ensure_datetime_index(obs).copy()
    if "month" not in base.columns:
        base["month"] = base.index.month
    if "hour" not in base.columns:
        base["hour"] = base.index.hour
    base = _ensure_air_temperature(base)

    # Marquem cada timestep com a violació o confort.
    if "temp_violation" in base.columns:
        viol_raw = pd.to_numeric(base["temp_violation"], errors="coerce")
        viol = (viol_raw > 0.0).where(viol_raw.notna(), np.nan)
    else:
        lower, upper = _comfort_bounds_from_reward_kwargs(base, comfort_config)
        tin = pd.to_numeric(base["air_temperature"], errors="coerce")
        viol = ((tin < lower) | (tin > upper)).where(tin.notna(), np.nan)

    base = base.assign(__viol__=viol.astype(float))

    # El filtre d'estació s'aplica abans de construir la matriu hora-mes.
    base = filter_by_season(base, season)

    # Cada cel·la guarda el percentatge de violació per mes i hora.
    if base.empty:
        pivot = pd.DataFrame(index=range(1, 13), columns=range(24), dtype=float)
    else:
        pivot = (
            base.groupby(["month", "hour"])["__viol__"]
                .mean()
                .mul(100.0)
                .unstack()                             # columnes = hora
                .reindex(index=range(1, 13))          # mesos 1..12
                .reindex(columns=range(24))           # hores 0..23
        )

    # Pintem el percentatge resultant en una escala comuna de 0 a 100.
    fig = px.imshow(
        pivot,
        origin="lower",
        labels={"x": "Hora", "y": "Mes", "color": "Violacions (%)"},
        aspect="auto",
        color_continuous_scale="Viridis",
    )
    fig.update_coloraxes(cmin=0, cmax=100)
    fig.update_layout(title=f"Violacions de confort (%) – Hora × Mes ({season})")
    return fig

# Heatmaps de temperatura per zona.


def _pretty_zone_temperature_name(name: str) -> str:
    """Retorna una etiqueta de zona llegible des d'un nom de columna de temperatura de l'aire."""
    base = name[: -len("_air_temperature")]
    base = base.replace("_", " ").strip()
    return base if base else name


def _zone_temperature_columns(obs: pd.DataFrame) -> list[tuple[str, str]]:
    """
    Detecta columnes de temperatura d'interior per zona.
    Retorna llista [(nom_zona,"colname"), …].
    Si no hi ha columnes *_air_temperature però existeix 'air_temperature',
    retorna [('All','air_temperature')].
    """
    cols = [c for c in obs.columns if c.endswith("_air_temperature")]
    if cols:
        return [(_pretty_zone_temperature_name(c), c) for c in cols]
    if "air_temperature" in obs.columns:
        return [("All", "air_temperature")]
    return []


def _ensure_month_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Assegura columnes 'month' i 'hour' a partir de l'índex temporal."""
    base = _ensure_datetime_index(df).copy()
    if "month" not in base.columns:
        base["month"] = base.index.month
    if "hour" not in base.columns:
        base["hour"] = base.index.hour
    return base


def _zone_heatmap_layout(nrows: int, ncols: int) -> tuple[float, float, int]:
    """Retorna l'espai i l'alçada segurs de la subparcel·la per a edificis grans de diverses zones."""
    horizontal_spacing = 0.06 if ncols > 1 else 0.0
    if nrows <= 1:
        vertical_spacing = 0.0
    else:
        vertical_spacing = min(0.045, 0.9 / max(nrows - 1, 1))
    height = max(560, 250 * nrows + 120)
    return horizontal_spacing, vertical_spacing, height


def compute_zone_temperature_pivots(
    obs: pd.DataFrame, season: str = "All", agg: str = "mean"
) -> dict[str, pd.DataFrame]:
    """
    Construeix, per a cada zona, un pivot Mes×Hora amb la temperatura d'interior.
    - Respecta el filtre d'estació (via filter_by_season).
    - Reindexa sempre a mesos 1..12 i hores 0..23 (cel·les inexistents -> NaN).
    - 'agg' pot ser 'mean' o 'median'.

    Retorna: {nom_zona: DataFrame (index=1..12 mesos, columns=0..23 hores)}
    """
    base = _ensure_month_hour(_ensure_air_temperature(obs))
    base = filter_by_season(base, season)

    zones = _zone_temperature_columns(base)
    if not zones:
        return {}

    aggfun = "median" if str(agg).lower() == "median" else "mean"

    pivots: dict[str, pd.DataFrame] = {}
    for zname, col in zones:
        s = pd.to_numeric(base[col], errors="coerce")
        g = (
            s.groupby([base["month"].astype(int), base["hour"].astype(int)])
             .agg(aggfun)
             .unstack()  # columnes = hour
        )
        # assegura el grid complet Mes(1..12) × Hora(0..23)
        g = g.reindex(index=range(1, 13)).reindex(columns=range(24))
        pivots[zname] = g

    return pivots


def make_zone_temperature_heatmaps(
    obs: pd.DataFrame,
    season: str = "All",
    agg: str = "mean",
    max_cols: int = 3,
) -> go.Figure:
    """Crea mapes de calor de temperatura interior mensuals per hores per a cada zona.

    La figura generada utilitza una escala de colors compartida entre zones, canònica
    eixos mes/hora, el filtre de temporada seleccionat i la mitjana o la mediana
    agregació. El creador de pivot omet les dades de zones buides o incompletes.

    Paràmetres:
        obs: DataFrame d'observació.
        season: filtre de temporada: ``All``, ``Winter``, ``Spring``, ``Summer`` o
            ``Autumn``.
        agg: mètode d'agregació, ja sigui ``mean`` o ``median``.
        max_cols: nombre màxim de columnes de subgràfic.

    Retorna:
        Una figura Plotly amb un mapa de calor per zona, o un únic mapa de calor quan el
        run només conté una zona.
    """
    pivots = compute_zone_temperature_pivots(obs, season=season, agg=agg)
    if not pivots:
        return go.Figure()

    # Escala comuna: min/max sobre totes les zones (ignorant NaN)
    all_vals = np.concatenate([p.values.flatten() for p in pivots.values()])
    finite_vals = all_vals[np.isfinite(all_vals)]
    if finite_vals.size:
        cmin = float(np.nanmin(finite_vals))
        cmax = float(np.nanmax(finite_vals))
    else:
        cmin, cmax = np.nan, np.nan
    if not np.isfinite(cmin) or not np.isfinite(cmax) or cmin == cmax:
        # reserva segura
        cmin, cmax = 15.0, 30.0

    znames = list(pivots.keys())
    n = len(znames)
    ncols = min(max_cols, n)
    nrows = (n + ncols - 1) // ncols
    horizontal_spacing, vertical_spacing, height = _zone_heatmap_layout(nrows, ncols)

    fig = make_subplots(
        rows=nrows,
        cols=ncols,
        subplot_titles=znames,
        horizontal_spacing=horizontal_spacing,
        vertical_spacing=vertical_spacing,
    )

    # Afegeix un heatmap per zona, compartint escala; una sola colorbar (últim subplot)
    for i, zname in enumerate(znames):
        r = i // ncols + 1
        c = i % ncols + 1
        pivot = pivots[zname]
        showscale = (i == n - 1)  # només a l'últim
        heat = go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),    # 0..23
            y=list(pivot.index),      # 1..12
            colorscale="Viridis",
            zmin=cmin,
            zmax=cmax,
            colorbar=dict(title="°C"),
            showscale=showscale,
        )
        fig.add_trace(heat, row=r, col=c)
        fig.update_xaxes(title_text="Hora", row=r, col=c, tickmode="linear", dtick=2)
        fig.update_yaxes(title_text="Mes",  row=r, col=c, autorange="reversed")  # 1..12 de dalt a baix

    fig.update_layout(
        title=f"Temperatura interior per zona – Mes × Hora ({season}, {agg})",
        margin=dict(l=60, r=20, t=60, b=40),
        height=height,
    )
    return fig
