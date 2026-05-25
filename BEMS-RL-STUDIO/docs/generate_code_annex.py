"""Generador de l'annex de codi tècnic de BEMS-RL Studio.

L'annex es genera intencionadament a partir de l'arbre del repositori perquè pugui incloure'l
el codi funcional complet de Python sense blocs de copiar/enganxar manualment.
S'exclouen els mòduls d'estil visual pur perquè l'annex se centra en l'executable
codi de flux, dades, entrenament, informes i integració.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = Path(__file__).resolve().parent
OUTPUT_TEX = DOCS_DIR / "annex_bems_rl_studio.tex"

EXCLUDED_DIRS = {"__pycache__", "docs", "resources", ".streamlit", "page_styles"}
EXCLUDED_FILES = {"ui_theme.py"}
UNICODE_PRINT_REPLACEMENTS = {
    "☀": r"\u2600",
    "✅": r"\u2705",
    "❄": r"\u2744",
    "️": "",
    "🌸": r"\U0001f338",
    "🍂": r"\U0001f342",
    "📁": r"\U0001f4c1",
    "📄": r"\U0001f4c4",
    "🔥": r"\U0001f525",
    "◫": r"\u25eb",
}

GROUP_ORDER = [
    "Entrypoints i navegacio",
    "Pagines Streamlit",
    "Components reutilitzables",
    "Backend funcional",
    "Grafics i metriques",
    "Eines de manteniment",
]


@dataclass(frozen=True)
class CodeFile:
    """Fitxer font inclòs a l'annex generat."""

    rel_path: str
    group: str
    line_count: int


@dataclass(frozen=True)
class ClassSummary:
    """Resum d'una classe detectada dins del codi funcional."""

    rel_path: str
    name: str
    kind: str
    purpose: str
    behavior: str


def latex_escape(text: str) -> str:
    """Escape de les cadenes curtes llegibles pels humans utilitzades fora de les llistes de codi."""

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def latex_path(text: str) -> str:
    """Formata una ruta de codi perquè LaTeX la pugui partir si és llarga."""

    return r"\path{" + text.replace("\\", "/") + "}"


def label_from_path(path: str) -> str:
    """Crea una etiqueta LaTeX estable des d'una ruta de repositori."""

    safe = []
    for char in path.lower():
        if char.isalnum():
            safe.append(char)
        else:
            safe.append("-")
    return "lst:" + "".join(safe).strip("-")


def sanitize_listing_text(text: str) -> str:
    """Normalitza els símbols UI que els tipus de lletra de codi comuns LaTeX no poden imprimir."""

    sanitized = text
    for source, replacement in UNICODE_PRINT_REPLACEMENTS.items():
        sanitized = sanitized.replace(source, replacement)
    return sanitized.rstrip() + "\n"


def group_for(rel_path: str) -> str:
    """Classifica un fitxer Python dins dels grups de navegació de l'annex."""

    if rel_path.startswith("pages/"):
        return "Pagines Streamlit"
    if rel_path.startswith("page_components/"):
        return "Components reutilitzables"
    if rel_path.startswith("backend/grafics/"):
        return "Grafics i metriques"
    if rel_path.startswith("backend/"):
        return "Backend funcional"
    if rel_path.startswith("tools/") or rel_path.startswith("test_"):
        return "Eines de manteniment"
    return "Entrypoints i navegacio"


def iter_functional_python_files() -> Iterable[CodeFile]:
    """Itera pels fitxers Python funcionals que han d'aparèixer a l'annex de codi."""

    for path in sorted(ROOT_DIR.rglob("*.py")):
        rel = path.relative_to(ROOT_DIR)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDED_FILES:
            continue
        rel_path = rel.as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        line_count = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        yield CodeFile(rel_path=rel_path, group=group_for(rel_path), line_count=line_count)


def read_code_file(code_file: CodeFile) -> str:
    """Llegeix el contingut d'un fitxer inclòs a l'annex."""

    return (ROOT_DIR / code_file.rel_path).read_text(encoding="utf-8", errors="replace")


def parse_code_file(code_file: CodeFile) -> ast.Module | None:
    """Parseja un fitxer Python i retorna None si no es pot analitzar."""

    try:
        return ast.parse(read_code_file(code_file), filename=code_file.rel_path)
    except SyntaxError:
        return None


def compact_text(text: str, max_chars: int = 190) -> str:
    """Deixa un text en una sola línia curta per a taules LaTeX."""

    cleaned = " ".join((text or "").replace("\n", " ").split())
    if not cleaned:
        return "Sense descripció explícita al mòdul."
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "…"


def first_doc_sentence(docstring: str | None, fallback: str) -> str:
    """Extreu la primera idea d'un docstring."""

    if not docstring:
        return fallback
    text = compact_text(docstring, max_chars=260)
    for separator in (". ", "? ", "! "):
        if separator in text:
            return compact_text(text.split(separator, 1)[0] + separator.strip(), max_chars=190)
    return compact_text(text, max_chars=190)


def top_level_names(tree: ast.Module | None, node_type: type[ast.AST]) -> list[str]:
    """Retorna noms de definicions de primer nivell d'un tipus concret."""

    if tree is None:
        return []
    names = []
    for node in tree.body:
        if isinstance(node, node_type):
            names.append(getattr(node, "name", ""))
    return [name for name in names if name]


def import_targets(tree: ast.Module | None) -> list[str]:
    """Resumeix imports interns importants d'un mòdul."""

    if tree is None:
        return []
    targets: set[str] = set()
    for node in tree.body:
        module_name = None
        if isinstance(node, ast.ImportFrom):
            module_name = node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(("backend", "page_components", "pages", "sidebar_nav")):
                    targets.add(alias.name)
        if module_name and module_name.startswith(("backend", "page_components", "pages", "sidebar_nav")):
            targets.add(module_name)
    return sorted(targets)


