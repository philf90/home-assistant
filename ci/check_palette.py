#!/usr/bin/env python3
"""Prueft jede Farbangabe in den Karten gegen die Owlet-Palette.

Die Palette steht in design/palette.yaml, die Regeln dazu in DESIGN.md.
Geprueft wird:

1. design/palette.yaml selbst: gueltige Hex-Werte, Pflichtfelder, bekannte
   Status-Werte, keine Farbe doppelt.
2. Jede Farbangabe in den Karten -- #rgb, #rgba, #rrggbb, #rrggbbaa, rgb() und
   rgba() mit festen Zahlen -- steht in der Palette. Deckkraft ist bei jeder
   Palettenfarbe erlaubt. Farben unter "nur_mit_deckkraft" (Weiss) duerfen
   nicht deckend vorkommen.

Nicht geprueft werden Farben, die erst zur Laufzeit entstehen
(rgba(${r},${g},${b},...), accent + '29'), benannte CSS-Farben und die
Grafana-Dashboards (eigene Farbnamen, siehe DESIGN.md).

Aufruf: python ci/check_palette.py [datei ...]
Ohne Argumente werden alle *.yaml und *.js im Repo-Wurzelverzeichnis geprueft.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PALETTE_FILE = REPO_ROOT / "design" / "palette.yaml"

STATUS_WERTE = {"bestand", "neu", "sonder"}
HEX_RE = re.compile(r"^#[0-9a-f]{6}$")

# "&#123;" (HTML-Entity) und "abc#def" (URL-Fragment) sind keine Farben.
FARBE_HEX = re.compile(
    r"(?<![&\w])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\w-])"
)
# Nur feste Zahlen -- Template-Platzhalter wie ${r} werden uebersprungen.
FARBE_RGB = re.compile(
    r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([0-9]*\.?[0-9]+%?)\s*)?\)"
)


def lade_palette() -> tuple[dict[str, str], set[str], set[str], list[str]]:
    """Liefert {hex: name}, die Vorschlagsfarben, die Nur-mit-Deckkraft-Farben und Fehler."""
    fehler: list[str] = []
    daten = yaml.safe_load(PALETTE_FILE.read_text(encoding="utf-8"))
    farben: dict[str, str] = {}
    # Fuer "naechster Palettenwert" -- zweckgebundene Sonderfarben nie vorschlagen.
    vorschlag: set[str] = set()

    def eintrag(e: object, ort: str, mit_status: bool) -> str | None:
        if not isinstance(e, dict):
            fehler.append(f"{ort}: Eintrag ist kein Mapping")
            return None
        pflicht = ("hex", "name", "zweck") + (("status",) if mit_status else ())
        fehlend = [k for k in pflicht if not e.get(k)]
        if fehlend:
            fehler.append(f"{ort}: Pflichtfeld fehlt: {', '.join(fehlend)}")
        hexwert = str(e.get("hex", "")).lower()
        if not HEX_RE.match(hexwert):
            fehler.append(f"{ort}: '{e.get('hex')}' ist kein #rrggbb-Wert")
            return None
        if mit_status and e.get("status") not in STATUS_WERTE:
            erlaubt = ", ".join(sorted(STATUS_WERTE))
            fehler.append(f"{ort}: status '{e.get('status')}' unbekannt ({erlaubt})")
        if hexwert in farben:
            fehler.append(f"{ort}: {hexwert} steht schon als '{farben[hexwert]}' in der Palette")
        return hexwert

    for gruppe, liste in (daten.get("farben") or {}).items():
        for i, e in enumerate(liste or []):
            hexwert = eintrag(e, f"farben.{gruppe}[{i}]", mit_status=True)
            if hexwert:
                farben[hexwert] = f"{e.get('name')} ({gruppe})"
                if e.get("status") != "sonder":
                    vorschlag.add(hexwert)

    nur_deckkraft: set[str] = set()
    for i, e in enumerate(daten.get("nur_mit_deckkraft") or []):
        hexwert = eintrag(e, f"nur_mit_deckkraft[{i}]", mit_status=False)
        if hexwert:
            nur_deckkraft.add(hexwert)
            farben[hexwert] = str(e.get("name"))

    return farben, vorschlag, nur_deckkraft, fehler


def zu_hex(treffer: re.Match[str]) -> tuple[str, float]:
    """Wandelt einen Treffer in (#rrggbb, Deckkraft 0..1)."""
    if treffer.re is FARBE_HEX:
        roh = treffer.group(1).lower()
        if len(roh) in (3, 4):
            roh = "".join(c * 2 for c in roh)
        alpha = int(roh[6:8], 16) / 255 if len(roh) == 8 else 1.0
        return "#" + roh[:6], alpha
    r, g, b = (min(int(treffer.group(i)), 255) for i in (1, 2, 3))
    roh_alpha = treffer.group(4)
    if roh_alpha is None:
        alpha = 1.0
    elif roh_alpha.endswith("%"):
        alpha = float(roh_alpha[:-1]) / 100
    else:
        alpha = float(roh_alpha)
    return f"#{r:02x}{g:02x}{b:02x}", alpha


def lab(hexwert: str) -> tuple[float, float, float]:
    """sRGB -> CIELAB (D65), fuer den Vorschlag des naechsten Palettenwerts."""

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(int(hexwert[i:i + 2], 16) / 255) for i in (1, 3, 5))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def naechster(hexwert: str, kandidaten: set[str]) -> str:
    ziel = lab(hexwert)

    def abstand(p: str) -> float:
        return sum((a - b) ** 2 for a, b in zip(lab(p), ziel, strict=True))

    return min(sorted(kandidaten), key=abstand)


