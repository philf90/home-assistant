# Home Assistant – Owlet-Dashboard

Lovelace-Karten, komplette Dashboard-Views und Grafana-Dashboards für meine
Home-Assistant-Instanz. Alle Karten folgen einem gemeinsamen Design, dem
**Owlet-Stil**, abgeleitet von der Owlet-Smart-Sock-Karte
(`owlet-smart-sock-button-card.yaml`).

> **Hinweis:** Die Dateien sind auf eine konkrete Instanz zugeschnitten.
> Entity-IDs, Gerätenamen, Routen und Pfade müssen vor dem Einsatz an die
> eigene Installation angepasst werden. Persönliche Angaben sind durch
> neutrale Platzhalter ersetzt, z. B. `person.bewohner`, `sensor.iphone_*`,
> `sensor.pv_anlage_*` und die Kennzeichen `AB - CD 123` / `AB - EF 456`.

## Inhalt

| Bereich | Dateien |
|---|---|
| Komplette Views | `flugradar-view.yaml`, `fussball-view.yaml`, `gesundheit-view.yaml`, `netzwerk-view.yaml` |
| Templates | `decluttering-templates.yaml`, `flugradar-button-card-templates.yaml`, `fussball-button-card-templates.yaml` |
| Navigation & Kopf | `navbar-card.yaml`, `top-navigation-button-card.yaml`, `welcome-banner-button-card.yaml` |
| Energie | `energie-autarkie-…`, `energie-diagramme-…`, `energie-flow-…`, `energie-flow-leiste-…`, `energie-pv-…`, `energie-verbrauch-uebersicht-…`, `gas-wasser-button-card.yaml` |
| Klima & Wetter | `temperaturen-…` (v1, v2), `thermostate-…` (v1, v2), `wetter-…`, `meteoalarm-…`, `pollenflug-button-card.yaml` |
| Licht, Fenster, Türen | `lichter-glow-card.yaml`, `lichter-mushroom-card.yaml`, `lichter-raum-card.yaml`, `lichter-slider-button-card.yaml`, `fenster-…`, `fenster-lichter-…`, `fenster-lichter-uebersicht-…`, `haustuer-lock-…`, `haustuer-ereignis-button-card.yaml` |
| Haushaltsgeräte | `waschmaschine-…`, `trockner-…`, `geschirrspueler-…`, `staubsauger-button-card.yaml` |
| Netzwerk & System | `unifi-…`, `unifi-clients-…`, `unifi-steuerung-…`, `unifi-udm-system-…`, `unifi-wan-durchsatz-…`, `homematic-…`, `system-button-card.yaml`, `wlan-expander-card.yaml` |
| Fahrzeuge | `autos-button-card.yaml` (v1, v2, v3), `template-autos-passat.yaml` |
| Garten & Pflanzen | `garten-…`, `pflanzen-status-button-card.yaml`, `pflanzen-flower-card.yaml` |
| Personen | `person-presence-…`, `owlet-smart-sock-button-card.yaml` |
| Sonstiges | `kameras-button-card.yaml`, `muellabfuhr-trash-card.yaml` (v1, v2) |
| Grafana | [`grafana/`](grafana/) – Energie-, Proxmox-VE- und Proxmox-Backup-Server-Dashboard |

Gibt es eine Karte in mehreren Varianten (`-v2`, `-v3`), bleibt die ältere Datei
unverändert erhalten. Der Kommentarkopf der neueren Datei erklärt den Unterschied.

## Owlet-Stil

- gemeinsame Kartenhülle, Palette (`#a6d49e`, `#f2f5f8`, `#6e7988`) und Typografie
- rundlich-quadratische Icon-Kacheln, die sich nach Zustand färben
- umgesetzt fast durchgängig mit `custom:button-card`; Styles werden innerhalb
  einer Datei über YAML-Anker geteilt
- Spezialkarten (Kamera-Stream, Sankey, Power-Flow, Pflanzen …) bleiben
  funktional erhalten und bekommen nur die Owlet-Hülle

## Voraussetzungen

