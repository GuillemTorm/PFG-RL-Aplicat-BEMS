from html import escape

import streamlit as st
from page_components.ui_fragments import render_hero as render_page_hero
from sidebar_nav import configure_studio_page
from page_styles.theme import inject_studio_theme


PAGE_TITLE = "Ajuda"
INTRODUCTION_TEXT = (
    "BEMS-RL STUDIO permet controlar el cicle complet de l'entrenament "
    "d'un agent RL aplicat a simulacións d'EnergyPlus."
)
INTRODUCTION_HINT = (
    "A continuació trobaràs una explicació detallada de cada funcionalitat "
    "disponible al menú de l'esquerra."
)
RESOURCES = (
    (
        "Documentació de Sinergym",
        "https://ugr-sail.github.io/sinergym/compilation/main/index.html",
    ),
    ("Stable Baselines 3", "https://stable-baselines3.readthedocs.io/"),
    ("EnergyPlus", "https://energyplus.net/"),
    ("Gymnasium", "https://gymnasium.farama.org/"),
)
SUPPORT_CONTACT = {
    "name": "Guillem Torm",
    "email": "guillem@suno.cat",
}
HELP_SECTIONS = (
    (
        "1. Inici",
        """
        - **Objectiu:** Oferir una entrada ràpida al flux complet de treball: crear o revisar entorns, entrenar agents, simular baselines, avaluar models i analitzar resultats.
        - **Quan usar-ho:** Quan vulguis situar-te abans de començar una sessió o saltar cap a una tasca concreta des de la barra lateral.
        - **Consell:** Si no tens clar per on començar, segueix l'ordre natural: **Crear Entorn** o **Mostrar Entorn**, després **Simular Entorn**, **Entrenar Agent**, **Avaluar Agent** i finalment **Resultats**.
        """,
    ),
    (
        "2. Crear Entorn",
        """
        - **Objectiu:** Registrar nous entorns Sinergym a partir d'un edifici, un fitxer climàtic i la configuració d'accions, observacions i actius energètics.
        - **Què pots fer:** Pujar o seleccionar un clima EPW, detectar controladors HVAC i bateria disponibles, ajustar l'espai d'accions i revisar el YAML generat abans de crear l'entorn.
        - **Consell:** Revisa el YAML final i comprova que les variables d'observació i actuació existeixen al model abans de llançar entrenaments llargs.
        """,
    ),
    (
        "3. Mostrar Entorn",
        """
        - **Objectiu:** Inspeccionar els entorns registrats i entendre què veu i què pot controlar l'agent.
        - **Què pots consultar:** Observacions, accions, configuració de reward, clima associat, geometria, zones, actius energètics i configuració crua.
        - **Consell:** Usa aquesta pàgina per validar compatibilitats abans d'entrenar: un entorn discret encaixa millor amb algorismes discrets, mentre que un entorn continu requereix polítiques preparades per accions contínues.
        """,
    ),
    (
        "4. Entrenar Agent",
        """
        - **Objectiu:** Configurar i llançar entrenaments amb Stable Baselines3 sobre entorns Sinergym.
        - **Què pots configurar:** Entorn, algorisme, política, reward, wrappers, paràmetres SB3 avançats, timesteps i configuració climàtica o de cost energètic quan la reward ho necessita.
        - **Consell:** Dona noms curts i descriptius a les execucions, sense espais ni caràcters especials, per facilitar la lectura dels resultats i evitar problemes amb rutes de fitxer.
        """,
    ),
    (
        "5. Resultats",
        """
        - **Objectiu:** Analitzar execucions guardades i convertir els CSV d'entrenament, simulació o avaluació en gràfics i KPIs.
        - **Què pots fer:** Seleccionar una execució, obrir el dashboard integrat, comparar agregacions horàries, diàries, mensuals o sèries reals, revisar confort per zones i descarregar dades.
        - **Consell:** No eliminis els fitxers de monitoratge d'una execució si encara vols visualitzar-ne el dashboard; la pàgina necessita els CSV generats durant el procés.
        """,
    ),
    (
        "6. Simular Entorn",
        """
        - **Objectiu:** Executar un baseline d'EnergyPlus sense control RL per tenir una referència física i energètica de l'entorn.
        - **Què pots fer:** Triar l'entorn, ajustar la configuració del baseline, iniciar o cancel·lar la simulació i comparar-ne els resultats amb execucions guardades.
        - **Consell:** Genera sempre un baseline abans de valorar si un agent RL millora el comportament; així pots comparar consum, confort i desviacions amb una referència clara.
        """,
    ),
    (
        "7. Avaluar Agent",
        """
        - **Objectiu:** Carregar un model entrenat i executar una avaluació controlada sobre un entorn Sinergym.
        - **Què pots fer:** Seleccionar models `.zip`, revisar metadades detectades, ajustar wrappers manuals si el model no inclou tota la configuració i iniciar, cancel·lar o reiniciar l'avaluació.
        - **Consell:** Mantén l'entorn, la normalització i els wrappers coherents amb l'entrenament original; canvis petits poden alterar molt les accions que produeix la política.
        """,
    ),
    (
        "8. Control en Viu",
        """
        - **Objectiu:** Interaccionar pas a pas amb el simulador, ja sigui deixant actuar l'agent o provant accions manuals.
        - **Què pots fer:** Inicialitzar un entorn, carregar un model opcional, generar observacions aleatòries, avançar passos amb l'agent o aplicar accions manuals i veure l'impacte en els KPIs.
        - **Consell:** Fes servir aquest mode per diagnosticar decisions concretes, no per substituir una avaluació completa. Quan acabis, atura o tanca la sessió abans de canviar de pàgina.
        """,
    ),
    (
        "9. Arxius",
        """
        - **Objectiu:** Gestionar fitxers del projecte des de la interfície sense obrir el terminal.
        - **Què pots organitzar:** Entrenaments, scripts, models, fitxers climàtics i configuracions d'entorns. També pots pujar nous fitxers o eliminar artefactes que ja no necessitis.
        - **Consell:** Abans d'esborrar una carpeta d'entrenament, comprova si encara la necessites a **Resultats** o com a referència d'avaluació.
        """,
    ),
    (
        "10. Visor EPW",
        """
        - **Objectiu:** Explorar fitxers climàtics EPW abans d'usar-los en entorns o simulacions.
        - **Què pots veure:** Resum climàtic, metadades, sèries temporals, patrons mensuals, distribucions i dades tabulars del fitxer.
        - **Consell:** Consulta el visor abans de crear un entorn nou; ajuda a detectar climes incoherents, períodes estranys o diferències fortes entre ciutats.
        """,
    ),
    (
        "Consells generals",
        """
        - **Ordre recomanat:** Primer valida l'entorn, després genera un baseline, entrena l'agent, avalua'l i compara els resultats amb el dashboard.
        - **Compatibilitat:** Comprova sempre que l'algorisme, l'espai d'accions i els wrappers coincideixen amb l'entorn i amb el model que vols carregar.
        - **Execucions llargues:** Evita tancar el navegador o canviar de pàgina mentre una simulació, entrenament o avaluació està en curs.
        - **Noms d'execució:** Usa noms llegibles i estables, com `PPO_Radiant_Hivern` o `SAC_OfficeGrid_Test01`.
        - **Comparació justa:** Quan comparis models, intenta mantenir el mateix clima, horitzó temporal, reward i configuració de confort.
        - **Neteja:** Usa el gestor d'arxius amb prudència: eliminar models o monitoratges pot deixar sense dades les pàgines d'avaluació i resultats.
        """,
    ),
)


