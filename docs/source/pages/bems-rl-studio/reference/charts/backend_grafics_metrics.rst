backend/grafics/metrics.py
==========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/metrics.py``

**Module path:** ``backend.grafics.metrics``

**Module docstring**

.. code-block:: text

   Agrega les dades d'observació i progrés en mètriques preparades per a gràfics.

   Les funcions aquí converteixen la sortida en brut Sinergym en mensual, per hora i
   DataFrames orientats a la comoditat consumits pel panell de resultats, Plotly builders
   i informes exportats.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``backend``, ``numpy``, ``pandas``, ``typing``

Functions
---------

_price_to_eur_per_kwh
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/metrics.py:22``.

.. code-block:: python

   def _price_to_eur_per_kwh(values: pd.Series) -> pd.Series

**Docstring**

.. code-block:: text

   Normalitza els valors dels preus de l'electricitat a EUR/kWh quan semblen ser EUR/MWh.

compute_metrics
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/metrics.py:31``.

.. code-block:: python

   def compute_metrics(progress: pd.DataFrame, obs: pd.DataFrame, yaml_cfg: Optional[dict] = None) -> dict

**Docstring**

.. code-block:: text

   Calcula tots els DataFrames agregats per a figures,
   validant contra les dades disponibles i opcionalment el fitxer YAML.

