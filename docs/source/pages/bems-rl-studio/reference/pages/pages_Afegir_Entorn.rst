pages/Afegir_Entorn.py
======================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py``

**Module path:** ``pages.Afegir_Entorn``

**Module docstring**

.. code-block:: text

   Sinergym Studio: vista per afegir entorns.

   Aquesta vista gestiona la UI de Streamlit per carregar models d'edifici
   EnergyPlus (.idf/.epJSON) i fitxers meteorològics (.epw), configurar els
   actuadors HVAC i la variabilitat climàtica, i registrar un entorn Gym nou a
   Sinergym mitjançant un fitxer YAML generat.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``backend``, ``importlib``, ``page_components``, ``page_styles``, ``pandas``, ``pathlib``, ``sidebar_nav``, ``streamlit``, ``subprocess``, ``typing``, ``yaml``

Functions
---------

render_add_environment_hero
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:59``.

.. code-block:: python

   def render_add_environment_hero() -> None

**Docstring**

.. code-block:: text

   Mostra la capçalera principal amb el mateix llenguatge visual de l'app.

render_weather_source_selector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:65``.

.. code-block:: python

   def render_weather_source_selector(target=st) -> str

**Docstring**

.. code-block:: text

   Mostra un control segmentat o un grup de ràdio per seleccionar la font meteorològica.

   Paràmetres:
       target: un contenidor Streamlit per vincular el widget. Per defecte a st.

   Retorna:
       str: El mode seleccionat ("Escollir existents" o "Pujar nous fitxers").

format_current_schedule_range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:98``.

.. code-block:: python

   def format_current_schedule_range(option) -> str

**Docstring**

.. code-block:: text

   Formata l'interval numèric vàlid d'un actuador per mostrar-lo en funció de la seva planificació inicial.

   Paràmetres:
       option (ActuatorOption): l'opció de l'actuador detectada des del model.

   Retorna:
       str: una cadena preformatada que presenta l'interval numèric detectat.

render_controller_selection_table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:118``.

.. code-block:: python

   def render_controller_selection_table( title: str, options, *, default_selected: bool, key: str, empty_message: str, )

**Docstring**

.. code-block:: text

   Mostra una taula interactiva per incloure/excloure controladors HVAC.

   Paràmetres:
       title (str): l'encapçalament que es mostra a sobre de la taula.
       options (Sequence[ActuatorOption]): les opcions de l'actuador disponibles.
       default_selected (bool): Si True, les caselles de selecció estan marcades inicialment.
       key (str): clau única d'estat de sessió Streamlit per a l'editor de dades.
       empty_message (str): Text alternativa quan no hi ha opcions per mostrar.

   Retorna:
       List[str]: una llista de les cadenes `option_id` seleccionades.

render_building_upload_card
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:178``.

.. code-block:: python

   def render_building_upload_card() -> Any

**Docstring**

.. code-block:: text

   Mostra la targeta d'upload de l'edifici i retorna el fitxer penjat.

   Retorna:
       Any: l'objecte del fitxer carregat Streamlit o None si no s'ha carregat cap fitxer.

render_weather_upload_card
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:201``.

.. code-block:: python

   def render_weather_upload_card() -> tuple[Path, Any]

**Docstring**

.. code-block:: text

   Mostra la targeta del fitxer meteorològic i torna el camí resolt al fitxer EPW seleccionat.

   Gestiona tant el selector de fitxers existents com els modes de càrrega de fitxers nous.
   Crida st.stop() si no hi ha cap fitxer meteorològic vàlid disponible o seleccionat.

   Retorna:
       tuple[Path, Any]: el camí del fitxer EPW seleccionat i el seu contenidor de la targeta Streamlit.

render_weather_variability_section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:270``.

.. code-block:: python

   def render_weather_variability_section() -> tuple[Optional[Dict], bool]

**Docstring**

.. code-block:: text

   Mostra la configuració opcional de variabilitat meteorològica estocàstica.

   Retorna:
       tuple[Optional[Dict], bool]: configuració de la variabilitat del clima i si
       les variants estocàstiques estan habilitades.

load_weather_temperature_preview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:308``.

.. code-block:: python

   def load_weather_temperature_preview( weather_path: str, weather_mtime_ns: int, sigma: float, mu: float, tau: float, ) -> List[Dict[str, float]]

**Docstring**

.. code-block:: text

   Carrega les dades de previsualització meteorològica anual a la memòria cau per al fitxer EPW seleccionat.

   Paràmetres:
       weather_path (str): camí cap al fitxer meteorològic EPW.
       weather_mtime_ns (int): marca de temps de modificació de fitxers utilitzada com a clau d'invalidació de la memòria cau.
       sigma (float): paràmetre de desviació estàndard per al procés d'OU.
       mu (float): paràmetre mitjà per al procés d'OU.
       tau (float): paràmetre constant de temps per al procés d'OU.

   Retorna:
       List[Dict[str, float]]: registres de previsualització diaris preparats per a la traça.

render_weather_temperature_preview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:332``.

.. code-block:: python

   def render_weather_temperature_preview( selected_weather_path: Path, weather_variability: Optional[Dict], ) -> None

**Docstring**

