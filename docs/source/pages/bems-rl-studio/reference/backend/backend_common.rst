backend/common.py
=================

**Group:** Backend Modules

**Source:** ``BEMS-RL-STUDIO/backend/common.py``

**Module path:** ``backend.common``

**Module docstring**

.. code-block:: text

   Utilitats compartides de projecte per al backend de BEMS-RL Studio.

   Aquest mòdul agrupa peces petites que abans vivien en fitxers molt curts:
   camins canònics del projecte, descoberta d'entorns Sinergym i helpers genèrics
   d'arguments/format UI. Són funcions utilitzades per diversos fluxos del backend.

.. contents:: In this file
   :local:
   :depth: 2

Imports
-------

``__future__``, ``gymnasium``, ``importlib``, ``inspect``, ``pathlib``, ``sinergym``, ``typing``

Functions
---------

_sinergym_package_dir
~~~~~~~~~~~~~~~~~~~~~

**Internal helper.** Defined in ``BEMS-RL-STUDIO/backend/common.py:18``.

.. code-block:: python

   def _sinergym_package_dir() -> Path

**Docstring**

.. code-block:: text

   Localitza el paquet Sinergym sense executar-ne el registre d'entorns.

registered_env_ids
~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/common.py:34``.

.. code-block:: python

   def registered_env_ids() -> tuple[str, ...]

**Docstring**

.. code-block:: text

   Retorna els ids d'entorn exposats per Sinergym.

list_registered_env_ids
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/common.py:45``.

.. code-block:: python

   def list_registered_env_ids(*, include_discrete: bool = True) -> List[str]

**Docstring**

.. code-block:: text

   Llista ids Sinergym, amb opcio d'excloure entorns discrets.

is_registered_env_id
~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/common.py:53``.

.. code-block:: python

   def is_registered_env_id(env_id: str) -> bool

**Docstring**

.. code-block:: text

   Indica si un id forma part del cataleg registrat de Sinergym.

filter_supported_kwargs
~~~~~~~~~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/common.py:58``.

.. code-block:: python

   def filter_supported_kwargs(callable_obj: Any, kwargs: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]

**Docstring**

.. code-block:: text

   Filtra kwargs no acceptats per una funcio o classe.

format_ui_value
~~~~~~~~~~~~~~~

**Public function.** Defined in ``BEMS-RL-STUDIO/backend/common.py:81``.

.. code-block:: python

   def format_ui_value(value: Any) -> str

**Docstring**

.. code-block:: text

   Formata valors arbitraris per mostrar-los a la UI.

