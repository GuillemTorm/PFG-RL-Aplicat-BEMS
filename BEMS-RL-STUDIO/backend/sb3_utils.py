"""Descoberta, càrrega i format d'accions per a models Stable-Baselines3.

Els fluxos de treball d'avaluació i control en directe utilitzen aquest mòdul per localitzar polítiques desades,
carregar fitxers zip SB3, adjuntar estadístiques VecNormalize, deduir Sinergym compatibles
entorns i convertir les accions en representacions amigables amb UI.
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from gymnasium.spaces import Box, Discrete, MultiBinary, MultiDiscrete
from stable_baselines3 import A2C, DDPG, DQN, PPO, SAC, TD3
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.save_util import load_from_zip_file
from stable_baselines3.common.vec_env import VecEnv, VecNormalize

from backend.common import list_registered_env_ids


ALGOS: Dict[str, type] = {"PPO": PPO, "A2C": A2C, "DQN": DQN, "SAC": SAC, "TD3": TD3, "DDPG": DDPG}
VECNORM_SUFFIXES: List[str] = ["vecnormalize.pkl", "vecnorm.pkl", "vec_norm.pkl", "normalize.pkl"]


def scan_model_zips(dir_list_text: str) -> pd.DataFrame:
    """Escaneja directoris separats per comes per trobar models Stable-Baselines3 ``.zip``."""
    rows: List[Dict[str, Any]] = []
    for chunk in dir_list_text.split(","):
        root = Path(chunk.strip())
        if not root.exists():
            continue
        for path in root.rglob("*.zip"):
            rows.append(
                {
                    "name": path.name,
                    "stem": path.stem,
                    "path": str(path.resolve()),
                    "dir": str(path.parent.resolve()),
                }
            )
    if not rows:
        return pd.DataFrame(columns=["name", "stem", "path", "dir"])
    return pd.DataFrame(rows).sort_values(by=["stem", "name"]).reset_index(drop=True)


def candidate_vecnorm(model_path: Path) -> Optional[Path]:
    """Retorna el fitxer d'estadístiques VecNormalize més probable al costat d'un zip de model."""
    folder = model_path.parent
    stem = model_path.stem.lower()
    for suffix in VECNORM_SUFFIXES:
        for candidate in [folder / f"{model_path.stem}_{suffix}", folder / f"{stem}_{suffix}"]:
            if candidate.exists():
                return candidate
    for file_path in folder.glob("*.pkl"):
        if any(file_path.name.lower().endswith(suffix) for suffix in VECNORM_SUFFIXES):
            return file_path
    return None


def _algo_cls_from_meta(meta: Dict[str, Any]) -> Optional[type]:
    """Resol la classe d'algorisme SB3 declarada a les metadades del model."""
    algo = (meta or {}).get("algo", None)
    if isinstance(algo, str) and algo.upper() in ALGOS:
        return ALGOS[algo.upper()]
    return None


def load_sb3_model_bytes(model_bytes: bytes, device: str = "cpu") -> Tuple[BaseAlgorithm, Dict[str, Any]]:
    """Carrega un model Stable-Baselines3 des de bytes ZIP i retorna les metadades del model."""
    buffer = io.BytesIO(model_bytes)
    meta: Dict[str, Any] = {}
    try:
        meta, _, _ = load_from_zip_file(buffer, device=device, print_system_info=False)
    except Exception:
        meta = {}

    algo_cls = _algo_cls_from_meta(meta)
    buffer.seek(0)
    model: Optional[BaseAlgorithm] = None

    if algo_cls is not None:
        model = algo_cls.load(buffer, device=device)
    else:
        for algo_type in ALGOS.values():
            try:
                buffer.seek(0)
                model = algo_type.load(buffer, device=device)
                break
            except Exception:
                continue

    if model is None:
        raise ValueError("No s'ha pogut carregar el model SB3.")

    return model, meta


def env_id_from_meta_or_name(meta: Dict[str, Any], zip_stem: str) -> Optional[str]:
    """Dedueix un identificador d'entorn Sinergym registrat a partir de les metadades del model o el nom del fitxer."""
    candidates = list_registered_env_ids()
    for key in ("env_id", "env", "gym_id", "environment"):
        value = meta.get(key)
        if isinstance(value, str) and value in candidates:
            return value

    match = re.search(r"(Eplus-[A-Za-z0-9_\-]+-v\d+)", zip_stem)
    if match:
        return match.group(1)

    tokens = [token for token in re.split(r"[_\-]+", zip_stem.lower()) if len(token) >= 3]
    best, best_score = None, 0
    for env_id in candidates:
        score = sum(token in env_id.lower() for token in tokens)
        if score > best_score:
            best, best_score = env_id, score
    return best


def build_monitored_vec_env(env_factory: Callable[[], Any], *, seed: int | None = None) -> VecEnv:
    """Crea un ``VecEnv`` d'un sol entorn delegant ``Monitor`` i seeds a SB3."""
    return make_vec_env(env_factory, n_envs=1, seed=seed)


