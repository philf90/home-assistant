#!/usr/bin/env python3
"""Prueft, dass geaenderte Template-Bibliotheken ihre VERSION erhoehen.

Einige button-card-Templates legen eine Bibliothek einmal pro Seite in window
ab (window.__owletWx, window.__fussball, ...) und verwenden sie wieder, solange
die VERSION gleich ist:

    const VERSION = 10, alt = window.__fussball;
    if (alt && alt.version === VERSION) return alt;

Aendert sich der Code, aber nicht die VERSION, behaelt eine offene Seite nach
einem Dashboard-Update die alte Bibliothek. Der Fehler zeigt sich erst nach
einem harten Neuladen und ist im Dashboard kaum zu erkennen.

Geprueft wird jede gegenueber der Basis geaenderte Lovelace-YAML: Jeder
YAML-Wert mit "const VERSION = N", dessen Code sich (ohne die VERSION-Zeile)
geaendert hat, muss N erhoehen. Kommentare und andere Werte zaehlen nicht.

Aufruf: python ci/check_template_version.py [--basis <git-ref>]
Basis ist der Stand, mit dem verglichen wird (Standard: origin/main);
verglichen wird ab dem gemeinsamen Vorgaenger (git merge-base).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath

from check_yaml import HALoader, walk
from dateien import REPO_ROOT, art

VERSION = re.compile(r"const VERSION = (\d+)")


def git(*argumente: str) -> str:
    return subprocess.run(
        ["git", *argumente], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def bibliotheken(text: str) -> dict[str, tuple[int, str]]:
    """{Pfad im YAML: (VERSION, Code ohne VERSION-Zahl)} fuer jede Bibliothek."""
    loader = HALoader(text)
    try:
        daten = loader.get_single_data()
    finally:
        loader.dispose()
    ergebnis = {}
    for pfad, wert in walk(daten):
        if isinstance(wert, str):
            treffer = VERSION.search(wert)
            if treffer:
                ergebnis[pfad] = (int(treffer.group(1)), VERSION.sub("const VERSION = N", wert))
    return ergebnis


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basis", default="origin/main")
    basis = parser.parse_args(argv).basis

    try:
        vorgaenger = git("merge-base", basis, "HEAD").strip()
    except subprocess.CalledProcessError:
        print(f"WARNUNG Basis '{basis}' nicht gefunden -- Pruefung uebersprungen")
        return 0

    fehler: list[str] = []
    geprueft = 0
    # Umbenennungen erkennen, damit verschobene Dateien mit ihrem alten Stand
    # verglichen werden; Arbeitsbaum statt HEAD, damit es auch vor dem Commit greift.
    for zeile in git("diff", "--name-status", "-M", vorgaenger, "--").splitlines():
        teile = zeile.split("\t")
        status, alt, neu = teile[0], teile[1], teile[-1]
        if status.startswith("D") or not neu.endswith(".yaml"):
            continue
        if art(PurePosixPath(neu)) != "lovelace":
            continue
        neu_text = (REPO_ROOT / neu).read_text(encoding="utf-8")
        if "const VERSION" not in neu_text or status.startswith("A"):
            continue
        alt_text = git("show", f"{vorgaenger}:{alt}")
        vorher, nachher = bibliotheken(alt_text), bibliotheken(neu_text)
        for pfad, (version, code) in nachher.items():
            if pfad not in vorher:
                continue
            geprueft += 1
            alte_version, alter_code = vorher[pfad]
            if code != alter_code and version <= alte_version:
                fehler.append(
                    f"{neu}: Bibliothek unter '{pfad}' geaendert, VERSION aber "
                    f"{alte_version} -> {version} -- VERSION erhoehen"
                )

    for f in fehler:
        print(f"FEHLER  {f}")
    print(f"\n{geprueft} Bibliothek(en) gegen {basis} geprueft, {len(fehler)} Problem(e).")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
