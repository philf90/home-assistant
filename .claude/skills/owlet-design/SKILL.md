---
name: owlet-design
description: Owlet-Stil fuer Lovelace-Karten und Views in diesem Repo einhalten -- Kartenhuelle, Icon-Kachel, gefuellte Kachel, Farbrollen aus design/palette.yaml, Bildschirmbreiten (Galaxy S25 360 px, iPhone 17 Pro 402 px). Verwenden, bevor eine Karte oder View neu gebaut, umgestaltet oder umgefaerbt wird, wenn eine Farbe gewaehlt werden muss, und wenn ci/check_palette.py eine Farbe ausserhalb der Palette meldet.
---

# Owlet-Stil anwenden

Die Regeln stehen in `DESIGN.md`, die Farbwerte in `design/palette.yaml`.
Beide zuerst lesen; diese Datei wiederholt sie nicht, sondern beschreibt den
Ablauf.

## Ablauf

1. **Rolle bestimmen, dann Farbe waehlen.** Nicht nach Optik aussuchen, sondern
   in `DESIGN.md` die Rolle nachschlagen: Status (gruen/amber/orange/rot),
   Bereichs-Akzent, Flaeche, Text. Text immer mindestens `#8794a5`, nie
   `#6e7988` -- auch nicht fuer "aus" oder "keine Daten".
2. **Bausteine aus dem Bestand uebernehmen.** Kartenhuelle, Unterkachel und
   Icon-Kachel genau wie in `DESIGN.md`, Abschnitt "Bausteine". Innerhalb einer
   Datei ueber YAML-Anker teilen, wie die vorhandenen Karten es tun.
3. **Deckkraft statt neuer Farbtoene.** Getoente Flaechen und Raender aus der
   Akzentfarbe ableiten, nur mit den Stufen aus `DESIGN.md` (Flaeche 0,12,
   Icon-Kachel 0,16, Schein 0,18, Rand 0,24, Leuchten 0,5), keine neuen
   dunklen Mischtoene erfinden.
   **Heller Modus:** Helle Hex-Werte gehoeren nie in eine Karte. Karten, die
   beide Modi koennen sollen, nutzen die Theme-Variablen (`var(--owlet-gruen)`,
   Toenung per `color-mix`), siehe `DESIGN.md`, Abschnitt "Heller Modus".
   Eine neue Farbe braucht dort auch ihren hellen Wert und eine Variable.
4. **Sonderfarben nur fuer ihren Zweck.** Eintraege mit `status: sonder` sind
   an das gebunden, was unter `zweck` steht (Owlet, Personen, Fussball,
   Flugradar, DWD).
5. **Fuer 360 px bauen.** `DESIGN.md`, Abschnitt "Bildschirmbreiten": Inhalt
   der Kartenhuelle 306 px (iPhone 348 px), Texte zweizeilig statt
   abgeschnitten, Anpassungen per Container Query mit gemessener Schwelle und
   Breitenkommentar, `--ha-icon-display: block` an jedem Icon, Popups bis
   629 px Hoehe.
6. **Pruefen:** `python ci/check_palette.py <datei>`,
   `python ci/check_mobil.py <datei>` (Grafana: `python ci/check_grafana.py`)
   und die uebrigen Checks aus `ci/README.md`. Dann die Karte bei 402 x 874 und
   360 x 697 ansehen, wie in `CONTRIBUTING.md`, Abschnitt "Auf beiden Handys
   pruefen".

## Wenn die Pruefung eine Farbe meldet

- Erst den vorgeschlagenen naechsten Palettenwert pruefen. Meist ist die
  gemeldete Farbe eine zufaellige Variante eines Palettentons.
- Nur wenn die Farbe eine eigene Rolle hat, die kein Palettenwert abdeckt: in
  `design/palette.yaml` aufnehmen (hex, name, status, zweck) und die Rolle in
  `DESIGN.md` ergaenzen. Die Aufnahme ist eine Design-Entscheidung -- im
  Zweifel den Nutzer fragen, statt still eine Farbe hinzuzufuegen.
