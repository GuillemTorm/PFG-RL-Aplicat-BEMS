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

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:26``.

.. code-block:: python

   def ui_text(value: object) -> str

**Docstring**

.. code-block:: text

   Retorna el text segur per a la pantalla, reparant el mojibake habitual de les metadades EPW.

build_active_month_axis
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:43``.

.. code-block:: python

   def build_active_month_axis(data_frame: pd.DataFrame) -> tuple[list[int], list[str]]

**Docstring**

.. code-block:: text

   Retorna les posicions de marca del mes que coincideixen amb les dades EPW visibles actualment.

apply_figure_style
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:60``.

.. code-block:: python

   def apply_figure_style(fig: go.Figure, title: str, *, legend: bool = True, height: int = 400) -> go.Figure

**Docstring**

.. code-block:: text

   Aplica l'estil visual compartit a una figura Plotly.

build_focus_timeseries_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:95``.

.. code-block:: python

   def build_focus_timeseries_figure(series_frame: pd.DataFrame, variable_key: str, aggregation_label: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea la sèrie temporal agregada per a la variable EPW seleccionada.

build_monthly_climate_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:115``.

.. code-block:: python

   def build_monthly_climate_figure(monthly_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea la comparació mensual de temperatura i humitat.

build_monthly_solar_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:167``.

.. code-block:: python

   def build_monthly_solar_figure(monthly_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea el resum mensual de radiació solar acumulada.

build_daily_temperature_band_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:200``.

.. code-block:: python

   def build_daily_temperature_band_figure(daily_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea la banda diària de temperatura amb mínims, mitjanes i màxims.

build_hourly_profile_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:238``.

.. code-block:: python

   def build_hourly_profile_figure(hourly_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea el perfil horari mitjà de temperatura, punt de rosada i humitat.

build_heatmap_figure
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:279``.

.. code-block:: python

   def build_heatmap_figure(heatmap_frame: pd.DataFrame, variable_key: str) -> go.Figure

**Docstring**

.. code-block:: text

   Crea un mapa de calor mes a hora per a la variable EPW seleccionada.

build_annual_heatmap_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:304``.

.. code-block:: python

   def build_annual_heatmap_figure( heatmap_frame: pd.DataFrame, variable_key: str, *, tick_values: list[int] | None = None, tick_labels: list[str] | None = None, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea un mapa de calor anual hora a dia per a l'escaneig a escala del panell.

build_comfort_radiation_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:384``.

.. code-block:: python

   def build_comfort_radiation_figure(radiation_frame: pd.DataFrame) -> go.Figure

**Docstring**

.. code-block:: text

   Crea el mapa polar de radiació amb efectes de confort per orientació.

build_monthly_wind_rose_grid_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/epw_figures.py:462``.

.. code-block:: python

   def build_monthly_wind_rose_grid_figure(monthly_rose_tables: dict[str, pd.DataFrame]) -> go.Figure

**Docstring**

.. code-block:: text

   Construeix una graella compacta de roses dels vents mensuals.

