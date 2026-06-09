page_components/resultats_dashboard.py
======================================

**Group:** Reusable Page Components

**Source:** ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py``

**Module path:** ``page_components.resultats_dashboard``

**Module docstring**

.. code-block:: text

   Component del panell en línia per a la pàgina de resultats.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``html``, ``pandas``, ``pathlib``, ``plotly``, ``streamlit``, ``typing``

Classes
-------

DashboardTabSpec
~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:76``.

.. code-block:: python

   class DashboardTabSpec(NamedTuple)

**Docstring**

.. code-block:: text

   Declaració d'una pestanya del dashboard i les figures que conté.

Functions
---------

_file_signature
~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:190``.

.. code-block:: python

   def _file_signature(path: str) -> tuple[str, int, int]

**Docstring**

.. code-block:: text

   Retorna una signatura de memòria cau estable per a la ruta d'un fitxer.

_run_data_signature
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:201``.

.. code-block:: python

   def _run_data_signature(progress_path: str, observations_path: str) -> tuple[object, ...]

**Docstring**

.. code-block:: text

   Retorna les entrades de memòria cau que canvien cada vegada que canvien les dades d'execució seleccionades.

_load_comparison_data_cached
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:220``.

.. code-block:: python

   def _load_comparison_data_cached(run_path: str) -> DashboardData | None

**Docstring**

.. code-block:: text

   Carrega una comparació i la desa a la memòria cau de sessió.

_cached_report_bytes
~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:235``.

.. code-block:: python

   def _cached_report_bytes( progress_path: str, observations_path: str, agg_mode: str, season: str, comfort_scope: str, zone_str: str, data_signature: tuple[object, ...], ) -> tuple[bytes, str]

**Docstring**

.. code-block:: text

   Retorna bytes d'informes a la memòria cau per als filtres del panell seleccionats.

_plot_if_available
~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:256``.

.. code-block:: python

   def _plot_if_available(fig: go.Figure | None) -> None

**Docstring**

.. code-block:: text

   Mostra un gràfic Plotly només quan conté traces visibles.

_dashboard_tab_is_visible
~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:264``.

.. code-block:: python

   def _dashboard_tab_is_visible(spec: DashboardTabSpec, figures: dict[str, go.Figure]) -> bool

**Docstring**

.. code-block:: text

   Decideix si una pestanya té dades suficients per aparèixer al dashboard.

_render_dashboard_tab_content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:273``.

.. code-block:: python

   def _render_dashboard_tab_content( spec: DashboardTabSpec, figures: dict[str, go.Figure], *, view_mode: str, ) -> None

**Docstring**

.. code-block:: text

   Pinta el contingut d'una pestanya de resultats segons la seva especificació.

_render_report_export
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:300``.

.. code-block:: python

   def _render_report_export( report_action_slot, data: DashboardData, *, plot_mode: str, plot_season: str, comfort_scope: str, zone_val: str | None, ) -> None

**Docstring**

.. code-block:: text

   Mostra els controls de generació i baixada d'informes.

_render_dashboard_tabs
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:361``.

.. code-block:: python

   def _render_dashboard_tabs(figures: dict[str, go.Figure], *, view_mode: str) -> None

**Docstring**

.. code-block:: text

   Mostra els gràfics de resultats amb la mateixa estructura de pestanyes del panell.

_build_dashboard_figures
~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:378``.

.. code-block:: python

   def _build_dashboard_figures( data: DashboardData, zobs: pd.DataFrame, action_data: pd.DataFrame, *, plot_mode: str, plot_season: str, comfort_scope: str, view_mode: str, real_period_kind: str, ) -> dict[str, go.Figure]

**Docstring**

.. code-block:: text

   Crea totes les figures Plotly utilitzades pel panell de resultats en línia.

_overlay_dashboard_figures
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:472``.

.. code-block:: python

   def _overlay_dashboard_figures( figures: dict[str, go.Figure], comparison_figures: dict[str, go.Figure], *, data: DashboardData, view_mode: str, ) -> dict[str, go.Figure]

**Docstring**

.. code-block:: text

   Superposeu traces de comparació a les xifres actives del panell.

_style_dashboard_figures
~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:492``.

.. code-block:: python

   def _style_dashboard_figures( figures: dict[str, go.Figure], *, view_mode: str, ) -> dict[str, go.Figure]

**Docstring**

.. code-block:: text

   Aplica la semàntica comuna de Plotly a les figures del panell abans de representar-les.

_kpi_delta_color
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:511``.

.. code-block:: python

   def _kpi_delta_color(key: str) -> str

**Docstring**

.. code-block:: text

   Retorna el mode de color delta utilitzat per les targetes de comparació KPI.

_render_kpis
~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:521``.

.. code-block:: python

   def _render_kpis(kpis: dict, comp_kpis: dict | None) -> None

**Docstring**

.. code-block:: text

   Pinta les targetes KPI amb deltes de comparació opcionals.

render_inline_dashboard
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/resultats_dashboard.py:589``.

.. code-block:: python

   def render_inline_dashboard( data: DashboardData, all_run_dirs: tuple, current_run_path: str, ) -> None

**Docstring**

.. code-block:: text

   Mostra el panell en línia complet per a una execució carregada a la UI de Streamlit.

