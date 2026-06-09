page_components/training_wrappers.py
====================================

**Group:** Reusable Page Components

**Source:** ``BEMS-RL-STUDIO/page_components/training_wrappers.py``

**Module path:** ``page_components.training_wrappers``

**Module docstring**

.. code-block:: text

   Controls de wrappers i registre per a la pàgina d'entrenament.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``streamlit``

Functions
---------

_checkbox_kwargs
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/training_wrappers.py:18``.

.. code-block:: python

   def _checkbox_kwargs(field: str, default: bool = False, *, disabled: bool = False) -> dict

**Docstring**

.. code-block:: text

   Prepara els arguments comuns dels checkboxes del formulari d'entrenament.

render_observation_wrappers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_wrappers.py:27``.

.. code-block:: python

   def render_observation_wrappers( observation_variables: list[str], context_variables: list[str], candidate_temp_vars: list[str], candidate_setpoint_vars: list[str], ) -> dict

**Docstring**

.. code-block:: text

   Pinta els controls que modifiquen les observacions abans d'arribar a l'agent.

render_action_wrappers
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_wrappers.py:302``.

.. code-block:: python

   def render_action_wrappers( env_meta: dict, action_variables: list[str], action_space, ) -> dict

**Docstring**

.. code-block:: text

   Pinta els controls que canvien com l'agent envia accions a l'entorn.

render_energy_logging_wrappers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_wrappers.py:473``.

.. code-block:: python

   def render_energy_logging_wrappers( energy_cost_files: list[str], initial_energy_cost_path: str, initial_file_logger_name: str, ) -> dict

**Docstring**

.. code-block:: text

   Pinta els controls de cost energètic i de fitxer de registre.

render_wrappers_section
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/training_wrappers.py:529``.

.. code-block:: python

   def render_wrappers_section( env_meta: dict, observation_variables: list[str], action_variables: list[str], action_space, context_variables: list[str], candidate_temp_vars: list[str], candidate_setpoint_vars: list[str], ) -> dict

**Docstring**

.. code-block:: text

   Agrupa els controls de wrappers i retorna una configuració plana per al backend.

