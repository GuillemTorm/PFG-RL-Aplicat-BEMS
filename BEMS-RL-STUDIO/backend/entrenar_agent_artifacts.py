"""Rutes d'artefacte d'entrenament, metadades i postprocessament CSV."""

from __future__ import annotations

import copy
import csv
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from backend.entrenar_agent_constants import (
    DETAILED_HVAC_METERS,
    JOULES_PER_KWH,
    TRAINING_ARTIFACTS_DIR_NAME,
    TRAINING_CONFIG_FILENAME,
)


def sanitize_training_name_component(value: str) -> str:
    """Higienitzar el component del nom de la entrenament."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return cleaned or "sense-nom"


def get_training_artifacts_root(base_path: Path | None = None) -> Path:
    """Retorna l'arrel dels artefactes d'entrenament."""
    return (base_path or Path.cwd()).resolve() / TRAINING_ARTIFACTS_DIR_NAME


def build_training_artifact_paths(
    training_config: Dict[str, Any],
    base_path: Path | None = None,
) -> Dict[str, Path | str]:
    """Calcula les rutes dels artefactes d'una sessió d'entrenament."""
    artifacts_root = get_training_artifacts_root(base_path)
    env_slug = sanitize_training_name_component(training_config["env_id"])
    reward_slug = sanitize_training_name_component(training_config["reward_name"])
    family_dir = artifacts_root / env_slug / reward_slug
    prefix = f"training-{env_slug}-{reward_slug}-"
    max_index = 0

    if family_dir.exists():
        for child in family_dir.iterdir():
            if not child.is_dir():
                continue
            match = re.fullmatch(rf"{re.escape(prefix)}(\d+)", child.name)
            if match:
                max_index = max(max_index, int(match.group(1)))

    artifact_name = f"{prefix}{max_index + 1:03d}"
    artifact_dir = family_dir / artifact_name
    return {
        "artifact_name": artifact_name,
        "artifact_dir": artifact_dir,
        "model_path": artifact_dir / f"{artifact_name}.zip",
        "vecnorm_path": artifact_dir / f"{artifact_name}_vecnorm.pkl",
        "eval_script_path": artifact_dir / f"{artifact_name}_eval.py",
        "training_script_path": artifact_dir / f"{artifact_name}.py",
        "config_path": artifact_dir / TRAINING_CONFIG_FILENAME,
    }


def append_detailed_meter_kwh_columns(observations_path: str | Path) -> None:
    """Afegeix columnes detallades del comptador de kWh."""
    observations_file = Path(observations_path) if observations_path else None
    if observations_file is None or not observations_file.is_file():
        return

    with open(observations_file, "r", newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames or not rows:
        return

    source_columns: Dict[str, str] = {}
    for alias, meter_name in DETAILED_HVAC_METERS.items():
        target_column = f"{alias}_kwh"
        if target_column in fieldnames:
            continue
        if alias in fieldnames:
            source_columns[alias] = alias
        elif meter_name in fieldnames:
            source_columns[alias] = meter_name

    if not source_columns:
        return

    # EnergyPlus escriu molts meters en joules. Afegim columnes *_kwh perquè els gràfics
    # posteriors no hagin de repetir aquesta conversió cada vegada.
    derived_columns = {source_alias: f"{source_alias}_kwh" for source_alias in source_columns}
    for row in rows:
        for source_alias, source_column in source_columns.items():
            target_column = derived_columns[source_alias]
            try:
                row[target_column] = str(float(row.get(source_column, "")) / JOULES_PER_KWH)
            except (TypeError, ValueError):
                row[target_column] = ""

    output_fields = fieldnames + list(derived_columns.values())
    with open(observations_file, "w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)


def append_detailed_meter_kwh_columns_in_workspace(workspace_path: str | Path | None) -> None:
    """Afegeix columnes detallades del comptador de kWh a l'espai de treball."""
    if not workspace_path:
        return

    workspace = Path(workspace_path)
    if not workspace.is_dir():
        return

    for observations_file in workspace.rglob("observations.csv"):
        try:
            append_detailed_meter_kwh_columns(observations_file)
        except Exception:
            continue


def get_runtime_workspace_path(runtime: Dict[str, Any]) -> str | None:
    """Retorna la ruta de l'espai de treball en temps d'execució."""
    if not runtime:
        return None

    try:
        paths = runtime["vec"].get_attr("workspace_path")
        if paths and paths[0]:
            return str(paths[0])
    except Exception:
        pass

    # Segon intent: alguns models guarden el VecEnv dins model.env, depenent de com s'ha
    # creat la run i de la versió d'SB3.
    try:
        paths = runtime["model"].env.get_attr("workspace_path")
        if paths and paths[0]:
            return str(paths[0])
    except Exception:
        pass

    try:
        # Últim recurs per a runs antigues: busquem la carpeta més recent que coincideixi
        # amb l'env_id i que contingui els CSV esperats.
        env_id = runtime["config"]["env_id"]
        candidates = sorted(
            [
                directory
                for directory in Path(os.getcwd()).iterdir()
                if directory.is_dir() and directory.name.startswith(f"{env_id}-res")
            ],
            key=lambda directory: directory.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return str(candidates[0])
    except Exception:
        pass

    return None


def build_training_ui_state(options: Dict[str, Any]) -> Dict[str, Any]:
    """Prepara l'estat inicial de la interfície d'entrenament."""
    excluded_keys = {"spec", "variables"}
    return {
        key: copy.deepcopy(value)
        for key, value in options.items()
        if key not in excluded_keys
    }


def list_saved_training_runs(base_path: Path | None = None) -> List[Dict[str, Any]]:
    """Llista les sessions d'entrenament desades."""
    artifacts_root = get_training_artifacts_root(base_path)
    if not artifacts_root.exists():
        return []

    runs: List[Dict[str, Any]] = []
    for config_path in artifacts_root.rglob(TRAINING_CONFIG_FILENAME):
        try:
            with open(config_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            continue

        artifact_name = payload.get("artifact_name") or config_path.parent.name
        artifact_dir = Path(payload.get("artifact_dir") or config_path.parent)
        files = payload.get("files") or {}
        training_script_name = files.get("training_script") or f"{artifact_name}.py"
        training_script_path = artifact_dir / training_script_name

        payload["artifact_name"] = artifact_name
        payload["artifact_dir"] = str(artifact_dir)
        payload["config_path"] = str(config_path)
        payload["training_script_path"] = str(training_script_path)
        payload["training_script_exists"] = training_script_path.exists()
        runs.append(payload)

    runs.sort(
        key=lambda item: (
            item.get("created_at") or "",
            item.get("artifact_name") or "",
        ),
        reverse=True,
    )
    return runs
