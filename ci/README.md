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
| `dateien.py` | Gemeinsame Dateiliste aller Pruefungen (aus `git ls-files`, in allen Ordnern). Ohne Argument: jede Datei hat genau eine Art (`lovelace`, `ressource`, `grafana`, `python`, `doku`, `entwurf`, `meta`), sonst Fehler. Mit Art als Argument: gibt deren Dateien aus. |
| `check_verweise.py` | Jeder genannte Repo-Dateiname existiert: `!include`-Ziele relativ zur einbindenden Datei, Pfade mit `/` relativ zum Repo oder zur Datei, blanke Dateinamen irgendwo im Repo. Erfasst werden Namen mit bekannter Endung und Bindestrich oder Unterstrich (wie alle Repo-Dateien), Punktdateien und `README.md`/`DESIGN.md`/`CLAUDE.md`/`SKILL.md`. Bewusste Ausnahmen stehen in `AUSNAHMEN` im Skript. |
| `check_struktur.py` | Ablage und Dateinamen nach der Repo-Struktur (siehe unten). Laeuft vorerst nur als Bericht; mit `--streng` schlaegt sie bei Verstoessen fehl. |
| `check-js-templates.js` | Jeden `[[[ ... ]]]`-Block in den Lovelace-YAMLs auf JS-Syntaxfehler. Warnt zusaetzlich vor Verwechslungen wie `state[` statt `states[`. |
| `check_yaml.py` | YAML parst (inkl. HA-Tags wie `!include`), keine doppelten Schluessel, `type: custom:*` steht in `known_cards.txt`, Entity-IDs sehen wie `domain.objekt` aus (Werte mit Templates oder Decluttering-Variablen `[[name]]` werden uebersprungen). |
| `check_palette.py` | Jede Farbangabe (Hex, `rgb()`, `rgba()`) in den Karten steht in `design/palette.yaml`. Meldet sonst Fundstelle und naechsten Palettenwert. Prueft auch die Palette selbst (Format, Pflichtfelder, Dubletten). Regeln: `DESIGN.md`. |
| `check_grafana.py` | Dashboards sind gueltiges JSON mit Pflichtfeldern, Panel-IDs eindeutig, Dashboard-UIDs repo-weit eindeutig, Datasources ueber `${DS}` statt fester UID, keine `__inputs`-Reste, Farben nur aus `design/palette.yaml` (keine Grafana-Farbnamen ausser `text`/`transparent`). |

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

Ziel ist eine Gliederung nach Themenbereichen. `check_struktur.py` prueft:

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

Solange die Dateien noch im Wurzelverzeichnis liegen, meldet die Pruefung das
als Warnung und bleibt gruen. Nach dem Umzug laeuft sie in der CI mit
`--streng`.

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
python ci/check_struktur.py
node ci/check-js-templates.js
python ci/check_yaml.py
python ci/check_palette.py
python ci/check_grafana.py
yamllint --strict -c .yamllint.yml .
ruff check grafana/ ci/
python -m compileall -q grafana/ ci/
```

Jedes Skript nimmt optional einzelne Dateien als Argument:

```bash
node ci/check-js-templates.js wetter-button-card.yaml
python ci/check_yaml.py wetter-button-card.yaml
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
in `DESIGN.md`, Abschnitt "Eine neue Farbe aufnehmen".

## Bewusst nicht geprueft

- **Voller Home-Assistant-Start.** Das sind Lovelace-Snippets, keine
  `configuration.yaml` -- HA validiert sie beim Start gar nicht.
- **Existenz der Entities.** Braeuchte Zugriff auf die laufende Instanz, also
  einen self-hosted Runner oder ein Token als Secret. Zu fragil fuer CI.
- **Formatierungszwang** (Prettier, `ruff format`). Die Dateien sind
  handkuratiert inklusive Kommentarbloecken und YAML-Ankern; ein Autoformatter
  richtet dort mehr Schaden als Nutzen an.
