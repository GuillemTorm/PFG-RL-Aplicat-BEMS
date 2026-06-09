backend/viewer_3d_backend.py
============================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py``

**Module path:** ``backend.viewer_3d_backend``

**Module docstring**

.. code-block:: text

   Backend del visor d'edificis 3D: processament de geometria i generació de figures Plotly.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``math``, ``numpy``, ``plotly``, ``streamlit``, ``trimesh``, ``typing``

Functions
---------

extract_vertices_general
~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:27``.

.. code-block:: python

   def extract_vertices_general(surface: dict) -> List[Tuple[float, float, float]]

**Docstring**

.. code-block:: text

   Extreu vèrtexs d'un dict de superfície.

   Admet tant una llista de "vèrtexs" com camps de coordenades indexats separats
   (vertex_N_x_coordinate / vertex_N_y_coordinate / vertex_N_z_coordinate).

_classify_type
~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:53``.

.. code-block:: python

   def _classify_type(surf_type_raw: str, kind: str) -> str

**Docstring**

.. code-block:: text

   Normalise a raw surface type string to a canonical type label.

_triangulate_fan
~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:73``.

.. code-block:: python

   def _triangulate_fan(n: int) -> List[Tuple[int, int, int]]

**Docstring**

.. code-block:: text

   Retorna l'índex de triangulació en ventall triplicat per a un polígon convex amb n vèrtexs.

_tilt_azimuth_from_normal
~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:78``.

.. code-block:: python

   def _tilt_azimuth_from_normal( nx: float, ny: float, nz: float ) -> Tuple[float, float, str]

**Docstring**

.. code-block:: text

   Calcula inclinació, azimut i orientació cardinal a partir d'una normal de superfície.

   Retorna:
       inclinació: Angle des de l'horitzontal en graus (0 = pla).
       azimut: en sentit horari des del nord en graus (0=N, 90=E, 180=S, 270=W).
       orientació: etiqueta cardinal ('N', 'NE', ..., 'H' per a gairebé horitzontal).

_polygon_mesh
~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:99``.

.. code-block:: python

   def _polygon_mesh(vertices: List[Tuple[float, float, float]]) -> trimesh.Trimesh

**Docstring**

.. code-block:: text

   Crea una malla triangular mínima a partir d'una superfície EnergyPlus.

_polygon_geometry
~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:108``.

.. code-block:: python

   def _polygon_geometry(vertices: List[Tuple[float, float, float]]) -> Tuple[float, Tuple[float, float, float]]

**Docstring**

.. code-block:: text

   Retorna àrea i normal mitjana ponderada per àrea d'una superfície.

_surface_hover_text
~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:117``.

.. code-block:: python

   def _surface_hover_text(record: Dict[str, Any]) -> str

**Docstring**

.. code-block:: text

   Crea una etiqueta de flotació llegible pels humans per a un registre de superfície.

_scaled_offset_polygon
~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:136``.

.. code-block:: python

   def _scaled_offset_polygon( vertices: List[Tuple[float, float, float]], offset: float = 0.05, shrink: float = 0.97, ) -> List[Tuple[float, float, float]]

**Docstring**

.. code-block:: text

   Retorna una còpia reduïda i amb desplaçament normal d'un polígon.

   Paràmetres:
       vèrtexs: vèrtexs de polígons originals.
       desplaçament: desplaçament al llarg de la unitat normal per evitar la lluita en z.
       contracció: factor d'escala [0..1] aplicat en relació al baricentre.

_collect_surfaces_with_names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:160``.

.. code-block:: python

   def _collect_surfaces_with_names(epjson: dict) -> List[Dict[str, Any]]

**Docstring**

.. code-block:: text

   Recull totes les superfícies d'un epJSON dict.

   Retorna una llista de dicts amb claus: nom, zona, type_raw, tipus ('principal'/'sub'), vèrtexs.

_bounds
~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:189``.

.. code-block:: python

   def _bounds( vertices_list: List[List[Tuple[float, float, float]]], ) -> Tuple[float, float, float, float, float, float]

**Docstring**

.. code-block:: text

   Retorna (xmin, xmax, ymin, ymax, zmin, zmax) el quadre delimitador de tots els vèrtexs proporcionats.

_color_for
~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:207``.

.. code-block:: python

   def _color_for(record: Dict[str, Any]) -> str

**Docstring**

.. code-block:: text

   Retorna el color de visualització d'un registre de superfície en funció del seu tipus canònic.

build_surface_records
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:213``.

.. code-block:: python

   def build_surface_records(epjson: dict) -> Dict[str, Any]

**Docstring**

.. code-block:: text

   Crea registres de superfície enriquits a partir d'un dic epJSON (emmagatzemat en memòria cau).

   Cada registre conté: id, nom, zona, tipus (normalitzat), tipus (principal/sub),
   vèrtexs originals, vèrtexs centrats, àrea, inclinació, azimut, orientació,
   i la mitjana z en coordenades centrades.

   Retorna un dict amb claus: registres, zones, tipus, centre, z_clip_range, name_index.
   El name_index mapes el nom de la superfície per registrar l'índex només per a les superfícies principals.

plot_3d_model
~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/viewer_3d_backend.py:273``.

.. code-block:: python

   def plot_3d_model( records: List[Dict[str, Any]], visible_types: Dict[str, bool], visible_zones: Dict[str, bool], z_clip: Tuple[float, float], pv_list: List[Dict[str, Any]], name_index: Dict[str, int], ) -> go.Figure

**Docstring**

.. code-block:: text

   Construeix una figura 3D Plotly de la geometria de l'edifici.

   Les superfícies es filtren per tipus, zona i rang de clip d'alçada.
   Els panells PV es representen com una capa addicional superposada a les seves superfícies host.

