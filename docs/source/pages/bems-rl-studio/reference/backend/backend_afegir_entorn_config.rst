backend/afegir_entorn_config.py
===============================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py``

**Module path:** ``backend.afegir_entorn_config``

**Module docstring**

.. code-block:: text

   Crea i valideu les configuracions de Sinergym des de l'entrada del formulari Studio.

   Aquest mòdul és l'últim pas del flux Afegeix un entorn. Rep el
   anàlisi d'edificis, variables seleccionades, comptadors, actuadors i paràmetres de recompensa,
   després escriu una configuració YAML que es pot registrar com a Gymnasium
   entorn.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``gymnasium``, ``json``, ``pathlib``, ``re``, ``sinergym``, ``subprocess``, ``sys``, ``typing``, ``yaml``

Functions
---------

build_variable_output_names
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:40``.

.. code-block:: python

   def build_variable_output_names(base_name: str, keys: Sequence[str] | str) -> List[str]

**Docstring**

.. code-block:: text

   Retorna àlies de variable de sortida estables per a una o més claus EnergyPlus.

add_variable_spec
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:47``.

.. code-block:: python

   def add_variable_spec( variables: Dict[str, Dict[str, Any]], available_output_variables: Sequence[Tuple[str, str]], canonical_variable_name: str, alias_name: str, keys: Sequence[str] | str, ) -> List[str]

**Docstring**

.. code-block:: text

   Afegeix una especificació variable.

build_training_observation_config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:97``.

.. code-block:: python

   def build_training_observation_config( analysis: BuildingTrainingAnalysis, ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str], List[str], List[str]]

**Docstring**

.. code-block:: text

   Munta la configuració d'observacions d'entrenament.

build_variable_name_for_actuator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:178``.

.. code-block:: python

   def build_variable_name_for_actuator( option: ActuatorOption, selected_options: Sequence[ActuatorOption], used_names: set[str], ) -> str

**Docstring**

.. code-block:: text

   Genera el nom de variable associat a un actuador.

build_action_space_expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:217``.

.. code-block:: python

   def build_action_space_expression(bounds: Sequence[Tuple[float, float]]) -> str

**Docstring**

.. code-block:: text

   Construeix una expressió d'espai d'acció.

build_environment_config
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:229``.

.. code-block:: python

   def build_environment_config( id_base: str, building_file_name: str, weather_profiles: Sequence[Dict[str, str]], analysis: BuildingTrainingAnalysis, selected_actuators: Sequence[ActuatorOption], actuator_bounds: Dict[str, Tuple[float, float]], weather_variability: Optional[Dict[str, Sequence[float]]] = None, ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Construeix el diccionari de configuració de l'entorn arrel Sinergym YAML.

   Paràmetres:
       id_base (str): nom base per al registre de l'entorn.
       building_file_name (str): el nom del fitxer d'estructura.
       weather_profiles (Sequence[Dict[str, str]]): Llista de mapes meteorològics (fitxa i claus).
       analysis (BuildingTrainingAnalysis): propietats detectades.
       selected_actuators (Sequence[ActuatorOption]): actuadors seleccionats del UI.
       actuator_bounds (Dict[str, Tuple[float, float]]): els límits continus de cada actuador.
       weather_variability (Optional[Dict[str, Sequence[float]]]): Diccionari de variabilitat opcional.

   Retorna:
       Dict[str, Any]: La configuració totalment estructurada està preparada per escriure com a YAML.

write_yaml_config
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:323``.

.. code-block:: python

   def write_yaml_config(cfg_path: Path, env_cfg: Dict[str, Any]) -> Path

**Docstring**

.. code-block:: text

   Escriu el diccionari de configuració de l'entorn generat en un fitxer YAML.

   Paràmetres:
       cfg_path (Path): Camí al fitxer de sortida YAML.
       env_cfg (Dict[str, Any]): dades de configuració del diccionari.

   Retorna:
       Path: la ruta del fitxer de sortida confirmada.

register_environment_from_yaml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:338``.

.. code-block:: python

   def register_environment_from_yaml(cfg_path: Path) -> None

**Docstring**

.. code-block:: text

   Registra o torna a registrar els entorns des d'una configuració Sinergym YAML mitjançant Gym.

   Paràmetres:
       cfg_path (Path): camí cap a la configuració vàlida Sinergym YAML.

build_registered_env_id
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:356``.

.. code-block:: python

   def build_registered_env_id(id_base: str, weather_key: str, stochastic: bool = False) -> str

**Docstring**

.. code-block:: text

   Crea l'ID de l'entorn del Gym canònic basat en les convencions de denominació Sinergym.

   Paràmetres:
       id_base (str): Nom base donat a l'element d'edifici.
       weather_key (str): descriptor breu de la cadena meteorològica.
       stochastic (bool, optional): si la variant pretén incloure variabilitat.

   Retorna:
       str: identificador d'entorn OpenAI Gym vàlid.

validate_registered_environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:371``.

.. code-block:: python

   def validate_registered_environment(env_id: str, cfg_path: Optional[Path] = None) -> EnvironmentValidationResult

**Docstring**

.. code-block:: text

   Executa un subprocés aïllat per activar i validar que l'entorn es registra i passa correctament.

   Paràmetres:
       env_id (str): cadena d'ID d'entorn Gym.
       cfg_path (Optional[Path], optional): camí cap a yaml si és necessari per al registre diferit.

   Retorna:
       EnvironmentValidationResult: un dict de verificació estructural que indica la matriu d'observació i els espais.

cleanup_failed_environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/afegir_entorn_config.py:438``.

.. code-block:: python

   def cleanup_failed_environment(cfg_path: Path, tmp_path: Path) -> List[Tuple[str, str]]

**Docstring**

.. code-block:: text

   Intenta eliminar les estructures de configuració no enllaçades o incorrectes com a resultat d'un registre fallit.

   Paràmetres:
       cfg_path (Path): Configuració interrompuda de YAML.
       tmp_path (Path): fitxer epJSON intermedi generat.

   Retorna:
       List[Tuple[str, str]]: Tuples de missatgeria de nivell de diagnòstic que mapegen quins recursos es van revertir.

