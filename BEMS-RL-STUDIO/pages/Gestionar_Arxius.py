from __future__ import annotations

import time
from datetime import datetime
from html import escape
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st
from page_components.ui_fragments import render_hero
from page_styles.gestionar_arxius import inject_file_manager_styles
from sidebar_nav import configure_studio_page

from backend.mapa_backend import render_multipoint_map
from backend.gestionar_arxius_backend import (
    DATA_BTC_PATH,
    DATA_WEA_PATH,
    ROOT_PATH,
    delete_item,
    filter_envs,
    filter_models,
    filter_trainings,
    filter_weather,
    list_explorer_items,
    load_weather_map_rows,
)


PAGE_TITLE = "Gestor de Fitxers Avançat"
PAGE_LAYOUT = "wide"
INTRODUCTION_TEXT = "Gestiona els fitxers del projecte organitzats per categories."
EXPLORER_COLUMN_LAYOUT = [0.8, 1.4, 5.9, 1.4, 2.5]
TRAINING_ARTIFACTS_PATH = ROOT_PATH / "trainings"


def render_weather_view_selector() -> str:
    """Mostra el selector de vista del bloc de climes sense ràdios."""

    options = ["Explorador", "Mapa"]
    current_value = st.session_state.get("weather_submenu", "Explorador")

    # Selector vista climes
    selected_value = st.segmented_control(
        "Vista de climes",
        options,
        default=current_value,
        key="weather_submenu_segmented",
    )
    if selected_value:
        st.session_state["weather_submenu"] = selected_value
    return st.session_state.get("weather_submenu", current_value)


def build_selection_archive(selected_paths: list[str]) -> bytes:
    """Construeix un zip en memòria amb els elements seleccionats."""

    archive_buffer = BytesIO()
    normalized_paths = sorted({str(Path(path_str)) for path_str in selected_paths})

    with ZipFile(archive_buffer, "w", ZIP_DEFLATED) as archive:
        for path_str in normalized_paths:
            path = Path(path_str)
            if not path.exists():
                continue

            if path.is_dir():
                archive.writestr(f"{path.name}/", "")
                for nested_path in sorted(path.rglob("*")):
                    archive_name = nested_path.relative_to(path.parent).as_posix()
                    if nested_path.is_dir():
                        try:
                            next(nested_path.iterdir())
                        except StopIteration:
                            archive.writestr(f"{archive_name}/", "")
                        except OSError:
                            pass
                        continue

                    archive.write(nested_path, archive_name)
                continue

            archive.write(path, path.name)

    archive_buffer.seek(0)
    return archive_buffer.getvalue()


def build_download_name(key_prefix: str) -> str:
    """Construeix un nom de fitxer estable per a la descàrrega."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{key_prefix}_seleccio_{timestamp}.zip"


def clear_prepared_archive_if_stale(key_prefix: str, selection_signature: tuple[str, ...]) -> None:
    """Neteja l'arxiu preparat si la selecció actual ja no coincideix."""

    archive_key = f"{key_prefix}_download_archive"
    archive_name_key = f"{key_prefix}_download_name"
    archive_signature_key = f"{key_prefix}_download_signature"

    prepared_signature = st.session_state.get(archive_signature_key)
    if prepared_signature == selection_signature:
        return

    st.session_state.pop(archive_key, None)
    st.session_state.pop(archive_name_key, None)
    st.session_state.pop(archive_signature_key, None)


def delete_items(items: list[str]) -> None:
    """Esborra els elements seleccionats mostrant progrés."""

    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, path_str in enumerate(items):
        path = Path(path_str)
        status_text.text(f"Eliminant: {path.name}...")
        error_message = delete_item(path_str)
        if error_message:
            # Error eliminacio fitxer
            st.error(f"Error eliminant {path.name}: {error_message}")
        progress_bar.progress((index + 1) / len(items))

    status_text.text("Fet.")
    time.sleep(1)
    st.rerun()


def handle_uploaded_files(current_path: Path, uploaded_files) -> None:
    """Desa els fitxers pujats a la ruta actual de l'explorador."""

    for uploaded_file in uploaded_files:
        destination = current_path / Path(uploaded_file.name).name
        try:
            with open(destination, "wb") as destination_handle:
                destination_handle.write(uploaded_file.getbuffer())
            st.toast(f"Fitxer carregat correctament: {destination.name}", icon="✅")
        except Exception as exc:
            # Error upload fitxer
            st.error(f"Error carregant {uploaded_file.name}: {exc}")

    time.sleep(1)
    st.rerun()


def navigate_file_explorer_up(path_key: str, current_path: Path, root_path: Path) -> None:
    """Mou l'explorador de fitxers un directori cap amunt sense sortir de l'arrel."""
    parent = current_path.parent
    if parent == root_path or root_path in parent.parents:
        st.session_state[path_key] = str(parent)
    else:
        st.session_state[path_key] = str(root_path)


def navigate_file_explorer_into(path_key: str, folder_path: str) -> None:
    """Mou l'explorador de fitxers cap a una carpeta filla."""
    st.session_state[path_key] = str(Path(folder_path).resolve())