def inject_help_styles() -> None:
    """Aplica el tema global d'estudi a la pàgina d'ajuda."""
    inject_studio_theme(max_width=1180)


def render_resources_card() -> None:
    """Mostra els recursos addicionals."""

    resource_items = "\n".join(
        f'<li><a href="{escape(url)}" target="_blank">{escape(label)}</a></li>'
        for label, url in RESOURCES
    )
    # Targeta recursos ajuda
    st.markdown(
        f"""
        <section class="resources-card">
            <div class="panel-kicker">Recursos</div>
            <div class="panel-title">Enllaços útils</div>
            <div class="panel-copy">
                Referències externes per aprofundir en les tecnologies que fa servir la plataforma.
            </div>
            <ul>
                {resource_items}
            </ul>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_support_card() -> None:
    """Mostra les dades de contacte del centre d'ajuda."""

    support_name = SUPPORT_CONTACT["name"]
    support_email = SUPPORT_CONTACT["email"]
    # Targeta contacte ajuda
    st.markdown(
        f"""
        <section class="section-card">
            <div class="panel-kicker">Contacte</div>
            <div class="panel-title">Suport del centre d'ajuda</div>
            <div class="panel-copy">
                Per dubtes o incidències, pots contactar amb
                <strong>{escape(support_name)}</strong> a
                <a href="mailto:{escape(support_email)}">{escape(support_email)}</a>.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_help_page() -> None:
    """Munta la pàgina d'ajuda."""

    configure_studio_page(PAGE_TITLE, layout="wide")
    inject_help_styles()

    render_page_hero("help-hero", "Guia d'ús", PAGE_TITLE, [INTRODUCTION_TEXT, INTRODUCTION_HINT])

    # Separador ajuda
    st.markdown("<div class='studio-spacer-115'></div>", unsafe_allow_html=True)
    # Titol seccions ajuda
    st.markdown('<h2 class="section-title">Funcionalitats i consells</h2>', unsafe_allow_html=True)

    for title, content in HELP_SECTIONS:
        # Acordio seccio ajuda
        with st.expander(title):
            st.markdown(content)

    render_support_card()
    # Separador recursos ajuda
    st.markdown("<div class='studio-spacer-100'></div>", unsafe_allow_html=True)
    render_resources_card()


render_help_page()
