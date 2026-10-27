#!/usr/bin/env python3
"""Erzeugt die Dateiuebersichten aus den Kopfbloecken und design/platzhalter.yaml.

Erzeugt werden:

- README.md zwischen "<!-- index:start -->" und "<!-- index:end -->": die
  Bereichstabelle (aktuelle Dateien, archiv/, entwuerfe/).
- README.md zwischen "<!-- platzhalter:start -->" und "<!-- platzhalter:end -->":
  die Tabelle der Platzhalter mit den Dateien, die sie enthalten.
- dashboard/README.md vollstaendig: jede Datei mit Titel, Art, Karten,
  Platzhaltern und Status.

Von Hand gepflegt werden nur die Kopfbloecke und design/platzhalter.yaml.

Aufruf:
  python ci/gen_index.py            schreibt die Dateien
  python ci/gen_index.py --pruefen  schlaegt fehl, wenn sie nicht aktuell sind
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath

import yaml
from check_kopf import ERSETZEN_HINWEIS, kopfzeilen, liste, parse_kopf
from dateien import BEREICHE, REPO_ROOT, alle_dateien, art

README = REPO_ROOT / "README.md"
DASHBOARD_README = REPO_ROOT / "dashboard" / "README.md"
PLATZHALTER_DATEI = REPO_ROOT / "design" / "platzhalter.yaml"

# Dateien, die Platzhalter nur erklaeren; sie stehen nicht in der Tabelle.
NUR_ERKLAERUNG = {
    "README.md",
    "dashboard/README.md",
    "design/platzhalter.yaml",
    ".claude/skills/platzhalter-einsetzen/SKILL.md",
}


def code(name: str) -> str:
    return f"`{name}`"


def zelle(text: str) -> str:
    return text.replace("|", "\\|")


def koepfe() -> dict[PurePosixPath, dict[str, str]]:
    """Kopfwerte (plus Titel) aller Dateien mit Kopfblock."""
    ergebnis = {}
    for p in alle_dateien():
        if p.parts[0] not in ("dashboard", "grafana") or p.name == "README.md":
            continue
        if p.parts[0] == "grafana" and "entwuerfe" not in p.parts:
            continue
        if art(p) == "bild":
            continue
        text = (REPO_ROOT / p).read_text(encoding="utf-8")
        zeilen = kopfzeilen(p, text)
        kopf = parse_kopf(zeilen) if zeilen is not None else None
        if isinstance(kopf, tuple):
            titel, eintraege = kopf
            ergebnis[p] = {"Titel": titel, **dict(eintraege)}
    return ergebnis


def ablage(p: PurePosixPath) -> str:
    if "archiv" in p.parts:
        return "archiv"
    if "entwuerfe" in p.parts:
        return "entwuerfe"
    return "aktuell"


def bereichstabelle(alle: dict[PurePosixPath, dict[str, str]]) -> str:
    gruppen: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for p in sorted(alle, key=lambda q: q.name):
        if p.parts[0] == "dashboard":
            gruppen[p.parts[1]][ablage(p)].append(code(p.name))
    zeilen = [
        "| Bereich | Aktuelle Dateien | `archiv/` | `entwuerfe/` |",
        "|---|---|---|---|",
    ]
    for bereich in BEREICHE:
        g = gruppen.get(bereich, {})
        spalten = [", ".join(g.get(k, [])) or "–" for k in ("aktuell", "archiv", "entwuerfe")]
        zeilen.append(f"| [`{bereich}/`](dashboard/{bereich}/) | " + " | ".join(spalten) + " |")

    dashboards = sorted(p.name for p in alle_dateien()
                        if p.parts[0] == "grafana" and p.suffix == ".json")
    grafana_entwuerfe = sorted(p.name for p in alle if p.parts[0] == "grafana")
    zeilen.append(
        "| [`grafana/`](grafana/) | " + ", ".join(map(code, dashboards)) + " | – | "
        + (", ".join(map(code, grafana_entwuerfe)) or "–") + " |"
    )
    doku = sorted(p.name for p in alle_dateien() if p.parts[0] == "doku")
    zeilen.append("| [`doku/`](doku/) | " + ", ".join(map(code, doku)) + " | – | – |")
    return "\n".join(zeilen)


def platzhaltertabelle(alle: dict[PurePosixPath, dict[str, str]]) -> str:
    daten = yaml.safe_load(PLATZHALTER_DATEI.read_text(encoding="utf-8"))
    vorkommen: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for p, werte in sorted(alle.items(), key=lambda e: e[0].name):
        for pid in liste(ERSETZEN_HINWEIS.sub("", werte["Platzhalter"])):
            gruppe = "archiv" if "archiv" in p.parts else "aktuell"
            vorkommen[pid][gruppe].append(code(p.name))
    muster = {e["id"]: re.compile(e["muster"]) for e in daten["platzhalter"]}
    for eintrag in sorted(daten.get("dateien_ohne_kopf") or []):
        if eintrag in NUR_ERKLAERUNG:
            continue
        text = (REPO_ROOT / eintrag).read_text(encoding="utf-8")
        for pid, rx in muster.items():
            if rx.search(text):
                vorkommen[pid]["aktuell"].append(code(eintrag))

    zeilen = [
        "| Platzhalter | Steht für | Echte ID finden | Dateien |",
        "|---|---|---|---|",
    ]
    for e in daten["platzhalter"]:
        v = vorkommen.get(e["id"], {})
        dateien = ", ".join(v.get("aktuell", [])) or "–"
        if v.get("archiv"):
            dateien += "; in `archiv/`: " + ", ".join(v["archiv"])
        spalten = [zelle(e["anzeige"]), zelle(e["steht_fuer"]), zelle(e["finden"]), dateien]
        zeilen.append("| " + " | ".join(spalten) + " |")
    return "\n".join(zeilen)


def status_text(werte: dict[str, str]) -> str:
    status = werte["Status"]
    treffer = re.fullmatch(r"archiv: ersetzt durch (\S+)", status)
    if treffer:
        return f"archiv, ersetzt durch {code(treffer.group(1))}"
    if status == "entwurf":
        gehoert = liste(werte.get("Gehoert-zu", "keine"))
        return "Entwurf" + (" zu " + ", ".join(map(code, gehoert)) if gehoert else "")
    return status


def dashboard_readme(alle: dict[PurePosixPath, dict[str, str]]) -> str:
    teile = [
        "<!-- Erzeugt von ci/gen_index.py aus den Kopfbloecken der Dateien. "
        "Nicht von Hand aendern, sondern die Koepfe pflegen und "
        "`python ci/gen_index.py` laufen lassen. -->",
        "",
        "# Dashboard-Dateien",
        "",
        "Alle Karten, Views, Templates, Konfig-Dateien und Entwürfe nach Bereich. "
        "Titel, Karten, Platzhalter und Status stammen aus dem Kopfblock jeder Datei "
        "(Aufbau: [`ci/README.md`](../ci/README.md), Abschnitt „Dateikopf“). "
        "Wie die Dateien eingefügt werden und was die Platzhalter bedeuten, steht im "
        "[README](../README.md).",
    ]
    for bereich in BEREICHE:
        reihenfolge = {"aktuell": 0, "entwuerfe": 1, "archiv": 2}
        eintraege = sorted(
            ((p, w) for p, w in alle.items() if p.parts[:2] == ("dashboard", bereich)),
            key=lambda e: (reihenfolge[ablage(e[0])], e[0].name),
        )
        if not eintraege:
            continue
        teile += [
            "",
            f"## {bereich}",
            "",
            "| Datei | Art | Titel | Karten | Platzhalter | Status |",
            "|---|---|---|---|---|---|",
        ]
        for p, w in eintraege:
            relativ = PurePosixPath(*p.parts[1:]).as_posix()
            platzhalter = ", ".join(map(code, liste(ERSETZEN_HINWEIS.sub("", w["Platzhalter"]))))
            teile.append(
                f"| [{code(p.name)}]({relativ}) | {w['Art']} | {zelle(w['Titel'])} | "
                f"{w.get('Karten', '–') if w.get('Karten') != 'keine' else '–'} | "
                f"{platzhalter or '–'} | {status_text(w)} |"
            )
    return "\n".join(teile) + "\n"


def ersetze_abschnitt(text: str, name: str, inhalt: str) -> str:
    start, ende = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(ende) != 1:
        raise SystemExit(f"README.md: Marker {start} / {ende} fehlen oder sind doppelt")
    vorne, rest = text.split(start)
    _, hinten = rest.split(ende)
    return f"{vorne}{start}\n{inhalt}\n{ende}{hinten}"


def main(argv: list[str]) -> int:
    pruefen = "--pruefen" in argv
    alle = koepfe()
    readme_alt = README.read_text(encoding="utf-8")
    readme_neu = ersetze_abschnitt(readme_alt, "index", bereichstabelle(alle))
    readme_neu = ersetze_abschnitt(readme_neu, "platzhalter", platzhaltertabelle(alle))
    ziele: list[tuple[Path, str]] = [
        (README, readme_neu),
        (DASHBOARD_README, dashboard_readme(alle)),
    ]

    veraltet = []
    for pfad, inhalt in ziele:
        alt = pfad.read_text(encoding="utf-8") if pfad.exists() else ""
        if alt != inhalt:
            veraltet.append(pfad.relative_to(REPO_ROOT).as_posix())
            if not pruefen:
                pfad.write_text(inhalt, encoding="utf-8")

    if pruefen and veraltet:
        for name in veraltet:
            print(f"FEHLER  {name} ist nicht aktuell -- python ci/gen_index.py laufen lassen")
        return 1
    print("Aktualisiert: " + ", ".join(veraltet) if veraltet and not pruefen
          else f"{len(alle)} Kopfbloecke, Uebersichten aktuell.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
