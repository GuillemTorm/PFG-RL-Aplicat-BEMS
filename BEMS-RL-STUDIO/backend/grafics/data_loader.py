"""Carrega i normalitza els fitxers CSV de resultats per a panells i informes.

La pàgina de resultats i el backend de l'informe passen per aquí per llegir el progrés de Sinergym,
arreglar buits de mètriques habituals, estandarditzar noms de columnes i retornar DataFrames preparats
per generar KPIs i figures Plotly.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

from backend.grafics.observation_columns import (
    add_meter_kwh_columns,
    normalize_observation_columns,
)
from backend.grafics.time_utils import sanitize_observation_time_columns

_DEFAULT_PROGRESS_HEADERS = [
    "episode_num",
    "mean_reward",
    "std_reward",
    "mean_reward_comfort_term",
    "std_reward_comfort_term",
    "mean_reward_energy_term",
    "std_reward_energy_term",
    "mean_comfort_penalty",
    "std_comfort_penalty",
    "mean_energy_penalty",
    "std_energy_penalty",
    "mean_temperature_violation",
    "std_temperature_violation",
    "mean_power_demand",
    "std_power_demand",
    "cumulative_power_demand",
    "comfort_violation_time(%)",
    "length(timesteps)",
    "time_elapsed(hours)",
    "terminated",
    "truncated",
]

_NUMERIC_PROGRESS_COLUMNS = tuple(
    column
    for column in _DEFAULT_PROGRESS_HEADERS
    if column not in {"terminated", "truncated"}
)


def _csv_signature(path: str | Path) -> tuple[str, int, int]:
    """Retorna una clau de memòria cau que canvia quan canvia el fitxer CSV."""

    csv_path = Path(path)
    stat = csv_path.stat()
    return str(csv_path), int(stat.st_mtime_ns), int(stat.st_size)


@lru_cache(maxsize=32)
def _read_csv_cached(
    path: str,
    mtime_ns: int,
    size: int,
    mode: str,
    names: tuple[str, ...],
) -> pd.DataFrame:
    """Llegeix un fitxer CSV mitjançant una memòria cau en procés conscient de mtime."""

    _ = (mtime_ns, size)
    if mode == "progress_no_header":
        return pd.read_csv(path, header=None, names=list(names))
    if mode == "low_memory_false":
        return pd.read_csv(path, low_memory=False)
    return pd.read_csv(path)


def _read_csv(path: str | Path, *, mode: str = "default", names: tuple[str, ...] = ()) -> pd.DataFrame:
    """Llegeix un fitxer CSV i en retorna una còpia segura per mutar."""

    csv_path, mtime_ns, size = _csv_signature(path)
    return _read_csv_cached(csv_path, mtime_ns, size, mode, names).copy()


def _fill_missing_or_zero(target: pd.Series, replacement: pd.Series) -> pd.Series:
    """Ompliu els valors objectiu que falten o zero amb una sèrie de substitució numèrica."""

    target = pd.to_numeric(target, errors="coerce")
    replacement = pd.to_numeric(replacement, errors="coerce")
    replace_mask = target.isna() | (
        (target == 0) & replacement.notna() & (replacement != 0)
    )
    result = target.copy()
    result.loc[replace_mask] = replacement.loc[replace_mask]
    return result


def _repair_power_metrics_from_progress(progress: pd.DataFrame) -> pd.DataFrame:
    """Repareu les mètriques de potència de progrés quan només hi hagi valors acumulatius o mitjans."""

    repaired = progress.copy()

    if (
        "cumulative_power_demand" in repaired.columns
        and "length(timesteps)" in repaired.columns
    ):
        derived_mean_from_cumulative = (
            pd.to_numeric(repaired["cumulative_power_demand"], errors="coerce")
            / pd.to_numeric(repaired["length(timesteps)"], errors="coerce").replace(0, pd.NA)
        )
        if "mean_power_demand" in repaired.columns:
            repaired["mean_power_demand"] = _fill_missing_or_zero(
                repaired["mean_power_demand"], derived_mean_from_cumulative
            )
        else:
            repaired["mean_power_demand"] = derived_mean_from_cumulative

    if (
        "mean_power_demand" in repaired.columns
        and "length(timesteps)" in repaired.columns
    ):
        derived_cumulative = (
            pd.to_numeric(repaired["mean_power_demand"], errors="coerce")
            * pd.to_numeric(repaired["length(timesteps)"], errors="coerce")
        )
        if "cumulative_power_demand" in repaired.columns:
            repaired["cumulative_power_demand"] = _fill_missing_or_zero(
                repaired["cumulative_power_demand"], derived_cumulative
            )
        else:
            repaired["cumulative_power_demand"] = derived_cumulative

    return repaired


def _drop_repeated_header_rows(data: pd.DataFrame) -> pd.DataFrame:
    """Elimina capçaleres CSV repetides accidentalment dins dels fitxers de registre."""

    if data.empty:
        return data

    header_mask = pd.Series(False, index=data.index)
    for column in data.columns:
        header_mask |= data[column].astype(str).str.strip().eq(str(column))

    if not header_mask.any():
        return data

    return data.loc[~header_mask].reset_index(drop=True)


def _coerce_progress_numeric_columns(progress: pd.DataFrame) -> pd.DataFrame:
    """Converteix les mètriques de progrés conegudes en valors numèrics."""

    coerced = progress.copy()
    for column in _NUMERIC_PROGRESS_COLUMNS:
        if column in coerced.columns:
            coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


def load_data(progress_path, obs_path):
    """Carrega els fitxers de progrés i observació CSV utilitzats pel panell de resultats."""

    progress = _read_csv(progress_path)

    # Comprova si el progress.csv té capçaleres que falten (comú quan s'afegeixen registres)
    if "mean_reward" not in progress.columns and "episode_num" not in progress.columns:
        if len(progress.columns) == len(_DEFAULT_PROGRESS_HEADERS):
            progress = _read_csv(
                progress_path,
                mode="progress_no_header",
                names=tuple(_DEFAULT_PROGRESS_HEADERS),
            )

    progress = _drop_repeated_header_rows(progress)
    progress = _coerce_progress_numeric_columns(progress)
    progress = _repair_power_metrics_from_progress(progress)

    obs = _read_csv(obs_path)

    infos_path = Path(obs_path).with_name("infos.csv")
    if infos_path.exists():
        try:
            infos = _read_csv(infos_path, mode="low_memory_false")
            if len(infos) == len(obs):
                for col in infos.columns:
                    if col not in obs.columns:
                        obs[col] = infos[col]
        except Exception:
            pass

    obs = sanitize_observation_time_columns(obs)
    obs = normalize_observation_columns(obs)
    obs = add_meter_kwh_columns(obs)

    return progress, obs
