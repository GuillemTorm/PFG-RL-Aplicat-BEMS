"""Càrrega de dades, preparació de KPI i descobriment d'execució per a la pàgina de resultats.

El backend de resultats converteix els artefactes de entrenament i avaluació persistents en el
Estructura ``DashboardData`` consumida per Streamlit i pel generador d'informes.
Manté deliberadament el descobriment del sistema de fitxers, la normalització CSV i les dades d'acció
alineació fora del fitxer de pàgina, de manera que el mateix comportament es pot reutilitzar de manera automatitzada
exportacions.
"""

from __future__ import annotations

import copy
import glob
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go

from backend.grafics.time_utils import _ensure_datetime_index


@dataclass(frozen=True)
class RunOption:
    """Directori d'execució seleccionable que es mostra a la pàgina de resultats."""

    path: str
    name: str

    def __str__(self) -> str:
        """Str."""
        return self.name


@dataclass(frozen=True)
class ResultsPageState:
    """S'han resolt les entrades necessàries abans que es pugui representar la pàgina de resultats."""

    default_base_dir: str
    run_dirs: tuple[RunOption, ...]
    warning_message: str | None = None


@dataclass(frozen=True)
class RunArtifacts:
    """Fitxers d'artefactes derivats d'una execució seleccionada."""

    progress_path: str
    observations_path: str
    error_message: str | None = None


@dataclass
class DashboardData:
    """Es requereix un paquet de dades carregat per representar el panell de resultats en línia."""

    progress: pd.DataFrame
    obs: pd.DataFrame
    actions: pd.DataFrame
    metrics_dict: dict
    zone_opts: list
    has_zones: bool
    all_zone_options: list
    has_occupied_scope: bool
    comfort_scope_options: list
    default_comfort_scope: str
    env_name: str
    run_mode: str
    timesteps_num: int
    model_name: str
    progress_path: str = ""
    observations_path: str = ""
    actions_path: str = ""
    yaml_cfg: Any = None


_IGNORED_RUN_PARTS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
_ACTION_CONTEXT_COLUMNS = (
    "datetime",
    "timestamp",
    "month",
    "day_of_month",
    "hour",
    "time_elapsed(hours)",
)


def _is_valid_run_directory(run_directory: Path) -> bool:
    """Retorna True si el directori conté tant progress.csv com almenys un observations.csv."""
    if any(part in _IGNORED_RUN_PARTS for part in run_directory.parts):
        return False
    if not (run_directory / "progress.csv").exists():
        return False
    observation_files = glob.glob(
        os.path.join(str(run_directory), "**", "observations.csv"),
        recursive=True,
    )
    return bool(observation_files)


def _build_run_display_name(run_directory: Path, base_directory: Path) -> str:
    """Retorna una etiqueta llegible per a un directori d'execució relativa al directori base."""
    try:
        relative_path = run_directory.relative_to(base_directory)
        return str(relative_path)
    except ValueError:
        return run_directory.name


def build_results_page_state(base_dir: str | None = None) -> ResultsPageState:
    """Escaneja el directori base i construeix l'estat inicial de resultats."""

    resolved_base_dir = Path.cwd() if base_dir is None else Path(base_dir)
    progress_files = glob.glob(
        os.path.join(str(resolved_base_dir), "**", "progress.csv"),
        recursive=True,
    )
    run_directories = sorted(
        {
            Path(path).parent
            for path in progress_files
            if _is_valid_run_directory(Path(path).parent)
        },
        key=os.path.getmtime,
        reverse=True,
    )

    if not run_directories:
        return ResultsPageState(
            default_base_dir=str(Path.cwd()),
            run_dirs=(),
            warning_message="No s'ha trobat cap execució amb progress.csv i observations.csv.",
        )

    return ResultsPageState(
        default_base_dir=str(Path.cwd()),
        run_dirs=tuple(
            RunOption(
                path=str(run_directory),
                name=_build_run_display_name(run_directory, resolved_base_dir),
            )
            for run_directory in run_directories
        ),
    )


