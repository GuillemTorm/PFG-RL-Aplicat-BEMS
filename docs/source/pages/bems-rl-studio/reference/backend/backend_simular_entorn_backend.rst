backend/simular_entorn_backend.py
=================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py``

**Module path:** ``backend.simular_entorn_backend``

**Module docstring**

.. code-block:: text

   Simulacions de referència per a execucions no controlades o basades en regles.

   La pàgina de simulació utilitza aquest backend per inspeccionar entorns registrats, executar
   episodis de referència, capturen el progrés i persisteixen la mateixa forma d'artefacte esperada
   pel panell de resultats. Això ofereix als usuaris una prova de referència abans de comparar
   agents formats.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``csv``, ``dataclasses``, ``glob``, ``gymnasium``, ``numpy``, ``os``, ``pathlib``, ``sinergym``, ``stable_baselines3``, ``time``, ``typing``

Classes
-------

EnvironmentSummary
~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:36``.

.. code-block:: python

   class EnvironmentSummary

**Docstring**

.. code-block:: text

   Descripció compacta d'un entorn Sinergym registrat.

BaselineSimulationResult
~~~~~~~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:50``.

.. code-block:: python

   class BaselineSimulationResult

**Docstring**

.. code-block:: text

   Sortides persistents i metadades d'estat per a una simulació de referència.

ScheduleBaselineReward
~~~~~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:61``.

.. code-block:: python

   class ScheduleBaselineReward(BaseReward)

**Docstring**

.. code-block:: text

   Reward zero que conserva les mètriques físiques per comparar contra agents entrenats.

**Methods**

``def __init__( self, temperature_variables: list[str] | None = None, energy_variables: list[str] | None = None, range_comfort_winter: tuple[float, float] = (20.0, 23.5), range_comfort_summer: tuple[float, float] = (23.0, 26.0), summer_start: tuple[int, int] = (6, 1), summer_final: tuple[int, int] = (9, 30), ) -> None``
**Method docstring**

.. code-block:: text

   Inicialitza la instància.

``def __call__(self, obs_dict: dict[str, float]) -> tuple[float, dict[str, float]]``
**Method docstring**

.. code-block:: text

   Executa l'objecte cridable.

``def _compute_power_demand(self, obs_dict: dict[str, float]) -> float``
**Method docstring**

.. code-block:: text

   Calcula la demanda de potència.

``def _compute_temperature_violation(self, obs_dict: dict[str, float]) -> float``
**Method docstring**

.. code-block:: text

   Calcula la violació de temperatura.

Functions
---------

list_environment_ids
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:134``.

.. code-block:: python

   def list_environment_ids() -> list[str]

**Docstring**

.. code-block:: text

   Retorna els entorns Sinergym que tenen sentit per a una línia de base de planificació.

describe_environment
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:140``.

.. code-block:: python

   def describe_environment(env_id: str) -> EnvironmentSummary

**Docstring**

.. code-block:: text

   Crea un resum compacte utilitzat per la interfície.

run_baseline_simulation
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:167``.

.. code-block:: python

   def run_baseline_simulation( env_id: str, steps_target: int, seed: int | None, should_stop: Callable[[], bool], on_progress: Callable[[int, int], None], ) -> BaselineSimulationResult

**Docstring**

.. code-block:: text

   Executa una línia de base sense control utilitzant els planificacions per defecte d'EnergyPlus.

_make_baseline_env
~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:218``.

.. code-block:: python

   def _make_baseline_env(env_id: str)

**Docstring**

.. code-block:: text

   Crea l'entorn de baseline.

_resolve_run_artifacts
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:244``.

.. code-block:: python

   def _resolve_run_artifacts(run_path: str) -> tuple[str, str]

**Docstring**

.. code-block:: text

   Retorna les sortides principals CSV de l'execució que acaba d'acabar.

_append_detailed_meter_kwh_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:257``.

.. code-block:: python

   def _append_detailed_meter_kwh_columns(observations_path: str) -> None

**Docstring**

.. code-block:: text

   Afegeix columnes detallades del comptador de kWh.

_build_baseline_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:294``.

.. code-block:: python

   def _build_baseline_reward_kwargs(env_kwargs: dict) -> dict[str, object]

**Docstring**

.. code-block:: text

   Crea kwargs de recompensa de referència.

_safe_int
~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:327``.

.. code-block:: python

   def _safe_int(value: object, *, default: int) -> int

**Docstring**

.. code-block:: text

   Safe int.

_is_within_summer
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/simular_entorn_backend.py:335``.

.. code-block:: python

   def _is_within_summer(current: tuple[int, int], start: tuple[int, int], end: tuple[int, int]) -> bool

**Docstring**

.. code-block:: text

   Is within summer.

