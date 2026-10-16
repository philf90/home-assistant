# Home Assistant – Owlet-Dashboard

Lovelace-Karten, komplette Dashboard-Views und Grafana-Dashboards für meine
Home-Assistant-Instanz. Alle Karten folgen einem gemeinsamen Design, dem
**Owlet-Stil**, abgeleitet von der Owlet-Smart-Sock-Karte
(`owlet-smart-sock-button-card.yaml`).

> **Hinweis:** Die Dateien sind auf eine konkrete Instanz zugeschnitten.
> Entity-IDs, Gerätenamen, Routen und Pfade müssen vor dem Einsatz an die
> eigene Installation angepasst werden. Persönliche Angaben sind durch
> Platzhalter ersetzt, die in keiner Instanz existieren – siehe
> [Platzhalter ersetzen](#platzhalter-ersetzen).

## Inhalt

| Bereich | Dateien |
|---|---|
| Komplette Views | `flugradar-view.yaml`, `fussball-view.yaml`, `gesundheit-view.yaml`, `netzwerk-view.yaml`, `pflanzen-view.yaml` |
| Templates | `decluttering-templates.yaml`, `flugradar-button-card-templates.yaml`, `fussball-button-card-templates.yaml`, `hausgeraete-animation-button-card-templates.yaml`, `pflanzen-decluttering-templates.yaml`, `wetter-animation-button-card-templates.yaml` |
| Navigation & Kopf | `navbar-card.yaml`, `top-navigation-button-card.yaml`, `welcome-banner-button-card.yaml` |
| Energie | `energie-autarkie-…`, `energie-diagramme-…`, `energie-flow-…`, `energie-flow-leiste-…`, `energie-pv-…`, `energie-verbrauch-uebersicht-…`, `energie-monatsbilanz-card.yaml`, `gas-wasser-button-card.yaml` |
| Klima & Wetter | `temperaturen-…` (v1, v2), `thermostate-…` (v1, v2), `wetter-…`, `meteoalarm-…`, `pollenflug-button-card.yaml` |
| Licht, Fenster, Türen | `lichter-glow-card.yaml`, `lichter-mushroom-card.yaml`, `lichter-raum-card.yaml`, `lichter-slider-button-card.yaml`, `fenster-…`, `fenster-lichter-…`, `fenster-lichter-uebersicht-…`, `haustuer-lock-…`, `haustuer-ereignis-button-card.yaml` |
| Haushaltsgeräte | `waschmaschine-…`, `trockner-…`, `geschirrspueler-…` (animiert über `owlet_geraete_fx`, Entwurf und Home-Connect-Analyse in `hausgeraete-vorschlaege.html`), `staubsauger-button-card.yaml` |
| Netzwerk & System | `unifi-netzwerk-status-…`, `unifi-leitungen-…`, `unifi-udm-system-…` (v1, v2), `unifi-unas-pro-button-card.yaml`, `unifi-verlauf-expander-card.yaml`, `unifi-netzplan-card.yaml` (+ `unifi-netzplan-card.js`, `unifi-kabel-clients.yaml`), `homematic-…`, `system-button-card.yaml`, `wlan-expander-card.yaml` |
| Fahrzeuge | `autos-button-card.yaml` (v1, v2, v3), `template-autos-passat.yaml` |
| Garten & Pflanzen | `garten-…`, `pflanzen-view.yaml` (ohne flower-card; ältere Fassung: `pflanzen-flower-card.yaml` + `pflanzen-status-button-card.yaml`) |
| Personen | `person-presence-…`, `owlet-smart-sock-button-card.yaml` |
| Sonstiges | `kameras-button-card.yaml`, `muellabfuhr-trash-card.yaml` (v1, v2) |
| Grafana | [`grafana/`](grafana/) – Energie-, Proxmox-VE- und Proxmox-Backup-Server-Dashboard |

Gibt es eine Karte in mehreren Varianten (`-v2`, `-v3`), bleibt die ältere Datei
unverändert erhalten. Der Kommentarkopf der neueren Datei erklärt den Unterschied.

## Owlet-Stil

- gemeinsame Kartenhülle, Palette (Grundtöne `#a6d49e`, `#f2f5f8`, `#6e7988`) und Typografie
- rundlich-quadratische Icon-Kacheln, die sich nach Zustand färben
- umgesetzt fast durchgängig mit `custom:button-card`; Styles werden innerhalb
  einer Datei über YAML-Anker geteilt
- Spezialkarten (Kamera-Stream, Sankey, Power-Flow, Pflanzen …) bleiben
  funktional erhalten und bekommen nur die Owlet-Hülle
- verbindlich beschrieben in [`DESIGN.md`](DESIGN.md); die Farbwerte stehen in
  [`design/palette.yaml`](design/palette.yaml) und werden in der CI geprüft

## Voraussetzungen

- Home Assistant mit [HACS](https://hacs.xyz/)
- Frontend-Karten aus HACS, je nach Datei: `button-card`, `card-mod`,
  `apexcharts-card`, `auto-entities`, `bubble-card`, `decluttering-card`, `expander-card`,
  `flower-card`, `homematicip-system-health-card`, `mushroom` (entity, light,
  vacuum), `navbar-card`, `power-flow-card-plus`, `sankey-chart`,
  `slider-button-card`, `trash-card`, `uptime-card`, `webrtc-camera`,
  `xiaomi-vacuum-map-card`
- die Integrationen der jeweiligen Geräte (z. B. Home Connect, UniFi,
  Homematic IP, VW Group Connect, Flightradar24)
- optional für den UniFi-Netzplan: die Integration
  [UniFi WAN](https://github.com/holdestmade/Unifi-WAN). Sie liefert je
  Internetleitung IPv4, IPv6 und Erreichbarkeit, die die offizielle
  UniFi-Integration nicht bereitstellt. Sie steht nicht im HACS-Standardkatalog:
  in HACS unter *Benutzerdefinierte Repositories* mit Typ *Integration*
  hinzufügen. Zur Einrichtung braucht sie einen lokalen API-Schlüssel der
  UniFi-Konsole (Einstellungen → Control Plane → Integrationen). Den
  automatischen Speedtest in ihren Optionen abschalten, sonst testet sie
  standardmäßig stündlich.
- für die UNAS-Pro-Karte: die Integration
  [UniFi UNAS (non-invasive)](https://github.com/LayerTM/unifi-unas-ha)
  (HACS-Standardkatalog, ab Home Assistant 2025.8). Die offizielle
  UniFi-Integration sieht ein UNAS nur als Client. Diese Integration liest
  Pool, Platten (Temperatur, Zustand, Health-Score, Betriebsstunden, defekte
  Sektoren), CPU und RAM über die lokale Drive-API des UNAS, ohne SSH und
  ohne etwas auf dem NAS zu installieren. Die API ist von Ubiquiti nicht
  dokumentiert und kann sich mit Firmware-Updates ändern. Einrichtung:
  1. Den API-Schlüssel in der UniFi-OS-Oberfläche des UNAS erzeugen, nicht
     auf der UDM.
  2. In HACS *UniFi UNAS (non-invasive)* herunterladen, Home Assistant neu
     starten.
  3. Einstellungen → Geräte & Dienste → Integration hinzufügen → *UniFi
     UNAS*: Host `<IP-des-UNAS>`, Port `443`, TLS-Modus und Anmeldung auf
     der Vorgabe lassen (Zertifikat beim ersten Kontakt hinterlegen,
     API-Schlüssel), Schlüssel `<API-Schlüssel des UNAS>`.

  Der Schlüssel liegt danach nur im Config-Entry von Home Assistant, nicht
  in einer Datei des Repos. Mit API-Schlüssel ist die Integration rein
  lesend. Freigaben, Firmware-Updates, Speicherdurchsatz und Steuerung
  (Neustart, Lüftermodus) gibt es nur mit lokalem Konto (Benutzer und
  Passwort); die Karte braucht davon nichts.
- optional für Kabel-Clients im UniFi-Netzplan: das Paket
  `unifi-kabel-clients.yaml`. Es fragt alle 5 Minuten die Controller-API ab
  und legt `sensor.unifi_kabel_clients` mit Switch und Port je Kabel-Client
  an, was die offizielle Integration nicht liefert. Einbinden unter
  `homeassistant: packages:` in der `configuration.yaml`; URL und lokaler
  API-Schlüssel stehen in der `secrets.yaml` (Details im Dateikopf).

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
`decluttering-templates.yaml` und `pflanzen-decluttering-templates.yaml`,
`button_card_templates:` aus den
Flugradar- und Fußball-Templates. Existiert der Block schon, nur die Einträge
darunter ergänzen.

**Template-Sensoren:** `template-autos-passat.yaml` gehört in die
`configuration.yaml`:

```yaml
template: !include template-autos-passat.yaml
```

## Platzhalter ersetzen

Persönliche Angaben (Namen, Gerätenamen, Adresse, Kennzeichen) sind im Repo
anonymisiert. Die Platzhalter gibt es in keiner Home-Assistant-Instanz: Eine
unverändert eingefügte Karte bleibt leer oder meldet „Entität nicht
verfügbar“. Betroffene Dateien tragen oben den Kommentar
`HINWEIS PLATZHALTER`.

| Platzhalter | Steht für | Echte ID finden | Dateien |
|---|---|---|---|
| `person.bewohner` | Personen-Entity | Einstellungen → Personen | `person-presence-…`, `karten-basemap-carto.md` |
| `sensor.iphone_*` | Sensoren der Companion App; `iphone` steht für den Gerätenamen | Einstellungen → Geräte & Dienste → Mobile App → Gerät | `gesundheit-view.yaml`, `person-presence-…` |
| `notify.mobile_app_iphone` | Benachrichtigungen an dasselbe Gerät | Entwicklerwerkzeuge → Aktionen, Suche `notify.mobile_app_` | `flugradar-view.yaml`, `garten-…` (Automationen im Kommentar) |
| `<breite>`, `<laenge>` | Koordinaten von Zuhause | Entwicklerwerkzeuge → Zustände, `zone.home` (Attribute `latitude`, `longitude`) | `flugradar-view.yaml` (Scrape-Ressource im Kommentar) |
| `sensor.pv_anlage_*` | Sensoren der PV-/Solarbank-Anlage | Einstellungen → Geräte & Dienste → Integration der Anlage | `energie-*-button-card.yaml` (5), `energie-monatsbilanz-card.yaml`, `grafana/` (dort ohne `sensor.`) |
| `AB - CD 123`, `AB - EF 456` | Kennzeichen, reiner Anzeigetext | – | `autos-button-card*.yaml` |
| `passat_fenster_kombiniert`, `passat_tueren_kombiniert` | `unique_id` der Template-Sensoren | bisherige `unique_id` übernehmen, sonst legt HA neue Entities an | `template-autos-passat.yaml` |
| `seriennr_geschirrspueler`, `seriennr_waschmaschine`, `seriennr_trockner` | Seriennummer des Home-Connect-Geräts am Anfang der Entity-ID (`sensor.seriennr_…_bsh_common_…`) | Einstellungen → Geräte & Dienste → Home-Connect-Integration → Gerät → Entitäten | `geschirrspueler-…`, `waschmaschine-…`, `trockner-…` |
| `*_seriennr`, `*_seriennr_1`, `*_seriennr_2` | Seriennummer des Geräts in der Entity-ID (Homematic IP, Owlet); `_1`/`_2` trennen zwei Geräte desselben Modells | Einstellungen → Geräte & Dienste → Integration → Gerät → Entitäten | `homematic-…`, `temperaturen-…` (2), `garten-…`, `owlet-smart-sock-…` |
| `*_mac` | MAC-Adresse des Shelly-Geräts in der Entity-ID | Einstellungen → Geräte & Dienste → Shelly → Gerät → Entitäten | `lichter-*` (4), `fenster-lichter-uebersicht-…`, `garten-…` |
| `fin_passat`, `fin_touran` | Fahrgestellnummer in der Entity-ID: V2 (`volkswagencarnet`) mit voller FIN, V3 (`vag_connect`) mit deren letzten 6 Stellen | Einstellungen → Geräte & Dienste → Integration des Fahrzeugs → Gerät → Entitäten | `autos-button-card-v2.yaml`, `autos-button-card-v3.yaml`, `autos-karten-v2-vorschlaege.html` |
| `ieee_adresse` | IEEE-Adresse des Zigbee-Geräts (`0x…`), solange die Entity nicht umbenannt ist | Einstellungen → Geräte & Dienste → Zigbee-Integration → Gerät | `pflanzen-flower-card.yaml`, `pflanzen-view.yaml` |
| `kind_1`, `kind_2` | Vorname eines Kindes in der Entity-ID (`sensor.temperatur_kind_1_*`, `light.kind_2`, `light.kinderzimmer_kind_2_namenslicht`); `1`/`2` entsprechen den Anzeigenamen „Kinderzimmer 1“/„Kinderzimmer 2“ | Einstellungen → Geräte & Dienste → Entitäten, nach Raum oder Gerät suchen | `temperaturen-…` (2), `lichter-*` (4), `fenster-lichter-uebersicht-…` |

Nicht anonymisiert, aber an die eigene Instanz gebunden: die Benutzer-IDs in
`visible:` und `condition: user` (`gesundheit-view.yaml`, `navbar-card.yaml`,
`decluttering-templates.yaml`, `kameras-button-card.yaml`). Am einfachsten
im Karteneditor unter *Sichtbarkeit* den Benutzer neu auswählen.
Ebenso die Entitäten in `unifi-netzplan-card.yaml`: die `device_tracker` der
eigenen UniFi-Geräte und die Sensoren von UniFi WAN, deren IDs Host und Site
der Konsole enthalten (`…_192_168_1_1_default_…`).
In `unifi-unas-pro-button-card.yaml` hängen die IDs am Gerätenamen des UNAS
(`sensor.unas_pro_…`) und des Zwischensteckers für die Leistung
(`sensor.shelly_plugs_unas_pro_…`, optional). Der Hot-Spare-Schacht steht
als Variable `spare` in der Karte, weil die Integration ihn nicht meldet.

**Manuell:** Alle Sensoren eines Geräts oder einer Anlage haben denselben
Präfix. Ein Suchen-und-Ersetzen auf den Präfix genügt, z. B. `sensor.iphone_`
→ `sensor.<eigener_gerätename>_`. Danach unter Entwicklerwerkzeuge → Zustände
stichprobenartig prüfen, ob die IDs existieren.

**Mit Claude:** Claude Code in diesem Repo starten, die Home-Assistant-
Verbindung (MCP) aktivieren und z. B. sagen: *„Bereite
`gesundheit-view.yaml` für meine Instanz vor.“* Der Projekt-Skill
[`.claude/skills/platzhalter-einsetzen`](.claude/skills/platzhalter-einsetzen/SKILL.md)
sucht die echten IDs in der Instanz, legt die Zuordnung zur Bestätigung vor
und erzeugt eine angepasste Fassung in `lokal/`. Ins Dashboard schreibt Claude
nur nach ausdrücklicher Freigabe.

Die echten Werte gehören nicht ins Repo. `lokal/` ist deshalb in
`.gitignore` eingetragen.

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
`autos-karten-v2-vorschlaege.html`, `wetter-animiert-vorschlaege.html`,
`grafana/proxmox-mockups.html`) sind
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
