"""Utilitats de representació de mapes compartides construïdes a pydeck i Streamlit."""

from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from page_styles.theme import build_pydeck_tooltip


def _chart_width(use_container_width: bool) -> str:
    """Tradueix el flag antic de Streamlit al valor de width actual."""
    return "stretch" if use_container_width else "content"


def render_location_map(
    latitude: float,
    longitude: float,
    *,
    zoom: float = 4.5,
    color: tuple[int, int, int, int] = (95, 84, 249, 220),
    radius: int = 22000,
    tooltip_html: str | None = None,
    use_container_width: bool = True,
) -> None:
    """Dibuixa un mapa de dispersió d'un sol punt centrat en les coordenades donades.

    tooltip_html accepta HTML preformatats (no calen referències de columna pydeck).
    """

    point_frame = pd.DataFrame([{"latitude": latitude, "longitude": longitude}])
    tooltip = build_pydeck_tooltip(tooltip_html, variant="location") if tooltip_html else None
    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=latitude,
                longitude=longitude,
                zoom=zoom,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=point_frame,
                    get_position="[longitude, latitude]",
                    get_fill_color=list(color),
                    get_radius=radius,
                    pickable=tooltip_html is not None,
                )
            ],
            tooltip=tooltip,
        ),
        width=_chart_width(use_container_width),
    )


def render_multipoint_map(
    data_frame: pd.DataFrame,
    *,
    center_latitude: float | None = None,
    center_longitude: float | None = None,
    zoom: float = 2,
    color: tuple[int, int, int, int] = (255, 0, 0, 200),
    radius: int = 55000,
    tooltip_html: str | None = None,
    use_container_width: bool = True,
) -> None:
    """Dibuixa un mapa de dispersió de diversos punts des d'un DataFrame amb latitud/longitud.

    La vista es centra a les coordenades mitjanes tret que center_latitude/center_longitude
    es proporcionen de manera explícita. tooltip_html admet marcadors de posició de nom de columna pydeck
    (e.g. '<b>{file_name}</b><br/>{ciutat}').
    """

    lat_center = center_latitude if center_latitude is not None else float(data_frame["latitude"].mean())
    lon_center = center_longitude if center_longitude is not None else float(data_frame["longitude"].mean())
    tooltip = build_pydeck_tooltip(tooltip_html, variant="multipoint") if tooltip_html else None
    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=lat_center,
                longitude=lon_center,
                zoom=zoom,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=data_frame,
                    get_position="[longitude, latitude]",
                    get_fill_color=list(color),
                    get_radius=radius,
                    pickable=tooltip_html is not None,
                )
            ],
            tooltip=tooltip,
        ),
        width=_chart_width(use_container_width),
    )
