#!/usr/bin/env python3
"""Prueft, dass jeder im Repo genannte Dateiname auch existiert.

Karten, Views, Doku und Entwuerfe verweisen aufeinander -- im Kommentarkopf
("Template aus wetter-animation-button-card-templates.yaml"), in Markdown-Links
und per "!include". Wird eine Datei umbenannt oder verschoben, zeigen diese
Verweise ins Leere, und nichts meldet es: Home Assistant nicht, weil Kommentare
nicht ausgewertet werden, und GitHub nicht, weil ein toter Link nur beim
Anklicken auffaellt.

Geprueft wird:

1. Jeder "!include"-Pfad in einer YAML-Datei existiert, relativ zu der Datei,
   die ihn einbindet (so loest Home Assistant ihn auf).
2. Jeder andere Dateiname, der wie eine Repo-Datei aussieht, existiert:
   - mit "/" als Pfad relativ zum Repo oder zur nennenden Datei,
   - ohne "/" als Dateiname irgendwo im Repo (Kommentare nennen meist nur
     den Namen, nicht den Ordner).

"Sieht wie eine Repo-Datei aus" heisst: bekannte Endung und ein Bindestrich
oder Unterstrich im Namen (wie bei allen Repo-Dateien), ein fuehrender Punkt
(.yamllint.yml) oder ein Name aus GROSS_DATEIEN. Das schliesst JS-Ausdruecke
wie "C.txt" und Dateien ausserhalb des Repos wie configuration.yaml und
secrets.yaml aus. Nicht geprueft werden URLs, absolute Pfade (/local/...),
Pfade unter lokal/, Muster mit * oder ... und Platzhalter wie <datei>.

Aufruf: python ci/check_verweise.py [datei ...]
Ohne Argumente werden alle Dateien ausser den Grafana-Dashboards geprueft
(JSON ohne Kommentare, die Proxmox-Dashboards sind generiert).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path, PurePosixPath

from dateien import REPO_ROOT, alle_dateien, art

ENDUNGEN = r"(?:yaml|yml|md|html|js|json|py|txt|toml)"

# Ein Pfad-Token: optional Ordner, dann ein Dateiname mit bekannter Endung.
# Davor kein Zeichen, das das Token zu einem laengeren Ausdruck macht ("*",
# "…", "<"), dahinter kein Wortzeichen.
TOKEN = re.compile(
    r"(?<![\w./*<>…-])((?:[\w.-]+/)*\.?[A-Za-z0-9][\w.-]*\." + ENDUNGEN + r")(?![\w/-])"
)
INCLUDE = re.compile(r"^[^#]*!include(?:_dir_\w+)?\s+([^\s#]+)")
URL = re.compile(r"[a-z][a-z0-9+.-]*://\S+")

GROSS_DATEIEN = {"README.md", "DESIGN.md", "CLAUDE.md", "SKILL.md"}

# Bewusst genannte Dateien, die es im Repo nicht (mehr) gibt.
AUSNAHMEN = {
    "unifi-button-card.yaml": "alte Fassung, nur noch im Git-Verlauf (netzwerk-view.yaml)",
}


def sieht_wie_repo_datei_aus(token: str) -> bool:
    name = token.rsplit("/", 1)[-1]
    if name.startswith(".") or name in GROSS_DATEIEN:
        return True
    stamm = name.rsplit(".", 1)[0]
    return re.search(r"[a-z0-9][-_][a-z0-9]", stamm) is not None


def normiert(pfad: PurePosixPath) -> str:
    return os.path.normpath(pfad.as_posix()).replace(os.sep, "/")


def pruefe_datei(
    pfad: PurePosixPath, pfade: set[str], namen: set[str]
) -> tuple[list[str], int]:
    fehler: list[str] = []
    anzahl = 0
    text = (REPO_ROOT / pfad).read_text(encoding="utf-8")
    ist_yaml = pfad.suffix in (".yaml", ".yml")

    for nr, zeile in enumerate(text.splitlines(), start=1):
        if ist_yaml:
            treffer = INCLUDE.match(zeile)
            if treffer:
                ziel = treffer.group(1).strip("'\"")
                ort = "Repo-Wurzel" if pfad.parent == PurePosixPath(".") else pfad.parent
                anzahl += 1
                if normiert(pfad.parent / ziel) not in pfade:
                    fehler.append(
                        f"{pfad}:{nr}: !include {ziel} -- Datei existiert nicht "
                        f"(relativ zu {ort})"
                    )

        for token in TOKEN.findall(URL.sub(" ", zeile)):
            if token.startswith(("lokal/", "/")) or not sieht_wie_repo_datei_aus(token):
                continue
            if token in AUSNAHMEN:
                continue
            anzahl += 1
            if "/" in token:
                gefunden = (
                    normiert(PurePosixPath(token)) in pfade
                    or normiert(pfad.parent / token) in pfade
                )
            else:
                gefunden = token in namen
            if not gefunden:
                fehler.append(f"{pfad}:{nr}: '{token}' gibt es im Repo nicht")

    return fehler, anzahl


def main(argv: list[str]) -> int:
    alle = alle_dateien()
    pfade = {p.as_posix() for p in alle}
    namen = {p.name for p in alle}

    if argv:
        zu_pruefen = [
            PurePosixPath(Path(a).resolve().relative_to(REPO_ROOT).as_posix()) for a in argv
        ]
    else:
        zu_pruefen = [p for p in alle if art(p) != "grafana" and p.name != "LICENSE"]

    if not zu_pruefen:
        print("Keine Dateien gefunden.")
        return 1

    fehler: list[str] = []
    verweise = 0
    for pfad in zu_pruefen:
        f, n = pruefe_datei(pfad, pfade, namen)
        fehler.extend(f)
        verweise += n

    for f in fehler:
        print(f"FEHLER  {f}")
    print(
        f"\n{len(zu_pruefen)} Datei(en), {verweise} Verweis(e) geprueft, "
        f"{len(fehler)} ins Leere."
    )
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
