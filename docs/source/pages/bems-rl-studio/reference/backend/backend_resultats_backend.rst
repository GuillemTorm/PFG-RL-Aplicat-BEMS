backend/resultats_backend.py
============================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/resultats_backend.py``

**Module path:** ``backend.resultats_backend``

**Module docstring**

.. code-block:: text

   Càrrega de dades, preparació de KPI i descobriment d'execució per a la pàgina de resultats.

   El backend de resultats converteix els artefactes de entrenament i avaluació persistents en el
   Estructura ``DashboardData`` consumida per Streamlit i pel generador d'informes.
   Manté deliberadament el descobriment del sistema de fitxers, la normalització CSV i les dades d'acció
   alineació fora del fitxer de pàgina, de manera que el mateix comportament es pot reutilitzar de manera automatitzada
   exportacions.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``copy``, ``dataclasses``, ``glob``, ``json``, ``os``, ``pandas``, ``pathlib``, ``plotly``, ``re``, ``typing``, ``yaml``

Classes
-------

RunOption
~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:28``.

.. code-block:: python

   class RunOption

**Docstring**

.. code-block:: text

   Directori d'execució seleccionable que es mostra a la pàgina de resultats.

**Methods**

``def __str__(self) -> str``
**Method docstring**

.. code-block:: text

   Str.

ResultsPageState
~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:40``.

.. code-block:: python

   class ResultsPageState

**Docstring**

.. code-block:: text

   S'han resolt les entrades necessàries abans que es pugui representar la pàgina de resultats.

RunArtifacts
~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:49``.

.. code-block:: python

   class RunArtifacts

**Docstring**

.. code-block:: text

   Fitxers d'artefactes derivats d'una execució seleccionada.

DashboardData
~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:58``.

.. code-block:: python

   class DashboardData

**Docstring**

.. code-block:: text

   Es requereix un paquet de dades carregat per representar el panell de resultats en línia.

Functions
---------

_is_valid_run_directory
~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:92``.

.. code-block:: python

   def _is_valid_run_directory(run_directory: Path) -> bool

**Docstring**

.. code-block:: text

   Retorna True si el directori conté tant progress.csv com almenys un observations.csv.

_build_run_display_name
~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:105``.

.. code-block:: python

   def _build_run_display_name(run_directory: Path, base_directory: Path) -> str

**Docstring**

.. code-block:: text

   Retorna una etiqueta llegible per a un directori d'execució relativa al directori base.

build_results_page_state
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:114``.

.. code-block:: python

   def build_results_page_state(base_dir: str | None = None) -> ResultsPageState

**Docstring**

.. code-block:: text

   Crea l'estat inicial de la pàgina escanejant el directori base per trobar execucions vàlides per al flux Studio.

get_run_artifacts
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:151``.

.. code-block:: python

   def get_run_artifacts(selected_run: str) -> RunArtifacts

**Docstring**

.. code-block:: text

   Resol els fitxers d'artefactes principals associats a una execució seleccionada.

load_action_data
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:184``.

.. code-block:: python

   def load_action_data(observations_path: str) -> tuple[pd.DataFrame, str]

**Docstring**

.. code-block:: text

   Carrega la primera acció admesa CSV que es troba al costat del fitxer d'observacions.

align_actions_with_observations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:199``.

.. code-block:: python

   def align_actions_with_observations( actions: pd.DataFrame, obs: pd.DataFrame, ) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Alineeu les files d'acció amb les marques de temps d'observació i columnes temporals útils.

select_actions_for_obs
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:224``.

