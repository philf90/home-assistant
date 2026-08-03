#!/usr/bin/env python3
"""Strukturpruefung der Lovelace-YAML-Dateien im Repo-Wurzelverzeichnis.

Geprueft wird, was im Dashboard sonst still fehlschlaegt:

1. Die Datei parst ueberhaupt -- inklusive der Home-Assistant-eigenen Tags
   (!include, !secret, ...), an denen ein normaler YAML-Parser scheitert.
2. Keine doppelten Schluessel in einem Mapping. PyYAML und Home Assistant
   ueberschreiben den ersten Wert kommentarlos, der Fehler ist unsichtbar.
3. Jeder "type: custom:..."-Wert steht in ci/known_cards.txt. Faengt Tippfehler
   im Kartennamen, die Lovelace nur als "Custom element doesn't exist" meldet.
4. Entity-IDs unter "entity:" und "triggers_update:" sehen wie "domain.objekt"
   aus (klein geschrieben, keine Leerzeichen).

Aufruf: python ci/check_yaml.py [datei ...]
Ohne Argumente werden alle *.yaml im Repo-Wurzelverzeichnis geprueft.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWN_CARDS_FILE = Path(__file__).resolve().parent / "known_cards.txt"

# Tags, die Home Assistant selbst aufloest. Fuer die reine Strukturpruefung
# reicht ein Platzhalter -- der Inhalt der referenzierten Datei wird hier nicht
# eingesetzt (das macht HA zur Laufzeit).
HA_TAGS = (
    "!include",
    "!include_dir_list",
    "!include_dir_merge_list",
    "!include_dir_merge_named",
    "!include_dir_named",
    "!secret",
    "!env_var",
    "!input",
)

ENTITY_RE = re.compile(r"^[a-z_]+\.[a-z0-9_]+$")

# Werte, die statt einer festen Entity ein Template liefern -- die kann nur die
# laufende Instanz aufloesen, deshalb werden sie uebersprungen.
TEMPLATE_MARKERS = ("[[[", "{{", "{%")


class Placeholder:
    """Steht fuer einen nicht aufgeloesten Home-Assistant-Tag."""

    def __init__(self, tag: str, value: object) -> None:
        self.tag = tag
        self.value = value


class HALoader(yaml.SafeLoader):
    """SafeLoader, der HA-Tags toleriert und doppelte Schluessel meldet."""

    def __init__(self, stream) -> None:
        super().__init__(stream)
        self.duplicate_keys: list[tuple[int, object]] = []


def _construct_placeholder(loader: HALoader, node: yaml.Node) -> Placeholder:
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_mapping(node)
    return Placeholder(node.tag, value)


def _construct_mapping(loader: HALoader, node: yaml.MappingNode) -> dict:
    seen: set = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, (str, int, float, bool, type(None))):
            continue
        if key in seen:
            loader.duplicate_keys.append((key_node.start_mark.line + 1, key))
        seen.add(key)
    return loader.construct_mapping(node, deep=False)


for _tag in HA_TAGS:
    HALoader.add_constructor(_tag, _construct_placeholder)
HALoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_known_cards() -> set[str]:
    cards = set()
    for raw in KNOWN_CARDS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            cards.add(line)
    return cards


def walk(node, path: str = ""):
    """Liefert (pfad, wert) fuer jeden Knoten der geladenen Struktur."""
    yield path, node
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}" if path else str(key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")
    elif isinstance(node, Placeholder):
        yield from walk(node.value, f"{path}{node.tag}")


def check_file(path: Path, known_cards: set[str]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    loader = HALoader(text)
    try:
        data = loader.get_single_data()
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f":{mark.line + 1}" if mark else ""
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        return [f"{path.name}{where}: YAML laesst sich nicht parsen -- {problem}"]
    finally:
        duplicates = loader.duplicate_keys
        loader.dispose()

    for line, key in duplicates:
        errors.append(
            f"{path.name}:{line}: doppelter Schluessel '{key}' -- "
            "der erste Wert wird still ueberschrieben"
        )

    if data is None:
        errors.append(f"{path.name}: Datei ist leer")
        return errors

    for node_path, value in walk(data):
        if not isinstance(value, dict):
            continue

        card_type = value.get("type")
        if isinstance(card_type, str) and card_type.startswith("custom:"):
            name = card_type[len("custom:") :]
            if name not in known_cards:
                errors.append(
                    f"{path.name}: unbekannte Karte '{card_type}' "
                    f"(unter '{node_path or 'root'}') -- Tippfehler, oder "
                    "in ci/known_cards.txt ergaenzen"
                )

        entity = value.get("entity")
        if isinstance(entity, str) and not any(m in entity for m in TEMPLATE_MARKERS):
            if not ENTITY_RE.match(entity.strip()):
                errors.append(
                    f"{path.name}: 'entity: {entity}' sieht nicht wie eine "
                    "Entity-ID aus (erwartet 'domain.objekt', klein geschrieben)"
                )

        triggers = value.get("triggers_update")
        if isinstance(triggers, str):
            triggers = [triggers]
        if isinstance(triggers, list):
            for trigger in triggers:
                if not isinstance(trigger, str) or trigger == "all":
                    continue
                if any(m in trigger for m in TEMPLATE_MARKERS):
                    continue
                if not ENTITY_RE.match(trigger.strip()):
                    errors.append(
                        f"{path.name}: 'triggers_update' enthaelt "
                        f"'{trigger}' -- keine gueltige Entity-ID"
                    )

    return errors


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(a) for a in argv]
    else:
        # Nur die Kartendateien -- Konfiguration wie .pre-commit-config.yaml
        # ist kein Lovelace-Snippet und wird von yamllint abgedeckt.
        paths = sorted(
            p for p in REPO_ROOT.glob("*.yaml") if not p.name.startswith(".")
        )

    if not paths:
        print("Keine YAML-Dateien gefunden.")
        return 1

    known_cards = load_known_cards()
    all_errors: list[str] = []
    for path in paths:
        all_errors.extend(check_file(path, known_cards))

    for error in all_errors:
        print(f"FEHLER  {error}")

    print(
        f"\n{len(paths)} Datei(en) geprueft, "
        f"{len(all_errors)} Problem(e) gefunden."
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
