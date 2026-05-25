################
BEMS-RL Studio
################

BEMS-RL Studio is the Streamlit application layer included with this project. It
turns the Sinergym simulation stack into an operator-facing workspace for
building-energy reinforcement learning: users can inspect weather files, create
environments, train agents, evaluate policies, compare runs, and export
decision-ready reports.

The Studio documentation is separated from the core Sinergym documentation
because it has a different audience and lifecycle. Sinergym is the simulation
library; BEMS-RL Studio is the application that coordinates that library with
interactive pages, persisted artefacts, charts, and operational workflows.

Main capabilities
=================

.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * - Area
     - What it does
     - Main modules
   * - Weather exploration
     - Loads EPW files, normalizes climate data, and renders seasonal and hourly
       profiles before an environment is configured.
     - ``backend.visor_epw_backend``, ``backend.epw_figures``
   * - Environment authoring
     - Converts uploaded building files, detects available variables and meters,
       and writes Sinergym-compatible YAML configurations.
     - ``backend.afegir_entorn_*``
   * - Agent training
     - Builds training jobs, resolves wrappers and reward parameters, and stores
       reproducible training artefacts.
     - ``backend.entrenar_agent_*``, ``page_components.training_*``
   * - Evaluation and live control
     - Loads saved policies, validates action spaces, and streams live progress
       to the UI.
     - ``backend.avaluar_agent_backend``,
       ``backend.interaccionar_agent_backend``
   * - Results and reporting
     - Reads simulation outputs, derives KPIs, creates Plotly figures, and
       exports an HTML/PDF report.
     - ``backend.resultats_backend``,
       ``backend.resultats_report_backend``, ``backend.grafics``

Documentation map
=================

Use the architecture and workflow pages to understand the application, then use
the API reference to inspect the exact source files, functions, classes and
docstrings behind each workflow. The generated code reference is organized by
folder so the sidebar can be used as a file navigator.

.. toctree::
   :maxdepth: 2

   architecture
   workflows
   api
