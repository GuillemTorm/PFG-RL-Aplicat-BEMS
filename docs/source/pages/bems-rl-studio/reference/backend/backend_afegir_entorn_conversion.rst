backend/afegir_entorn_conversion.py
===================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/afegir_entorn_conversion.py``

**Module path:** ``backend.afegir_entorn_conversion``

**Module docstring**

.. code-block:: text

   Conversió i actualització d'IDF/epJSON dins del flux per afegir entorns.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``os``, ``pathlib``, ``re``, ``shutil``, ``ssl``, ``subprocess``, ``tarfile``, ``typing``, ``urllib``

Functions
---------

detect_idf_version
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_conversion.py:23``.

.. code-block:: python

   def detect_idf_version(idf_path: Path) -> Optional[Tuple[int, int]]

**Docstring**

.. code-block:: text

   Llegeix un fitxer IDF per extreure la seva versió de destinació EnergyPlus.

   Paràmetres:
       idf_path (Path): camí cap al fitxer IDF.

   Retorna:
       Optional[Tuple[int, int]]: una tupla de nombres enters majors i menors si es troba, sinó None.

needs_idf_upgrade
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_conversion.py:46``.

.. code-block:: python

   def needs_idf_upgrade(version: Tuple[int, int]) -> bool

**Docstring**

.. code-block:: text

   Avalua si una versió IDF requereix l'actualització a la versió del simulador de destinació.

   Paràmetres:
       version (Tuple[int, int]): versió major i menor de IDF.

   Retorna:
       bool: True si la versió és estrictament més antiga que la `TARGET_EPLUS_VERSION`.

get_transition_updater_dir
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_conversion.py:60``.

.. code-block:: python

   def get_transition_updater_dir() -> Optional[Path]

**Docstring**

.. code-block:: text

   Recupera el directori local que conté EnergyPlus IDFVersionUpdater binaris.

   Retorna:
       Optional[Path]: camí cap a les eines d'actualització, o None si no es troba localment.

download_transition_tools
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_conversion.py:75``.

.. code-block:: python

   def download_transition_tools() -> Path

**Docstring**

.. code-block:: text

   Baixa i extreu EnergyPlus Eines de transició al directori alternatiu.

   En lloc de descarregar tota la suite EnergyPlus, només extreu l'actualitzador PreProcess.

   Retorna:
       Path: el directori local que conté les eines de transició descarregades.

upgrade_idf_version
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_conversion.py:98``.

.. code-block:: python

   def upgrade_idf_version(idf_path: Path, updater_dir: Path) -> UpgradeResult

**Docstring**

.. code-block:: text

   Actualitza seqüencialment un fitxer IDF mitjançant cadenes de transició EnergyPlus.

   Paràmetres:
       idf_path (Path): camí cap al fitxer IDF de destinació.
       updater_dir (Path): Directori que conté les eines de transició.

   Retorna:
       UpgradeResult: Estructura resumida de l'operació d'actualització.

convert_idf_to_epjson
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_conversion.py:167``.

.. code-block:: python

   def convert_idf_to_epjson(idf_path: Path) -> Path

**Docstring**

.. code-block:: text

   Converteix un fitxer EnergyPlus IDF al format epJSON mitjançant les eines CLI.

   Paràmetres:
       idf_path (Path): camí cap al fitxer estructural IDF.

   Retorna:
       Path: el camí del fitxer epJSON convertit resultant.

