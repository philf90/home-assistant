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

## Pruefungen

Vor einem Push die Checks aus `ci/README.md` lokal ausfuehren. Neue
`custom:`-Kartentypen in `ci/known_cards.txt` eintragen.
