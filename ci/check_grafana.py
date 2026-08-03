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

Aufruf: python ci/check_grafana.py [datei ...]
Ohne Argumente werden alle grafana/*.json geprueft.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GRAFANA_DIR = REPO_ROOT / "grafana"

REQUIRED_KEYS = ("uid", "title", "schemaVersion", "panels")
VARIABLE_RE = re.compile(r"^\$\{?(\w+)\}?$")

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


def check_file(path: Path) -> tuple[list[str], str | None]:
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

    for path in paths:
        errors, uid = check_file(path)
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
