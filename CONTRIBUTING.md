# Mitarbeiten

Dieses Repo sammelt Lovelace-Karten, Views und Grafana-Dashboards im
Nachtblau-Stil. Die Regeln hier gelten für jede neue und jede geänderte Datei. Die
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

## Routen und Sichtbarkeit

Jedes Sprungziel der Navigation und jeder View hat genau eine Klasse in
[`design/routen.yaml`](design/routen.yaml). Als Sprungziel zählen
`navigation_path` (auch über `variables.pfad`), die `url` einer Route der
navbar-card und ein `url_path`, der mit `/` beginnt; dazu Dienstaufrufe, für
die Home Assistant Adminrechte verlangt (Abschnitt `dienste`, z. B.
`homeassistant.restart`).

| Klasse | Wofür | Navigation (Kachel, Route) | View |
|---|---|---|---|
| `admin` | Wartung, oder Home Assistant verlangt für das Ziel selbst Adminrechte | `hidden: '[[[ return !user.is_admin; ]]]'` | `visible` mit den `admin_konten` |
| `person` | persönliche Inhalte einzelner Konten | `conditional` oder `visibility` mit `condition: user` und genau den `konten` | `visible` mit denselben `konten` |
| `alle` | jedes angemeldete Konto | keine Bedingung nach Benutzer oder Rolle | kein `visible` |

- **Neue Route:** zuerst in `design/routen.yaml` eintragen (Klasse, Grund, bei
  `person` die Konten), dann verwenden. `ci/check_routen.py` meldet
  Sprungziele und Views ohne Klasse und solche, deren Bedingung nicht zur
  Klasse passt.
- **Warum zwei Mechanismen:** Home Assistant kennt für Views und Karten nur
  Bedingungen nach Benutzer-ID (`visible`, `condition: user`), keine nach
  Rolle. Die Rolle steht nur in JS-Templates zur Verfügung (`user.is_admin`
  in button-card und navbar-card). Deshalb steht bei `admin` an Views die
  Liste der Admin-Konten; kommt ein Admin-Konto dazu, wird es in
  `admin_konten` und an den Views ergänzt.
- **Ausblenden ist keine Sicherheit:** `visible` blendet nur den Tab aus, über
  die URL öffnet sich der View trotzdem. Normale Benutzer dürfen in Home
  Assistant alle Entitäten lesen und schalten. Echte Grenzen setzt nur Home
  Assistant selbst (Admin-Dienste, Einstellungen, Speichern von Dashboards).
  Die Klassen sorgen dafür, dass niemand Ziele angeboten bekommt, die nicht
  für ihn gedacht sind oder für ihn nicht funktionieren.
- **Gruppen im Menü:** Ein Raster (`type: grid`) hat kein `hidden`. Eine Gruppe
  der Klasse `admin` blendet deshalb Überschrift und jede Kachel einzeln aus;
  das leere Raster bleibt stehen (Abstand siehe `navbar-karte.yaml`).
- **Instanz prüfen:** Einen Abzug eines Dashboards (JSON) lokal mit
  `python ci/check_routen.py --json <abzug> --dashboard <url_path> --konto
  benutzer_id_1=<id>` prüfen. Abzug und echte IDs nie committen.

## Labels, Bereiche und Kategorien

Gilt für die Instanz, nicht für Dateien im Repo; Karten und Templates, die ein
Label lesen, verlassen sich darauf. Der Labelsatz steht in
[`design/labels.yaml`](design/labels.yaml). Home Assistant hat drei
Ordnungswerkzeuge, jedes beantwortet genau eine Frage:

| Frage | Werkzeug | Gilt für |
|---|---|---|
| Wo? | Bereich, Stockwerk | Geräte, Entitäten; Automationen und Szenen, wenn sie genau einen Bereich betreffen |
| Worum? | Label | Geräte, Entitäten (auch Helfer, Automationen, Skripte, Szenen), Bereiche |
| Welche Art? | Kategorie | nur die Listen von Automationen, Skripten, Szenen und Helfern |

1. **Ort nie als Label.** Kein „Garten“, „Keller“. Außenbereiche ohne
   Stockwerk werden ein Stockwerk, dann reicht `floor_id` als Ziel.
