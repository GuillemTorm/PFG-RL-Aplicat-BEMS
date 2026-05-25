backend/grafics/episode.py
==========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/episode.py``

**Module path:** ``backend.grafics.episode``

**Module docstring**

.. code-block:: text

   Xifres del quadre de comandament a nivell d'episodi.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``numpy``, ``pandas``, ``plotly``

Functions
---------

_resolve_episode_mean_power
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/episode.py:12``.

.. code-block:: python

   def _resolve_episode_mean_power(progress: pd.DataFrame) -> pd.Series | None

**Docstring**

.. code-block:: text

   Resol la potència mitjana de l'episodi.

make_episode_metrics
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/episode.py:44``.

.. code-block:: python

   def make_episode_metrics(progress: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Mètriques d'episodi amb 3 subtrames:
   1) Recompensa
   2) Violació de la temperatura
   3) Demanda mitjana de potència

