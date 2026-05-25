"""Lògica d'aplicació de BEMS-RL Studio segura per importar.

El paquet backend conté el codi que dona suport a la interfície Streamlit:
creació d'entorns, anàlisi climàtica, orquestració de l'entrenament, avaluació,
control en directe, agregació de resultats i generació d'informes. Els mòduls
d'aquest paquet eviten renderitzar la UI directament perquè es puguin importar
des de proves, scripts i Sphinx autodoc.
"""
