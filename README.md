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
`-konfig` (für die `configuration.yaml`). Titel, Karten und Status jeder
Datei stehen in [`dashboard/README.md`](dashboard/README.md); beide Übersichten
erzeugt `ci/gen_index.py` aus den Kopfblöcken der Dateien.

<!-- index:start -->
| Bereich | Aktuelle Dateien | `archiv/` | `entwuerfe/` |
|---|---|---|---|
| [`allgemein/`](dashboard/allgemein/) | `navbar-karte.yaml`, `navigation-templates.yaml`, `owlet-theme-konfig.yaml`, `top-navigation-karte.yaml`, `welcome-banner-karte.yaml` | – | `banner-hell.html`, `home-kacheln.html` |
| [`energie/`](dashboard/energie/) | `energie-flow-karte.yaml`, `energie-monatsbilanz-karte.yaml`, `energie-solarbank-pv-karte.yaml`, `energie-templates.yaml`, `energie-verbraucher-karte.yaml`, `energie-zaehler-karte.yaml` | `energie-autarkie-karte.yaml`, `energie-diagramme-karte.yaml`, `energie-flow-leiste-karte.yaml`, `energie-pv-karte.yaml`, `energie-verbrauch-uebersicht-karte.yaml`, `gas-wasser-karte.yaml` | `energiefluss.html` |
| [`klima/`](dashboard/klima/) | `heizung-templates.yaml`, `meteoalarm-karte.yaml`, `pollenflug-karte.yaml`, `temperaturen-karte-v2.yaml`, `thermostate-karte-v3.yaml`, `warnlage-templates.yaml`, `wetter-karte-v2.yaml`, `wetter-templates.yaml`, `wetter-view.yaml` | `temperaturen-karte.yaml`, `thermostate-karte-v2.yaml`, `thermostate-karte.yaml`, `wetter-karte.yaml` | `wetter-animiert.html` |
| [`licht/`](dashboard/licht/) | `fenster-karte.yaml`, `fenster-lichter-karte.yaml`, `fenster-lichter-uebersicht-karte.yaml`, `haustuer-ereignis-karte.yaml`, `haustuer-lock-karte.yaml`, `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`, `lichter-raum-karte.yaml`, `lichter-slider-karte.yaml` | – | – |
| [`hausgeraete/`](dashboard/hausgeraete/) | `geschirrspueler-karte.yaml`, `hausgeraete-templates.yaml`, `trockner-karte.yaml`, `waschmaschine-karte.yaml` | `staubsauger-karte.yaml` | `hausgeraete.html` |
| [`netzwerk/`](dashboard/netzwerk/) | `homematic-view.yaml`, `netzwerk-view.yaml`, `system-karte.yaml`, `unifi-kabel-clients-konfig.yaml`, `unifi-leitungen-karte.yaml`, `unifi-netzplan-card.js`, `unifi-netzplan-karte.yaml`, `unifi-netzwerk-status-karte.yaml`, `unifi-udm-system-karte-v2.yaml`, `unifi-unas-pro-karte.yaml`, `unifi-verlauf-karte.yaml`, `wlan-karte.yaml` | `homematic-karte.yaml`, `unifi-udm-system-karte.yaml` | – |
| [`fahrzeuge/`](dashboard/fahrzeuge/) | `autos-karte-v4.yaml`, `autos-passat-konfig.yaml`, `autos-templates.yaml` | `autos-karte-v2.yaml`, `autos-karte-v3.yaml`, `autos-karte.yaml` | `autos-animation.html`, `autos-karten-v2.html` |
| [`garten/`](dashboard/garten/) | `garten-karte.yaml`, `pflanzen-templates.yaml`, `pflanzen-view.yaml` | `pflanzen-flower-karte.yaml`, `pflanzen-status-karte.yaml` | – |
| [`personen/`](dashboard/personen/) | `gesundheit-view.yaml`, `owlet-smart-sock-karte.yaml`, `person-presence-karte.yaml` | – | – |
| [`flugradar/`](dashboard/flugradar/) | `flugradar-templates.yaml`, `flugradar-view.yaml` | – | – |
| [`fussball/`](dashboard/fussball/) | `fussball-espn-konfig.yaml`, `fussball-meldungen-konfig.yaml`, `fussball-templates.yaml`, `fussball-view.yaml` | – | – |
| [`sonstiges/`](dashboard/sonstiges/) | `kameras-templates.yaml`, `kameras-view.yaml`, `muellabfuhr-karte-v2.yaml` | `kameras-karte.yaml`, `muellabfuhr-karte.yaml` | – |
| [`grafana/`](grafana/) | `energie-dashboard.json`, `proxmox-pbs-dashboard.json`, `proxmox-ve-dashboard.json` | – | `proxmox-mockups.html`, `proxmox-mockups.md` |
| [`doku/`](doku/) | `karten-basemap-carto.md`, `proxmox-haos-secure-boot-warnung.md`, `proxmox-haos-speicher-erweitern.md`, `umbenennung-2026-10.md` | – | – |
<!-- index:end -->

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
  `flower-card`, `homematicip-system-health-card`, `mushroom` (entity,
  light), `navbar-card`, `power-flow-card-plus`, `sankey-chart`,
  `slider-button-card`, `trash-card`, `uptime-card`, `webrtc-camera`
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
[`design/platzhalter.yaml`](design/platzhalter.yaml); die Tabelle unten wird
daraus und aus den Kopfblöcken erzeugt.

