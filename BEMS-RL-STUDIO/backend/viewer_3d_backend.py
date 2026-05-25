"""Backend del visor d'edificis 3D: processament de geometria i generació de figures Plotly."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import trimesh

SURFACE_STYLES: Dict[str, Dict[str, Any]] = {
    'Wall':      {'color': 'orange',   'opacity': 0.45},
    'Roof':      {'color': 'green',    'opacity': 0.45},
    'Floor':     {'color': 'blue',     'opacity': 0.35},
    'Ceiling':   {'color': 'purple',   'opacity': 0.35},
    'Window':    {'color': 'skyblue',  'opacity': 0.60},
    'Door':      {'color': '#8B4513', 'opacity': 0.90},
    'Glassdoor': {'color': 'cyan',     'opacity': 0.60},
    'Unknown':   {'color': 'darkgray', 'opacity': 0.50},
}
PV_STYLE_COLOR = "#222222"
PV_STYLE_OPACITY = 0.90


def extract_vertices_general(surface: dict) -> List[Tuple[float, float, float]]:
    """Extreu vèrtexs d'un dict de superfície.

    Admet tant una llista de "vèrtexs" com camps de coordenades indexats separats
    (vertex_N_x_coordinate / vertex_N_y_coordinate / vertex_N_z_coordinate).
    """
    vertices = []
    if "vertices" in surface:
        for vertex in surface["vertices"]:
            x = vertex.get("vertex_x_coordinate")
            y = vertex.get("vertex_y_coordinate")
            z = vertex.get("vertex_z_coordinate")
            if None not in (x, y, z):
                vertices.append((x, y, z))
    else:
        index = 1
        while f"vertex_{index}_x_coordinate" in surface:
            x = surface.get(f"vertex_{index}_x_coordinate")
            y = surface.get(f"vertex_{index}_y_coordinate")
            z = surface.get(f"vertex_{index}_z_coordinate")
            if None not in (x, y, z):
                vertices.append((x, y, z))
            index += 1
    return vertices


def _classify_type(surf_type_raw: str, kind: str) -> str:
    """Normalise a raw surface type string to a canonical type label."""
    surface_type = (surf_type_raw or "Unknown").strip().lower()
    if kind == "sub":
        if "door" in surface_type and "glass" in surface_type:
            return "Glassdoor"
        if "door" in surface_type:
            return "Door"
        return "Window"
    if "wall" in surface_type:
        return "Wall"
    if "roof" in surface_type:
        return "Roof"
    if "ceiling" in surface_type:
        return "Ceiling"
    if "floor" in surface_type:
        return "Floor"
    return "Unknown"


def _triangulate_fan(n: int) -> List[Tuple[int, int, int]]:
    """Retorna l'índex de triangulació en ventall triplicat per a un polígon convex amb n vèrtexs."""
    return [(0, i, i + 1) for i in range(1, n - 1)] if n >= 3 else []


