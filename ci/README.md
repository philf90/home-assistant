# CI-Pruefungen

Die Dateien in diesem Repo sind Konfiguration ohne Laufzeit-Rueckmeldung: Ein
Fehler faellt erst auf, wenn die Karte im Dashboard landet -- bei
`custom:button-card` oft nicht einmal als Fehlermeldung, sondern als leere
Kachel. Die Pruefungen hier fangen genau diese stillen Fehler ab.

Ausgefuehrt werden sie von `.github/workflows/validate.yml` bei jedem Push und
Pull Request. Alle Skripte laufen aber genauso lokal.

## Was geprueft wird

| Skript | Prueft |
|---|---|
| `dateien.py` | Gemeinsame Dateiliste aller Pruefungen (aus `git ls-files`, in allen Ordnern). Ohne Argument: jede Datei hat genau eine Art (`lovelace`, `ressource`, `grafana`, `python`, `doku`, `entwurf`, `meta`, `bild`), sonst Fehler. `bild` (PNG, JPG, GIF, WebP) ist binaer und wird von keiner Pruefung als Text gelesen. Mit Art als Argument: gibt deren Dateien aus. |
| `check_verweise.py` | Jeder genannte Repo-Dateiname existiert: `!include`-Ziele relativ zur einbindenden Datei, Pfade mit `/` relativ zum Repo oder zur Datei, blanke Dateinamen irgendwo im Repo. Erfasst werden Namen mit bekannter Endung (Text- und Bilddateien, auch `.svg`) und Bindestrich oder Unterstrich (wie alle Repo-Dateien), Punktdateien und `README.md`/`DESIGN.md`/`CLAUDE.md`/`SKILL.md`. Bewusste Ausnahmen stehen in `AUSNAHMEN` im Skript, ausgenommene Dateien (die Liste alter Namen in `doku/umbenennung-2026-10.md`) in `AUSGENOMMENE_DATEIEN`. |
| `check_kopf.py` | Kopfblock jeder Datei unter `dashboard/` und jedes Entwurfs (siehe unten): Schluessel der Dateiart in fester Reihenfolge, Art/Bereich/Status passend zu Name und Ort, `Karten` = genutzte `custom:`-Karten plus card-mod, `Templates` = genutzte Templates mit definierender Datei, `Platzhalter` = Treffer der Muster aus `design/platzhalter.yaml`. Dateien ohne Kopfblock mit Platzhaltern muessen dort unter `dateien_ohne_kopf` stehen. |
| `gen_index.py` | Erzeugt die Bereichs- und die Platzhaltertabelle im README (zwischen den Markern `<!-- index:… -->` und `<!-- platzhalter:… -->`) und `dashboard/README.md` aus den Kopfbloecken und `design/platzhalter.yaml`. Mit `--pruefen` (CI, pre-commit) schlaegt es fehl, wenn der committete Stand nicht aktuell ist. |
| `check_template_version.py` | Template-Bibliotheken mit `const VERSION = N`: hat sich ihr Code gegenueber dem Basiszweig geaendert, muss `N` steigen. Sonst behaelt eine offene Seite die alte Bibliothek. |
| `check_persoenlich.py` | Nur lokal (pre-commit, auch auf die Commit-Nachricht): gestagte Aenderungen gegen die Sperrliste `lokal/sperrliste.txt`. Siehe unten. |
| `check_struktur.py` | Ablage und Dateinamen nach der Repo-Struktur (siehe unten). Mit `--streng` (CI, pre-commit) schlaegt sie bei Verstoessen fehl, ohne nur Bericht. |
| `check-js-templates.js` | Jeden `[[[ ... ]]]`-Block in den Lovelace-YAMLs auf JS-Syntaxfehler. Warnt zusaetzlich vor Verwechslungen wie `state[` statt `states[`. |
| `check_yaml.py` | YAML parst (inkl. HA-Tags wie `!include`), keine doppelten Schluessel, `type: custom:*` steht in `known_cards.txt`, Entity-IDs sehen wie `domain.objekt` aus (Werte mit Templates oder Decluttering-Variablen `[[name]]` werden uebersprungen). |
| `check_palette.py` | Jede Farbangabe (Hex, `rgb()`, `rgba()`) in den Karten steht in `design/palette.yaml`. Meldet sonst Fundstelle und naechsten Palettenwert. Prueft auch die Palette selbst (Format, Pflichtfelder, Dubletten) und den hellen Modus: `hell_farben` und `theme` (Variablennamen, Werte aus der Palette, kein ungenutzter heller Wert). Werte aus `hell_farben` sind nur in der Theme-Datei erlaubt. Weiss nur mit Deckkraft, deckend nur als Schrift auf einer Farbe aus `deckend_auf` (Vereinsrot) in derselben Zeile. Regeln: `DESIGN.md`. |
| `check_mobil.py` | Regeln aus `DESIGN.md`, Abschnitt "Bildschirmbreiten" (Galaxy S25 360 px, iPhone 17 Pro 402 px), soweit sie am Text erkennbar sind: jedes button-card-Icon mit `styles.icon` setzt `--ha-icon-display: block` (oder ein genutztes Template tut es, oder `show_icon: false`); kein `labels.formatter` auf der Zeitachse von apexcharts-card; jede Container Query mit Pixel-Schwelle hat direkt davor einen Kommentar mit mindestens zwei px-Werten (die gemessenen Breiten beider Geraete). Fuer Icons von vor der Regel steht der Bestand je Datei in `BESTAND` im Skript; er darf nur sinken und wird im selben Commit gesenkt. `archiv/` ist ausgenommen. |
| `gen_theme.py` | Erzeugt das Theme `dashboard/allgemein/nachtblau-theme-konfig.yaml` aus dem Abschnitt `theme` der Palette. Mit `--pruefen` (CI, pre-commit) schlaegt es fehl, wenn die committete Datei nicht aktuell ist. |
| `check_grafana.py` | Dashboards sind gueltiges JSON mit Pflichtfeldern, Panel-IDs eindeutig, Dashboard-UIDs repo-weit eindeutig, Datasources ueber `${DS}` statt fester UID, keine `__inputs`-Reste, Farben nur aus `design/palette.yaml` (`color`, `fixedColor`, `iconColor`, Heatmap-`fill`; keine Grafana-Farbnamen ausser `text`/`transparent`). |

