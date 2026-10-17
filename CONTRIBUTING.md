# Mitarbeiten

Dieses Repo sammelt Lovelace-Karten, Views und Grafana-Dashboards im
Owlet-Stil. Die Regeln hier gelten für jede neue und jede geänderte Datei. Die
meisten prüft die CI; was sie nicht prüfen kann, steht ausdrücklich dabei.

Einmal einrichten, dann laufen alle Prüfungen vor jedem Commit:

```bash
pip install pre-commit pyyaml yamllint ruff
pre-commit install
```

## Neue Datei

1. **Bereich wählen:** `dashboard/<bereich>/`, die Bereiche stehen in
   `BEREICHE` in [`ci/dateien.py`](ci/dateien.py). Passt keiner, kommt die Datei
   nach `dashboard/sonstiges/`. Ein neuer Bereich lohnt sich ab drei aktiven
   Dateien und wird in `BEREICHE` eingetragen.
2. **Namen bilden:** `<thema>[-<variante>]-<art>[-vN].yaml` mit der Art
   `karte`, `view`, `templates` oder `konfig`. Nur Kleinbuchstaben, Ziffern und
   Bindestriche, Umlaute als ae/oe/ue. Die Kartenbibliothek gehört nicht in den
   Namen. HTML-Entwürfe liegen in `entwuerfe/`, Notizen in `doku/`.
3. **Kopfblock schreiben**, wie in [`ci/README.md`](ci/README.md), Abschnitt
   „Dateikopf“: Art, Bereich, Status, Karten, Templates, Einfuegen,
   Platzhalter. Darunter frei erklären, mit einer Zeile `Voraussetzung` für
   Integrationen, Helfer und Sensoren.
4. **Neue `custom:`-Karte** in [`ci/known_cards.txt`](ci/known_cards.txt)
   eintragen.
5. **Farben** nur aus [`design/palette.yaml`](design/palette.yaml), Rollen in
   [`DESIGN.md`](DESIGN.md). Eine neue Farbe zuerst dort aufnehmen und
   begründen.
6. **Persönliche Angaben** nur als Platzhalter aus
   [`design/platzhalter.yaml`](design/platzhalter.yaml). Ein neuer Platzhalter
   wird zuerst dort eingetragen.
7. **Übersichten erzeugen:** `python ci/gen_index.py`. Das aktualisiert die
   Tabellen im README und [`dashboard/README.md`](dashboard/README.md).

## Datei ändern

- Den Kopfblock mitpflegen: `Karten`, `Templates`, `Platzhalter`.
- Ein Template mit `const VERSION = N` (Bibliothek in `window`): Ändert sich
  der Code, steigt `N` um 1. Sonst behält eine offene Seite die alte Fassung.
- Umbenennen oder verschieben nur mit `git mv`, alle Verweise im selben
  Commit anpassen. `ci/check_verweise.py` meldet vergessene.
- Fassungen in `archiv/` bekommen nur noch Änderungen, die alle Dateien
  betreffen (Palette, Anonymisierung, CI-Fehler), keine neuen Funktionen.

## Neue Version einer Karte

1. Kopie als `-v<N+1>` im Bereichsordner. Der Text unter dem Kopfblock nennt
   den Unterschied zur Vorgängerin.
2. Die Vorgängerin mit `git mv` nach `archiv/` verschieben und ihren Status
   auf `archiv: ersetzt durch <neue datei>` setzen.
3. Views, die die alte Datei per `!include` einbinden, umstellen.

Eine **Variante** ist eine gleichwertige Alternative (`lichter-raum-karte`,
`lichter-glow-karte`) und bleibt neben den anderen im Bereichsordner. Eine
**Version** löst ihre Vorgängerin ab; je Ordner gibt es höchstens eine aktive
Version.

## Commit-Nachrichten

`<bereich>: <was sich ändert>`, z. B. `fussball: Popup zeigt Kurznamen`. Für
Änderungen über Bereiche hinweg: `ci`, `design`, `doku`, `grafana` oder `repo`.
Das ist eine Empfehlung; keine Prüfung setzt sie durch.

Keine echten Namen, Gerätenamen, Adressen, Kennzeichen oder Entity-IDs mit
Personenbezug, auch nicht in Commit-Nachrichten, PR-Texten und Kommentaren.

## Was die Prüfungen nicht abdecken

- Ob eine Farbe die richtige **Rolle** hat (Grün heißt „in Ordnung“).
- Ob eine Datei im **passenden Bereich** liegt.
- **Echte Namen:** Die CI kennt sie nicht. Lokal prüft
  `ci/check_persoenlich.py` gegen eine eigene Sperrliste in
  `lokal/sperrliste.txt` (ein Begriff pro Zeile, nicht im Repo).
- Ob die Entitäten in einer Instanz existieren.

Alle Prüfungen mit Erklärung: [`ci/README.md`](ci/README.md).
