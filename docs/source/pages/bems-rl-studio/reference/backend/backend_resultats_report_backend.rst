backend/resultats_report_backend.py
===================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/resultats_report_backend.py``

**Module path:** ``backend.resultats_report_backend``

**Module docstring**

.. code-block:: text

   Generació d'informes HTML i PDF per a les execucions de Studio completades.

   El backend de l'informe comparteix els carregadors del panell de resultats i la figura Plotly
   builders, després organitza els gràfics disponibles en un document estructurat. Figures
   sense dades utilitzables es salten, de manera que els informes exportats reflecteixen els artefactes
   produït realment per una tirada.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``base64``, ``dataclasses``, ``datetime``, ``html``, ``math``, ``numbers``, ``page_styles``, ``pdfkit``, ``plotly``

Classes
-------

ReportFigure
~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:63``.

.. code-block:: python

   class ReportFigure

**Docstring**

.. code-block:: text

   Plotly gràfic més la secció d'informe on hauria d'aparèixer.

Functions
---------

generate_report_bytes
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:71``.

.. code-block:: python

   def generate_report_bytes( progress_path: str, observations_path: str, agg_mode: str, season: str, comfort_scope: str, zone_str: str, ) -> tuple[bytes, str]

**Docstring**

.. code-block:: text

   Crea un informe que es pot descarregar per a una execució completada.

   La funció retorna PDF bytes quan ``pdfkit`` i ``wkhtmltopdf`` són
   disponible. Si la representació estàtica PDF no està disponible, retorna un informe HTML
   amb el mateix contingut perquè UI encara pugui oferir una exportació completa.

_build_report_figures
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:121``.

.. code-block:: python

   def _build_report_figures( data: DashboardData, zone_obs, action_data, agg_mode: str, season: str, comfort_scope: str, ) -> tuple[ReportFigure, ...]

**Docstring**

.. code-block:: text

   Prepara les figures incloses en un informe de resultats exportat.

_render_report_document
~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:267``.

.. code-block:: python

   def _render_report_document( data: DashboardData, kpis: dict, figures: tuple[ReportFigure, ...], agg_mode: str, season: str, selected_zone: str | None, comfort_scope: str, ) -> tuple[bytes, str]

**Docstring**

.. code-block:: text

   Genera l'informe HTML i el converteix a PDF quan pdfkit està disponible.

_format_kpi_value
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:383``.

.. code-block:: python

   def _format_kpi_value(key: str, value) -> str

**Docstring**

.. code-block:: text

   Formata els valors KPI de manera coherent per a l'informe exportat.

_render_report_figures
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:398``.

.. code-block:: python

   def _render_report_figures( figures: tuple[ReportFigure, ...], ) -> tuple[list[str], int, bool]

**Docstring**

.. code-block:: text

   Retorna fragments seccionats de HTML per a cada figura d'informe amb dades visibles.

_render_single_report_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:440``.

.. code-block:: python

   def _render_single_report_figure( item: ReportFigure, *, include_plotlyjs: bool, ) -> tuple[str | None, bool, bool]

**Docstring**

.. code-block:: text

   Converteix una figura a imatge estàtica o, si cal, a HTML interactiu.

_prepare_export_figure
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_report_backend.py:473``.

.. code-block:: python

   def _prepare_export_figure(fig: go.Figure) -> go.Figure

**Docstring**

.. code-block:: text

   Copia i normalitzeu una figura Plotly per a la representació d'informes.

