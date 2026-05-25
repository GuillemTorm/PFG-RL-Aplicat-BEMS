"""Gestió de fitxers per a actius, models i dades meteorològiques de Studio.

Aquest mòdul fa una còpia de seguretat de la pàgina del navegador de fitxers. Formata metadades del sistema de fitxers,
resumeix els fitxers meteorològics EPW, descobreix artefactes de model entrenats i s'aplica
operacions de còpia/supressió limitades utilitzades per la UI de Streamlit.
"""

import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_PATH = Path.cwd().resolve()
DATA_BTC_PATH = ROOT_PATH / 'sinergym' / 'data' / 'buildings'
DATA_WEA_PATH = ROOT_PATH / 'sinergym' / 'data' / 'weather'
MODEL_FILE_EXTENSIONS = (".zip", ".pkl")
MODEL_ROOT_DIRECTORY_NAMES = {"models", "trainings"}


@dataclass(frozen=True)
class ExplorerItem:
    """Fila del navegador de fitxers serialitzable que es mostra a la pàgina de gestió d'actius."""
    name: str
    path: str
    size: str
    mtime: str
    is_dir: bool


def get_size_format(b, factor=1024, suffix="B"):
    """Retorna una mida compacta i llegible, com ara ``12.40KB``."""
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


@st.cache_data(show_spinner=False)
def parse_epw_overview(epw_file):
    """Llegeix les metadades d'ubicació i la temperatura mitjana del bulb sec d'un fitxer EPW."""
    with open(epw_file, 'r', encoding='utf-8', errors='ignore') as handle:
        lines = handle.readlines()

    loc = lines[0].strip().split(',')
    location = {
        'city': loc[1] if len(loc) > 1 else '-',
        'state': loc[2] if len(loc) > 2 else '-',
        'country': loc[3] if len(loc) > 3 else '-',
        'latitude': float(loc[6]) if len(loc) > 6 else 0.0,
        'longitude': float(loc[7]) if len(loc) > 7 else 0.0,
    }

    df = pd.read_csv(epw_file, skiprows=8, header=None)
    avg_temp = float(df.iloc[:, 6].mean())
    climate_zone = 'hot' if avg_temp > 22 else 'cold' if avg_temp < 12 else 'cool'
    return location, avg_temp, climate_zone


@st.cache_data(show_spinner=False)
def load_weather_map_rows(root_path_str):
    """Retorna les files de fitxers meteorològics preparats per al mapa descobertes a continuació ``root_path_str``."""
    root_path = Path(root_path_str)
    rows = []
    color_map = {
        'hot': [230, 120, 40],
        'cool': [70, 130, 180],
        'cold': [80, 190, 220],
    }

    for epw_path in sorted(root_path.rglob('*.epw')):
        try:
            location, avg_temp, climate_zone = parse_epw_overview(str(epw_path))
        except Exception:
            continue

        color = color_map.get(climate_zone, [120, 120, 120])
        rows.append({
            'file_name': epw_path.name,
            'relative_path': str(epw_path.relative_to(root_path)),
            'city': location['city'],
            'country': location['country'],
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'climate': climate_zone,
            'avg_temp': round(avg_temp, 2),
            'color_r': color[0],
            'color_g': color[1],
            'color_b': color[2],
        })

    return pd.DataFrame(rows)


def delete_item(path_str):
    """Suprimeix l'element."""
    path = Path(path_str)
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            if path.exists():
                path.unlink()
    except Exception as exc:
        return str(exc)
    return None


def list_explorer_items(current_path, root_path, filter_func=None):
    """Llista els elements de l'explorador."""
    try:
        with os.scandir(current_path) as iterator:
            entries = list(iterator)
    except Exception as exc:
        return (), str(exc)

    folders = []
    files = []

    for entry in entries:
        if filter_func:
            if not filter_func(entry.name, entry.is_dir(), current_path == root_path):
                continue

        try:
            stat = entry.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            size_str = "DIR" if entry.is_dir() else get_size_format(stat.st_size)

            item = ExplorerItem(
                name=entry.name,
                path=entry.path,
                size=size_str,
                mtime=mtime,
                is_dir=entry.is_dir(),
            )

            if entry.is_dir():
                folders.append(item)
            else:
                files.append(item)
        except Exception:
            continue

    folders.sort(key=lambda item: item.name.lower())
    files.sort(key=lambda item: item.name.lower())
    return tuple(folders + files), None


def filter_trainings(name, is_dir, is_root):
    """Entrenaments de filtre."""
    if is_root:
        return is_dir and (
            name == "trainings"
            or name.startswith("Eplus-")
            or name.startswith("ppo_")
        )
    return True


def filter_models(name, is_dir, is_root):
    """Models de filtre."""
    name_lower = name.lower()
    if not is_dir:
        return name_lower.endswith(MODEL_FILE_EXTENSIONS)
    if is_root:
        return (
            name_lower in MODEL_ROOT_DIRECTORY_NAMES
            or name_lower.startswith("eplus-")
            or name_lower.startswith("ppo_")
            or name_lower.startswith("training-")
        )
    return True


def filter_weather(name, is_dir, is_root):
    """Filtre el temps."""
    if not is_dir:
        return name.endswith(".epw")
    return True


def filter_envs(name, is_dir, is_root):
    """Filtre envs."""
    if not is_dir:
        return name.endswith(".epJSON") or name.endswith(".idf")
    return True
