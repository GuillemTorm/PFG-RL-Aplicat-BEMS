backend/grafics/comfort.py
==========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/comfort.py``

**Module path:** ``backend.grafics.comfort``

**Module docstring**

.. code-block:: text

   Compliment de la comoditat i xifres d'incompliment de la temperatura.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``numpy``, ``pandas``, ``plotly``

Functions
---------

_violation_marker
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:29``.

.. code-block:: python

   def _violation_marker(color=None) -> dict

**Docstring**

.. code-block:: text

   Retorna el marcador comú de barres de violació tèrmica.

_add_violation_bar
~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:37``.

.. code-block:: python

   def _add_violation_bar(fig: go.Figure, *, x, y, name: str, color=None) -> None

**Docstring**

.. code-block:: text

   Afegeix una barra de violació amb el mateix estil visual.

_extract_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:48``.

.. code-block:: python

   def _extract_reward_kwargs(config) -> dict

**Docstring**

.. code-block:: text

   Extreu kwargs de recompensa.

_coerce_pair
~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:78``.

.. code-block:: python

   def _coerce_pair(value, default_pair)

**Docstring**

.. code-block:: text

   Converteix una parella de valors.

_coerce_month_day
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:88``.

.. code-block:: python

   def _coerce_month_day(value, default_pair)

**Docstring**

.. code-block:: text

   Converteix una parella de mes i dia.

_comfort_bounds_from_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:98``.

.. code-block:: python

   def _comfort_bounds_from_reward_kwargs(df: pd.DataFrame, comfort_config=None)

**Docstring**

.. code-block:: text

   Retorna els límits de comoditat de reward_kwargs. Els punts de consigna del termòstat són controls,
   no són criteris de confort, de manera que aquí no s'utilitzen intencionadament.

_categorize_comfort
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:141``.

.. code-block:: python

   def _categorize_comfort(df: pd.DataFrame, comfort_config=None) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Afegeix:
     - air_temperature (si cal)
     - month/hour (si cal)
     - comfort_cat: 'Massa fred' | 'En confort' | 'Massa calor'

_ensure_temp_violation_column
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:200``.

.. code-block:: python

   def _ensure_temp_violation_column(df: pd.DataFrame, comfort_config=None) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Assegura una columna `temp_violation` per pas de temps.

   Utilitza el valor del monitor quan existeix. En cas contrari, deriva la violació de
   reward_kwargs rangs de comoditat, tornant als rangs predeterminats de Sinergym.
   Els punts de consigna del termòstat són controls i no s'utilitzen intencionadament aquí.

make_comfort_compliance
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:231``.

.. code-block:: python

   def make_comfort_compliance( obs: pd.DataFrame, mode: str, season: str, comfort_scope: str = "all", comfort_config=None, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea el gràfic de percentatge d'hores dins el rang de confort.

make_violation_bars
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:307``.

.. code-block:: python

   def make_violation_bars( obs: pd.DataFrame, mode: str, season: str, comfort_scope: str = "all", comfort_config=None, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea el gràfic de barres de desviació de confort.

_fix_colors_for_visibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:362``.

.. code-block:: python

   def _fix_colors_for_visibility(fig, *, kind: str, mode: str)

**Docstring**

.. code-block:: text

   Aplica colors/contorns més marcats a barres en 'daily' i 'raw'.
   kind: 'violation' | 'hvac' | qualsevol altre (ignora).

make_violation_single_line
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort.py:388``.

.. code-block:: python

   def make_violation_single_line( obs: pd.DataFrame, mode: str, season: str, comfort_config=None, ) -> go.Figure

**Docstring**

.. code-block:: text

   Crea la línia de desviació de temperatura.