def affected_area(code_file: CodeFile) -> str:
    """Explica quina part de l'aplicació queda afectada pel fitxer."""

    rel_path = code_file.rel_path
    if rel_path.startswith("pages/Afegir_Entorn"):
        return "Creació i registre d'entorns."
    if rel_path.startswith("pages/Entrenar_Agent"):
        return "Flux d'entrenament i estat de Streamlit."
    if rel_path.startswith("pages/Resultats"):
        return "Selecció de runs, dashboard i descàrregues."
    if rel_path.startswith("pages/Simular_Entorn"):
        return "Baseline sense agent i comparació posterior."
    if rel_path.startswith("pages/Avaluar_Agent"):
        return "Avaluació de models SB3."
    if rel_path.startswith("pages/Interaccionar"):
        return "Control en viu i prova manual de polítiques."
    if rel_path.startswith("pages/Mostrar_Entorn"):
        return "Visualització d'entorns i geometria 3D."
    if rel_path.startswith("pages/Visor_Climes"):
        return "Inspecció de fitxers EPW i clima."
    if rel_path.startswith("pages/Gestionar"):
        return "Gestió de fitxers del projecte."
    if rel_path.startswith("page_components/training"):
        return "Formularis compartits d'entrenament."
    if rel_path.startswith("page_components/resultats"):
        return "Dashboard incrustat de resultats."
    if rel_path.startswith("backend/entrenar_agent"):
        return "Preparació, execució i persistència d'entrenaments."
    if rel_path.startswith("backend/afegir_entorn"):
        return "Anàlisi, conversió i YAML d'entorns."
    if rel_path.startswith("backend/grafics"):
        return "KPIs, normalització temporal i figures Plotly."
    if rel_path.startswith("backend/resultats"):
        return "Càrrega de runs, mètriques i exportació d'informes."
    if rel_path.startswith("backend/avaluar") or rel_path.startswith("backend/interaccionar"):
        return "Execució de models entrenats sobre entorns."
    if rel_path.startswith("backend/simular"):
        return "Simulació baseline i artefactes comparables."
    if rel_path.startswith("backend/mostrar") or rel_path.startswith("backend/viewer"):
        return "Lectura d'actius i representació 3D."
    if rel_path.startswith("backend/visor") or rel_path.startswith("backend/epw"):
        return "Lectura i gràfics de clima EPW."
    if rel_path.startswith("backend/gestionar"):
        return "Exploració, pujada, descàrrega i eliminació de fitxers."
    if rel_path.startswith("tools/"):
        return "Qualitat i manteniment del repositori."
    return code_file.group + "."


def file_summary(code_file: CodeFile) -> tuple[str, str, str]:
    """Crea les tres cel·les descriptives d'un fitxer."""

    tree = parse_code_file(code_file)
    doc = ast.get_docstring(tree) if tree is not None else None
    purpose = first_doc_sentence(doc, f"Mòdul funcional {code_file.rel_path}.")
    functions = [name for name in top_level_names(tree, ast.FunctionDef) if not name.startswith("_")]
    classes = top_level_names(tree, ast.ClassDef)
    targets = import_targets(tree)

    behavior_parts: list[str] = []
    if classes:
        behavior_parts.append("Defineix " + ", ".join(classes[:3]) + ("…" if len(classes) > 3 else ""))
    if functions:
        behavior_parts.append("organitza funcions com " + ", ".join(functions[:3]) + ("…" if len(functions) > 3 else ""))
    if targets:
        readable_targets = [target.replace("backend.", "").replace("page_components.", "") for target in targets[:3]]
        behavior_parts.append("connecta amb " + ", ".join(readable_targets) + ("…" if len(targets) > 3 else ""))
    if not behavior_parts:
        behavior_parts.append("agrupa constants o inicialització de mòdul")
    behavior = compact_text("; ".join(behavior_parts) + ".", max_chars=210)
    return purpose, affected_area(code_file), behavior


def render_file_summaries(files: list[CodeFile]) -> str:
    """Renderitza una guia breu de què fa cada fitxer inclòs a l'annex."""

    by_group: dict[str, list[CodeFile]] = defaultdict(list)
    for code_file in files:
        by_group[code_file.group].append(code_file)

    chunks = [
        r"\section{Guia ràpida de fitxers}",
        (
            "Aquesta taula resumeix cada fitxer inclòs a l'annex: què fa, quina part "
            "del projecte afecta i com treballa per dins. Les descripcions surten del "
            "docstring del mòdul i d'una lectura estàtica de funcions, classes i imports."
        ),
    ]
    for group in GROUP_ORDER:
        group_files = by_group.get(group, [])
        if not group_files:
            continue
        chunks.append(f"\\subsection{{{latex_escape(group)}}}")
        rows = [
            r"\begingroup",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3pt}",
            r"\sloppy",
            r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.20\linewidth}"
            r">{\raggedright\arraybackslash}p{0.29\linewidth}"
            r">{\raggedright\arraybackslash}p{0.20\linewidth}"
            r">{\raggedright\arraybackslash}p{0.23\linewidth}}",
            r"\toprule",
            r"Fitxer & Què fa & A què afecta & Com funciona \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"Fitxer & Què fa & A què afecta & Com funciona \\",
            r"\midrule",
            r"\endhead",
        ]
        for code_file in group_files:
            purpose, affected, behavior = file_summary(code_file)
            rows.append(
                latex_path(code_file.rel_path)
                + " & "
                + latex_escape(purpose)
                + " & "
                + latex_escape(affected)
                + " & "
                + latex_escape(behavior)
                + r" \\"
            )
        rows.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", r"\normalsize"])
        chunks.append("\n".join(rows))
    return "\n\n".join(chunks)


def class_kind(node: ast.ClassDef) -> str:
    """Classifica una classe segons decoradors i bases principals."""

    decorator_names = set()
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        decorator_names.add(getattr(target, "id", getattr(target, "attr", "")))
    base_names = {
        getattr(base, "id", getattr(base, "attr", ""))
        for base in node.bases
    }
    if "dataclass" in decorator_names:
        return "dataclass"
    if "Wrapper" in base_names:
        return "wrapper Gym"
    if "BaseReward" in base_names:
        return "reward Sinergym"
    if "NodeVisitor" in base_names:
        return "visitor AST"
    return "classe"


def class_behavior(node: ast.ClassDef) -> str:
    """Descriu breument com treballa una classe."""

    methods = [
        item.name
        for item in node.body
        if isinstance(item, ast.FunctionDef) and not item.name.startswith("__")
    ]
    bases = [
        getattr(base, "id", getattr(base, "attr", ""))
        for base in node.bases
        if getattr(base, "id", getattr(base, "attr", ""))
    ]
    parts: list[str] = []
    if bases:
        parts.append("Hereta de " + ", ".join(bases[:2]))
    if methods:
        parts.append("mètodes clau: " + ", ".join(methods[:4]) + ("…" if len(methods) > 4 else ""))
    if not parts:
        parts.append("guarda dades tipades sense lògica complexa")
    return compact_text("; ".join(parts) + ".", max_chars=180)


def collect_class_summaries(files: list[CodeFile]) -> list[ClassSummary]:
    """Recull totes les classes de primer nivell dels fitxers funcionals."""

    summaries: list[ClassSummary] = []
    for code_file in files:
        tree = parse_code_file(code_file)
        if tree is None:
            continue
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            purpose = first_doc_sentence(
                ast.get_docstring(node),
                f"Classe definida a {code_file.rel_path}.",
            )
            summaries.append(
                ClassSummary(
                    rel_path=code_file.rel_path,
                    name=node.name,
                    kind=class_kind(node),
                    purpose=purpose,
                    behavior=class_behavior(node),
                )
            )
    return summaries


