backend/entrenar_agent_charts.py
================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_charts.py``

**Module path:** ``backend.entrenar_agent_charts``

**Module docstring**

.. code-block:: text

   Gràfics d'entrenament en directe per a la pàgina d'entrenament de l'agent.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``os``, ``pandas``, ``pathlib``, ``streamlit``

Functions
---------

_get_workspace_from_runtime
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_charts.py:16``.

.. code-block:: python

   def _get_workspace_from_runtime(runtime: dict) -> str | None

**Docstring**

.. code-block:: text

   Extreu el workspace_path del VecEnv actiu.

   Intenta tres estratègies per ordre de preferència:
   1. ``VecEnv.get_attr`` (travessa la cadena de wrappers Gymnasium).
   2. ``model.env.get_attr`` (accés directe a l'entorn intern del model).
   3. Exploració de CWD per trobar directoris que coincideixin amb ``{env_id}-res*`` (retrocés).

   Retorna:
       Camí absolut a l'espai de treball com a cadena, o ``None`` si no
       l'estratègia té èxit.

render_live_training_charts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_charts.py:61``.

.. code-block:: python

   def render_live_training_charts() -> None

**Docstring**

.. code-block:: text

   Mostra els gràfics d'evolució per episodi llegint ``progress.csv``.

   Llegeix ``progress.csv`` de l'espai de treball actiu i en mostra tres
   subgràfics (recompensa, infracció de temperatura i demanda d'energia). Si no
   l'episodi encara s'ha completat, es mostra un missatge d'espera.

