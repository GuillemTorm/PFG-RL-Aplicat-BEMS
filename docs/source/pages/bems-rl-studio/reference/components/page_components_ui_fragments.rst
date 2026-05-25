page_components/ui_fragments.py
===============================

**Group:** Reusable Page Components

**Source:** ``BEMS-RL-STUDIO/page_components/ui_fragments.py``

**Module path:** ``page_components.ui_fragments``

**Module docstring**

.. code-block:: text

   Fragments UI compartits per pàgines Streamlit de BEMS-RL Studio.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``collections``, ``html``, ``streamlit``, ``time``, ``typing``

Functions
---------

render_hero
~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:13``.

.. code-block:: python

   def render_hero(class_name: str, kicker: str, title: str, copy_text: str | Iterable[str]) -> None

**Docstring**

.. code-block:: text

   Crea una capçalera hero amb les classes CSS de la pàgina.

render_section_title
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:29``.

.. code-block:: python

   def render_section_title(title: str, class_name: str = "page-section-title", level: int = 2) -> None

**Docstring**

.. code-block:: text

   Mostra un títol de secció escapant el text.

render_section_card
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:36``.

.. code-block:: python

   def render_section_card(title: str, description: str, *, title_class: str, card_class: str) -> None

**Docstring**

.. code-block:: text

   Combina títol de secció i una targeta descriptiva simple.

render_card_header
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:50``.

.. code-block:: python

   def render_card_header( target: Any, *, anchor_class: str, kicker: str, title: str, description: str = "", kicker_class: str = "upload-card-kicker", title_class: str = "upload-card-title", description_class: str = "upload-card-copy", ) -> None

**Docstring**

.. code-block:: text

   Pinta la capçalera HTML comuna d'una targeta Streamlit.

render_info_panel
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:79``.

.. code-block:: python

   def render_info_panel(class_name: str, title: str, kicker: str, copy_text: str) -> None

**Docstring**

.. code-block:: text

   Mostra un panell informatiu compacte.

render_metric_card_grid
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:94``.

.. code-block:: python

   def render_metric_card_grid( metrics: Iterable[tuple[Any, Any]], *, shell_class: str, card_class: str, label_class: str, value_class: str, formatter: Callable[[Any], str] | None = None, label_formatter: Callable[[Any], str] | None = None, ) -> None

**Docstring**

.. code-block:: text

   Mostra una graella HTML de targetes KPI compactes.

render_detail_list_card
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:127``.

.. code-block:: python

   def render_detail_list_card( *, title: str, rows: Iterable[tuple[Any, Any]], card_class: str, title_class: str, list_class: str, row_class: str, label_class: str, value_class: str, formatter: Callable[[Any], str] | None = None, label_formatter: Callable[[Any], str] | None = None, ) -> None

**Docstring**

.. code-block:: text

   Mostra una targeta de detalls amb parelles etiqueta/valor.

render_copy_block
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:164``.

.. code-block:: python

   def render_copy_block(class_name: str, text: str, *, formatter: Callable[[str], str] | None = None) -> None

**Docstring**

.. code-block:: text

   Mostra un bloc de text HTML escapant-ne el contingut.

render_metric_row
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:174``.

.. code-block:: python

   def render_metric_row( items: Iterable[dict[str, Any]], *, columns: int = 3, ) -> None

**Docstring**

.. code-block:: text

   Mostra mètriques Streamlit en columnes amb fallback informatiu.

build_metric_item
~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:200``.

.. code-block:: python

   def build_metric_item( current: dict, previous: dict | None, field: str | None, *, label: str, value_format: Callable[[Any], str], delta_format: Callable[[Any], str], empty_message: str, delta_color: str = "off", ) -> dict[str, Any]

**Docstring**

.. code-block:: text

   Prepara una mètrica declarativa a partir d'un camp opcional.

render_kicker_section
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:224``.

.. code-block:: python

   def render_kicker_section(class_name: str, title: str, kicker: str, description: str) -> None

**Docstring**

.. code-block:: text

   Munta una secció amb títol, kicker i text descriptiu.

render_runtime_progress
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:239``.

.. code-block:: python

   def render_runtime_progress( runtime: dict[str, Any], *, progress_label: str = "Progrés", freeze_from_result: bool = False, ) -> None

**Docstring**

.. code-block:: text

   Mostra barra i mètriques de progrés per a un runtime en segon pla.

_copy_html
~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:265``.

.. code-block:: python

   def _copy_html(copy_text: str | Iterable[str]) -> str

**Docstring**

.. code-block:: text

   No docstring available yet.

_elapsed_seconds
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/page_components/ui_fragments.py:271``.

.. code-block:: python

   def _elapsed_seconds(runtime: dict[str, Any], *, freeze_from_result: bool) -> int

**Docstring**

.. code-block:: text

   No docstring available yet.