def render_class_summaries(files: list[CodeFile]) -> str:
    """Renderitza una guia de totes les classes incloses a l'annex."""

    classes = collect_class_summaries(files)
    lines = [
        r"\section{Guia de classes}",
        (
            "Aquesta secció explica totes les classes i dataclasses del codi funcional "
            "inclòs a l'annex. Serveix com a mapa ràpid abans d'entrar al codi complet."
        ),
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\sloppy",
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.18\linewidth}"
        r">{\raggedright\arraybackslash}p{0.13\linewidth}"
        r">{\raggedright\arraybackslash}p{0.25\linewidth}"
        r">{\raggedright\arraybackslash}p{0.18\linewidth}"
        r">{\raggedright\arraybackslash}p{0.18\linewidth}}",
        r"\toprule",
        r"Classe & Tipus & Què fa & Fitxer & Com funciona \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Classe & Tipus & Què fa & Fitxer & Com funciona \\",
        r"\midrule",
        r"\endhead",
    ]
    for summary in classes:
        lines.append(
            r"\texttt{"
            + latex_escape(summary.name)
            + "} & "
            + latex_escape(summary.kind)
            + " & "
            + latex_escape(summary.purpose)
            + " & "
            + latex_path(summary.rel_path)
            + " & "
            + latex_escape(summary.behavior)
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", r"\normalsize"])
    return "\n".join(lines)


def render_file_inventory(files: list[CodeFile]) -> str:
    """Renderitza la taula d'inventari de fitxers agrupats."""

    by_group: dict[str, list[CodeFile]] = defaultdict(list)
    for code_file in files:
        by_group[code_file.group].append(code_file)

    lines = [
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.28\linewidth}rr}",
        r"\toprule",
        r"Grup & Fitxers & Línies \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Grup & Fitxers & Línies \\",
        r"\midrule",
        r"\endhead",
    ]
    for group in GROUP_ORDER:
        group_files = by_group.get(group, [])
        if not group_files:
            continue
        lines.append(
            f"{latex_escape(group)} & {len(group_files)} & {sum(file.line_count for file in group_files):,} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}"])
    return "\n".join(lines)


def render_code_listings(files: list[CodeFile]) -> str:
    """Mostra totes les llistes de codi agrupades per subsistema."""

    by_group: dict[str, list[CodeFile]] = defaultdict(list)
    for code_file in files:
        by_group[code_file.group].append(code_file)

    chunks: list[str] = [
        r"\appendix",
        r"\section{Annex de codi funcional}",
        (
            "Les llistes següents inclouen el codi Python funcional de BEMS-RL "
            "Studio dins d'aquest mateix document LaTeX. S'exclouen només els mòduls d'estil CSS pur "
            r"(\texttt{page\_styles/*.py} i \texttt{ui\_theme.py}) perquè "
            "no aporten lògica d'aplicació, dades, entrenament, simulació o "
            "generació d'informes. Les icones Unicode es representen com a escapes "
            r"\texttt{\textbackslash u...} o \texttt{\textbackslash U...} per evitar "
            "glifs buits en el PDF."
        ),
    ]

    for group in GROUP_ORDER:
        group_files = by_group.get(group, [])
        if not group_files:
            continue
        chunks.append(f"\\section{{Codi: {latex_escape(group)}}}")
        for code_file in group_files:
            escaped_path = latex_escape(code_file.rel_path)
            listing_text = sanitize_listing_text(
                (ROOT_DIR / code_file.rel_path).read_text(encoding="utf-8")
            )
            chunks.extend(
                [
                    r"\Needspace{8\baselineskip}",
                    (
                        r"\subsection{\texorpdfstring{\texttt{"
                        + escaped_path
                        + r"}}{"
                        + escaped_path
                        + r"}}"
                    ),
                    (
                        f"\\begin{{lstlisting}}[style=studioPython,caption={{{escaped_path}}},"
                        f"label={{{label_from_path(code_file.rel_path)}}}]\n"
                        f"{listing_text}"
                        "\\end{lstlisting}"
                    ),
                ]
            )
    return "\n\n".join(chunks)


def render_preamble() -> str:
    """Retorna el preàmbul LaTeX."""

    # El preàmbul és llarg perquè ha de compilar tant amb pdfLaTeX com amb Tectonic/XeLaTeX
    # i mantenir el codi llegible dins l'annex.
    return r"""\documentclass[10pt,a4paper]{article}

\usepackage{iftex}
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
\else
  \usepackage{fontspec}
  \defaultfontfeatures{Ligatures=TeX}
  \IfFontExistsTF{Consolas}{%
    \setmonofont{Consolas}[Scale=0.84]
  }{%
    \IfFileExists{C:/Windows/Fonts/consola.ttf}{%
      \setmonofont{C:/Windows/Fonts/consola.ttf}[Scale=0.84]
    }{}
  }
\fi

\usepackage[catalan]{babel}
\usepackage[a4paper,margin=1.8cm,headheight=14pt]{geometry}
\usepackage{array}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{enumitem}
\usepackage{float}
\usepackage{hyperref}
\usepackage{longtable}
\usepackage{microtype}
\usepackage{needspace}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,fit,matrix,positioning,shapes.geometric,shapes.multipart}

\definecolor{StudioInk}{HTML}{1F2A2E}
\definecolor{StudioMuted}{HTML}{5C6F6B}
\definecolor{StudioLine}{HTML}{60746F}
\definecolor{StudioBorder}{HTML}{8DA7A1}
\definecolor{StudioFill}{HTML}{F8FBFA}
\definecolor{StudioAccent}{HTML}{EAF4F1}
\definecolor{StudioBlue}{HTML}{2E6F95}
\definecolor{StudioBlueFill}{HTML}{EEF6FF}
\definecolor{StudioAmber}{HTML}{A06D2C}
\definecolor{StudioAmberFill}{HTML}{FFF8EF}
\definecolor{CodeBg}{HTML}{FBFCFC}
\definecolor{CodeFrame}{HTML}{CBD9D6}
\definecolor{CodeKeyword}{HTML}{205D7A}
\definecolor{CodeString}{HTML}{7A4B20}
\definecolor{CodeComment}{HTML}{5F7A72}

\hypersetup{
  colorlinks=true,
  linkcolor=StudioBlue,
  urlcolor=StudioBlue,
  citecolor=StudioBlue,
  pdftitle={Annex de codi de BEMS-RL Studio},
  pdfauthor={Guillem Torm}
}

\captionsetup{font=small,labelfont=bf}
\setlist[itemize]{leftmargin=1.4em,itemsep=0.25em}
\setlist[enumerate]{leftmargin=1.6em,itemsep=0.25em}
\setlength{\parskip}{0.55em}
\setlength{\parindent}{0pt}
\setlength{\emergencystretch}{2em}
\newcommand{\diagramnote}[1]{\par\smallskip\noindent\textbf{Lectura del diagrama.} #1\par\medskip}

\tikzset{
  studioBox/.style={
    draw=StudioBorder,
    fill=StudioFill,
    rounded corners=3pt,
    align=center,
    minimum width=2.65cm,
    minimum height=0.9cm,
    inner sep=5pt,
    font=\small
  },
  studioWide/.style={studioBox, minimum width=3.6cm},
  studioBlue/.style={studioBox, draw=StudioBlue, fill=StudioBlueFill},
  studioAmber/.style={studioBox, draw=StudioAmber, fill=StudioAmberFill},
  studioCluster/.style={draw=StudioBorder, fill=StudioAccent, rounded corners=4pt, inner sep=8pt},
  studioEdge/.style={-{Latex[length=2.1mm]}, thick, draw=StudioLine},
  studioDashed/.style={studioEdge, dashed},
  classBox/.style={
    draw=StudioBorder,
    fill=StudioFill,
    rectangle split,
    rectangle split parts=3,
    rounded corners=2pt,
    align=left,
    text width=4.1cm,
    font=\scriptsize,
    inner sep=4pt
  }
}

\lstdefinestyle{studioPython}{
  language=Python,
  basicstyle=\ttfamily\scriptsize,
  keywordstyle=\bfseries\color{CodeKeyword},
  stringstyle=\color{CodeString},
  commentstyle=\itshape\color{CodeComment},
  backgroundcolor=\color{CodeBg},
  frame=single,
  rulecolor=\color{CodeFrame},
  framerule=0.4pt,
  numbers=left,
  numberstyle=\tiny\color{StudioMuted},
  stepnumber=1,
  numbersep=7pt,
  showstringspaces=false,
  keepspaces=true,
  columns=fullflexible,
  breaklines=true,
  breakatwhitespace=false,
  tabsize=4,
  upquote=true,
  captionpos=t,
  inputencoding=utf8,
  extendedchars=true,
  literate=*
    {°}{{$^\circ$}}1
    {²}{{$^2$}}1
    {·}{{$\cdot$}}1
    {À}{{\`A}}1
    {Â}{{\^A}}1
    {Ã}{{\~A}}1
    {Ó}{{\'O}}1
    {Ú}{{\'U}}1
    {à}{{\`a}}1
    {â}{{\^a}}1
    {ç}{{\c{c}}}1
    {è}{{\`e}}1
    {é}{{\'e}}1
    {í}{{\'i}}1
    {ï}{{\"i}}1
    {ò}{{\`o}}1
    {ó}{{\'o}}1
    {ú}{{\'u}}1
    {ā}{{\=a}}1
    {Δ}{{$\Delta$}}1
    {×}{{$\times$}}1
    {–}{{--}}1
    {—}{{---}}1
    {’}{{'}}1
    {•}{{$\bullet$}}1
    {…}{{\ldots}}1
    {→}{{$\to$}}1
    {−}{{$-$}}1
    {≈}{{$\approx$}}1
    {≥}{{$\ge$}}1
    {─}{{-}}1
    {▲}{{$\triangle$}}1
    {▸}{{$\triangleright$}}1
    {▼}{{$\triangledown$}}1
    {◫}{{$\square$}}1
    {☀}{{sun}}1
    {✅}{{ok}}1
    {❄}{{snow}}1
    {️}{{}}0
    {🌸}{{spring}}1
    {🍂}{{autumn}}1
    {📁}{{folder}}1
    {📄}{{file}}1
    {🔥}{{heat}}1
}
"""


