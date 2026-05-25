backend/grafics/figures_zones.py
================================

**Group:** Chart and KPI Modules

**Source:** ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py``

**Module path:** ``backend.grafics.figures_zones``

**Module docstring**

.. code-block:: text

   Detecció i filtratge de zones per als panells de resultats.

   Aquest mòdul detecta zones tèrmiques des de la configuració de YAML o de la columna d'observació
   patrons, i mapes les columnes de la zona seleccionada als camps genèrics que fan servir
   les figures comunes.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``pandas``, ``re``, ``typing``

Functions
---------

_zones_from_yaml
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py:35``.

.. code-block:: python

   def _zones_from_yaml(yaml_cfg: Optional[dict]) -> List[str]

**Docstring**

.. code-block:: text

   Zones definides a YAML sota variables→air_temperature→keys.

_try_extract_zone_name
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py:49``.

.. code-block:: python

   def _try_extract_zone_name(col: str, pattern: re.Pattern) -> Optional[str]

**Docstring**

.. code-block:: text

   Donada una columna i un patró de variable (p.ex. air_temperature),
   retorna el 'nom de zona' eliminant aquesta part.
   Exemple: 'zone1_office_air_temperature' -> 'zone1_office'

_zones_from_columns
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py:68``.

.. code-block:: python

   def _zones_from_columns(obs: pd.DataFrame) -> List[str]

**Docstring**

.. code-block:: text

   Infereix zones a partir de columnes que contenen variables de zona conegudes.

detect_zones
~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py:94``.

.. code-block:: python

   def detect_zones(obs: pd.DataFrame, yaml_cfg: Optional[dict] = None) -> List[str]

**Docstring**

.. code-block:: text

   API pública de detecció de zones.

_zone_columns
~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py:103``.

.. code-block:: python

   def _zone_columns(obs: pd.DataFrame, zone: str) -> Dict[str, str]

**Docstring**

.. code-block:: text

   Per una zona concreta, retorna un mapatge {var_key -> nom_columna} segons VAR_PATTERNS.
   Exemple: {'air_temperature': 'zone1_office_air_temperature', ...}

filter_obs_by_zone
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py:119``.

.. code-block:: python

   def filter_obs_by_zone(obs: pd.DataFrame, zone: Optional[str], yaml_cfg: Optional[dict] = None) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna les observacions assignades a la zona seleccionada.

   Es conserven les columnes globals, s'eliminen les columnes que pertanyen a altres zones,
   i els valors de la zona seleccionada s'exposen mitjançant els noms genèrics utilitzats per
   Constructors de figures comuns: ``air_temperature``, ``htg_setpoint``,
   ``clg_setpoint`` i ``temp_violation``.

get_zone_options
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/grafics/figures_zones.py:179``.

.. code-block:: python

   def get_zone_options(obs: pd.DataFrame, yaml_cfg: Optional[dict] = None) -> List[Dict[str, str]]

**Docstring**

.. code-block:: text

   Retorna les opcions de zona.

