"""Backend de metadades de l'entorn: carrega actius, PV, emmagatzematge i dades per pintar la UI."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from backend.viewer_3d_backend import build_surface_records


@st.cache_data(show_spinner=False)
def load_epjson(path: str) -> dict:
    """Llegeix i retorna un fitxer epJSON del disc (emmagatzemat a la memòria cau)."""
    with open(path, 'r') as fh:
        return json.load(fh)


def _safe_float(value: Any) -> Optional[float]:
    """Retorna float(valor) o None si la conversió falla."""
    try:
        return None if value is None else float(value)
    except Exception:
        return None


def _getf(data: dict, *keys: str) -> Optional[float]:
    """Retorna el primer valor numèric trobat entre les claus donades, o None."""
    for key in keys:
        value = data.get(key)
        try:
            if value is None:
                continue
            return float(value)
        except Exception:
            continue
    return None


def _derive_kibam_metrics(
    obj: dict,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Deriva (energy_kwh, p_charge_kw, p_discharge_kw) d'un objecte de bateria KiBaM.

    Processa ElectricLoadCenter:Emmagatzematge:camps de bateria per estimar el nivell de paquet
    capacitat energètica i límits de potència de càrrega/descàrrega.
    """
    cap_ah = _getf(obj, "maximum_module_capacity")
    voltage_full = _getf(obj, "fully_charged_module_open_circuit_voltage")
    voltage_cut = _getf(obj, "module_cut_off_voltage")
    c_rate = _getf(obj, "module_charge_rate_limit")
    current_discharge = _getf(obj, "maximum_module_discharging_current")

    n_series = int(_getf(obj, "number_of_battery_modules_in_series") or 1)
    n_parallel = int(_getf(obj, "number_of_battery_modules_in_parallel") or 1)

    if cap_ah is None:
        return None, None, None

    if voltage_full and voltage_cut:
        voltage_nominal = 0.5 * (voltage_full + voltage_cut)
    elif voltage_full:
        voltage_nominal = 0.95 * voltage_full
    elif voltage_cut:
        voltage_nominal = 1.10 * voltage_cut
    else:
        voltage_nominal = 12.0

    voltage_pack = voltage_nominal * n_series
    cap_ah_pack = cap_ah * n_parallel
    energy_kwh = (cap_ah_pack * voltage_pack) / 1000.0

    p_charge_kw = None
    if c_rate is not None:
        p_charge_kw = (c_rate * cap_ah * n_parallel * voltage_pack) / 1000.0

    p_discharge_kw = None
    if current_discharge is not None:
        p_discharge_kw = (current_discharge * n_parallel * voltage_pack) / 1000.0

    return energy_kwh, p_charge_kw, p_discharge_kw


def parse_pv_and_storage(epjson: dict) -> Dict[str, Any]:
    """Analitza generadors de PV i objectes d'emmagatzematge de la bateria des d'un epJSON dict.

    Admet generador: fotovoltaic, generador: PVWatts,
    ElectricLoadCenter:Emmagatzematge:Simple, :Bateria i :LiIonNMCBattery.
    Retorna un dict amb les claus 'pv' i 'emmagatzematge', cadascuna una llista de dicts normalitzats.
    """
    output: Dict[str, List[dict]] = {'pv': [], 'storage': []}

    # EnergyPlus té dues famílies habituals de generadors solars. Les normalitzem a la
    # mateixa estructura perquè el visor no hagi de conèixer cada tipus.
    for key in ("Generator:Photovoltaic", "Generator:PVWatts"):
        for name, obj in epjson.get(key, {}).items():
            output['pv'].append({
                'name': name,
                'surface_name': obj.get("surface_name"),
                'type': key,
                'capacity_dc': obj.get("dc_system_capacity"),
                'num_series': obj.get("number_of_modules_in_series"),
                'num_strings': obj.get("number_of_series_strings"),
                'performance_obj': obj.get("module_performance_name"),
                'array_geometry_type': obj.get("array_geometry_type"),
            })

    for name, obj in epjson.get("ElectricLoadCenter:Storage:Simple", {}).items():
        # En Storage:Simple l'eficiència de volta completa es pot estimar multiplicant
        # càrrega i descàrrega, si totes dues existeixen.
        eff_charge = _safe_float(obj.get("nominal_energètic_efficiency_for_charging"))
        eff_discharge = _safe_float(obj.get("nominal_discharging_energètic_efficiency"))
        eff_roundtrip = None
        if eff_charge is not None and eff_discharge is not None:
            try:
                eff_roundtrip = float(eff_charge) * float(eff_discharge)
            except Exception:
                pass
        output['storage'].append({
            'name': name,
            'type': "ElectricLoadCenter:Storage:Simple",
            'energy_kwh': _safe_float(obj.get("maximum_storage_capacity")),
            'p_charge_kw': _safe_float(obj.get("maximum_power_for_charging")),
            'p_discharge_kw': _safe_float(obj.get("maximum_power_for_discharging")),
            'eff_roundtrip': eff_roundtrip,
            'zone_name': obj.get("zone_name"),
        })

    for name, obj in epjson.get("ElectricLoadCenter:Storage:Battery", {}).items():
        energy_kwh, p_charge_kw, p_discharge_kw = _derive_kibam_metrics(obj)
        output['storage'].append({
            'name': name,
            'type': "ElectricLoadCenter:Storage:Battery",
            'energy_kwh': None if energy_kwh is None else round(energy_kwh, 2),
            'p_charge_kw': None if p_charge_kw is None else round(p_charge_kw, 2),
            'p_discharge_kw': None if p_discharge_kw is None else round(p_discharge_kw, 2),
            'eff_roundtrip': None,
            'zone_name': obj.get("zone_name"),
        })

    for name, obj in epjson.get("ElectricLoadCenter:Storage:LiIonNMCBattery", {}).items():
        output['storage'].append({
            'name': name,
            'type': "ElectricLoadCenter:Storage:LiIonNMCBattery",
            'energy_kwh': None,
            'p_charge_kw': None,
            'p_discharge_kw': None,
            'eff_roundtrip': None,
            'zone_name': obj.get("zone_name"),
        })

    return output


