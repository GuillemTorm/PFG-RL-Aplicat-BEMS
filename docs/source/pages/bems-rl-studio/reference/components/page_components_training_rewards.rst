page_components/training_rewards.py
===================================

**Group:** Reusable Page Components

**Source:** ``BEMS-RL-STUDIO/page_components/training_rewards.py``

**Module path:** ``page_components.training_rewards``

**Module docstring**

.. code-block:: text

   Controls de configuració de recompenses per a la pàgina de entrenament.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``streamlit``

Functions
---------

render_reward_kwargs_section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_rewards.py:16``.

.. code-block:: python

   def render_reward_kwargs_section( reward_name: str, observation_variables: list[str], candidate_grid_energy_vars: list[str], candidate_battery_charge_vars: list[str], candidate_battery_discharge_vars: list[str], candidate_battery_loss_vars: list[str], ) -> dict

**Docstring**

.. code-block:: text

   Mostra tots els widgets de recompensa i retorna els valors recollits.

   Cobreix pesos d'energia/confort, rangs de confort estacionals, específics de la bateria
   paràmetres, paràmetres de recompensa de cost i configuració d'hores ocupades.

   Retorna:
       Un dict amb tots els kwargs de recompensa recollits dels widgets.

