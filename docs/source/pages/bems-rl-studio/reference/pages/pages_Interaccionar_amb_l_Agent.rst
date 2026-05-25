pages/Interaccionar_amb_l'Agent.py
==================================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py``

**Module path:** ``pages.Interaccionar_amb_l'Agent``

**Module docstring**

.. code-block:: text

   Pàgina de control en viu d'un entorn Sinergym.

   Permet provar un model entrenat o aplicar accions manuals pas a pas.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``backend``, ``gymnasium``, ``html``, ``numpy``, ``page_components``, ``page_styles``, ``pandas``, ``pathlib``, ``sidebar_nav``, ``streamlit``

Functions
---------

render_interaction_hero
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py:52``.

.. code-block:: python

   def render_interaction_hero() -> None

**Docstring**

.. code-block:: text

   Mostra la introducció de la pàgina principal a la UI de Streamlit.

render_interaction_section
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py:58``.

.. code-block:: python

   def render_interaction_section(title: str, kicker: str, description: str) -> None

**Docstring**

.. code-block:: text

   Crea una capçalera visual compacta per a una secció de pàgina.

init_session
~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py:71``.

.. code-block:: python

   def init_session()

**Docstring**

.. code-block:: text

   Inicialitzeu les claus de sessió utilitzades pel flux d'interacció en directe.

stop_simulation
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py:95``.

.. code-block:: python

   def stop_simulation()

**Docstring**

.. code-block:: text

   Tanqueu l'entorn actiu i restabliu l'estat d'interacció en directe.

randomize_policy_test_observations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py:116``.

.. code-block:: python

   def randomize_policy_test_observations(obs_vars: list[str]) -> None

**Docstring**

.. code-block:: text

   Substituïu les observacions de la prova de política per valors aleatoris per a les variables actives.

apply_live_action_step
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py:123``.

.. code-block:: python

   def apply_live_action_step( vec_env: object, core_env: object, action_to_take: object, action_source: str = "", repeat_n: int = 1, ) -> None

**Docstring**

.. code-block:: text

   Avançar la simulació en directe i mantenir l'estat d'observació resultant.

_calendar_or_reward_metric
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Interaccionar_amb_l'Agent.py:169``.

.. code-block:: python

   def _calendar_or_reward_metric(curr: dict, prev: dict | None, core_env: object) -> dict

**Docstring**

.. code-block:: text

   Prepara la mètrica de calendari o recompensa quan el temps no és disponible.

