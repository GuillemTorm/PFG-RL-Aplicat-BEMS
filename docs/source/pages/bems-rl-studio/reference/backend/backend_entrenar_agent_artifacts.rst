backend/entrenar_agent_artifacts.py
===================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py``

**Module path:** ``backend.entrenar_agent_artifacts``

**Module docstring**

.. code-block:: text

   Rutes d'artefacte d'entrenament, metadades i postprocessament CSV.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``copy``, ``csv``, ``json``, ``os``, ``pathlib``, ``re``, ``typing``

Functions
---------

sanitize_training_name_component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:21``.

.. code-block:: python

   def sanitize_training_name_component(value: str) -> str

**Docstring**

.. code-block:: text

   Higienitzar el component del nom de la entrenament.

get_training_artifacts_root
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:27``.

.. code-block:: python

   def get_training_artifacts_root(base_path: Path | None = None) -> Path

**Docstring**

.. code-block:: text

   Retorna l'arrel dels artefactes d'entrenament.

build_training_artifact_paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:32``.

.. code-block:: python

   def build_training_artifact_paths( training_config: Dict[str, Any], base_path: Path | None = None, ) -> Dict[str, Path | str]

**Docstring**

.. code-block:: text

   Calcula les rutes dels artefactes d'una sessió d'entrenament.

append_detailed_meter_kwh_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:65``.

.. code-block:: python

   def append_detailed_meter_kwh_columns(observations_path: str | Path) -> None

**Docstring**

.. code-block:: text

   Afegeix columnes detallades del comptador de kWh.

append_detailed_meter_kwh_columns_in_workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:110``.

.. code-block:: python

   def append_detailed_meter_kwh_columns_in_workspace(workspace_path: str | Path | None) -> None

**Docstring**

.. code-block:: text

   Afegeix columnes detallades del comptador de kWh a l'espai de treball.

get_runtime_workspace_path
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:126``.

.. code-block:: python

   def get_runtime_workspace_path(runtime: Dict[str, Any]) -> str | None

**Docstring**

.. code-block:: text

   Retorna la ruta de l'espai de treball en temps d'execució.

build_training_ui_state
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:168``.

.. code-block:: python

   def build_training_ui_state(options: Dict[str, Any]) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Prepara l'estat inicial de la interfície d'entrenament.

list_saved_training_runs
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_artifacts.py:178``.

.. code-block:: python

   def list_saved_training_runs(base_path: Path | None = None) -> List[Dict[str, Any]]

**Docstring**

.. code-block:: text

   Llista les sessions d'entrenament desades.

