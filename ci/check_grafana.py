#!/usr/bin/env python3
"""Pruefung der Grafana-Dashboards in grafana/*.json.

Geprueft wird, was den Import in eine fremde Grafana-Instanz brechen wuerde:

1. Die Datei ist gueltiges JSON und hat die Pflichtfelder eines Dashboards.
2. Panel-IDs sind innerhalb eines Dashboards eindeutig. Doppelte IDs fuehren
   dazu, dass Grafana beim Speichern Panels ueberschreibt.
3. Dashboard-UIDs sind ueber alle Dateien hinweg eindeutig -- sonst
   ueberschreibt der Import eines Dashboards ein anderes.
4. Datasources werden ueber eine Template-Variable referenziert ("${DS}"),
   nicht ueber eine feste UID aus der Export-Instanz. Eine hart kodierte UID
   zeigt beim Import auf eine Datasource, die es dort nicht gibt.
5. Jede referenzierte Datasource-Variable ist unter "templating" definiert.
6. Keine "__inputs"/"__requires"-Reste aus dem "Export for sharing"-Dialog --
   die verlangen beim Import eine manuelle Zuordnung.
7. Farben ("color", "fixedColor", "iconColor") stammen aus der Owlet-Palette
   (design/palette.yaml). Grafanas Farbnamen wie "green" oder "dark-red" sehen
   je nach Grafana-Theme anders aus; erlaubt sind nur "text" und "transparent".

Aufruf: python ci/check_grafana.py [datei ...]
Ohne Argumente werden alle grafana/*.json geprueft.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from check_palette import FARBE_HEX, FARBE_RGB, lade_palette, zu_hex

REPO_ROOT = Path(__file__).resolve().parent.parent
GRAFANA_DIR = REPO_ROOT / "grafana"

REQUIRED_KEYS = ("uid", "title", "schemaVersion", "panels")
VARIABLE_RE = re.compile(r"^\$\{?(\w+)\}?$")

FARB_SCHLUESSEL = ("color", "fixedColor", "iconColor")
GRAFANA_FARBEN_ERLAUBT = {"text", "transparent"}

# Panel-Typen ohne Datenabfrage -- die brauchen keine Datasource.
DATASOURCE_EXEMPT_TYPES = {"row", "text", "dashlist", "news", "welcome"}


def iter_panels(panels):
    """Liefert alle Panels inklusive der in Rows verschachtelten."""
    for panel in panels or []:
        yield panel
        yield from iter_panels(panel.get("panels"))


def declared_variables(dashboard: dict) -> set[str]:
    names = set()
    for var in dashboard.get("templating", {}).get("list", []) or []:
        name = var.get("name")
        if name:
            names.add(name)
    return names


def collect_datasource_refs(dashboard: dict):
    """Liefert (quelle, datasource-referenz) fuer Panels und Targets."""
    for panel in iter_panels(dashboard.get("panels")):
        label = f"Panel {panel.get('id')} '{panel.get('title', '')}'".strip()
        if panel.get("datasource") is not None:
            yield label, panel["datasource"]
        for index, target in enumerate(panel.get("targets") or []):
            if target.get("datasource") is not None:
                yield f"{label}, Target {index}", target["datasource"]


def collect_colors(node, where: str = "Dashboard"):
    """Liefert (ort, farbe) fuer jede Farbangabe unter FARB_SCHLUESSEL."""
    if isinstance(node, dict):
        if "type" in node and "title" in node:
            where = f"Panel '{node.get('title') or node.get('type')}'"
        for key, value in node.items():
            if key in FARB_SCHLUESSEL and isinstance(value, str):
                yield where, value
            else:
                yield from collect_colors(value, where)
    elif isinstance(node, list):
        for item in node:
            yield from collect_colors(item, where)


def check_colors(path: Path, dashboard: dict, palette) -> list[str]:
    farben, _vorschlag, nur_deckkraft, _ = palette
    errors = []
    for where, value in collect_colors(dashboard):
        if value in GRAFANA_FARBEN_ERLAUBT:
            continue
        treffer = FARBE_HEX.fullmatch(value) or FARBE_RGB.fullmatch(value)
        if treffer:
            hexwert, alpha = zu_hex(treffer)
            if hexwert in farben and not (hexwert in nur_deckkraft and alpha >= 1):
                continue
        errors.append(
            f"{path.name}: {where} nutzt die Farbe '{value}' -- nur Werte aus "
            "design/palette.yaml (siehe DESIGN.md) oder 'text'/'transparent'"
        )
    return errors


def check_file(path: Path, palette=None) -> tuple[list[str], str | None]:
    errors: list[str] = []

    try:
        dashboard = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}:{exc.lineno}: ungueltiges JSON -- {exc.msg}"], None

    if not isinstance(dashboard, dict):
        return [f"{path.name}: erwartet ein JSON-Objekt auf oberster Ebene"], None

    for key in REQUIRED_KEYS:
        if key not in dashboard:
            errors.append(f"{path.name}: Pflichtfeld '{key}' fehlt")

    for leftover in ("__inputs", "__requires"):
        if leftover in dashboard:
            errors.append(
                f"{path.name}: '{leftover}' aus dem Sharing-Export ist noch "
                "enthalten -- verlangt beim Import manuelle Zuordnung"
            )

    panels = list(iter_panels(dashboard.get("panels")))
    if not panels:
        errors.append(f"{path.name}: Dashboard enthaelt keine Panels")

    ids = [p.get("id") for p in panels if p.get("id") is not None]
    for panel_id, count in Counter(ids).items():
        if count > 1:
            errors.append(
                f"{path.name}: Panel-ID {panel_id} kommt {count}x vor -- "
                "muss innerhalb eines Dashboards eindeutig sein"
            )

    for panel in panels:
        if panel.get("id") is None and panel.get("type") not in DATASOURCE_EXEMPT_TYPES:
            errors.append(
                f"{path.name}: Panel '{panel.get('title', '?')}' hat keine 'id'"
            )

    variables = declared_variables(dashboard)
    for label, ref in collect_datasource_refs(dashboard):
        if isinstance(ref, str):
            uid = ref
        elif isinstance(ref, dict):
            uid = ref.get("uid")
        else:
            continue
        if uid is None:
            continue

        match = VARIABLE_RE.match(str(uid))
        if not match:
            errors.append(
                f"{path.name}: {label} verweist auf die feste Datasource-UID "
                f"'{uid}' -- stattdessen eine Template-Variable wie '${{DS}}' "
                "verwenden, sonst bricht der Import in anderen Instanzen"
            )
        elif match.group(1) not in variables:
            errors.append(
                f"{path.name}: {label} nutzt die Variable '{uid}', die unter "
                "'templating' nicht definiert ist"
            )

    if palette is not None:
        errors.extend(check_colors(path, dashboard, palette))

    return errors, dashboard.get("uid")


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(a) for a in argv]
    else:
        paths = sorted(GRAFANA_DIR.glob("*.json"))

    if not paths:
        print("Keine Grafana-Dashboards gefunden.")
        return 1

    all_errors: list[str] = []
    uids: dict[str, list[str]] = {}

    palette = lade_palette()
    if palette[3]:
        all_errors.extend(f"design/palette.yaml: {f}" for f in palette[3])

    for path in paths:
        errors, uid = check_file(path, palette)
        all_errors.extend(errors)
        if uid:
            uids.setdefault(uid, []).append(path.name)

    for uid, files in sorted(uids.items()):
        if len(files) > 1:
            all_errors.append(
                f"Dashboard-UID '{uid}' wird von mehreren Dateien belegt "
                f"({', '.join(files)}) -- der Import wuerde sie gegenseitig "
                "ueberschreiben"
            )

    for error in all_errors:
        print(f"FEHLER  {error}")

    print(
        f"\n{len(paths)} Dashboard(s) geprueft, "
        f"{len(all_errors)} Problem(e) gefunden."
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
