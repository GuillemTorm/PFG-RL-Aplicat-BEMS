backend/entrenar_agent_wrappers.py
==================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py``

**Module path:** ``backend.entrenar_agent_wrappers``

**Module docstring**

.. code-block:: text

   Configuració i aplicació de wrapper per a entorns d'entrenament.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``csv``, ``gymnasium``, ``numpy``, ``sinergym``, ``typing``

Classes
-------

EnergyCostFileLogger
~~~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:16``.

.. code-block:: python

   class EnergyCostFileLogger(Wrapper)

**Docstring**

.. code-block:: text

   Logger addicional (opcional) que escriu cost per pas en un CSV independent.

**Methods**

``def __init__(self, env, filename="energy_cost_log.csv")``
**Method docstring**

.. code-block:: text

   Inicialitza la instància.

``def step(self, action)``
**Method docstring**

.. code-block:: text

   Step.

``def reset(self, **kwargs)``
**Method docstring**

.. code-block:: text

   Restableix.

``def close(self)``
**Method docstring**

.. code-block:: text

   Close.

Functions
---------

wrapper_details
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:49``.

.. code-block:: python

   def wrapper_details(params: Dict[str, Any]) -> str

**Docstring**

.. code-block:: text

   Detalls del wrapper.

build_wrapper_summary_rows
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:56``.

.. code-block:: python

   def build_wrapper_summary_rows(wrapper_configs: Sequence[Dict[str, Any]]) -> List[Dict[str, str]]

**Docstring**

.. code-block:: text

   Prepara les files de resum dels wrappers seleccionats.

apply_training_wrappers
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:70``.

.. code-block:: python

   def apply_training_wrappers(env: Any, wrapper_configs: Sequence[Dict[str, Any]]) -> Any

**Docstring**

.. code-block:: text

   Aplica wrappers d'entrenament.

_normalize_wrapper_params
~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:91``.

.. code-block:: python

   def _normalize_wrapper_params(name: str, params: Dict[str, Any]) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Converteix paràmetres serialitzats per la UI al format que espera Sinergym.

_wrapper_import_path
~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:104``.

.. code-block:: python

   def _wrapper_import_path(name: str) -> str

**Docstring**

.. code-block:: text

   Retorna la ruta importable que consumeix ``sinergym.utils.common.apply_wrappers_info``.

build_energy_cost_wrapper_reward_kwargs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:111``.

.. code-block:: python

   def build_energy_cost_wrapper_reward_kwargs( options: Dict[str, Any], temp_vars: Sequence[str], energy_vars: Sequence[str], ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Munta els kwargs del wrapper de costos energètics.

build_wrapper_configs
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_wrappers.py:131``.

.. code-block:: python

   def build_wrapper_configs( options: Dict[str, Any], energy_cost_reward_kwargs: Dict[str, Any] | None = None, recalculate_energy_cost_reward: bool = True, ) -> List[Dict[str, Any]]

**Docstring**

.. code-block:: text

   Munta la configuració dels wrappers d'entrenament.