def render_diagrams() -> str:
    """Retorna els diagrames explicatius inclosos abans de l'apèndix de codi complet."""

    # Els diagrames s'escriuen com a LaTeX estàtic perquè l'annex sigui reproduible sense
    # dependre d'eines externes de dibuix.
    return r"""
\section{Visió general del codi}

BEMS-RL Studio està organitzat com una capa d'aplicació sobre Sinergym. Les
pàgines Streamlit gestionen la interacció amb l'usuari, els components
reutilitzables concentren formularis i panells compartits, i el backend manté
la lògica de fitxers, validació, entrenament, simulació, avaluació, gràfics i
informes. Aquesta separació és la que permet documentar el codi amb autodoc i,
alhora, mantenir les pàgines com a punts d'entrada lleugers.

\subsection{Arquitectura d'execució}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.4cm and 1.4cm]
  \node[studioBox] (user) {Usuari};
  \node[studioBlue, right=of user] (pages) {Pàgines\\Streamlit};
  \node[studioBox, right=of pages] (components) {Components\\reutilitzables};
  \node[studioWide, right=of components] (backend) {Backends\\d'aplicació};
  \node[studioBox, above right=0.6cm and 1.2cm of backend] (charts) {Capa de gràfics\\\texttt{backend.grafics}};
  \node[studioBox, below right=0.6cm and 1.2cm of backend] (sinergym) {Sinergym\\Gymnasium + EnergyPlus};
  \node[studioBox, right=2.1cm of charts] (reports) {Informes\\HTML/PDF};
  \node[studioBox, right=2.1cm of sinergym] (artifacts) {Artefactes\\models, logs, CSV};
  \draw[studioEdge] (user) -- (pages);
  \draw[studioEdge] (pages) -- (components);
  \draw[studioEdge] (components) -- (backend);
  \draw[studioEdge] (pages) to[bend left=20] (backend);
  \draw[studioEdge] (backend) -- (charts);
  \draw[studioEdge] (backend) -- (sinergym);
  \draw[studioEdge] (charts) -- (reports);
  \draw[studioEdge] (sinergym) -- (artifacts);
  \draw[studioEdge] (artifacts) -- (charts);
\end{tikzpicture}}
\caption{Arquitectura lògica de BEMS-RL Studio i relació amb Sinergym.}
\end{figure}
\diagramnote{El diagrama separa l'aplicació en capes. L'usuari només toca les pàgines Streamlit; aquestes pàgines deleguen en components i backends. El backend és qui parla amb Sinergym, llegeix o escriu artefactes i passa dades a la capa de gràfics i informes.}

\subsection{Topologia Docker i documentació}

\begin{figure}[H]
\centering
\resizebox{0.92\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.45cm and 1.3cm]
  \node[studioBox] (browser) {Navegador};
  \node[studioBlue, right=of browser] (app) {\texttt{bemsrlstudio}\\Streamlit\\:8501};
  \node[studioBox, above right=0.65cm and 1.35cm of app] (sinDocs) {\texttt{docs-sinergym}\\Sphinx\\:8000};
  \node[studioBox, below right=0.65cm and 1.35cm of app] (studioDocs) {\texttt{docs-studio}\\Sphinx\\:8001};
  \node[studioWide, right=2.0cm of app] (source) {Arbre de codi\\compartit};
  \node[studioWide, right=of source] (build) {Sortida Sphinx\\\texttt{docs/build}};
  \draw[studioEdge] (browser) -- node[above,font=\scriptsize] {aplicació} (app);
  \draw[studioEdge] (browser) to[bend left=24] node[above,font=\scriptsize] {docs Sinergym} (sinDocs);
  \draw[studioEdge] (browser) to[bend right=24] node[below,font=\scriptsize] {docs Studio} (studioDocs);
  \draw[studioEdge] (source) -- (app);
  \draw[studioEdge] (source) -- (sinDocs);
  \draw[studioEdge] (source) -- (studioDocs);
  \draw[studioEdge] (sinDocs) -- (build);
  \draw[studioEdge] (studioDocs) -- (build);
\end{tikzpicture}}
\caption{Serveis locals: aplicació i documentació separada en dos ports.}
\end{figure}
\diagramnote{Aquest dibuix mostra la topologia d'execució local. Streamlit serveix la interfície principal, mentre que la documentació queda separada en serveis propis. Tots tres serveis llegeixen el mateix arbre de codi, però generen sortides diferents.}

\subsection{Propietat de dades i artefactes}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.0cm and 1.05cm]
  \node[studioBox] (idf) {IDF / epJSON};
  \node[studioBox, below=of idf] (epw) {EPW};
  \node[studioWide, right=of idf] (env) {\texttt{afegir\_entorn\_*}\\configuració i validació};
  \node[studioBox, right=of env] (yaml) {YAML\\Sinergym};
  \node[studioWide, right=of yaml] (train) {\texttt{entrenar\_agent\_*}\\workspace reproduïble};
  \node[studioBox, above right=0.35cm and 1.0cm of train] (model) {Model\\SB3};
  \node[studioBox, below right=0.35cm and 1.0cm of train] (logs) {CSV\\progress + obs.};
  \node[studioWide, right=1.15cm of logs] (results) {\texttt{resultats\_backend}\\KPIs i dades};
  \node[studioWide, above=of results] (eval) {Avaluació\\i control en viu};
  \node[studioBox, right=of results] (report) {Informe\\HTML/PDF};
  \draw[studioEdge] (idf) -- (env);
  \draw[studioEdge] (epw) -- (env);
  \draw[studioEdge] (env) -- (yaml);
  \draw[studioEdge] (yaml) -- (train);
  \draw[studioEdge] (train) -- (model);
  \draw[studioEdge] (train) -- (logs);
  \draw[studioEdge] (model) -- (eval);
  \draw[studioEdge] (logs) -- (results);
  \draw[studioEdge] (results) -- (report);
\end{tikzpicture}}
\caption{Mòduls responsables de cada família d'artefactes.}
\end{figure}
\diagramnote{Aquí es veu el recorregut dels fitxers físics. Els IDF/epJSON i EPW entren pel flux de creació d'entorns, es converteixen en YAML de Sinergym i després alimenten entrenaments. Dels entrenaments surten models i CSV, que són la base de resultats i informes.}

\subsection{Límit d'importació i autodoc}

\begin{figure}[H]
\centering
\resizebox{0.82\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.25cm and 1.45cm]
  \node[studioAmber] (pages) {\texttt{pages/*.py}\\UI executada en importar};
  \node[studioBox, right=of pages] (components) {\texttt{page\_components}\\components reutilitzables de pantalla};
  \node[studioBox, below=of components] (backend) {\texttt{backend}\\lògica importable};
  \node[studioBox, above=of components] (styles) {\texttt{page\_styles}\\CSS importable};
  \node[studioBlue, right=2.0cm of components] (autodoc) {Sphinx\\autodoc};
  \node[studioBox, below=of autodoc] (staticref) {Referència\\AST estàtica};
  \draw[studioEdge] (pages) -- (components);
  \draw[studioEdge] (pages) -- (backend);
  \draw[studioEdge] (pages) -- (styles);
  \draw[studioEdge] (autodoc) -- (components);
  \draw[studioEdge] (autodoc) -- (backend);
  \draw[studioEdge] (autodoc) -- (styles);
  \draw[studioDashed] (staticref) -- node[below,font=\scriptsize] {sense executar UI} (pages);
\end{tikzpicture}}
\caption{Frontera entre lògica importable i punts d'entrada de Streamlit.}
\end{figure}
\diagramnote{La frontera important és que les pàgines Streamlit s'executen en importar-les, mentre que backend i components han de ser importables sense efectes laterals pesats. Per això la documentació automàtica tracta les pàgines amb més prudència.}

\section{Fluxos principals}

\subsection{Creació d'entorns}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.0cm and 0.95cm]
  \node[studioBox] (upload) {Pujar fitxers\\edifici + clima};
  \node[studioBox, right=of upload] (inspect) {Inspeccionar\\variables i actuadors};
  \node[studioBox, right=of inspect] (configure) {Construir\\YAML};
  \node[studioBox, right=of configure] (validate) {Validar\\Gymnasium};
  \node[studioBox, right=of validate] (register) {Registrar\\entorn};
  \node[studioBox, right=of register] (use) {Entrenar\\simular\\avaluar};
  \draw[studioEdge] (upload) -- (inspect);
  \draw[studioEdge] (inspect) -- (configure);
  \draw[studioEdge] (configure) -- (validate);
  \draw[studioEdge] (validate) -- (register);
  \draw[studioEdge] (register) -- (use);
\end{tikzpicture}}
\caption{Flux d'autoria d'entorns de la documentació de Studio.}
\end{figure}
\diagramnote{El flux va d'esquerra a dreta: primer es carreguen fitxers, després s'inspeccionen variables i actuadors, es construeix el YAML, es valida amb Gymnasium i finalment l'entorn queda llest per entrenar, simular o avaluar.}

\subsection{Cicle d'entrenament}

\begin{figure}[H]
\centering
\resizebox{0.92\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.1cm and 1.15cm]
  \node[studioBox] (form) {Formulari\\d'entrenament};
  \node[studioBox, right=of form] (state) {Estat UI\\validat};
  \node[studioBox, right=of state] (workspace) {Workspace\\d'entrenament};
  \node[studioBox, above right=0.35cm and 1.15cm of workspace] (scripts) {Scripts\\reproduïbles};
  \node[studioBox, right=of workspace] (model) {Model\\\texttt{.zip}};
  \node[studioBox, below right=0.35cm and 1.15cm of workspace] (logs) {Logs i\\observacions};
  \draw[studioEdge] (form) -- (state);
  \draw[studioEdge] (state) -- (workspace);
  \draw[studioEdge] (workspace) -- (scripts);
  \draw[studioEdge] (workspace) -- (model);
  \draw[studioEdge] (workspace) -- (logs);
\end{tikzpicture}}
\caption{Cicle de vida dels artefactes d'entrenament.}
\end{figure}
\diagramnote{El formulari no entrena directament. Primer es converteix en estat validat, després es crea un workspace reproduïble i, a partir d'aquí, es guarden model, logs, observacions i scripts que permeten repetir l'experiment.}

\subsection{Resultats i selecció de gràfics}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.05cm and 1.05cm]
  \node[studioBox] (progress) {\texttt{progress.csv}};
  \node[studioBox, below=of progress] (obs) {\texttt{observations.csv}};
  \node[studioWide, right=of progress] (loader) {\texttt{DashboardData}};
  \node[studioBox, right=of loader] (kpis) {KPIs};
  \node[studioWide, below=of kpis] (figures) {Constructors\\Plotly};
  \node[studioBox, right=of kpis] (dashboard) {Dashboard\\Resultats};
  \node[studioBox, right=of figures] (report) {Informe\\HTML/PDF};
  \node[studioBox, below=of figures] (skip) {Ometre secció\\si no hi ha dades};
  \draw[studioEdge] (progress) -- (loader);
  \draw[studioEdge] (obs) -- (loader);
  \draw[studioEdge] (loader) -- (kpis);
  \draw[studioEdge] (loader) -- (figures);
  \draw[studioEdge] (kpis) -- (dashboard);
  \draw[studioEdge] (figures) -- (dashboard);
  \draw[studioEdge] (figures) -- node[above,font=\scriptsize] {traça vàlida} (report);
  \draw[studioDashed] (figures) -- node[right,font=\scriptsize] {sense dades} (skip);
\end{tikzpicture}}
\caption{Ruta de dades de resultats i criteri d'inclusió de figures.}
\end{figure}
\diagramnote{Els resultats sempre parteixen de \texttt{progress.csv} i \texttt{observations.csv}. El carregador els converteix en \texttt{DashboardData}; les figures només passen al dashboard o a l'informe quan tenen dades reals, així s'eviten gràfics buits.}

\subsection{Control en viu}

\begin{figure}[H]
\centering
\resizebox{0.94\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.05cm and 1.05cm]
  \node[studioBox] (model) {Model SB3};
  \node[studioBox, right=of model] (metadata) {Metadades\\del model};
  \node[studioBox, below=of metadata] (env) {Entorn\\seleccionat};
  \node[studioWide, right=of metadata] (validate) {Compatibilitat\\d'espai d'accions};
  \node[studioBox, right=of validate] (predict) {Predir\\acció};
  \node[studioBox, right=of predict] (step) {Pas\\EnergyPlus};
  \node[studioBox, below=of step] (status) {Progrés\\i avisos};
  \node[studioBox, left=of status] (ui) {Interfície\\Streamlit};
  \draw[studioEdge] (model) -- (metadata);
  \draw[studioEdge] (metadata) -- (validate);
  \draw[studioEdge] (env) -- (validate);
  \draw[studioEdge] (validate) -- (predict);
  \draw[studioEdge] (predict) -- (step);
  \draw[studioEdge] (step) -- (status);
  \draw[studioEdge] (status) -- (ui);
  \draw[studioEdge] (step) to[bend left=35] node[above,font=\scriptsize] {següent observació} (predict);
\end{tikzpicture}}
\caption{Bucle d'execució de control en viu.}
\end{figure}
\diagramnote{El bucle de control comprova metadades i compatibilitat abans de predir. Després aplica l'acció a EnergyPlus, rep la següent observació i actualitza la UI. La fletxa de retorn indica que el procés es repeteix a cada pas.}

\section{Dependències entre fitxers}

Els diagrames següents mostren les dependències principals entre fitxers. No
inclouen cada import petit de suport, sinó les relacions que cal entendre per
defensar el projecte: pàgina, components, backend, artefactes i classes de dades.

\subsection{Creació d'entorns}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.0cm and 1.0cm]
  \node[studioBlue, text width=3.8cm] (page) {Pàgina\\\texttt{pages/Afegir\_Entorn.py}};
  \node[studioWide, text width=4.4cm, right=of page] (facade) {Orquestració\\\texttt{afegir\_entorn\_backend.py}};
  \node[studioWide, text width=4.7cm, right=of facade] (analysis) {Lectura i conversió\\\texttt{afegir\_entorn\_analysis}\\\texttt{afegir\_entorn\_conversion}};
  \node[studioWide, text width=4.7cm, right=of analysis] (config) {Configuració segura\\\texttt{afegir\_entorn\_config}\\\texttt{afegir\_entorn\_types}\\\texttt{afegir\_entorn\_utils}};
  \node[studioWide, text width=4.2cm, right=of config] (support) {Context del projecte\\\texttt{weather\_profiles}\\\texttt{paths}};
  \node[studioAmber, text width=3.3cm, right=of support] (yaml) {YAML\\entorn registrat};
  \draw[studioEdge] (page) -- (facade);
  \draw[studioEdge] (facade) -- (analysis);
  \draw[studioEdge] (analysis) -- (config);
  \draw[studioEdge] (config) -- (support);
  \draw[studioEdge] (support) -- (yaml);
\end{tikzpicture}}
\caption{Dependències dels fitxers que creen i registren entorns Sinergym.}
\end{figure}
\diagramnote{Aquest flux comença a la pàgina d'alta d'entorns i passa pel backend principal, que reparteix la feina entre lectura del model, conversió de fitxers, construcció del YAML i validació. Els fitxers de tipus i utilitats eviten repetir estructures; \texttt{weather\_profiles} i \texttt{paths} situen l'entorn dins del projecte.}

\subsection{Entrenament d'agents}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.0cm and 0.95cm]
  \node[studioBlue, text width=3.6cm] (page) {Pàgina\\\texttt{pages/Entrenar\_Agent.py}};
  \node[studioWide, text width=4.5cm, right=of page] (ui) {Components UI\\\texttt{training\_page}\\\texttt{training\_agent}\\\texttt{training\_rewards}\\\texttt{training\_wrappers}\\\texttt{training\_shared}};
  \node[studioWide, text width=4.2cm, right=of ui] (facade) {Backend principal\\\texttt{entrenar\_agent\_backend.py}};
  \node[studioWide, text width=4.6cm, right=of facade] (prepare) {Sessió i configuració\\\texttt{entrenar\_agent\_session}\\\texttt{entrenar\_agent\_env}\\\texttt{entrenar\_agent\_rewards}\\\texttt{entrenar\_agent\_wrappers}};
  \node[studioWide, text width=4.4cm, right=of prepare] (run) {Execució RL\\\texttt{entrenar\_agent\_runtime}\\\texttt{training\_scripts}\\\texttt{sb3\_utils}};
  \node[studioAmber, text width=3.6cm, right=of run] (out) {Artefactes\\\texttt{entrenar\_agent\_artifacts}\\models\\logs\\config};
  \draw[studioEdge] (page) -- (ui);
  \draw[studioEdge] (ui) -- (facade);
  \draw[studioEdge] (facade) -- (prepare);
  \draw[studioEdge] (prepare) -- (run);
  \draw[studioEdge] (run) -- (out);
\end{tikzpicture}}
\caption{Dependències principals del flux d'entrenament.}
\end{figure}
\diagramnote{La pàgina només recull opcions i mostra estat. Els components separen pestanyes i formularis, el backend principal valida la petició i els mòduls de sessió, entorn, recompenses i wrappers preparen una configuració coherent. L'execució real queda a \texttt{entrenar\_agent\_runtime}, \texttt{training\_scripts} i \texttt{sb3\_utils}; al final es deixen models, logs i configuració reproduïble.}

\subsection{Resultats, dashboard i informes}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.0cm and 1.0cm]
  \node[studioBlue, text width=3.4cm] (page) {Pàgina\\\texttt{pages/Resultats.py}};
  \node[studioWide, text width=4.4cm, right=of page] (backend) {Selecció de runs\\\texttt{resultats\_backend}\\\texttt{resultats\_dashboard}};
  \node[studioWide, text width=4.4cm, right=of backend] (data) {Dades i KPIs\\\texttt{data\_loader}\\\texttt{kpis}\\\texttt{metrics}\\\texttt{figures\_zones}};
  \node[studioWide, text width=4.8cm, right=of data] (figures) {Famílies de gràfics\\\texttt{figures\_common}\\battery, comfort, hvac, thermal\\control, energy, indoor};
  \node[studioWide, text width=4.2cm, right=of figures] (report) {Exportació\\\texttt{resultats\_report\_backend}\\\texttt{style}\\\texttt{time\_utils}};
  \node[studioAmber, text width=3.2cm, right=of report] (out) {Dashboard\\HTML/PDF};
  \draw[studioEdge] (page) -- (backend);
  \draw[studioEdge] (backend) -- (data);
  \draw[studioEdge] (data) -- (figures);
  \draw[studioEdge] (figures) -- (report);
  \draw[studioEdge] (report) -- (out);
\end{tikzpicture}}
\caption{Dependències entre fitxers del flux de resultats i exportació.}
\end{figure}
\diagramnote{El flux de resultats primer localitza la run i els fitxers necessaris. Després carrega CSV, calcula mètriques i prepara dades de zona. Les famílies de gràfics comparteixen format i criteris visuals; l'exportador reutilitza aquestes figures per generar l'informe HTML/PDF sense duplicar càlculs.}

\subsection{Simulació, avaluació i control en viu}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.0cm and 1.0cm]
  \node[studioBlue, text width=4.0cm] (pages) {Pàgines\\\texttt{Simular\_Entorn.py}\\\texttt{Avaluar\_Agent.py}\\\texttt{Interaccionar\_amb\_l'Agent.py}};
  \node[studioWide, text width=4.5cm, right=of pages] (backends) {Backends d'execució\\\texttt{simular\_entorn\_backend}\\\texttt{avaluar\_agent\_backend}\\\texttt{interaccionar\_agent\_backend}};
  \node[studioWide, text width=4.2cm, right=of backends] (shared) {Peces compartides\\\texttt{sb3\_utils}\\\texttt{entrenar\_agent\_backend}};
  \node[studioAmber, text width=3.6cm, right=of shared] (engine) {Sinergym\\EnergyPlus\\models\\VecNormalize};
  \node[studioAmber, text width=3.3cm, right=of engine] (out) {CSV\\mètriques\\estat en viu};
  \draw[studioEdge] (pages) -- (backends);
  \draw[studioEdge] (backends) -- (shared);
  \draw[studioEdge] (shared) -- (engine);
  \draw[studioEdge] (engine) -- (out);
\end{tikzpicture}}
\caption{Dependències dels fluxos d'execució sense editar entorns.}
\end{figure}
\diagramnote{Aquests tres fluxos comparteixen la idea d'executar un entorn ja existent. La simulació genera una línia base, l'avaluació carrega un agent entrenat i el control en viu repeteix prediccions pas a pas. \texttt{sb3\_utils} centralitza càrrega i formes d'acció perquè els tres camins no tinguin regles diferents.}

\subsection{Visors i gestió de fitxers}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=1.0cm and 1.0cm]
  \node[studioBlue, text width=4.0cm] (pages) {Pàgines\\\texttt{Mostrar\_Entorn.py}\\\texttt{Visor\_Climes\_EPW.py}\\\texttt{Gestionar\_Arxius.py}};
  \node[studioWide, text width=4.4cm, right=of pages] (backends) {Backends\\\texttt{mostrar\_entorn\_backend}\\\texttt{visor\_epw\_backend}\\\texttt{gestionar\_arxius\_backend}};
  \node[studioWide, text width=4.2cm, right=of backends] (viewers) {Visualització\\\texttt{viewer\_3d\_backend}\\\texttt{mapa\_backend}\\\texttt{epw\_figures}};
  \node[studioWide, text width=3.7cm, right=of viewers] (paths) {Fitxers\\\texttt{paths}\\IDF\\EPW\\models};
  \node[studioAmber, text width=3.1cm, right=of paths] (out) {Mapa\\3D\\gràfics\\gestió};
  \draw[studioEdge] (pages) -- (backends);
  \draw[studioEdge] (backends) -- (viewers);
  \draw[studioEdge] (viewers) -- (paths);
  \draw[studioEdge] (paths) -- (out);
\end{tikzpicture}}
\caption{Dependències dels visors d'entorn/clima i del gestor d'arxius.}
\end{figure}
\diagramnote{Aquest bloc agrupa les pantalles que no entrenen agents. Els backends preparen metadades i fitxers; els mòduls de visualització converteixen aquesta informació en mapa, visor 3D o gràfics EPW. \texttt{paths} manté rutes consistents perquè el gestor d'arxius i els visors mirin el mateix lloc.}

\section{Classes i dataclasses principals}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=0.8cm and 0.9cm]
  \node[classBox] (upgrade) {
    \textbf{UpgradeResult}
    \nodepart{second}
    path\\version\\warnings
    \nodepart{third}
    resultat de conversió IDF
  };
  \node[classBox, right=of upgrade] (validation) {
    \textbf{EnvironmentValidationResult}
    \nodepart{second}
    ok\\message\\warnings
    \nodepart{third}
    prova de fum de l'entorn
  };
  \node[classBox, right=of validation] (analysis) {
    \textbf{BuildingTrainingAnalysis}
    \nodepart{second}
    variables\\meters\\actuators
    \nodepart{third}
    base per crear YAML
  };
  \node[classBox, below=of analysis] (actuator) {
    \textbf{ActuatorOption}
    \nodepart{second}
    name\\component\\control type
    \nodepart{third}
    opció d'acció candidata
  };
  \node[classBox, left=of actuator] (probe) {
    \textbf{ProbeReward}
    \nodepart{second}
    reward zero\\inspecció segura
    \nodepart{third}
    evita efectes durant l'anàlisi
  };
  \node[classBox, right=of actuator] (weather) {
    \textbf{WeatherProfileSuggestion}
    \nodepart{second}
    climate\\profile\\rationale
    \nodepart{third}
    proposta de perfil EPW
  };
  \draw[studioEdge] (upgrade) -- (validation);
  \draw[studioEdge] (validation) -- (analysis);
  \draw[studioEdge] (analysis) -- (actuator);
  \draw[studioEdge] (probe) -- (actuator);
  \draw[studioEdge] (actuator) -- (weather);
\end{tikzpicture}}
\caption{Classes i dataclasses del flux de creació d'entorns.}
\end{figure}
\diagramnote{\texttt{UpgradeResult} i \texttt{EnvironmentValidationResult} descriuen resultats de processos que poden fallar o generar avisos. \texttt{BuildingTrainingAnalysis} concentra allò que s'ha llegit de l'edifici i es connecta amb actuadors, recompenses de prova i suggeriments de clima per acabar generant una configuració entrenable.}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=0.8cm and 0.9cm]
  \node[classBox] (summary) {
    \textbf{EnvironmentSummary}
    \nodepart{second}
    env\\variables\\meters
    \nodepart{third}
    resum per simulació base
  };
  \node[classBox, right=of summary] (baseline) {
    \textbf{BaselineSimulationResult}
    \nodepart{second}
    run path\\elapsed\\cancelled
    \nodepart{third}
    retorn del baseline
  };
  \node[classBox, right=of baseline] (eval) {
    \textbf{EvaluationResult}
    \nodepart{second}
    elapsed\\cancelled\\warnings
    \nodepart{third}
    retorn de l'avaluació SB3
  };
  \node[classBox, below=of baseline] (baselineReward) {
    \textbf{ScheduleBaselineReward}
    \nodepart{second}
    reward zero\\mètriques físiques
    \nodepart{third}
    conserva schedules EnergyPlus
  };
  \node[classBox, right=of baselineReward] (costLogger) {
    \textbf{EnergyCostFileLogger}
    \nodepart{second}
    step\\cost\\energy
    \nodepart{third}
    CSV addicional de cost
  };
  \node[classBox, right=of costLogger] (epwState) {
    \textbf{EpwDashboardState}
    \nodepart{second}
    path\\metadata\\figures
    \nodepart{third}
    estat del visor EPW
  };
  \draw[studioEdge] (summary) -- (baseline);
  \draw[studioEdge] (baseline) -- (eval);
  \draw[studioEdge] (baselineReward) -- (baseline);
  \draw[studioEdge] (baselineReward) -- (costLogger);
  \draw[studioEdge] (costLogger) -- (epwState);
\end{tikzpicture}}
\caption{Classes del flux d'execució: baseline, entrenament, avaluació i clima.}
\end{figure}
\diagramnote{\texttt{EnvironmentSummary}, \texttt{BaselineSimulationResult} i \texttt{EvaluationResult} són els retorns grans que les pàgines poden mostrar sense conèixer els detalls d'EnergyPlus. A sota hi ha classes de suport: una recompensa neutra per executar baselines, un logger de cost i l'estat del visor EPW.}

\begin{figure}[H]
\centering
\resizebox{\linewidth}{!}{%
\begin{tikzpicture}[node distance=0.8cm and 0.9cm]
  \node[classBox] (runOption) {
    \textbf{RunOption}
    \nodepart{second}
    label\\path\\kind
    \nodepart{third}
    opció al selector de runs
  };
  \node[classBox, right=of runOption] (pageState) {
    \textbf{ResultsPageState}
    \nodepart{second}
    options\\selected\\warning
    \nodepart{third}
    estat inicial de Resultats
  };
  \node[classBox, right=of pageState] (artifacts) {
    \textbf{RunArtifacts}
    \nodepart{second}
    progress\\observations\\metadata
    \nodepart{third}
    fitxers necessaris d'una run
  };
  \node[classBox, right=of artifacts] (dashboard) {
    \textbf{DashboardData}
    \nodepart{second}
    progress\\obs\\metrics
    \nodepart{third}
    alimenta dashboard i informe
  };
  \node[classBox, right=of dashboard] (figure) {
    \textbf{ReportFigure}
    \nodepart{second}
    title\\figure\\description
    \nodepart{third}
    gràfic exportable
  };
  \node[classBox, below=of pageState] (explorer) {
    \textbf{ExplorerItem}
    \nodepart{second}
    path\\kind\\metadata
    \nodepart{third}
    element del gestor d'arxius
  };
  \draw[studioEdge] (runOption) -- (pageState);
  \draw[studioEdge] (pageState) -- (artifacts);
  \draw[studioEdge] (artifacts) -- (dashboard);
  \draw[studioEdge] (dashboard) -- (figure);
\end{tikzpicture}}
\caption{Classes i dataclasses de resultats, informes i gestió de fitxers.}
\end{figure}
\diagramnote{El primer tram explica el camí normal de Resultats: opció seleccionable, estat de pàgina, fitxers trobats, dades preparades i figures exportables. \texttt{ExplorerItem} queda separat perquè representa elements del gestor d'arxius, no del càlcul principal de KPIs.}
"""


