backend/entrenar_agent_env.py
=============================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py``

**Module path:** ``backend.entrenar_agent_env``

**Module docstring**

.. code-block:: text

   Descobriment d'entorns i metadades per configurar entrenaments.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``gymnasium``, ``os``, ``pathlib``, ``typing``, ``yaml``

Functions
---------

list_registered_envs
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:17``.

.. code-block:: python

   def list_registered_envs() -> List[str]

**Docstring**

.. code-block:: text

   Llista d'envs registrats.

list_files
~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:22``.

.. code-block:: python

   def list_files(directory: Path, suffixes: Sequence[str]) -> List[str]

**Docstring**

.. code-block:: text

   Llista de fitxers.

with_detailed_hvac_meters
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:33``.

.. code-block:: python

   def with_detailed_hvac_meters(meters: Dict[str, str] | None) -> Dict[str, str]

**Docstring**

.. code-block:: text

   Retorna només comptadors configurats.

   Inventar els metres HVAC predeterminats fa que EnergyPlus retorni els identificadors API no vàlids
   per a edificis que no els exposen, omplint eplusout.err amb errors `Severe getMeterValue`
   errors getMeterValue. Els comptadors detallats encara s'utilitzen quan es generen
   la configuració de l'entorn els va detectar explícitament.

get_training_meters_for_env
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:44``.

.. code-block:: python

   def get_training_meters_for_env(env_id: str) -> Dict[str, str]

**Docstring**

.. code-block:: text

   Retorna els mesuradors d'entrenament per a env.

_effective_action_space_from_spec
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:55``.

.. code-block:: python

   def _effective_action_space_from_spec(spec: gym.envs.registration.EnvSpec, fallback: Any) -> Any

**Docstring**

.. code-block:: text

   Espai d'acció efectiu des de les especificacions.

get_env_metadata
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:67``.

.. code-block:: python

   def get_env_metadata(env_id: str) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Retorna les metadades de l'env.

is_comfort_temperature_variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:114``.

.. code-block:: python

   def is_comfort_temperature_variable(variable_name: str, variables: Dict[str, Any]) -> bool

**Docstring**

.. code-block:: text

   És variable la temperatura de confort.

default_comfort_temperature_variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:136``.

.. code-block:: python

   def default_comfort_temperature_variables( variable_names: Sequence[str], variables: Dict[str, Any] ) -> List[str]

**Docstring**

.. code-block:: text

   Variables de temperatura de confort per defecte.

is_energy_variable
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:147``.

.. code-block:: python

   def is_energy_variable(variable_name: str, variables: Dict[str, Any]) -> bool

**Docstring**

.. code-block:: text

   És l'energia variable.

default_grid_energy_variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:171``.

.. code-block:: python

   def default_grid_energy_variables(variable_names: Sequence[str]) -> List[str]

**Docstring**

.. code-block:: text

   Variables d'energia de xarxa per defecte.

default_battery_variables
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:190``.

.. code-block:: python

   def default_battery_variables(variable_names: Sequence[str], kind: str) -> List[str]

**Docstring**

.. code-block:: text

   Variables per defecte de la bateria.

load_default_reward_variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_env.py:220``.

.. code-block:: python

   def load_default_reward_variables( spec: Any, env_id: str, variables: Dict[str, Any] ) -> Tuple[Dict[str, Any], List[str], List[str], List[str]]

**Docstring**

.. code-block:: text

   Carrega les variables de recompensa predeterminades.

