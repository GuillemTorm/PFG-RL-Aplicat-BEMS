backend/entrenar_agent_runtime.py
=================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_runtime.py``

**Module path:** ``backend.entrenar_agent_runtime``

**Module docstring**

.. code-block:: text

   Cicle de vida d'execució per a sessions d'entrenament en directe.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``copy``, ``datetime``, ``functools``, ``gymnasium``, ``json``, ``pathlib``, ``sinergym``, ``streamlit``, ``typing``

Functions
---------

clear_training_runtime
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_runtime.py:28``.

.. code-block:: python

   def clear_training_runtime() -> None

**Docstring**

.. code-block:: text

   Neteja el temps d'execució de l'entrenament.

learn_training_chunk
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_runtime.py:48``.

.. code-block:: python

   def learn_training_chunk(model: Any, timesteps: int) -> None

**Docstring**

.. code-block:: text

   Executa un bloc d'entrenament amb la inicialització incremental pròpia de SB3.

save_training_artifacts
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_runtime.py:53``.

.. code-block:: python

   def save_training_artifacts(runtime: Dict[str, Any]) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Deseu els artefactes d'entrenament.

build_training_env_instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_runtime.py:93``.

.. code-block:: python

   def build_training_env_instance( env_id: str, reward_name: str, reward_kwargs: Dict[str, Any], meters: Dict[str, str], wrapper_configs: Sequence[Dict[str, Any]], ) -> Any

**Docstring**

.. code-block:: text

   Crea una instància d'entorn embolicat per a l'entrenament en directe.

create_training_runtime
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_runtime.py:109``.

.. code-block:: python

   def create_training_runtime( training_config: Dict[str, Any], ui_state: Dict[str, Any] | None = None, ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Crea temps d'execució de la entrenament.