def get_run_artifacts(selected_run: str) -> RunArtifacts:
    """Resol els fitxers d'artefactes principals associats a una execució seleccionada."""

    latest_progress = os.path.join(selected_run, "progress.csv")
    observation_files = glob.glob(
        os.path.join(selected_run, "**", "observations.csv"),
        recursive=True,
    )

    if not (os.path.exists(latest_progress) and observation_files):
        return RunArtifacts(
            progress_path=latest_progress,
            observations_path="",
            error_message="Falten progress.csv o observations.csv en l'execució seleccionada.",
        )

    sorted_observation_files = sorted(
        observation_files,
        key=os.path.getmtime,
        reverse=True,
    )
    # Quan hi ha més d'un episodi, el CSV més recent sol correspondre a l'episodi
    # en curs (potencialment incomplet); agafem el segon, que és l'últim complet.
    selected_observation = (
        sorted_observation_files[1]
        if len(sorted_observation_files) > 1
        else sorted_observation_files[0]
    )

    return RunArtifacts(
        progress_path=latest_progress,
        observations_path=selected_observation,
    )


def load_action_data(observations_path: str) -> tuple[pd.DataFrame, str]:
    """Carrega la primera acció admesa CSV que es troba al costat del fitxer d'observacions."""

    monitor_dir = Path(observations_path).parent
    for filename in ("simulated_actions.csv", "agent_actions.csv"):
        candidate = monitor_dir / filename
        if not candidate.is_file():
            continue
        try:
            return pd.read_csv(candidate), str(candidate)
        except Exception:
            continue
    return pd.DataFrame(), ""


def align_actions_with_observations(
    actions: pd.DataFrame,
    obs: pd.DataFrame,
) -> pd.DataFrame:
    """Alineeu les files d'acció amb les marques de temps d'observació i columnes temporals útils."""

    if actions.empty or obs.empty:
        return actions

    aligned = actions.copy()
    obs_index = obs.index
    action_count = len(aligned)
    if len(obs_index) == action_count + 1:
        context = obs.iloc[1:action_count + 1]
    else:
        context = obs.iloc[:action_count]

    aligned = aligned.iloc[:len(context)].copy()
    aligned.index = context.index
    for column in _ACTION_CONTEXT_COLUMNS:
        if column in context.columns and column not in aligned.columns:
            aligned[column] = context[column].to_numpy()
    return aligned


