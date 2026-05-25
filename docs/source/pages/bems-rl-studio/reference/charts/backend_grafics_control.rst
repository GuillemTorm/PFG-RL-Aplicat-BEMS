backend/grafics/control.py
==========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/control.py``

**Module path:** ``backend.grafics.control``

**Module docstring**

.. code-block:: text

   Figures de control i acciÃ³ per a HVAC i pistes de terra radiant.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``pandas``, ``plotly``

Functions
---------

_mean_series
~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/control.py:18``.

.. code-block:: python

   def _mean_series(base: pd.DataFrame, columns: list[str]) -> pd.Series

**Docstring**

.. code-block:: text

   Retorna la mitjana numÃ¨rica per files per a les columnes seleccionades.

_add_radiant_control_trace
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/control.py:24``.

.. code-block:: python

   def _add_radiant_control_trace( fig: go.Figure, base: pd.DataFrame, series_name: str, label: str, secondary_y: bool, suffix: str, mode: str, season: str, ) -> None

**Docstring**

.. code-block:: text

   Afegeix un traça de control radiant a la figura.

_pretty_action_name
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/control.py:57``.

.. code-block:: python

   def _pretty_action_name(column_name: str) -> str

**Docstring**

.. code-block:: text

   Retorna una etiqueta de visualitzaciÃ³ per a una columna d'acciÃ³.

_add_agent_action_trace
~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/control.py:62``.

.. code-block:: python

   def _add_agent_action_trace( fig: go.Figure, base: pd.DataFrame, column: str, row: int, color: str, temp_columns: list[str], mode: str, season: str, ) -> None

**Docstring**

.. code-block:: text

   Afegeix un rastre d'acciÃ³ a la figura d'acciÃ³ de diverses files.

make_radiant_control_plot
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/control.py:98``.

.. code-block:: python

   def make_radiant_control_plot(obs: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per al control radiant.

make_agent_actions_plot
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/control.py:147``.

.. code-block:: python

   def make_agent_actions_plot(actions: pd.DataFrame, mode: str, season: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura Plotly per a les accions de l'agent.

