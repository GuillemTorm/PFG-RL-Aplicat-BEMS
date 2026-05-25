backend/grafics/observation_columns.py
======================================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/observation_columns.py``

**Module path:** ``backend.grafics.observation_columns``

**Module docstring**

.. code-block:: text

   Utilitats de normalització de columnes per a fitxers d'observació Sinergym.

   Els entorns Sinergym i les configuracions personalitzades poden emetre comptadors equivalents
   sota diferents noms o unitats. Aquest mòdul centralitza els àlies, HVAC energia
   conversió i creació de columnes normalitzades perquè tots els gràfics llegeixin igual
   camps canònics.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``pandas``, ``typing``

Functions
---------

find_first_available_column
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/observation_columns.py:118``.

.. code-block:: python

   def find_first_available_column( columns: Iterable[str], candidates: Iterable[str] ) -> str | None

**Docstring**

.. code-block:: text

   Cerqueu la primera columna disponible.

normalize_observation_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/observation_columns.py:129``.

.. code-block:: python

   def normalize_observation_columns(obs: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Normalitza les columnes d'observació.

find_hvac_consumption_source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/observation_columns.py:141``.

.. code-block:: python

   def find_hvac_consumption_source(columns: Iterable[str]) -> tuple[str, str] | None

**Docstring**

.. code-block:: text

   Retorna la millor font de consum HVAC i el seu tipus d'unitat.

   EnergyPlus els comptadors informen l'energia per pas de temps en Joules, mentre que el
   La variable de sortida de la taxa de demanda informa de la potència en watts.

convert_hvac_source_to_kwh
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/observation_columns.py:169``.

.. code-block:: python

   def convert_hvac_source_to_kwh( values: pd.Series, unit_kind: str, timestep_hours: float | None = None, ) -> pd.Series

**Docstring**

.. code-block:: text

   Convertir la font d'HVAC a kwh.

add_meter_kwh_columns
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/observation_columns.py:184``.

.. code-block:: python

   def add_meter_kwh_columns(obs: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Afegeix columnes derivades de kWh per a les sortides conegudes del comptador EnergyPlus en Joules.

