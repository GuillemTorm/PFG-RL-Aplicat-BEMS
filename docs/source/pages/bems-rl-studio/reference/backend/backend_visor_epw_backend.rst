backend/visor_epw_backend.py
============================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/visor_epw_backend.py``

**Module path:** ``backend.visor_epw_backend``

**Module docstring**

.. code-block:: text

   Utilitats de preparació de dades per al visor climàtic EPW.

   El backend del visor EPW localitza fitxers meteorològics d'EnergyPlus,
   normalitza els camps EPW en brut, afegeix atributs de calendari i produeix
   taules de resum per a la UI de Streamlit. Les sortides es mantenen com a
   DataFrames perquè els gràfics i les descàrregues es puguin construir sense
   tornar a llegir el fitxer meteorològic.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``numpy``, ``pandas``, ``pathlib``, ``streamlit``

Functions
---------

_parse_optional_float
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:185``.

.. code-block:: python

   def _parse_optional_float(value: str | None) -> float

**Docstring**

.. code-block:: text

   Retorna un camp numèric EPW com a flotant, o NaN quan el valor està en blanc o no és vàlid.

_header_payload
~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:196``.

.. code-block:: python

   def _header_payload(header_lines: list[str], line_index: int) -> str

**Docstring**

.. code-block:: text

   Retorna la càrrega útil després de la primera coma en una línia de capçalera EPW.

_classify_climate
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:204``.

.. code-block:: python

   def _classify_climate(annual_mean_temp: float) -> str

**Docstring**

.. code-block:: text

   Classifica la família climàtica a partir de la temperatura mitjana anual de bulb sec.

_metadata_coordinates
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:214``.

.. code-block:: python

   def _metadata_coordinates(metadata: dict[str, object]) -> tuple[float, float, float] | None

**Docstring**

.. code-block:: text

   Retorna valors vàlids de latitud, longitud i zona horària de les metadades EPW.

variable_label
~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:230``.

.. code-block:: python

   def variable_label(variable_key: str, *, aggregated: bool = False) -> str

**Docstring**

.. code-block:: text

   Retorna l'etiqueta UI i la unitat de visualització per a una clau variable EPW.

_parse_location_line
~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:241``.

.. code-block:: python

   def _parse_location_line(line: str) -> dict[str, object]

**Docstring**

.. code-block:: text

   Analitza la línia de capçalera EPW LOCATION als camps de metadades del lloc.

_read_epw_header
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:258``.

.. code-block:: python

   def _read_epw_header(epw_path: Path) -> list[str]

**Docstring**

.. code-block:: text

   Llegeix i torna les vuit línies de capçalera estàndard EPW.

_build_epw_metadata
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:265``.

.. code-block:: python

   def _build_epw_metadata(epw_path: Path, header_lines: list[str]) -> dict[str, object]

**Docstring**

.. code-block:: text

   Crea metadades de fitxer i ubicació a partir de les línies de capçalera EPW.

_read_epw_data
~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:282``.

.. code-block:: python

   def _read_epw_data(epw_path: Path) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Llegeix les files de dades per hora EPW en un DataFrame sense processar.

_clean_epw_data
~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:296``.

.. code-block:: python

   def _clean_epw_data(data_frame: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Converteix EPW columnes numèriques i substituir EPW els sentinelles de valors que falten per NaN.

_add_time_features
~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:309``.

.. code-block:: python

   def _add_time_features(data_frame: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Afegeix segells de temps normalitzats i atributs de calendari utilitzades pels gràfics de visualització.

_add_climate_metadata
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:334``.

.. code-block:: python

   def _add_climate_metadata(metadata: dict[str, object], data_frame: pd.DataFrame) -> dict[str, object]

**Docstring**

.. code-block:: text

   Afegeix mètriques climàtiques derivades a les metadades EPW carregades.

list_epw_catalog
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:344``.

.. code-block:: python

   def list_epw_catalog(root_path_str: str) -> tuple[dict[str, str], ...]

**Docstring**

.. code-block:: text

   Escaneja un directori arrel i retorna entrades de catàleg cercables per a tots els fitxers EPW.

load_epw_bundle
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:378``.

.. code-block:: python

   def load_epw_bundle(epw_path_str: str) -> dict[str, object]

**Docstring**

.. code-block:: text

   Carrega un fitxer EPW i retorna'n les metadades més un clima enriquit DataFrame.

summarize_epw_metrics
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:395``.

.. code-block:: python

   def summarize_epw_metrics(data_frame: pd.DataFrame) -> dict[str, float]

**Docstring**

.. code-block:: text

   Retorna les mètriques del clima, el vent, la humitat, la pressió i la radiació.

build_monthly_summary
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:421``.

.. code-block:: python

   def build_monthly_summary(data_frame: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Agrupa les principals variables tèrmiques, d'humitat, de vent i solars per mes.

aggregate_epw_timeseries
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:447``.

.. code-block:: python

   def aggregate_epw_timeseries( data_frame: pd.DataFrame, variable_key: str, aggregation_label: str, ) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Agrega una variable EPW a la sèrie horària, diària, setmanal o mensual sol·licitada.

build_daily_temperature_profile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:475``.

.. code-block:: python

   def build_daily_temperature_profile(data_frame: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna els valors diaris mínims, mitjans i màxims de temperatura de bulb sec.

build_hourly_profile
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:491``.

.. code-block:: python

   def build_hourly_profile(data_frame: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna perfils horaris mitjans per a les principals variables meteorològiques.

build_heatmap_table
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:506``.

.. code-block:: python

   def build_heatmap_table(data_frame: pd.DataFrame, variable_key: str) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Crea una taula dinàmica mes a hora per a la variable EPW seleccionada.

build_annual_hourly_heatmap_table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:522``.

.. code-block:: python

   def build_annual_hourly_heatmap_table(data_frame: pd.DataFrame, variable_key: str) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Crea una taula dinàmica hora a dia de l'any per a la variable EPW seleccionada.

_solar_position_frame
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:539``.

.. code-block:: python

   def _solar_position_frame( data_frame: pd.DataFrame, latitude_deg: float, longitude_deg: float, timezone_hours: float, ) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Estima l'altitud i l'azimut solar per a cada fila horària EPW.

build_comfort_radiation_table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:605``.

.. code-block:: python

   def build_comfort_radiation_table(data_frame: pd.DataFrame, metadata: dict[str, object]) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Estima la radiació incident per orientació, ponderada pel benefici de calefacció o refrigeració.

_build_wind_rose_table
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:686``.

.. code-block:: python

   def _build_wind_rose_table(data_frame: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Freqüència del vent de retorn i velocitat mitjana agrupades en sectors de brúixola.

build_monthly_wind_rose_tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:717``.

.. code-block:: python

   def build_monthly_wind_rose_tables(data_frame: pd.DataFrame) -> dict[str, pd.DataFrame]

**Docstring**

.. code-block:: text

   Construeix una taula resum de la rosa dels vents per a cada mes natural.

build_download_frame
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/visor_epw_backend.py:729``.

.. code-block:: python

   def build_download_frame(data_frame: pd.DataFrame) -> pd.DataFrame

**Docstring**

.. code-block:: text

   Retorna les columnes EPW netes que s'exporten com a CSV des de UI.

