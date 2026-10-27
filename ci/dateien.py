#!/usr/bin/env python3
"""Gemeinsame Dateiliste fuer alle Pruefungen.

Jede Pruefung holt ihre Dateien von hier, statt selbst ein Verzeichnis zu
durchsuchen. Grund: Sucht jedes Skript nur im Wurzelverzeichnis, faellt eine
Datei nach dem Verschieben in einen Unterordner still aus der Pruefung -- die
CI bleibt gruen, obwohl nichts mehr geprueft wird.

Grundlage ist "git ls-files" (versionierte und noch nicht versionierte,
nicht ignorierte Dateien). Damit zaehlen neue Karten schon vor "git add" mit,
"lokal/" bleibt ueber .gitignore draussen.

Jede Datei bekommt genau eine Art:

  lovelace   *.yaml ausser Konfiguration (Punktdateien, ci/, design/)
  ressource  *.js ausser ci/ -- eigene Frontend-Module
  grafana    grafana/**/*.json
  python     *.py
  doku       *.md
  entwurf    *.html
  meta       Repo-Konfiguration (Punktdateien, LICENSE, pyproject.toml,
             ci/, design/, .claude/, .github/)
  bild       *.png, *.jpg, *.jpeg, *.gif, *.webp -- Binaerdateien; keine
             Pruefung liest sie als Text

Eine Datei, die in keine Art passt, ist ein Fehler: Entweder ist sie falsch
abgelegt, oder die Regeln hier muessen erweitert werden.

Aufruf:
  python ci/dateien.py            prueft, dass jede Datei eine Art hat
  python ci/dateien.py <art> ...  gibt die Dateien dieser Arten aus
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent

ARTEN = ("lovelace", "ressource", "grafana", "python", "doku", "entwurf", "meta", "bild")

# Themenbereiche unter dashboard/. Ein neuer Bereich wird hier eingetragen,
# sonst meldet ci/check_struktur.py den Ordner.
BEREICHE = (
    "allgemein",
    "energie",
    "klima",
    "licht",
    "hausgeraete",
    "netzwerk",
    "fahrzeuge",
    "garten",
    "personen",
    "flugradar",
    "fussball",
    "sicherheit",
    "sonstiges",
)

# Ordner, deren Inhalt Repo-Konfiguration ist, keine Karte.
META_ORDNER = (".claude", ".github", "ci", "design")
META_DATEIEN = ("LICENSE", "pyproject.toml")

# Binaere Bilddateien, z. B. die Social Preview in design/.
BILD_ENDUNGEN = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def alle_dateien() -> list[PurePosixPath]:
    """Alle Dateien, die git kennt oder kennen wuerde, relativ zum Repo."""
    try:
        ausgabe = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"git ls-files fehlgeschlagen: {exc}") from exc
    dateien = {PurePosixPath(p) for p in ausgabe.decode("utf-8").split("\0") if p}
    # Im Arbeitsbaum geloeschte, aber noch versionierte Dateien auslassen.
    return sorted(p for p in dateien if (REPO_ROOT / p).is_file())


def art(pfad: PurePosixPath) -> str | None:
    """Ordnet eine Datei genau einer Art zu, None wenn keine Regel passt."""
    teile = pfad.parts
    name = pfad.name
    endung = pfad.suffix

    # Bilder zuerst: Sie sind binaer, auch unter design/ (sonst meta).
    if endung in BILD_ENDUNGEN:
        return "bild"
    # Fachliche Dateien vor Konfiguration: Markdown und Python unter ci/ sind
    # trotzdem Doku bzw. Skripte und werden als solche geprueft.
    if endung == ".py":
        return "python"
    if endung == ".md":
        return "doku"
    if teile[0] in META_ORDNER or name.startswith(".") or name in META_DATEIEN:
        return "meta"
    if endung == ".yaml":
        return "lovelace"
    if endung == ".js":
        return "ressource"
    if endung == ".json" and teile[0] == "grafana":
        return "grafana"
    if endung == ".html":
        return "entwurf"
    return None


def dateien(*arten: str) -> list[Path]:
    """Absolute Pfade aller Dateien der genannten Arten, sortiert."""
    unbekannt = set(arten) - set(ARTEN)
    if unbekannt:
        raise ValueError(f"unbekannte Art: {', '.join(sorted(unbekannt))}")
    return [REPO_ROOT / p for p in alle_dateien() if art(p) in arten]


def ohne_art() -> list[PurePosixPath]:
    return [p for p in alle_dateien() if art(p) is None]


def main(argv: list[str]) -> int:
    if argv:
        try:
            for pfad in dateien(*argv):
                print(pfad.relative_to(REPO_ROOT).as_posix())
        except ValueError as exc:
            print(f"FEHLER  {exc} (erlaubt: {', '.join(ARTEN)})")
            return 2
        return 0

    fehlend = ohne_art()
    for pfad in fehlend:
        print(
            f"FEHLER  {pfad}: keine Art zugeordnet -- falsch abgelegt, oder "
            "Regel in ci/dateien.py ergaenzen"
        )
    gesamt = len(alle_dateien())
    print(f"\n{gesamt} Datei(en), {len(fehlend)} ohne Art.")
    return 1 if fehlend else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
