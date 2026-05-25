backend/grafics/plot_helpers.py
===============================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py``

**Module path:** ``backend.grafics.plot_helpers``

**Module docstring**

.. code-block:: text

   Helpers Plotly comuns per als gràfics agregats del dashboard.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``numpy``, ``pandas``, ``plotly``

Functions
---------

build_mode_scatter_trace
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py:21``.

.. code-block:: python

   def build_mode_scatter_trace( base: pd.DataFrame, column: str | None, mode: str, season: str, *, name: str, color: str, units: str = "", sign: float = 1.0, line_width: float = 2.4, marker_size: int = 6, trace_mode: str | None = None, hovertemplate: str | None = None, plain_hovertemplate: str | None = None, line_shape: str | None = None, fill: str | None = None, fillcolor: str | None = None, meta: str | None = None, ) -> go.Scatter | None

**Docstring**

.. code-block:: text

   Crea una traça scatter usant la mateixa agregació temporal que la resta de gràfics.

add_mode_scatter_trace
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py:78``.

.. code-block:: python

   def add_mode_scatter_trace( fig: go.Figure, base: pd.DataFrame, column: str | None, mode: str, season: str, **kwargs, ) -> go.Scatter | None

**Docstring**

.. code-block:: text

   Afegeix una traça scatter agregada a una figura si la columna existeix.

energy_series_for_mode
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py:93``.

.. code-block:: python

   def energy_series_for_mode( base: pd.DataFrame, column: str, mode: str, season: str, *, raw_hourly: bool = False, ) -> tuple[list, list, list | None] | None

**Docstring**

.. code-block:: text

   Retorna sèries d'energia kWh amb sumes coherents per mode temporal.

add_energy_bar_trace
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py:143``.

.. code-block:: python

   def add_energy_bar_trace( fig: go.Figure, base: pd.DataFrame, column: str, *, label: str, color: str, mode: str, season: str, hover_units: str = "kWh", raw_hourly: bool = False, ) -> go.Bar | None

**Docstring**

.. code-block:: text

   Afegeix barres d'energia agregades amb hover homogeni.

raw_hourly_total_series
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py:182``.

.. code-block:: python

   def raw_hourly_total_series(df: pd.DataFrame, column: str) -> tuple[list, list, list]

**Docstring**

.. code-block:: text

   Agrupa una sèrie raw en totals horaris per evitar gràfics de barres massa densos.

energy_axis_title
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py:201``.

.. code-block:: python

   def energy_axis_title(mode: str, *, raw_title: str = "Consumption per Timestep (kWh)") -> str

**Docstring**

.. code-block:: text

   Retorna el títol Y habitual per a gràfics de consum energètic.

_default_hovertemplate
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/plot_helpers.py:211``.

.. code-block:: python

   def _default_hovertemplate(units: str) -> str

**Docstring**

.. code-block:: text

   No docstring available yet.

