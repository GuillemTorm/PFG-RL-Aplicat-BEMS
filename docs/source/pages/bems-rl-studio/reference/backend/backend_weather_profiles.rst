backend/weather_profiles.py
===========================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/weather_profiles.py``

**Module path:** ``backend.weather_profiles``

**Module docstring**

.. code-block:: text

   Anàlisi de perfils meteorològics i vista prèvia per crear entorns.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``csv``, ``dataclasses``, ``numpy``, ``pathlib``, ``plotly``, ``re``, ``typing``

Classes
-------

WeatherProfileSuggestion
~~~~~~~~~~~~~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:41``.

.. code-block:: python

   class WeatherProfileSuggestion

**Docstring**

.. code-block:: text

   Descriu un suggeriment de fitxer meteorològic per a la creació de l'entorn UI.

Functions
---------

_sanitize_weather_identifier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:21``.

.. code-block:: python

   def _sanitize_weather_identifier(raw_value: str, fallback: str) -> str

**Docstring**

.. code-block:: text

   Retorna un identificador estable en minúscules per a les claus del perfil meteorològic.

_unique_weather_identifier
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:28``.

.. code-block:: python

   def _unique_weather_identifier(base: str, used: set[str]) -> str

**Docstring**

.. code-block:: text

   Retorna un identificador meteorològic únic dins del conjunt proporcionat.

summarize_weather_file
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:51``.

.. code-block:: python

   def summarize_weather_file(weather_path: Path) -> Tuple[Optional[float], str]

**Docstring**

.. code-block:: text

   Analitza un fitxer EnergyPlus Weather (EPW) per suggerir una classificació climàtica.

   Paràmetres:
       weather_path (Path): camí cap al fitxer EPW.

   Retorna:
       Tuple[Optional[float], str]: una tupla que conté la temperatura mitjana de bulb sec (si s'analitza correctament),
       i una cadena de category ('calent', 'cool', 'mixt' o 'personalitzat').

_parse_epw_int
~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:88``.

.. code-block:: python

   def _parse_epw_int(value: str) -> Optional[int]

**Docstring**

.. code-block:: text

   Analitza un nombre enter d'una cel·la EPW tot tolerant les cadenes decimals.

_parse_epw_float
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:97``.

.. code-block:: python

   def _parse_epw_float(value: str) -> Optional[float]

**Docstring**

.. code-block:: text

   Analitza un nombre flotant d'una cel·la EPW i retorna None quan la cel·la no sigui vàlida.

_calculate_epw_day_of_year
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:106``.

.. code-block:: python

   def _calculate_epw_day_of_year(row: Sequence[str], fallback_index: int) -> int

**Docstring**

.. code-block:: text

   Retorna el dia de l'any basat en 1 representat per una fila de dades EPW.

load_epw_dry_bulb_series
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:121``.

.. code-block:: python

   def load_epw_dry_bulb_series(weather_path: Path) -> List[Dict[str, float]]

**Docstring**

.. code-block:: text

   Carrega els registres de temperatura de bulb sec cada hora des d'un fitxer meteorològic EPW.

   Paràmetres:
       weather_path (Path): camí cap al fitxer meteorològic EPW.

   Retorna:
       List[Dict[str, float]]: registres horàries amb dia de l'any, índex d'hores,
       i temperatura de bulb sec en graus centígrads. S'ometen files no vàlides.

_build_ornstein_uhlenbeck_noise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:160``.

.. code-block:: python

   def _build_ornstein_uhlenbeck_noise( row_count: int, sigma: float, mu: float, tau: float, *, seed: int = WEATHER_PREVIEW_RANDOM_SEED, ) -> np.ndarray

**Docstring**

.. code-block:: text

   Construeix un soroll determinista Ornstein-Uhlenbeck per al gràfic de vista prèvia del clima.

build_weather_temperature_preview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:185``.

.. code-block:: python

   def build_weather_temperature_preview( weather_path: Path, sigma: float, mu: float, tau: float, ) -> List[Dict[str, float]]

**Docstring**

.. code-block:: text

   Crea dades de vista prèvia de la temperatura diària per a la variació estocàstica del clima.

   La vista prèvia reflecteix la pertorbació meteorològica d'Ornstein-Uhlenbeck amb Sinergym
   una llavor aleatòria fixa, de manera que UI s'actualitza de manera previsible quan l'usuari canvia el
   controls sigma, mu o tau.

   Paràmetres:
       weather_path (Path): fitxer EPW utilitzat com a font climàtica base.
       sigma (float): paràmetre de desviació estàndard per al procés d'OU.
       mu (float): paràmetre mitjà per al procés d'OU.
       tau (float): paràmetre constant de temps per al procés d'OU, en hores.

   Retorna:
       List[Dict[str, float]]: temperatures mitjanes diàries per al EPW original,
       la vista prèvia modificada determinista i una banda sigma visual.

build_weather_temperature_preview_figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:260``.

.. code-block:: python

   def build_weather_temperature_preview_figure(preview_records: Sequence[Dict[str, float]]) -> go.Figure

**Docstring**

.. code-block:: text

   Crea la figura de previsualització anual de la temperatura per a la pàgina Afegeix un entorn.

   Paràmetres:
       preview_records (Sequence[Dict[str, float]]): dades de vista prèvia de la temperatura diària.

   Retorna:
       go.Figure: Plotly figura que compara la temperatura de bulb sec original i modificada.

build_weather_profile_suggestions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/weather_profiles.py:338``.

.. code-block:: python

   def build_weather_profile_suggestions(weather_paths: Sequence[Path]) -> List[WeatherProfileSuggestion]

**Docstring**

.. code-block:: text

   Crea configuracions de perfils per a fitxers meteorològics amb noms i categorització fàcils d'utilitzar.

   Paràmetres:
       weather_paths (Sequence[Path]): una col·lecció de camins que apunten a fitxers EPW.

   Retorna:
       List[WeatherProfileSuggestion]: Configuracions recomanades i resums climàtics per als fitxers.

