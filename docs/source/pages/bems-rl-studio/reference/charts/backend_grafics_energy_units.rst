backend/grafics/energy_units.py
===============================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/energy_units.py``

**Module path:** ``backend.grafics.energy_units``

**Module docstring**

.. code-block:: text

   Conversions d'energia, preu i unitats de bateria per als gràfics.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``pandas``

Functions
---------

_energy_price_series_eur_per_kwh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/energy_units.py:9``.

.. code-block:: python

   def _energy_price_series_eur_per_kwh(df: pd.DataFrame, col: str) -> pd.Series

**Docstring**

.. code-block:: text

   Preu de l'energia sèrie eur per kwh.

_energy_to_kwh
~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/energy_units.py:22``.

.. code-block:: python

   def _energy_to_kwh(values: pd.Series, unit_kind: str, timestep_hours: float | None = None) -> pd.Series

**Docstring**

.. code-block:: text

   Energy to kwh.

_battery_state_display_series
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/energy_units.py:35``.

.. code-block:: python

   def _battery_state_display_series( base: pd.DataFrame, state_col: str, ) -> tuple[pd.Series, str, str]

**Docstring**

.. code-block:: text

   Retorna la sèrie de visualització, la unitat i l'etiqueta per a les sortides de l'estat de la bateria.