def _tilt_azimuth_from_normal(
    nx: float, ny: float, nz: float
) -> Tuple[float, float, str]:
    """Calcula inclinació, azimut i orientació cardinal a partir d'una normal de superfície.

    Retorna:
        inclinació: Angle des de l'horitzontal en graus (0 = pla).
        azimut: en sentit horari des del nord en graus (0=N, 90=E, 180=S, 270=W).
        orientació: etiqueta cardinal ('N', 'NE', ..., 'H' per a gairebé horitzontal).
    """
    norm = float(np.linalg.norm([nx, ny, nz])) or 1e-9
    tilt = math.degrees(math.acos(abs(nz) / norm))
    azimuth = (math.degrees(math.atan2(nx, ny)) + 360.0) % 360.0
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
    index = int(((azimuth + 22.5) % 360) // 45)
    orientation = directions[index]
    if tilt < 15:
        orientation = 'H'
    return tilt, azimuth, orientation


def _polygon_mesh(vertices: List[Tuple[float, float, float]]) -> trimesh.Trimesh:
    """Crea una malla triangular mínima a partir d'una superfície EnergyPlus."""
    return trimesh.Trimesh(
        vertices=np.asarray(vertices, dtype=float),
        faces=np.asarray(_triangulate_fan(len(vertices)), dtype=np.int64),
        process=False,
    )


def _polygon_geometry(vertices: List[Tuple[float, float, float]]) -> Tuple[float, Tuple[float, float, float]]:
    """Retorna àrea i normal mitjana ponderada per àrea d'una superfície."""
    mesh = _polygon_mesh(vertices)
    if len(mesh.faces) == 0:
        return 0.0, (0.0, 0.0, 1.0)
    normal = np.average(mesh.face_normals, axis=0, weights=mesh.area_faces)
    return float(mesh.area), tuple(float(value) for value in trimesh.util.unitize(normal))


def _surface_hover_text(record: Dict[str, Any]) -> str:
    """Crea una etiqueta de flotació llegible pels humans per a un registre de superfície."""
    geometry_line = f"Area: {record['area']:.2f} m2"
    if record['orientation'] == 'H':
        orientation_line = f"Tilt: {record['tilt']:.1f} deg | Orientation: horizontal"
    else:
        orientation_line = (
            f"Tilt: {record['tilt']:.1f} deg | "
            f"Azimuth: {record['azimuth']:.1f} deg ({record['orientation']})"
        )
    return (
        f"Surface: {record['name']}<br>"
        f"Zone: {record['zone']}<br>"
        f"Type: {record['type']} ({record['kind']})<br>"
        f"{geometry_line}<br>"
        f"{orientation_line}"
    )


def _scaled_offset_polygon(
    vertices: List[Tuple[float, float, float]],
    offset: float = 0.05,
    shrink: float = 0.97,
) -> List[Tuple[float, float, float]]:
    """Retorna una còpia reduïda i amb desplaçament normal d'un polígon.

    Paràmetres:
        vèrtexs: vèrtexs de polígons originals.
        desplaçament: desplaçament al llarg de la unitat normal per evitar la lluita en z.
        contracció: factor d'escala [0..1] aplicat en relació al baricentre.
    """
    if not vertices:
        return vertices
    points = np.asarray(vertices, dtype=float)
    centroid = points.mean(axis=0)
    _area, normal = _polygon_geometry(vertices)
    output = []
    for point in points:
        shifted = centroid + shrink * (point - centroid) + np.asarray(normal) * offset
        output.append(tuple(float(value) for value in shifted))
    return output


def _collect_surfaces_with_names(epjson: dict) -> List[Dict[str, Any]]:
    """Recull totes les superfícies d'un epJSON dict.

    Retorna una llista de dicts amb claus: nom, zona, type_raw, tipus ('principal'/'sub'), vèrtexs.
    """
    output = []
    for name, surface in epjson.get("BuildingSurface:Detailed", {}).items():
        vertices = extract_vertices_general(surface)
        if len(vertices) >= 3:
            output.append({
                'name': name,
                'zone': surface.get("zone_name", "Unknown"),
                'type_raw': surface.get("surface_type", "Unknown"),
                'kind': 'main',
                'vertices': vertices,
            })
    for name, surface in epjson.get("FenestrationSurface:Detailed", {}).items():
        vertices = extract_vertices_general(surface)
        if len(vertices) >= 3:
            output.append({
                'name': name,
                'zone': surface.get("building_surface_name", "Unknown"),
                'type_raw': surface.get("surface_type", "Unknown"),
                'kind': 'sub',
                'vertices': vertices,
            })
    return output


def _bounds(
    vertices_list: List[List[Tuple[float, float, float]]],
) -> Tuple[float, float, float, float, float, float]:
    """Retorna (xmin, xmax, ymin, ymax, zmin, zmax) el quadre delimitador de tots els vèrtexs proporcionats."""
    points = [point for vertices in vertices_list for point in vertices]
    if not points:
        return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    bounds = trimesh.points.PointCloud(np.asarray(points, dtype=float)).bounds
    return (
        float(bounds[0][0]),
        float(bounds[1][0]),
        float(bounds[0][1]),
        float(bounds[1][1]),
        float(bounds[0][2]),
        float(bounds[1][2]),
    )


def _color_for(record: Dict[str, Any]) -> str:
    """Retorna el color de visualització d'un registre de superfície en funció del seu tipus canònic."""
    return SURFACE_STYLES.get(record['type'], SURFACE_STYLES['Unknown'])['color']


@st.cache_data(show_spinner=False)
def build_surface_records(epjson: dict) -> Dict[str, Any]:
    """Crea registres de superfície enriquits a partir d'un dic epJSON (emmagatzemat en memòria cau).

    Cada registre conté: id, nom, zona, tipus (normalitzat), tipus (principal/sub),
    vèrtexs originals, vèrtexs centrats, àrea, inclinació, azimut, orientació,
    i la mitjana z en coordenades centrades.

    Retorna un dict amb claus: registres, zones, tipus, centre, z_clip_range, name_index.
    El name_index mapes el nom de la superfície per registrar l'índex només per a les superfícies principals.
    """
    items = _collect_surfaces_with_names(epjson)
    vertices_list = [item['vertices'] for item in items]
    xmn, xmx, ymn, ymx, zmn, zmx = _bounds(vertices_list)
    cx = (xmn + xmx) / 2.0
    cy = (ymn + ymx) / 2.0
    cz = (zmn + zmx) / 2.0

    records: List[Dict[str, Any]] = []
    zones: set = set()
    types: set = set()
    name_index: Dict[str, int] = {}

    for index, item in enumerate(items):
        normalized_type = _classify_type(item['type_raw'], item['kind'])
        zones.add(item['zone'])
        types.add(normalized_type)

        area, (nx, ny, nz) = _polygon_geometry(item['vertices'])
        tilt, azimuth, orientation = _tilt_azimuth_from_normal(nx, ny, nz)
        vertices_c = [(x - cx, y - cy, z - cz) for (x, y, z) in item['vertices']]

        record: Dict[str, Any] = {
            'id': index,
            'name': item['name'],
            'zone': item['zone'],
            'type': normalized_type,
            'kind': item['kind'],
            'vertices': item['vertices'],
            'vertices_c': vertices_c,
            'area': area,
            'tilt': tilt,
            'azimuth': azimuth,
            'orientation': orientation,
            'z_mean_c': sum(v[2] for v in vertices_c) / len(vertices_c),
        }
        records.append(record)
        if item['kind'] == 'main':
            name_index[item['name']] = index

    z_values = [r['z_mean_c'] for r in records] or [0.0]
    return {
        'records': records,
        'zones': sorted(zones),
        'types': sorted(types),
        'center': (cx, cy, cz),
        'z_clip_range': (float(min(z_values)), float(max(z_values))),
        'name_index': name_index,
    }


def plot_3d_model(
    records: List[Dict[str, Any]],
    visible_types: Dict[str, bool],
    visible_zones: Dict[str, bool],
    z_clip: Tuple[float, float],
    pv_list: List[Dict[str, Any]],
    name_index: Dict[str, int],
) -> go.Figure:
    """Construeix una figura 3D Plotly de la geometria de l'edifici.

    Les superfícies es filtren per tipus, zona i rang de clip d'alçada.
    Els panells PV es representen com una capa addicional superposada a les seves superfícies host.
    """
    fig = go.Figure()
    zmin, zmax = z_clip

    for record in records:
        # El filtre es fa abans de crear traces perquè Plotly es torna lent si li passem
        # superfícies ocultes i després només les amaguem a la llegenda.
        if not visible_types.get(record['type'], False):
            continue
        if not visible_zones.get(record['zone'], False):
            continue
        if not (zmin <= record['z_mean_c'] <= zmax):
            continue

        vertices = record['vertices_c']
        x, y, z = zip(*vertices)
        # EnergyPlus dona polígons; Mesh3d necessita triangles. El fan és suficient per a
        # superfícies habituals d'edifici, que normalment són convexes o gairebé planes.
        triangles = _triangulate_fan(len(vertices))
        if not triangles:
            continue
        i_idx, j_idx, k_idx = zip(*triangles)
        color = _color_for(record)
        opacity = SURFACE_STYLES.get(record['type'], SURFACE_STYLES['Unknown'])['opacity']

        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i_idx, j=j_idx, k=k_idx,
            color=color, opacity=opacity,
            name=f"{record['zone']} - {record['type']}",
            hovertext=_surface_hover_text(record),
            hoverinfo='text',
            showscale=False,
        ))

        if record['kind'] == 'sub':
            fig.add_trace(go.Scatter3d(
                x=list(x) + [x[0]],
                y=list(y) + [y[0]],
                z=list(z) + [z[0]],
                mode='lines',
                line=dict(color='black', width=2),
                name="Subsurface edge",
                showlegend=False,
                hoverinfo='skip',
            ))

    if pv_list and visible_types.get('PV', False):
        for pv in pv_list:
            surface_name = pv.get('surface_name')
            if surface_name not in name_index:
                continue
            record = records[name_index[surface_name]]
            if not (zmin <= record['z_mean_c'] <= zmax):
                continue
            # El panell PV es dibuixa una mica separat i encongit perquè no faci z-fighting
            # amb la superfície de la coberta o façana que el suporta.
            pv_polygon = _scaled_offset_polygon(record['vertices_c'], offset=0.03, shrink=0.96)
            px, py, pz = zip(*pv_polygon)
            triangles = _triangulate_fan(len(pv_polygon))
            if not triangles:
                continue
            i_idx, j_idx, k_idx = zip(*triangles)
            fig.add_trace(go.Mesh3d(
                x=px, y=py, z=pz,
                i=i_idx, j=j_idx, k=k_idx,
                color=PV_STYLE_COLOR, opacity=PV_STYLE_OPACITY,
                name=f"PV - {pv.get('name')}",
                hovertext=(
                    f"Panel: {pv.get('name')}<br>"
                    f"Surface: {surface_name}<br>"
                    f"DC capacity: {pv.get('capacity_dc', '-')}"
                ),
                hoverinfo='text',
                showscale=False,
            ))
            fig.add_trace(go.Scatter3d(
                x=list(px) + [px[0]],
                y=list(py) + [py[0]],
                z=list(pz) + [pz[0]],
                mode='lines',
                line=dict(color='black', width=2),
                name="PV edge",
                showlegend=False,
                hoverinfo='skip',
            ))

    fig.update_layout(
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z", aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=0),
        height=550,
        showlegend=True,
    )
    return fig
