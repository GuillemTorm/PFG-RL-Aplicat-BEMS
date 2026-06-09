pages/Simular_Entorn.py
=======================

**Group:** Streamlit Pages

**Source:** ``BEMS-RL-STUDIO/pages/Simular_Entorn.py``

**Module path:** ``pages.Simular_Entorn``

**Module docstring**

.. code-block:: text

   No docstring available yet.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``backend``, ``functools``, ``html``, ``page_components``, ``page_styles``, ``queue``, ``sidebar_nav``, ``streamlit``, ``threading``, ``time``, ``traceback``

Functions
---------

_key
~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:29``.

.. code-block:: python

   def _key(name: str) -> str

**Docstring**

.. code-block:: text

   Key.

empty_baseline_runtime
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:33``.

.. code-block:: python

   def empty_baseline_runtime() -> dict[str, object]

**Docstring**

.. code-block:: text

   Temps d'execució de base buit.

ensure_baseline_runtime
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:56``.

.. code-block:: python

   def ensure_baseline_runtime() -> dict[str, object]

**Docstring**

.. code-block:: text

   Assegureu-vos el temps d'execució de referència.

reset_baseline_runtime
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:64``.

.. code-block:: python

   def reset_baseline_runtime() -> dict[str, object]

**Docstring**

.. code-block:: text

   Restableix el temps d'execució de referència.

drain_baseline_runtime
~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:75``.

.. code-block:: python

   def drain_baseline_runtime(runtime: dict[str, object]) -> None

**Docstring**

.. code-block:: text

   Esgota el temps d'execució de la línia base.

sync_baseline_runtime
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:128``.

.. code-block:: python

   def sync_baseline_runtime() -> dict[str, object]

**Docstring**

.. code-block:: text

   Sincronitza el temps d'execució de referència.

consume_baseline_rerun_flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:135``.

.. code-block:: python

   def consume_baseline_rerun_flag(runtime: dict[str, object] | None = None) -> bool

**Docstring**

.. code-block:: text

   Consumeix la bandera de repetició de la línia de base.

request_baseline_stop
~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:144``.

.. code-block:: python

   def request_baseline_stop(runtime: dict[str, object] | None = None) -> bool

**Docstring**

.. code-block:: text

   Sol·licita l'aturada de la línia de base.

push_baseline_progress_event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:160``.

.. code-block:: python

   def push_baseline_progress_event( event_queue: "queue.Queue[dict[str, object]]", job_config: dict[str, object], step_number: int, total_steps: int, ) -> None

**Docstring**

.. code-block:: text

   Envieu un esdeveniment de progrés de referència a la cua de temps d'execució de la pàgina.

baseline_worker
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:177``.

.. code-block:: python

   def baseline_worker( job_config: dict[str, object], event_queue: "queue.Queue[dict[str, object]]", stop_event: threading.Event, ) -> None

**Docstring**

.. code-block:: text

   Executa la simulació baseline en segon pla.

start_baseline_run
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:204``.

.. code-block:: python

   def start_baseline_run(request: dict[str, object]) -> dict[str, object]

**Docstring**

.. code-block:: text

   Inicia l'execució de la línia de base.

render_environment_summary
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:267``.

.. code-block:: python

   def render_environment_summary(env_id: str) -> None

**Docstring**

.. code-block:: text

   Mostra el resum de l'entorn a la UI de Streamlit.

render_completed_baseline
~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:301``.

.. code-block:: python

   def render_completed_baseline(runtime: dict[str, object]) -> None

**Docstring**

.. code-block:: text

   Mostra la secció de referència completada a la UI de Streamlit.

render_baseline_runtime
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:328``.

.. code-block:: python

   def render_baseline_runtime(runtime: dict[str, object]) -> None

**Docstring**

.. code-block:: text

   Mostra la secció de temps d'execució de la línia de base a la UI de Streamlit.

render_baseline_runtime_frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/pages/Simular_Entorn.py:354``.

.. code-block:: python

   def render_baseline_runtime_frame() -> None

**Docstring**

.. code-block:: text

   Mostra el marc de runtime del baseline a la UI de Streamlit.

