pages/Gestionar_Arxius.py
=========================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py``

**Module path:** ``pages.Gestionar_Arxius``

**Module docstring**

.. code-block:: text

   No docstring available yet.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``datetime``, ``html``, ``io``, ``page_components``, ``page_styles``, ``pathlib``, ``sidebar_nav``, ``streamlit``, ``time``, ``zipfile``

Functions
---------

render_weather_view_selector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:37``.

.. code-block:: python

   def render_weather_view_selector() -> str

**Docstring**

.. code-block:: text

   Mostra el selector de vista del bloc de climes sense ràdios.

build_selection_archive
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:55``.

.. code-block:: python

   def build_selection_archive(selected_paths: list[str]) -> bytes

**Docstring**

.. code-block:: text

   Construeix un zip en memòria amb els elements seleccionats.

build_download_name
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:89``.

.. code-block:: python

   def build_download_name(key_prefix: str) -> str

**Docstring**

.. code-block:: text

   Construeix un nom de fitxer estable per a la descàrrega.

clear_prepared_archive_if_stale
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:96``.

.. code-block:: python

   def clear_prepared_archive_if_stale(key_prefix: str, selection_signature: tuple[str, ...]) -> None

**Docstring**

.. code-block:: text

   Neteja l'arxiu preparat si la selecció actual ja no coincideix.

delete_items
~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:112``.

.. code-block:: python

   def delete_items(items: list[str]) -> None

**Docstring**

.. code-block:: text

   Esborra els elements seleccionats mostrant progrés.

handle_uploaded_files
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:132``.

.. code-block:: python

   def handle_uploaded_files(current_path: Path, uploaded_files) -> None

**Docstring**

.. code-block:: text

   Desa els fitxers pujats a la ruta actual de l'explorador.

navigate_file_explorer_up
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:149``.

.. code-block:: python

   def navigate_file_explorer_up(path_key: str, current_path: Path, root_path: Path) -> None

**Docstring**

.. code-block:: text

   Mou l'explorador de fitxers un directori cap amunt sense sortir de l'arrel.

navigate_file_explorer_into
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:158``.

.. code-block:: python

   def navigate_file_explorer_into(path_key: str, folder_path: str) -> None

**Docstring**

.. code-block:: text

   Mou l'explorador de fitxers cap a una carpeta filla.

render_explorer
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Gestionar_Arxius.py:163``.

.. code-block:: python

   def render_explorer( key_prefix: str, root_path: Path, filter_func=None, allow_nav_up: bool = True, allow_upload: bool = False, upload_label: str | None = None, upload_types: list[str] | None = None, upload_help: str | None = None, ) -> None

**Docstring**

.. code-block:: text

   Mostra l'explorador de fitxers per a cada categoria.

