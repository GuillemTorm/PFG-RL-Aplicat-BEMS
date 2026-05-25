backend/mostrar_entorn_backend.py
=================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py``

**Module path:** ``backend.mostrar_entorn_backend``

**Module docstring**

.. code-block:: text

   Backend de metadades de l'entorn: carrega actius, PV, emmagatzematge i dades per pintar la UI.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``json``, ``pandas``, ``streamlit``, ``typing``

Functions
---------

load_epjson
~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:15``.

.. code-block:: python

   def load_epjson(path: str) -> dict

**Docstring**

.. code-block:: text

   Llegeix i retorna un fitxer epJSON del disc (emmagatzemat a la memòria cau).

_safe_float
~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:21``.

.. code-block:: python

   def _safe_float(value: Any) -> Optional[float]

**Docstring**

.. code-block:: text

   Retorna float(valor) o None si la conversió falla.

_getf
~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:29``.

.. code-block:: python

   def _getf(data: dict, *keys: str) -> Optional[float]

**Docstring**

.. code-block:: text

   Retorna el primer valor numèric trobat entre les claus donades, o None.

_derive_kibam_metrics
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:42``.

.. code-block:: python

   def _derive_kibam_metrics( obj: dict, ) -> Tuple[Optional[float], Optional[float], Optional[float]]

**Docstring**

.. code-block:: text

   Deriva (energy_kwh, p_charge_kw, p_discharge_kw) d'un objecte de bateria KiBaM.

   Processa ElectricLoadCenter:Emmagatzematge:camps de bateria per estimar el nivell de paquet
   capacitat energètica i límits de potència de càrrega/descàrrega.

parse_pv_and_storage
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:86``.

.. code-block:: python

   def parse_pv_and_storage(epjson: dict) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Analitza generadors de PV i objectes d'emmagatzematge de la bateria des d'un epJSON dict.

   Admet generador: fotovoltaic, generador: PVWatts,
   ElectricLoadCenter:Emmagatzematge:Simple, :Bateria i :LiIonNMCBattery.
   Retorna un dict amb les claus 'pv' i 'emmagatzematge', cadascuna una llista de dicts normalitzats.

load_environment_assets
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:158``.

.. code-block:: python

   def load_environment_assets(epjson_path: str) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Carrega i prepareu tots els actius principals per a un entorn Sinergym (emmagatzemats a la memòria cau).

   Llegeix el fitxer epJSON, crea registres de superfície enriquits i analitza
   PV/objectes d'emmagatzematge. Retorna un dict unificat preparat per a UI.

summarize_pv
~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:179``.

.. code-block:: python

   def summarize_pv( records: List[dict], name_index: Dict[str, int], pv_list: List[dict], ) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Calculeu mètriques agregades per als panells PV associats a les superfícies de l'edifici.

   Recompte de retorns, llista de noms de superfície actives, àrea total, inclinació mitjana i
   azimut mitjà. L'àrea i els angles són None quan no es troben superfícies coincidents.

parse_epw_metadata_and_temperature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:211``.

.. code-block:: python

   def parse_epw_metadata_and_temperature(epw_file: str)

**Docstring**

.. code-block:: text

   Llegeix les metadades d'ubicació i la temperatura anual mitjana d'un fitxer EPW (emmagatzemat a la memòria cau).

   Retorna (location_dict, avg_temp_celsius, climate_zone_label).

_format_ui_value
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:231``.

.. code-block:: python

   def _format_ui_value(value: Any) -> str

**Docstring**

.. code-block:: text

   Formata qualsevol valor per mostrar-lo, retornant '-' per als valors buits/None.

_tuple_mapping_to_df
~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:240``.

.. code-block:: python

   def _tuple_mapping_to_df(mapping: Dict[str, Any], columns: List[str]) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Converteix un dict d'entrades amb valors de tupla a una etiqueta DataFrame.

_sequence_to_df
~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:253``.

.. code-block:: python

   def _sequence_to_df(values: List[Any], column_name: str) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Converteix una llista plana de valors en una sola columna DataFrame.

_reward_summary_frames
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mostrar_entorn_backend.py:258``.

.. code-block:: python

   def _reward_summary_frames( reward_kwargs: Dict[str, Any], ) -> Tuple[pd.DataFrame, pd.DataFrame]

**Docstring**

.. code-block:: text

   Divideix els kwargs de recompensa en escalar i agrupa (list-valued) DataFrames.

