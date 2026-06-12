"""Execució en directe per provar agents entrenats dins d'un entorn Sinergym.

La pàgina de control en directe utilitza aquest mòdul per crear entorns Sinergym amb wrappers,
carregueu les polítiques Stable-Baselines3, valideu la compatibilitat de les accions i traduïu-les
observacions/accions en estructures fàcils de mostrar. Evita intencionadament
Streamlit, de manera que les mateixes comprovacions poden donar suport a l'avaluació i la documentació.
"""

from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import gymnasium as gym
import numpy as np
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.vec_env import VecNormalize
from sinergym.utils.wrappers import CSVLogger, LoggerWrapper, NormalizeAction

from backend.model_metadata import (
    build_gym_kwargs_from_metadata,
    load_model_metadata,
    validate_action_spaces,
)
from backend.sb3_utils import (
    candidate_vecnorm,
    build_monitored_vec_env,
    format_action_for_env,
    load_sb3_model_bytes,
    load_vecnormalize,
    should_apply_normalize_action,
)
from backend.common import is_registered_env_id


def _make_runtime_env(
    selected_env_id: str,
    wrapper_configs: Optional[Sequence[Dict[str, Any]]] = None,
    *,
    trust_training_metadata: bool = False,
    model_action_space: Any = None,
    gym_kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """Crea una instància d'entorn d'interacció en directe embolicada."""
    env = gym.make(selected_env_id, **(gym_kwargs or {}))
    if wrapper_configs:
        from backend.entrenar_agent_wrappers import apply_training_wrappers

        env = apply_training_wrappers(env, wrapper_configs)
    elif not trust_training_metadata and should_apply_normalize_action(model_action_space, env.action_space):
        env = NormalizeAction(env)
    env = LoggerWrapper(env)
    env = CSVLogger(env)
    return env


def mode_requires_model(mode_label: str) -> bool:
    """El mode requereix un model."""
    lowered = (mode_label or "").lower()
    return "interactiva" in lowered or "avaluaci" in lowered


def load_model_training_metadata(model_path: Path) -> Dict[str, Any]:
    """Carrega les metadades d'entrenament del model."""
    return load_model_metadata(model_path)


def build_env_factory(
    selected_env_id: str,
    wrapper_configs: Optional[Sequence[Dict[str, Any]]] = None,
    *,
    trust_training_metadata: bool = False,
    model_action_space: Any = None,
    gym_kwargs: Optional[Dict[str, Any]] = None,
) -> Callable[[], Any]:
    """Crea la funció que inicialitza l'entorn de la sessió d'interacció."""
    return partial(
        _make_runtime_env,
        selected_env_id,
        wrapper_configs,
        trust_training_metadata=trust_training_metadata,
        model_action_space=model_action_space,
        gym_kwargs=gym_kwargs,
    )


def validate_action_contract(
    model_obj: Optional[BaseAlgorithm],
    vec_env: Any,
    metadata: Dict[str, Any],
) -> None:
    """Validació del contracte d'actuació."""
    if model_obj is None:
        return

    model_action_space = getattr(model_obj, "action_space", None)
    env_action_space = getattr(vec_env, "action_space", None)
    validate_action_spaces(model_action_space, env_action_space, metadata)


def _space_shape(space: Any) -> Tuple[int, ...] | None:
    """Space shape."""
    shape = getattr(space, "shape", None)
    if shape is None:
        return None
    try:
        return tuple(int(value) for value in shape)
    except Exception:
        return None


def get_model_observation_size(model_obj: Optional[BaseAlgorithm]) -> Optional[int]:
    """Retorna la mida d'observació del model."""
    if model_obj is None:
        return None
    shape = _space_shape(getattr(model_obj, "observation_space", None))
    if not shape:
        return None
    return int(np.prod(shape))


def get_observation_size_from_space(space: Any) -> Optional[int]:
    """Retorna la mida d'observació des de l'espai."""
    shape = _space_shape(space)
    if not shape:
        return None
    return int(np.prod(shape))


def get_observation_size_from_array(obs: Any) -> Optional[int]:
    """Retorna la mida de l'observació de la matriu."""
    try:
        arr = np.asarray(obs)
        if arr.ndim > 1:
            arr = arr.reshape(arr.shape[0], -1)[0]
        return int(arr.size)
    except Exception:
        return None


def flatten_observation_values(values: Any) -> List[float]:
    """Aplanar els valors d'observació."""
    if values is None:
        return []
    try:
        return [float(value) for value in np.asarray(values, dtype=np.float32).reshape(-1)]
    except Exception:
        flattened: List[float] = []
        try:
            iterator = list(values)
        except Exception:
            iterator = []
        for value in iterator:
            if isinstance(value, (list, tuple, np.ndarray)):
                flattened.extend(flatten_observation_values(value))
                continue
            try:
                flattened.append(float(value))
            except Exception:
                pass
        return flattened


def get_runtime_observation_variables(
    core_env: Any,
    obs: Any = None,
    model_obj: Optional[BaseAlgorithm] = None,
    vec_env: Any = None,
) -> List[str]:
    """Retorna les variables d'observació del clima d'execució."""
    obs_vars = get_wrapper_variables(core_env, "observation_variables")
    target_size = (
        get_model_observation_size(model_obj)
        or get_observation_size_from_space(getattr(vec_env, "observation_space", None))
        or get_observation_size_from_array(obs)
        or len(obs_vars)
    )

    if not target_size:
        return obs_vars
    if len(obs_vars) == target_size:
        return obs_vars
    if obs_vars and target_size % len(obs_vars) == 0:
        repeats = target_size // len(obs_vars)
        if repeats > 1:
            return [
                f"{variable}_hist{block + 1}"
                for block in range(repeats)
                for variable in obs_vars
            ]
    return [f"obs_{index + 1:03d}" for index in range(target_size)]


def coerce_observation_values(values: Sequence[float], expected_size: Optional[int]) -> List[float]:
    """Converteix els valors d'observació."""
    coerced = flatten_observation_values(values)
    if expected_size is None or len(coerced) == expected_size:
        return coerced
    if len(coerced) > expected_size:
        return coerced[:expected_size]
    fill_value = coerced[-1] if coerced else 0.0
    return coerced + [fill_value] * (expected_size - len(coerced))


def initialize_runtime(
    selected_env_id: str,
    mode_label: str,
    model_path: Optional[Path] = None,
) -> Tuple[Any, Any, Optional[BaseAlgorithm], Any, List[str]]:
    """Inicialitza l'execució de l'entorn."""
    init_warnings: List[str] = []
    model_obj: Optional[BaseAlgorithm] = None
    vecnorm_path: Optional[Path] = None
    metadata: Dict[str, Any] = {}
    if mode_requires_model(mode_label) and model_path is not None:
        with open(model_path, "rb") as file_handle:
            model_obj, _ = load_sb3_model_bytes(file_handle.read(), device="cpu")
        vecnorm_path = candidate_vecnorm(model_path)
        metadata = load_model_training_metadata(model_path)

    metadata_env_id = metadata.get("env_id")
    if isinstance(metadata_env_id, str) and is_registered_env_id(metadata_env_id):
        # Si el model porta env_id al metadata, el fem prevaldre sobre el text escrit a mà.
        # Això evita carregar una política entrenada amb un espai d'accions diferent.
        selected_env_id = metadata_env_id

    has_wrapper_contract = "wrapper_configs" in metadata
    wrapper_configs = list(metadata.get("wrapper_configs") or [])
    gym_kwargs = build_gym_kwargs_from_metadata(metadata)
    env_factory = build_env_factory(
        selected_env_id,
        wrapper_configs=wrapper_configs,
        trust_training_metadata=has_wrapper_contract,
        model_action_space=getattr(model_obj, "action_space", None),
        gym_kwargs=gym_kwargs or None,
    )

    vec_env = None
    if mode_requires_model(mode_label) and vecnorm_path and vecnorm_path.exists():
        # VecNormalize només és segur si es reconstrueix amb la mateixa funció de creació d'entorn.
        try:
            vec_env = load_vecnormalize(str(vecnorm_path), env_factory)
        except ValueError as exc:
            init_warnings.append(
                f"VecNormalize no aplicat: {exc} "
                "Continuant sense normalitzacio d'observacions; les prediccions del model poden ser menys precises."
            )
    if vec_env is None:
        vec_env = build_monitored_vec_env(env_factory)

    try:
        validate_action_contract(model_obj, vec_env, metadata)
    except ValueError as exc:
        init_warnings.append(f"Avis de contracte d'accions: {exc}")

    model_obs_shape = _space_shape(getattr(model_obj, "observation_space", None)) if model_obj else None
    env_obs_shape = _space_shape(getattr(vec_env, "observation_space", None))
    if model_obs_shape and env_obs_shape and model_obs_shape != env_obs_shape:
        # En mode interactiu no aturem directament: avisem i deixem que l'usuari decideixi,
        # perquè pot estar fent una prova ràpida de compatibilitat.
        model_size = int(np.prod(model_obs_shape))
        env_size = int(np.prod(env_obs_shape))
        init_warnings.append(
            f"Avis de contracte d'observacions: el model espera {model_size} variables {model_obs_shape} "
            f"pero l'entorn en dona {env_size} {env_obs_shape}. "
            "Les prediccions de l'agent no seran fiables."
        )

    core_env = vec_env.envs[0] if hasattr(vec_env, "envs") else vec_env
    obs = vec_env.reset()
    return vec_env, core_env, model_obj, obs, init_warnings


def get_wrapper_variables(core_env: Any, attr_name: str) -> List[Any]:
    """Retorna les variables del wrapper."""
    if hasattr(core_env, "get_wrapper_attr"):
        values = core_env.get_wrapper_attr(attr_name)
        if values is None:
            return []
        return list(values)
    return []


def extract_policy_test_defaults(
    obs: Any,
    info_dict: Dict[str, Any],
    obs_vars: Sequence[str],
    vec_env: Any,
    core_env: Any,
) -> List[float]:
    """Extreu els valors predeterminats de la prova de política."""
    raw_obs_values = obs[0] if getattr(obs, "ndim", 0) > 1 else obs
    has_raw = False
    if isinstance(info_dict, dict) and "observation" in info_dict:
        # Si l'entorn ens dona l'observació crua a info, és la millor base per al formulari.
        if len(info_dict["observation"]) == len(obs_vars):
            raw_obs_values = info_dict["observation"]
            has_raw = True

    if not has_raw:
        if isinstance(vec_env, VecNormalize):
            # En avaluació estàtica volem valors humans; desfem VecNormalize quan és possible.
            try:
                raw_obs_values = vec_env.unnormalize_obs(np.array([raw_obs_values]))[0]
            except Exception:
                pass

        temp = core_env
        while hasattr(temp, "env"):
            if type(temp).__name__ == "NormalizeObservation":
                # Alguns wrappers normalitzen sense VecNormalize; busquem aquest cas caminant
                # la cadena de wrappers.
                try:
                    std = np.sqrt(temp.obs_rms.var + temp.epsilon)
                    raw_obs_values = (raw_obs_values * std) + temp.obs_rms.mean
                except Exception:
                    pass
                break
            temp = temp.env

    return flatten_observation_values(raw_obs_values)


def randomize_observation_values(obs_vars: Sequence[str]) -> List[float]:
    """Aleatoritzar els valors d'observació."""
    import random

    new_vals: List[float] = []
    for var_name in obs_vars:
        lowered = var_name.lower()
        if "temperature" in lowered or "temp" in lowered:
            new_vals.append(random.uniform(5.0, 35.0))
        elif "power" in lowered or "rate" in lowered:
            new_vals.append(random.uniform(0.0, 5000.0))
        elif "month" in lowered:
            new_vals.append(float(random.randint(1, 12)))
        elif "day" in lowered:
            new_vals.append(float(random.randint(1, 31)))
        elif "hour" in lowered:
            new_vals.append(float(random.randint(0, 23)))
        else:
            new_vals.append(random.uniform(0.0, 1.0))
    return new_vals


def infer_unit(var_name: str) -> str:
    """Infer unit."""
    lowered = var_name.lower()
    if "temperature" in lowered or "temp" in lowered or "setpoint" in lowered:
        return "°C"
    if "power" in lowered or "rate" in lowered or "demand" in lowered:
        return "W"
    if "humidity" in lowered:
        return "%"
    if "speed" in lowered:
        return "m/s"
    if "direction" in lowered or "angle" in lowered:
        return "°"
    if "radiation" in lowered:
        return "W/m²"
    if "month" in lowered or "day" in lowered or "hour" in lowered:
        return ""
    return ""


def normalize_policy_observation(
    custom_obs: Sequence[float],
    core_env: Any,
    vec_env: Any,
    expected_size: Optional[int] = None,
) -> np.ndarray:
    """Normalitza l'observació de les polítiques."""
    expected_shape = _space_shape(getattr(vec_env, "observation_space", None))
    if expected_size is None and expected_shape:
        expected_size = int(np.prod(expected_shape))

    normalized_values = coerce_observation_values(custom_obs, expected_size)
    if expected_shape and int(np.prod(expected_shape)) == len(normalized_values):
        normalized = np.array(normalized_values, dtype=np.float32).reshape((1, *expected_shape))
    else:
        normalized = np.array([normalized_values], dtype=np.float32)

    temp = core_env
    while hasattr(temp, "env"):
        if type(temp).__name__ == "NormalizeObservation":
            try:
                std = np.sqrt(temp.obs_rms.var + temp.epsilon)
                normalized[0] = (normalized[0] - temp.obs_rms.mean) / std
            except Exception:
                pass
            break
        temp = temp.env

    if isinstance(vec_env, VecNormalize):
        return vec_env.normalize_obs(normalized)
    return normalized


def unnormalize_sinergym_action(action_array: Any, env_obj: Any) -> Any:
    """Unnormalize sinergym action."""
    temp = env_obj
    while hasattr(temp, "env"):
        if type(temp).__name__ == "NormalizeAction":
            return temp.action(action_array)
        temp = temp.env
    return action_array


def prepare_action_display(action: Any, vec_env: Any, core_env: Any) -> Any:
    """Prepara la visualització de l'acció."""
    action_formatted = format_action_for_env(action, vec_env)
    if isinstance(action_formatted, np.ndarray) and len(action_formatted.shape) > 1:
        action_display = action_formatted[0]
    else:
        action_display = action_formatted
    return unnormalize_sinergym_action(action_display, core_env)


def extract_display_observation(
    obs: Any,
    info_dict: Dict[str, Any],
    obs_vars: Sequence[str],
    vec_env: Any,
) -> Tuple[Any, Any]:
    """Extreu l'observació de visualització."""
    actual_obs = obs[0] if isinstance(obs, np.ndarray) and len(obs.shape) > 1 else obs
    raw_obs_values: Any = []
    has_raw = False

    # Preferim l'observació crua que torna Sinergym a info; és la que té unitats humanes.
    if isinstance(info_dict, dict) and "observation" in info_dict:
        last_raw_obs = info_dict["observation"]
        if len(last_raw_obs) == len(obs_vars):
            raw_obs_values = last_raw_obs
            has_raw = True

    if not has_raw and isinstance(vec_env, VecNormalize):
        # Si la run passa per VecNormalize, el model veu valors normalitzats. Per mostrar-los
        # a pantalla els tornem a l'escala original quan es pot.
        try:
            raw_obs_values = vec_env.unnormalize_obs(np.array([actual_obs]))[0]
            has_raw = True
        except Exception:
            pass

    display_obs = flatten_observation_values(raw_obs_values if has_raw else actual_obs)
    return actual_obs, display_obs


def extract_info_dict(infos: Any) -> Dict[str, Any]:
    """Extreu el diccionari info d'un step de VecEnv o Gym."""
    if isinstance(infos, (tuple, list, np.ndarray)):
        return infos[0] if len(infos) > 0 else {}
    if isinstance(infos, dict):
        return infos
    return {}


def build_history_entry(
    step_number: int,
    reward: float,
    info_dict: Dict[str, Any],
    next_obs: Any,
    obs_vars: Sequence[str],
    vec_env: Any,
) -> Dict[str, Any]:
    """Prepara una entrada d'historial per a una acció de l'agent."""
    hist_entry: Dict[str, Any] = {"pas": step_number, "reward": reward}

    raw_vals: Any = []
    has_raw = False
    if isinstance(info_dict, dict) and "observation" in info_dict:
        # Guardem historial en escala real perquè els KPI del panell siguin interpretables.
        last_raw = info_dict["observation"]
        if len(last_raw) == len(obs_vars):
            raw_vals = last_raw
            has_raw = True

    if not has_raw and isinstance(vec_env, VecNormalize):
        try:
            obs_2d = np.array([next_obs[0] if len(next_obs.shape) > 1 else next_obs])
            raw_vals = vec_env.unnormalize_obs(obs_2d)[0]
            has_raw = True
        except Exception:
            pass

    vals_to_log = flatten_observation_values(
        raw_vals if has_raw else (next_obs[0] if len(next_obs.shape) > 1 else next_obs)
    )
    if len(vals_to_log) == len(obs_vars):
        for var_name, value in zip(obs_vars, vals_to_log):
            hist_entry[var_name] = value

    return hist_entry


def run_environment_steps(
    vec_env: Any,
    core_env: Any,
    action_to_take: Any,
    current_step: int,
    repeat_n: int = 1,
    obs_vars: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Executa els passos de l'entorn."""
    if hasattr(core_env, "action_space"):
        action_formatted = format_action_for_env(action_to_take, vec_env)
    else:
        action_formatted = action_to_take

    runtime_obs_vars = (
        list(obs_vars)
        if obs_vars is not None
        else get_wrapper_variables(core_env, "observation_variables")
    )
    history_entries: List[Dict[str, Any]] = []
    next_obs = None
    reward = 0.0
    info_dict: Dict[str, Any] = {}
    episode_finished = False
    reset_obs = None

    for offset in range(repeat_n):
        next_obs, rewards, dones, infos = vec_env.step(action_formatted)
        reward = rewards[0] if isinstance(rewards, (list, np.ndarray)) else rewards
        done = dones[0] if isinstance(dones, (list, np.ndarray)) else dones
        info_dict = extract_info_dict(infos)

        history_entries.append(
            build_history_entry(
                step_number=current_step + offset + 1,
                reward=reward,
                info_dict=info_dict,
                next_obs=next_obs,
                obs_vars=runtime_obs_vars,
                vec_env=vec_env,
            )
        )

        if done:
            episode_finished = True
            reset_obs = vec_env.reset()
            next_obs = reset_obs
            break

    return {
        "next_obs": next_obs,
        "reward": reward,
        "info_dict": info_dict,
        "history_entries": history_entries,
        "episode_finished": episode_finished,
        "reset_obs": reset_obs,
    }


def find_matching_column(row: Dict[str, Any], keywords: Sequence[str]) -> Optional[str]:
    """Troba una columna compatible."""
    for col_name in row.keys():
        if any(keyword.lower() in col_name.lower() for keyword in keywords):
            return col_name
    return None
