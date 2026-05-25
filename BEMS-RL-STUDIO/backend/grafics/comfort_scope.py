"""Filtres d'abast de confort compartits per KPI, gràfics i informes.

Aquest fitxer decideix si una mètrica de confort s'ha de calcular sobre totes les hores o només sobre
les hores amb ocupació, i manté el mateix criteri al dashboard i als informes descarregables.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd


def derive_occupied_mask(obs: pd.DataFrame) -> Optional[pd.Series]:
    """Inferir una màscara booleana per als registres ocupats quan les dades ho proporcionen."""
    if obs is None or obs.empty:
        return None

    explicit_cols = (
        "occupied_hour",
        "people_occupant",
        "people_occupants",
        "occupancy",
        "occupants",
        "is_occupied",
    )
    for col in explicit_cols:
        if col in obs.columns:
            values = pd.to_numeric(obs[col], errors="coerce").fillna(0.0)
            return pd.Series(values > 0.0, index=obs.index)

    fuzzy_cols = [
        c for c in obs.columns
        if any(token in c.lower() for token in ("occupant", "occupancy", "people"))
    ]
    if fuzzy_cols:
        values = (
            obs[fuzzy_cols]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
            .sum(axis=1)
        )
        return pd.Series(values > 0.0, index=obs.index)

    return None


def has_occupied_data(obs: pd.DataFrame) -> bool:
    """Retorna si les observacions contenen prou dades d'ocupació per filtrar per àmbit."""
    return derive_occupied_mask(obs) is not None


def filter_by_comfort_scope(obs: pd.DataFrame, comfort_scope: str) -> pd.DataFrame:
    """Retorna totes les files o només les files ocupades en funció de l'àmbit seleccionat."""
    if comfort_scope != "occupied":
        return obs.copy()

    mask = derive_occupied_mask(obs)
    if mask is None:
        return obs.copy()
    return obs.loc[mask].copy()


def comfort_scope_label(comfort_scope: str) -> str:
    """Retorna l'etiqueta de visualització associada a un identificador d'abast de confort."""
    return "Occupied Hours" if comfort_scope == "occupied" else "All Hours"