Dazu im Workflow:

- `yamllint` mit der bewusst lockeren `.yamllint.yml` (Formatierung weitgehend
  aus, damit die Ausgabe signalstark bleibt)
- `ruff check` und `compileall` auf `grafana/` und `ci/`, konfiguriert in `pyproject.toml`
- Abgleich, dass `grafana/*.json` zu `grafana/proxmox_dashboards.py` passt
- `gitleaks` als Secret-Scan, konfiguriert in `.gitleaks.toml`; das Image ist
  auf eine Version gepinnt, damit eine neue Regel die CI nicht ohne Aenderung
  im Repo rot faerbt

## Welche Dateien geprueft werden

Kein Skript durchsucht selbst ein Verzeichnis. Alle holen ihre Dateien aus
`ci/dateien.py`, das jede Datei aus `git ls-files` genau einer Art zuordnet.
So kann eine Karte nach dem Verschieben in einen Unterordner nicht still aus
der Pruefung fallen: Sie behaelt ihre Art, und eine Datei ohne Art laesst
`python ci/dateien.py` fehlschlagen. Neue, noch nicht mit `git add`
hinzugefuegte Dateien zaehlen mit, `lokal/` bleibt ueber `.gitignore` draussen.
Findet eine Pruefung gar keine Datei, schlaegt sie fehl, statt Erfolg zu melden.

## Repo-Struktur

Das Repo ist nach Themenbereichen gegliedert. `check_struktur.py --streng` prueft:

- Im Wurzelverzeichnis nur `README.md`, `DESIGN.md`, `CLAUDE.md`,
  `CONTRIBUTING.md`, `LICENSE`, `pyproject.toml` und Punktdateien.
- Oberste Ordner: `dashboard/`, `design/`, `grafana/`, `doku/`, `ci/`,
  `.claude/`, `.github/`.
- `dashboard/<bereich>/` mit einem Bereich aus `BEREICHE` in `ci/dateien.py`,
  darunter nur `archiv/` (abgeloeste Fassungen) und `entwuerfe/` (HTML,
  Markdown).
- Lovelace-YAML heisst `<thema>[-<variante>]-<art>[-vN].yaml`, Art `karte`,
  `view`, `templates` oder `konfig`; v1 ohne Suffix. Nur Kleinbuchstaben,
  Ziffern, Bindestriche.
- Je Ordner hoechstens eine aktive Version einer Karte.
- `doku/` enthaelt nur Markdown.

Ohne `--streng` meldet das Skript Verstoesse nur als Warnung; CI und
pre-commit laufen mit `--streng`.

Neue Datei: Bereich waehlen (passt keiner, `sonstiges/`), Namen nach dem
Schema bilden, beim Umbenennen oder Verschieben `git mv` verwenden und alle
Verweise im selben Commit anpassen -- `check_verweise.py` meldet vergessene.
Ein neuer Bereich wird in `BEREICHE` in `ci/dateien.py` eingetragen.

## Dateikopf

Jede Datei unter `dashboard/` und jeder Entwurf beginnt mit diesem Block.
Lange Werte gehen in einer mit mindestens drei Leerzeichen eingerueckten
Zeile weiter. Darunter folgt frei der bisherige Erklaertext mit der Zeile
`Voraussetzung` (Integrationen, Helfer, Sensoren).

```yaml
# ============================================================================
# Waschmaschine (Home Connect)
# ----------------------------------------------------------------------------
# Art:           karte
# Bereich:       hausgeraete
# Status:        aktiv
# Karten:        button-card
# Templates:     nachtblau_geraete_fx (hausgeraete-templates.yaml)
# Einfuegen:     Karte hinzufuegen -> Manuell
# Platzhalter:   seriennr_<geraet>
#                (vor dem Einfuegen ersetzen, siehe README.md)
# ============================================================================
```

