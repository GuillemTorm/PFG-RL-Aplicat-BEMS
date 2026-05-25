backend/grafics/style.py
========================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/style.py``

**Module path:** ``backend.grafics.style``

**Module docstring**

.. code-block:: text

   Estil Plotly compartit per a les figures del panell BEMS-RL Studio.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``numpy``, ``plotly``

Functions
---------

pick_semantic_trace_color
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/style.py:47``.

.. code-block:: python

   def pick_semantic_trace_color( trace_name: str | None, *, reference: bool = False, fallback: str | None = None, ) -> str

**Docstring**

.. code-block:: text

   Retorna un color semàntic segons el nom de la traça.

_alpha_color
~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/style.py:98``.

.. code-block:: python

   def _alpha_color(hex_color: str, alpha: float = 0.30) -> str

**Docstring**

.. code-block:: text

   Converteix un color hex a rgba amb transparència.

_apply_figure_theme
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/style.py:104``.

.. code-block:: python

   def _apply_figure_theme(fig: go.Figure, *, heatmap: bool = False) -> go.Figure

**Docstring**

.. code-block:: text

   Aplica un estil més contrastat i homogeni a les figures.

style_figure_semantics
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/style.py:144``.

.. code-block:: python

   def style_figure_semantics(fig: go.Figure) -> go.Figure

**Docstring**

.. code-block:: text

   Recolora traces segons la seva semàntica i aplica el tema comú.

