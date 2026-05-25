"""Conversió i actualització d'IDF/epJSON dins del flux per afegir entorns."""

from __future__ import annotations

import os
import re
import shutil
import ssl
import subprocess
import tarfile
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

from backend.afegir_entorn_common import (
    ENERGYPLUS_SUBPROCESS_TIMEOUT_SECONDS,
    FALLBACK_UPDATER_DIR,
    TARGET_EPLUS_VERSION,
    TRANSITION_DOWNLOAD_URL,
)
from backend.afegir_entorn_common import UpgradeResult

def detect_idf_version(idf_path: Path) -> Optional[Tuple[int, int]]:
    """Llegeix un fitxer IDF per extreure la seva versió de destinació EnergyPlus.

    Paràmetres:
        idf_path (Path): camí cap al fitxer IDF.

    Retorna:
        Optional[Tuple[int, int]]: una tupla de nombres enters majors i menors si es troba, sinó None.
    """
    with open(idf_path, "r", encoding="utf-8", errors="ignore") as file_handle:
        content = file_handle.read()

    match = re.search(r"Version,\s*([\d\.]+)\s*;", content, re.IGNORECASE)
    if not match:
        return None

    parts = match.group(1).strip().split(".")
    if len(parts) < 2:
        return None

    return int(parts[0]), int(parts[1])


def needs_idf_upgrade(version: Tuple[int, int]) -> bool:
    """Avalua si una versió IDF requereix l'actualització a la versió del simulador de destinació.

    Paràmetres:
        version (Tuple[int, int]): versió major i menor de IDF.

    Retorna:
        bool: True si la versió és estrictament més antiga que la `TARGET_EPLUS_VERSION`.
    """
    major, minor = version
    target_major, target_minor = TARGET_EPLUS_VERSION
    return not (major > target_major or (major == target_major and minor >= target_minor))


def get_transition_updater_dir() -> Optional[Path]:
    """Recupera el directori local que conté EnergyPlus IDFVersionUpdater binaris.

    Retorna:
        Optional[Path]: camí cap a les eines d'actualització, o None si no es troba localment.
    """
    ep_base_dir = Path(os.environ.get("EPLUS_PATH", "/usr/local/EnergyPlus-24-1-0"))
    updater_dir = ep_base_dir / "PreProcess" / "IDFVersionUpdater"
    if updater_dir.exists():
        return updater_dir
    if FALLBACK_UPDATER_DIR.exists():
        return FALLBACK_UPDATER_DIR
    return None


def download_transition_tools() -> Path:
    """Baixa i extreu EnergyPlus Eines de transició al directori alternatiu.

    En lloc de descarregar tota la suite EnergyPlus, només extreu l'actualitzador PreProcess.

    Retorna:
        Path: el directori local que conté les eines de transició descarregades.
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    tar_path, _ = urllib.request.urlretrieve(TRANSITION_DOWNLOAD_URL, "/tmp/eplus.tar.gz")
    FALLBACK_UPDATER_DIR.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as tar:
        members = []
        for member in tar.getmembers():
            if "PreProcess/IDFVersionUpdater/" in member.name:
                member.name = member.name.split("PreProcess/IDFVersionUpdater/")[1]
                if member.name:
                    members.append(member)
        tar.extractall(path=FALLBACK_UPDATER_DIR, members=members)
    Path("/tmp/eplus.tar.gz").unlink(missing_ok=True)
    return FALLBACK_UPDATER_DIR


def upgrade_idf_version(idf_path: Path, updater_dir: Path) -> UpgradeResult:
    """Actualitza seqüencialment un fitxer IDF mitjançant cadenes de transició EnergyPlus.

    Paràmetres:
        idf_path (Path): camí cap al fitxer IDF de destinació.
        updater_dir (Path): Directori que conté les eines de transició.

    Retorna:
        UpgradeResult: Estructura resumida de l'operació d'actualització.
    """
    initial_version = detect_idf_version(idf_path)
    if initial_version is None or not needs_idf_upgrade(initial_version):
        return UpgradeResult(upgraded=False, final_version=initial_version)

    current_major, current_minor = initial_version
    working_dir = Path("/tmp/eplus_upgrade")
    working_dir.mkdir(parents=True, exist_ok=True)
    working_file = working_dir / idf_path.name
    shutil.copy(idf_path, working_file)

    loops = 0
    failed_transition_version = None
    while loops < 20:
        prefix = f"Transition-V{current_major}-{current_minor}-0-to-V"
        tool = next(
            (
                file_path
                for file_path in updater_dir.glob("Transition-*")
                if file_path.name.startswith(prefix)
            ),
            None,
        )

        if not tool:
            break

        try:
            subprocess.run(
                [str(tool), str(working_file)],
                check=True,
                cwd=str(updater_dir),
                capture_output=True,
                timeout=ENERGYPLUS_SUBPROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.CalledProcessError:
            failed_transition_version = (current_major, current_minor)
            break

        next_version = detect_idf_version(working_file)
        if next_version is None:
            break

        current_major, current_minor = next_version
        loops += 1

    shutil.copy(working_file, idf_path)
    final_version = detect_idf_version(idf_path)

    upgraded = False
    if initial_version is not None and final_version is not None:
        upgraded = final_version[0] > initial_version[0] or final_version[1] > initial_version[1]

    return UpgradeResult(
        upgraded=upgraded,
        final_version=final_version,
        failed_transition_version=failed_transition_version,
    )


def convert_idf_to_epjson(idf_path: Path) -> Path:
    """Converteix un fitxer EnergyPlus IDF al format epJSON mitjançant les eines CLI.

    Paràmetres:
        idf_path (Path): camí cap al fitxer estructural IDF.

    Retorna:
        Path: el camí del fitxer epJSON convertit resultant.
    """
    epjson_path = idf_path.with_suffix(".epJSON")
    subprocess.run(
        [
            "energyplus",
            "--convert-only",
            "--output-directory",
            str(idf_path.parent),
            str(idf_path),
        ],
        check=True,
        timeout=ENERGYPLUS_SUBPROCESS_TIMEOUT_SECONDS,
    )
    return epjson_path
