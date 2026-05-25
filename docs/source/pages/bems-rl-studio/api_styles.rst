################
Style API
################

The ``page_styles`` package keeps page-specific CSS away from workflow logic.
Each module exposes a small injection function that is called by the owning
Streamlit page.

Style ownership
===============

.. graphviz::
   :caption: Page-level ownership of style injection helpers.

   digraph style_map {
     graph [rankdir=LR, bgcolor="transparent", pad="0.25"];
     node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10, color="#8da7a1", fillcolor="#f8fbfa"];
     edge [fontname="Arial", fontsize=9, color="#60746f", arrowsize=0.8];

     pages [label="Streamlit pages"];
     styles [label="page_styles"];
     css [label="Injected CSS"];
     browser [label="Rendered UI"];

     pages -> styles -> css -> browser;
   }

.. automodule:: page_styles.afegir_entorn
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.gestionar_arxius
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.inici
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.interaccionar_agent
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.mostrar_entorn
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.reports
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.resultats
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.runtime_pages
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.sidebar
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.theme
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.training
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: page_styles.visor_climes_epw
   :members:
   :undoc-members:
   :show-inheritance:
