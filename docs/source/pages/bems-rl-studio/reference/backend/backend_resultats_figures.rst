backend/resultats_figures.py
============================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/resultats_figures.py``

**Module path:** ``backend.resultats_figures``

**Module docstring**

.. code-block:: text

   Construcció compartida de figures per al dashboard i els informes de resultats.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``dataclasses``, ``pandas``, ``plotly``

Classes
-------

ReportFigure
~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/resultats_figures.py:47``.

.. code-block:: python

   class ReportFigure

**Docstring**

.. code-block:: text

   Gràfic Plotly més la secció d'informe on hauria d'aparèixer.

Functions
---------

build_dashboard_figures
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_figures.py:135``.

.. code-block:: python

   def build_dashboard_figures( data: DashboardData, zobs: pd.DataFrame, action_data: pd.DataFrame, *, plot_mode: str, plot_season: str, comfort_scope: str, view_mode: str, real_period_kind: str, ) -> dict[str, go.Figure]

**Docstring**

.. code-block:: text

   Crea totes les figures Plotly utilitzades pel panell de resultats en línia.

overlay_dashboard_figures
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_figures.py:226``.

.. code-block:: python

   def overlay_dashboard_figures( figures: dict[str, go.Figure], comparison_figures: dict[str, go.Figure], *, data: DashboardData, view_mode: str, ) -> dict[str, go.Figure]

**Docstring**

.. code-block:: text

   Superposa traces de comparació a les figures actives del panell.

style_dashboard_figures
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_figures.py:246``.

.. code-block:: python

   def style_dashboard_figures( figures: dict[str, go.Figure], *, view_mode: str, ) -> dict[str, go.Figure]

**Docstring**

.. code-block:: text

   Aplica la semàntica comuna de Plotly a les figures del panell abans de representar-les.

build_report_figures
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_figures.py:262``.

.. code-block:: python

   def build_report_figures( data: DashboardData, zone_obs: pd.DataFrame, action_data: pd.DataFrame, *, agg_mode: str, season: str, comfort_scope: str, ) -> tuple[ReportFigure, ...]

**Docstring**

.. code-block:: text

   Prepara les figures incloses en un informe de resultats exportat.

