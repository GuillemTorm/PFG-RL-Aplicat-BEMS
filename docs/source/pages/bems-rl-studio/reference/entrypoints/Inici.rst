Inici.py
========

**Group:** Application Entry Points

**Source:** ``BEMS-RL-STUDIO/Inici.py``

**Module path:** ``Inici``

**Module docstring**

.. code-block:: text

   Pàgina inicial de BEMS-RL STUDIO.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``base64``, ``html``, ``page_styles``, ``pathlib``, ``sidebar_nav``, ``streamlit``, ``subprocess``

Functions
---------

get_energyplus_logo_data_uri
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:40``.

.. code-block:: python

   def get_energyplus_logo_data_uri() -> str

**Docstring**

.. code-block:: text

   Carrega el logo d'EnergyPlus com a data URI per incrustar-lo a la UI.

detect_energyplus_status
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:51``.

.. code-block:: python

   def detect_energyplus_status() -> tuple[bool, str]

**Docstring**

.. code-block:: text

   Retorna si EnergyPlus està disponible i el missatge per mostrar a la UI.

render_hero
~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:68``.

.. code-block:: python

   def render_hero() -> None

**Docstring**

.. code-block:: text

   Mostra el bloc principal de presentació.

render_status_panel
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:84``.

.. code-block:: python

   def render_status_panel(energyplus_available: bool, energyplus_message: str) -> None

**Docstring**

.. code-block:: text

   Mostra l'estat d'EnergyPlus amb una targeta visual.

render_navigation_panel
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:108``.

.. code-block:: python

   def render_navigation_panel() -> None

**Docstring**

.. code-block:: text

   Dibuixa la pista de navegació lateral.

render_capability_card
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:124``.

.. code-block:: python

   def render_capability_card(index: int, capability: str) -> None

**Docstring**

.. code-block:: text

   Crea una targeta de funcionalitat.

render_capability_grid
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:139``.

.. code-block:: python

   def render_capability_grid() -> None

**Docstring**

.. code-block:: text

   Organitza les funcionalitats en files de tres targetes alineades.

render_organization_footer
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:156``.

.. code-block:: python

   def render_organization_footer() -> None

**Docstring**

.. code-block:: text

   Afegeix el bloc informatiu final.

render_home_page
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/Inici.py:178``.

.. code-block:: python

   def render_home_page() -> None

**Docstring**

.. code-block:: text

   Munta la pàgina inicial.

