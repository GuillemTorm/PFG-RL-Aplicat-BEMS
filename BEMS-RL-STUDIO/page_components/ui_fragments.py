"""Fragments UI compartits per pàgines Streamlit de BEMS-RL Studio."""

from __future__ import annotations

from collections.abc import Callable
from html import escape
import time
from typing import Any, Iterable

import streamlit as st


def render_hero(class_name: str, kicker: str, title: str, copy_text: str | Iterable[str]) -> None:
    """Crea una capçalera hero amb les classes CSS de la pàgina."""
    copy_html = _copy_html(copy_text)
    # Hero pagina
    st.markdown(
        f"""
        <section class="{escape(class_name)}">
            <div class="hero-kicker">{escape(kicker)}</div>
            <h1 class="hero-title">{escape(title)}</h1>
            <div class="hero-copy">{copy_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title: str, class_name: str = "page-section-title", level: int = 2) -> None:
    """Mostra un títol de secció escapant el text."""
    tag = f"h{level}"
    # Titol seccio
    st.markdown(f'<{tag} class="{escape(class_name)}">{escape(title)}</{tag}>', unsafe_allow_html=True)


def render_section_card(title: str, description: str, *, title_class: str, card_class: str) -> None:
    """Combina títol de secció i una targeta descriptiva simple."""
    render_section_title(title, title_class)
    # Targeta seccio
    st.markdown(
        f"""
        <section class="{escape(card_class)} section-card-spaced">
            <div class="section-copy">{escape(description)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_card_header(
    target: Any,
    *,
    anchor_class: str,
    kicker: str,
    title: str,
    description: str = "",
    kicker_class: str = "upload-card-kicker",
    title_class: str = "upload-card-title",
    description_class: str = "upload-card-copy",
) -> None:
    """Pinta la capçalera HTML comuna d'una targeta Streamlit."""
    description_html = (
        f'<div class="{escape(description_class)}">{escape(description)}</div>'
        if description
        else ""
    )
    # Capcalera targeta
    target.markdown(
        f"""
        <div class="{escape(anchor_class)}"></div>
        <div class="{escape(kicker_class)}">{escape(kicker)}</div>
        <div class="{escape(title_class)}">{escape(title)}</div>
        {description_html}
        """,
        unsafe_allow_html=True,
    )


def render_info_panel(class_name: str, title: str, kicker: str, copy_text: str) -> None:
    """Mostra un panell informatiu compacte."""
    # Panell informatiu
    st.markdown(
        f"""
        <section class="{escape(class_name)}">
            <div class="panel-kicker">{escape(kicker)}</div>
            <div class="panel-title">{escape(title)}</div>
            <div class="panel-copy">{escape(copy_text)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card_grid(
    metrics: Iterable[tuple[Any, Any]],
    *,
    shell_class: str,
    card_class: str,
    label_class: str,
    value_class: str,
    formatter: Callable[[Any], str] | None = None,
    label_formatter: Callable[[Any], str] | None = None,
) -> None:
    """Mostra una graella HTML de targetes KPI compactes."""
    metric_items = list(metrics)
    if not metric_items:
        return

    format_value = formatter or str
    format_label = label_formatter or str
    cards = "".join(
        (
            f'<section class="{escape(card_class)}">'
            f'<div class="{escape(label_class)}">{escape(format_label(label))}</div>'
            f'<div class="{escape(value_class)}">{escape(format_value(value))}</div>'
            "</section>"
        )
        for label, value in metric_items
    )
    # Graella targetes KPI
    st.markdown(
        f'<section class="{escape(shell_class)}">{cards}</section>',
        unsafe_allow_html=True,
    )


def render_detail_list_card(
    *,
    title: str,
    rows: Iterable[tuple[Any, Any]],
    card_class: str,
    title_class: str,
    list_class: str,
    row_class: str,
    label_class: str,
    value_class: str,
    formatter: Callable[[Any], str] | None = None,
    label_formatter: Callable[[Any], str] | None = None,
) -> None:
    """Mostra una targeta de detalls amb parelles etiqueta/valor."""
    format_value = formatter or str
    format_label = label_formatter or str
    row_html = "".join(
        f"""
        <div class="{escape(row_class)}">
            <div class="{escape(label_class)}">{escape(format_label(label))}</div>
            <div class="{escape(value_class)}">{escape(format_value(value))}</div>
        </div>
        """
        for label, value in rows
    )
    # Targeta llista detall
    st.markdown(
        f"""
        <section class="{escape(card_class)}">
            <div class="{escape(title_class)}">{escape(title)}</div>
            <div class="{escape(list_class)}">{row_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_copy_block(class_name: str, text: str, *, formatter: Callable[[str], str] | None = None) -> None:
    """Mostra un bloc de text HTML escapant-ne el contingut."""
    display_text = formatter(text) if formatter is not None else text
    # Text informatiu
    st.markdown(
        f"<div class='{escape(class_name)}'>{escape(display_text)}</div>",
        unsafe_allow_html=True,
    )


def render_metric_row(
    items: Iterable[dict[str, Any]],
    *,
    columns: int = 3,
) -> None:
    """Mostra mètriques Streamlit en columnes amb fallback informatiu."""
    item_list = list(items)
    if not item_list:
        return
    cols = st.columns(columns)
    for index, item in enumerate(item_list):
        with cols[index % columns]:
            empty_message = item.get("empty_message")
            if item.get("empty") and empty_message:
                # Avís mètrica buida
                st.info(str(empty_message))
                continue
            # Metrica fila
            st.metric(
                str(item.get("label", "")),
                str(item.get("value", "")),
                delta=item.get("delta"),
                delta_color=item.get("delta_color", "normal"),
            )


def build_metric_item(
    current: dict,
    previous: dict | None,
    field: str | None,
    *,
    label: str,
    value_format: Callable[[Any], str],
    delta_format: Callable[[Any], str],
    empty_message: str,
    delta_color: str = "off",
) -> dict[str, Any]:
    """Prepara una mètrica declarativa a partir d'un camp opcional."""
    if not field or field not in current:
        return {"empty": True, "empty_message": empty_message}
    value = current[field]
    old_value = previous[field] if previous and field in previous else value
    return {
        "label": label,
        "value": value_format(value),
        "delta": delta_format(value - old_value),
        "delta_color": delta_color,
    }


def render_kicker_section(class_name: str, title: str, kicker: str, description: str) -> None:
    """Munta una secció amb títol, kicker i text descriptiu."""
    render_section_title(title)
    # Bloc seccio amb kicker
    st.markdown(
        f"""
        <section class="{escape(class_name)}">
            <div class="section-kicker">{escape(kicker)}</div>
            <div class="section-copy">{escape(description)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_runtime_progress(
    runtime: dict[str, Any],
    *,
    progress_label: str = "Progrés",
    freeze_from_result: bool = False,
) -> None:
    """Mostra barra i mètriques de progrés per a un runtime en segon pla."""
    steps_target = max(int(runtime.get("steps_target") or 1), 1)
    latest_step = min(int(runtime.get("latest_step") or 0), steps_target)
    progress_value = min(latest_step / steps_target, 1.0)
    elapsed_seconds = _elapsed_seconds(runtime, freeze_from_result=freeze_from_result)

    # Barra progres runtime
    st.progress(progress_value)
    # Metriques runtime
    metric_cols = st.columns(3)
    metric_cols[0].metric("Passos", f"{latest_step}/{steps_target}")
    metric_cols[1].metric(progress_label, f"{progress_value * 100:.0f}%")
    metric_cols[2].metric("Temps", f"{elapsed_seconds // 60}m {elapsed_seconds % 60:02d}s")

    status_text = str(runtime.get("status") or "").strip()
    if status_text:
        # Text estat runtime
        st.caption(status_text)


def _copy_html(copy_text: str | Iterable[str]) -> str:
    """Escapa text o paràgrafs per inserir-los dins d'un bloc HTML segur."""
    if isinstance(copy_text, str):
        return escape(copy_text)
    return "<br><br>".join(escape(str(part)) for part in copy_text)


def _elapsed_seconds(runtime: dict[str, Any], *, freeze_from_result: bool) -> int:
    """Calcula segons transcorreguts a partir de l'estat runtime o del resultat final."""
    result = runtime.get("result")
    if freeze_from_result and result is not None:
        return int(float(getattr(result, "elapsed_seconds", 0.0)))
    if freeze_from_result and runtime.get("frozen_elapsed_seconds") is not None:
        return int(float(runtime.get("frozen_elapsed_seconds") or 0.0))
    started_at = runtime.get("started_at")
    if started_at:
        return max(0, int(time.time() - float(started_at)))
    return 0
