backend/grafics/hvac.py
=======================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/hvac.py``

**Module path:** ``backend.grafics.hvac``

**Module docstring**

.. code-block:: text

   HVAC xifres de consum i avaria del comptador.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``pandas``, ``plotly``

Functions
---------

_with_hvac_consumption_kwh
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/hvac.py:24``.

.. code-block:: python

   def _with_hvac_consumption_kwh(df: pd.DataFrame, hvac_col: str, unit_kind: str) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Afegeix una columna temporal amb el consum HVAC per timestep en kWh.

make_hvac_consumption_plot
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/hvac.py:37``.

.. code-block:: python

   def make_hvac_consumption_plot( obs: pd.DataFrame, mode: str, season: str, *, raw_as_rate: bool = False, raw_as_line: bool = False, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per al consum de climatització.

make_hvac_meter_breakdown_plot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/hvac.py:176``.

.. code-block:: python

   def make_hvac_meter_breakdown_plot( obs: pd.DataFrame, mode: str, season: str, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per a l'avaria del comptador de climatització.