<!-- platzhalter:start -->
| Platzhalter | Steht für | Echte ID finden | Dateien |
|---|---|---|---|
| `person.bewohner` | Personen-Entity | Einstellungen → Personen | `person-presence-karte.yaml`, `doku/karten-basemap-carto.md` |
| `sensor.iphone_*` | Sensoren der Companion App; `iphone` steht für den Gerätenamen | Einstellungen → Geräte & Dienste → Mobile App → Gerät | `gesundheit-view.yaml`, `person-presence-karte.yaml` |
| `notify.mobile_app_iphone` | Benachrichtigungen an dasselbe Gerät | Entwicklerwerkzeuge → Aktionen, Suche `notify.mobile_app_` | `flugradar-view.yaml`, `fussball-meldungen-konfig.yaml`, `fussball-view.yaml`, `garten-karte.yaml`, `hausgeraete.html` |
| `<breite>`, `<laenge>` | Koordinaten von Zuhause | Entwicklerwerkzeuge → Zustände, `zone.home` (Attribute `latitude`, `longitude`) | `flugradar-view.yaml` |
| `sensor.pv_anlage_*` | Sensoren der PV-/Solarbank-Anlage (in Grafana ohne `sensor.`) | Einstellungen → Geräte & Dienste → Integration der Anlage | `energie-flow-karte.yaml`, `energie-monatsbilanz-karte.yaml`, `energie-solarbank-pv-karte.yaml`, `energie-templates.yaml`, `energie-verbraucher-karte.yaml`, `energiefluss.html`, `grafana/README.md`, `grafana/energie-dashboard.json`; in `archiv/`: `energie-autarkie-karte.yaml`, `energie-diagramme-karte.yaml`, `energie-flow-leiste-karte.yaml`, `energie-pv-karte.yaml` |
| `AB - CD 123`, `AB - EF 456` | Kennzeichen, reiner Anzeigetext | – | `autos-animation.html`, `autos-karte-v4.yaml`, `autos-karten-v2.html`, `autos-passat-konfig.yaml`; in `archiv/`: `autos-karte-v2.yaml`, `autos-karte-v3.yaml`, `autos-karte.yaml` |
| `passat_fenster_kombiniert`, `passat_tueren_kombiniert` | `unique_id` der Template-Sensoren | bisherige `unique_id` übernehmen, sonst legt HA neue Entities an | `autos-passat-konfig.yaml` |
| `seriennr_geschirrspueler`, `seriennr_waschmaschine`, `seriennr_trockner` | Seriennummer des Home-Connect-Geräts am Anfang der Entity-ID (`sensor.seriennr_…_bsh_common_…`) | Einstellungen → Geräte & Dienste → Home-Connect-Integration → Gerät → Entitäten | `geschirrspueler-karte.yaml`, `trockner-karte.yaml`, `waschmaschine-karte.yaml` |
| `*_seriennr`, `*_seriennr_1`, `*_seriennr_2` | Seriennummer des Geräts in der Entity-ID (Homematic IP, Owlet); `_1`/`_2` trennen zwei Geräte desselben Modells | Einstellungen → Geräte & Dienste → Integration → Gerät → Entitäten | `garten-karte.yaml`, `homematic-view.yaml`, `owlet-smart-sock-karte.yaml`, `temperaturen-karte-v2.yaml`; in `archiv/`: `homematic-karte.yaml`, `temperaturen-karte.yaml` |
| `*_mac` | MAC-Adresse des Shelly-Geräts in der Entity-ID | Einstellungen → Geräte & Dienste → Shelly → Gerät → Entitäten | `fenster-lichter-uebersicht-karte.yaml`, `garten-karte.yaml`, `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`, `lichter-raum-karte.yaml`, `lichter-slider-karte.yaml` |
| `fin_passat`, `fin_touran` | Fahrgestellnummer in der Entity-ID: V2 (`volkswagencarnet`) mit voller FIN, V3 (`vag_connect`) mit deren letzten 6 Stellen | Einstellungen → Geräte & Dienste → Integration des Fahrzeugs → Gerät → Entitäten | `autos-animation.html`, `autos-karte-v4.yaml`, `autos-karten-v2.html`; in `archiv/`: `autos-karte-v2.yaml`, `autos-karte-v3.yaml` |
| `ieee_adresse` | IEEE-Adresse des Zigbee-Geräts (`0x…`), solange die Entity nicht umbenannt ist | Einstellungen → Geräte & Dienste → Zigbee-Integration → Gerät | `pflanzen-view.yaml`; in `archiv/`: `pflanzen-flower-karte.yaml` |
| `kind_1`, `kind_2` | Vorname eines Kindes in der Entity-ID (`sensor.temperatur_kind_1_*`, `light.kind_2`, `light.kinderzimmer_kind_2_namenslicht`); `1`/`2` entsprechen den Anzeigenamen „Kinderzimmer 1“/„Kinderzimmer 2“ | Einstellungen → Geräte & Dienste → Entitäten, nach Raum oder Gerät suchen | `fenster-lichter-uebersicht-karte.yaml`, `homematic-view.yaml`, `kameras-view.yaml`, `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`, `lichter-raum-karte.yaml`, `lichter-slider-karte.yaml`, `temperaturen-karte-v2.yaml`; in `archiv/`: `temperaturen-karte.yaml` |
| `weather.wohnort` | Wetter-Entity des Wohnorts (Vorhersage, Bedingung fürs Icon) | Einstellungen → Geräte & Dienste → Deutscher Wetterdienst (HACS, `dwd_weather`) → Station → Entität `weather.*` | `welcome-banner-karte.yaml`, `wetter-karte-v2.yaml`; in `archiv/`: `wetter-karte.yaml` |
| `sensor.warnregion_*` | Sensoren der DWD-Wetterwarnungen (`…_aktuelle_warnstufe`, `…_vorwarnstufe`); `warnregion` steht für den Namen der Warnregion | Einstellungen → Geräte & Dienste → DWD Weather Warnings → Region → Entitäten | `meteoalarm-karte.yaml`, `warnlage-templates.yaml`, `wetter-view.yaml` |
| `benutzer_id_1`, `benutzer_id_2` | ID eines Home-Assistant-Benutzers in `visible:` (View) und `condition: user` (Karte); `1` und `2` trennen zwei Benutzer. Unersetzt sind die betroffenen Views und Karten für niemanden sichtbar | View- bzw. Karteneditor → *Sichtbarkeit* → Benutzer auswählen, Home Assistant setzt die ID selbst ein | `gesundheit-view.yaml`, `kameras-view.yaml`, `navbar-karte.yaml`, `navigation-templates.yaml`, `netzwerk-view.yaml`; in `archiv/`: `kameras-karte.yaml` |
<!-- platzhalter:end -->

Nicht anonymisiert, aber an die eigene Instanz gebunden: die Entitäten in
`unifi-netzplan-karte.yaml`, also die `device_tracker` der
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
- dass die Übersichten im README und in `dashboard/README.md` zu den Kopfblöcken passen (`ci/gen_index.py`)
- dass geänderte Template-Bibliotheken ihre `VERSION` erhöhen (`ci/check_template_version.py`)
- Grafana-JSON sowie den Abgleich mit `proxmox_dashboards.py`
- Secrets mit `gitleaks`

Neue `custom:`-Karte im Repo? Kartentyp in `ci/known_cards.txt` eintragen.
Lokal ausführen und Details: [ci/README.md](ci/README.md). Mit
[pre-commit](https://pre-commit.com/) laufen dieselben Prüfungen vor jedem Commit:

```bash
pip install pre-commit && pre-commit install
```

## Mitarbeiten

Regeln für neue und geänderte Dateien: [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Lizenz

[MIT](LICENSE) – Kopieren, Anpassen und Weitergeben ausdrücklich erwünscht,
solange der Lizenzhinweis erhalten bleibt.
