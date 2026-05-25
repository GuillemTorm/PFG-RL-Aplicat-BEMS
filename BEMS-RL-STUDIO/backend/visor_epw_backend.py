"""Utilitats de preparació de dades per al visor climàtic EPW.

El backend del visor EPW localitza fitxers meteorològics d'EnergyPlus,
normalitza els camps EPW en brut, afegeix atributs de calendari i produeix
taules de resum per a la UI de Streamlit. Les sortides es mantenen com a
DataFrames perquè els gràfics i les descàrregues es puguin construir sense
tornar a llegir el fitxer meteorològic.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


ROOT_PATH = Path.cwd().resolve()
WEATHERS_DIR = ROOT_PATH / "sinergym" / "data" / "weather"
WEATHER_ROOT = WEATHERS_DIR if WEATHERS_DIR.exists() else ROOT_PATH
DEG = "\N{DEGREE SIGN}"
DEG_C = f"{DEG}C"
SQUARE_2 = "\N{SUPERSCRIPT TWO}"
WH_PER_M2 = f"Wh/m{SQUARE_2}"
KWH_PER_M2 = f"kWh/m{SQUARE_2}"
MID_DOT = "\N{MIDDLE DOT}"

MONTH_LABELS = {
    1: "Gen",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Oct",
    11: "Nov",
    12: "Des",
}
MONTH_ORDER = list(MONTH_LABELS.values())
WIND_DIRECTION_LABELS = (
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
)
TIME_AGGREGATION_RULES = {
    "Hora": None,
    "Dia": "D",
    "Setmana": "W-MON",
    "Mes": "M",
}
CATALOG_SEPARATOR = f" {MID_DOT} "

EPW_COLUMNS = [
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "data_source",
    "dry_bulb_c",
    "dew_point_c",
    "relative_humidity_pct",
    "atmospheric_pressure_pa",
    "extraterrestrial_horizontal_radiation_wh_m2",
    "extraterrestrial_direct_normal_radiation_wh_m2",
    "horizontal_infrared_radiation_wh_m2",
    "global_horizontal_radiation_wh_m2",
    "direct_normal_radiation_wh_m2",
    "diffuse_horizontal_radiation_wh_m2",
    "global_horizontal_illuminance_lux",
    "direct_normal_illuminance_lux",
    "diffuse_horizontal_illuminance_lux",
    "zenith_luminance_cd_m2",
    "wind_direction_deg",
    "wind_speed_m_s",
    "total_sky_cover_tenths",
    "opaque_sky_cover_tenths",
    "visibility_km",
    "ceiling_height_m",
    "present_weather_observation",
    "present_weather_codes",
    "precipitable_water_mm",
    "aerosol_optical_depth_thousandths",
    "snow_depth_cm",
    "days_since_last_snowfall",
    "albedo",
    "liquid_precipitation_depth_mm",
    "liquid_precipitation_quantity_hr",
]
NUMERIC_EPW_COLUMNS = tuple(column for column in EPW_COLUMNS if column != "data_source")

EPW_VARIABLES = {
    "dry_bulb_c": {
        "label": "Temperatura seca",
        "unit": DEG_C,
        "aggregate": "mean",
        "color": "#f26b5b",
    },
    "relative_humidity_pct": {
        "label": "Humitat relativa",
        "unit": "%",
        "aggregate": "mean",
        "color": "#4f8ef7",
    },
    "wind_speed_m_s": {
        "label": "Velocitat del vent",
        "unit": "m/s",
        "aggregate": "mean",
        "color": "#2ca58d",
    },
    "direct_normal_radiation_wh_m2": {
        "label": "Radiació directa normal",
        "unit": WH_PER_M2,
        "aggregate": "sum",
        "color": "#ef7d57",
        "scale_to_kilo": True,
        "display_unit_aggregated": KWH_PER_M2,
    },
}

MISSING_SENTINELS = {
    "dry_bulb_c": {99.9},
    "dew_point_c": {99.9},
    "relative_humidity_pct": {999.0},
    "atmospheric_pressure_pa": {999999.0},
    "extraterrestrial_horizontal_radiation_wh_m2": {9999.0},
    "extraterrestrial_direct_normal_radiation_wh_m2": {9999.0},
    "horizontal_infrared_radiation_wh_m2": {9999.0},
    "global_horizontal_radiation_wh_m2": {9999.0},
    "direct_normal_radiation_wh_m2": {9999.0},
    "diffuse_horizontal_radiation_wh_m2": {9999.0},
    "global_horizontal_illuminance_lux": {999999.0},
    "direct_normal_illuminance_lux": {999999.0},
    "diffuse_horizontal_illuminance_lux": {999999.0},
    "zenith_luminance_cd_m2": {999999.0, 9999.0},
    "wind_direction_deg": {999.0},
    "wind_speed_m_s": {999.0},
    "total_sky_cover_tenths": {99.0},
    "opaque_sky_cover_tenths": {99.0},
    "visibility_km": {9999.0},
    "ceiling_height_m": {99999.0},
    "precipitable_water_mm": {999.0},
    "snow_depth_cm": {999.0},
    "days_since_last_snowfall": {99.0},
    "albedo": {999.0},
    "liquid_precipitation_depth_mm": {999.0},
    "liquid_precipitation_quantity_hr": {99.0},
}

COMFORT_RADIATION_SOURCE_COLUMNS = (
    "dry_bulb_c",
    "direct_normal_radiation_wh_m2",
    "diffuse_horizontal_radiation_wh_m2",
    "day_of_year",
    "hour_start",
)
COMFORT_RADIATION_COLUMNS = (
    "direction",
    "theta_deg",
    "altitude_band",
    "radius_start",
    "radius_size",
    "comfort_radiation_kwh_m2",
    "incident_radiation_kwh_m2",
)


def _parse_optional_float(value: str | None) -> float:
    """Retorna un camp numèric EPW com a flotant, o NaN quan el valor està en blanc o no és vàlid."""

    if value is None or value == "":
        return np.nan
    try:
        return float(value)
    except ValueError:
        return np.nan


def _header_payload(header_lines: list[str], line_index: int) -> str:
    """Retorna la càrrega útil després de la primera coma en una línia de capçalera EPW."""

    if len(header_lines) <= line_index or "," not in header_lines[line_index]:
        return "-"
    return header_lines[line_index].split(",", 1)[1].strip() or "-"


def _classify_climate(annual_mean_temp: float) -> str:
    """Classifica la família climàtica a partir de la temperatura mitjana anual de bulb sec."""

    if annual_mean_temp > 22:
        return "Càlid"
    if annual_mean_temp < 12:
        return "Fred"
    return "Mixt"


def _metadata_coordinates(metadata: dict[str, object]) -> tuple[float, float, float] | None:
    """Retorna valors vàlids de latitud, longitud i zona horària de les metadades EPW."""

    try:
        coordinates = (
            float(metadata.get("latitude")),
            float(metadata.get("longitude")),
            float(metadata.get("timezone")),
        )
    except (TypeError, ValueError):
        return None
    if any(pd.isna(value) for value in coordinates):
        return None
    return coordinates


def variable_label(variable_key: str, *, aggregated: bool = False) -> str:
    """Retorna l'etiqueta UI i la unitat de visualització per a una clau variable EPW."""

    spec = EPW_VARIABLES[variable_key]
    if aggregated and spec.get("display_unit_aggregated"):
        unit = spec["display_unit_aggregated"]
    else:
        unit = spec["unit"]
    return f"{spec['label']} ({unit})" if unit else spec["label"]


