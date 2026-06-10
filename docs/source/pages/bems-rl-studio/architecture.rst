############################
BEMS-RL Studio architecture
############################

BEMS-RL Studio follows a deliberately thin-page architecture. Streamlit pages
own layout and user interaction, reusable page components own repeated UI
sections, and backend modules own data loading, validation, training orchestration
and figure generation. This keeps expensive simulation and artefact logic out of
the page files and makes the backend functions easier to test and document.

System overview
===============

.. graphviz::
   :caption: Runtime relationship between the Studio UI, backend helpers, Sinergym and persisted artefacts.

   digraph studio_architecture {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25", nodesep="0.55", ranksep="0.75"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     user [label="User"];
     pages [label="Streamlit pages\nBEMS-RL-STUDIO/pages"];
     components [label="Reusable components\npage_components"];
     backend [label="Application backends\nbackend"];
     charts [label="Chart layer\nbackend.grafics"];
     sinergym [label="Sinergym package\nGymnasium + EnergyPlus"];
     energyplus [label="EnergyPlus runtime"];
     artifacts [label="Artefacts\nmodels, trainings,\nSinergym-logs"];
     reports [label="HTML/PDF reports"];

     user -> pages [label="interacts"];
     pages -> components [label="renders"];
     pages -> backend [label="requests data/actions"];
     components -> backend [label="shared workflows"];
     backend -> charts [label="figures + KPIs"];
     backend -> sinergym [label="env creation"];
     sinergym -> energyplus [label="simulation"];
     backend -> artifacts [label="read/write"];
     charts -> reports [label="report figures"];
     artifacts -> charts [label="progress + observations"];
   }

Deployment topology
===================

The default Docker Compose setup separates the application runtime from the
Studio documentation site. Sinergym remains part of the application image as the
simulation library, but the local Sinergym documentation site is not mounted or
served by this project.

.. graphviz::
   :caption: Local Docker topology and exposed ports.

   digraph deployment_topology {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25", nodesep="0.5", ranksep="0.75"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     browser [label="Browser"];
     app [label="bemsrlstudio\nStreamlit\n:8501", fillcolor="#eef6ff", color="#78a3c7"];
     studio_docs [label="docs-studio\nSphinx\n:8001", fillcolor="#f8fbfa"];
     source [label="Shared source tree\nBEMS-RL-STUDIO + docs"];
     build [label="docs/build\nstudio/html"];

     browser -> app [label="use app"];
     browser -> studio_docs [label="Studio docs"];
     source -> app;
     source -> studio_docs;
     studio_docs -> build;
   }

Data ownership
==============

Studio modules are organized around the artefacts they own. Pages should call
the module that owns the relevant artefact instead of reading paths or parsing
CSV files directly.

.. graphviz::
   :caption: Data ownership across the Studio backend.

   digraph data_ownership {
     graph [rankdir=TB, bgcolor="transparent", pad="0.25", nodesep="0.45", ranksep="0.55"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     subgraph cluster_inputs {
       label="Inputs";
       color="#d8e7e4";
       buildings [label="IDF / epJSON"];
       weather [label="EPW weather"];
       yaml [label="YAML configuration"];
     }

     subgraph cluster_runtime {
       label="Runtime";
       color="#d8e7e4";
       training [label="Training workspace"];
       models [label="SB3 model zip"];
       vecnorm [label="VecNormalize pkl"];
     }

     subgraph cluster_outputs {
       label="Outputs";
       color="#d8e7e4";
       progress [label="progress.csv"];
       observations [label="observations.csv"];
       report [label="HTML/PDF report"];
     }

     env_backend [label="afegir_entorn_*"];
     train_backend [label="entrenar_agent_*"];
     eval_backend [label="avaluar_agent_backend\ninteraccionar_agent_backend"];
     result_backend [label="resultats_backend"];
     result_figures [label="resultats_figures\nbackend.grafics"];
     report_backend [label="resultats_report_backend"];

     buildings -> env_backend;
     weather -> env_backend;
     env_backend -> yaml;
     yaml -> train_backend;
     train_backend -> training;
     training -> models;
     training -> vecnorm;
     models -> eval_backend;
     vecnorm -> eval_backend;
     eval_backend -> progress;
     eval_backend -> observations;
     progress -> result_backend;
     observations -> result_backend;
     result_backend -> result_figures -> report_backend -> report;
   }

Package responsibilities
========================

``pages``
   Streamlit entry points. These files should stay focused on page composition,
   widget state and calling backend functions. The professional code reference
   parses them statically so their functions are documented without executing
   UI code during a Sphinx build.

``page_components``
   Shared Streamlit rendering functions for training forms, reward parameters,
   wrapper controls and the inline results dashboard.

``backend``
   Application logic. This package contains the code that can be documented with
   autodoc: data discovery, file conversion, environment configuration, training
   runtime management, evaluation loops, model loading, result aggregation and
   report generation.

``backend.grafics``
   Plotly figure builders and data-normalization helpers used by the Results
   page and report backend. Figure functions should accept already-loaded data
   and return configured Plotly figures without mutating page state.

``page_styles``
   CSS injection helpers that keep page-specific visual design outside the
   workflow code.

Import boundaries
=================

The most important boundary is between UI execution and importable logic:

.. graphviz::
   :caption: Import-safe boundary used by autodoc and tests.

   digraph import_boundary {
     graph [rankdir=TB, bgcolor="transparent", pad="0.25"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     pages [label="pages/*.py\nUI executes on import", fillcolor="#fff8ef", color="#d7a05c"];
     components [label="page_components\nimport-safe render helpers"];
     backend [label="backend\nimport-safe application logic"];
     styles [label="page_styles\nimport-safe CSS helpers"];
     autodoc [label="Sphinx autodoc", fillcolor="#eef6ff", color="#78a3c7"];
     staticref [label="Static AST reference", fillcolor="#f8fbfa"];

     pages -> components;
     pages -> backend;
     pages -> styles;
     autodoc -> components;
     autodoc -> backend;
     autodoc -> styles;
     staticref -> pages [label="documents without import"];
   }

Design conventions
==================

* Keep Streamlit session-state mutation at the page or runtime-boundary layer.
* Keep figure builders deterministic: inputs in, Plotly figure out.
* Keep filesystem decisions centralized in backend modules so Docker, local and
  production paths behave consistently.
* Preserve reproducibility by storing generated configs, wrapper selections,
  reward parameters and training scripts next to training artefacts.
* Document public helpers with docstrings that explain the UI workflow they
  support, not only their local implementation detail.
