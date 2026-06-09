pages/Visor_Climes_EPW.py
=========================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py``

**Module path:** ``pages.Visor_Climes_EPW``

**Module docstring**

.. code-block:: text

   No docstring available yet.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``dataclasses``, ``page_components``, ``page_styles``, ``pandas``, ``sidebar_nav``, ``streamlit``

Classes
-------

EpwDashboardState
~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:46``.

.. code-block:: python

   class EpwDashboardState

**Docstring**

.. code-block:: text

   Dades preparades necessàries per representar les pestanyes del panell EPW.

Functions
---------

format_number
~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:76``.

.. code-block:: python

   def format_number(value: float | int | None, *, decimals: int = 1, suffix: str = "") -> str

**Docstring**

.. code-block:: text

   Formata un valor numèric amb separadors catalans i un sufix opcional.

data_frame_has_plot_values
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:91``.

.. code-block:: python

   def data_frame_has_plot_values( data_frame: pd.DataFrame, columns: list[str] | None = None, *, require_non_zero: bool = False, ) -> bool

**Docstring**

.. code-block:: text

   Retorna si un DataFrame conté valors numèrics que val la pena dibuixar.

wind_rose_tables_have_plot_values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:124``.

.. code-block:: python

   def wind_rose_tables_have_plot_values(monthly_rose_tables: dict[str, pd.DataFrame]) -> bool

**Docstring**

.. code-block:: text

   Indica si almenys una taula mensual de roses dels vents conté freqüències de vent.

render_detail_card
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:133``.

.. code-block:: python

   def render_detail_card( metadata: dict[str, object], selected_entry: dict[str, str], total_records: int, filtered_records: int, ) -> None

**Docstring**

.. code-block:: text

   Mostra la targeta de metadades del fitxer EPW seleccionada a la UI de Streamlit.

build_map_chart
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:167``.

.. code-block:: python

   def build_map_chart(metadata: dict[str, object]) -> None

**Docstring**

.. code-block:: text

   Dibuixa un mapa centrat a les coordenades de l'estació meteorològica EPW.

configure_epw_dashboard_page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:193``.

.. code-block:: python

   def configure_epw_dashboard_page() -> None

**Docstring**

.. code-block:: text

   Configura Chrome de la pàgina global i renderitza l'heroi EPW.

select_epw_entry
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:201``.

.. code-block:: python

   def select_epw_entry() -> tuple[dict[str, str], dict[str, object], pd.DataFrame]

**Docstring**

.. code-block:: text

   Mostra els controls de cerca i carrega el paquet EPW seleccionat.

build_metric_card_values
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:243``.

.. code-block:: python

   def build_metric_card_values(filtered_metrics: dict[str, float]) -> list[tuple[str, str]]

**Docstring**

.. code-block:: text

   Crea valors de visualització per a les targetes EPW de resum KPI.

prepare_epw_dashboard_state
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:274``.

.. code-block:: python

   def prepare_epw_dashboard_state( selected_entry: dict[str, str], metadata: dict[str, object], epw_data: pd.DataFrame, ) -> EpwDashboardState

**Docstring**

.. code-block:: text

   Crea totes les taules i etiquetes derivades necessàries per al panell EPW.

render_tab_intro
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:343``.

.. code-block:: python

   def render_tab_intro(text: str) -> None

**Docstring**

.. code-block:: text

   Mostra un text breu al començament de cada pestanya EPW.

render_annual_heatmap
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:349``.

.. code-block:: python

   def render_annual_heatmap( frame: pd.DataFrame, variable_key: str, state: EpwDashboardState, empty_message: str, *, require_non_zero: bool = False, ) -> None

**Docstring**

.. code-block:: text

   Mostra un mapa de calor anual quan la taula d'origen té valors útils.

render_epw_chart
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:372``.

.. code-block:: python

   def render_epw_chart( frame: pd.DataFrame, columns: list[str] | None, figure_builder, empty_message: str, *, require_non_zero: bool = False, ) -> None

**Docstring**

.. code-block:: text

   Mostra un gràfic EPW quan les dades tenen valors, o un avís si no.

render_overview_tab
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:393``.

.. code-block:: python

   def render_overview_tab(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Mostra la pestanya de visió general de l'EPW a la UI de Streamlit.

render_climate_dashboard_tab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:423``.

.. code-block:: python

   def render_climate_dashboard_tab(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Mostra mapes de calor climàtics anuals i gràfics d'orientació/vents.

render_comfort_radiation_chart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:465``.

.. code-block:: python

   def render_comfort_radiation_chart(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Genera un gràfic de radiació orientat a la comoditat quan hi hagi prou dades a la UI de Streamlit.

render_monthly_wind_rose_chart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:490``.

.. code-block:: python

   def render_monthly_wind_rose_chart(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Mostra les roses dels vents mensuals quan hi ha dades de vent suficients.

render_series_tab
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:505``.

.. code-block:: python

   def render_series_tab(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Mostra la pestanya de sèries temporals EPW a la UI de Streamlit.

render_patterns_tab
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:541``.

.. code-block:: python

   def render_patterns_tab(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Mostra els patrons climàtics mensuals i intradia.

render_pattern_heatmaps
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:571``.

.. code-block:: python

   def render_pattern_heatmaps(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Mostra els heatmaps de la pestanya de patrons.

render_epw_tabs
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:597``.

.. code-block:: python

   def render_epw_tabs(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Munta totes les pestanyes del panell EPW.

render_epw_download
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:614``.

.. code-block:: python

   def render_epw_download(state: EpwDashboardState) -> None

**Docstring**

.. code-block:: text

   Mostra els controls de baixada CSV per al fitxer EPW seleccionat.

render_epw_dashboard
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Visor_Climes_EPW.py:632``.

.. code-block:: python

   def render_epw_dashboard() -> None

**Docstring**

.. code-block:: text

   Mostra el flux complet del visor EPW a la UI de Streamlit.

