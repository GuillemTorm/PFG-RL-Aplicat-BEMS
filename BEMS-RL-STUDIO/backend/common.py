"""Utilitats compartides de projecte per al backend de BEMS-RL Studio.

Aquest mòdul agrupa peces petites que abans vivien en fitxers molt curts:
camins canònics del projecte, descoberta d'entorns Sinergym i helpers genèrics
d'arguments/format UI. Són funcions utilitzades per diversos fluxos del backend.
"""

from __future__ import annotations

import inspect
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, List, Tuple

import gymnasium as gym


def _sinergym_package_dir() -> Path:
    """Localitza el paquet Sinergym sense executar-ne el registre d'entorns."""
    spec = find_spec("sinergym")
    if spec and spec.origin:
        return Path(spec.origin).resolve().parent
    return Path("sinergym")


PKG_DIR = _sinergym_package_dir()
BUILDINGS_DIR = PKG_DIR / "data" / "buildings"
WEATHERS_DIR = PKG_DIR / "data" / "weather"
CFG_DIR = PKG_DIR / "data" / "default_configuration"

ONE_YEAR_STEPS = 35040


def registered_env_ids() -> tuple[str, ...]:
    """Retorna els ids d'entorn exposats per Sinergym."""
    try:
        import sinergym

        env_ids = sinergym.ids()
    except Exception:
        env_ids = [env_id for env_id in gym.envs.registry.keys() if env_id.startswith("Eplus-")]
    return tuple(sorted(env_ids))


def list_registered_env_ids(*, include_discrete: bool = True) -> List[str]:
    """Llista ids Sinergym, amb opcio d'excloure entorns discrets."""
    env_ids = list(registered_env_ids())
    if include_discrete:
        return env_ids
    return [env_id for env_id in env_ids if "discrete" not in env_id.lower()]


def is_registered_env_id(env_id: str) -> bool:
    """Indica si un id forma part del cataleg registrat de Sinergym."""
    return env_id in registered_env_ids()


def filter_supported_kwargs(callable_obj: Any, kwargs: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Filtra kwargs no acceptats per una funcio o classe."""
    try:
        signature_target = callable_obj.__init__ if inspect.isclass(callable_obj) else callable_obj
        signature = inspect.signature(signature_target)
    except (TypeError, ValueError):
        return dict(kwargs), []

    parameters = signature.parameters
    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()):
        return dict(kwargs), []

    allowed_kwargs = {
        name
        for name, parameter in parameters.items()
        if name != "self"
        and parameter.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    }
    filtered_kwargs = {key: value for key, value in kwargs.items() if key in allowed_kwargs}
    dropped_kwargs = [key for key in kwargs if key not in allowed_kwargs]
    return filtered_kwargs, dropped_kwargs


def format_ui_value(value: Any) -> str:
    """Formata valors arbitraris per mostrar-los a la UI."""
    if value is None:
        return "-"
    if isinstance(value, dict):
        return ", ".join(f"{key}: {format_ui_value(item)}" for key, item in value.items()) if value else "-"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(format_ui_value(item) for item in value) if value else "-"
    return str(value)
