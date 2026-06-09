backend/grafics/data_loader.py
==============================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/data_loader.py``

**Module path:** ``backend.grafics.data_loader``

**Module docstring**

.. code-block:: text

   Carrega i normalitza els fitxers CSV de resultats per a panells i informes.

   La pàgina de resultats i el backend de l'informe passen per aquí per llegir el progrés de Sinergym,
   arreglar buits de mètriques habituals, estandarditzar noms de columnes i retornar DataFrames preparats
   per generar KPIs i figures Plotly.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``backend``, ``functools``, ``pandas``, ``pathlib``

Functions
---------

_csv_signature
~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:50``.

.. code-block:: python

   def _csv_signature(path: str | Path) -> tuple[str, int, int]

**Docstring**

.. code-block:: text

   Retorna una clau de memòria cau que canvia quan canvia el fitxer CSV.

_read_csv_cached
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:59``.

.. code-block:: python

   def _read_csv_cached( path: str, mtime_ns: int, size: int, mode: str, names: tuple[str, ...], ) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Llegeix un fitxer CSV mitjançant una memòria cau en procés conscient de mtime.

_read_csv
~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:76``.

.. code-block:: python

   def _read_csv(path: str | Path, *, mode: str = "default", names: tuple[str, ...] = ()) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Llegeix un fitxer CSV i en retorna una còpia segura per mutar.

_fill_missing_or_zero
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:83``.

.. code-block:: python

   def _fill_missing_or_zero(target: pd.Series, replacement: pd.Series) -> pd.Series

**Docstring**

.. code-block:: text

   Ompliu els valors objectiu que falten o zero amb una sèrie de substitució numèrica.

_repair_power_metrics_from_progress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:96``.

.. code-block:: python

   def _repair_power_metrics_from_progress(progress: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Repareu les mètriques de potència de progrés quan només hi hagi valors acumulatius o mitjans.

_drop_repeated_header_rows
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:134``.

.. code-block:: python

   def _drop_repeated_header_rows(data: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Elimina capçaleres CSV repetides accidentalment dins dels fitxers de registre.

_coerce_progress_numeric_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:150``.

.. code-block:: python

   def _coerce_progress_numeric_columns(progress: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Converteix les mètriques de progrés conegudes en valors numèrics.

load_data
~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/data_loader.py:160``.

.. code-block:: python

   def load_data(progress_path, obs_path)

**Docstring**

.. code-block:: text

   Carrega els fitxers de progrés i observació CSV utilitzats pel panell de resultats.

