backend/entrenar_agent_session.py
=================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py``

**Module path:** ``backend.entrenar_agent_session``

**Module docstring**

.. code-block:: text

   Gestió de l'estat de sessió per a la pàgina d'entrenament de l'agent.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``streamlit``

Functions
---------

training_form_key
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:27``.

.. code-block:: python

   def training_form_key(field: str) -> str

**Docstring**

.. code-block:: text

   Retorna la clau d'estat de sessió per a un camp de formulari d'entrenament.

reset_widget_state_if_disabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:32``.

.. code-block:: python

   def reset_widget_state_if_disabled(field: str, disabled: bool, value=False) -> None

**Docstring**

.. code-block:: text

   Restableix l'estat de sessió d'un widget quan està desactivat.

ensure_select_state
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:38``.

.. code-block:: python

   def ensure_select_state(field: str, options: list[str], fallback: str | None = None) -> str

**Docstring**

.. code-block:: text

   Assegureu-vos que un camp de casella de selecció tingui un valor vàlid en estat de sessió.

   Si el valor actual no es troba a les opcions, se substitueix per una alternativa (si és vàlid)
   o per la primera opció.

selectbox_state_kwargs
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:55``.

.. code-block:: python

   def selectbox_state_kwargs(field: str, options: list, fallback=None) -> dict

**Docstring**

.. code-block:: text

   Retorna kwargs per a selectbox sense duplicar valor per defecte i session_state.

sanitize_multiselect_state
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:72``.

.. code-block:: python

   def sanitize_multiselect_state( field: str, options: list[str], fallback: list[str] | None = None, ) -> None

**Docstring**

.. code-block:: text

   Elimina valors obsolets d'un camp de selecció múltiple en estat de sessió.

   Els valors que ja no estan presents a les opcions s'eliminen. Si el resultat és
   buit i es proporciona una alternativa, s'utilitzen elements de reserva vàlids.

normalize_training_range_state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:96``.

.. code-block:: python

   def normalize_training_range_state() -> None

**Docstring**

.. code-block:: text

   Converteix els camps d'interval codificats per llista en tuples en estat de sessió.

   Streamlit serialitza les tuples lliscants com a llistes quan es restaura l'estat de la sessió
   d'una carrera guardada; aquesta funció els torna a convertir en tuples de manera que
   ``st.slider`` no genera cap desajust de tipus.

clear_incremental_widget_state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:110``.

.. code-block:: python

   def clear_incremental_widget_state() -> None

**Docstring**

.. code-block:: text

   Elimina totes les claus del widget incremental dinàmic de l'estat de sessió.

   Les claus s'identifiquen pel seu patró de prefix, que és generat per
   ``training_form_key`` per a cada widget incremental per variable.

apply_saved_training_ui_state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:127``.

.. code-block:: python

   def apply_saved_training_ui_state(ui_state: dict, envs: list[str]) -> None

**Docstring**

.. code-block:: text

   Restaura un estat d'entrenament desat anteriorment UI a l'estat de sessió.

   Primer esborra totes les claus del widget incrementals i després escriu cada camp des de
   ``ui_state``, converteix els camps d'interval en tuples i restableix l'entrenament
   temps d'execució perquè la configuració carregada tingui efecte a la següent execució.

seed_incremental_widget_defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:147``.

.. code-block:: python

   def seed_incremental_widget_defaults(selected_variables: list[str]) -> None

**Docstring**

.. code-block:: text

   Emplena els widgets incrementals per variable des de l'estat desat.

   Només escriu a claus d'estat de sessió que encara no existeixen, de manera que
   Els valors dels widgets en directe mai es sobreescriuen en tornar a renderitzar.

seed_discrete_incremental_widget_defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/entrenar_agent_session.py:177``.

.. code-block:: python

   def seed_discrete_incremental_widget_defaults(action_variables: list[str]) -> None

**Docstring**

.. code-block:: text

   Emplena els widgets incrementals discrets per variable des de l'estat desat.

   Només escriu a claus d'estat de sessió que encara no existeixen.

