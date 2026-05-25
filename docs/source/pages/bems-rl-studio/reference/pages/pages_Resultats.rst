pages/Resultats.py
==================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Resultats.py``

**Module path:** ``pages.Resultats``

**Module docstring**

.. code-block:: text

   Streamlit frontend per a la pàgina de resultats de BEMS-RL STUDIO.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``page_components``, ``page_styles``, ``pathlib``, ``sidebar_nav``, ``streamlit``

Functions
---------

build_download_filename
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Resultats.py:28``.

.. code-block:: python

   def build_download_filename(prefix: str, run_name: str) -> str

**Docstring**

.. code-block:: text

   Crea un nom de fitxer de descàrrega estable CSV per a una execució seleccionada.

render_results_page
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Resultats.py:39``.

.. code-block:: python

   def render_results_page() -> None

**Docstring**

.. code-block:: text

   Prepara la pàgina de resultats: selector d'execució, dashboard i downloads CSV.