def render_explorer(
    key_prefix: str,
    root_path: Path,
    filter_func=None,
    allow_nav_up: bool = True,
    allow_upload: bool = False,
    upload_label: str | None = None,
    upload_types: list[str] | None = None,
    upload_help: str | None = None,
) -> None:
    """Mostra l'explorador de fitxers per a cada categoria."""

    root_path = root_path.resolve()
    path_key = f"{key_prefix}_path"
    if path_key not in st.session_state:
        st.session_state[path_key] = str(root_path)

    current_path = Path(st.session_state[path_key]).resolve()

    # El path surt de session_state, així que el validem sempre contra l'arrel de la categoria.
    # D'aquesta manera un valor vell o manipulat no pot fer navegar fora de la carpeta prevista.
    try:
        current_path.relative_to(root_path)
    except ValueError:
        st.session_state[path_key] = str(root_path)
        current_path = root_path

    # Navegacio explorador
    nav_columns = st.columns([1.1, 5.4], gap="small")
    with nav_columns[0]:
        disabled = (current_path == root_path) or not allow_nav_up
        # Botó upload carpeta
        if st.button("Amunt", key=f"{key_prefix}_up", disabled=disabled, type="primary", width="stretch"):
            navigate_file_explorer_up(path_key, current_path, root_path)
            # Canviar carpeta modifica l'estat; forcem rerun perquè la llista es repinti de seguida.
            st.rerun()

    try:
        relative_path = current_path.relative_to(root_path)
        display_path = f"/{relative_path.as_posix()}" if str(relative_path) != "." else "/"
    except ValueError:
        display_path = str(current_path)

    with nav_columns[1]:
        # Ruta carpeta actual
        st.markdown(f"<div class='file-explorer-path'>{escape(display_path)}</div>", unsafe_allow_html=True)

    if allow_upload:
        # Upload fitxers
        uploaded_files = st.file_uploader(
            upload_label or f"Pujar fitxers a {display_path}",
            accept_multiple_files=True,
            type=upload_types,
            help=upload_help,
            key=f"{key_prefix}_upload",
        )
        if uploaded_files:
            # Les pujades es desen a la carpeta actual, no a l'arrel global del projecte.
            handle_uploaded_files(current_path, uploaded_files)

    all_items, error_message = list_explorer_items(current_path, root_path, filter_func)
    if error_message:
        # Error lectura directori
        st.error(f"Error llegint el directori: {error_message}")
        all_items = ()

    if not all_items:
        # Avís carpeta buida
        st.info("Aquesta carpeta és buida.")
        return

    # Capçalera taula fitxers
    header_columns = st.columns(EXPLORER_COLUMN_LAYOUT, gap="small")
    headers = ("Sel.", "Tipus", "Nom", "Mida", "Data")
    for column, header in zip(header_columns, headers):
        column.markdown(f"<div class='file-explorer-header'>{header}</div>", unsafe_allow_html=True)

    # Separador taula fitxers
    st.markdown("---")

    selected_items: list[str] = []
    for index, item in enumerate(all_items):
        # Fila fitxer explorador
        row_columns = st.columns(EXPLORER_COLUMN_LAYOUT, gap="small")
        checkbox_key = f"{key_prefix}_chk_{item.path}"
        # Checkbox seleccionar fitxer
        is_selected = row_columns[0].checkbox(
            f"Seleccionar {item.name}",
            key=checkbox_key,
            label_visibility="collapsed",
        )
        if is_selected:
            selected_items.append(item.path)

        item_type = "Carpeta" if item.is_dir else "Fitxer"
        item_size = "—" if item.is_dir else item.size
        item_icon = "📁" if item.is_dir else "📄"

        # Cel·la tipus fitxer
        row_columns[1].markdown(f"<div class='file-explorer-muted'>{item_type}</div>", unsafe_allow_html=True)
        name_columns = row_columns[2].columns([0.6, 7.8], gap="small")
        # Cel·la icona fitxer
        name_columns[0].markdown(
            f"<div class='file-explorer-icon-cell'><span class='file-explorer-icon'>{item_icon}</span></div>",
            unsafe_allow_html=True,
        )

        if item.is_dir:
            # Botó obrir carpeta
            if name_columns[1].button(
                item.name,
                key=f"{key_prefix}_btn_{item.path}",
                type="secondary",
                width="stretch",
            ):
                navigate_file_explorer_into(path_key, item.path)
                st.rerun()
        else:
            safe_name = escape(item.name)
            # Cel·la nom fitxer
            name_columns[1].markdown(
                (
                    "<div class='file-explorer-cell file-explorer-name'>"
                    f"<span class='file-explorer-label'>{safe_name}</span>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        # Cel·la mida fitxer
        row_columns[3].markdown(f"<div class='file-explorer-muted'>{escape(item_size)}</div>", unsafe_allow_html=True)
        # Cel·la data fitxer
        row_columns[4].markdown(f"<div class='file-explorer-muted'>{escape(item.mtime)}</div>", unsafe_allow_html=True)
        if index < len(all_items) - 1:
            # Separador fila fitxer
            st.markdown("<div class='file-explorer-row-spacer'></div>", unsafe_allow_html=True)

    # Separador seleccio fitxers
    st.markdown("---")

    if not selected_items:
        return

    # Controls seleccio fitxers
    selection_columns = st.columns([2.4, 1.5, 1.2], gap="small")
    selection_columns[0].markdown(
        f"<div class='file-explorer-selection'>{len(selected_items)} elements seleccionats.</div>",
        unsafe_allow_html=True,
    )
    selection_signature = tuple(sorted({str(Path(path_str)) for path_str in selected_items}))
    # Si canvia la selecció, descartem el zip preparat anterior. Evita baixar un arxiu
    # que ja no correspon al que es veu marcat a pantalla.
    clear_prepared_archive_if_stale(key_prefix, selection_signature)

    archive_key = f"{key_prefix}_download_archive"
    archive_name_key = f"{key_prefix}_download_name"
    archive_signature_key = f"{key_prefix}_download_signature"
    archive_ready = (
        st.session_state.get(archive_signature_key) == selection_signature
        and st.session_state.get(archive_key) is not None
    )

    with selection_columns[1]:
        download_slot = st.empty()
        # Botó preparar download
        if not archive_ready and download_slot.button(
            "Descarregar selecció",
            key=f"{key_prefix}_prepare_download",
            type="primary",
            width="stretch",
        ):
            try:
                with st.spinner("Preparant la descàrrega..."):
                    st.session_state[archive_key] = build_selection_archive(selected_items)
                st.session_state[archive_name_key] = build_download_name(key_prefix)
                st.session_state[archive_signature_key] = selection_signature
                archive_ready = True
            except Exception as exc:
                # Error preparar download
                st.error(f"No s'ha pogut preparar la descàrrega: {exc}")
                archive_ready = False

        if archive_ready:
            # Botó download zip
            download_slot.download_button(
                "Descarregar selecció",
                data=st.session_state[archive_key],
                file_name=st.session_state[archive_name_key],
                mime="application/zip",
                key=f"{key_prefix}_download",
                type="primary",
                width="stretch",
            )

    with selection_columns[2]:
        # Botó esborrar seleccio
        if st.button("Esborrar", key=f"{key_prefix}_del", type="primary", width="stretch"):
            delete_items(selected_items)


configure_studio_page(PAGE_TITLE, layout=PAGE_LAYOUT)
inject_file_manager_styles()

render_hero("files-hero", "Exploració i manteniment", PAGE_TITLE, INTRODUCTION_TEXT)

# Separador gestor fitxers
st.markdown("<div class='studio-spacer-045'></div>", unsafe_allow_html=True)
# Pestanyes gestor fitxers
tab_train, tab_scripts, tab_models, tab_weather, tab_envs = st.tabs(
    ["Entrenaments", "Scripts", "Models", "Climes", "Entorns"]
)

with tab_train:
    render_explorer("train", ROOT_PATH, filter_trainings)

with tab_scripts:
    if TRAINING_ARTIFACTS_PATH.exists():
        render_explorer("training_scripts", TRAINING_ARTIFACTS_PATH)
    else:
        # Avís carpeta trainings absent
        st.info("Encara no hi ha cap carpeta `trainings/`. Es creara quan es guardi el primer entrenament.")

with tab_models:
    models_root = TRAINING_ARTIFACTS_PATH if TRAINING_ARTIFACTS_PATH.exists() else ROOT_PATH
    render_explorer("models", models_root, filter_models)

with tab_weather:
    weather_root = DATA_WEA_PATH if DATA_WEA_PATH.exists() else ROOT_PATH
    # Selector vista climes
    weather_view = render_weather_view_selector()

    if weather_view == "Explorador":
        render_explorer(
            "weather",
            weather_root,
            filter_weather,
            allow_upload=True,
            upload_label="Pujar fitxers climàtics (.epw)",
            upload_types=["epw"],
            upload_help="Afegeix nous fitxers meteorològics EPW al catàleg de climes.",
        )
    else:
        # Text mapa climes
        st.caption("Mapa amb tots els fitxers `.epw` disponibles.")
        with st.spinner("Generant mapa de climes..."):
            weather_df = load_weather_map_rows(str(weather_root))

        if weather_df.empty:
            # Avís mapa climes buit
            st.warning("No s'han trobat fitxers `.epw` per mostrar al mapa.")
        else:
            render_multipoint_map(
                weather_df,
                zoom=2,
                color=(255, 0, 0, 200),
                radius=55000,
                tooltip_html=(
                    "<b>{file_name}</b><br/>{city}, {country}"
                    "<br/>Clima: {climate}<br/>Avg tmp: {avg_temp} C"
                ),
            )
            # Taula climes mapa
            st.dataframe(
                weather_df[["file_name", "city", "country", "climate", "avg_temp"]],
                hide_index=True,
                width="stretch",
            )

with tab_envs:
    env_root = DATA_BTC_PATH if DATA_BTC_PATH.exists() else ROOT_PATH
    render_explorer("envs", env_root, filter_envs)
