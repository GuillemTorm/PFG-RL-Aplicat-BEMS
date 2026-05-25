backend/sb3_utils.py
====================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/sb3_utils.py``

**Module path:** ``backend.sb3_utils``

**Module docstring**

.. code-block:: text

   Descoberta, càrrega i format d'accions per a models Stable-Baselines3.

   Els fluxos de treball d'avaluació i control en directe utilitzen aquest mòdul per localitzar polítiques desades,
   carregar fitxers zip SB3, adjuntar estadístiques VecNormalize, deduir Sinergym compatibles
   entorns i convertir les accions en representacions amigables amb UI.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``gymnasium``, ``io``, ``numpy``, ``pandas``, ``pathlib``, ``re``, ``stable_baselines3``, ``typing``

Functions
---------

scan_model_zips
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:31``.

.. code-block:: python

   def scan_model_zips(dir_list_text: str) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Escaneja directoris separats per comes per trobar models Stable-Baselines3 ``.zip``.

candidate_vecnorm
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:52``.

.. code-block:: python

   def candidate_vecnorm(model_path: Path) -> Optional[Path]

**Docstring**

.. code-block:: text

   Retorna el fitxer d'estadístiques VecNormalize més probable al costat d'un zip de model.

_algo_cls_from_meta
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:66``.

.. code-block:: python

   def _algo_cls_from_meta(meta: Dict[str, Any]) -> Optional[type]

**Docstring**

.. code-block:: text

   Resol la classe d'algorisme SB3 declarada a les metadades del model.

load_sb3_model_bytes
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:74``.

.. code-block:: python

   def load_sb3_model_bytes(model_bytes: bytes, device: str = "cpu") -> Tuple[BaseAlgorithm, Dict[str, Any]]

**Docstring**

.. code-block:: text

   Carrega un model Stable-Baselines3 des de bytes ZIP i retorna les metadades del model.

env_id_from_meta_or_name
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:104``.

.. code-block:: python

   def env_id_from_meta_or_name(meta: Dict[str, Any], zip_stem: str) -> Optional[str]

**Docstring**

.. code-block:: text

   Dedueix un identificador d'entorn Sinergym registrat a partir de les metadades del model o el nom del fitxer.

build_monitored_vec_env
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:125``.

.. code-block:: python

   def build_monitored_vec_env(env_factory: Callable[[], Any], *, seed: int | None = None) -> VecEnv

**Docstring**

.. code-block:: text

   Crea un ``VecEnv`` d'un sol entorn delegant ``Monitor`` i seeds a SB3.

build_vecnormalize_env
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:130``.

.. code-block:: python

   def build_vecnormalize_env( env_factory: Callable[[], Any], *, seed: int | None = None, norm_obs: bool = True, norm_reward: bool = True, training: bool = True, ) -> VecNormalize

**Docstring**

.. code-block:: text

   Crea un ``VecNormalize`` sobre el ``VecEnv`` monitoritzat de SB3.

load_vecnormalize
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:150``.

.. code-block:: python

   def load_vecnormalize(vec_path: str, env_factory: Callable[[], Any]) -> VecNormalize

**Docstring**

.. code-block:: text

   Carrega les estadístiques de VecNormalize sobre un entorn vectoritzat acabat de crear.

_unwrap_action_space
~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:171``.

.. code-block:: python

   def _unwrap_action_space(vecenv: VecEnv)

**Docstring**

.. code-block:: text

   Unwrap action space.

_space_shape_tuple
~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:176``.

.. code-block:: python

   def _space_shape_tuple(space: Any) -> Optional[Tuple[int, ...]]

**Docstring**

.. code-block:: text

   Space shape tuple.

is_normalized_box_space
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:187``.

.. code-block:: python

   def is_normalized_box_space(space: Any) -> bool

**Docstring**

.. code-block:: text

   Is normalized box space.

action_spaces_compatible
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:196``.

.. code-block:: python

   def action_spaces_compatible(expected_space: Any, actual_space: Any) -> bool

**Docstring**

.. code-block:: text

   Espais d'acció compatibles.

should_apply_normalize_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:218``.

.. code-block:: python

   def should_apply_normalize_action(model_action_space: Any, env_action_space: Any) -> bool

**Docstring**

.. code-block:: text

   S'ha d'aplicar l'acció de normalització.

describe_action_space
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:227``.

.. code-block:: python

   def describe_action_space(space: Any) -> str

**Docstring**

.. code-block:: text

   Describe action space.

_as_action_array
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:240``.

.. code-block:: python

   def _as_action_array(action: Any) -> np.ndarray

**Docstring**

.. code-block:: text

   Converteix una acció SB3 en ndarray sense assumir encara la forma final.

_reshape_action_batch
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:249``.

.. code-block:: python

   def _reshape_action_batch( action_values: np.ndarray, action_shape: Tuple[int, ...], n_envs: int, dtype: Any, ) -> np.ndarray

**Docstring**

.. code-block:: text

   Porta una acció plana a la forma ``(n_envs, *action_shape)`` esperada per VecEnv.

format_action_for_env
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/sb3_utils.py:286``.

.. code-block:: python

   def format_action_for_env(action: Any, vecenv: VecEnv) -> np.ndarray

**Docstring**

.. code-block:: text

   Converteix l'acció que retorna el model al format esperat pel VecEnv:
     - Discrete: array shape (n_envs,), dtype=int64
     - Box: array shape (n_envs, act_dim), dtype=float32 (clip a [low, high])

