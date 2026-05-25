pages/Entrenar_Agent.py
=======================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Entrenar_Agent.py``

**Module path:** ``pages.Entrenar_Agent``

**Module docstring**

.. code-block:: text

   Pàgina d'entrenament de l'agent per a l'aplicació BEMS-RL-STUDIO.

   Orquestra el flux complet d'entrenament: selecció de l'entorn, configuració de la
   reward, wrappers, hiperparàmetres de l'agent i bucle incremental amb gràfics en directe.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``page_components``, ``sidebar_nav``, ``streamlit``

Functions
---------

train_tab
~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Entrenar_Agent.py:51``.

.. code-block:: python

   def train_tab() -> None

**Docstring**

.. code-block:: text

   Punt d'entrada a la pàgina d'entrenament.

   Orquestra totes les seccions UI en ordre:
   1. Inicialització de l'estat de la sessió.
   2. Entorn, algorisme i selecció de polítiques.
   3. Recompensa kwargs (pesos, rangs estacionals, comoditat).
   4. Selecció i configuració de wrappers (observació, acció, logs).
   5. Paràmetres de l'agent (taxa d'aprenentatge, n_steps, total_timesteps).
   6. Controls d'execució (inici/aturada).
   7. Cicle d'entrenament incremental amb gràfics en directe.

