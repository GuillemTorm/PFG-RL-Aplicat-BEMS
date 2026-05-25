backend/grafics/column_utils.py
===============================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/column_utils.py``

**Module path:** ``backend.grafics.column_utils``

**Module docstring**

.. code-block:: text

   Detecció de columnes disponibles per construir les figures del panell.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``pandas``

Functions
---------

_ensure_air_temperature
~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/column_utils.py:7``.

.. code-block:: python

   def _ensure_air_temperature(df: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Assegura 'air_temperature'; si no hi és, fa la mitjana de columnes *_air_temperature.

_find_first_present_column
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/column_utils.py:17``.

.. code-block:: python

   def _find_first_present_column(columns, candidates) -> str | None

**Docstring**

.. code-block:: text

   Troba la primera columna disponible.

_find_battery_state_column
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/column_utils.py:94``.

.. code-block:: python

   def _find_battery_state_column(columns) -> str | None

**Docstring**

.. code-block:: text

   Cerca la columna d'estat de la bateria.

_find_energy_price_column
~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/column_utils.py:99``.

.. code-block:: python

   def _find_energy_price_column(columns) -> str | None

**Docstring**

.. code-block:: text

   Cerqueu la columna del preu de l'energia.

