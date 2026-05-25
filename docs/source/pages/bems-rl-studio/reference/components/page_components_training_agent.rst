page_components/training_agent.py
=================================

**Group:** Reusable Page Components

**Source:** ``BEMS-RL-STUDIO/page_components/training_agent.py``

**Module path:** ``page_components.training_agent``

**Module docstring**

.. code-block:: text

   Controls d'hiperparàmetres de l'agent per a la pàgina d'entrenament.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``streamlit``

Functions
---------

render_agent_params_section
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_agent.py:9``.

.. code-block:: python

   def render_agent_params_section(algo_name: str) -> dict

**Docstring**

.. code-block:: text

   Mostra els widgets d'hiperparàmetres de l'agent i retorna els seus valors.

   Cobreix la taxa d'aprenentatge, n_steps, els passos de temps totals i tots els SB3 avançats
   paràmetres (batch_size, gamma, n_epochs, gae_lambda, clip_range,
   ent_coef, vf_coef, max_grad_norm).

   Retorna:
       Un dict amb tots els valors dels paràmetres d'agent recollits dels widgets.