.. code-block:: text

   Mostra la previsualització anual de la temperatura EPW per als canvis meteorològics estocàstics.

   Paràmetres:
       selected_weather_path (Path): fitxer EPW seleccionat o carregat actualment.
       weather_variability (Optional[Dict]): configuració activa de la variabilitat del clima.

prepare_building_file
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:380``.

.. code-block:: python

   def prepare_building_file(uploaded_file: Any) -> tuple[Path, Path]

**Docstring**

.. code-block:: text

   Desa, actualitza si cal i converteix el fitxer de construcció penjat a epJSON.

   Utilitza l'estat de la sessió per emmagatzemar el resultat a la memòria cau i evitar el processament redundant en les reexecucions.
   Crida st.stop() per errors irrecuperables.

   Paràmetres:
       uploaded_file: l'objecte de fitxer carregat Streamlit per al model d'edifici.

   Retorna:
       Tuple[Path, Path]: el camí desat en brut (tmp_path) i el camí final epJSON (building_path).

load_or_run_training_analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:487``.

.. code-block:: python

   def load_or_run_training_analysis(building_path: Path, weather_path: Path)

**Docstring**

.. code-block:: text

   Retorna la memòria cau BuildingTrainingAnalysis o l'executa nova si les entrades han canviat.

   Paràmetres:
       building_path (Path): camí cap al model d'edifici epJSON.
       weather_path (Path): camí cap al fitxer meteorològic EPW.

   Retorna:
       BuildingTrainingAnalysis: Detectats termòstats, actuadors, variables i comptadors.

render_environment_id_section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:509``.

.. code-block:: python

   def render_environment_id_section( building_path: Path, weather_profiles: List[Dict], enable_stochastic: bool, ) -> str

**Docstring**

.. code-block:: text

   Mostra l'entrada d'ID base de l'entorn i previsualitza tots els ID que es registraran.

   Paràmetres:
       building_path (Path): S'utilitza per obtenir un nom base predeterminat de la base del fitxer.
       weather_profiles (List[Dict]): perfils meteorològics per calcular tots els ID generats.
       enable_stochastic (bool): si s'han d'incloure els ID de variants estocàstiques.

   Retorna:
       str: l'identificador de l'entorn base validat i netejat.

render_controller_selection_section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:551``.

.. code-block:: python

   def render_controller_selection_section(analysis) -> tuple[dict, list]

**Docstring**

.. code-block:: text

   Mostra la detecció del controlador i retorna els ID dels actuadors seleccionats.

   Crida st.stop() si no hi ha actuadors disponibles o no n'hi ha cap seleccionat.

   Paràmetres:
       analysis (BuildingTrainingAnalysis): resultat de l'anàlisi de l'edifici detectat.

   Retorna:
       Tuple[dict, list]: les opcions completes de l'actuador en forma de diccionari i la llista d'ID d'opcions seleccionades.

render_action_space_section
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:644``.

.. code-block:: python

   def render_action_space_section(actuator_options: dict, selected_actuator_ids: List[str]) -> dict

**Docstring**

.. code-block:: text

   Mostra l'editor de límits de l'espai d'acció i retorna els límits validats.

   Crida a st.stop() si algun actuador té un límit no vàlid (mínim >= màxim).

   Paràmetres:
       actuator_options (dict): Dict complet dels objectes ActuatorOption disponibles per ID.
       selected_actuator_ids (List[str]): ID dels actuadors seleccionats per l'usuari.

   Retorna:
       dict: Mapeig de option_id a tuples flotants (baix, alt).

render_registration_section
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:705``.

.. code-block:: python

   def render_registration_section( id_base: str, building_path: Path, tmp_path: Path, weather_profiles: List[Dict], analysis, actuator_options: dict, selected_actuator_ids: List[str], actuator_bounds: dict, weather_variability: Optional[Dict], ) -> None

**Docstring**

.. code-block:: text

   Gestiona el botó de registre, la creació i la validació de l'entorn.

   En cas d'èxit, mostra el YAML generat i executa una simulació de validació ràpida.
   En cas d'error, reverteix els fitxers escrits parcialment i mostra els detalls de l'error.

   Paràmetres:
       id_base (str): identificador de base netejat per al entorn.
       building_path (Path): Camí al fitxer de construcció epJSON preparat.
       tmp_path (Path): camí cap al fitxer de construcció original penjat.
       weather_profiles (List[Dict]): llista de perfils meteorològics utilitzat per a la generació de la configuració.
       analysis (BuildingTrainingAnalysis): resultat de l'anàlisi de l'edifici detectat.
       actuator_options (dict): totes les opcions de l'actuador detectades teclejades per option_id.
       selected_actuator_ids (List[str]): ID dels actuadors seleccionats per l'usuari.
       actuator_bounds (dict): Mapeig de option_id a tuples de lligat (baix, alt).
       weather_variability (Optional[Dict]): configuració de la variabilitat del clima estocàstic, o None.

main
~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Afegir_Entorn.py:799``.

.. code-block:: python

   def main() -> None

**Docstring**

.. code-block:: text

   Punt d'entrada a la pàgina Afegir Entorn Streamlit.

   Organitza el flux complet de la pàgina: estils, heroi, càrregues de fitxers, processament d'edificis,
   detecció d'actuadors, configuració de l'espai d'acció i registre de l'entorn.

