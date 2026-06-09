sidebar_nav.py
==============

**Group:** Application Entry Points

**Source:** ``BEMS-RL-STUDIO/sidebar_nav.py``

**Module path:** ``sidebar_nav``

**Module docstring**

.. code-block:: text

   Navegació lateral compartida de BEMS-RL STUDIO.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``html``, ``page_styles``, ``streamlit``

Functions
---------

configure_studio_page
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/sidebar_nav.py:43``.

.. code-block:: python

   def configure_studio_page(page_title: str, *, layout: str = "wide") -> None

**Docstring**

.. code-block:: text

   Configura una pàgina i renderitza la barra lateral compartida.

render_studio_sidebar
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/sidebar_nav.py:56``.

.. code-block:: python

   def render_studio_sidebar() -> None

**Docstring**

.. code-block:: text

   Mostra la navegació personalitzada de la barra lateral de Streamlit.

_render_section_header
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/sidebar_nav.py:83``.

.. code-block:: python

   def _render_section_header(title: str, copy_text: str) -> None

**Docstring**

.. code-block:: text

   Crea la capçalera de la secció.

_render_support_footer
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/sidebar_nav.py:95``.

.. code-block:: python

   def _render_support_footer() -> None

**Docstring**

.. code-block:: text

   Mostra el contacte al final de la barra lateral.