2. **Thema als Label:** fasst zusammen, was über Bereiche oder Integrationen
   verteilt ist, über alle Objektarten. Der Name ist das Präfix der
   Automationsnamen (`Bewässerung: Zonen-Timer` → Bewässerung).
3. **Gerätetyp nur, wenn Home Assistant ihn nicht kennt.** Trennen Domain und
   Geräteklasse die Menge (Rauchmelder: `device_class: smoke`), kein Label.
   Trennen sie sie nicht (Fenster: Autos melden auch `window`), Label.
4. **Kein Label für Hersteller oder Integration.** Das filtert Home Assistant
   selbst.
5. **Steuer-Flag nur mit Verbraucher.** Die Beschreibung nennt das Template,
   die Automation oder Karte, die es liest (Vorbild: `keine_batteriemeldung`).
6. **Eine Ebene.** Physisches Gerät: Label am Gerät. Entitätslabel nur für
   Entitäten ohne Gerät (Helfer, Automation, Skript, Szene, Gruppe) oder wenn
   nur einzelne Entitäten eines Geräts gemeint sind. Ein Ziel `label_id`
   erfasst die Entitäten gelabelter Geräte, `label_entities()` nicht;
   Templates lesen deshalb beide Wege:
   `label_devices(x) | map('device_entities') | sum(start=[]) + label_entities(x)`.
   Ein bestehendes Entitätslabel erst entfernen, wenn kein Template es mit
   `label_entities()` liest; auch Template-Sensoren in der Instanz-YAML
   prüfen, die nicht im Repo liegen.
7. **Vollständig oder gar nicht.** Ein Label erfasst alle passenden Objekte,
   sonst übergeht ein Ziel still Geräte. Ein neues Label lohnt sich ab drei
   Objekten.
8. **Art als Kategorie.** Automationen: Meldung, Steuerung, Merker, Wartung.
   Helfer: Meldeschalter, Einstellung, Merker.
9. **Form:** deutscher Name, Einzahl, Beschreibung Pflicht, Farbe nach Achse
   (Thema bunt, Gerätetyp `blue-grey`, Flag `grey`). Die `label_id` bleibt
   bei einer Umbenennung gleich; bekommt ein Label eine neue Bedeutung, ein
   neues anlegen, umhängen und das alte löschen.
10. **Register zuerst:** ein neues Label zuerst in `design/labels.yaml`
    eintragen, dann in der Instanz anlegen. Das gilt auch für Änderungen
    direkt in der Instanz.

## Auf beiden Handys prüfen

Für jede neue oder geänderte Karte und View, nach den Regeln in
[`DESIGN.md`](DESIGN.md), Abschnitt „Bildschirmbreiten“:

1. **Bei 402 × 874 und 360 × 697 ansehen** (iPhone 17 Pro und Galaxy S25,
   CSS-Pixel), im Browser per Geräteansicht oder in der App auf beiden Geräten.
2. **Nichts abgeschnitten:** Texte mit „…“ nur bei Werten. Zustandsabhängige
   Texte (Wetter, Warnungen, Zeitangaben wie „seit Mo 16:35 · 5 Tage“) in der
   längsten Form prüfen.
3. **Vorher und nachher vergleichen,** nicht nur auf Kürzungen achten: Eine
   Diagrammachse mit drei statt zwölf Beschriftungen kürzt nichts und ist
   trotzdem falsch.
4. **Das iPhone ändert sich nur, wo es beabsichtigt ist.** Eine Schwelle, die
   versehentlich auch 402 px trifft, fällt nur im Vergleich auf.
5. **Popups und Menüs** passen bei 697 px Höhe ohne Scrollen.

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
- Labels in der Instanz: `design/labels.yaml` liest bisher keine Prüfung.
- Ob die **Klasse einer Route** die richtige ist (`design/routen.yaml`);
  geprüft wird nur, dass die Bedingungen zur eingetragenen Klasse passen.
- Wie eine Karte bei 360 und 402 px **aussieht**. `ci/check_mobil.py` prüft
  nur einzelne Regeln aus „Bildschirmbreiten“; der Rest ist der Blick auf
  beide Breiten (siehe oben).

Alle Prüfungen mit Erklärung: [`ci/README.md`](ci/README.md).
