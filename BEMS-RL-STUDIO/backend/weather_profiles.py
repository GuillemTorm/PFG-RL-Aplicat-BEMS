"""Anàlisi de perfils meteorològics i vista prèvia per crear entorns."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import plotly.graph_objects as go


EPW_HEADER_ROW_COUNT = 8
EPW_DRY_BULB_COLUMN_INDEX = 6
WEATHER_PREVIEW_RANDOM_SEED = 42
MONTH_START_DAYS = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def _sanitize_weather_identifier(raw_value: str, fallback: str) -> str:
    """Retorna un identificador estable en minúscules per a les claus del perfil meteorològic."""

    slug = re.sub(r"[^a-zA-Z0-9]+", "_", raw_value.strip().lower()).strip("_")
    return slug or fallback


def _unique_weather_identifier(base: str, used: set[str]) -> str:
    """Retorna un identificador meteorològic únic dins del conjunt proporcionat."""

    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


@dataclass(frozen=True)
class WeatherProfileSuggestion:
    """Descriu un suggeriment de fitxer meteorològic per a la creació de l'entorn UI."""

    file_name: str
    path: str
    suggested_key: str
    climate_label: str
    mean_dry_bulb: Optional[float]


def summarize_weather_file(weather_path: Path) -> Tuple[Optional[float], str]:
    """Analitza un fitxer EnergyPlus Weather (EPW) per suggerir una classificació climàtica.

    Paràmetres:
        weather_path (Path): camí cap al fitxer EPW.

    Retorna:
        Tuple[Optional[float], str]: una tupla que conté la temperatura mitjana de bulb sec (si s'analitza correctament),
        i una cadena de category ('calent', 'cool', 'mixt' o 'personalitzat').
    """
    try:
        with open(weather_path, "r", encoding="utf-8", errors="ignore") as file_handle:
            lines = file_handle.readlines()[8:]
    except OSError:
        return None, "custom"

    temperatures: List[float] = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) <= 6:
            continue
        try:
            temperatures.append(float(parts[6]))
        except ValueError:
            continue

    if not temperatures:
        return None, "custom"

    mean_dry_bulb = sum(temperatures) / len(temperatures)
    if mean_dry_bulb >= 18.0:
        return mean_dry_bulb, "hot"
    if mean_dry_bulb <= 12.0:
        return mean_dry_bulb, "cool"
    return mean_dry_bulb, "mixed"


def _parse_epw_int(value: str) -> Optional[int]:
    """Analitza un nombre enter d'una cel·la EPW tot tolerant les cadenes decimals."""

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _parse_epw_float(value: str) -> Optional[float]:
    """Analitza un nombre flotant d'una cel·la EPW i retorna None quan la cel·la no sigui vàlida."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _calculate_epw_day_of_year(row: Sequence[str], fallback_index: int) -> int:
    """Retorna el dia de l'any basat en 1 representat per una fila de dades EPW."""

    fallback_day = fallback_index // 24 + 1
    if len(row) < 3:
        return fallback_day

    month = _parse_epw_int(row[1])
    day = _parse_epw_int(row[2])
    if month is None or day is None or month < 1 or month > 12 or day < 1:
        return fallback_day

    return MONTH_START_DAYS[month - 1] + day


def load_epw_dry_bulb_series(weather_path: Path) -> List[Dict[str, float]]:
    """Carrega els registres de temperatura de bulb sec cada hora des d'un fitxer meteorològic EPW.

    Paràmetres:
        weather_path (Path): camí cap al fitxer meteorològic EPW.

    Retorna:
        List[Dict[str, float]]: registres horàries amb dia de l'any, índex d'hores,
        i temperatura de bulb sec en graus centígrads. S'ometen files no vàlides.
    """

    records: List[Dict[str, float]] = []
    try:
        with open(weather_path, "r", encoding="utf-8", errors="ignore", newline="") as file_handle:
            reader = csv.reader(file_handle)
            for _ in range(EPW_HEADER_ROW_COUNT):
                next(reader, None)

            for row in reader:
                if len(row) <= EPW_DRY_BULB_COLUMN_INDEX:
                    continue
                temperature = _parse_epw_float(row[EPW_DRY_BULB_COLUMN_INDEX])
                if temperature is None:
                    continue

                record_index = len(records)
                records.append(
                    {
                        "annual_hour": float(record_index + 1),
                        "day_of_year": float(_calculate_epw_day_of_year(row, record_index)),
                        "dry_bulb_temperature_c": temperature,
                    }
                )
    except OSError:
        return []

    return records


