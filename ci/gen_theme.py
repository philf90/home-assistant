#!/usr/bin/env python3
"""Erzeugt das Owlet-Theme fuer Home Assistant aus design/palette.yaml.

Quelle ist der Abschnitt "theme" der Palette: jede Variable mit ihrem Wert im
dunklen und im hellen Modus, dazu die Schalter (Prozentwerte je Modus). Die
Datei theme.datei wird vollstaendig erzeugt, samt Kopfblock; von Hand
gepflegt wird nur die Palette. Ob die Werte selbst gueltig sind, prueft
ci/check_palette.py.

Aufruf:
  python ci/gen_theme.py            schreibt die Theme-Datei
  python ci/gen_theme.py --pruefen  schlaegt fehl, wenn sie nicht aktuell ist
"""

from __future__ import annotations

import sys

import yaml
from dateien import REPO_ROOT

PALETTE_FILE = REPO_ROOT / "design" / "palette.yaml"

KOPF = """\
# ============================================================================
# Owlet-Theme – Farben fuer den hellen und den dunklen Modus
# ----------------------------------------------------------------------------
# Art:           konfig
# Bereich:       allgemein
# Status:        aktiv
# Einfuegen:     /config/themes/{name}.yaml, in configuration.yaml
#                frontend: themes: !include_dir_merge_named themes
# Platzhalter:   keine
# ============================================================================
# ERZEUGT aus design/palette.yaml (Abschnitt theme) mit python ci/gen_theme.py.
# Nicht von Hand aendern: Werte in der Palette pflegen und neu erzeugen.
# Regeln und Messwerte: DESIGN.md, Abschnitt "Heller Modus".
#
# Das Theme hat beide Modi. Welcher gilt, waehlt jeder Benutzer im Profil
# oder im More-Menue (System, Hell, Dunkel); "System" folgt dem Geraet.
# Karten lesen die Farben als CSS-Variablen, z. B. var(--owlet-gruen);
# Toenungen entstehen mit color-mix(in srgb, var(--owlet-gruen) 12%, transparent).
# Die Home-Assistant-Variablen (primary-background-color usw.) bekommen
# dieselben Werte wie die zugehoerigen owlet-Variablen.
# Schalter sind keine Farben, sondern Anteile fuer color-mix: Der Wert von
# owlet-dunkel-anteil (dunkel 100 %, hell 0 %) waehlt zwischen zwei Farben.
#
# Aktivieren: Profil -> Theme "{name}", oder fuer alle als Standard mit der
# Aktion frontend.set_theme (name: {name}).
#
# Voraussetzung: keine Integration; nach dem Einfuegen Aktion
# frontend.reload_themes ausfuehren oder Home Assistant neu starten.
"""


def wert(text: str) -> str:
    return '"' + text + '"'


def erzeuge(theme: dict) -> str:
    variablen = theme["variablen"]
    zeilen = [KOPF.format(name=theme["name"]).rstrip("\n"), f"{theme['name']}:", "  modes:"]
    for modus, schluessel in (("dark", "dunkel"), ("light", "hell")):
        zeilen.append(f"    {modus}:")
        ha = [(h, v[schluessel]) for v in variablen for h in v.get("ha") or []]
        if ha:
            zeilen.append("      # Home Assistant")
            zeilen += [f"      {h}: {wert(w)}" for h, w in ha]
            zeilen.append("      # Owlet")
        zeilen += [f"      {v['name']}: {wert(v[schluessel])}" for v in variablen]
        schalter = theme.get("schalter") or []
        if schalter:
            zeilen.append("      # Schalter")
            zeilen += [f"      {s['name']}: {wert(s[schluessel])}" for s in schalter]
    return "\n".join(zeilen) + "\n"


def main(argv: list[str]) -> int:
    pruefen = "--pruefen" in argv
    daten = yaml.safe_load(PALETTE_FILE.read_text(encoding="utf-8"))
    theme = daten.get("theme") or {}
    if not theme.get("name") or not theme.get("datei") or not theme.get("variablen"):
        print("FEHLER  design/palette.yaml: Abschnitt theme braucht name, datei und variablen")
        return 1

    ziel = REPO_ROOT / theme["datei"]
    neu = erzeuge(theme)
    alt = ziel.read_text(encoding="utf-8") if ziel.exists() else ""
    anzahl = f"{len(theme['variablen'])} Variablen, {len(theme.get('schalter') or [])} Schalter"
    if alt == neu:
        print(f"{theme['datei']} ist aktuell ({anzahl}).")
        return 0
    if pruefen:
        print(f"FEHLER  {theme['datei']} ist nicht aktuell -- python ci/gen_theme.py laufen lassen")
        return 1
    ziel.write_text(neu, encoding="utf-8")
    print(f"Geschrieben: {theme['datei']} ({anzahl})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