def select_actions_for_obs(actions: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame:
    """Retorna les files d'acció que corresponen al sector d'observació proporcionat."""

    if actions.empty or obs.empty:
        return pd.DataFrame()
    if isinstance(actions.index, pd.DatetimeIndex) and isinstance(obs.index, pd.DatetimeIndex):
        selected = actions.loc[actions.index.isin(obs.index)].copy()
        if not selected.empty:
            return selected.sort_index(kind="mergesort")
    return actions.iloc[:len(obs)].copy().sort_index(kind="mergesort")


def is_radiant_run(data: DashboardData) -> bool:
    """Retorna si l'execució seleccionada pertany a una configuració d'edifici radiant."""

    run_text = f"{data.env_name} {data.model_name} {data.yaml_cfg}".lower()
    return "radiant" in run_text


def select_radiant_action_data(actions: pd.DataFrame, data: DashboardData) -> pd.DataFrame:
    """Retorna les dades d'acció només quan l'execució seleccionada utilitza el control del sòl radiant."""

    if actions.empty or not is_radiant_run(data):
        return pd.DataFrame(index=actions.index)
    return actions


def load_dashboard_data(progress_path: str, observations_path: str) -> DashboardData:
    """Carrega i retorna el paquet de dades complet utilitzat pel panell de resultats."""

    import yaml

    from backend.grafics.comfort_scope import has_occupied_data
    from backend.grafics.data_loader import load_data
    from backend.grafics.figures_zones import get_zone_options
    from backend.grafics.metrics import compute_metrics

    yaml_cfg = None
    try:
        yaml_candidates = list(Path(progress_path).parent.glob("*.yaml"))
        if yaml_candidates:
            with open(yaml_candidates[0], "r", encoding="utf-8") as config_file:
                yaml_cfg = yaml.safe_load(config_file)
    except Exception:
        pass

    progress, obs = load_data(progress_path, observations_path)
    obs = _ensure_observation_time_columns(obs)

    actions, actions_path = load_action_data(observations_path)
    actions = align_actions_with_observations(actions, obs)

    metrics_dict = compute_metrics(progress, obs, yaml_cfg=yaml_cfg)
    zone_opts = get_zone_options(obs, yaml_cfg)
    has_zones = len(zone_opts) > 1
    all_zone_options = [{"label": "Global (Totes)", "value": "ALL"}] + zone_opts
    has_occupied_scope = has_occupied_data(obs)
    comfort_scope_options = [{"label": "Totes les hores", "value": "all"}]
    if has_occupied_scope:
        comfort_scope_options.append(
            {"label": "Nomes hores ocupades", "value": "occupied"}
        )
    default_comfort_scope = "occupied" if has_occupied_scope else "all"

    run_folder = Path(progress_path).parent
    run_folder_name = run_folder.name
    match_env = re.match(r"(.*?)(?:-res\d+)?$", run_folder_name)
    env_name = match_env.group(1) if match_env else run_folder_name
    is_eval = len(progress) < 10
    run_mode = "Avaluacio" if is_eval else "Entrenament"

    if "time/total_timesteps" in progress.columns:
        timesteps_num = int(progress["time/total_timesteps"].max())
    elif "length(timesteps)" in progress.columns:
        timesteps_num = int(progress["length(timesteps)"].sum())
    else:
        timesteps_num = len(obs)

    model_name = resolve_model_name_for_run(progress_path, env_name)

    return DashboardData(
        progress=progress,
        obs=obs,
        actions=actions,
        metrics_dict=metrics_dict,
        zone_opts=zone_opts,
        has_zones=has_zones,
        all_zone_options=all_zone_options,
        has_occupied_scope=has_occupied_scope,
        comfort_scope_options=comfort_scope_options,
        default_comfort_scope=default_comfort_scope,
        env_name=env_name,
        run_mode=run_mode,
        timesteps_num=timesteps_num,
        model_name=model_name,
        progress_path=progress_path,
        observations_path=observations_path,
        actions_path=actions_path,
        yaml_cfg=yaml_cfg,
    )


def resolve_model_name_for_run(progress_path: str, env_name: str) -> str:
    """Retorna el nom del model desat més probable per a una execució de resultats."""

    run_folder = Path(progress_path).parent
    env_slug = _slugify_model_lookup(env_name)
    fallback = "Desconegut / No Especificat"

    metadata_candidate = _model_name_from_training_metadata(run_folder, env_name, env_slug)
    if metadata_candidate:
        return metadata_candidate

    zip_candidate = _model_name_from_zip_search(run_folder, env_name, env_slug)
    if zip_candidate:
        return zip_candidate

    return fallback


def _slugify_model_lookup(value: str) -> str:
    """Normalitza els noms igual que els directoris d'artefactes d'entrenament."""

    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", str(value)).strip("-").lower()
    return cleaned or "sense-nom"


def _candidate_model_roots(run_folder: Path) -> list[Path]:
    """Retorna les arrels probables que continguin artefactes de model desats."""

    cwd = Path.cwd()
    roots = [
        run_folder,
        run_folder.parent,
        cwd / "trainings",
        cwd / "models",
        cwd,
    ]
    unique_roots: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except Exception:
            resolved = root
        if resolved in seen or not root.exists():
            continue
        seen.add(resolved)
        unique_roots.append(root)
    return unique_roots


def _model_name_from_training_metadata(
    run_folder: Path,
    env_name: str,
    env_slug: str,
) -> str | None:
    """Troba un training_config.json que coincideixi i retorna la base del fitxer del model."""

    config_candidates: list[tuple[int, float, str]] = []
    progress_mtime = _safe_mtime(run_folder / "progress.csv")

    # Busquem training_config.json propers a la run. Si hi ha diversos candidats, guanya
    # el que coincideix millor amb l'env_id i amb una data de modificació més propera.
    for root in _candidate_model_roots(run_folder):
        if root.name in _IGNORED_RUN_PARTS:
            continue
        try:
            config_paths = (
                root.rglob("training_config.json")
                if root.name in {"trainings", "models"}
                else root.glob("training_config.json")
            )
            for config_path in config_paths:
                try:
                    with open(config_path, "r", encoding="utf-8") as handle:
                        payload = json.load(handle)
                except Exception:
                    continue

                payload_env = str(payload.get("env_id") or "")
                payload_slug = _slugify_model_lookup(payload_env)
                if payload_env != env_name and payload_slug != env_slug:
                    continue

                artifact_name = str(payload.get("artifact_name") or config_path.parent.name)
                files = payload.get("files") if isinstance(payload.get("files"), dict) else {}
                model_file = str(files.get("model") or f"{artifact_name}.zip")
                model_stem = Path(model_file).stem or artifact_name
                model_path = config_path.parent / model_file
                distance = abs(_safe_mtime(model_path if model_path.exists() else config_path) - progress_mtime)
                score = 2 if payload_env == env_name else 1
                config_candidates.append((score, -distance, model_stem))
        except Exception:
            continue

    if not config_candidates:
        return None

    config_candidates.sort(reverse=True)
    return config_candidates[0][2]


def _model_name_from_zip_search(
    run_folder: Path,
    env_name: str,
    env_slug: str,
) -> str | None:
    """Troba un model zip probable quan les metadades no estiguin disponibles."""

    env_text = env_name.lower()
    zip_candidates: list[tuple[int, float, str]] = []
    progress_mtime = _safe_mtime(run_folder / "progress.csv")

    for root in _candidate_model_roots(run_folder):
        try:
            zip_paths = (
                root.rglob("*.zip")
                if root.name in {"trainings", "models"}
                else root.glob("*.zip")
            )
            for zip_path in zip_paths:
                stem_lower = zip_path.stem.lower()
                stem_slug = _slugify_model_lookup(zip_path.stem)
                score = 0
                if env_slug and env_slug in stem_slug:
                    score = 2
                elif env_text and env_text in stem_lower:
                    score = 1
                if score <= 0:
                    continue
                distance = abs(_safe_mtime(zip_path) - progress_mtime)
                zip_candidates.append((score, -distance, zip_path.stem))
        except Exception:
            continue

    if not zip_candidates:
        return None

    zip_candidates.sort(reverse=True)
    return zip_candidates[0][2]


def _safe_mtime(path: Path) -> float:
    """Retorna un fitxer mtime, o 0 quan no estigui disponible."""

    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def load_comparison_data(run_path: str) -> DashboardData | None:
    """Carrega les dades del panell per a una execució de comparació, retornant None quan no és vàlid."""

    artifacts = get_run_artifacts(run_path)
    if artifacts.error_message:
        return None
    try:
        return load_dashboard_data(artifacts.progress_path, artifacts.observations_path)
    except Exception:
        return None


def prepare_obs_time_index(obs: pd.DataFrame) -> pd.DataFrame:
    """Retorna les observacions amb un DatetimeIndex coherent per a visualitzacions de sèries temporals reals."""

    return _ensure_datetime_index(obs)


def build_real_period_options(obs: pd.DataFrame, period_kind: str) -> list[tuple[str, str]]:
    """Prepara opcions de dia, setmana o mes per a les sèries temporals en brut."""

    df = prepare_obs_time_index(obs)
    if df.empty or not isinstance(df.index, pd.DatetimeIndex):
        return []

    if period_kind == "day":
        days = pd.Index(df.index.floor("D").unique()).sort_values()
        return [
            (day.strftime("%Y-%m-%d"), day.strftime("%d/%m/%Y"))
            for day in days
        ]

    if period_kind == "week":
        normalized = df.index.normalize()
        week_starts = pd.Index(
            normalized - pd.to_timedelta(normalized.dayofweek, unit="D")
        ).unique().sort_values()
        return [
            (
                start.strftime("%Y-%m-%d"),
                f"{start.strftime('%d/%m/%Y')} - {(start + pd.Timedelta(days=6)).strftime('%d/%m/%Y')}",
            )
            for start in week_starts
        ]

    months = pd.Index(df.index.to_period("M").unique()).sort_values()
    return [
        (month.strftime("%Y-%m"), month.strftime("%m/%Y"))
        for month in months
    ]


def slice_obs_for_real_period(
    obs: pd.DataFrame,
    period_kind: str,
    selected_value: str,
    *,
    allow_fallback: bool = False,
) -> tuple[pd.DataFrame, str | None]:
    """Filtreu les observacions al període de dia, setmana o mes seleccionat."""

    df = prepare_obs_time_index(obs)
    if df.empty or not selected_value:
        return df.iloc[0:0].copy(), None

    if period_kind == "day":
        target = pd.Timestamp(selected_value).normalize()
        mask = df.index.floor("D") == target
        if not mask.any() and allow_fallback:
            # Les runs de comparació poden tenir un any diferent; en aquest cas comparem
            # el mateix dia i mes, que és el que l'usuari espera visualment.
            mask = (df.index.month == target.month) & (df.index.day == target.day)
        result = df.loc[mask].copy().sort_index(kind="mergesort")
        if result.empty:
            return result, target.strftime("%d/%m/%Y")
        actual_day = result.index[0].normalize()
        return result, actual_day.strftime("%d/%m/%Y")

    if period_kind == "week":
        target = pd.Timestamp(selected_value).normalize()
        week_start = df.index.normalize() - pd.to_timedelta(df.index.dayofweek, unit="D")
        mask = week_start == target
        if not mask.any() and allow_fallback:
            iso_target = target.isocalendar()
            iso_current = df.index.isocalendar()
            mask = iso_current.week.astype(int) == int(iso_target.week)
        result = df.loc[mask].copy().sort_index(kind="mergesort")
        if result.empty:
            end = target + pd.Timedelta(days=6)
            return result, f"{target.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}"
        actual_start = result.index.min().normalize()
        actual_start = actual_start - pd.Timedelta(days=int(actual_start.dayofweek))
        actual_end = actual_start + pd.Timedelta(days=6)
        return result, f"{actual_start.strftime('%d/%m/%Y')} - {actual_end.strftime('%d/%m/%Y')}"

    target = pd.Period(selected_value, freq="M")
    mask = df.index.to_period("M") == target
    if not mask.any() and allow_fallback:
        mask = df.index.month == int(target.month)
    result = df.loc[mask].copy().sort_index(kind="mergesort")
    if result.empty:
        return result, target.strftime("%m/%Y")
    actual_month = result.index[0].to_period("M")
    return result, actual_month.strftime("%m/%Y")


def apply_real_period_axis(
    fig: go.Figure,
    obs: pd.DataFrame,
    period_kind: str,
) -> go.Figure:
    """Mapeja els rastres de figures de sèries temporals en brut en un eix de temps relatiu compacte."""

    if not has_figure_data(fig):
        return fig

    df = prepare_obs_time_index(obs)
    if df.empty or not isinstance(df.index, pd.DatetimeIndex):
        return fig

    start = df.index.min()
    elapsed = pd.Series(
        (df.index - start).total_seconds(),
        index=df.index,
        dtype=float,
    )

    if period_kind == "day":
        relative_x = elapsed / 3600.0
        markers = pd.Series(df.index.floor("h"), index=df.index)
        start_flags = markers.ne(markers.shift())
        tickvals = relative_x[start_flags].tolist()
        ticktext = [stamp.strftime("%H:%M") for stamp in markers[start_flags].tolist()]
        axis_title = "Hores del dia"
    elif period_kind == "week":
        relative_x = elapsed / 86400.0
        markers = pd.Series(df.index.floor("D"), index=df.index)
        start_flags = markers.ne(markers.shift())
        tickvals = relative_x[start_flags].tolist()
        ticktext = [f"Dia {idx}" for idx in range(1, len(tickvals) + 1)]
        axis_title = "Dies del període"
    else:
        relative_x = elapsed / 86400.0
        markers = pd.Series(df.index.floor("D"), index=df.index)
        start_flags = markers.ne(markers.shift())
        tickvals = relative_x[start_flags].tolist()
        ticktext = [str(stamp.day) for stamp in markers[start_flags].tolist()]
        axis_title = "Dies del mes"

    if not tickvals:
        return fig

    relative_x_values = relative_x.tolist()
    period_start_x_values = relative_x[start_flags].tolist()
    hour_markers = pd.Series(df.index.floor("h"), index=df.index)
    hour_start_flags = hour_markers.ne(hour_markers.shift())
    hour_start_x_values = relative_x[hour_start_flags].tolist()
    for trace in fig.data:
        try:
            # Cada figura pot venir amb granularitats diferents: punts raw, agregats per hora
            # o agregats pel període. Triem l'eix relatiu mirant quants punts té la traça.
            x_values = getattr(trace, "x", None)
            if x_values is None:
                continue
            if len(x_values) == len(relative_x_values):
                trace.x = relative_x_values
            elif len(x_values) == len(hour_start_x_values):
                trace.x = hour_start_x_values
            elif len(x_values) == len(period_start_x_values):
                trace.x = period_start_x_values
        except Exception:
            continue

    fig.update_xaxes(
        title=axis_title,
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        range=[float(relative_x.iloc[0]), float(relative_x.iloc[-1])],
    )
    return fig


def flatten_trace_values(values: Any) -> list[Any]:
    """Retorna valors escalars de les matrius de traça Plotly possiblement imbricades."""

    # Plotly pot guardar dades com list, Series, ndarray o fins i tot DataFrame.
    # Ho aplanem tot per poder decidir si una figura té valors numèrics reals.
    if values is None:
        return []

    if isinstance(values, (str, bytes)):
        return [values]

    if isinstance(values, pd.DataFrame):
        return values.to_numpy().ravel().tolist()

    if isinstance(values, pd.Series):
        return values.tolist()

    if hasattr(values, "ravel"):
        try:
            return values.ravel().tolist()
        except Exception:
            pass

    if hasattr(values, "to_numpy"):
        try:
            return values.to_numpy().ravel().tolist()
        except Exception:
            pass

    try:
        iterator = list(values)
    except TypeError:
        return [values]

    flattened: list[Any] = []
    for item in iterator:
        # Les traces de heatmap solen venir imbricades; fem recursió només amb llistes
        # i tuples per no tractar strings com a seqüències de caràcters.
        if isinstance(item, (str, bytes)):
            flattened.append(item)
            continue
        if isinstance(item, pd.Series):
            flattened.extend(item.tolist())
            continue
        if isinstance(item, pd.DataFrame):
            flattened.extend(item.to_numpy().ravel().tolist())
            continue
        if hasattr(item, "ravel"):
            try:
                flattened.extend(item.ravel().tolist())
                continue
            except Exception:
                pass
        if isinstance(item, (list, tuple)):
            flattened.extend(flatten_trace_values(item))
            continue
        flattened.append(item)

    return flattened


def trace_has_numeric_values(trace: go.BaseTraceType) -> bool:
    """Retorna si una traça Plotly conté almenys un valor numèric."""

    for attribute in ("y", "z", "r", "values"):
        values = flatten_trace_values(getattr(trace, attribute, None))
        if not values:
            continue
        numeric_values = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
        if not numeric_values.empty:
            return True
    return False


def has_figure_data(fig: go.Figure) -> bool:
    """Retorna si una figura Plotly té almenys un rastre amb valors traçables."""

    if fig is None:
        return False

    traces = getattr(fig, "data", [])
    if not traces:
        return False

    return any(trace_has_numeric_values(trace) for trace in traces)


def has_action_figure_data(fig: go.Figure) -> bool:
    """Retorna si una figura d'accions d'agent conté una acció real diferent de zero."""

    if not has_figure_data(fig):
        return False

    for trace in getattr(fig, "data", []):
        values = flatten_trace_values(getattr(trace, "y", None))
        if not values:
            continue
        numeric_values = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
        if not numeric_values.empty and bool((numeric_values.abs() > 0).any()):
            return True

    return False


def add_comfort_percentage_kpi(
    kpi_dict: dict,
    df: pd.DataFrame,
    comfort_config: Any = None,
) -> None:
    """Afegeix un percentatge d'hores de confort KPI al diccionari KPI proporcionat al seu lloc."""

    violation_column = next(
        (column for column in df.columns if re.search(r"(?i)temp[_]?violation", column)),
        None,
    )
    if violation_column is not None:
        series = pd.to_numeric(df[violation_column], errors="coerce").dropna()
        if not series.empty:
            kpi_dict["% Hores en Confort"] = round(float((series <= 1e-9).mean() * 100), 1)
            return

    try:
        from backend.grafics.comfort import _ensure_temp_violation_column

        with_violation = _ensure_temp_violation_column(df, comfort_config)
        violation = pd.to_numeric(with_violation["temp_violation"], errors="coerce").dropna()
        if not violation.empty:
            kpi_dict["% Hores en Confort"] = round(float((violation <= 1e-9).mean() * 100), 1)
            return
    except Exception:
        pass

    average_violation = kpi_dict.get("Avg Temp Violation (All Hours, C)")
    if average_violation is not None:
        kpi_dict["% Hores en Confort"] = (
            100.0 if float(average_violation) == 0.0 else None
        )


def overlay_comparison_traces(
    main_fig: go.Figure,
    comp_fig: go.Figure,
    label_suffix: str = " (ref)",
) -> go.Figure:
    """Superposeu traces de referència en una figura principal quan el tipus de gràfic ho admet."""

    if not has_figure_data(comp_fig):
        return main_fig

    main_barmode = (main_fig.layout.barmode or "").lower()
    if main_barmode in ("stack", "relative"):
        return main_fig

    if any(getattr(trace, "type", "") == "pie" for trace in main_fig.data) or any(
        getattr(trace, "type", "") == "pie" for trace in comp_fig.data
    ):
        return main_fig
    if any(getattr(trace, "type", "") == "heatmap" for trace in main_fig.data) or any(
        getattr(trace, "type", "") == "heatmap" for trace in comp_fig.data
    ):
        return main_fig

    result = go.Figure(main_fig)
    main_bar_index = 0
    for trace in result.data:
        if isinstance(trace, go.Bar):
            # Les barres de la run principal i la referència han d'anar en grups separats,
            # no apilades, perquè el delta sigui llegible d'un cop d'ull.
            trace.update(
                offsetgroup=f"main-{main_bar_index}",
                alignmentgroup="comparison-bars",
            )
            main_bar_index += 1
        elif isinstance(trace, (go.Scatter, go.Scattergl)) and getattr(trace, "stackgroup", None):
            trace.update(stackgroup=f"{trace.stackgroup}-main")

    has_bar_traces = any(isinstance(trace, go.Bar) for trace in comp_fig.data)
    comp_bar_index = 0

    for trace in comp_fig.data:
        trace_copy = copy.deepcopy(trace)
        original_name = getattr(trace_copy, "name", None) or ""
        trace_copy.name = original_name + label_suffix

        if isinstance(trace_copy, (go.Scatter, go.Scattergl)):
            # Les línies de referència van puntejades per no confondre-les amb la run actual.
            if getattr(trace_copy, "stackgroup", None):
                trace_copy.update(stackgroup=f"{trace_copy.stackgroup}-ref")
            trace_copy.update(line=dict(dash="dot", width=3.0), opacity=0.92)
        elif isinstance(trace_copy, go.Bar):
            trace_copy.update(
                marker_line_width=1,
                offsetgroup=f"ref-{comp_bar_index}",
                alignmentgroup="comparison-bars",
                opacity=0.58,
            )
            comp_bar_index += 1
        else:
            trace_copy.update(opacity=0.55)

        result.add_trace(trace_copy)

    if has_bar_traces:
        result.update_layout(barmode="group", bargap=0.18, bargroupgap=0.08)

    return result


def _ensure_observation_time_columns(obs: pd.DataFrame) -> pd.DataFrame:
    """Assegureu-vos que les observacions incloguin camps de mes i hora quan hi hagi marques de temps."""

    if "month" in obs.columns and "hour" in obs.columns:
        return obs

    if "timestamp" in obs.columns:
        timestamps = pd.to_datetime(obs["timestamp"], errors="coerce")
    elif "datetime" in obs.columns:
        timestamps = pd.to_datetime(obs["datetime"], errors="coerce")
    else:
        return obs

    result = obs.copy()
    result["month"] = timestamps.dt.month
    result["hour"] = timestamps.dt.hour
    result.index = timestamps
    return result
