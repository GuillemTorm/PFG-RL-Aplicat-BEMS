page_components/training_shared.py
==================================

**Group:** Reusable Page Components

**Source:** ``BEMS-RL-STUDIO/page_components/training_shared.py``

**Module path:** ``page_components.training_shared``

**Module docstring**

.. code-block:: text

   Constants de pàgina d'entrenament compartides i components de capçalera reutilitzables.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``html``, ``page_styles``, ``pathlib``, ``streamlit``

Functions
---------

render_training_hero
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_shared.py:29``.

.. code-block:: python

   def render_training_hero() -> None

**Docstring**

.. code-block:: text

   Mostra el bloc de capçalera principal de la pàgina a la UI de Streamlit.

render_training_section
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_shared.py:44``.

.. code-block:: python

   def render_training_section(title: str, kicker: str, description: str) -> None

**Docstring**

.. code-block:: text

   Crea la capçalera visual d'una secció de pàgina a la UI de Streamlit.

format_saved_training_label
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_shared.py:50``.

.. code-block:: python

   def format_saved_training_label(run: dict) -> str

**Docstring**

.. code-block:: text

   Retorna una etiqueta llegible per persones per a una cursa d'entrenament desada.

render_saved_training_field
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_shared.py:58``.

.. code-block:: python

   def render_saved_training_field(label: str, value: object) -> None

**Docstring**

.. code-block:: text

   Mostra un únic camp etiquetat dins de la biblioteca de entrenament desada.

render_saved_training_library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_shared.py:72``.

.. code-block:: python

   def render_saved_training_library(envs: list[str]) -> None

**Docstring**

.. code-block:: text

   Mostra la biblioteca d'entrenaments desats amb controls d'upload i download.