- Home Assistant mit [HACS](https://hacs.xyz/)
- Frontend-Karten aus HACS, je nach Datei: `button-card`, `card-mod`,
  `apexcharts-card`, `bubble-card`, `decluttering-card`, `expander-card`,
  `flower-card`, `homematicip-system-health-card`, `mushroom` (entity, light,
  vacuum), `navbar-card`, `power-flow-card-plus`, `sankey-chart`,
  `slider-button-card`, `trash-card`, `uptime-card`, `webrtc-camera`,
  `xiaomi-vacuum-map-card`
- die Integrationen der jeweiligen Geräte (z. B. Home Connect, UniFi,
  Homematic IP, VW Group Connect, Flightradar24)

Welche Karten und Integrationen eine Datei braucht, steht in ihrem
Kommentarkopf unter **Voraussetzung**.

## Verwendung

**Einzelne Karte:** Dashboard bearbeiten → Karte hinzufügen → *Manuell* →
Inhalt der YAML-Datei einfügen.

**Komplette View:** in einem YAML-Dashboard per `!include` einbinden, z. B.

```yaml
views:
  - !include netzwerk-view.yaml
```

Die Pfade sind relativ zum Konfigurationsordner von Home Assistant.

**Templates:** einmalig im Raw-Konfigurationseditor des Dashboards auf
oberster Ebene (neben `views:`) einfügen – `decluttering_templates:` aus
`decluttering-templates.yaml`, `button_card_templates:` aus den
Flugradar- und Fußball-Templates. Existiert der Block schon, nur die Einträge
darunter ergänzen.

**Template-Sensoren:** `template-autos-passat.yaml` gehört in die
`configuration.yaml`:

```yaml
template: !include template-autos-passat.yaml
```

## Grafana

| Dashboard | UID | Datenquelle | Doku |
|---|---|---|---|
| `energie-dashboard.json` | `ha-energie` | InfluxDB 2 | [grafana/README.md](grafana/README.md) |
| `proxmox-ve-dashboard.json` | `proxmox-ve` | InfluxDB 2 | [grafana/proxmox-dashboards.md](grafana/proxmox-dashboards.md) |
| `proxmox-pbs-dashboard.json` | `proxmox-pbs` | InfluxDB 2 + PBS-API (Infinity) | [grafana/proxmox-dashboards.md](grafana/proxmox-dashboards.md) |

Dazu:

- `ha_statistics_backfill.py` überträgt vorhandene Langzeitstatistiken aus
  Home Assistant nach InfluxDB 2, damit das Energie-Dashboard auch rückwirkend
  Daten zeigt.
- `proxmox_dashboards.py` erzeugt die beiden Proxmox-Dashboards. Änderungen
  gehören in den Generator, nicht ins JSON.

## Notizen

- [`karten-basemap-carto.md`](karten-basemap-carto.md) – „API KEY REQUIRED“
  auf allen Karten im Frontend
- [`proxmox-haos-secure-boot-warnung.md`](proxmox-haos-secure-boot-warnung.md) –
  Proxmox-Warnung `ms-cert=2023k` beim Start der HA-VM
- [`proxmox-haos-speicher-erweitern.md`](proxmox-haos-speicher-erweitern.md) –
  Festplatte von Home Assistant OS unter Proxmox vergrößern

Die HTML-Dateien (`home-kacheln-vorschlaege.html`,
`autos-karten-v2-vorschlaege.html`, `grafana/proxmox-mockups.html`) sind
Design-Entwürfe und werden direkt im Browser geöffnet.

## Prüfungen

Der Workflow `Validate` läuft bei jedem Push und Pull Request und prüft:

- JavaScript in `[[[ … ]]]`-Templates der button-card auf Syntaxfehler
- YAML-Struktur: Parsing, doppelte Schlüssel, bekannte Kartentypen, Format der Entity-IDs
- `yamllint`, `ruff` und Python-Übersetzung
- Grafana-JSON sowie den Abgleich mit `proxmox_dashboards.py`
- Secrets mit `gitleaks`

Neue `custom:`-Karte im Repo? Kartentyp in `ci/known_cards.txt` eintragen.
Lokal ausführen und Details: [ci/README.md](ci/README.md). Mit
[pre-commit](https://pre-commit.com/) laufen dieselben Prüfungen vor jedem Commit:

```bash
pip install pre-commit && pre-commit install
```

## Lizenz

[MIT](LICENSE) – Kopieren, Anpassen und Weitergeben ausdrücklich erwünscht,
solange der Lizenzhinweis erhalten bleibt.
