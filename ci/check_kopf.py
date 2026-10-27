#!/usr/bin/env python3
"""Prueft den Kopfblock jeder Datei unter dashboard/ und der Entwuerfe.

Jede Karte, View, Template- und Konfig-Datei, jedes JS-Modul und jeder Entwurf
beginnt mit einem festen Block:

    # ============================================================================
    # Waschmaschine – Programmstatus mit Animation
    # ----------------------------------------------------------------------------
    # Art:           karte
    # Bereich:       hausgeraete
    # Status:        aktiv
    # Karten:        button-card
    # Templates:     nachtblau_geraete_fx (hausgeraete-templates.yaml)
    # Einfuegen:     Karte hinzufuegen -> Manuell
    # Platzhalter:   seriennr_<geraet> (vor dem Einfuegen ersetzen, siehe README.md)
    # ============================================================================

JS-Module schreiben dieselben Zeilen mit "//", HTML- und Markdown-Entwuerfe
ohne Praefix in einem "<!-- ... -->"-Kommentar ganz oben. Eine lange Zeile
darf mit mindestens drei Leerzeichen eingerueckt weitergehen.

Geprueft wird:

1. Block vorhanden, Titel nicht leer, genau die Schluessel der Dateiart in
   fester Reihenfolge (SCHLUESSEL).
2. Art passt zum Dateinamen, Bereich zum Ordner, Status zum Ablageort:
   "aktiv" im Bereichsordner, "entwurf" in entwuerfe/, in archiv/ "archiv"
   oder "archiv: ersetzt durch <datei>" (die Datei existiert).
3. Karten = die im Inhalt genutzten "custom:"-Karten plus card-mod, nicht mehr,
   nicht weniger. Eingebundene Dateien (!include) zaehlen nicht mit.
4. Templates = die genutzten button-card- und decluttering-Templates, die nicht
   in der Datei selbst stehen, jeweils mit der Datei, die sie definiert.
5. Platzhalter = die Treffer der Muster aus design/platzhalter.yaml. Dateien
   ausserhalb von dashboard/ mit Platzhaltern stehen dort unter
   "dateien_ohne_kopf".
6. Gehoert-zu (Entwuerfe) nennt nur Dateien, die es gibt.

Aufruf: python ci/check_kopf.py
"""

from __future__ import annotations

import re
import sys
from pathlib import PurePosixPath

import yaml
from check_yaml import HALoader, walk
from dateien import REPO_ROOT, alle_dateien, art

PLATZHALTER_DATEI = REPO_ROOT / "design" / "platzhalter.yaml"

SCHLUESSEL = {
    "karte": ("Art", "Bereich", "Status", "Karten", "Templates", "Einfuegen", "Platzhalter"),
    "view": ("Art", "Bereich", "Status", "Karten", "Templates", "Einfuegen", "Platzhalter"),
    "templates": ("Art", "Bereich", "Status", "Karten", "Templates", "Einfuegen", "Platzhalter"),
    "konfig": ("Art", "Bereich", "Status", "Einfuegen", "Platzhalter"),
    "ressource": ("Art", "Bereich", "Status", "Einfuegen", "Platzhalter"),
    "entwurf": ("Art", "Bereich", "Status", "Gehoert-zu", "Platzhalter"),
}

LINIE_DOPPELT = re.compile(r"^=+$")
LINIE_EINFACH = re.compile(r"^-+$")
SCHLUESSEL_ZEILE = re.compile(r"^([A-Za-z-]+):\s+(\S.*)$")
FORTSETZUNG = re.compile(r"^\s{3,}(\S.*)$")
LOVELACE_ART = re.compile(r"-(karte|view|templates|konfig)(?:-v\d+)?\.yaml$")
TEMPLATE_NAME = re.compile(r"^[a-z0-9_]+$")
CUSTOM_KARTE = re.compile(r"custom:([a-z0-9-]+)")
ERSETZEN_HINWEIS = re.compile(r"\s*\(vor dem Einfuegen ersetzen[^)]*\)\s*$")


def im_geltungsbereich(pfad: PurePosixPath) -> bool:
    if "entwuerfe" in pfad.parts:
        return pfad.suffix in (".html", ".md")
    return pfad.parts[0] == "dashboard" and art(pfad) in ("lovelace", "ressource")


def erwartete_art(pfad: PurePosixPath) -> str | None:
    if "entwuerfe" in pfad.parts:
        return "entwurf"
    if pfad.suffix == ".js":
        return "ressource"
    treffer = LOVELACE_ART.search(pfad.name)
    return treffer.group(1) if treffer else None


def kopfzeilen(pfad: PurePosixPath, text: str) -> list[str] | None:
    """Die Zeilen des Kopfblocks ohne Kommentarpraefix, oder None."""
    zeilen = text.splitlines()
    if pfad.suffix in (".html", ".md"):
        if not zeilen or zeilen[0].strip() != "<!--":
            return None
        try:
            ende = next(i for i, z in enumerate(zeilen) if z.strip() == "-->")
        except StopIteration:
            return None
        return zeilen[1:ende]
    praefix = "//" if pfad.suffix == ".js" else "#"
    block: list[str] = []
    for zeile in zeilen:
        if not zeile.startswith(praefix):
            break
        block.append(zeile[len(praefix):].removeprefix(" "))
    return block


