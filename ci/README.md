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
| `check-js-templates.js` | Jeden `[[[ ... ]]]`-Block in den Lovelace-YAMLs auf JS-Syntaxfehler. Warnt zusaetzlich vor Verwechslungen wie `state[` statt `states[`. |
| `check_yaml.py` | YAML parst (inkl. HA-Tags wie `!include`), keine doppelten Schluessel, `type: custom:*` steht in `known_cards.txt`, Entity-IDs sehen wie `domain.objekt` aus. |
| `check_grafana.py` | Dashboards sind gueltiges JSON mit Pflichtfeldern, Panel-IDs eindeutig, Dashboard-UIDs repo-weit eindeutig, Datasources ueber `${DS}` statt fester UID, keine `__inputs`-Reste. |

Dazu im Workflow:

- `yamllint` mit der bewusst lockeren `.yamllint.yml` (Formatierung weitgehend
  aus, damit die Ausgabe signalstark bleibt)
- `ruff check` auf den Python-Skripten, konfiguriert in `pyproject.toml`
- Abgleich, dass `grafana/*.json` zu `grafana/proxmox_dashboards.py` passt
- `gitleaks` als Secret-Scan, konfiguriert in `.gitleaks.toml`

## Warum doppelte Schluessel eigenen Aufwand wert sind

PyYAML und Home Assistant melden ein doppelt vergebenes Mapping-Feld nicht --
der erste Wert wird stillschweigend ueberschrieben. In Kartendateien mit
mehreren hundert Zeilen und YAML-Ankern ist das leicht passiert und im
Dashboard praktisch nicht zu diagnostizieren. `check_yaml.py` bringt dafuer
einen eigenen Loader mit.

## Lokal ausfuehren

```bash
pip install pyyaml yamllint ruff

node ci/check-js-templates.js
python ci/check_yaml.py
python ci/check_grafana.py
yamllint --strict -c .yamllint.yml .
ruff check grafana/ ci/
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

## Bewusst nicht geprueft

- **Voller Home-Assistant-Start.** Das sind Lovelace-Snippets, keine
  `configuration.yaml` -- HA validiert sie beim Start gar nicht.
- **Existenz der Entities.** Braeuchte Zugriff auf die laufende Instanz, also
  einen self-hosted Runner oder ein Token als Secret. Zu fragil fuer CI.
- **Formatierungszwang** (Prettier, `ruff format`). Die Dateien sind
  handkuratiert inklusive Kommentarbloecken und YAML-Ankern; ein Autoformatter
  richtet dort mehr Schaden als Nutzen an.
