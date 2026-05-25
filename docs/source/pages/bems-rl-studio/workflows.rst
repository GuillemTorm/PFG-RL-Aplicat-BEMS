###########################
BEMS-RL Studio workflows
###########################

This section describes the application workflows as they are implemented in the
Studio backend. It is intended for contributors who need to extend a page,
diagnose a run, or understand where artefacts are produced.

Environment preparation
=======================

The environment workflow starts from building and weather assets and ends with a
Sinergym YAML configuration that can be registered and used by training,
simulation, evaluation and live-control pages.

.. graphviz::
   :caption: Environment authoring flow.

   digraph environment_flow {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     upload [label="Upload building\nand weather files"];
     inspect [label="Inspect variables,\nmeters, actuators"];
     configure [label="Build YAML\nconfiguration"];
     validate [label="Validate Gymnasium\nenvironment"];
     register [label="Register environment"];
     use [label="Use in training,\nsimulation or evaluation"];

     upload -> inspect -> configure -> validate -> register -> use;
   }

Training lifecycle
==================

Training is built around reproducibility. The UI collects an environment,
algorithm, reward, wrapper and runtime configuration. The backend turns that
state into a training workspace with scripts and metadata before execution.

.. graphviz::
   :caption: Training artefact lifecycle.

   digraph training_lifecycle {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     form [label="Training form"];
     state [label="Validated UI state"];
     workspace [label="Training workspace"];
     scripts [label="Reproducible scripts"];
     model [label="Saved model .zip"];
     logs [label="Progress and\nobservation logs"];

     form -> state -> workspace;
     workspace -> scripts;
     workspace -> model;
     workspace -> logs;
   }

Evaluation and live control
===========================

Evaluation and live-control pages share model-loading and action-space
compatibility checks. This protects the user from running a policy against an
environment with a different action contract than the one used during training.

Key backend responsibilities:

* resolve the intended environment from model metadata when possible;
* load Stable-Baselines3 models and optional ``VecNormalize`` statistics;
* compare model action spaces with the selected environment;
* format actions for display and for EnergyPlus execution;
* stream progress and warnings to Streamlit without blocking the page.

Results and reporting
=====================

The Results page reads persisted outputs, derives KPIs, and renders interactive
charts. The report backend reuses the same data-loading and figure-building
logic so that the downloadable report matches the dashboard.

.. graphviz::
   :caption: Results data path.

   digraph results_flow {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     progress [label="progress.csv"];
     observations [label="observations.csv"];
     loader [label="DashboardData"];
     kpis [label="KPIs"];
     figures [label="Plotly figures"];
     dashboard [label="Results dashboard"];
     report [label="HTML/PDF report"];

     progress -> loader;
     observations -> loader;
     loader -> kpis;
     loader -> figures;
     kpis -> dashboard;
     figures -> dashboard;
     kpis -> report;
     figures -> report;
   }

Report figure inclusion
-----------------------

Reports include every figure that can be backed by available data. Builders that
cannot produce a valid figure for a run are skipped instead of inserting empty
or misleading sections.

.. graphviz::
   :caption: Figure-selection path used by the report backend.

   digraph report_figure_selection {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25", nodesep="0.5", ranksep="0.7"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     data [label="DashboardData"];
     catalog [label="Available figure builders"];
     validate [label="Validate required columns\nand non-empty traces"];
     include [label="Include in report"];
     skip [label="Skip section"];
     html [label="Rendered HTML/PDF"];

     data -> catalog -> validate;
     validate -> include [label="has data"];
     validate -> skip [label="missing data"];
     include -> html;
   }

Live-control loop
=================

Live control is intentionally conservative. The model and environment contract
are checked before actions are sent to the EnergyPlus runtime, and progress is
streamed back to the page through explicit status objects.

.. graphviz::
   :caption: Live-control runtime loop.

   digraph live_control_loop {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25", nodesep="0.5", ranksep="0.7"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     model [label="SB3 model"];
     metadata [label="Model metadata"];
     env [label="Selected Sinergym env"];
     validate [label="Action-space\ncompatibility"];
     predict [label="Predict action"];
     step [label="EnergyPlus step"];
     status [label="Progress + warnings"];
     ui [label="Streamlit UI"];

     model -> metadata -> validate;
     env -> validate;
     validate -> predict -> step -> status -> ui;
     step -> predict [label="next observation"];
   }

Documentation services
======================

Docker Compose includes a single Studio documentation service. It runs a Sphinx
build for the BEMS-RL Studio guide and API reference. The local Sinergym
documentation site is intentionally not mounted or served by this project.

.. list-table::
   :header-rows: 1
   :widths: 28 24 48

   * - Service
     - Port
     - Content
   * - ``docs-studio``
     - ``8001``
     - BEMS-RL Studio guide, architecture, workflows and Studio API reference.

Useful commands:

.. code-block:: powershell

   docker compose up -d --build
   docker compose logs -f docs-studio

The application remains available on port ``8501`` while the documentation is
served on port ``8001``.
