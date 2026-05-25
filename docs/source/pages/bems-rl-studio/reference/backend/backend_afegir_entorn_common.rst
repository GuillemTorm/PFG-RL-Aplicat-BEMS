backend/afegir_entorn_common.py
===============================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py``

**Module path:** ``backend.afegir_entorn_common``

**Module docstring**

.. code-block:: text

   Constants, tipus i helpers compartits pel flux d'afegir entorns.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``dataclasses``, ``pathlib``, ``re``, ``typing``

Classes
-------

UpgradeResult
~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:61``.

.. code-block:: python

   class UpgradeResult

**Docstring**

.. code-block:: text

   Resultat d'un intent d'actualitzar una IDF a la versio suportada.

EnvironmentValidationResult
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:69``.

.. code-block:: python

   class EnvironmentValidationResult

**Docstring**

.. code-block:: text

   Espais i observacio inicial retornats en validar un entorn registrat.

ActuatorOption
~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:77``.

.. code-block:: python

   class ActuatorOption

**Docstring**

.. code-block:: text

   Opcio d'actuador candidata detectada en un model EnergyPlus.

BuildingTrainingAnalysis
~~~~~~~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:94``.

.. code-block:: python

   class BuildingTrainingAnalysis

**Docstring**

.. code-block:: text

   Resultat agregat de l'analisi d'un edifici per entrenament RL.

Functions
---------

save_uploaded_bytes
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:105``.

.. code-block:: python

   def save_uploaded_bytes(target_path: Path, content: bytes) -> Path

**Docstring**

.. code-block:: text

   Desa bytes pujats per Streamlit a disc i retorna la ruta.

sanitize_identifier
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:113``.

.. code-block:: python

   def sanitize_identifier(raw_value: str, fallback: str) -> str

**Docstring**

.. code-block:: text

   Neteja una cadena per utilitzar-la com a identificador segur.

normalize_token
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:119``.

.. code-block:: python

   def normalize_token(value: str) -> str

**Docstring**

.. code-block:: text

   Normalitza una cadena per fer comparacions flexibles.

unique_identifier
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_common.py:127``.

.. code-block:: python

   def unique_identifier(base: str, used: set[str]) -> str

**Docstring**

.. code-block:: text

   Genera un identificador únic afegint un sufix incremental si cal.

