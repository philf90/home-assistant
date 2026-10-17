# Hinweise fuer Claude

Lovelace-Karten, Views und Grafana-Dashboards einer Home-Assistant-Instanz.
Das Repo ist oeffentlich (MIT). Ueberblick: `README.md`.

## Persoenliche Angaben

- Namen, Geraetenamen, Adressen, Kennzeichen und Entity-IDs mit
  Personenbezug kommen nie ins Repo, auch nicht in Commit-Nachrichten,
  PR-Texte oder PR-Kommentare. Stattdessen die Platzhalter aus
  `README.md`, Abschnitt "Platzhalter ersetzen", verwenden.
- Soll eine Datei in die eigene Instanz uebernommen werden, gilt der Skill
  `.claude/skills/platzhalter-einsetzen`. Angepasste Fassungen liegen nur in
  `lokal/` (gitignored).

## Design

- Alle Karten folgen dem Owlet-Stil aus `DESIGN.md`. Farben nur aus
  `design/palette.yaml`; `ci/check_palette.py` laesst andere nicht durch.
- Eine neue Farbe zuerst in `design/palette.yaml` aufnehmen und in `DESIGN.md`
  begruenden, erst dann verwenden. Beim Bauen oder Umfaerben von Karten gilt
  der Skill `.claude/skills/owlet-design`.

## Ablage

- Dateien fuer Home Assistant liegen unter `dashboard/<bereich>/`, abgeloeste
  Fassungen in `archiv/`, HTML-Entwuerfe in `entwuerfe/`, Notizen in `doku/`.
- Namen: `<thema>[-<variante>]-<art>[-vN].yaml`, Art `karte`, `view`,
  `templates` oder `konfig`. Regeln und Ablauf: `ci/README.md`, Abschnitt
  "Repo-Struktur". Verschieben und Umbenennen nur mit `git mv`, Verweise im
  selben Commit anpassen.
- Jede Datei beginnt mit dem Kopfblock aus `ci/README.md`, Abschnitt
  "Dateikopf". `Karten`, `Templates` und `Platzhalter` beim Aendern
  mitpflegen; `ci/check_kopf.py` vergleicht sie mit dem Inhalt.

## Pruefungen

Vor einem Push die Checks aus `ci/README.md` lokal ausfuehren. Neue
`custom:`-Kartentypen in `ci/known_cards.txt` eintragen.
