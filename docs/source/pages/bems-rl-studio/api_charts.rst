########################
Charts and Metrics API
########################

The ``backend.grafics`` package owns the data-normalization and figure-building
layer used by the Results page and exported reports. Functions in this package
should accept explicit dataframe inputs and return deterministic KPI values,
normalized tables or Plotly figures.

Chart data pipeline
===================

.. graphviz::
   :caption: How raw Sinergym output becomes dashboard and report visuals.

   digraph chart_pipeline {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25", nodesep="0.5", ranksep="0.7"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     csv [label="progress.csv\nobservations.csv"];
     normalize [label="observation_columns\ntime_utils"];
     metrics [label="metrics\nkpis"];
     figures [label="battery, comfort,\ncontrol, hvac,\nthermal, heatmaps"];
     style [label="style"];
     dashboard [label="Streamlit dashboard"];
     report [label="HTML/PDF report"];

     csv -> normalize -> metrics -> figures;
     style -> figures;
     figures -> dashboard;
     figures -> report;
     metrics -> dashboard;
     metrics -> report;
   }

Data loading and normalization
==============================

.. automodule:: backend.grafics.data_loader
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.observation_columns
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.time_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.energy_units
   :members:
   :undoc-members:
   :show-inheritance:

KPIs and aggregated metrics
===========================

.. automodule:: backend.grafics.kpis
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.metrics
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.comfort_scope
   :members:
   :undoc-members:
   :show-inheritance:

Figure builders
===============

.. automodule:: backend.grafics.battery
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.comfort
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.control
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.episode
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.figures_zones
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.heatmaps
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.hvac
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.thermal
   :members:
   :undoc-members:
   :show-inheritance:

Styling and column helpers
==========================

.. automodule:: backend.grafics.column_utils
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: backend.grafics.style
   :members:
   :undoc-members:
   :show-inheritance:
