backend/entrenar_agent_rewards.py
=================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py``

**Module path:** ``backend.entrenar_agent_rewards``

**Module docstring**

.. code-block:: text

   Recompenses, algorismes i creadors de càrrega útil de entrenament completa.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``typing``

Functions
---------

build_multizone_temp_mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:30``.

.. code-block:: python

   def build_multizone_temp_mapping( variables: Dict[str, Any], temp_vars: Sequence[str], pair_setpoints: bool = False ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Prepara un mapa de temperatures i setpoints per zones.

build_multizone_occupancy_mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:71``.

.. code-block:: python

   def build_multizone_occupancy_mapping( variables: Dict[str, Any], temp_vars: Sequence[str] ) -> Dict[str, str]

**Docstring**

.. code-block:: text

   Prepara un mapa d'ocupació per zones.

_build_common_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:104``.

.. code-block:: python

   def _build_common_reward_kwargs( options: Dict[str, Any], temp_vars: Sequence[str], energy_vars: Sequence[str], ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Crea els paràmetres compartits per les rewards lineals i de bateria.

_build_battery_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:123``.

.. code-block:: python

   def _build_battery_reward_kwargs( options: Dict[str, Any], variables: Dict[str, Any], ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Crea la part comuna de les rewards que penalitzen xarxa i bateria.

_build_multizone_base_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:164``.

.. code-block:: python

   def _build_multizone_base_kwargs( options: Dict[str, Any], energy_vars: Sequence[str], temp_mapping: Dict[str, Any], ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Crea la base de kwargs que comparteixen les rewards multizona.

_add_energy_cost_file_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:180``.

.. code-block:: python

   def _add_energy_cost_file_kwargs( reward_kwargs: Dict[str, Any], options: Dict[str, Any], cost_vars: Sequence[str], ) -> None

**Docstring**

.. code-block:: text

   Afegeix cost horari i fitxer de preus quan la reward ho necessita.

_build_single_zone_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:196``.

.. code-block:: python

   def _build_single_zone_reward_kwargs( reward_name: str, options: Dict[str, Any], reward_common: Dict[str, Any], battery_kwargs: Dict[str, Any], temp_vars: Sequence[str], energy_vars: Sequence[str], cost_vars: Sequence[str], ) -> Dict[str, Any] | None

**Docstring**

.. code-block:: text

   Crea kwargs per rewards que treballen amb variables globals o monozona.

_build_multizone_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:249``.

.. code-block:: python

   def _build_multizone_reward_kwargs( reward_name: str, options: Dict[str, Any], energy_vars: Sequence[str], cost_vars: Sequence[str], temp_mapping: Dict[str, Any], occupancy_mapping: Dict[str, str], battery_kwargs: Dict[str, Any], ) -> Dict[str, Any] | None

**Docstring**

.. code-block:: text

   Crea kwargs per rewards que separen temperatura i consignes per zona.

build_reward_kwargs
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:308``.

.. code-block:: python

   def build_reward_kwargs( options: Dict[str, Any], variables: Dict[str, Any], temp_vars: Sequence[str], energy_vars: Sequence[str], cost_vars: Sequence[str], ) -> Tuple[Dict[str, Any], Dict[str, str], List[str]]

**Docstring**

.. code-block:: text

   Munta els kwargs de recompensa a partir de la configuració.

validate_training_configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:356``.

.. code-block:: python

   def validate_training_configuration( options: Dict[str, Any], temp_mapping: Dict[str, str] ) -> List[str]

**Docstring**

.. code-block:: text

   Valida la recompensa, l'algorisme, l'espai d'acció i la compatibilitat dels wrappers.

build_algo_kwargs
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:460``.

.. code-block:: python

   def build_algo_kwargs(options: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]

**Docstring**

.. code-block:: text

   Munta els kwargs de l'algorisme a partir de la configuració.

assemble_training_payload
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_rewards.py:482``.

.. code-block:: python

   def assemble_training_payload(options: Dict[str, Any]) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Munta tota la configuració d'entrenament a partir de la UI.

