pages/Mostrar_Entorn.py
=======================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py``

**Module path:** ``pages.Mostrar_Entorn``

**Module docstring**

.. code-block:: text

   Pàgina de visualització d'entorns Sinergym.

   Mostra la geometria 3D, el clima, la configuració i els actius energètics
   associats a l'entorn seleccionat.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``backend``, ``gymnasium``, ``html``, ``json``, ``numpy``, ``page_components``, ``page_styles``, ``pandas``, ``re``, ``sidebar_nav``, ``streamlit``, ``typing``

Functions
---------

_dataframe_height
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:46``.

.. code-block:: python

   def _dataframe_height(row_count: int, *, max_height: int = 340) -> int

**Docstring**

.. code-block:: text

   Calcula una alçada de taula ajustada al nombre de files visibles.

render_environment_hero
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:54``.

.. code-block:: python

   def render_environment_hero() -> None

**Docstring**

.. code-block:: text

   Munta el bloc principal de la pàgina.

render_environment_section
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:60``.

.. code-block:: python

   def render_environment_section(title: str, kicker: str, description: str) -> None

**Docstring**

.. code-block:: text

   Mostra la capçalera visual d'una secció.

describe_environment_tags
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:66``.

.. code-block:: python

   def describe_environment_tags(env_name: str) -> List[str]

**Docstring**

.. code-block:: text

   Resumeix propietats de l'entorn en etiquetes curtes.

render_environment_tags
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:88``.

.. code-block:: python

   def render_environment_tags(tags: List[str]) -> None

**Docstring**

.. code-block:: text

   Mostra propietats detectades en format d'etiqueta.

render_metric_card
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:98``.

.. code-block:: python

   def render_metric_card(label: str, value: str, variant: str = "") -> None

**Docstring**

.. code-block:: text

   Crea una targeta compacta amb una metrica o text curt.

render_metric_cards
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:114``.

.. code-block:: python

   def render_metric_cards(items: List[Tuple[str, str]], columns: int = 2, wide_first: bool = False) -> None

**Docstring**

.. code-block:: text

   Distribueix targetes compactes en files estables.

render_detail_card
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:136``.

.. code-block:: python

   def render_detail_card(title: str, rows: List[Tuple[str, str]]) -> None

**Docstring**

.. code-block:: text

   Crea una targeta compacta de detall.

render_battery_cards
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:157``.

.. code-block:: python

   def render_battery_cards(storage_list: List[dict]) -> None

**Docstring**

.. code-block:: text

   Mostra les bateries detectades com a targetes visuals.

_reward_label
~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:195``.

.. code-block:: python

   def _reward_label(reward_value: Any) -> str

**Docstring**

.. code-block:: text

   Retorna una etiqueta llegible per al reward configurat.

render_basic_config
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:201``.

.. code-block:: python

   def render_basic_config(spec: gym.envs.registration.EnvSpec, kwargs: Dict[str, Any]) -> None

**Docstring**

.. code-block:: text

   Omple la secció de configuració bàsica a la UI de Streamlit.

render_action_space_summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:216``.

.. code-block:: python

   def render_action_space_summary(action_space: Any) -> None

**Docstring**

.. code-block:: text

   Resumeix l'espai d'acció a la UI de Streamlit.

_actuators_mapping_df
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:284``.

.. code-block:: python

   def _actuators_mapping_df(actuators: Dict[str, Any]) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Construeix un resum llegible del mapatge entre dimensions i actuadors.

_json_safe_value
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:312``.

.. code-block:: python

   def _json_safe_value(value: Any) -> Any

**Docstring**

.. code-block:: text

   Converteix objectes Python/Gym/NumPy a valors aptes per a JSON.

_json_download_payload
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:330``.

.. code-block:: python

   def _json_download_payload(value: Dict[str, Any]) -> bytes

**Docstring**

.. code-block:: text

   Serialitza la configuració de l'entorn per descarregar-la sense renderitzar-la.

_safe_json_filename
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:341``.

.. code-block:: python

   def _safe_json_filename(env_name: str) -> str

**Docstring**

.. code-block:: text

   Crea un nom de fitxer estable per descarregar la configuració de l'entorn.

render_kwargs_overview
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:348``.

.. code-block:: python

   def render_kwargs_overview(kwargs: Dict[str, Any], env_name: str) -> None

**Docstring**

.. code-block:: text

   Secció de visió general de renderització de kwargs a la UI de Streamlit.

render_3d_viewer
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:462``.

.. code-block:: python

   def render_3d_viewer( records: List[dict], zones: List[str], types: List[str], z_clip_range: Tuple[float, float], pv_list: List[dict], name_index: Dict[str, int], ) -> None

**Docstring**

.. code-block:: text

   Mostra el visor de geometria de l'edifici en 3D.

   Mostra la figura 3D interactiva Plotly. Totes les superfícies es mostren amb
   per defecte amb tots els tipus i zones visibles.

render_environment_page
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:495``.

.. code-block:: python

   def render_environment_page() -> None

**Docstring**

.. code-block:: text

   Munta la pàgina amb la presentació visual actualitzada.

