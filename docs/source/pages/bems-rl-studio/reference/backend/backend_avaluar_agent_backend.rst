backend/avaluar_agent_backend.py
================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py``

**Module path:** ``backend.avaluar_agent_backend``

**Module docstring**

.. code-block:: text

   Temps d'execució d'avaluació asíncrona per a agents Studio entrenats.

   L'avaluació es pot executar per a molts passos de simulació, de manera que aquest backend aïlla el
   bucle d'execució, cua de progrés i estat de cancel·lació des de la pàgina Streamlit. Això
   també centralitza la càrrega de models, la creació d'entorns i la validació de l'espai d'acció
   de manera que el control i l'avaluació en directe segueixen el mateix contracte.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``dataclasses``, ``functools``, ``gymnasium``, ``numpy``, ``pathlib``, ``queue``, ``sinergym``, ``stable_baselines3``, ``streamlit``, ``threading``, ``time``, ``traceback``, ``typing``

Classes
-------

EvaluationResult
~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:50``.

.. code-block:: python

   class EvaluationResult

**Docstring**

.. code-block:: text

   Resum de resultats d'una execució d'un treballador d'avaluació.

Functions
---------

push_evaluation_progress
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:57``.

.. code-block:: python

   def push_evaluation_progress( event_queue: "queue.Queue[Dict[str, Any]]", job_config: Dict[str, Any], step_number: int, total_steps: int, ) -> None

**Docstring**

.. code-block:: text

   Envieu un esdeveniment de progrés d'avaluació a la cua d'execució.

build_evaluation_env
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:75``.

.. code-block:: python

   def build_evaluation_env( env_id: str, gym_kwargs: Dict[str, Any], model_action_space: Any, wrapper_configs: Optional[List[Dict[str, Any]]], ) -> Any

**Docstring**

.. code-block:: text

   Crea un entorn embolicat per a una execució d'avaluació d'agent.

empty_evaluation_runtime
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:89``.

.. code-block:: python

   def empty_evaluation_runtime() -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Temps d'execució d'avaluació buit.

ensure_evaluation_runtime
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:111``.

.. code-block:: python

   def ensure_evaluation_runtime() -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Assegura el temps d'execució de l'avaluació.

reset_evaluation_runtime
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:118``.

.. code-block:: python

   def reset_evaluation_runtime() -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Restableix el temps d'execució de l'avaluació.

push_evaluation_event
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:129``.

.. code-block:: python

   def push_evaluation_event(event_queue: "queue.Queue[Dict[str, Any]]", payload: Dict[str, Any]) -> None

**Docstring**

.. code-block:: text

   Esdeveniment d'avaluació push.

evaluation_worker
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:134``.

.. code-block:: python

   def evaluation_worker( job_config: Dict[str, Any], event_queue: "queue.Queue[Dict[str, Any]]", stop_event: threading.Event, ) -> None

**Docstring**

.. code-block:: text

   Executa l'avaluació en segon pla.

drain_evaluation_runtime
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:166``.

.. code-block:: python

   def drain_evaluation_runtime(runtime: Dict[str, Any]) -> None

**Docstring**

.. code-block:: text

   Temps d'execució de l'avaluació del buidatge.

sync_evaluation_runtime
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:216``.

.. code-block:: python

   def sync_evaluation_runtime() -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Sincronitza el temps d'execució de l'avaluació.

consume_evaluation_runtime_rerun_flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:223``.

.. code-block:: python

   def consume_evaluation_runtime_rerun_flag(runtime: Optional[Dict[str, Any]] = None) -> bool

**Docstring**

.. code-block:: text

   Indicador de reexecució del clima d'execució de l'avaluació.

request_evaluation_stop
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:232``.

.. code-block:: python

   def request_evaluation_stop(runtime: Optional[Dict[str, Any]] = None) -> bool

**Docstring**

.. code-block:: text

   Sol·licitar l'aturada de l'avaluació.

start_evaluation_run
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:244``.

.. code-block:: python

   def start_evaluation_run(request: Dict[str, Any]) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Iniciar l'execució d'avaluació.

apply_evaluation_action_contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:312``.

.. code-block:: python

   def apply_evaluation_action_contract( env: gym.Env, model_action_space: Any, wrapper_configs: List[Dict[str, Any]], ) -> gym.Env

**Docstring**

.. code-block:: text

   Aplica contracte d'acció d'avaluació.

validate_action_contract
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:327``.

.. code-block:: python

   def validate_action_contract(model_action_space: Any, env_action_space: Any, metadata: Dict[str, Any]) -> None

**Docstring**

.. code-block:: text

   Validació del contracte d'actuació.

make_env
~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:332``.

.. code-block:: python

   def make_env(env_id: str, seed: int = 0, gym_kwargs: Optional[Dict[str, Any]] = None) -> gym.Env

**Docstring**

.. code-block:: text

   Crea l'entorn utilitzat durant l'avaluació.

run_agent_evaluation
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/avaluar_agent_backend.py:339``.

.. code-block:: python

   def run_agent_evaluation( model_path: Path, env_id: str, use_vecnorm: bool, vecnorm_path: Optional[Path], steps_target: int, deterministic: bool, should_stop: Callable[[], bool], on_progress: Callable[[int, int], None], override_wrapper_configs: Optional[List[Dict[str, Any]]] = None, ) -> EvaluationResult

**Docstring**

.. code-block:: text

   Executa l'avaluació i retorna el resum d'execució.

