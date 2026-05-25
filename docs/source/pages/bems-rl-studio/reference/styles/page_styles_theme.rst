page_styles/theme.py
====================

**Group:** Page Style Modules

**Source:** ``BEMS-RL-STUDIO/page_styles/theme.py``

**Module path:** ``page_styles.theme``

**Module docstring**

.. code-block:: text

   Tema visual compartit per donar coherència a les pàgines de BEMS-RL STUDIO.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``streamlit``, ``textwrap``

Functions
---------

build_pydeck_tooltip
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_styles/theme.py:16``.

.. code-block:: python

   def build_pydeck_tooltip(tooltip_html: str, *, variant: str = "location") -> dict[str, object]

**Docstring**

.. code-block:: text

   Prepara la configuració visual dels tooltips de mapes pydeck.

inject_studio_theme
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_styles/theme.py:23``.

.. code-block:: python

   def inject_studio_theme(*, max_width: int = 1220, hide_first_heading: bool = False) -> None

**Docstring**

.. code-block:: text

   Injecteu el tema compartit Streamlit utilitzat a BEMS-RL STUDIO.