def _build_ornstein_uhlenbeck_noise(
    row_count: int,
    sigma: float,
    mu: float,
    tau: float,
    *,
    seed: int = WEATHER_PREVIEW_RANDOM_SEED,
) -> np.ndarray:
    """Construeix un soroll determinista Ornstein-Uhlenbeck per al gràfic de vista prèvia del clima."""

    safe_tau = max(float(tau), 1e-9)
    sigma_bis = float(sigma) * np.sqrt(2.0 / safe_tau)
    rng = np.random.default_rng(seed)
    noise = np.zeros(row_count)

    for index in range(row_count - 1):
        noise[index + 1] = (
            noise[index]
            + (-(noise[index] - float(mu)) / safe_tau)
            + sigma_bis * rng.normal()
        )

    return noise


def build_weather_temperature_preview(
    weather_path: Path,
    sigma: float,
    mu: float,
    tau: float,
) -> List[Dict[str, float]]:
    """Crea dades de vista prèvia de la temperatura diària per a la variació estocàstica del clima.

    La vista prèvia reflecteix la pertorbació meteorològica d'Ornstein-Uhlenbeck amb Sinergym
    una llavor aleatòria fixa, de manera que UI s'actualitza de manera previsible quan l'usuari canvia el
    controls sigma, mu o tau.

    Paràmetres:
        weather_path (Path): fitxer EPW utilitzat com a font climàtica base.
        sigma (float): paràmetre de desviació estàndard per al procés d'OU.
        mu (float): paràmetre mitjà per al procés d'OU.
        tau (float): paràmetre constant de temps per al procés d'OU, en hores.

    Retorna:
        List[Dict[str, float]]: temperatures mitjanes diàries per al EPW original,
        la vista prèvia modificada determinista i una banda sigma visual.
    """

    hourly_records = load_epw_dry_bulb_series(weather_path)
    if not hourly_records:
        return []

    noise = _build_ornstein_uhlenbeck_noise(
        len(hourly_records),
        sigma=float(sigma),
        mu=float(mu),
        tau=float(tau),
    )
    daily_accumulators: Dict[int, Dict[str, float]] = {}

    for index, record in enumerate(hourly_records):
        day = int(record["day_of_year"])
        base_temperature = record["dry_bulb_temperature_c"]
        expected_temperature = base_temperature + float(mu)
        modified_temperature = base_temperature + float(noise[index])
        accumulator = daily_accumulators.setdefault(
            day,
            {
                "count": 0.0,
                "base_temperature_c": 0.0,
                "expected_temperature_c": 0.0,
                "modified_temperature_c": 0.0,
                "lower_temperature_c": 0.0,
                "upper_temperature_c": 0.0,
            },
        )
        accumulator["count"] += 1.0
        accumulator["base_temperature_c"] += base_temperature
        accumulator["expected_temperature_c"] += expected_temperature
        accumulator["modified_temperature_c"] += modified_temperature
        accumulator["lower_temperature_c"] += expected_temperature - float(sigma)
        accumulator["upper_temperature_c"] += expected_temperature + float(sigma)

    preview_records: List[Dict[str, float]] = []
    for day, accumulator in sorted(daily_accumulators.items()):
        count = max(accumulator.pop("count"), 1.0)
        preview_records.append(
            {
                "day_of_year": float(day),
                "base_temperature_c": accumulator["base_temperature_c"] / count,
                "expected_temperature_c": accumulator["expected_temperature_c"] / count,
                "modified_temperature_c": accumulator["modified_temperature_c"] / count,
                "lower_temperature_c": accumulator["lower_temperature_c"] / count,
                "upper_temperature_c": accumulator["upper_temperature_c"] / count,
            }
        )

    return preview_records


