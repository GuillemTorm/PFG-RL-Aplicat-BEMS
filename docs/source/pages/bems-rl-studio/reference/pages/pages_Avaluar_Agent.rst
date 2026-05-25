pages/Avaluar_Agent.py
======================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Avaluar_Agent.py``

**Module path:** ``pages.Avaluar_Agent``

**Module docstring**

.. code-block:: text

   Pàgina per avaluar un agent SB3 entrenat en un entorn Sinergym.

   Escaneja models, detecta l'entorn més probable i executa l'avaluació en segon pla
   perquè la interfície continuï responent mentre EnergyPlus treballa.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``html``, ``page_components``, ``page_styles``, ``pathlib``, ``sidebar_nav``, ``streamlit``, ``time``

Functions
---------

_key
~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Avaluar_Agent.py:42``.

.. code-block:: python

   def _key(s: str) -> str

**Docstring**

.. code-block:: text

   Key.

render_metadata_grid
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Avaluar_Agent.py:46``.

.. code-block:: python

   def render_metadata_grid(cards: list[tuple[str, list[tuple[str, str]]]]) -> None

**Docstring**

.. code-block:: text

   Mostra un resum en graella amb targetes d'alçada uniforme.

render_evaluation_runtime
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Avaluar_Agent.py:74``.

.. code-block:: python

   def render_evaluation_runtime(runtime: dict[str, object]) -> None

**Docstring**

.. code-block:: text

   Mostra el progrés i el resultat de l'avaluació activa.

render_evaluation_runtime_frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Avaluar_Agent.py:112``.

.. code-block:: python

   def render_evaluation_runtime_frame() -> None

**Docstring**

.. code-block:: text

   Manté sincronitzat el bloc d'estat amb el runtime en segon pla.

