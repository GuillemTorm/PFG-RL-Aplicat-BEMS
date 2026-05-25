backend/grafics/heatmaps.py
===========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py``

**Module path:** ``backend.grafics.heatmaps``

**Module docstring**

.. code-block:: text

   Xifres de mapes de calor per als resums del panell global i de zona.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``numpy``, ``pandas``, ``plotly``

Functions
---------

make_heatmap
~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:15``.

.. code-block:: python

   def make_heatmap(pivot_df: pd.DataFrame, label: str) -> go.Figure

**Docstring**

.. code-block:: text

   Mapa de calor genèric donat un dataframe pivotat (Mes × Hora).

make_violation_heatmap_percent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:29``.

.. code-block:: python

   def make_violation_heatmap_percent( obs: pd.DataFrame, season: str = "All", comfort_config=None, ) -> go.Figure

**Docstring**

.. code-block:: text

   Mapa de calor (Mes x Hora) amb el % de timesteps en violacio de confort.
     - Usa temp_violation si existeix; si no, reward_kwargs o defaults.
     - Respecta filtre d'estació via months (Winter/Spring/Summer/Autumn/All).
     - Escala de color 0..100 (%).

_pretty_zone_temperature_name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:90``.

.. code-block:: python

   def _pretty_zone_temperature_name(name: str) -> str

**Docstring**

.. code-block:: text

   Retorna una etiqueta de zona llegible des d'un nom de columna de temperatura de l'aire.

_zone_temperature_columns
~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:97``.

.. code-block:: python

   def _zone_temperature_columns(obs: pd.DataFrame) -> list[tuple[str, str]]

**Docstring**

.. code-block:: text

   Detecta columnes de temperatura d'interior per zona.
   Retorna llista [(nom_zona,"colname"), …].
   Si no hi ha columnes *_air_temperature però existeix 'air_temperature',
   retorna [('All','air_temperature')].

_ensure_month_hour
~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:112``.

.. code-block:: python

   def _ensure_month_hour(df: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Assegura columnes 'month' i 'hour' a partir de l'índex temporal.

_zone_heatmap_layout
~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:122``.

.. code-block:: python

   def _zone_heatmap_layout(nrows: int, ncols: int) -> tuple[float, float, int]

**Docstring**

.. code-block:: text

   Retorna l'espai i l'alçada segurs de la subparcel·la per a edificis grans de diverses zones.

compute_zone_temperature_pivots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:133``.

.. code-block:: python

   def compute_zone_temperature_pivots( obs: pd.DataFrame, season: str = "All", agg: str = "mean" ) -> dict[str, pd.DataFrame]

**Docstring**

.. code-block:: text

   Construeix, per a cada zona, un pivot Mes×Hora amb la temperatura d'interior.
   - Respecta el filtre d'estació (via filter_by_season).
   - Reindexa sempre a mesos 1..12 i hores 0..23 (cel·les inexistents -> NaN).
   - 'agg' pot ser 'mean' o 'median'.

   Retorna: {nom_zona: DataFrame (index=1..12 mesos, columns=0..23 hores)}

make_zone_temperature_heatmaps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/heatmaps.py:168``.

.. code-block:: python

   def make_zone_temperature_heatmaps( obs: pd.DataFrame, season: str = "All", agg: str = "mean", max_cols: int = 3, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea mapes de calor de temperatura interior mensuals per hores per a cada zona.

   La figura generada utilitza una escala de colors compartida entre zones, canònica
   eixos mes/hora, el filtre de temporada seleccionat i la mitjana o la mediana
   agregació. El creador de pivot omet les dades de zones buides o incompletes.

   Paràmetres:
       obs: DataFrame d'observació.
       season: filtre de temporada: ``All``, ``Winter``, ``Spring``, ``Summer`` o
           ``Autumn``.
       agg: mètode d'agregació, ja sigui ``mean`` o ``median``.
       max_cols: nombre màxim de columnes de subgràfic.

   Retorna:
       Una figura Plotly amb un mapa de calor per zona, o un únic mapa de calor quan el
       run només conté una zona.