def build_vecnormalize_env(
    env_factory: Callable[[], Any],
    *,
    seed: int | None = None,
    norm_obs: bool = True,
    norm_reward: bool = True,
    training: bool = True,
) -> VecNormalize:
    """Crea un ``VecNormalize`` sobre el ``VecEnv`` monitoritzat de SB3."""
    venv = VecNormalize(
        build_monitored_vec_env(env_factory, seed=seed),
        norm_obs=norm_obs,
        norm_reward=norm_reward,
    )
    venv.training = training
    if not training:
        venv.norm_reward = False
    return venv


def load_vecnormalize(vec_path: str, env_factory: Callable[[], Any]) -> VecNormalize:
    """Carrega les estadístiques de VecNormalize sobre un entorn vectoritzat acabat de crear."""
    venv = build_monitored_vec_env(env_factory)
    try:
        venv = VecNormalize.load(vec_path, venv)
    except AssertionError as exc:
        msg = str(exc)
        if "spaces must have the same shape" in msg:
            import re as _re
            m = _re.search(r"\((\d+),\).*?\((\d+),\)", msg)
            detail = f" ({m.group(1)} vs {m.group(2)})" if m else ""
            raise ValueError(
                f"L'espai d'observacio del VecNormalize no coincideix amb l'entorn seleccionat{detail}. "
                "Assegura't d'avaluar el model amb el mateix entorn amb que va ser entrenat."
            ) from exc
        raise
    venv.training = False
    venv.norm_reward = False
    return venv


def _unwrap_action_space(vecenv: VecEnv):
    """Unwrap action space."""
    return vecenv.action_space


def _space_shape_tuple(space: Any) -> Optional[Tuple[int, ...]]:
    """Space shape tuple."""
    shape = getattr(space, "shape", None)
    if shape is None:
        return None
    try:
        return tuple(int(value) for value in shape)
    except Exception:
        return None


def is_normalized_box_space(space: Any) -> bool:
    """Is normalized box space."""
    if not isinstance(space, Box):
        return False
    low = np.asarray(space.low, dtype=np.float32)
    high = np.asarray(space.high, dtype=np.float32)
    return bool(np.allclose(low, -1.0) and np.allclose(high, 1.0))


def action_spaces_compatible(expected_space: Any, actual_space: Any) -> bool:
    """Espais d'acció compatibles."""
    if expected_space is None or actual_space is None:
        return True
    # Comparar només el tipus no és suficient: en Box importen forma i límits; en
    # MultiDiscrete importen els nvec. Això evita acceptar models quasi compatibles.
    if isinstance(expected_space, Box) and isinstance(actual_space, Box):
        if _space_shape_tuple(expected_space) != _space_shape_tuple(actual_space):
            return False
        return bool(
            np.allclose(expected_space.low, actual_space.low)
            and np.allclose(expected_space.high, actual_space.high)
        )
    if isinstance(expected_space, Discrete) and isinstance(actual_space, Discrete):
        return int(expected_space.n) == int(actual_space.n)
    if isinstance(expected_space, MultiDiscrete) and isinstance(actual_space, MultiDiscrete):
        return bool(np.array_equal(expected_space.nvec, actual_space.nvec))
    if isinstance(expected_space, MultiBinary) and isinstance(actual_space, MultiBinary):
        return _space_shape_tuple(expected_space) == _space_shape_tuple(actual_space)
    return type(expected_space) is type(actual_space)


def should_apply_normalize_action(model_action_space: Any, env_action_space: Any) -> bool:
    """S'ha d'aplicar l'acció de normalització."""
    if not isinstance(model_action_space, Box) or not isinstance(env_action_space, Box):
        return False
    if _space_shape_tuple(model_action_space) != _space_shape_tuple(env_action_space):
        return False
    return is_normalized_box_space(model_action_space) and not is_normalized_box_space(env_action_space)


def describe_action_space(space: Any) -> str:
    """Describe action space."""
    if isinstance(space, Box):
        return f"Box(shape={space.shape}, low={np.asarray(space.low).tolist()}, high={np.asarray(space.high).tolist()})"
    if isinstance(space, Discrete):
        return f"Discrete(n={space.n})"
    if isinstance(space, MultiDiscrete):
        return f"MultiDiscrete(nvec={np.asarray(space.nvec).tolist()})"
    if isinstance(space, MultiBinary):
        return f"MultiBinary(shape={space.shape})"
    return type(space).__name__


def _as_action_array(action: Any) -> np.ndarray:
    """Converteix una acció SB3 en ndarray sense assumir encara la forma final."""
    if isinstance(action, np.ndarray):
        return action
    if isinstance(action, (list, tuple)):
        return np.asarray(action)
    return np.asarray([action])


