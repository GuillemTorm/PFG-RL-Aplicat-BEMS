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

``backend``, ``gymnasium``, ``html``, ``numpy``, ``page_components``, ``page_styles``, ``pandas``, ``sidebar_nav``, ``streamlit``, ``typing``

Functions
---------

render_environment_hero
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:41``.

.. code-block:: python

   def render_environment_hero() -> None

**Docstring**

.. code-block:: text

   Munta el bloc principal de la pàgina.

render_environment_section
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:47``.

.. code-block:: python

   def render_environment_section(title: str, kicker: str, description: str) -> None

**Docstring**

.. code-block:: text

   Mostra la capçalera visual d'una secció.

describe_environment_tags
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:53``.

.. code-block:: python

   def describe_environment_tags(env_name: str) -> List[str]

**Docstring**

.. code-block:: text

   Resumeix propietats de l'entorn en etiquetes curtes.

render_environment_tags
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:75``.

.. code-block:: python

   def render_environment_tags(tags: List[str]) -> None

**Docstring**

.. code-block:: text

   Mostra propietats detectades en format d'etiqueta.

render_metric_card
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:85``.

.. code-block:: python

   def render_metric_card(label: str, value: str, variant: str = "") -> None

**Docstring**

.. code-block:: text

   Crea una targeta compacta amb una metrica o text curt.

render_metric_cards
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:101``.

.. code-block:: python

   def render_metric_cards(items: List[Tuple[str, str]], columns: int = 2, wide_first: bool = False) -> None

**Docstring**

.. code-block:: text

   Distribueix targetes compactes en files estables.

render_detail_card
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:123``.

.. code-block:: python

   def render_detail_card(title: str, rows: List[Tuple[str, str]]) -> None

**Docstring**

.. code-block:: text

   Crea una targeta compacta de detall.

render_battery_cards
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:144``.

.. code-block:: python

   def render_battery_cards(storage_list: List[dict]) -> None

**Docstring**

.. code-block:: text

   Mostra les bateries detectades com a targetes visuals.

_reward_label
~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:182``.

.. code-block:: python

   def _reward_label(reward_value: Any) -> str

**Docstring**

.. code-block:: text

   Retorna una etiqueta llegible per al reward configurat.

render_basic_config
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:188``.

.. code-block:: python

   def render_basic_config(spec: gym.envs.registration.EnvSpec, kwargs: Dict[str, Any]) -> None

**Docstring**

.. code-block:: text

   Omple la secció de configuració bàsica a la UI de Streamlit.

render_action_space_summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:203``.

.. code-block:: python

   def render_action_space_summary(action_space: Any) -> None

**Docstring**

.. code-block:: text

   Resumeix l'espai d'acció a la UI de Streamlit.

_actuators_mapping_df
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:261``.

.. code-block:: python

   def _actuators_mapping_df(actuators: Dict[str, Any]) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Construeix un resum llegible del mapatge entre dimensions i actuadors.

render_kwargs_overview
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:289``.

.. code-block:: python

   def render_kwargs_overview(kwargs: Dict[str, Any]) -> None

**Docstring**

.. code-block:: text

   Secció de visió general de renderització de kwargs a la UI de Streamlit.

render_3d_viewer
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:387``.

.. code-block:: python

   def render_3d_viewer( records: List[dict], zones: List[str], types: List[str], z_clip_range: Tuple[float, float], pv_list: List[dict], name_index: Dict[str, int], ) -> None

**Docstring**

.. code-block:: text

   Mostra el visor de geometria de l'edifici en 3D.

   Mostra la figura 3D interactiva Plotly. Totes les superfícies es mostren amb
   per defecte amb tots els tipus i zones visibles.

render_environment_page
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Mostrar_Entorn.py:420``.

.. code-block:: python

   def render_environment_page() -> None

**Docstring**

.. code-block:: text

   Munta la pàgina amb la presentació visual actualitzada.