def build_weather_temperature_preview_figure(preview_records: Sequence[Dict[str, float]]) -> go.Figure:
    """Crea la figura de previsualització anual de la temperatura per a la pàgina Afegeix un entorn.

    Paràmetres:
        preview_records (Sequence[Dict[str, float]]): dades de vista prèvia de la temperatura diària.

    Retorna:
        go.Figure: Plotly figura que compara la temperatura de bulb sec original i modificada.
    """

    day_values = [record["day_of_year"] for record in preview_records]
    max_day = max(day_values) if day_values else 365.0
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=day_values,
            y=[record["upper_temperature_c"] for record in preview_records],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=day_values,
            y=[record["lower_temperature_c"] for record in preview_records],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(95, 84, 249, 0.13)",
            line=dict(width=0),
            name="Rang sigma",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=day_values,
            y=[record["base_temperature_c"] for record in preview_records],
            mode="lines",
            name="EPW original",
            line=dict(color="#3b82f6", width=2),
            hovertemplate="Dia %{x:.0f}<br>Original %{y:.1f} °C<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=day_values,
            y=[record["modified_temperature_c"] for record in preview_records],
            mode="lines",
            name="Variant simulada",
            line=dict(color="#ef4444", width=2.2),
            hovertemplate="Dia %{x:.0f}<br>Simulada %{y:.1f} °C<extra></extra>",
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=42, r=24, t=34, b=46),
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f7f9fe",
        font=dict(color="#17233c", family="Bahnschrift, Aptos, Segoe UI"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            title="Dia de l'any",
            range=[1, max(365.0, float(max_day))],
            gridcolor="#dce3f2",
            zeroline=False,
        ),
        yaxis=dict(
            title="Temperatura seca (°C)",
            gridcolor="#dce3f2",
            zeroline=False,
        ),
    )
    return fig


def build_weather_profile_suggestions(weather_paths: Sequence[Path]) -> List[WeatherProfileSuggestion]:
    """Crea configuracions de perfils per a fitxers meteorològics amb noms i categorització fàcils d'utilitzar.

    Paràmetres:
        weather_paths (Sequence[Path]): una col·lecció de camins que apunten a fitxers EPW.

    Retorna:
        List[WeatherProfileSuggestion]: Configuracions recomanades i resums climàtics per als fitxers.
    """
    used_keys: set[str] = set()
    suggestions: List[WeatherProfileSuggestion] = []

    for path in weather_paths:
        mean_dry_bulb, suggested_family = summarize_weather_file(path)
        if mean_dry_bulb is None:
            climate_label = "Sense resum climàtic automàtic"
            base_key = _sanitize_weather_identifier(path.stem, "weather")
        else:
            if suggested_family == "hot":
                climate_label = f"Clima càlid ({mean_dry_bulb:.1f} °C de bulb sec mitjà)"
            elif suggested_family == "cool":
                climate_label = f"Clima fred ({mean_dry_bulb:.1f} °C de bulb sec mitjà)"
            else:
                climate_label = f"Clima mixt ({mean_dry_bulb:.1f} °C de bulb sec mitjà)"
            base_key = suggested_family

        unique_key = _unique_weather_identifier(base_key, used_keys)
        suggestions.append(
            WeatherProfileSuggestion(
                file_name=path.name,
                path=str(path),
                suggested_key=unique_key,
                climate_label=climate_label,
                mean_dry_bulb=mean_dry_bulb,
            )
        )

    return suggestions
