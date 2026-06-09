backend/interaccionar_agent_backend.py
======================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py``

**Module path:** ``backend.interaccionar_agent_backend``

**Module docstring**

.. code-block:: text

   Execució en directe per provar agents entrenats dins d'un entorn Sinergym.

   La pàgina de control en directe utilitza aquest mòdul per crear entorns Sinergym amb wrappers,
   carregueu les polítiques Stable-Baselines3, valideu la compatibilitat de les accions i traduïu-les
   observacions/accions en estructures fàcils de mostrar. Evita intencionadament
   Streamlit, de manera que les mateixes comprovacions poden donar suport a l'avaluació i la documentació.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``backend``, ``functools``, ``gymnasium``, ``numpy``, ``pathlib``, ``random``, ``sinergym``, ``stable_baselines3``, ``typing``

Functions
---------

_make_runtime_env
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:37``.

.. code-block:: python

   def _make_runtime_env( selected_env_id: str, wrapper_configs: Optional[Sequence[Dict[str, Any]]] = None, *, trust_training_metadata: bool = False, model_action_space: Any = None, gym_kwargs: Optional[Dict[str, Any]] = None, ) -> Any

**Docstring**

.. code-block:: text

   Crea una instància d'entorn d'interacció en directe embolicada.

mode_requires_model
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:58``.

.. code-block:: python

   def mode_requires_model(mode_label: str) -> bool

**Docstring**

.. code-block:: text

   El mode requereix un model.

load_model_training_metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:64``.

.. code-block:: python

   def load_model_training_metadata(model_path: Path) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Carrega les metadades d'entrenament del model.

build_env_factory
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:69``.

.. code-block:: python

   def build_env_factory( selected_env_id: str, wrapper_configs: Optional[Sequence[Dict[str, Any]]] = None, *, trust_training_metadata: bool = False, model_action_space: Any = None, gym_kwargs: Optional[Dict[str, Any]] = None, ) -> Callable[[], Any]

**Docstring**

.. code-block:: text

   Crea la funció que inicialitza l'entorn de la sessió d'interacció.

validate_action_contract
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:88``.

.. code-block:: python

   def validate_action_contract( model_obj: Optional[BaseAlgorithm], vec_env: Any, metadata: Dict[str, Any], ) -> None

**Docstring**

.. code-block:: text

   Validació del contracte d'actuació.

_space_shape
~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:102``.

.. code-block:: python

   def _space_shape(space: Any) -> Tuple[int, ...] | None

**Docstring**

.. code-block:: text

   Space shape.

get_model_observation_size
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:113``.

.. code-block:: python

   def get_model_observation_size(model_obj: Optional[BaseAlgorithm]) -> Optional[int]

**Docstring**

.. code-block:: text

   Retorna la mida d'observació del model.

get_observation_size_from_space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:123``.

.. code-block:: python

   def get_observation_size_from_space(space: Any) -> Optional[int]

**Docstring**

.. code-block:: text

   Retorna la mida d'observació des de l'espai.

get_observation_size_from_array
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:131``.

.. code-block:: python

   def get_observation_size_from_array(obs: Any) -> Optional[int]

**Docstring**

.. code-block:: text

   Retorna la mida de l'observació de la matriu.

flatten_observation_values
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:142``.

.. code-block:: python

   def flatten_observation_values(values: Any) -> List[float]

**Docstring**

.. code-block:: text

   Aplanar els valors d'observació.

get_runtime_observation_variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:165``.

.. code-block:: python

   def get_runtime_observation_variables( core_env: Any, obs: Any = None, model_obj: Optional[BaseAlgorithm] = None, vec_env: Any = None, ) -> List[str]

**Docstring**

.. code-block:: text

   Retorna les variables d'observació del clima d'execució.

coerce_observation_values
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:195``.

.. code-block:: python

   def coerce_observation_values(values: Sequence[float], expected_size: Optional[int]) -> List[float]

**Docstring**

.. code-block:: text

   Converteix els valors d'observació.

initialize_runtime
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:206``.

.. code-block:: python

   def initialize_runtime( selected_env_id: str, mode_label: str, model_path: Optional[Path] = None, ) -> Tuple[Any, Any, Optional[BaseAlgorithm], Any, List[str]]

**Docstring**

.. code-block:: text

   Inicialitza l'execució de l'entorn.

get_wrapper_variables
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:275``.

.. code-block:: python

   def get_wrapper_variables(core_env: Any, attr_name: str) -> List[Any]

**Docstring**

.. code-block:: text

   Retorna les variables del wrapper.

extract_policy_test_defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:285``.

.. code-block:: python

   def extract_policy_test_defaults( obs: Any, info_dict: Dict[str, Any], obs_vars: Sequence[str], vec_env: Any, core_env: Any, ) -> List[float]

**Docstring**

.. code-block:: text

   Extreu els valors predeterminats de la prova de política.

randomize_observation_values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:325``.

.. code-block:: python

   def randomize_observation_values(obs_vars: Sequence[str]) -> List[float]

**Docstring**

.. code-block:: text

   Aleatoritzar els valors d'observació.

infer_unit
~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:347``.

.. code-block:: python

   def infer_unit(var_name: str) -> str

**Docstring**

.. code-block:: text

   Infer unit.

normalize_policy_observation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:367``.

.. code-block:: python

   def normalize_policy_observation( custom_obs: Sequence[float], core_env: Any, vec_env: Any, expected_size: Optional[int] = None, ) -> np.ndarray

**Docstring**

.. code-block:: text

   Normalitza l'observació de les polítiques.

unnormalize_sinergym_action
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:400``.

.. code-block:: python

   def unnormalize_sinergym_action(action_array: Any, env_obj: Any) -> Any

**Docstring**

.. code-block:: text

   Unnormalize sinergym action.

prepare_action_display
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:410``.

.. code-block:: python

   def prepare_action_display(action: Any, vec_env: Any, core_env: Any) -> Any

**Docstring**

.. code-block:: text

   Prepara la visualització de l'acció.

extract_display_observation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:420``.

.. code-block:: python

   def extract_display_observation( obs: Any, info_dict: Dict[str, Any], obs_vars: Sequence[str], vec_env: Any, ) -> Tuple[Any, Any]

**Docstring**

.. code-block:: text

   Extreu l'observació de visualització.

extract_info_dict
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:451``.

.. code-block:: python

   def extract_info_dict(infos: Any) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Extreu el diccionari info d'un step de VecEnv o Gym.

build_history_entry
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:460``.

.. code-block:: python

   def build_history_entry( step_number: int, reward: float, info_dict: Dict[str, Any], next_obs: Any, obs_vars: Sequence[str], vec_env: Any, ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Prepara una entrada d'historial per a una acció de l'agent.

run_environment_steps
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:498``.

.. code-block:: python

   def run_environment_steps( vec_env: Any, core_env: Any, action_to_take: Any, current_step: int, repeat_n: int = 1, obs_vars: Optional[Sequence[str]] = None, ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Executa els passos de l'entorn.

find_matching_column
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/interaccionar_agent_backend.py:557``.

.. code-block:: python

   def find_matching_column(row: Dict[str, Any], keywords: Sequence[str]) -> Optional[str]

**Docstring**

.. code-block:: text

   Troba una columna compatible.

