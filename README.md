# Home Assistant – Owlet-Dashboard

Lovelace-Karten, komplette Dashboard-Views und Grafana-Dashboards für meine
Home-Assistant-Instanz. Alle Karten folgen einem gemeinsamen Design, dem
**Owlet-Stil**, abgeleitet von der Owlet-Smart-Sock-Karte
(`owlet-smart-sock-karte.yaml`).

> **Hinweis:** Die Dateien sind auf eine konkrete Instanz zugeschnitten.
> Entity-IDs, Gerätenamen, Routen und Pfade müssen vor dem Einsatz an die
> eigene Installation angepasst werden. Persönliche Angaben sind durch
> Platzhalter ersetzt, die in keiner Instanz existieren – siehe
> [Platzhalter ersetzen](#platzhalter-ersetzen).

## Inhalt

Alles, was in Home Assistant landet, liegt unter `dashboard/<bereich>/`. In
jedem Bereich stehen die aktuellen Dateien direkt im Ordner, abgelöste
Fassungen in `archiv/` und HTML-Entwürfe in `entwuerfe/`. Die Dateiart steht
im Namen: `-karte`, `-view`, `-templates` (für den Raw-Konfigurationseditor),
`-konfig` (für die `configuration.yaml`).

| Bereich | Aktuelle Dateien | `archiv/` | `entwuerfe/` |
|---|---|---|---|
| [`allgemein/`](dashboard/allgemein/) | `navbar-karte.yaml`, `top-navigation-karte.yaml`, `welcome-banner-karte.yaml`, `navigation-templates.yaml` | – | `home-kacheln.html` |
| [`energie/`](dashboard/energie/) | `energie-flow-karte.yaml` (animiertes Flussdiagramm mit Autarkie jetzt und heute), `energie-verbraucher-karte.yaml`, `energie-monatsbilanz-karte.yaml` (Autarkie je Monat und Jahr), `energie-solarbank-pv-karte.yaml`, `energie-zaehler-karte.yaml`, `energie-templates.yaml` (Aufbau im Dateikopf) | `energie-autarkie-karte.yaml`, `energie-diagramme-karte.yaml`, `energie-flow-leiste-karte.yaml`, `energie-pv-karte.yaml`, `energie-verbrauch-uebersicht-karte.yaml`, `gas-wasser-karte.yaml` | `energiefluss.html` (Entwurf und Messwerte) |
| [`klima/`](dashboard/klima/) | `temperaturen-karte-v2.yaml`, `thermostate-karte-v3.yaml` (animiert über `owlet_heizung_fx`, Zustand „Fenster offen“), `heizung-templates.yaml`, `wetter-karte.yaml`, `meteoalarm-karte.yaml`, `pollenflug-karte.yaml`, `wetter-templates.yaml` | `temperaturen-karte.yaml`, `thermostate-karte.yaml`, `thermostate-karte-v2.yaml` | `wetter-animiert.html` |
| [`licht/`](dashboard/licht/) | Varianten `lichter-raum-karte.yaml`, `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`, `lichter-slider-karte.yaml`; `fenster-karte.yaml`, `fenster-lichter-karte.yaml`, `fenster-lichter-uebersicht-karte.yaml`, `haustuer-lock-karte.yaml`, `haustuer-ereignis-karte.yaml` | – | – |
| [`hausgeraete/`](dashboard/hausgeraete/) | `waschmaschine-karte.yaml`, `trockner-karte.yaml`, `geschirrspueler-karte.yaml` (animiert über `owlet_geraete_fx`), `staubsauger-karte.yaml`, `hausgeraete-templates.yaml` | – | `hausgeraete.html` (Entwurf und Home-Connect-Analyse) |
| [`netzwerk/`](dashboard/netzwerk/) | `netzwerk-view.yaml` (bindet sechs Karten aus demselben Ordner ein), `unifi-netzwerk-status-karte.yaml`, `unifi-leitungen-karte.yaml`, `unifi-udm-system-karte-v2.yaml`, `unifi-unas-pro-karte.yaml`, `unifi-verlauf-karte.yaml`, `unifi-netzplan-karte.yaml` mit `unifi-netzplan-card.js` und `unifi-kabel-clients-konfig.yaml`, `homematic-karte.yaml`, `system-karte.yaml`, `wlan-karte.yaml` | `unifi-udm-system-karte.yaml` | – |
| [`fahrzeuge/`](dashboard/fahrzeuge/) | `autos-karte-v4.yaml` (animiert über `owlet_auto_fx`), `autos-templates.yaml`, `autos-passat-konfig.yaml` | `autos-karte.yaml`, `autos-karte-v2.yaml`, `autos-karte-v3.yaml` | `autos-animation.html` (Entwurf und Datenlage), `autos-karten-v2.html` |
| [`garten/`](dashboard/garten/) | `garten-karte.yaml`, `pflanzen-view.yaml` (ohne flower-card), `pflanzen-templates.yaml` | `pflanzen-flower-karte.yaml`, `pflanzen-status-karte.yaml` | – |
| [`personen/`](dashboard/personen/) | `person-presence-karte.yaml`, `owlet-smart-sock-karte.yaml`, `gesundheit-view.yaml` | – | – |
| [`flugradar/`](dashboard/flugradar/) | `flugradar-view.yaml`, `flugradar-templates.yaml` | – | – |
| [`fussball/`](dashboard/fussball/) | `fussball-view.yaml`, `fussball-templates.yaml` | – | – |
| [`sonstiges/`](dashboard/sonstiges/) | `kameras-karte.yaml`, `muellabfuhr-karte-v2.yaml` | `muellabfuhr-karte.yaml` | – |
| [`grafana/`](grafana/) | Energie-, Proxmox-VE- und Proxmox-Backup-Server-Dashboard | – | `proxmox-mockups.html`, `proxmox-mockups.md` |
| [`doku/`](doku/) | Notizen, siehe [Notizen](#notizen) | – | – |

Varianten (`lichter-raum-…`, `lichter-glow-…`) sind gleichwertige
Alternativen. Versionen (`-v2`, `-v3`) lösen ihre Vorgängerin ab; die
Vorgängerin liegt dann in `archiv/` und bekommt nur noch Änderungen, die alle
Dateien betreffen (Palette, Anonymisierung). Der Kommentarkopf der neueren
Datei erklärt den Unterschied.

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
  `unifi-kabel-clients-konfig.yaml`. Es fragt alle 5 Minuten die Controller-API ab
  und legt `sensor.unifi_kabel_clients` mit Switch und Port je Kabel-Client
  an, was die offizielle Integration nicht liefert. Einbinden unter
  `homeassistant: packages:` in der `configuration.yaml`; URL und lokaler
  API-Schlüssel stehen in der `secrets.yaml` (Details im Dateikopf).

Jede Datei beginnt mit einem festen Kopfblock: Art, Bereich, Status, die
genutzten HACS-Karten (**Karten**), die nötigen Templates mit ihrer Datei
(**Templates**), wie sie eingefügt wird (**Einfuegen**) und ihre
**Platzhalter**. Integrationen und weitere Voraussetzungen stehen im Text
darunter unter **Voraussetzung**.

## Verwendung

**Einzelne Karte:** Dashboard bearbeiten → Karte hinzufügen → *Manuell* →
Inhalt der YAML-Datei einfügen.

**Komplette View:** in einem YAML-Dashboard per `!include` einbinden. Die
View zusammen mit den Karten, die sie einbindet, in einen Ordner im
Konfigurationsordner kopieren, z. B. `dashboard/netzwerk/`:

```yaml
views:
  - !include dashboard/netzwerk/netzwerk-view.yaml
```

Der Pfad ist relativ zur Datei, die das `!include` enthält; die Includes in
der View selbst zeigen auf Dateien im selben Ordner.

**Templates:** einmalig im Raw-Konfigurationseditor des Dashboards auf
oberster Ebene (neben `views:`) einfügen – `decluttering_templates:` aus
`navigation-templates.yaml` und `pflanzen-templates.yaml`,
`button_card_templates:` aus den
Flugradar-, Fußball-, Wetter-, Hausgeräte- und Heizungs-Templates. Existiert der Block schon, nur die Einträge
darunter ergänzen.

**Template-Sensoren:** `autos-passat-konfig.yaml` gehört in die
`configuration.yaml`:

```yaml
template: !include dashboard/fahrzeuge/autos-passat-konfig.yaml
```

## Platzhalter ersetzen

Persönliche Angaben (Namen, Gerätenamen, Adresse, Kennzeichen) sind im Repo
anonymisiert. Die Platzhalter gibt es in keiner Home-Assistant-Instanz: Eine
unverändert eingefügte Karte bleibt leer oder meldet „Entität nicht
verfügbar“. Welche Platzhalter eine Datei enthält, steht in ihrem Kopfblock
in der Zeile `Platzhalter:`. Die verbindliche Liste mit Suchmustern steht in
[`design/platzhalter.yaml`](design/platzhalter.yaml).

| Platzhalter | Steht für | Echte ID finden | Dateien |
|---|---|---|---|
| `person.bewohner` | Personen-Entity | Einstellungen → Personen | `person-presence-karte.yaml`, `karten-basemap-carto.md` |
| `sensor.iphone_*` | Sensoren der Companion App; `iphone` steht für den Gerätenamen | Einstellungen → Geräte & Dienste → Mobile App → Gerät | `gesundheit-view.yaml`, `person-presence-karte.yaml` |
| `notify.mobile_app_iphone` | Benachrichtigungen an dasselbe Gerät | Entwicklerwerkzeuge → Aktionen, Suche `notify.mobile_app_` | `flugradar-view.yaml`, `garten-karte.yaml` (Automationen im Kommentar), `hausgeraete.html` |
| `<breite>`, `<laenge>` | Koordinaten von Zuhause | Entwicklerwerkzeuge → Zustände, `zone.home` (Attribute `latitude`, `longitude`) | `flugradar-view.yaml` (Scrape-Ressource im Kommentar) |
| `sensor.pv_anlage_*` | Sensoren der PV-/Solarbank-Anlage | Einstellungen → Geräte & Dienste → Integration der Anlage | `energie/`: `energie-flow-karte.yaml`, `energie-verbraucher-karte.yaml`, `energie-solarbank-pv-karte.yaml`, `energie-monatsbilanz-karte.yaml`, `energie-templates.yaml`, `energiefluss.html`, in `archiv/` vier weitere; `grafana/` (dort ohne `sensor.`) |
| `AB - CD 123`, `AB - EF 456` | Kennzeichen, reiner Anzeigetext | – | `fahrzeuge/`: alle Auto-Karten, `autos-passat-konfig.yaml`, die Entwürfe |
| `passat_fenster_kombiniert`, `passat_tueren_kombiniert` | `unique_id` der Template-Sensoren | bisherige `unique_id` übernehmen, sonst legt HA neue Entities an | `autos-passat-konfig.yaml` |
| `seriennr_geschirrspueler`, `seriennr_waschmaschine`, `seriennr_trockner` | Seriennummer des Home-Connect-Geräts am Anfang der Entity-ID (`sensor.seriennr_…_bsh_common_…`) | Einstellungen → Geräte & Dienste → Home-Connect-Integration → Gerät → Entitäten | `geschirrspueler-karte.yaml`, `waschmaschine-karte.yaml`, `trockner-karte.yaml` |
| `*_seriennr`, `*_seriennr_1`, `*_seriennr_2` | Seriennummer des Geräts in der Entity-ID (Homematic IP, Owlet); `_1`/`_2` trennen zwei Geräte desselben Modells | Einstellungen → Geräte & Dienste → Integration → Gerät → Entitäten | `homematic-karte.yaml`, `temperaturen-karte-v2.yaml` (und v1 in `archiv/`), `garten-karte.yaml`, `owlet-smart-sock-karte.yaml` |
| `*_mac` | MAC-Adresse des Shelly-Geräts in der Entity-ID | Einstellungen → Geräte & Dienste → Shelly → Gerät → Entitäten | die vier `lichter-*-karte.yaml`, `fenster-lichter-uebersicht-karte.yaml`, `garten-karte.yaml` |
| `fin_passat`, `fin_touran` | Fahrgestellnummer in der Entity-ID: V2 (`volkswagencarnet`) mit voller FIN, V3 (`vag_connect`) mit deren letzten 6 Stellen | Einstellungen → Geräte & Dienste → Integration des Fahrzeugs → Gerät → Entitäten | `autos-karte-v2.yaml`, `autos-karte-v3.yaml`, `autos-karte-v4.yaml`, `autos-karten-v2.html` |
| `ieee_adresse` | IEEE-Adresse des Zigbee-Geräts (`0x…`), solange die Entity nicht umbenannt ist | Einstellungen → Geräte & Dienste → Zigbee-Integration → Gerät | `pflanzen-flower-karte.yaml`, `pflanzen-view.yaml` |
| `kind_1`, `kind_2` | Vorname eines Kindes in der Entity-ID (`sensor.temperatur_kind_1_*`, `light.kind_2`, `light.kinderzimmer_kind_2_namenslicht`); `1`/`2` entsprechen den Anzeigenamen „Kinderzimmer 1“/„Kinderzimmer 2“ | Einstellungen → Geräte & Dienste → Entitäten, nach Raum oder Gerät suchen | `temperaturen-karte-v2.yaml` (und v1 in `archiv/`), die vier `lichter-*-karte.yaml`, `fenster-lichter-uebersicht-karte.yaml` |

Nicht anonymisiert, aber an die eigene Instanz gebunden: die Benutzer-IDs in
`visible:` und `condition: user` (`gesundheit-view.yaml`, `navbar-karte.yaml`,
`navigation-templates.yaml`, `kameras-karte.yaml`). Am einfachsten
im Karteneditor unter *Sichtbarkeit* den Benutzer neu auswählen.
Ebenso die Entitäten in `unifi-netzplan-karte.yaml`: die `device_tracker` der
eigenen UniFi-Geräte und die Sensoren von UniFi WAN, deren IDs Host und Site
der Konsole enthalten (`…_192_168_1_1_default_…`).
In `unifi-unas-pro-karte.yaml` hängen die IDs am Gerätenamen des UNAS
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

- [`umbenennung-2026-10.md`](doku/umbenennung-2026-10.md) – alte Dateinamen
  und ihr neuer Ort nach dem Umzug in die Bereichsordner
- [`karten-basemap-carto.md`](doku/karten-basemap-carto.md) – „API KEY REQUIRED“
  auf allen Karten im Frontend
- [`proxmox-haos-secure-boot-warnung.md`](doku/proxmox-haos-secure-boot-warnung.md) –
  Proxmox-Warnung `ms-cert=2023k` beim Start der HA-VM
- [`proxmox-haos-speicher-erweitern.md`](doku/proxmox-haos-speicher-erweitern.md) –
  Festplatte von Home Assistant OS unter Proxmox vergrößern

Die HTML-Dateien in den Ordnern `entwuerfe/` sind Design-Entwürfe und werden
direkt im Browser geöffnet.

## Prüfungen

Der Workflow `Validate` läuft bei jedem Push und Pull Request und prüft:

- JavaScript in `[[[ … ]]]`-Templates der button-card auf Syntaxfehler
- YAML-Struktur: Parsing, doppelte Schlüssel, bekannte Kartentypen, Format der Entity-IDs
- `yamllint`, `ruff` und Python-Übersetzung
- dass jede Datei einer Art zugeordnet ist (`ci/dateien.py`), damit keine Datei still aus den Prüfungen fällt
- dass jeder genannte Dateiname und jedes `!include`-Ziel existiert (`ci/check_verweise.py`)
- den Kopfblock jeder Datei: Karten, Templates und Platzhalter müssen zum Inhalt passen (`ci/check_kopf.py`)
- Ablage und Dateinamen nach der Ordnerstruktur (`ci/check_struktur.py`)
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