def _parse_location_line(line: str) -> dict[str, object]:
    """Analitza la línia de capçalera EPW LOCATION als camps de metadades del lloc."""

    parts = [part.strip() for part in line.strip().split(",")]
    return {
        "city": parts[1] if len(parts) > 1 else "-",
        "state": parts[2] if len(parts) > 2 else "-",
        "country": parts[3] if len(parts) > 3 else "-",
        "source": parts[4] if len(parts) > 4 else "-",
        "wmo": parts[5] if len(parts) > 5 else "-",
        "latitude": _parse_optional_float(parts[6] if len(parts) > 6 else None),
        "longitude": _parse_optional_float(parts[7] if len(parts) > 7 else None),
        "timezone": _parse_optional_float(parts[8] if len(parts) > 8 else None),
        "elevation_m": _parse_optional_float(parts[9] if len(parts) > 9 else None),
    }


def _read_epw_header(epw_path: Path) -> list[str]:
    """Llegeix i torna les vuit línies de capçalera estàndard EPW."""

    with epw_path.open("r", encoding="utf-8", errors="ignore") as file_handle:
        return [file_handle.readline().rstrip("\n") for _ in range(8)]


def _build_epw_metadata(epw_path: Path, header_lines: list[str]) -> dict[str, object]:
    """Crea metadades de fitxer i ubicació a partir de les línies de capçalera EPW."""

    metadata = _parse_location_line(header_lines[0] if header_lines else "")
    metadata.update(
        {
            "file_name": epw_path.name,
            "stem": epw_path.stem,
            "comments_1": _header_payload(header_lines, 5),
            "comments_2": _header_payload(header_lines, 6),
            "data_periods": header_lines[7] if len(header_lines) > 7 else "-",
            "header_lines": header_lines,
        }
    )
    return metadata


