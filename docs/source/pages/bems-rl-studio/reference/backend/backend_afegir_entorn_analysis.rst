backend/afegir_entorn_analysis.py
=================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py``

**Module path:** ``backend.afegir_entorn_analysis``

**Module docstring**

.. code-block:: text

   Lectura i anàlisi d'edificis per preparar la configuració dels entorns.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``csv``, ``gymnasium``, ``io``, ``json``, ``numpy``, ``pathlib``, ``sinergym``, ``typing``

Classes
-------

ProbeReward
~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:20``.

.. code-block:: python

   class ProbeReward(BaseReward)

**Docstring**

.. code-block:: text

   Reward nul usat només per inspeccionar handlers disponibles.

**Methods**

``def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]``
**Method docstring**

.. code-block:: text

   Executa l'objecte cridable.

Functions
---------

load_building_json
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:28``.

.. code-block:: python

   def load_building_json(building_path: Path) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Carrega i analitza un fitxer d'edifici de format epJSON en un diccionari.

   Paràmetres:
       building_path (Path): camí cap al fitxer epJSON.

   Retorna:
       Dict[str, Any]: el diccionari carregat que renderitza les dades de l'edifici.

extract_schedule_type_index
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:41``.

.. code-block:: python

   def extract_schedule_type_index(building_data: Dict[str, Any]) -> Dict[str, str]

**Docstring**

.. code-block:: text

   Extreu una assignació de noms d'objectes de planificació als seus respectius tipus de blocs de planificació.

   Paràmetres:
       building_data (Dict[str, Any]): les dades de l'edifici epJSON carregades.

   Retorna:
       Dict[str, str]: un diccionari que assigna noms de planificació als seus tipus de bloc d'objectes
       (e.g., 'Programació:Compact').

resolve_schedule_name
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:60``.

.. code-block:: python

   def resolve_schedule_name( schedule_types: Dict[str, str], schedule_name: str, ) -> Optional[str]

**Docstring**

.. code-block:: text

   Resol les referències de planificació amb noms d'estil EnergyPlus que no distingeixen entre majúscules i minúscules.

_register_thermostat_candidate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:83``.

.. code-block:: python

   def _register_thermostat_candidate( detected: Dict[Tuple[str, str], Dict[str, Any]], schedule_types: Dict[str, str], schedule_name: str, category: str, zone_name: Optional[str], ) -> None

**Docstring**

.. code-block:: text

   Registra una planificació de termòstat com a entrada de controlador candidat si encara no s'ha fet un seguiment.

   Crea una nova entrada a `detected` per a la clau donada (categoria, schedule_name) si no hi ha,
   aleshores hi associa el nom de la zona.

   Paràmetres:
       detected (Dict): Registre de candidats acumulat clausurat per (categoria, schedule_name).
       schedule_types (Dict[str, str]): Mapeig de noms de planificació amb les seves cadenes del tipus de bloc.
       schedule_name (str): el nom del programa EnergyPlus per registrar-se.
       category (str): categoria de consigna, e.g. 'heating_setpoint' o 'cooling_setpoint'.
       zone_name (Optional[str]): Nom de la zona a associar amb aquest candidat.

extract_thermostat_schedule_candidates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:120``.

.. code-block:: python

   def extract_thermostat_schedule_candidates( building_data: Dict[str, Any], schedule_types: Dict[str, str], ) -> Tuple[List[str], List[Dict[str, Any]]]

**Docstring**

.. code-block:: text

   Detecta programes de termòstat implícits basats en els punts de consigna Dual i Single del model.

   Paràmetres:
       building_data (Dict[str, Any]): les dades epJSON carregades.
       schedule_types (Dict[str, str]): una assignació de noms de planificació a tipus de bloc de planificació.

   Retorna:
       Tuple[List[str], List[Dict[str, Any]]]: una tupla que conté una llista de detectats
       zones del termòstat i una llista de diccionaris estructurats amb detalls dels actuadors candidats.

_collect_schedule_references_from_value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:208``.

.. code-block:: python

   def _collect_schedule_references_from_value( value: Any, schedule_types: Dict[str, str], ) -> List[str]

**Docstring**

.. code-block:: text

   Recolliu referències de calendari a partir del valor.

extract_schedule_numeric_values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:227``.

.. code-block:: python

   def extract_schedule_numeric_values( building_data: Dict[str, Any], schedule_types: Dict[str, str], schedule_name: str, visited: Optional[set[str]] = None, ) -> List[float]

**Docstring**

.. code-block:: text

   Extreu valors numèrics de planificació.

extract_schedule_value_range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:298``.

.. code-block:: python

   def extract_schedule_value_range( building_data: Dict[str, Any], schedule_types: Dict[str, str], schedule_name: str, ) -> Tuple[Optional[float], Optional[float]]

**Docstring**

.. code-block:: text

   Extreu l'interval de valors de la planificació.

summarize_references
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:310``.

.. code-block:: python

   def summarize_references(prefix: str, references: Sequence[str]) -> str

**Docstring**

.. code-block:: text

   Summarize references.

