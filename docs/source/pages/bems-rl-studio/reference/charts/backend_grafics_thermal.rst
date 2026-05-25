backend/grafics/thermal.py
==========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/thermal.py``

**Module path:** ``backend.grafics.thermal``

**Module docstring**

.. code-block:: text

   Dades d'entrada de confort tèrmic: temperatura, humitat i consignes.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``pandas``, ``plotly``

Functions
---------

make_indoor_temperature_plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/thermal.py:23``.

.. code-block:: python

   def make_indoor_temperature_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Dibuixa la temperatura interior com a barres i l'exterior com una línia amb marcadors.

make_indoor_humidity_plot
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/thermal.py:127``.

.. code-block:: python

   def make_indoor_humidity_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Dibuixa la humitat interior com a barres o línies i l'exterior amb marcadors.

_with_global_setpoint_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/thermal.py:229``.

.. code-block:: python

   def _with_global_setpoint_columns(base: pd.DataFrame) -> tuple[pd.DataFrame, bool]

**Docstring**

.. code-block:: text

   Afegeix consignes globals mitjanes quan les dades venen per zona.

_build_setpoint_trace
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/thermal.py:241``.

.. code-block:: python

   def _build_setpoint_trace( base: pd.DataFrame, series_name: str, label: str, line_style: dict, mode: str, season: str, ) -> go.Scatter | None

**Docstring**

.. code-block:: text

   Crea una traça relacionada amb el punt de consigna per al mode d'agregació seleccionat.

make_setpoints_plot
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/thermal.py:265``.

.. code-block:: python

   def make_setpoints_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per als punts de consigna.

make_setpoints_vs_indoor_plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/thermal.py:292``.

.. code-block:: python

   def make_setpoints_vs_indoor_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per a punts de consigna vs interior.

