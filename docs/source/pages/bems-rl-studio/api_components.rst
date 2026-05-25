####################
Component API
####################

The ``page_components`` package contains import-safe Streamlit render helpers.
These functions are still UI-facing, but they are reusable across pages and can
be documented without importing the page entry points themselves.

Component composition
=====================

.. graphviz::
   :caption: Shared components used by the training and results pages.

   digraph component_map {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     training_entry [label="Entrenar_Agent page"];
     training_shared [label="training_shared"];
     training_agent [label="training_agent"];
     training_rewards [label="training_rewards"];
     training_wrappers [label="training_wrappers"];
     results_page [label="Results page"];
     results_dashboard [label="resultats_dashboard"];

     training_entry -> training_shared;
     training_entry -> training_agent;
     training_entry -> training_rewards;
     training_entry -> training_wrappers;
     results_page -> results_dashboard;
   }

.. automodule:: page_components.resultats_dashboard
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_components.training_agent
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_components.training_rewards
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_components.training_shared
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_components.training_wrappers
   :members:
   :undoc-members:
   :show-inheritance:
