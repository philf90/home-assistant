#!/usr/bin/env python3
"""Lokale Sperre fuer echte persoenliche Angaben vor dem Commit.

Das Repo ist oeffentlich. Echte Namen, Geraetenamen, Adressen, Kennzeichen und
Entity-IDs mit Personenbezug duerfen weder in Dateien noch in
Commit-Nachrichten landen (siehe CLAUDE.md und README, "Platzhalter ersetzen").
Die CI kann das nicht pruefen: Die Liste der echten Werte darf selbst nicht ins
Repo. Deshalb laeuft diese Pruefung nur lokal, als pre-commit-Hook.

Die Sperrliste steht in lokal/sperrliste.txt (lokal/ ist in .gitignore): ein
Begriff pro Zeile, Gross-/Kleinschreibung egal, "#" leitet einen Kommentar ein.
Fehlt die Datei, gibt es nur einen Hinweis.

Geprueft wird:
- ohne Argument: jede hinzugefuegte Zeile der gestagten Aenderungen
  (git diff --cached) und die Namen gestagter Dateien,
- mit --commit-msg <datei>: die Commit-Nachricht (Hook "commit-msg").

Aufruf: python ci/check_persoenlich.py [--commit-msg <datei>]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPERRLISTE = REPO_ROOT / "lokal" / "sperrliste.txt"


def lade_sperrliste() -> list[str]:
    begriffe = []
    for zeile in SPERRLISTE.read_text(encoding="utf-8").splitlines():
        begriff = zeile.split("#", 1)[0].strip()
        if begriff:
            begriffe.append(begriff.lower())
    return begriffe


def gestagte_zeilen() -> list[tuple[str, str]]:
    """(Ort, Text) fuer jede hinzugefuegte Zeile und jeden gestagten Dateinamen."""
    ausgabe = subprocess.run(
        ["git", "diff", "--cached", "-U0", "--no-color"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    zeilen: list[tuple[str, str]] = []
    datei = "?"
    for zeile in ausgabe.splitlines():
        if zeile.startswith("+++ "):
            datei = zeile[6:] if zeile.startswith("+++ b/") else zeile[4:]
            zeilen.append((f"{datei} (Dateiname)", datei))
        elif zeile.startswith("+") and not zeile.startswith("+++"):
            zeilen.append((datei, zeile[1:]))
    return zeilen


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit-msg", metavar="DATEI")
    args = parser.parse_args(argv)

    if not SPERRLISTE.exists():
        print(
            "HINWEIS lokal/sperrliste.txt fehlt -- keine Pruefung auf echte Namen. "
            "Ein Begriff pro Zeile anlegen, siehe ci/README.md."
        )
        return 0
    begriffe = lade_sperrliste()

    if args.commit_msg:
        text = Path(args.commit_msg).read_text(encoding="utf-8")
        zeilen = [("Commit-Nachricht", z) for z in text.splitlines() if not z.startswith("#")]
    else:
        zeilen = gestagte_zeilen()

    treffer = 0
    for ort, text in zeilen:
        klein = text.lower()
        for nr, begriff in enumerate(begriffe, start=1):
            if begriff in klein:
                treffer += 1
                # Den Begriff nicht ausgeben: die Ausgabe landet sonst in Logs.
                print(f"FEHLER  {ort}: enthaelt Eintrag {nr} aus lokal/sperrliste.txt")
    if treffer:
        print(f"\n{treffer} Treffer -- durch den Platzhalter ersetzen "
              "(README, 'Platzhalter ersetzen').")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
