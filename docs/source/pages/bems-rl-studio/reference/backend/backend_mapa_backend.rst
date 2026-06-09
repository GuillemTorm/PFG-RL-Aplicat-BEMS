backend/mapa_backend.py
=======================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/mapa_backend.py``

**Module path:** ``backend.mapa_backend``

**Module docstring**

.. code-block:: text

   Utilitats de representació de mapes compartides construïdes a pydeck i Streamlit.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``page_styles``, ``pandas``, ``pydeck``, ``streamlit``

Functions
---------

_chart_width
~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/mapa_backend.py:12``.

.. code-block:: python

   def _chart_width(use_container_width: bool) -> str

**Docstring**

.. code-block:: text

   Tradueix el flag antic de Streamlit al valor de width actual.

render_location_map
~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/mapa_backend.py:17``.

.. code-block:: python

   def render_location_map( latitude: float, longitude: float, *, zoom: float = 4.5, color: tuple[int, int, int, int] = (95, 84, 249, 220), radius: int = 22000, tooltip_html: str | None = None, use_container_width: bool = True, ) -> None

**Docstring**

.. code-block:: text

   Dibuixa un mapa de dispersió d'un sol punt centrat en les coordenades donades.

   tooltip_html accepta HTML preformatats (no calen referències de columna pydeck).

render_multipoint_map
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/mapa_backend.py:58``.

.. code-block:: python

   def render_multipoint_map( data_frame: pd.DataFrame, *, center_latitude: float | None = None, center_longitude: float | None = None, zoom: float = 2, color: tuple[int, int, int, int] = (255, 0, 0, 200), radius: int = 55000, tooltip_html: str | None = None, use_container_width: bool = True, ) -> None

**Docstring**

.. code-block:: text

   Dibuixa un mapa de dispersió de diversos punts des d'un DataFrame amb latitud/longitud.

   La vista es centra a les coordenades mitjanes tret que center_latitude/center_longitude
   es proporcionen de manera explícita. tooltip_html admet marcadors de posició de nom de columna pydeck
   (e.g. '<b>{file_name}</b><br/>{ciutat}').

