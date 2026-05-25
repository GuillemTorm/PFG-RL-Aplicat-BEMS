"""Metadades de l'aplicació per a l'espai de treball Streamlit de BEMS-RL Studio.

El punt d'entrada executable és :mod:`Inici`; les pàgines individuals viuen sota
``pages`` i Streamlit les carrega automàticament. Aquest mòdul es manté sense
efectes secundaris perquè la documentació i les eines de diagnòstic puguin
importar l'arrel de Studio sense renderitzar cap pàgina.
"""

from __future__ import annotations

APP_NAME = "BEMS-RL Studio"
APP_ENTRYPOINT = "Inici.py"

__all__ = ["APP_NAME", "APP_ENTRYPOINT"]