def render_document(files: list[CodeFile]) -> str:
    """Compon el document LaTeX complet."""

    total_lines = sum(code_file.line_count for code_file in files)
    total_files = len(files)
    inventory = render_file_inventory(files)
    file_summaries = render_file_summaries(files)
    class_summaries = render_class_summaries(files)
    listings = render_code_listings(files)
    diagrams = render_diagrams()

    return (
        render_preamble()
        + rf"""

\title{{\textbf{{Annex de codi de BEMS-RL Studio}}\\
\large Arquitectura, diagrames UML i codi funcional complet}}
\author{{Guillem Torm}}
\date{{© 2025, Guillem Torm}}

\begin{{document}}
\maketitle
\tableofcontents
\clearpage

\section{{Objectiu i abast}}

Aquest annex acompanya la documentació professional de BEMS-RL Studio. El seu
objectiu és donar una visió tècnica suficient per entendre com està estructurat
el projecte i, després, conservar una còpia compilable de tot el codi Python
funcional de l'aplicació.

L'annex inclou {total_files} fitxers Python i {total_lines:,} línies de codi.
Abans de les llistes completes s'hi incorporen els diagrames principals de la
documentació Sphinx, adaptats a LaTeX/TikZ, i un UML conceptual dels tipus de
dades que vertebren els workflows.

El codi reproduït en aquest annex correspon exclusivament a BEMS-RL Studio.
No s'hi copia ni s'hi reprodueix codi font del paquet Sinergym: les aparicions
del nom Sinergym dins del document indiquen integracions, importacions,
artefactes, rutes o dependències utilitzades per l'aplicació.

\subsection{{Criteri d'inclusió}}

\begin{{itemize}}
  \item S'inclou el codi funcional de pàgines, components, backend, generació de
        gràfics, informes, eines de manteniment i punts d'entrada.
  \item No s'inclouen els mòduls d'estil CSS pur: \texttt{{page\_styles/*.py}} i
        \texttt{{ui\_theme.py}}. El seu contingut és visual i ja queda cobert per
        la documentació d'interfície.
  \item El codi queda incrustat en el fitxer LaTeX generat. Les icones Unicode
        del codi es mostren com a escapes per evitar glifs buits en el PDF,
        però els fitxers originals no es modifiquen.
\end{{itemize}}

\subsection{{Inventari resumit}}

{inventory}

\clearpage

{file_summaries}

\clearpage

{class_summaries}

\clearpage

{diagrams}

{listings}

\end{{document}}
"""
    )


def main() -> None:
    """Genera ``annex_bems_rl_studio.tex``."""

    files = list(iter_functional_python_files())
    with OUTPUT_TEX.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_document(files))
    total_lines = sum(file.line_count for file in files)
    print(f"Wrote {OUTPUT_TEX} with {len(files)} files and {total_lines:,} lines.")


if __name__ == "__main__":
    main()
