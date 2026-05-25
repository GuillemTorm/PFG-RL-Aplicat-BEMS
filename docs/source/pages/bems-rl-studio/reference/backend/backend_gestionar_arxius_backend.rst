backend/gestionar_arxius_backend.py
===================================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py``

**Module path:** ``backend.gestionar_arxius_backend``

**Module docstring**

.. code-block:: text

   Gestió de fitxers per a actius, models i dades meteorològiques de Studio.

   Aquest mòdul fa una còpia de seguretat de la pàgina del navegador de fitxers. Formata metadades del sistema de fitxers,
   resumeix els fitxers meteorològics EPW, descobreix artefactes de model entrenats i s'aplica
   operacions de còpia/supressió limitades utilitzades per la UI de Streamlit.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``dataclasses``, ``datetime``, ``os``, ``pandas``, ``pathlib``, ``shutil``, ``streamlit``

Classes
-------

ExplorerItem
~~~~~~~~~~~~

**Class.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:26``.

.. code-block:: python

   class ExplorerItem

**Docstring**

.. code-block:: text

   Fila del navegador de fitxers serialitzable que es mostra a la pàgina de gestió d'actius.

Functions
---------

get_size_format
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:35``.

.. code-block:: python

   def get_size_format(b, factor=1024, suffix="B")

**Docstring**

.. code-block:: text

   Retorna una mida compacta i llegible, com ara ``12.40KB``.

parse_epw_overview
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:45``.

.. code-block:: python

   def parse_epw_overview(epw_file)

**Docstring**

.. code-block:: text

   Llegeix les metadades d'ubicació i la temperatura mitjana del bulb sec d'un fitxer EPW.

load_weather_map_rows
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:66``.

.. code-block:: python

   def load_weather_map_rows(root_path_str)

**Docstring**

.. code-block:: text

   Retorna les files de fitxers meteorològics preparats per al mapa descobertes a continuació ``root_path_str``.

delete_item
~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:100``.

.. code-block:: python

   def delete_item(path_str)

**Docstring**

.. code-block:: text

   Suprimeix l'element.

list_explorer_items
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:114``.

.. code-block:: python

   def list_explorer_items(current_path, root_path, filter_func=None)

**Docstring**

.. code-block:: text

   Llista els elements de l'explorador.

filter_trainings
~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:155``.

.. code-block:: python

   def filter_trainings(name, is_dir, is_root)

**Docstring**

.. code-block:: text

   Entrenaments de filtre.

filter_models
~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:166``.

.. code-block:: python

   def filter_models(name, is_dir, is_root)

**Docstring**

.. code-block:: text

   Models de filtre.

filter_weather
~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:181``.

.. code-block:: python

   def filter_weather(name, is_dir, is_root)

**Docstring**

.. code-block:: text

   Filtre el temps.

filter_envs
~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/gestionar_arxius_backend.py:188``.

.. code-block:: python

   def filter_envs(name, is_dir, is_root)

**Docstring**

.. code-block:: text

   Filtre envs.