.. code-block:: python

   def select_actions_for_obs(actions: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna les files d'acció que corresponen al sector d'observació proporcionat.

is_radiant_run
~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:236``.

.. code-block:: python

   def is_radiant_run(data: DashboardData) -> bool

**Docstring**

.. code-block:: text

   Retorna si l'execució seleccionada pertany a una configuració d'edifici radiant.

select_radiant_action_data
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:243``.

.. code-block:: python

   def select_radiant_action_data(actions: pd.DataFrame, data: DashboardData) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna les dades d'acció només quan l'execució seleccionada utilitza el control del sòl radiant.

load_dashboard_data
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:251``.

.. code-block:: python

   def load_dashboard_data(progress_path: str, observations_path: str) -> DashboardData

**Docstring**

.. code-block:: text

   Carrega i retorna el paquet de dades complet utilitzat pel panell de resultats.

resolve_model_name_for_run
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:326``.

.. code-block:: python

   def resolve_model_name_for_run(progress_path: str, env_name: str) -> str

**Docstring**

.. code-block:: text

   Retorna el nom del model desat més probable per a una execució de resultats.

_slugify_model_lookup
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:344``.

.. code-block:: python

   def _slugify_model_lookup(value: str) -> str

**Docstring**

.. code-block:: text

   Normalitzeu els noms de la mateixa manera que ho fan els directoris d'artefactes d'entrenament.

_candidate_model_roots
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:351``.

.. code-block:: python

   def _candidate_model_roots(run_folder: Path) -> list[Path]

**Docstring**

.. code-block:: text

   Retorna les arrels probables que continguin artefactes de model desats.

_model_name_from_training_metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:376``.

.. code-block:: python

   def _model_name_from_training_metadata( run_folder: Path, env_name: str, env_slug: str, ) -> str | None

**Docstring**

.. code-block:: text

   Troba un training_config.json que coincideixi i retorna la base del fitxer del model.

_model_name_from_zip_search
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:427``.

.. code-block:: python

   def _model_name_from_zip_search( run_folder: Path, env_name: str, env_slug: str, ) -> str | None

**Docstring**

.. code-block:: text

   Troba un model zip probable quan les metadades no estiguin disponibles.

_safe_mtime
~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:467``.

.. code-block:: python

   def _safe_mtime(path: Path) -> float

**Docstring**

.. code-block:: text

   Retorna un fitxer mtime, o 0 quan no estigui disponible.

load_comparison_data
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:476``.

.. code-block:: python

   def load_comparison_data(run_path: str) -> DashboardData | None

**Docstring**

.. code-block:: text

   Carrega les dades del panell per a una execució de comparació, retornant None quan no és vàlid.

prepare_obs_time_index
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:488``.

.. code-block:: python

   def prepare_obs_time_index(obs: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna les observacions amb un DatetimeIndex coherent per a visualitzacions de sèries temporals reals.

build_real_period_options
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:494``.

.. code-block:: python

   def build_real_period_options(obs: pd.DataFrame, period_kind: str) -> list[tuple[str, str]]

**Docstring**

.. code-block:: text

   Crea opcions de dia, setmana o mes seleccionables per a les visualitzacions de sèries temporals en brut per al flux Studio.

slice_obs_for_real_period
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:528``.

.. code-block:: python

   def slice_obs_for_real_period( obs: pd.DataFrame, period_kind: str, selected_value: str, *, allow_fallback: bool = False, ) -> tuple[pd.DataFrame, str | None]

**Docstring**

.. code-block:: text

   Filtreu les observacions al període de dia, setmana o mes seleccionat.

apply_real_period_axis
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:582``.

.. code-block:: python

   def apply_real_period_axis( fig: go.Figure, obs: pd.DataFrame, period_kind: str, ) -> go.Figure

**Docstring**

.. code-block:: text

   Mapeja els rastres de figures de sèries temporals en brut en un eix de temps relatiu compacte.

flatten_trace_values
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:659``.

.. code-block:: python

   def flatten_trace_values(values: Any) -> list[Any]

**Docstring**

.. code-block:: text

   Retorna valors escalars de les matrius de traça Plotly possiblement imbricades.

trace_has_numeric_values
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:720``.

.. code-block:: python

   def trace_has_numeric_values(trace: go.BaseTraceType) -> bool

**Docstring**

.. code-block:: text

   Retorna si una traça Plotly conté almenys un valor numèric.

has_figure_data
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:733``.

.. code-block:: python

   def has_figure_data(fig: go.Figure) -> bool

**Docstring**

.. code-block:: text

   Retorna si una figura Plotly té almenys un rastre amb valors traçables.

has_action_figure_data
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:746``.

.. code-block:: python

   def has_action_figure_data(fig: go.Figure) -> bool

**Docstring**

.. code-block:: text

   Retorna si una figura d'accions d'agent conté una acció real diferent de zero.

add_comfort_percentage_kpi
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:763``.

.. code-block:: python

   def add_comfort_percentage_kpi( kpi_dict: dict, df: pd.DataFrame, comfort_config: Any = None, ) -> None

**Docstring**

.. code-block:: text

   Afegeix un percentatge d'hores de confort KPI al diccionari KPI proporcionat al seu lloc.

overlay_comparison_traces
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:798``.

.. code-block:: python

   def overlay_comparison_traces( main_fig: go.Figure, comp_fig: go.Figure, label_suffix: str = " (ref)", ) -> go.Figure

**Docstring**

.. code-block:: text

   Superposeu traces de referència en una figura principal quan el tipus de gràfic ho admet.

_ensure_observation_time_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/resultats_backend.py:867``.

.. code-block:: python

   def _ensure_observation_time_columns(obs: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Assegureu-vos que les observacions incloguin camps de mes i hora quan hi hagi marques de temps.

