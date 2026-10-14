---
name: owlet-design
description: Owlet-Stil fuer Lovelace-Karten und Views in diesem Repo einhalten -- Kartenhuelle, Icon-Kachel, gefuellte Kachel, Farbrollen aus design/palette.yaml. Verwenden, bevor eine Karte oder View neu gebaut, umgestaltet oder umgefaerbt wird, wenn eine Farbe gewaehlt werden muss, und wenn ci/check_palette.py eine Farbe ausserhalb der Palette meldet.
---

# Owlet-Stil anwenden

Die Regeln stehen in `DESIGN.md`, die Farbwerte in `design/palette.yaml`.
Beide zuerst lesen; diese Datei wiederholt sie nicht, sondern beschreibt den
Ablauf.

## Ablauf

1. **Rolle bestimmen, dann Farbe waehlen.** Nicht nach Optik aussuchen, sondern
   in `DESIGN.md` die Rolle nachschlagen: Status (gruen/amber/orange/rot),
   Bereichs-Akzent, Flaeche, Text. Kleine Schrift immer `#8794a5`, nie
   `#6e7988`.
2. **Bausteine aus dem Bestand uebernehmen.** Kartenhuelle, Unterkachel und
   Icon-Kachel genau wie in `DESIGN.md`, Abschnitt "Bausteine". Innerhalb einer
   Datei ueber YAML-Anker teilen, wie die vorhandenen Karten es tun.
3. **Deckkraft statt neuer Farbtoene.** Getoente Flaechen und Raender aus der
   Akzentfarbe ableiten (Stufen 0,12 / 0,24 / 0,5), keine neuen dunklen
   Mischtoene erfinden.
4. **Sonderfarben nur fuer ihren Zweck.** Eintraege mit `status: sonder` sind
   an das gebunden, was unter `zweck` steht (Owlet, Personen, Fussball,
   Flugradar, DWD).
5. **Pruefen:** `python ci/check_palette.py <datei>` und die uebrigen Checks
   aus `ci/README.md`.

## Wenn die Pruefung eine Farbe meldet

- Erst den vorgeschlagenen naechsten Palettenwert pruefen. Meist ist die
  gemeldete Farbe eine zufaellige Variante eines Palettentons.
- Nur wenn die Farbe eine eigene Rolle hat, die kein Palettenwert abdeckt: in
  `design/palette.yaml` aufnehmen (hex, name, status, zweck) und die Rolle in
  `DESIGN.md` ergaenzen. Die Aufnahme ist eine Design-Entscheidung -- im
  Zweifel den Nutzer fragen, statt still eine Farbe hinzuzufuegen.