def _read_epw_data(epw_path: Path) -> pd.DataFrame:
    """Llegeix les files de dades per hora EPW en un DataFrame sense processar."""

    raw_data_frame = pd.read_csv(
        epw_path,
        skiprows=8,
        header=None,
        names=EPW_COLUMNS,
        encoding="utf-8",
        encoding_errors="ignore",
    )
    return raw_data_frame


def _clean_epw_data(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Converteix EPW columnes numèriques i substituir EPW els sentinelles de valors que falten per NaN."""

    for column in NUMERIC_EPW_COLUMNS:
        data_frame[column] = pd.to_numeric(data_frame[column], errors="coerce")

    for column, sentinels in MISSING_SENTINELS.items():
        if column in data_frame.columns:
            data_frame[column] = data_frame[column].replace(list(sentinels), np.nan)

    return data_frame


def _add_time_features(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Afegeix segells de temps normalitzats i atributs de calendari utilitzades pels gràfics de visualització."""

    data_frame["hour_start"] = data_frame["hour"].fillna(1).clip(1, 24).astype(int) - 1
    data_frame["source_year"] = data_frame["year"].fillna(2001).astype("Int64")
    data_frame["timestamp"] = pd.to_datetime(
        {
            "year": 2001,
            "month": data_frame["month"].fillna(1).astype(int),
            "day": data_frame["day"].fillna(1).astype(int),
            "hour": data_frame["hour_start"],
            "minute": 0,
        },
        errors="coerce",
    )
    data_frame["date"] = data_frame["timestamp"].dt.normalize()
    data_frame["month_label"] = pd.Categorical(
        data_frame["month"].map(MONTH_LABELS),
        categories=MONTH_ORDER,
        ordered=True,
    )
    data_frame["day_of_year"] = data_frame["timestamp"].dt.dayofyear
    return data_frame


def _add_climate_metadata(metadata: dict[str, object], data_frame: pd.DataFrame) -> dict[str, object]:
    """Afegeix mètriques climàtiques derivades a les metadades EPW carregades."""

    annual_mean_temp = float(data_frame["dry_bulb_c"].mean())
    metadata["annual_mean_temp"] = annual_mean_temp
    metadata["climate_family"] = _classify_climate(annual_mean_temp)
    return metadata


@st.cache_data(show_spinner=False)
def list_epw_catalog(root_path_str: str) -> tuple[dict[str, str], ...]:
    """Escaneja un directori arrel i retorna entrades de catàleg cercables per a tots els fitxers EPW."""

    root_path = Path(root_path_str)
    rows: list[dict[str, str]] = []

    for epw_path in sorted(root_path.rglob("*.epw")):
        city = "-"
        country = "-"
        try:
            with epw_path.open("r", encoding="utf-8", errors="ignore") as file_handle:
                first_line = file_handle.readline()
            location = _parse_location_line(first_line)
            city = str(location["city"])
            country = str(location["country"])
        except OSError:
            pass

        relative_path = epw_path.relative_to(root_path).as_posix()
        display_name = f"{city}, {country}{CATALOG_SEPARATOR}{relative_path}" if city != "-" else relative_path
        search_blob = " ".join([display_name, epw_path.stem, relative_path]).lower()
        rows.append(
            {
                "path": str(epw_path),
                "relative_path": relative_path,
                "display_name": display_name,
                "search_blob": search_blob,
            }
        )

    return tuple(rows)


@st.cache_data(show_spinner=False)
def load_epw_bundle(epw_path_str: str) -> dict[str, object]:
    """Carrega un fitxer EPW i retorna'n les metadades més un clima enriquit DataFrame."""

    epw_path = Path(epw_path_str)
    header_lines = _read_epw_header(epw_path)
    data_frame = _read_epw_data(epw_path)
    data_frame = _clean_epw_data(data_frame)
    data_frame = _add_time_features(data_frame)
    metadata = _build_epw_metadata(epw_path, header_lines)
    metadata = _add_climate_metadata(metadata, data_frame)

    return {
        "metadata": metadata,
        "data": data_frame,
    }


def summarize_epw_metrics(data_frame: pd.DataFrame) -> dict[str, float]:
    """Retorna les mètriques del clima, el vent, la humitat, la pressió i la radiació."""

    has_rows = not data_frame.empty
    ghi_total_kwh_m2 = np.nan
    dni_total_kwh_m2 = np.nan
    dhi_total_kwh_m2 = np.nan
    if has_rows:
        ghi_total_kwh_m2 = float(data_frame["global_horizontal_radiation_wh_m2"].sum() / 1000.0)
        dni_total_kwh_m2 = float(data_frame["direct_normal_radiation_wh_m2"].sum() / 1000.0)
        dhi_total_kwh_m2 = float(data_frame["diffuse_horizontal_radiation_wh_m2"].sum() / 1000.0)

    return {
        "records": float(len(data_frame)),
        "mean_temp": float(data_frame["dry_bulb_c"].mean()) if has_rows else np.nan,
        "min_temp": float(data_frame["dry_bulb_c"].min()) if has_rows else np.nan,
        "max_temp": float(data_frame["dry_bulb_c"].max()) if has_rows else np.nan,
        "mean_rh": float(data_frame["relative_humidity_pct"].mean()) if has_rows else np.nan,
        "mean_wind": float(data_frame["wind_speed_m_s"].mean()) if has_rows else np.nan,
        "max_wind": float(data_frame["wind_speed_m_s"].max()) if has_rows else np.nan,
        "ghi_total_kwh_m2": ghi_total_kwh_m2,
        "dni_total_kwh_m2": dni_total_kwh_m2,
        "dhi_total_kwh_m2": dhi_total_kwh_m2,
    }


def build_monthly_summary(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Agrupa les principals variables tèrmiques, d'humitat, de vent i solars per mes."""

    monthly = (
        data_frame.groupby(["month", "month_label"], observed=True)
        .agg(
            dry_bulb_mean=("dry_bulb_c", "mean"),
            dry_bulb_min=("dry_bulb_c", "min"),
            dry_bulb_max=("dry_bulb_c", "max"),
            relative_humidity_mean=("relative_humidity_pct", "mean"),
            global_horizontal_radiation_kwh_m2=("global_horizontal_radiation_wh_m2", "sum"),
            direct_normal_radiation_kwh_m2=("direct_normal_radiation_wh_m2", "sum"),
            diffuse_horizontal_radiation_kwh_m2=("diffuse_horizontal_radiation_wh_m2", "sum"),
        )
        .reset_index()
        .sort_values("month")
    )
    radiation_columns = [
        "global_horizontal_radiation_kwh_m2",
        "direct_normal_radiation_kwh_m2",
        "diffuse_horizontal_radiation_kwh_m2",
    ]
    monthly[radiation_columns] = monthly[radiation_columns] / 1000.0
    return monthly


def aggregate_epw_timeseries(
    data_frame: pd.DataFrame,
    variable_key: str,
    aggregation_label: str,
) -> pd.DataFrame:
    """Agrega una variable EPW a la sèrie horària, diària, setmanal o mensual sol·licitada."""

    series_frame = data_frame[["timestamp", variable_key]].dropna().sort_values("timestamp")
    if series_frame.empty:
        return series_frame

    rule = TIME_AGGREGATION_RULES.get(aggregation_label)
    if not rule:
        return series_frame.reset_index(drop=True)

    variable_spec = EPW_VARIABLES[variable_key]
    aggregate_mode = variable_spec["aggregate"]
    if aggregate_mode == "sum":
        aggregated = series_frame.set_index("timestamp").resample(rule).sum(numeric_only=True).reset_index()
    else:
        aggregated = series_frame.set_index("timestamp").resample(rule).mean(numeric_only=True).reset_index()

    if variable_spec.get("scale_to_kilo"):
        aggregated[variable_key] = aggregated[variable_key] / 1000.0

    return aggregated.reset_index(drop=True)


def build_daily_temperature_profile(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Retorna els valors diaris mínims, mitjans i màxims de temperatura de bulb sec."""

    daily = (
        data_frame.dropna(subset=["date"])
        .groupby("date", observed=False)
        .agg(
            dry_bulb_min=("dry_bulb_c", "min"),
            dry_bulb_mean=("dry_bulb_c", "mean"),
            dry_bulb_max=("dry_bulb_c", "max"),
        )
        .reset_index()
    )
    return daily


def build_hourly_profile(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Retorna perfils horaris mitjans per a les principals variables meteorològiques."""

    hourly = (
        data_frame.groupby("hour_start", observed=False)
        .agg(
            dry_bulb_mean=("dry_bulb_c", "mean"),
            dew_point_mean=("dew_point_c", "mean"),
            relative_humidity_mean=("relative_humidity_pct", "mean"),
        )
        .reset_index()
    )
    return hourly


def build_heatmap_table(data_frame: pd.DataFrame, variable_key: str) -> pd.DataFrame:
    """Crea una taula dinàmica mes a hora per a la variable EPW seleccionada."""

    heatmap = (
        data_frame.pivot_table(
            index="month_label",
            columns="hour_start",
            values=variable_key,
            aggfunc="mean",
            observed=False,
        )
        .reindex(MONTH_ORDER)
    )
    return heatmap


def build_annual_hourly_heatmap_table(data_frame: pd.DataFrame, variable_key: str) -> pd.DataFrame:
    """Crea una taula dinàmica hora a dia de l'any per a la variable EPW seleccionada."""

    heatmap = (
        data_frame.pivot_table(
            index="hour_start",
            columns="day_of_year",
            values=variable_key,
            aggfunc="mean",
            observed=False,
        )
        .sort_index()
        .reindex(index=list(range(24)))
    )
    return heatmap


def _solar_position_frame(
    data_frame: pd.DataFrame,
    latitude_deg: float,
    longitude_deg: float,
    timezone_hours: float,
) -> pd.DataFrame:
    """Estima l'altitud i l'azimut solar per a cada fila horària EPW."""

    solar_frame = data_frame[["day_of_year", "hour_start"]].copy()
    solar_frame = solar_frame.dropna()
    if solar_frame.empty:
        return pd.DataFrame(columns=["altitude_deg", "azimuth_deg"])

    day_of_year = solar_frame["day_of_year"].to_numpy(dtype=float)
    local_hour = solar_frame["hour_start"].to_numpy(dtype=float) + 0.5

    gamma = 2.0 * np.pi / 365.0 * (day_of_year - 1.0 + (local_hour - 12.0) / 24.0)
    equation_of_time = 229.18 * (
        0.000075
        + 0.001868 * np.cos(gamma)
        - 0.032077 * np.sin(gamma)
        - 0.014615 * np.cos(2.0 * gamma)
        - 0.040849 * np.sin(2.0 * gamma)
    )
    declination = (
        0.006918
        - 0.399912 * np.cos(gamma)
        + 0.070257 * np.sin(gamma)
        - 0.006758 * np.cos(2.0 * gamma)
        + 0.000907 * np.sin(2.0 * gamma)
        - 0.002697 * np.cos(3.0 * gamma)
        + 0.00148 * np.sin(3.0 * gamma)
    )

    true_solar_minutes = (local_hour * 60.0 + equation_of_time + 4.0 * longitude_deg - 60.0 * timezone_hours) % 1440.0
    hour_angle_deg = true_solar_minutes / 4.0 - 180.0
    hour_angle_rad = np.deg2rad(hour_angle_deg)
    latitude_rad = np.deg2rad(latitude_deg)

    cos_zenith = (
        np.sin(latitude_rad) * np.sin(declination)
        + np.cos(latitude_rad) * np.cos(declination) * np.cos(hour_angle_rad)
    )
    cos_zenith = np.clip(cos_zenith, -1.0, 1.0)
    zenith_rad = np.arccos(cos_zenith)
    altitude_deg = np.rad2deg(np.pi / 2.0 - zenith_rad)

    azimuth_deg = (
        np.rad2deg(
            np.arctan2(
                np.sin(hour_angle_rad),
                np.cos(hour_angle_rad) * np.sin(latitude_rad) - np.tan(declination) * np.cos(latitude_rad),
            )
        )
        + 180.0
    ) % 360.0

    return pd.DataFrame(
        {
            "altitude_deg": altitude_deg,
            "azimuth_deg": azimuth_deg,
        },
        index=solar_frame.index,
    )


def build_comfort_radiation_table(data_frame: pd.DataFrame, metadata: dict[str, object]) -> pd.DataFrame:
    """Estima la radiació incident per orientació, ponderada pel benefici de calefacció o refrigeració."""

    empty_result = pd.DataFrame(columns=COMFORT_RADIATION_COLUMNS)
    coordinates = _metadata_coordinates(metadata)
    if coordinates is None:
        return empty_result.copy()
    latitude, longitude, timezone = coordinates

    radiation_frame = data_frame[list(COMFORT_RADIATION_SOURCE_COLUMNS)].dropna().copy()
    if radiation_frame.empty:
        return empty_result.copy()

    solar_frame = _solar_position_frame(radiation_frame, latitude, longitude, timezone)
    if solar_frame.empty:
        return empty_result.copy()

    radiation_frame = radiation_frame.join(solar_frame)
    radiation_frame = radiation_frame[radiation_frame["altitude_deg"] > 0.0].copy()
    if radiation_frame.empty:
        return empty_result.copy()

    altitude_edges = np.array([0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 90.0])
    altitude_labels = tuple(
        f"{int(start)}-{int(end)}{DEG}" for start, end in zip(altitude_edges[:-1], altitude_edges[1:])
    )
    altitude_indices = np.digitize(radiation_frame["altitude_deg"].to_numpy(), altitude_edges, right=False) - 1
    altitude_indices = np.clip(altitude_indices, 0, len(altitude_labels) - 1)

    temperature = radiation_frame["dry_bulb_c"].to_numpy(dtype=float)
    direct_normal = radiation_frame["direct_normal_radiation_wh_m2"].to_numpy(dtype=float)
    diffuse_horizontal = radiation_frame["diffuse_horizontal_radiation_wh_m2"].to_numpy(dtype=float)
    altitude_rad = np.deg2rad(radiation_frame["altitude_deg"].to_numpy(dtype=float))
    azimuth_deg = radiation_frame["azimuth_deg"].to_numpy(dtype=float)

    benefit_weight = np.clip((18.0 - temperature) / 8.0, 0.0, 1.0)
    harm_weight = np.clip((temperature - 24.0) / 8.0, 0.0, 1.0)
    comfort_weight = benefit_weight - harm_weight

    rows: list[dict[str, float | str]] = []
    orientation_centers = np.arange(0.0, 360.0, 22.5)

    for direction_label, theta_deg in zip(WIND_DIRECTION_LABELS, orientation_centers):
        azimuth_delta_rad = np.deg2rad(((azimuth_deg - theta_deg + 180.0) % 360.0) - 180.0)
        incident_direct = direct_normal * np.maximum(0.0, np.cos(altitude_rad) * np.cos(azimuth_delta_rad))
        incident_vertical = incident_direct + diffuse_horizontal * 0.5
        signed_incident = incident_vertical * comfort_weight

        orientation_frame = pd.DataFrame(
            {
                "altitude_band": [altitude_labels[int(index)] for index in altitude_indices],
                "comfort_radiation_kwh_m2": signed_incident / 1000.0,
                "incident_radiation_kwh_m2": incident_vertical / 1000.0,
            }
        )
        summary = (
            orientation_frame.groupby("altitude_band", observed=False)
            .agg(
                comfort_radiation_kwh_m2=("comfort_radiation_kwh_m2", "sum"),
                incident_radiation_kwh_m2=("incident_radiation_kwh_m2", "sum"),
            )
            .reindex(altitude_labels, fill_value=0.0)
            .reset_index()
        )

        for band_index, band_row in summary.iterrows():
            rows.append(
                {
                    "direction": direction_label,
                    "theta_deg": float(theta_deg),
                    "altitude_band": str(band_row["altitude_band"]),
                    "radius_start": float(altitude_edges[band_index]),
                    "radius_size": float(altitude_edges[band_index + 1] - altitude_edges[band_index]),
                    "comfort_radiation_kwh_m2": float(band_row["comfort_radiation_kwh_m2"]),
                    "incident_radiation_kwh_m2": float(band_row["incident_radiation_kwh_m2"]),
                }
            )

    return pd.DataFrame(rows)


def _build_wind_rose_table(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Freqüència del vent de retorn i velocitat mitjana agrupades en sectors de brúixola."""

    wind_frame = data_frame[["wind_direction_deg", "wind_speed_m_s"]].dropna()
    if wind_frame.empty:
        return pd.DataFrame(columns=["direction", "frequency_pct", "mean_speed"])

    adjusted = (wind_frame["wind_direction_deg"] + 11.25) % 360
    sector_indices = ((adjusted / 22.5).astype(int) % len(WIND_DIRECTION_LABELS)).to_numpy()
    sectors = [WIND_DIRECTION_LABELS[int(index)] for index in sector_indices]
    rose = (
        pd.DataFrame(
            {
                "direction": sectors,
                "wind_speed_m_s": wind_frame["wind_speed_m_s"].to_numpy(),
            }
        )
        .groupby("direction", as_index=False)
        .agg(
            count=("wind_speed_m_s", "size"),
            mean_speed=("wind_speed_m_s", "mean"),
        )
        .set_index("direction")
        .reindex(WIND_DIRECTION_LABELS, fill_value=0.0)
        .reset_index()
    )
    total = rose["count"].sum()
    rose["frequency_pct"] = np.where(total > 0, rose["count"] / total * 100.0, 0.0)
    return rose


def build_monthly_wind_rose_tables(data_frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Construeix una taula resum de la rosa dels vents per a cada mes natural."""

    month_tables: dict[str, pd.DataFrame] = {}
    for month_number, month_label in MONTH_LABELS.items():
        month_frame = data_frame[data_frame["month"] == month_number]
        rose = _build_wind_rose_table(month_frame)
        if not rose.empty:
            month_tables[month_label] = rose
    return month_tables


def build_download_frame(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Retorna les columnes EPW netes que s'exporten com a CSV des de UI."""

    export_columns = [
        "timestamp",
        "source_year",
        "month",
        "day",
        "hour",
        "dry_bulb_c",
        "dew_point_c",
        "relative_humidity_pct",
        "wind_speed_m_s",
        "wind_direction_deg",
        "atmospheric_pressure_pa",
        "global_horizontal_radiation_wh_m2",
        "direct_normal_radiation_wh_m2",
        "diffuse_horizontal_radiation_wh_m2",
        "total_sky_cover_tenths",
        "opaque_sky_cover_tenths",
    ]
    export_frame = data_frame[export_columns].copy()
    export_frame["timestamp"] = export_frame["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    return export_frame