def parse_kopf(zeilen: list[str]) -> tuple[str, list[tuple[str, str]]] | str:
    """(titel, [(schluessel, wert)]) oder eine Fehlermeldung."""
    if len(zeilen) < 4 or not LINIE_DOPPELT.match(zeilen[0].strip()):
        return "kein Kopfblock (erste Zeile '# ====...')"
    titel = zeilen[1].strip()
    if not titel or not LINIE_EINFACH.match(zeilen[2].strip()):
        return "Kopfblock: Titelzeile und '# ----...' darunter fehlen"
    eintraege: list[tuple[str, str]] = []
    for zeile in zeilen[3:]:
        if LINIE_DOPPELT.match(zeile.strip()):
            return titel, eintraege
        schluessel = SCHLUESSEL_ZEILE.match(zeile)
        weiter = FORTSETZUNG.match(zeile)
        if schluessel:
            eintraege.append((schluessel.group(1), schluessel.group(2).strip()))
        elif weiter and eintraege:
            k, v = eintraege[-1]
            eintraege[-1] = (k, f"{v} {weiter.group(1).strip()}")
        else:
            return f"Kopfblock: unerwartete Zeile '{zeile.strip()}'"
    return "Kopfblock ohne abschliessende Zeile '# ====...'"


def ohne_kopf(pfad: PurePosixPath, text: str) -> str:
    """Der Text ohne den Kopfblock -- sonst bestaetigte sich die Zeile
    "Platzhalter:" selbst, weil sie die Platzhalter nennt."""
    zeilen = text.splitlines()
    if pfad.suffix in (".html", ".md"):
        ende = next((i for i, z in enumerate(zeilen) if z.strip() == "-->"), -1)
        return "\n".join(zeilen[ende + 1:])
    praefix = "//" if pfad.suffix == ".js" else "#"
    doppelt = [i for i, z in enumerate(zeilen[:60])
               if z.startswith(praefix) and LINIE_DOPPELT.match(z[len(praefix):].strip())]
    return "\n".join(zeilen[doppelt[1] + 1:]) if len(doppelt) >= 2 else text


def abweichung(pfad: PurePosixPath, was: str, angegeben: set[str], genutzt: set[str]) -> str:
    fehlt = ", ".join(sorted(genutzt - angegeben)) or "-"
    zuviel = ", ".join(sorted(angegeben - genutzt)) or "-"
    return f"{pfad}: {was} passen nicht zum Inhalt (fehlt: {fehlt}; zu viel: {zuviel})"


def liste(wert: str) -> list[str]:
    return [] if wert == "keine" else [t.strip() for t in wert.split(",") if t.strip()]


def ohne_kommentare(text: str) -> str:
    return "\n".join(z for z in text.splitlines() if not z.lstrip().startswith(("#", "//")))


def genutzte_karten(text: str) -> set[str]:
    rumpf = ohne_kommentare(text)
    karten = set(CUSTOM_KARTE.findall(rumpf))
    if re.search(r"\bcard_mod\b", rumpf):
        karten.add("card-mod")
    return karten


def lade_yaml(text: str):
    loader = HALoader(text)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()


def templates_in(daten) -> tuple[set[str], set[str]]:
    """(definiert, genutzt) in einer geladenen YAML-Struktur."""
    definiert: set[str] = set()
    if isinstance(daten, dict):
        for block in ("button_card_templates", "decluttering_templates"):
            definiert |= set((daten.get(block) or {}).keys())
    genutzt: set[str] = set()
    for _, knoten in walk(daten):
        if isinstance(knoten, dict) and "template" in knoten:
            werte = knoten["template"]
            for wert in werte if isinstance(werte, list) else [werte]:
                if isinstance(wert, str) and TEMPLATE_NAME.match(wert):
                    genutzt.add(wert)
    return definiert, genutzt


def platzhalter_treffer(text: str, muster: dict[str, re.Pattern[str]]) -> set[str]:
    return {pid for pid, rx in muster.items() if rx.search(text)}


