# -*- coding: utf-8 -*-
"""Detecció i filtratge de zones per als panells de resultats.

Aquest mòdul detecta zones tèrmiques des de la configuració de YAML o de la columna d'observació
patrons, i mapes les columnes de la zona seleccionada als camps genèrics que fan servir
les figures comunes.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import re

import pandas as pd

# Patrons flexibles per detectar variables de zona sense dependre d'un únic prefix.
VAR_PATTERNS: Dict[str, re.Pattern] = {
    # temperatura interior de la zona
    "air_temperature": re.compile(r"(?i)(?:^|_)air[_]?temperature(?:$|_)"),
    # consignes
    "htg_setpoint":   re.compile(r"(?i)(?:^|_)htg[_]?setpoint(?:$|_)|(?:^|_)heating[_]?setpoint(?:$|_)"),
    "clg_setpoint":   re.compile(r"(?i)(?:^|_)clg[_]?setpoint(?:$|_)|(?:^|_)cooling[_]?setpoint(?:$|_)"),
    # violació (si la registres per zona)
    "temp_violation": re.compile(r"(?i)(?:^|_)temp[_]?violation(?:$|_)"),
    # opcional (no es fan servir a les figures, però ajuda a detectar zones)
    "air_humidity":   re.compile(r"(?i)(?:^|_)air[_]?humidity(?:$|_)"),
    "people":         re.compile(r"(?i)(?:^|_)people(?:$|_)|(?:^|_)occupant(?:$|_)"),
}

# Quines variables mapejarem a genèriques per a les figures
GENERIC_MAP_KEYS = ("air_temperature", "htg_setpoint", "clg_setpoint", "temp_violation")


# Detecció de zones a partir del YAML o dels noms de columna.
def _zones_from_yaml(yaml_cfg: Optional[dict]) -> List[str]:
    """Zones definides a YAML sota variables→air_temperature→keys."""
    if not yaml_cfg or not isinstance(yaml_cfg.get("variables"), dict):
        return []
    for var_name, var_def in yaml_cfg["variables"].items():
        if str(var_def.get("variable_names")).lower() == "air_temperature":
            keys = var_def.get("keys")
            if isinstance(keys, list) and keys:
                return [str(k).strip() for k in keys if str(k).strip()]
            if isinstance(keys, str) and keys.strip():
                return [keys.strip()]
    return []


def _try_extract_zone_name(col: str, pattern: re.Pattern) -> Optional[str]:
    """
    Donada una columna i un patró de variable (p.ex. air_temperature),
    retorna el 'nom de zona' eliminant aquesta part.
    Exemple: 'zone1_office_air_temperature' -> 'zone1_office'
    """
    m = pattern.search(col)
    if not m:
        return None
    start, end = m.span()
    # Retirem el separador '_' veí si cal
    prefix = (col[:start].rstrip("_"))
    suffix = (col[end:].lstrip("_"))
    # Preferim el prefix (estil 'zone1_office_air_temperature').
    zone = prefix if prefix else suffix
    zone = zone.strip("_")
    return zone or None


def _zones_from_columns(obs: pd.DataFrame) -> List[str]:
    """Infereix zones a partir de columnes que contenen variables de zona conegudes."""
    candidate_sets: List[set] = []
    for var, pat in VAR_PATTERNS.items():
        cols = [c for c in obs.columns if pat.search(c)]
        zones = set()
        for c in cols:
            z = _try_extract_zone_name(c, pat)
            if z:
                zones.add(z)
        if len(zones) >= 2:
            candidate_sets.append(zones)

    if not candidate_sets:
        # Últim recurs: busca *_air_temperature estrictament al final
        zones = set()
        for c in obs.columns:
            if c.endswith("_air_temperature"):
                zones.add(c[: -len("_air_temperature")])
        return sorted(zones)

    # Tria el conjunt amb més cobertura (més zones detectades)
    zones = max(candidate_sets, key=len)
    return sorted(zones)


def detect_zones(obs: pd.DataFrame, yaml_cfg: Optional[dict] = None) -> List[str]:
    """API pública de detecció de zones."""
    zones = _zones_from_yaml(yaml_cfg)
    if zones:
        return zones
    return _zones_from_columns(obs)


# Mapatge de columnes originals cap a noms genèrics per zona.
def _zone_columns(obs: pd.DataFrame, zone: str) -> Dict[str, str]:
    """
    Per una zona concreta, retorna un mapatge {var_key -> nom_columna} segons VAR_PATTERNS.
    Exemple: {'air_temperature': 'zone1_office_air_temperature', ...}
    """
    mapping: Dict[str, str] = {}
    for key, pat in VAR_PATTERNS.items():
        for c in obs.columns:
            if pat.search(c):
                z = _try_extract_zone_name(c, pat)
                if z and z.lower() == zone.lower():
                    # si hi ha duplicats, manté el primer (ordre del CSV)
                    mapping.setdefault(key, c)
    return mapping


def filter_obs_by_zone(obs: pd.DataFrame, zone: Optional[str], yaml_cfg: Optional[dict] = None) -> pd.DataFrame:
    """Retorna les observacions assignades a la zona seleccionada.

    Es conserven les columnes globals, s'eliminen les columnes que pertanyen a altres zones,
    i els valors de la zona seleccionada s'exposen mitjançant els noms genèrics utilitzats per
    Constructors de figures comuns: ``air_temperature``, ``htg_setpoint``,
    ``clg_setpoint`` i ``temp_violation``.
    """
    zones = detect_zones(obs, yaml_cfg)
    if not zone or len(zones) <= 1 or zone not in zones:
        return obs

    # Construïm llistat de columnes de zona vs globals. No podem fiar-nos només del prefix
    # perquè alguns CSV barregen noms de zona, alias i variables globals al mateix fitxer.
    zone_cols_by_zone: Dict[str, set] = {z: set() for z in zones}
    for key, pat in VAR_PATTERNS.items():
        for c in obs.columns:
            if pat.search(c):
                z = _try_extract_zone_name(c, pat)
                if z in zone_cols_by_zone:
                    zone_cols_by_zone[z].add(c)

    keep_cols: List[str] = []
    for c in obs.columns:
        # Si pertany a alguna zona…
        matched_zone = None
        for z, cols in zone_cols_by_zone.items():
            if c in cols:
                matched_zone = z
                break
        if matched_zone is None:
            # global
            keep_cols.append(c)
        elif matched_zone == zone:
            keep_cols.append(c)
        # si és d'una altra zona, s'omet

    out = obs[keep_cols].copy()

    # Mapem la zona triada a noms genèrics perquè les figures comunes no hagin de saber
    # com es deia originalment cada columna al CSV.
    mapping = _zone_columns(out, zone)
    for key in GENERIC_MAP_KEYS:
        col = mapping.get(key)
        if col and col in out.columns:
            out[key] = out[col]

    # Evita que _ensure_air_temperature faci mitjanes entre zones
    # Si tenim la genèrica 'air_temperature', podem eliminar altres *_air_temperature
    if "air_temperature" in out.columns:
        candidates = [c for c in out.columns if VAR_PATTERNS["air_temperature"].search(c)]
        for c in candidates:
            if c != mapping.get("air_temperature"):
                # Drop amb errors='ignore' per si ja no hi és
                out.drop(columns=[c], inplace=True, errors="ignore")

    return out


# Opcions de zona per als selectors de la interfície.
def get_zone_options(obs: pd.DataFrame, yaml_cfg: Optional[dict] = None) -> List[Dict[str, str]]:
    """Retorna les opcions de zona."""
    zones = detect_zones(obs, yaml_cfg)
    return [{"label": z, "value": z} for z in zones]
