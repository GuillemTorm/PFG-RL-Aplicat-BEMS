backend/model_metadata.py
=========================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/model_metadata.py``

**Module path:** ``backend.model_metadata``

**Module docstring**

.. code-block:: text

   Utilitats compartides per reconstruir models entrenats de l'Studio.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``json``, ``pathlib``, ``sinergym``, ``typing``

Functions
---------

load_model_metadata
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/model_metadata.py:12``.

.. code-block:: python

   def load_model_metadata(model_path: Path) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Carrega les metadades d'entrenament associades a un model SB3.

build_gym_kwargs_from_metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/model_metadata.py:50``.

.. code-block:: python

   def build_gym_kwargs_from_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Reconstrueix els kwargs de Gym a partir de les metadades d'entrenament.

resolve_reward_class
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/model_metadata.py:75``.

.. code-block:: python

   def resolve_reward_class(reward_name: str | None) -> Any

**Docstring**

.. code-block:: text

   Resol una reward usant les classes exposades per Sinergym.

validate_action_spaces
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/model_metadata.py:88``.

.. code-block:: python

   def validate_action_spaces( model_action_space: Any, env_action_space: Any, metadata: Dict[str, Any], ) -> None

**Docstring**

.. code-block:: text

   Valida que el model i l'entorn comparteixin el mateix contracte d'accions.

