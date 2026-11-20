#!/usr/bin/env python3
"""Strukturpruefung der Lovelace-YAML-Dateien (Art "lovelace" aus ci/dateien.py).

Geprueft wird, was im Dashboard sonst still fehlschlaegt:

1. Die Datei parst ueberhaupt -- inklusive der Home-Assistant-eigenen Tags
   (!include, !secret, ...), an denen ein normaler YAML-Parser scheitert.
2. Keine doppelten Schluessel in einem Mapping. PyYAML und Home Assistant
   ueberschreiben den ersten Wert kommentarlos, der Fehler ist unsichtbar.
3. Jeder "type: custom:..."-Wert steht in ci/known_cards.txt. Faengt Tippfehler
   im Kartennamen, die Lovelace nur als "Custom element doesn't exist" meldet.
4. Entity-IDs unter "entity:" sehen wie "domain.objekt" aus (klein
   geschrieben, keine Leerzeichen). Werte mit Templates oder
   Decluttering-Variablen ("[[name]]") werden uebersprungen.
5. Aktionen in der aktuellen Schreibweise: "action: perform-action" mit
   "perform_action" und "data" statt "action: call-service" mit "service" und
   "service_data". Die alte Form laeuft weiter (button-card und HA-Frontend
   setzen sie in denselben Zweig um), ist aber nur noch Rueckwaertskompatibilitaet.
   Geprueft wird auch ein per Template berechneter action-Wert.
6. browser_mod-Dienste aus einer Karte als Browser-Aufruf: "action:
   fire-dom-event" mit "browser_mod: {service, data}". Als Dienstaufruf
   (perform-action) ohne browser_id/user_id ist es ein Server-Aufruf, und
   browser_mod fuehrt ihn auf allen registrierten, gerade verbundenen Browsern
   aus (Popup erscheint auf jedem offenen Geraet, nicht nur dem tippenden).
7. Keine button-card-Optionen, die es seit Version 7.0.0 nicht mehr gibt:
   "triggers_update" ist wirkungslos (neu gezeichnet wird, wenn sich eine per
   states[...] gelesene Entitaet aendert; einen Takt liefert ein gelesenes
   states['sensor.time']), "spin" heisst jetzt "rotate".
8. Kein Durchlauf ueber alle Zustaende mit Object.values/Object.entries in
   JS-Templates (states, hass.states): button-card v7 verfolgt jeden
   gelesenen Zustand, die Karte zeichnete dann bei jeder Aenderung im Haus
   neu. Stattdessen Object.keys(...) filtern und gezielt states[id] lesen.

Aufruf: python ci/check_yaml.py [datei ...]
Ohne Argumente werden alle Lovelace-YAMLs geprueft (Art "lovelace" aus
ci/dateien.py, in allen Unterordnern).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from dateien import dateien

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

# Durchlauf ueber alle Zustaende (Regel 8): states, hass.states, x.hass.states.
ALLE_ZUSTAENDE_RE = re.compile(
    r"Object\.(?:values|entries)\(\s*(?:[A-Za-z_$][\w$]*\.)*(?:hass\.)?states\s*\)"
)
# Seit button-card 7.0.0 entfallene Optionen (Regel 7).
BC7_ENTFALLEN = {
    "triggers_update": "wirkungslos seit button-card 7.0.0 -- neu gezeichnet wird, "
    "wenn sich eine per states[...] gelesene Entitaet aendert; fuer einen Takt "
    "states['sensor.time'] lesen",
    "spin": "heisst seit button-card 7.0.0 'rotate'",
}

# Werte, die statt einer festen Entity ein Template liefern -- die kann nur die
# laufende Instanz aufloesen, deshalb werden sie uebersprungen. "[[" deckt
# button-card-JS ("[[[ ... ]]]") und Decluttering-Variablen ("[[name]]") ab.
TEMPLATE_MARKERS = ("[[", "{{", "{%")


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

        action = value.get("action")
        if isinstance(action, str) and "call-service" in action:
            errors.append(
                f"{path.name}: 'action: call-service' (unter '{node_path or 'root'}') -- "
                "neue Schreibweise: action: perform-action, perform_action: <dienst>, data: ..."
            )
        if "service_data" in value and "action" in value:
            errors.append(
                f"{path.name}: 'service_data' in einer Aktion (unter '{node_path or 'root'}') -- "
                "heisst jetzt 'data'"
            )

        dienst = value.get("perform_action") or value.get("service")
        daten = value.get("data") if isinstance(value.get("data"), dict) else {}
        if (
            isinstance(action, str)
            and ("perform-action" in action or "call-service" in action)
            and isinstance(dienst, str)
            and dienst.startswith("browser_mod.")
            and "browser_id" not in daten
            and "user_id" not in daten
        ):
            errors.append(
                f"{path.name}: '{dienst}' als Dienstaufruf ohne browser_id (unter "
                f"'{node_path or 'root'}') -- geht an alle registrierten Browser; "
                "action: fire-dom-event mit browser_mod: {service, data} verwenden"
            )

        for schluessel, grund in BC7_ENTFALLEN.items():
            if schluessel in value:
                errors.append(
                    f"{path.name}: '{schluessel}' (unter '{node_path or 'root'}') -- {grund}"
                )

    for node_path, value in walk(data):
        if isinstance(value, str) and ALLE_ZUSTAENDE_RE.search(value):
            errors.append(
                f"{path.name}: Object.values/entries ueber alle Zustaende "
                f"(unter '{node_path or 'root'}') -- button-card v7 verfolgt dann "
                "jede Entitaet; Object.keys(...) filtern und gezielt states[id] lesen"
            )

    return errors


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(a) for a in argv]
    else:
        # Nur die Kartendateien -- Konfiguration wie .pre-commit-config.yaml
        # ist kein Lovelace-Snippet und wird von yamllint abgedeckt.
        paths = dateien("lovelace")

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
