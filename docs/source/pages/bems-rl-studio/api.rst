############################
BEMS-RL Studio API reference
############################

This reference documents the Studio source tree by file. The generated
:doc:`reference/index` section appears in the sidebar as folders and file pages;
each file page lists its imports, classes, functions, signatures, docstrings and
source line numbers. Streamlit pages are parsed statically so documentation
builds can show page functions without executing UI code.

The autodoc pages remain available for import-safe backend, chart, component and
style modules when you want Sphinx to render Python API objects directly.

Reference map
=============

.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * - Section
     - Scope
     - Typical reader question
   * - :doc:`api_backend`
     - Environment authoring, training, evaluation, live control, reports,
       file management and shared SB3 utilities.
     - "Which function loads this model, validates this environment or builds
       this report?"
   * - :doc:`api_charts`
     - Plotly figure builders, KPI calculations, observation-column normalization
       and result metric aggregation.
     - "Which dataframe columns does this chart expect, and what does it
       return?"
   * - :doc:`api_components`
     - Import-safe Streamlit component renderers used by multiple pages.
     - "Where is this repeated UI section composed?"
   * - :doc:`api_styles`
     - CSS injection helpers for page-specific visual design.
     - "Which style module owns this page's visual layer?"

.. toctree::
   :maxdepth: 3

   reference/index
   api_backend
   api_charts
   api_components
   api_styles
