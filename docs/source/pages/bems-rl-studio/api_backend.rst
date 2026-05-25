########################
Backend API
########################

The backend package contains the operational logic of BEMS-RL Studio. These
modules are safe to import in tests and documentation builds: they perform data
loading, validation, model handling, environment preparation, simulation,
training orchestration and report generation outside the Streamlit page files.

Backend module map
==================

.. graphviz::
   :caption: Main backend module groups and the workflows they support.

   digraph backend_module_map {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25", nodesep="0.5", ranksep="0.7"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     assets [label="Building + weather assets"];
     environment [label="afegir_entorn_*"];
     training [label="entrenar_agent_*"];
     sb3 [label="sb3_utils"];
     evaluation [label="avaluar_agent_backend"];
     live [label="interaccionar_agent_backend"];
     results [label="resultats_backend"];
     reports [label="resultats_report_backend"];
     files [label="gestionar_arxius_backend"];
     epw [label="visor_epw_backend\nweather_profiles\nepw_figures"];
     sinergym [label="Sinergym environments"];
     artefacts [label="models, trainings,\nSinergym-logs"];

     assets -> environment -> sinergym;
     assets -> epw;
     environment -> training -> artefacts;
     sb3 -> evaluation;
     sb3 -> live;
     artefacts -> evaluation;
     artefacts -> live;
     artefacts -> results -> reports;
     files -> assets;
     files -> artefacts;
   }

Environment authoring
=====================

.. automodule:: backend.afegir_entorn_common
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.afegir_entorn_analysis
   :members:
   :undoc-members:
   :show-inheritance:

``backend.afegir_entorn_backend`` is a compatibility facade that re-exports the
split ``afegir_entorn_*`` modules for legacy page imports. Members are
documented in their owning modules below to avoid duplicate API targets.

.. automodule:: backend.afegir_entorn_config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.afegir_entorn_conversion
   :members:
   :undoc-members:
   :show-inheritance:

Training orchestration
======================

.. automodule:: backend.entrenar_agent_artifacts
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.entrenar_agent_charts
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.entrenar_agent_env
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.entrenar_agent_rewards
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.entrenar_agent_runtime
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.entrenar_agent_session
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.entrenar_agent_wrappers
   :members:
   :undoc-members:
   :show-inheritance:

Evaluation and live control
===========================

.. automodule:: backend.avaluar_agent_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.interaccionar_agent_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.sb3_utils
   :members:
   :undoc-members:
   :show-inheritance:

Simulation and inspection
=========================

.. automodule:: backend.simular_entorn_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.mostrar_entorn_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.viewer_3d_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.mapa_backend
   :members:
   :undoc-members:
   :show-inheritance:

Weather and EPW analysis
========================

.. automodule:: backend.visor_epw_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.weather_profiles
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.epw_figures
   :members:
   :undoc-members:
   :show-inheritance:

Results, reports and artefacts
==============================

.. automodule:: backend.resultats_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.resultats_report_backend
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.gestionar_arxius_backend
   :members:
   :undoc-members:
   :show-inheritance:

Shared paths and scripts
========================

.. automodule:: backend.common
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.training_scripts
   :members:
   :undoc-members:
   :show-inheritance:
