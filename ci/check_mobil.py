#!/usr/bin/env python3
"""Prueft Regeln aus DESIGN.md, Abschnitt "Bildschirmbreiten".

Das Dashboard muss auf zwei Geraeten sauber aussehen: Galaxy S25 (360 px
breit) und iPhone 17 Pro (402 px). Geprueft wird, was sich am Text der Karten
erkennen laesst:

1. Icon in einer Textzeile: Ein button-card-Icon mit eigenen Stilen
   (styles.icon) braucht "--ha-icon-display: block". Ohne steht das Icon in
   einer Textzeile und sitzt 1 bis 1,3 px zu tief (gemessen in der
   Lichter-Karte, PR #269). Erfuellt ist die Regel auch, wenn ein genutztes
   Template sie setzt oder show_icon false ist. Fuer den Bestand von vor der
   Regel gilt BESTAND: je Datei darf die Zahl der Stellen nicht steigen, und
   sinkt sie, wird BESTAND im selben Commit gesenkt.
2. Kein labels.formatter auf der Zeitachse von apexcharts-card: ApexCharts
   erzeugt damit nur noch wenige Teilstriche (Monatsbilanz zeigte "D J D"
   statt zwoelf Monaten, PR #268). Kleinere Beschriftung per card_mod und
   font-size.
3. Jede Container Query mit Pixel-Schwelle hat direkt davor einen Kommentar
   mit den gemessenen Breiten beider Geraete (mindestens zwei px-Werte). Eine
   Schwelle ohne Messung traf in PR #266 auch das iPhone (Chips 154 px breit,
   Schwelle 160 px).

Nicht pruefbar: ob ein gekuerzter Text ("white-space: nowrap" mit "...")
umbrechen sollte, ob eine Schwelle zwischen den Breiten liegt und wie die
Karte aussieht. Dafuer die Pruefschritte in CONTRIBUTING.md.

Archivierte Fassungen (archiv/) werden nicht geprueft.

Aufruf: python ci/check_mobil.py [datei ...]
Ohne Argumente: alle Lovelace-YAMLs (Art "lovelace" aus ci/dateien.py).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from dateien import dateien

REPO_ROOT = Path(__file__).resolve().parent.parent

# Regel 1, Bestand vor der Regel (Stand 25.10.2026): Datei -> Zahl der Icons
# ohne "--ha-icon-display: block". Darf nur sinken.
BESTAND: dict[str, int] = {
    "dashboard/allgemein/navigation-templates.yaml": 10,
    "dashboard/allgemein/top-navigation-karte.yaml": 10,
    "dashboard/garten/garten-karte.yaml": 6,
    "dashboard/garten/pflanzen-templates.yaml": 1,
    "dashboard/garten/pflanzen-view.yaml": 1,
    "dashboard/licht/fenster-lichter-karte.yaml": 1,
    "dashboard/licht/haustuer-lock-karte.yaml": 3,
    "dashboard/licht/lichter-glow-karte.yaml": 15,
    "dashboard/licht/lichter-mushroom-karte.yaml": 1,
    "dashboard/licht/lichter-slider-karte.yaml": 1,
    "dashboard/netzwerk/docker-templates.yaml": 1,
    "dashboard/netzwerk/unifi-leitungen-karte.yaml": 1,
    "dashboard/netzwerk/wlan-karte-v2.yaml": 1,
    "dashboard/sonstiges/muellabfuhr-karte-v2.yaml": 1,
}

HA_TAGS = (
    "!include",
    "!include_dir_list",
    "!include_dir_named",
    "!include_dir_merge_list",
    "!include_dir_merge_named",
    "!secret",
    "!env_var",
    "!input",
)

CONTAINER_RE = re.compile(r"@container\b[^{]*?\((?:max|min)-width:\s*[\d.]+px\)")
KOMMENTAR_RE = re.compile(r"/\*(.*?)\*/", re.S)
PX_WERT_RE = re.compile(r"\d+(?:[.,]\d+)?\s*px")


class Knoten(dict):
    """Mapping mit der Zeile, in der es in der Datei beginnt."""

    zeile = 0


class Loader(yaml.SafeLoader):
    """SafeLoader, der HA-Tags toleriert und Zeilen mitfuehrt."""


def _mapping(loader: Loader, node: yaml.MappingNode) -> Knoten:
    k = Knoten(loader.construct_mapping(node, deep=True))
    k.zeile = node.start_mark.line + 1
    return k


def _tag(loader: Loader, node: yaml.Node) -> None:
    return None


Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)
for _t in HA_TAGS:
    Loader.add_constructor(_t, _tag)


def laden(pfad: Path) -> object:
    try:
        return yaml.load(pfad.read_text(encoding="utf-8"), Loader=Loader)
    except yaml.YAMLError:
        return None  # meldet ci/check_yaml.py


def knoten(o: object):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from knoten(v)
    elif isinstance(o, list):
        for v in o:
            yield from knoten(v)


def rel(pfad: Path) -> str:
    try:
        return pfad.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return pfad.as_posix()


def setzt_display(eintrag: object) -> bool:
    stile = eintrag.get("styles") if isinstance(eintrag, dict) else None
    icon = stile.get("icon") if isinstance(stile, dict) else None
    return isinstance(icon, list) and any(
        isinstance(x, dict) and "--ha-icon-display" in x for x in icon
    )


def template_liste(eintrag: dict) -> list[str]:
    t = eintrag.get("template")
    if isinstance(t, str):
        return [t]
    if isinstance(t, list):
        return [x for x in t if isinstance(x, str)]
    return []


def alle_templates() -> dict[str, dict]:
    """button_card_templates aus allen Dateien, auch aus archiv/ und ungeprueften."""
    vorlagen: dict[str, dict] = {}
    for pfad in dateien("lovelace"):
        daten = laden(pfad)
        if not isinstance(daten, dict):
            continue
        bct = daten.get("button_card_templates")
        if isinstance(bct, dict):
            for name, t in bct.items():
                if isinstance(t, dict):
                    vorlagen.setdefault(str(name), t)
    return vorlagen


def von_template_gesetzt(eintrag: dict, vorlagen: dict[str, dict], tiefe: int = 0) -> bool:
    if tiefe > 10:
        return False
    for name in template_liste(eintrag):
        t = vorlagen.get(name)
        if t is not None and (setzt_display(t) or von_template_gesetzt(t, vorlagen, tiefe + 1)):
            return True
    return False


def icon_stellen(daten: object, vorlagen: dict[str, dict]) -> list[tuple[int, str]]:
    """Regel 1: (zeile, beschreibung) je Icon ohne --ha-icon-display."""
    stellen: list[tuple[int, str]] = []
    template_eintraege: set[int] = set()
    if isinstance(daten, dict) and isinstance(daten.get("button_card_templates"), dict):
        template_eintraege = {id(t) for t in daten["button_card_templates"].values()}
    for k in knoten(daten):
        ist_karte = k.get("type") == "custom:button-card"
        if not (ist_karte or id(k) in template_eintraege):
            continue
        stile = k.get("styles")
        if not isinstance(stile, dict) or "icon" not in stile:
            continue
        if k.get("show_icon") is False or setzt_display(k) or von_template_gesetzt(k, vorlagen):
            continue
        name = k.get("name")
        if isinstance(name, str) and "[[[" not in name:
            wer = f"'{name}'"
        else:
            wer = k.get("icon") or "button-card"
        stellen.append((getattr(k, "zeile", 0), str(wer)))
    return stellen


def formatter_stellen(daten: object) -> list[int]:
    """Regel 2: Zeilen von apexcharts-card mit xaxis.labels.formatter."""
    zeilen = []
    for k in knoten(daten):
        if k.get("type") != "custom:apexcharts-card":
            continue
        apex = k.get("apex_config")
        xaxis = apex.get("xaxis") if isinstance(apex, dict) else None
        labels = xaxis.get("labels") if isinstance(xaxis, dict) else None
        if isinstance(labels, dict) and "formatter" in labels:
            zeilen.append(getattr(labels, "zeile", getattr(k, "zeile", 0)))
    return zeilen


def container_stellen(text: str) -> list[int]:
    """Regel 3: Zeilen von Container Queries ohne Breitenkommentar davor."""
    zeilen = []
    for m in CONTAINER_RE.finditer(text):
        davor = text[: m.start()]
        # Nur der Kommentar unmittelbar davor zaehlt (hoechstens Leerraum dazwischen).
        kommentare = list(KOMMENTAR_RE.finditer(davor))
        ok = False
        if kommentare:
            letzter = kommentare[-1]
            zwischen = davor[letzter.end():]
            if not zwischen.strip() and len(PX_WERT_RE.findall(letzter.group(1))) >= 2:
                ok = True
        if not ok:
            zeilen.append(text.count("\n", 0, m.start()) + 1)
    return zeilen


def main(argv: list[str]) -> int:
    pfade = [Path(a) for a in argv] if argv else dateien("lovelace")
    pfade = [p for p in pfade if "archiv" not in p.parts]
    if not pfade:
        print("Keine YAML-Dateien gefunden.")
        return 1
    vorlagen = alle_templates()
    fehler: list[str] = []
    gezaehlt: dict[str, int] = {}

    for pfad in pfade:
        name = rel(pfad)
        text = pfad.read_text(encoding="utf-8")
        daten = laden(pfad)

        stellen = icon_stellen(daten, vorlagen)
        gezaehlt[name] = len(stellen)
        erlaubt = BESTAND.get(name, 0)
        if len(stellen) > erlaubt:
            for zeile, wer in stellen:
                fehler.append(
                    f"{name}:{zeile}: Icon {wer} ohne '--ha-icon-display: block' in "
                    "styles.icon (sitzt sonst in einer Textzeile zu tief; "
                    f"{len(stellen)} Stelle(n), Bestand {erlaubt})"
                )
        elif len(stellen) < erlaubt:
            fehler.append(
                f"{name}: {len(stellen)} statt {erlaubt} Icons ohne '--ha-icon-display: block' -- "
                f"BESTAND in ci/check_mobil.py auf {len(stellen)} senken"
            )

        for zeile in formatter_stellen(daten):
            fehler.append(
                f"{name}:{zeile}: apexcharts-card mit xaxis.labels.formatter -- auf der "
                "Zeitachse erzeugt ApexCharts damit nur noch wenige Teilstriche; "
                "Groesse per card_mod/font-size"
            )

        for zeile in container_stellen(text):
            fehler.append(
                f"{name}:{zeile}: Container Query ohne Kommentar davor, der die gemessenen Breiten "
                "beider Geraete nennt (z. B. '360 px breites Handy: 133 px, iPhone 17 Pro: 154 px')"
            )

    if not argv:
        for name in sorted(set(BESTAND) - set(gezaehlt)):
            fehler.append(
                f"{name}: steht in BESTAND, gibt es aber nicht (mehr) -- Eintrag entfernen"
            )

    for f in fehler:
        print(f"FEHLER  {f}")
    print(f"\n{len(pfade)} Datei(en) geprueft, {len(fehler)} Problem(e) gefunden.")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