def main() -> int:
    daten = yaml.safe_load(PLATZHALTER_DATEI.read_text(encoding="utf-8"))
    muster = {e["id"]: re.compile(e["muster"]) for e in daten["platzhalter"]}
    ausnahmen = set(daten.get("dateien_ohne_kopf") or [])

    dateien = alle_dateien()
    namen = {p.name for p in dateien}
    texte = {p: (REPO_ROOT / p).read_text(encoding="utf-8") for p in dateien if art(p) != "bild"}

    # Wo ist welches Template definiert?
    definiert_in: dict[str, str] = {}
    for p, text in texte.items():
        if p.parts[0] == "dashboard" and art(p) == "lovelace":
            for name in templates_in(lade_yaml(text))[0]:
                definiert_in[name] = p.name

    fehler: list[str] = []
    geprueft = 0
    for p in dateien:
        text = texte.get(p)
        if text is None:
            continue
        if not im_geltungsbereich(p):
            treffer = platzhalter_treffer(text, muster)
            if treffer and p.as_posix() not in ausnahmen:
                fehler.append(
                    f"{p}: enthaelt Platzhalter ({', '.join(sorted(treffer))}) ohne Kopfblock "
                    "-- in design/platzhalter.yaml unter dateien_ohne_kopf eintragen"
                )
            continue

        geprueft += 1
        zeilen = kopfzeilen(p, text)
        kopf = parse_kopf(zeilen) if zeilen is not None else "kein Kopfblock"
        if isinstance(kopf, str):
            fehler.append(f"{p}: {kopf}")
            continue
        _, eintraege = kopf
        werte = dict(eintraege)
        treffer = platzhalter_treffer(ohne_kopf(p, text), muster)
        dateiart = erwartete_art(p)
        erwartet = SCHLUESSEL.get(dateiart or "", ())
        if tuple(k for k, _ in eintraege) != erwartet:
            fehler.append(
                f"{p}: Schluessel {', '.join(k for k, _ in eintraege)} -- erwartet "
                f"{', '.join(erwartet)} in dieser Reihenfolge"
            )
            continue

        if werte["Art"] != dateiart:
            fehler.append(f"{p}: Art '{werte['Art']}', laut Dateiname '{dateiart}'")
        bereich = p.parts[1] if p.parts[0] == "dashboard" else p.parts[0]
        if werte["Bereich"] != bereich:
            fehler.append(f"{p}: Bereich '{werte['Bereich']}', laut Ordner '{bereich}'")

        status = werte["Status"]
        if "entwuerfe" in p.parts:
            if status != "entwurf":
                fehler.append(f"{p}: Status muss 'entwurf' sein")
        elif "archiv" in p.parts:
            ersatz = re.fullmatch(r"archiv(?:: ersetzt durch (\S+))?", status)
            if not ersatz:
                fehler.append(
                    f"{p}: Status muss 'archiv' oder 'archiv: ersetzt durch <datei>' sein"
                )
            elif ersatz.group(1) and ersatz.group(1) not in namen:
                fehler.append(f"{p}: Nachfolgerin '{ersatz.group(1)}' gibt es nicht")
        elif status != "aktiv":
            fehler.append(f"{p}: Status muss 'aktiv' sein (ausserhalb von archiv/)")

        if "Karten" in werte:
            angegeben = set(liste(werte["Karten"]))
            genutzt = genutzte_karten(text)
            if angegeben != genutzt:
                fehler.append(abweichung(p, "Karten", angegeben, genutzt))

        if "Templates" in werte:
            definiert, genutzt = templates_in(lade_yaml(text))
            genutzt -= definiert
            angegeben: dict[str, str] = {}
            for eintrag in liste(werte["Templates"]):
                t = re.fullmatch(r"([a-z0-9_]+) \(([^)]+)\)", eintrag)
                if not t:
                    fehler.append(f"{p}: Templates-Eintrag '{eintrag}' -- Form 'name (datei)'")
                    continue
                angegeben[t.group(1)] = t.group(2)
            if set(angegeben) != genutzt:
                fehler.append(abweichung(p, "Templates", set(angegeben), genutzt))
            for name, datei in angegeben.items():
                if name in genutzt and definiert_in.get(name) != datei:
                    ort = definiert_in.get(name, "nirgends im Repo")
                    fehler.append(f"{p}: Template {name} steht in {ort}, nicht in {datei}")

        if "Gehoert-zu" in werte:
            for datei in liste(werte["Gehoert-zu"]):
                if datei not in namen:
                    fehler.append(f"{p}: Gehoert-zu nennt '{datei}', die es nicht gibt")

        wert = werte["Platzhalter"]
        ids = liste(ERSETZEN_HINWEIS.sub("", wert))
        if ids and not ERSETZEN_HINWEIS.search(wert):
            fehler.append(f"{p}: Platzhalter ohne '(vor dem Einfuegen ersetzen, siehe README.md)'")
        if set(ids) != treffer:
            fehler.append(abweichung(p, "Platzhalter", set(ids), treffer))

    for eintrag in sorted(ausnahmen):
        p = PurePosixPath(eintrag)
        if p not in texte:
            fehler.append(
                f"design/platzhalter.yaml: dateien_ohne_kopf nennt '{eintrag}', die es nicht gibt"
            )
        elif not platzhalter_treffer(texte[p], muster):
            fehler.append(f"design/platzhalter.yaml: '{eintrag}' enthaelt keine Platzhalter mehr")

    for f in fehler:
        print(f"FEHLER  {f}")
    print(f"\n{geprueft} Datei(en) mit Kopfblock geprueft, {len(fehler)} Problem(e).")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
