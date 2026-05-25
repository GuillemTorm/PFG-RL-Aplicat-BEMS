backend/epw_figures.py
======================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/epw_figures.py``

**Module path:** ``backend.epw_figures``

**Module docstring**

.. code-block:: text

   Plotly creadors de figures per al visor de clima EPW.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``math``, ``pandas``, ``plotly``

Functions
---------

ui_text
~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:27``.

.. code-block:: python

   def ui_text(value: object) -> str

**Docstring**

.. code-block:: text

   Retorna el text segur per a la pantalla, reparant el mojibake habitual de les metadades EPW.

build_active_month_axis
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:44``.

.. code-block:: python

   def build_active_month_axis(data_frame: pd.DataFrame) -> tuple[list[int], list[str]]

**Docstring**

.. code-block:: text

   Retorna les posicions de marca del mes que coincideixen amb les dades EPW visibles actualment.

apply_figure_style
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:61``.

.. code-block:: python

   def apply_figure_style(fig: go.Figure, title: str, *, legend: bool = True, height: int = 400) -> go.Figure

**Docstring**

.. code-block:: text

   Aplica l'estil visual compartit a una figura Plotly.

build_focus_timeseries_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:96``.

.. code-block:: python

   def build_focus_timeseries_figure(series_frame: pd.DataFrame, variable_key: str, aggregation_label: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea la figura de sèrie temporal agregada principal per a la variable EPW seleccionada per al flux Studio.

build_monthly_climate_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:116``.

.. code-block:: python

   def build_monthly_climate_figure(monthly_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea una figura mensual de comparació de temperatura i humitat per al flux Studio.

build_monthly_solar_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:168``.

.. code-block:: python

   def build_monthly_solar_figure(monthly_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea un gràfic de barres de radiació solar acumulada mensual per al flux Studio.

build_daily_temperature_band_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:201``.

.. code-block:: python

   def build_daily_temperature_band_figure(daily_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea la figura de la banda de temperatura diària amb valors mínims, mitjans i màxims per al flux Studio.

build_hourly_profile_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:239``.

.. code-block:: python

   def build_hourly_profile_figure(hourly_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea un perfil horari mitjà de temperatura, punt de rosada i humitat per al flux Studio.

build_heatmap_figure
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:280``.

.. code-block:: python

   def build_heatmap_figure(heatmap_frame: pd.DataFrame, variable_key: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea un mapa de calor mes a hora per a la variable EPW seleccionada.

build_annual_heatmap_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:305``.

.. code-block:: python

   def build_annual_heatmap_figure( heatmap_frame: pd.DataFrame, variable_key: str, *, tick_values: list[int] | None = None, tick_labels: list[str] | None = None, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea un mapa de calor anual hora a dia per a l'escaneig a escala del panell.

build_comfort_radiation_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:385``.

.. code-block:: python

   def build_comfort_radiation_figure(radiation_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea un gràfic de radiació polar benefici-dany per a les orientacions de façana per al flux Studio.

build_monthly_wind_rose_grid_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:463``.

.. code-block:: python

   def build_monthly_wind_rose_grid_figure(monthly_rose_tables: dict[str, pd.DataFrame]) -> go.Figure

**Docstring**

.. code-block:: text

   Construeix una graella compacta de roses dels vents mensuals.

