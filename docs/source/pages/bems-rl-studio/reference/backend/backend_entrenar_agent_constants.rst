backend/entrenar_agent_constants.py
===================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_constants.py``

**Module path:** ``backend.entrenar_agent_constants``

**Module docstring**

.. code-block:: text

   Constants i registres per al backend de l'agent de entrenament.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``collections``, ``gymnasium``, ``typing``

Classes
-------

RewardClassRegistry
~~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_constants.py:39``.

.. code-block:: python

   class RewardClassRegistry(Mapping[str, Any])

**Docstring**

.. code-block:: text

   Registre lazy de classes de recompensa exposades per Sinergym.

**Methods**

``def __iter__(self) -> Iterator[str]``
**Method docstring**

.. code-block:: text

   No docstring available yet.

``def __len__(self) -> int``
**Method docstring**

.. code-block:: text

   No docstring available yet.

``def __getitem__(self, reward_name: str) -> Any``
**Method docstring**

.. code-block:: text

   No docstring available yet.

