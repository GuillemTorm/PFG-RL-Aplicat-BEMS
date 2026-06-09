backend/grafics/kpis.py
=======================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/kpis.py``

**Module path:** ``backend.grafics.kpis``

**Module docstring**

.. code-block:: text

   Càlculs de KPI per als resums de resultats de BEMS-RL Studio.

   Aquest mòdul deriva mètriques operatives compactes a partir de les observacions
   normalitzades: desviacions de confort, consum HVAC, cost energètic i resums de
   temperatura de zona.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``backend``, ``pandas``, ``re``

Functions
---------

_normalize_name
~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/kpis.py:19``.

.. code-block:: python

   def _normalize_name(s: str) -> str

**Docstring**

.. code-block:: text

   Normalitza els noms de zona perquè coincideixin amb les columnes de manera més tolerant.

_pick_zone_temperature_series
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/kpis.py:26``.

.. code-block:: python

   def _pick_zone_temperature_series( obs: pd.DataFrame, selected_zone: str | None, ) -> pd.Series | None

**Docstring**

.. code-block:: text

   Retorna la sèrie de temperatura interior utilitzada per les targetes KPI.

_temperature_violation_frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/kpis.py:54``.

.. code-block:: python

   def _temperature_violation_frame(obs: pd.DataFrame, comfort_config=None) -> pd.DataFrame | None

**Docstring**

.. code-block:: text

   Retorna les observacions amb una infracció de confort alineada per registre.

compute_kpis
~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/kpis.py:78``.

.. code-block:: python

   def compute_kpis( obs: pd.DataFrame, cost_hourly: pd.DataFrame | None, selected_zone: str | None = None, comfort_scope: str = "all", comfort_config=None, )

**Docstring**

.. code-block:: text

   Calcula les targetes KPI mostrades al panell i exportades a PDF.

   Els KPI de temperatura respecten la zona seleccionada. HVAC i els KPI de costos segueixen sent globals.
   La desviació de confort es mostra amb una etiqueta d'abast explícita per a hores ocupades
   les recompenses no es comparen amb una mètrica de totes les hores per accident.

