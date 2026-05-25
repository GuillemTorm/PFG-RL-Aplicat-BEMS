"""Estil Plotly compartit per a les figures del panell BEMS-RL Studio."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go


# Paleta i format comú de les figures.
STUDIO_CHART_COLORS = {
    "heating": "#c81e1e",
    "heating_ref": "#ef4444",
    "cooling": "#1d4ed8",
    "cooling_ref": "#38bdf8",
    "consumption": "#f59e0b",
    "consumption_muted": "#fbbf24",
    "consumption_edge": "#b45309",
    "violation": "#dc2626",
    "violation_muted": "#f87171",
    "violation_edge": "#991b1b",
    "indoor": "#0f766e",
    "outdoor": "#64748b",
    "comfort_ok": "#16a34a",
    "comfort_cold": "#2563eb",
    "comfort_hot": "#dc2626",
    "battery": "#7c3aed",
    "battery_charge": "#15803d",
    "battery_discharge": "#ea580c",
    "grid_purchase": "#ca8a04",
    "price": "#0891b2",
    "reward": "#6d28d9",
    "neutral": "#475569",
    "neutral_soft": "#cbd5e1",
    "grid": "#d7deeb",
    "paper": "#ffffff",
    "plot": "#f8fbff",
    "text": "#17233c",
}

STUDIO_HEATMAP_SCALES = {
    "consumption": "YlOrBr",
    "violation": "Reds",
    "temperature": "RdYlBu_r",
}


def pick_semantic_trace_color(
    trace_name: str | None,
    *,
    reference: bool = False,
    fallback: str | None = None,
) -> str:
    """Retorna un color semàntic segons el nom de la traça."""
    label = (trace_name or "").lower()

    # Les figures arriben de mòduls diferents i no sempre comparteixen palette. Fem servir
    # paraules del nom de la traça per mantenir colors coherents sense acoblar els gràfics.
    if "heating" in label or "htg" in label:
        return STUDIO_CHART_COLORS["heating_ref" if reference else "heating"]
    if "cooling" in label or "clg" in label:
        return STUDIO_CHART_COLORS["cooling_ref" if reference else "cooling"]
    if "viol" in label:
        return STUDIO_CHART_COLORS["violation_muted" if reference else "violation"]
    if "massa fred" in label or "cold" in label:
        return STUDIO_CHART_COLORS["comfort_cold"]
    if "massa calor" in label or "hot" in label:
        return STUDIO_CHART_COLORS["comfort_hot"]
    if "confort" in label or "comfort" in label:
        return STUDIO_CHART_COLORS["comfort_ok"]
    if "hvac" in label or "consum" in label or "demand rate" in label or "mean power" in label:
        return STUDIO_CHART_COLORS["consumption_muted" if reference else "consumption"]
    if "price" in label or "preu" in label or "eur/kwh" in label:
        return STUDIO_CHART_COLORS["price"]
    if "reward" in label:
        return STUDIO_CHART_COLORS["reward"]
    if "outdoor" in label:
        return STUDIO_CHART_COLORS["outdoor"]
    if "radiant operation" in label or "radiant availability" in label:
        return STUDIO_CHART_COLORS["battery"]
    if "radiant inlet" in label:
        return STUDIO_CHART_COLORS["price"]
    if "radiant outlet" in label or "radiant water" in label:
        return STUDIO_CHART_COLORS["battery_discharge"]
    if "discharge" in label:
        return STUDIO_CHART_COLORS["battery_discharge"]
    if "charge" in label:
        return STUDIO_CHART_COLORS["battery_charge"]
    if "battery" in label or "stored energy" in label or "soc" in label or "bateria" in label:
        return STUDIO_CHART_COLORS["battery_charge"]
    if "xarxa" in label or "compra" in label or "grid purchase" in label:
        return STUDIO_CHART_COLORS["grid_purchase"]
    if "indoor" in label:
        return STUDIO_CHART_COLORS["indoor"]

    return fallback or STUDIO_CHART_COLORS["neutral"]


def _alpha_color(hex_color: str, alpha: float = 0.30) -> str:
    """Converteix un color hex a rgba amb transparència."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def _apply_figure_theme(fig: go.Figure, *, heatmap: bool = False) -> go.Figure:
    """Aplica un estil més contrastat i homogeni a les figures."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=STUDIO_CHART_COLORS["paper"],
        plot_bgcolor=STUDIO_CHART_COLORS["plot"],
        font=dict(color=STUDIO_CHART_COLORS["text"], size=14),
        title=dict(
            x=0.02,
            xanchor="left",
            font=dict(size=20, color=STUDIO_CHART_COLORS["text"]),
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=STUDIO_CHART_COLORS["grid"],
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font_color=STUDIO_CHART_COLORS["text"],
        ),
        margin=dict(l=60, r=28, t=72, b=56),
    )
    fig.update_xaxes(
        showgrid=not heatmap,
        gridcolor=STUDIO_CHART_COLORS["grid"],
        linecolor=STUDIO_CHART_COLORS["grid"],
        ticks="outside",
        zeroline=False,
    )
    fig.update_yaxes(
        showgrid=not heatmap,
        gridcolor=STUDIO_CHART_COLORS["grid"],
        linecolor=STUDIO_CHART_COLORS["grid"],
        ticks="outside",
        zeroline=False,
    )
    return fig


def style_figure_semantics(fig: go.Figure) -> go.Figure:
    """Recolora traces segons la seva semàntica i aplica el tema comú."""
    heatmap_like = False

    for trace in getattr(fig, "data", []):
        trace_type = getattr(trace, "type", "")
        name = getattr(trace, "name", None) or ""
        base_name = name.replace(" (ref)", "")
        is_reference = "(ref)" in name.lower()
        if getattr(trace, "legendgroup", None) == "agent_actions":
            continue
        if getattr(trace, "meta", None) == "keep_color":
            continue
        # Algunes traces ja porten colors especials (per exemple heatmaps o accions).
        # Les altres es recoloren aquí perquè el dashboard sembli una sola peça.
        color = pick_semantic_trace_color(base_name, reference=is_reference)

        if trace_type in ("scatter", "scattergl"):
            line = getattr(trace, "line", None)
            width = max(float(getattr(line, "width", 0) or 0), 2.8 if is_reference else 2.6)
            marker = getattr(trace, "marker", None)
            marker_color = getattr(marker, "color", None)
            trace.line = dict(
                color=color,
                width=width,
            )
            if "markers" in str(getattr(trace, "mode", "")):
                trace.marker = dict(
                    color=marker_color if isinstance(marker_color, (list, tuple, np.ndarray)) and not is_reference else color,
                    size=max(int(getattr(marker, "size", 0) or 0), 6),
                )
            if is_reference:
                trace.opacity = max(float(getattr(trace, "opacity", 1.0) or 1.0), 0.92)

        elif trace_type == "bar":
            marker = getattr(trace, "marker", None)
            marker_color = getattr(marker, "color", None)
            edge_color = (
                STUDIO_CHART_COLORS["violation_edge"]
                if color in (STUDIO_CHART_COLORS["violation"], STUDIO_CHART_COLORS["violation_muted"])
                else STUDIO_CHART_COLORS["consumption_edge"]
            )
            trace.marker = dict(
                color=marker_color if isinstance(marker_color, (list, tuple, np.ndarray)) and not is_reference else color,
                line=dict(color=edge_color, width=0.8),
            )
            if is_reference:
                trace.opacity = min(float(getattr(trace, "opacity", 1.0) or 1.0), 0.58)

        elif trace_type == "heatmap":
            heatmap_like = True
            title_text = str(getattr(getattr(fig.layout, "title", None), "text", "") or "").lower()
            if "viol" in title_text:
                trace.colorscale = STUDIO_HEATMAP_SCALES["violation"]
            elif "consum" in title_text or "hvac" in title_text:
                trace.colorscale = STUDIO_HEATMAP_SCALES["consumption"]
            else:
                trace.colorscale = STUDIO_HEATMAP_SCALES["temperature"]

    return _apply_figure_theme(fig, heatmap=heatmap_like)
