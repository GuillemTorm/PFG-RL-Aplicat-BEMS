backend/grafics/battery.py
==========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/battery.py``

**Module path:** ``backend.grafics.battery``

**Module docstring**

.. code-block:: text

   Dades del quadre de comandament de la bateria, la xarxa i les tarifes.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``pandas``, ``plotly``

Functions
---------

_add_battery_power_trace
~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:39``.

.. code-block:: python

   def _add_battery_power_trace( fig: go.Figure, base: pd.DataFrame, series: str | None, label: str, sign: int, mode: str, season: str, units: str, ) -> None

**Docstring**

.. code-block:: text

   Afegeix un rastre de càrrega o descàrrega a la figura de la bateria.

_add_battery_grid_bar_trace
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:69``.

.. code-block:: python

   def _add_battery_grid_bar_trace( fig: go.Figure, base: pd.DataFrame, column: str, label: str, color: str, mode: str, season: str, ) -> None

**Docstring**

.. code-block:: text

   Afegeix una traça de la barra de bateria contra la xarxa per al mode d'agregació seleccionat.

make_battery_power_plot
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:90``.

.. code-block:: python

   def make_battery_power_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per a la bateria.

make_battery_soc_plot
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:133``.

.. code-block:: python

   def make_battery_soc_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per a la bateria.

_grid_source_unit_kind
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:170``.

.. code-block:: python

   def _grid_source_unit_kind(column_name: str) -> str

**Docstring**

.. code-block:: text

   Tipus d'unitat font de la xarxa.

make_energy_price_plot
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:182``.

.. code-block:: python

   def make_energy_price_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura de Plotly per al preu de l'energia.

make_battery_vs_grid_plot
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:217``.

.. code-block:: python

   def make_battery_vs_grid_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per a la bateria i la xarxa.

make_battery_charge_with_price_plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/battery.py:265``.

.. code-block:: python

   def make_battery_charge_with_price_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per a la càrrega de la bateria amb el preu.

