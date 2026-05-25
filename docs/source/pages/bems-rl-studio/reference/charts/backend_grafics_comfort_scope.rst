backend/grafics/comfort_scope.py
================================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/comfort_scope.py``

**Module path:** ``backend.grafics.comfort_scope``

**Module docstring**

.. code-block:: text

   Filtres d'abast de confort compartits per KPI, gràfics i informes.

   Aquest fitxer decideix si una mètrica de confort s'ha de calcular sobre totes les hores o només sobre
   les hores amb ocupació, i manté el mateix criteri al dashboard i als informes descarregables.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``pandas``, ``typing``

Functions
---------

derive_occupied_mask
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort_scope.py:14``.

.. code-block:: python

   def derive_occupied_mask(obs: pd.DataFrame) -> Optional[pd.Series]

**Docstring**

.. code-block:: text

   Inferir una màscara booleana per als registres ocupats quan les dades ho proporcionen.

has_occupied_data
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort_scope.py:48``.

.. code-block:: python

   def has_occupied_data(obs: pd.DataFrame) -> bool

**Docstring**

.. code-block:: text

   Retorna si les observacions contenen prou dades d'ocupació per filtrar per àmbit.

filter_by_comfort_scope
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort_scope.py:53``.

.. code-block:: python

   def filter_by_comfort_scope(obs: pd.DataFrame, comfort_scope: str) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna totes les files o només les files ocupades en funció de l'àmbit seleccionat.

comfort_scope_label
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/comfort_scope.py:64``.

.. code-block:: python

   def comfort_scope_label(comfort_scope: str) -> str

**Docstring**

.. code-block:: text

   Retorna l'etiqueta de visualització associada a un identificador d'abast de confort.

