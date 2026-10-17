#!/usr/bin/env python3
"""Prueft Ablageort und Namen jeder Datei gegen die Repo-Struktur.

Die Regeln stehen kurz hier und ausfuehrlich in ci/README.md:

1. Im Wurzelverzeichnis liegen nur README.md, DESIGN.md, CLAUDE.md,
   CONTRIBUTING.md, LICENSE, pyproject.toml und Punktdateien.
2. Oberste Ordner: dashboard/, design/, grafana/, doku/, ci/, .claude/,
   .github/.
3. dashboard/<bereich>/ mit einem Bereich aus ci/dateien.py (BEREICHE);
   darunter nur die Unterordner archiv/ und entwuerfe/.
4. Lovelace-YAML heisst <thema>[-<variante>]-<art>[-vN].yaml mit der Art
   karte, view, templates oder konfig; JS-Module <name>.js; alles klein,
   ASCII, Bindestriche.
5. In entwuerfe/ nur HTML und Markdown, in doku/ nur Markdown.
6. Je Ordner hoechstens eine aktive Version einer Karte: abgeloeste
   Fassungen gehoeren nach archiv/.

Aufruf: python ci/check_struktur.py [--streng]
Ohne --streng werden Verstoesse nur als WARNUNG gemeldet und die Pruefung
bleibt gruen. Das gilt, bis die Dateien in die neue Struktur umgezogen sind;
danach laeuft sie in der CI mit --streng.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import PurePosixPath

from dateien import BEREICHE, alle_dateien, art

WURZEL_DATEIEN = {
    "README.md",
    "DESIGN.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "pyproject.toml",
}
OBERSTE_ORDNER = {"dashboard", "design", "grafana", "doku", "ci", ".claude", ".github"}
UNTERORDNER = {"archiv", "entwuerfe"}

LOVELACE_NAME = re.compile(
    r"^(?P<stamm>[a-z0-9]+(?:-[a-z0-9]+)*?)-(?P<art>karte|view|templates|konfig)"
    r"(?:-v(?P<version>[2-9]|[1-9][0-9]))?\.yaml$"
)
EINFACHER_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z]+$")


def pruefe(pfad: PurePosixPath) -> list[str]:
    teile = pfad.parts
    name = pfad.name

    if len(teile) == 1:
        if name in WURZEL_DATEIEN or name.startswith("."):
            return []
        return [f"{pfad}: gehoert nicht ins Wurzelverzeichnis (Bereich unter dashboard/)"]

    if teile[0] not in OBERSTE_ORDNER:
        erlaubt = ", ".join(sorted(OBERSTE_ORDNER))
        return [f"{pfad}: Ordner '{teile[0]}/' ist nicht vorgesehen ({erlaubt})"]

    if teile[0] == "doku":
        if pfad.suffix != ".md" or len(teile) != 2:
            return [f"{pfad}: in doku/ liegt nur Markdown, ohne Unterordner"]
        return []

    if teile[0] != "dashboard":
        return []

    fehler: list[str] = []
    if len(teile) < 3 or teile[1] not in BEREICHE:
        return [f"{pfad}: '{teile[1]}' ist kein Bereich (ci/dateien.py, BEREICHE)"]
    if len(teile) > 4 or (len(teile) == 4 and teile[2] not in UNTERORDNER):
        return [f"{pfad}: unter dashboard/{teile[1]}/ nur archiv/ und entwuerfe/"]

    in_entwuerfen = len(teile) == 4 and teile[2] == "entwuerfe"
    dateiart = art(pfad)
    if in_entwuerfen:
        if pfad.suffix not in (".html", ".md"):
            fehler.append(f"{pfad}: in entwuerfe/ liegen nur HTML und Markdown")
        elif not EINFACHER_NAME.match(name):
            fehler.append(f"{pfad}: Name nur klein, ASCII, Bindestriche")
    elif dateiart == "lovelace":
        if not LOVELACE_NAME.match(name):
            fehler.append(
                f"{pfad}: Name folgt nicht <thema>[-<variante>]-<art>[-vN].yaml "
                "(art: karte, view, templates, konfig)"
            )
    elif dateiart == "ressource":
        if not EINFACHER_NAME.match(name):
            fehler.append(f"{pfad}: Name nur klein, ASCII, Bindestriche")
    else:
        fehler.append(f"{pfad}: Entwuerfe nach entwuerfe/, Doku nach doku/")
    return fehler


def doppelte_versionen(dateien: list[PurePosixPath]) -> list[str]:
    """Mehr als eine aktive Version derselben Karte im selben Ordner."""
    gruppen: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for pfad in dateien:
        if "archiv" in pfad.parts:
            continue
        treffer = LOVELACE_NAME.match(pfad.name)
        if treffer:
            schluessel = (pfad.parent.as_posix(), treffer["stamm"], treffer["art"])
            gruppen[schluessel].append(pfad.name)
    return [
        f"{ordner}/: {len(namen)} aktive Versionen von {stamm}-{dateiart} "
        f"({', '.join(sorted(namen))}) -- abgeloeste nach archiv/"
        for (ordner, stamm, dateiart), namen in sorted(gruppen.items())
        if len(namen) > 1
    ]


def main(argv: list[str]) -> int:
    streng = "--streng" in argv
    dateien = alle_dateien()
    verstoesse = [f for pfad in dateien for f in pruefe(pfad)]
    verstoesse += doppelte_versionen(dateien)

    stufe = "FEHLER " if streng else "WARNUNG"
    for v in verstoesse:
        print(f"{stufe} {v}")
    print(f"\n{len(dateien)} Datei(en) geprueft, {len(verstoesse)} Verstoss/Verstoesse.")
    if verstoesse and not streng:
        print("Nur Bericht: ohne --streng bleibt die Pruefung gruen.")
    return 1 if verstoesse and streng else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