def _reshape_action_batch(
    action_values: np.ndarray,
    action_shape: Tuple[int, ...],
    n_envs: int,
    dtype: Any,
) -> np.ndarray:
    """Porta una acció plana a la forma ``(n_envs, *action_shape)`` esperada per VecEnv."""
    action_dimension = int(np.prod(action_shape))
    flat_action = action_values.astype(dtype).reshape(-1)

    # SB3 pot retornar una sola acció, una acció per entorn o una forma intermèdia.
    # Aquí fem que totes acabin amb la mateixa estructura abans d'aplicar límits.
    if flat_action.size == 1 and action_dimension > 1:
        flat_action = np.repeat(flat_action.item(), action_dimension)
    elif flat_action.size > action_dimension and flat_action.size % action_dimension == 0:
        pass
    elif flat_action.size > action_dimension:
        flat_action = flat_action[:action_dimension]
    elif flat_action.size < action_dimension:
        fill_value = flat_action[-1] if flat_action.size else 0
        flat_action = np.concatenate(
            [flat_action, np.repeat(fill_value, action_dimension - flat_action.size)]
        )

    action_batch = flat_action.reshape(-1, *action_shape)
    if action_batch.shape[0] == 1 and n_envs > 1:
        action_batch = np.repeat(action_batch, n_envs, axis=0)
    elif action_batch.shape[0] > n_envs:
        action_batch = action_batch[:n_envs]
    elif action_batch.shape[0] < n_envs:
        action_batch = np.concatenate(
            [action_batch] + [action_batch[-1:]] * (n_envs - action_batch.shape[0]),
            axis=0,
        )
    return action_batch.astype(dtype)


def format_action_for_env(action: Any, vecenv: VecEnv) -> np.ndarray:
    """
    Converteix l'acció que retorna el model al format esperat pel VecEnv:
      - Discrete: array shape (n_envs,), dtype=int64
      - Box: array shape (n_envs, act_dim), dtype=float32 (clip a [low, high])
    """
    action_space = _unwrap_action_space(vecenv)
    n_envs = getattr(vecenv, "num_envs", 1)

    # SB3 pot retornar escalar, llista o ndarray segons l'algorisme; primer ho normalitzem
    # per no tenir quatre camins diferents fent el mateix.
    normalized_action = _as_action_array(action)

    if isinstance(action_space, Discrete):
        # En Discrete cada entorn paral·lel espera un sol enter; si falta algun valor,
        # repetim l'últim perquè VecEnv no falli per forma incorrecta.
        normalized_action = normalized_action.reshape(-1)
        if normalized_action.size == 1 and n_envs > 1:
            normalized_action = np.repeat(int(normalized_action.item()), n_envs)
        if normalized_action.size > n_envs:
            normalized_action = normalized_action[:n_envs]
        if normalized_action.size < n_envs:
            normalized_action = np.pad(normalized_action, (0, n_envs - normalized_action.size), mode="edge")
        normalized_action = normalized_action.astype(np.int64)
        normalized_action = np.clip(normalized_action, 0, action_space.n - 1)
        return normalized_action

    if isinstance(action_space, MultiDiscrete):
        # MultiDiscrete és el cas més fàcil de trencar: l'acció pot venir plana o ja
        # agrupada per entorns. La portem a la forma (n_envs, *shape) abans de retallar.
        nvec = np.asarray(action_space.nvec, dtype=np.int64)
        action_shape = tuple(int(value) for value in nvec.shape)
        normalized_action = _reshape_action_batch(normalized_action, action_shape, n_envs, np.int64)
        return np.clip(normalized_action, 0, nvec - 1).astype(np.int64)

    if isinstance(action_space, MultiBinary):
        # MultiBinary comparteix la mateixa idea que MultiDiscrete, però només accepta 0/1.
        # El clip final evita que un model carregat amb petites diferències retorni valors fora de rang.
        action_shape = tuple(int(value) for value in action_space.shape)
        normalized_action = _reshape_action_batch(normalized_action, action_shape, n_envs, np.int64)
        return np.clip(normalized_action, 0, 1).astype(np.int8)

    if isinstance(action_space, Box):
        # En espais continus mantenim float32 i fem clip als límits reals de l'entorn.
        # Això és especialment important quan hi ha wrappers que canvien l'escala de l'acció.
        action_shape = tuple(int(value) for value in action_space.shape)
        normalized_action = _reshape_action_batch(normalized_action, action_shape, n_envs, np.float32)
        low = np.array(action_space.low, dtype=np.float32).reshape(1, *action_shape)
        high = np.array(action_space.high, dtype=np.float32).reshape(1, *action_shape)
        normalized_action = np.clip(normalized_action, low, high).astype(np.float32)
        return normalized_action

    # Fallback conservador per a espais poc habituals: es prioritza que el VecEnv rebi
    # una mida coherent, encara que després el mateix entorn acabi rebutjant l'acció.
    normalized_action = normalized_action.reshape(-1)
    if normalized_action.size == 1 and n_envs > 1:
        normalized_action = np.repeat(normalized_action.item(), n_envs)
    elif normalized_action.size > n_envs:
        normalized_action = normalized_action[:n_envs]
    elif normalized_action.size < n_envs:
        normalized_action = np.pad(normalized_action, (0, n_envs - normalized_action.size), mode="edge")
    return normalized_action.astype(np.int64)
