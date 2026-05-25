backend/training_scripts.py
===========================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/training_scripts.py``

**Module path:** ``backend.training_scripts``

**Module docstring**

.. code-block:: text

   Genereu scripts d'ajuda d'entrenament reproduïbles per a les execucions BEMS-RL desades.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``pprint``, ``typing``

Functions
---------

build_training_eval_script
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/training_scripts.py:9``.

.. code-block:: python

   def build_training_eval_script(training_config: Dict[str, Any]) -> str

**Docstring**

.. code-block:: text

   Crea un petit script d'ajuda d'avaluació desat al costat d'una sessió d'entrenament per al flux Studio.

build_training_repro_script
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/training_scripts.py:25``.

.. code-block:: python

   def build_training_repro_script( artifact_name: str, training_config: Dict[str, Any], ) -> str

**Docstring**

.. code-block:: text

   Crea un script autònom que pugui reproduir una configuració d'entrenament desada.

