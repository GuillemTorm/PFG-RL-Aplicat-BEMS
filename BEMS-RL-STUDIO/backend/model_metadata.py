"""Utilitats compartides per reconstruir models entrenats de l'Studio."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from backend.sb3_utils import action_spaces_compatible, describe_action_space


def load_model_metadata(model_path: Path) -> Dict[str, Any]:
    """Carrega les metadades d'entrenament associades a un model SB3."""
    metadata_path = model_path.with_name(model_path.stem + "_metadata.json")
    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as handle:
            metadata = json.load(handle)
        training_config = metadata.get("training_config") if isinstance(metadata.get("training_config"), dict) else {}
        if not metadata.get("env_id"):
            metadata["env_id"] = training_config.get("env_id")
        if not metadata.get("reward_name"):
            metadata["reward_name"] = training_config.get("reward_name")
        if "wrapper_configs" not in metadata and "wrapper_configs" in training_config:
            metadata["wrapper_configs"] = training_config.get("wrapper_configs", [])
        if "meters" not in metadata and "meters" in training_config:
            metadata["meters"] = training_config.get("meters")
        if "reward_kwargs" not in metadata and "reward_kwargs" in training_config:
            metadata["reward_kwargs"] = training_config.get("reward_kwargs")
        metadata["metadata_source"] = str(metadata_path)
        return metadata

    training_config_path = model_path.parent / "training_config.json"
    if training_config_path.exists():
        with open(training_config_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        training_config = dict(payload.get("training_config") or {})
        return {
            "env_id": payload.get("env_id") or training_config.get("env_id"),
            "reward_name": payload.get("reward_name") or training_config.get("reward_name"),
            "wrapper_configs": training_config.get("wrapper_configs", []),
            "meters": training_config.get("meters"),
            "reward_kwargs": training_config.get("reward_kwargs"),
            "training_config": training_config,
            "artifact_name": payload.get("artifact_name"),
            "metadata_source": str(training_config_path),
        }
    return {}


def build_gym_kwargs_from_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Reconstrueix els kwargs de Gym a partir de les metadades d'entrenament."""
    training_config = metadata.get("training_config") or {}
    meters = metadata.get("meters") or training_config.get("meters")
    reward_name = metadata.get("reward_name") or training_config.get("reward_name")
    reward_kwargs = metadata.get("reward_kwargs") or training_config.get("reward_kwargs") or {}

    kwargs: Dict[str, Any] = {}
    if not reward_name and not meters:
        return kwargs

    try:
        from backend.entrenar_agent_env import with_detailed_hvac_meters

        kwargs["meters"] = with_detailed_hvac_meters(meters or {})
        reward_cls = resolve_reward_class(reward_name)
        if reward_cls is not None:
            kwargs["reward"] = reward_cls
            if reward_kwargs:
                kwargs["reward_kwargs"] = reward_kwargs
    except Exception:
        pass
    return kwargs


def resolve_reward_class(reward_name: str | None) -> Any:
    """Resol una reward usant les classes exposades per Sinergym."""
    if not reward_name:
        return None
    if ":" in reward_name:
        from sinergym.utils.common import import_from_path

        return import_from_path(reward_name)
    import sinergym.utils.rewards as reward_module

    return getattr(reward_module, reward_name, None)


def validate_action_spaces(
    model_action_space: Any,
    env_action_space: Any,
    metadata: Dict[str, Any],
) -> None:
    """Valida que el model i l'entorn comparteixin el mateix contracte d'accions."""
    if action_spaces_compatible(model_action_space, env_action_space):
        return

    wrappers = metadata.get("wrapper_configs") or []
    wrapper_names = ", ".join(str(item.get("name")) for item in wrappers if isinstance(item, dict)) or "cap detectat"
    source = metadata.get("metadata_source") or "metadades no trobades"
    raise ValueError(
        "L'espai d'accions de l'entorn no coincideix amb el que espera el model. "
        f"Model: {describe_action_space(model_action_space)}; "
        f"entorn: {describe_action_space(env_action_space)}. "
        f"Wrappers detectats: {wrapper_names}. Font: {source}."
    )
