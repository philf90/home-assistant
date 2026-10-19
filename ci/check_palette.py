#!/usr/bin/env python3
"""Prueft jede Farbangabe in den Karten gegen die Owlet-Palette.

Die Palette steht in design/palette.yaml, die Regeln dazu in DESIGN.md.
Geprueft wird:

1. design/palette.yaml selbst: gueltige Hex-Werte, Pflichtfelder, bekannte
   Status-Werte, keine Farbe doppelt.
2. Jede Farbangabe in den Karten -- #rgb, #rgba, #rrggbb, #rrggbbaa, rgb() und
   rgba() mit festen Zahlen -- steht in der Palette. Deckkraft ist bei jeder
   Palettenfarbe erlaubt. Farben unter "nur_mit_deckkraft" (Weiss) duerfen
   nicht deckend vorkommen, ausser als Schrift auf einer Farbe aus ihrem
   "deckend_auf": Steht eine davon in derselben Zeile, ist der Wert erlaubt.

3. Der helle Modus: "hell_farben" (Format, keine Dublette mit der dunklen
   Palette, jeder Wert von einer Variable genutzt) und "theme" (jede Variable
   mit gueltigem Namen, "dunkel" aus der dunklen Palette, "hell" aus der
   dunklen Palette oder hell_farben). Werte aus hell_farben sind nur in der
   Theme-Datei (theme.datei) erlaubt, Weiss dort auch deckend.

Nicht geprueft werden Farben, die erst zur Laufzeit entstehen
(rgba(${r},${g},${b},...), accent + '29'), benannte CSS-Farben und die
Grafana-Dashboards (eigene Farbnamen, siehe DESIGN.md).

Aufruf: python ci/check_palette.py [datei ...]
Ohne Argumente werden alle Lovelace-YAMLs und eigenen JS-Module geprueft
(Arten "lovelace" und "ressource" aus ci/dateien.py, in allen Unterordnern).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from dateien import dateien as repo_dateien

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


def lade_deckend_auf(farben: dict[str, str]) -> tuple[dict[str, set[str]], list[str]]:
    """Liefert {weiss: {erlaubte Grundfarben}} aus nur_mit_deckkraft[].deckend_auf.

    Getrennt von lade_palette(), damit check_grafana.py die Ausnahme nicht erbt.
    """
    fehler: list[str] = []
    daten = yaml.safe_load(PALETTE_FILE.read_text(encoding="utf-8"))
    erlaubt: dict[str, set[str]] = {}
    for i, e in enumerate(daten.get("nur_mit_deckkraft") or []):
        if not isinstance(e, dict) or "deckend_auf" not in e:
            continue
        ort = f"nur_mit_deckkraft[{i}].deckend_auf"
        werte = e["deckend_auf"]
        if not isinstance(werte, list) or not werte:
            fehler.append(f"{ort}: Liste von #rrggbb-Werten erwartet")
            continue
        for w in werte:
            w = str(w).lower()
            if not HEX_RE.match(w) or w not in farben:
                fehler.append(f"{ort}: '{w}' ist kein Wert der Palette")
            else:
                erlaubt.setdefault(str(e.get("hex", "")).lower(), set()).add(w)
    return erlaubt, fehler


VARIABLE_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
ANTEIL_RE = re.compile(r"^(?:100|[1-9]?[0-9])(?:\.[0-9]+)?%$")


def farbwert(text: str) -> tuple[str, float] | None:
    """Liest einen einzelnen Farbwert ("#rrggbb", "rgba(...)") als (hex, Deckkraft)."""
    treffer = FARBE_HEX.fullmatch(text) or FARBE_RGB.fullmatch(text)
    return zu_hex(treffer) if treffer else None


def lade_hell(
    farben: dict[str, str], nur_deckkraft: set[str]
) -> tuple[dict[str, str], dict, list[str]]:
    """Liefert {hex: name} der hellen Werte, den Abschnitt theme und Fehler.

    Getrennt von lade_palette(), damit check_grafana.py nur die dunkle Palette
    sieht und dessen Schnittstelle gleich bleibt.
    """
    fehler: list[str] = []
    daten = yaml.safe_load(PALETTE_FILE.read_text(encoding="utf-8"))
    hell: dict[str, str] = {}

    for gruppe, liste in (daten.get("hell_farben") or {}).items():
        for i, e in enumerate(liste or []):
            ort = f"hell_farben.{gruppe}[{i}]"
            if not isinstance(e, dict):
                fehler.append(f"{ort}: Eintrag ist kein Mapping")
                continue
            fehlend = [k for k in ("hex", "name", "zweck") if not e.get(k)]
            if fehlend:
                fehler.append(f"{ort}: Pflichtfeld fehlt: {', '.join(fehlend)}")
            hexwert = str(e.get("hex", "")).lower()
            if not HEX_RE.match(hexwert):
                fehler.append(f"{ort}: '{e.get('hex')}' ist kein #rrggbb-Wert")
                continue
            if hexwert in farben:
                fehler.append(
                    f"{ort}: {hexwert} steht schon als '{farben[hexwert]}' in der dunklen "
                    "Palette -- im Theme direkt verwenden, nicht doppelt aufnehmen"
                )
            elif hexwert in hell:
                fehler.append(f"{ort}: {hexwert} steht schon als '{hell[hexwert]}' in hell_farben")
            hell[hexwert] = f"{e.get('name')} (hell_farben.{gruppe})"

    theme = daten.get("theme") or {}
    if not theme.get("name") or not theme.get("datei"):
        fehler.append("theme: Pflichtfeld fehlt: name und datei")
    elif not (REPO_ROOT / theme["datei"]).parent.is_dir():
        fehler.append(f"theme.datei: Ordner von {theme['datei']} gibt es nicht")

    genutzt: set[str] = set()
    namen: set[str] = set()
    ha_namen: set[str] = set()
    for i, v in enumerate(theme.get("variablen") or []):
        ort = f"theme.variablen[{i}]"
        if not isinstance(v, dict):
            fehler.append(f"{ort}: Eintrag ist kein Mapping")
            continue
        fehlend = [k for k in ("name", "dunkel", "hell", "zweck") if not v.get(k)]
        if fehlend:
            fehler.append(f"{ort}: Pflichtfeld fehlt: {', '.join(fehlend)}")
            continue
        name = str(v["name"])
        ort = f"theme.variablen {name}"
        if not name.startswith("owlet-") or not VARIABLE_RE.match(name):
            fehler.append(f"{ort}: Name muss mit 'owlet-' beginnen (a-z, 0-9, Bindestrich)")
        for ha in v.get("ha") or []:
            if not VARIABLE_RE.match(str(ha)):
                fehler.append(f"{ort}: ha-Variable '{ha}' ist kein gueltiger Name")
            if ha in ha_namen:
                fehler.append(f"{ort}: ha-Variable '{ha}' ist schon vergeben")
            ha_namen.add(ha)
        if name in namen:
            fehler.append(f"{ort}: Variable doppelt")
        namen.add(name)

        dunkel = farbwert(str(v["dunkel"]))
        if dunkel is None:
            fehler.append(f"{ort}: dunkel '{v['dunkel']}' ist kein Farbwert")
        elif dunkel[0] not in farben:
            fehler.append(f"{ort}: dunkel {v['dunkel']} steht nicht in der dunklen Palette")
        elif dunkel[0] in nur_deckkraft and dunkel[1] >= 1:
            fehler.append(f"{ort}: dunkel {v['dunkel']} nur mit Deckkraft < 1 erlaubt")

        hellwert = farbwert(str(v["hell"]))
        if hellwert is None:
            fehler.append(f"{ort}: hell '{v['hell']}' ist kein Farbwert")
        elif hellwert[0] not in farben and hellwert[0] not in hell:
            fehler.append(f"{ort}: hell {v['hell']} steht weder in der Palette noch in hell_farben")
        else:
            genutzt.add(hellwert[0])

    for i, s in enumerate(theme.get("schalter") or []):
        ort = f"theme.schalter[{i}]"
        if not isinstance(s, dict):
            fehler.append(f"{ort}: Eintrag ist kein Mapping")
            continue
        fehlend = [k for k in ("name", "dunkel", "hell", "zweck") if not s.get(k)]
        if fehlend:
            fehler.append(f"{ort}: Pflichtfeld fehlt: {', '.join(fehlend)}")
            continue
        name = str(s["name"])
        ort = f"theme.schalter {name}"
        if not name.startswith("owlet-") or not VARIABLE_RE.match(name):
            fehler.append(f"{ort}: Name muss mit 'owlet-' beginnen (a-z, 0-9, Bindestrich)")
        if name in namen:
            fehler.append(f"{ort}: Name schon vergeben")
        namen.add(name)
        for modus in ("dunkel", "hell"):
            if not ANTEIL_RE.match(str(s[modus])):
                fehler.append(f"{ort}: {modus} '{s[modus]}' ist kein Anteil von 0% bis 100%")

    for hexwert, name in sorted(hell.items()):
        if hexwert not in genutzt:
            fehler.append(f"hell_farben: {hexwert} ({name}) nutzt keine Theme-Variable")

    return hell, theme, fehler


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
    pfad: Path,
    farben: dict[str, str],
    vorschlag: set[str],
    nur_deckkraft: set[str],
    hell: dict[str, str] | None = None,
    ist_theme: bool = False,
    deckend_auf: dict[str, set[str]] | None = None,
) -> list[str]:
    fehler: list[str] = []
    hell = hell or {}
    deckend_auf = deckend_auf or {}
    name = pfad.relative_to(REPO_ROOT) if pfad.is_relative_to(REPO_ROOT) else pfad
    if ist_theme:
        # Im Theme stehen beide Modi; Weiss ist dort als erhoehte Flaeche
        # im hellen Modus deckend erlaubt (DESIGN.md, "Heller Modus").
        farben = {**farben, **hell}
        nur_deckkraft = set()
    for nr, zeile in enumerate(pfad.read_text(encoding="utf-8").splitlines(), start=1):
        in_zeile = {zu_hex(t)[0] for m in (FARBE_HEX, FARBE_RGB) for t in m.finditer(zeile)}
        for muster in (FARBE_HEX, FARBE_RGB):
            for treffer in muster.finditer(zeile):
                hexwert, alpha = zu_hex(treffer)
                text = treffer.group(0)
                if hexwert in hell and hexwert not in farben:
                    fehler.append(
                        f"{name}:{nr}: {text} ist ein Wert des hellen Modus ({hell[hexwert]}) "
                        "und nur im Theme erlaubt -- in Karten die Theme-Variable verwenden"
                    )
                elif hexwert not in farben:
                    fehler.append(
                        f"{name}:{nr}: {text} steht nicht in design/palette.yaml "
                        f"(naechster Palettenwert: {naechster(hexwert, vorschlag)})"
                    )
                elif (
                    hexwert in nur_deckkraft
                    and alpha >= 1
                    and not deckend_auf.get(hexwert, set()) & in_zeile
                ):
                    fehler.append(
                        f"{name}:{nr}: {text} -- {farben[hexwert]} nur mit Deckkraft < 1 erlaubt, "
                        f"deckend stattdessen #f2f5f8"
                    )
    return fehler


def main(argv: list[str]) -> int:
    farben, vorschlag, nur_deckkraft, fehler = lade_palette()
    hell, theme, fehler_hell = lade_hell(farben, nur_deckkraft)
    fehler.extend(fehler_hell)
    deckend_auf, fehler_deckend = lade_deckend_auf(farben)
    fehler.extend(fehler_deckend)
    if fehler:
        print("design/palette.yaml ist fehlerhaft:")
        for f in fehler:
            print(f"  {f}")
        return 1

    if argv:
        dateien = [Path(a).resolve() for a in argv if a.endswith((".yaml", ".js"))]
    else:
        dateien = repo_dateien("lovelace", "ressource")
        if not dateien:
            print("Keine Kartendateien gefunden.")
            return 1

    theme_pfad = (REPO_ROOT / theme["datei"]).resolve()
    for pfad in dateien:
        fehler.extend(
            pruefe_datei(
                pfad, farben, vorschlag, nur_deckkraft, hell, pfad == theme_pfad, deckend_auf
            )
        )

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
        f"({len(farben)} Werte, dazu {len(hell)} helle im Theme)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
