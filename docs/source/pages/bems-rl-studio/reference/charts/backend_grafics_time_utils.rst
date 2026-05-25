backend/grafics/time_utils.py
=============================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/time_utils.py``

**Module path:** ``backend.grafics.time_utils``

**Module docstring**

.. code-block:: text

   Filtrat temporal i ajuda d'eix per a figures del panell.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``numpy``, ``pandas``

Functions
---------

_bounded_int_series
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:11``.

.. code-block:: python

   def _bounded_int_series( df: pd.DataFrame, column: str, lower: int, upper: int, ) -> pd.Series

**Docstring**

.. code-block:: text

   Retorna una sèrie entera anul·lable amb valors temporals impossibles eliminats.

_coerce_temporal_parts
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:24``.

.. code-block:: python

   def _coerce_temporal_parts(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]

**Docstring**

.. code-block:: text

   Retorna les columnes mes/dia/hora netejades per a la reconstrucció de data i hora.

sanitize_observation_time_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:33``.

.. code-block:: python

   def sanitize_observation_time_columns(df: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Converteix les columnes d'observació temporal i emmascarar valors físicament impossibles.

_infer_timestep_hours
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:48``.

.. code-block:: python

   def _infer_timestep_hours(df: pd.DataFrame) -> float

**Docstring**

.. code-block:: text

   Infereix la durada del timestep en hores a partir del temps disponible.

_seasonal_marker_colors
~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:89``.

.. code-block:: python

   def _seasonal_marker_colors( x_vals: list[int], season: str, *, active_color: str, muted_color: str | None = None, ) -> list[str]

**Docstring**

.. code-block:: text

   Seasonal marker colors.

_season_months
~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:103``.

.. code-block:: python

   def _season_months(name: str)

**Docstring**

.. code-block:: text

   Season months.

_ensure_datetime_index
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:114``.

.. code-block:: python

   def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Garanteix un DatetimeIndex per reagrupar per hores/dies/mesos.
   Si no hi ha 'datetime' ni 'timestamp', reconstrueix un índex sintètic
   coherent amb els timesteps de 15 minuts del projecte.

_month_series
~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:191``.

.. code-block:: python

   def _month_series(df: pd.DataFrame) -> pd.Series

**Docstring**

.. code-block:: text

   Sèrie 'mes' canònica 1..12:
     - Prioritza columna 'month' si existeix (normalitza possibles 0/13).
     - Si no, usa el DatetimeIndex.

_hour_series
~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:207``.

.. code-block:: python

   def _hour_series(df: pd.DataFrame) -> pd.Series

**Docstring**

.. code-block:: text

   Sèrie 'hora' canònica 0..23:
     - Prioritza columna 'hour' si existeix (normalitza 24→0).
     - Si no, usa el DatetimeIndex.

filter_by_season
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:222``.

.. code-block:: python

   def filter_by_season(df: pd.DataFrame, season: str) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Filtra per estació amb la sèrie de mesos canònica.

_get_outdoor_temperature_series
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:231``.

.. code-block:: python

   def _get_outdoor_temperature_series(df: pd.DataFrame) -> pd.Series | None

**Docstring**

.. code-block:: text

   Retorna la columna de temperatura exterior utilitzada per les observacions generades.

_has_mdh
~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:239``.

.. code-block:: python

   def _has_mdh(df: pd.DataFrame) -> bool

**Docstring**

.. code-block:: text

   Té columnes month/day_of_month/hour del CSV?

_canon_day_series
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:244``.

.. code-block:: python

   def _canon_day_series(df: pd.DataFrame, col: str)

**Docstring**

.. code-block:: text

   Retorna (x, y, hover) per a una sèrie agregada DIÀRIA sense anys:
     - Si hi ha columnes 'month' i 'day_of_month', fa mean per (MM,DD).
     - Si només hi ha DatetimeIndex, resample('D') i mitjana per (MM,DD) (uneix anys).
   Sempre torna UNA observació per MM-DD i X=1..365.

_canon_day_total_series
~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:287``.

.. code-block:: python

   def _canon_day_total_series(df: pd.DataFrame, col: str)

**Docstring**

.. code-block:: text

   Retorna (x, y, hover) per a totals diaris en un eix canònic MM-DD.

_raw_axis_data
~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:312``.

.. code-block:: python

   def _raw_axis_data(df: pd.DataFrame, col: str)

**Docstring**

.. code-block:: text

   X=1..N (pas), hover='MM-DD HHh' si es pot.

_mode_axis_config
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:335``.

.. code-block:: python

   def _mode_axis_config(mode: str) -> tuple[str, dict]

**Docstring**

.. code-block:: text

   Retorna el títol i la configuració d'eix X per al mode temporal.

_apply_mode_xaxis
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:346``.

.. code-block:: python

   def _apply_mode_xaxis(fig, mode: str, **kwargs)

**Docstring**

.. code-block:: text

   Aplica a una figura Plotly l'eix X habitual del mode temporal.

_series_for_mode
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:353``.

.. code-block:: python

   def _series_for_mode( base: pd.DataFrame, column: str, mode: str, season: str, *, sign: float = 1.0, ) -> tuple[list, list, list | None, str] | None

**Docstring**

.. code-block:: text

   Retorna dades x/y/hover/trace-mode per a una sèrie mitjana segons el mode.

_auto_scale_series
~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/time_utils.py:398``.

.. code-block:: python

   def _auto_scale_series(dfcol: pd.Series)

**Docstring**

.. code-block:: text

   Retorna sèrie escalada i sufix ('', '×1e3', '×1e6', '×1e9').