extract_scheduled_hvac_controller_candidates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:322``.

.. code-block:: python

   def extract_scheduled_hvac_controller_candidates( building_data: Dict[str, Any], schedule_types: Dict[str, str], excluded_schedule_names: Sequence[str], ) -> List[Dict[str, Any]]

**Docstring**

.. code-block:: text

   Identifica els punts de consigna programats i els gestors de disponibilitat a partir del model d'edifici que
   encara no es gestionen com a punts de consigna explícits del termòstat.

   Paràmetres:
       building_data (Dict[str, Any]): les dades epJSON carregades.
       schedule_types (Dict[str, str]): una assignació de noms de planificació a tipus de planificació.
       excluded_schedule_names (Sequence[str]): Noms de les planificacions per ignorar
       (normalment ja està assignat als termòstats).

   Retorna:
       List[Dict[str, Any]]: una llista de diccionaris genèrics HVAC candidats.

extract_storage_controller_candidates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:413``.

.. code-block:: python

   def extract_storage_controller_candidates( building_data: Dict[str, Any], schedule_types: Dict[str, str], excluded_schedule_names: Sequence[str], ) -> List[Dict[str, Any]]

**Docstring**

.. code-block:: text

   Identifica els horaris de càrrega/descàrrega de la bateria que es poden exposar com a accions.

parse_available_handlers
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:483``.

.. code-block:: python

   def parse_available_handlers(available_data: str) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str]], List[str]]

**Docstring**

.. code-block:: text

   Analitzar els controladors disponibles.

probe_available_handlers
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:505``.

.. code-block:: python

   def probe_available_handlers(building_path: Path, weather_path: Path) -> Tuple[bool, str, Optional[str]]

**Docstring**

.. code-block:: text

   Inicia un bucle mínim Sinergym per extreure exactament quins controladors EnergyPlus estan disponibles.

   Paràmetres:
       building_path (Path): camí cap al model d'edifici IDF o epJSON.
       weather_path (Path): camí cap al fitxer meteorològic EPW.

   Retorna:
       Tuple[bool, str, Optional[str]]: una tupla que conté un booleà d'èxit, un text csv de controladors sense processar i una cadena d'error si escau.

find_available_output_variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:546``.

.. code-block:: python

   def find_available_output_variable( available_variables: Sequence[Tuple[str, str]], variable_name: str, variable_key: str, ) -> Optional[Tuple[str, str]]

**Docstring**

.. code-block:: text

   Troba la variable de sortida disponible.

find_available_meter
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:560``.

.. code-block:: python

   def find_available_meter( available_meters: Sequence[str], meter_name: str, ) -> Optional[str]

**Docstring**

.. code-block:: text

   Troba el comptador disponible.

default_bounds_for_category
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:572``.

.. code-block:: python

   def default_bounds_for_category( category: str, actuator_key: str, current_low: Optional[float], current_high: Optional[float], ) -> Tuple[float, float]

**Docstring**

.. code-block:: text

   Límits per defecte per a la categoria.

build_actuator_label
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:598``.

.. code-block:: python

   def build_actuator_label(category: str) -> str

**Docstring**

.. code-block:: text

   Crea una etiqueta de l'actuador per al flux Studio.

_build_actuator_option
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:615``.

.. code-block:: python

   def _build_actuator_option( candidate: Dict[str, Any], building_data: Dict[str, Any], schedule_types: Dict[str, str], ) -> ActuatorOption

**Docstring**

.. code-block:: text

   Construeix un ActuatorOption escrit a partir d'un diccionari candidat en brut.

   Extreu l'interval de valors de la planificació de les dades de l'edifici i calcula sensiblement
   límits d'acció per defecte basats en la categoria de l'actuador.

   Paràmetres:
       candidate (Dict[str, Any]): Dicte de candidat en brut que conté schedule_name, categoria,
           zones, referències, camps element_type i source_kind.
       building_data (Dict[str, Any]): dades completes de l'edifici epJSON per a l'extracció de l'interval de planificació.
       schedule_types (Dict[str, str]): Assignació de noms de planificació a tipus de blocs de planificació.

   Retorna:
       ActuatorOption: una opció d'actuador estructurada i immutable preparada per a la representació de UI i
           configuració de l'entorn.

build_training_analysis
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_analysis.py:675``.

.. code-block:: python

   def build_training_analysis( building_path: Path, weather_path: Path, probe_handlers: bool = False, ) -> BuildingTrainingAnalysis

**Docstring**

.. code-block:: text

   Realitza una anàlisi completa d'un model d'edifici per extreure controladors HVAC entrenables.

   Paràmetres:
       building_path (Path): camí cap al model d'edifici.
       weather_path (Path): Camí al fitxer meteorològic per resoldre les restriccions de l'entorn.
       probe_handlers (bool, optional): Si True, un entorn de sonda Sinergym s'executa exactament
           determinar els components de sortida. El valor predeterminat és False.

   Retorna:
       BuildingTrainingAnalysis: una classe de dades estructurada que conté resultats de detecció per
       termòstats, variables, comptadors i actuadors.