def pruefe_datei(
    pfad: Path, farben: dict[str, str], vorschlag: set[str], nur_deckkraft: set[str]
) -> list[str]:
    fehler: list[str] = []
    name = pfad.relative_to(REPO_ROOT) if pfad.is_relative_to(REPO_ROOT) else pfad
    for nr, zeile in enumerate(pfad.read_text(encoding="utf-8").splitlines(), start=1):
        for muster in (FARBE_HEX, FARBE_RGB):
            for treffer in muster.finditer(zeile):
                hexwert, alpha = zu_hex(treffer)
                text = treffer.group(0)
                if hexwert not in farben:
                    fehler.append(
                        f"{name}:{nr}: {text} steht nicht in design/palette.yaml "
                        f"(naechster Palettenwert: {naechster(hexwert, vorschlag)})"
                    )
                elif hexwert in nur_deckkraft and alpha >= 1:
                    fehler.append(
                        f"{name}:{nr}: {text} -- {farben[hexwert]} nur mit Deckkraft < 1 erlaubt, "
                        f"deckend stattdessen #f2f5f8"
                    )
    return fehler


def main(argv: list[str]) -> int:
    farben, vorschlag, nur_deckkraft, fehler = lade_palette()
    if fehler:
        print("design/palette.yaml ist fehlerhaft:")
        for f in fehler:
            print(f"  {f}")
        return 1

    if argv:
        dateien = [Path(a).resolve() for a in argv if a.endswith((".yaml", ".js"))]
    else:
        dateien = sorted(REPO_ROOT.glob("*.yaml")) + sorted(REPO_ROOT.glob("*.js"))

    for pfad in dateien:
        fehler.extend(pruefe_datei(pfad, farben, vorschlag, nur_deckkraft))

    if fehler:
        for f in fehler:
            print(f)
        print(
            f"\n{len(fehler)} Farbangabe(n) ausserhalb der Owlet-Palette. Palettenwert verwenden "
            "oder die Farbe begruendet in design/palette.yaml aufnehmen (siehe DESIGN.md)."
        )
        return 1

    print(
        f"{len(dateien)} Datei(en) geprueft, alle Farben aus der Owlet-Palette "
        f"({len(farben)} Werte)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