@st.cache_data(show_spinner=False)
def load_environment_assets(epjson_path: str) -> Dict[str, Any]:
    """Carrega i prepareu tots els actius principals per a un entorn Sinergym (emmagatzemats a la memòria cau).

    Llegeix el fitxer epJSON, crea registres de superfície enriquits i analitza
    PV/objectes d'emmagatzematge. Retorna un dict unificat preparat per a UI.
    """
    data = load_epjson(epjson_path)
    enriched = build_surface_records(data)
    energy = parse_pv_and_storage(data)
    return {
        'records': enriched['records'],
        'zones': enriched['zones'],
        'types': enriched['types'],
        'center': enriched['center'],
        'z_clip_range': enriched['z_clip_range'],
        'name_index': enriched['name_index'],
        'pv': energy['pv'],
        'storage': energy['storage'],
    }


def summarize_pv(
    records: List[dict],
    name_index: Dict[str, int],
    pv_list: List[dict],
) -> Dict[str, Any]:
    """Calcula mètriques agregades dels panells PV associats a superfícies de l'edifici.

    Recompte de retorns, llista de noms de superfície actives, àrea total, inclinació mitjana i
    azimut mitjà. L'àrea i els angles són None quan no es troben superfícies coincidents.
    """
    used_surfaces = []
    total_area = 0.0
    tilts: List[float] = []
    azimuths: List[float] = []
    for pv in pv_list:
        surface_name = pv.get('surface_name')
        if surface_name in name_index:
            record = records[name_index[surface_name]]
            used_surfaces.append(surface_name)
            total_area += record['area']
            tilts.append(record['tilt'])
            azimuths.append(record['azimuth'])
    return {
        'count': len(pv_list),
        'surfaces_with_pv': sorted(set(used_surfaces)),
        'area_m2': total_area,
        'avg_tilt': sum(tilts) / len(tilts) if tilts else None,
        'avg_azimuth': sum(azimuths) / len(azimuths) if azimuths else None,
    }


@st.cache_data(show_spinner=False)
def parse_epw_metadata_and_temperature(epw_file: str):
    """Llegeix les metadades d'ubicació i la temperatura anual mitjana d'un fitxer EPW (emmagatzemat a la memòria cau).

    Retorna (location_dict, avg_temp_celsius, climate_zone_label).
    """
    with open(epw_file, 'r') as fh:
        lines = fh.readlines()

    loc = lines[0].strip().split(',')
    loc_data = {
        'city': loc[1], 'state': loc[2], 'country': loc[3],
        'latitude': float(loc[6]), 'longitude': float(loc[7]),
        'timezone': float(loc[8]), 'elevation': float(loc[9]),
    }
    df = pd.read_csv(epw_file, skiprows=8, header=None)
    avg_temp = df.iloc[:, 6].mean()
    climate_zone = "hot" if avg_temp > 22 else "cold" if avg_temp < 12 else "cool"
    return loc_data, avg_temp, climate_zone


def _format_ui_value(value: Any) -> str:
    """Formata qualsevol valor per mostrar-lo, retornant '-' per als valors buits/None."""
    if value is None:
        return '-'
    if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
        return '-'
    return str(value)


def _tuple_mapping_to_df(mapping: Dict[str, Any], columns: List[str]) -> pd.DataFrame:
    """Converteix un dict d'entrades amb valors de tupla a una etiqueta DataFrame."""
    rows = []
    for alias, values in (mapping or {}).items():
        flat = list(values) if isinstance(values, (list, tuple)) else [values]
        padded = flat + [''] * max(0, len(columns) - len(flat))
        row: Dict[str, Any] = {'Alias': alias}
        for index, column in enumerate(columns):
            row[column] = _format_ui_value(padded[index])
        rows.append(row)
    return pd.DataFrame(rows)


def _sequence_to_df(values: List[Any], column_name: str) -> pd.DataFrame:
    """Converteix una llista plana de valors en una sola columna DataFrame."""
    return pd.DataFrame([{column_name: _format_ui_value(v)} for v in (values or [])])


def _reward_summary_frames(
    reward_kwargs: Dict[str, Any],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Divideix els kwargs de recompensa en escalar i agrupa (list-valued) DataFrames."""
    scalar_rows: List[dict] = []
    grouped_rows: List[dict] = []
    for key, value in (reward_kwargs or {}).items():
        if isinstance(value, (list, tuple)):
            grouped_rows.append({'Parametre': key, 'Valor': ', '.join(map(_format_ui_value, value))})
        else:
            scalar_rows.append({'Parametre': key, 'Valor': _format_ui_value(value)})
    return pd.DataFrame(scalar_rows), pd.DataFrame(grouped_rows)