| Art | Schluessel |
|---|---|
| `karte`, `view`, `templates` | Art, Bereich, Status, Karten, Templates, Einfuegen, Platzhalter |
| `konfig`, `ressource` (JS, mit `//`) | Art, Bereich, Status, Einfuegen, Platzhalter |
| `entwurf` (HTML, Markdown, in `<!-- ... -->` ganz oben, ohne Praefix) | Art, Bereich, Status, Gehoert-zu, Platzhalter |

- `Status`: `aktiv` im Bereichsordner, `entwurf` in `entwuerfe/`, in `archiv/`
  `archiv: ersetzt durch <datei>` oder nur `archiv`, wenn keine Nachfolgerin
  belegt ist.
- `Karten` und `Templates` nennen nur, was die Datei selbst nutzt; Dateien
  hinter `!include` haben ihren eigenen Kopf. Keine: `keine`.
- `Platzhalter`: die `id`s aus `design/platzhalter.yaml`, dahinter
  `(vor dem Einfuegen ersetzen, siehe README.md)`; sonst `keine`.

## Sperrliste fuer echte Namen

Das Repo ist oeffentlich; echte Namen, Geraetenamen, Adressen, Kennzeichen und
Entity-IDs mit Personenbezug gehoeren nicht hinein. Die CI kann das nicht
pruefen, weil die Liste der echten Werte selbst nicht ins Repo darf.
`check_persoenlich.py` prueft deshalb nur lokal gegen `lokal/sperrliste.txt`:

```text
# ein Begriff pro Zeile, Gross-/Kleinschreibung egal
Vorname
Nachname
```

`lokal/` steht in `.gitignore`. Fehlt die Datei, gibt der Hook nur einen
Hinweis aus. Treffer nennen nur die Zeilennummer der Sperrliste, nicht den
Begriff, damit er nicht in Logs landet.

## Warum doppelte Schluessel eigenen Aufwand wert sind

PyYAML und Home Assistant melden ein doppelt vergebenes Mapping-Feld nicht --
der erste Wert wird stillschweigend ueberschrieben. In Kartendateien mit
mehreren hundert Zeilen und YAML-Ankern ist das leicht passiert und im
Dashboard praktisch nicht zu diagnostizieren. `check_yaml.py` bringt dafuer
einen eigenen Loader mit.

## Lokal ausfuehren

```bash
pip install pyyaml yamllint ruff

python ci/dateien.py
python ci/check_verweise.py
python ci/check_struktur.py --streng
python ci/check_kopf.py
python ci/gen_index.py --pruefen
python ci/gen_theme.py --pruefen
python ci/check_template_version.py
node ci/check-js-templates.js
python ci/check_yaml.py
python ci/check_palette.py
python ci/check_mobil.py
python ci/check_grafana.py
yamllint --strict -c .yamllint.yml .
ruff check grafana/ ci/
python -m compileall -q grafana/ ci/
```

Jedes Skript nimmt optional einzelne Dateien als Argument:

```bash
node ci/check-js-templates.js dashboard/klima/wetter-karte-v2.yaml
python ci/check_yaml.py dashboard/klima/wetter-karte-v2.yaml
```

Mit [pre-commit](https://pre-commit.com/) laufen dieselben Pruefungen
automatisch vor jedem Commit:

```bash
pip install pre-commit && pre-commit install
```

## Neue Karte eingefuehrt?

Kartentyp ohne `custom:`-Praefix in `ci/known_cards.txt` eintragen, sonst
schlaegt `check_yaml.py` fehl. Die Whitelist existiert, damit ein Tippfehler
im Kartennamen auffaellt, bevor Lovelace nur noch
"Custom element doesn't exist" anzeigt.

## Neue Farbe verwendet?

`check_palette.py` schlaegt fehl, bis die Farbe in `design/palette.yaml`
steht. Meist ist ein vorhandener Palettenwert gemeint -- die Meldung nennt den
naechsten. Ist die Farbe wirklich neu: Eintrag in der Palette und Begruendung
in `DESIGN.md`, Abschnitt "Eine neue Farbe aufnehmen". Aendert sie sich im
hellen Modus, gehoert auch ihr heller Wert in die Palette (`hell_farben`,
`theme.variablen`); danach `python ci/gen_theme.py` und das Theme mit
committen. Meldet `check_palette.py` einen Wert "des hellen Modus" in einer
Karte, ist dort die Theme-Variable gemeint (`var(--nachtblau-...)`).

## Bewusst nicht geprueft

- **Voller Home-Assistant-Start.** Das sind Lovelace-Snippets, keine
  `configuration.yaml` -- HA validiert sie beim Start gar nicht.
- **Existenz der Entities.** Braeuchte Zugriff auf die laufende Instanz, also
  einen self-hosted Runner oder ein Token als Secret. Zu fragil fuer CI.
- **Formatierungszwang** (Prettier, `ruff format`). Die Dateien sind
  handkuratiert inklusive Kommentarbloecken und YAML-Ankern; ein Autoformatter
  richtet dort mehr Schaden als Nutzen an.
