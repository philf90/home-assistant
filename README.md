<picture>
  <source media="(prefers-color-scheme: dark)" srcset="design/banner-dunkel.svg">
  <img alt="Nachtblau-Dashboard: Karten, Views und Grafana-Dashboards für Home Assistant" src="design/banner-hell.svg">
</picture>

# Home Assistant – Nachtblau-Dashboard

Lovelace-Karten, komplette Dashboard-Views und Grafana-Dashboards für meine
Home-Assistant-Instanz. Alle Karten folgen einem gemeinsamen Design, dem
**Nachtblau-Stil**: dunkler Navy-Grund, Pastell-Akzente und Icon-Kacheln, die
sich nach Zustand färben. Die Farben stehen als Palette in
[`design/palette.yaml`](design/palette.yaml), dazu gibt es ein Theme mit hellem
und dunklem Modus.

> **Hinweis:** Die Dateien sind auf eine konkrete Instanz zugeschnitten.
> Entity-IDs, Gerätenamen, Routen und Pfade müssen vor dem Einsatz an die
> eigene Installation angepasst werden. Persönliche Angaben sind durch
> Platzhalter ersetzt, die in keiner Instanz existieren – siehe
> [Platzhalter ersetzen](#platzhalter-ersetzen).

**Auf dieser Seite:**
[Voraussetzungen](#voraussetzungen) ·
[Installation](#installation) ·
[Integrationen einrichten](#integrationen-einrichten) ·
[Platzhalter ersetzen](#platzhalter-ersetzen) ·
[Nachtblau-Stil](#nachtblau-stil) ·
[Inhalt](#inhalt) ·
[Grafana](#grafana) ·
[Notizen](#notizen) ·
[Prüfungen](#prüfungen) ·
[Mitarbeiten](#mitarbeiten) ·
[Lizenz](#lizenz)

## Voraussetzungen

Welche Karten, Templates und Platzhalter eine Datei braucht, steht in ihrem
Kopfblock (Zeilen `Karten`, `Templates`, `Platzhalter`), Integrationen, Helfer
und Sensoren im Kommentar darunter in der Zeile `Voraussetzung`. Die Listen
hier fassen das für alle aktuellen Dateien zusammen.

### Für alle Karten

- Home Assistant mit [HACS](https://hacs.xyz/)
- aus HACS die Frontend-Karten **`button-card`** (Version 7, getestet mit
  7.0.1) und **`card-mod`**. Fast jede Karte nutzt `button-card`, die meisten
  auch `card-mod`.
- ein Browser bzw. eine App-WebView mit `color-mix()`: ab Chrome/WebView 111,
  Safari 16.2 oder Firefox 113

### Je nach Datei

| HACS-Frontend-Karte | genutzt von (aktuelle Dateien) |
|---|---|
| `decluttering-card` | allen Views (Templates aus `navigation-templates.yaml`), Pflanzen und Kameras |
| `apexcharts-card` (ab v2.0, getestet 2.2.3) | Energie-Monatsbilanz, Tanken, Flugradar, Gesundheit, Pflanzen, UniFi-Leitungen und -Verlauf, Docker-Verlauf, WoW-Spielwelt |
| `auto-entities` | Docker-Karten, Energie-Monatsbilanz |
| `bubble-card` | Flugradar- und Fußball-View, `wlan-karte-v2.yaml` |
| `expander-card` | Docker-Karten, `unifi-verlauf-karte.yaml` |
| `uptime-card` | `system-karte.yaml`, `unifi-verlauf-karte.yaml` |
| `navbar-card` | `navbar-karte.yaml`, `navigation-templates.yaml` |
| `mushroom` (entity, light) | `lichter-mushroom-karte.yaml` |
| `slider-button-card` | `lichter-slider-karte.yaml` |

Dazu:

- **`browser_mod`** (HACS-Integration) für Popups und das More-Menü der
  Navigationsleiste: Navigation, Wetter, Warnlage und Pollen, Tanken und
  Fahrzeiten, Pflanzen, Kameras, WoW
- **WebRTC Camera** (HACS-Integration, bringt die Karte `webrtc-camera` mit)
  für die Kamera-View
- **`unifi-netzplan-card.js`** für den UniFi-Netzplan; die Karte liegt im
  Repo und wird als Dashboard-Ressource eingebunden, nicht über HACS
  ([Installation](#installation), Schritt 5)
- **Icon-Sets** für die Navigation sowie einzelne Icons in den Licht-,
  Garten-, Wetter- und Homematic-Dateien:
  - `phu:` aus [Custom brand icons](https://github.com/elax46/custom-brand-icons)
    (HACS, Frontend)
  - `bi:` (Bootstrap Icons), `fa6-solid:` (Font Awesome 6 Solid) und
    `flat-ui:` (Flat UI Icons) aus [Iconify](https://iconify.design/) über die
    Integration [Custom Icons](https://github.com/thomasloven/hass-custom_icons)
    (HACS). Nach der Einrichtung unter Einstellungen → Geräte & Dienste →
    Custom Icons → *Konfigurieren* einmal *Download* wählen und die drei Sets
    aktivieren, dann den Browser neu laden.
- **Home Assistant 2026.7 oder neuer** für `wachmodus-konfig.yaml` (neue
  Trigger und Bedingungen)

Nur noch Fassungen in `archiv/` nutzen `flower-card`,
`homematicip-system-health-card`, `mushroom-vacuum-card`,
`power-flow-card-plus`, `sankey-chart`, `trash-card` und
`xiaomi-vacuum-map-card`.

### Integrationen

Jede Karte zeigt die Daten einer Integration. Welche, steht im Kopf der
Datei; die Übersicht nach Bereich:

| Bereich | Integrationen |
|---|---|
| `allgemein/` | Deutscher Wetterdienst (`dwd_weather`, HACS) für das Wetter im Begrüßungsbanner |
| `energie/` | Anker Solix (`thomluther/ha-anker-solix`, HACS) für die PV-/Solarbank-Anlage |
| `klima/` | Deutscher Wetterdienst (`dwd_weather`, HACS), DWD Weather Warnings (`dwd_weather_warnings`), DWD Pollenflug (HACS), Wetterstation Homematic IP HmIP-SWO-PR |
| `licht/` | Shelly, Time & Date (`sensor.time`) |
| `hausgeraete/` | Home Connect Alt (`ekutner/home-connect-hass`, HACS), nicht das offizielle Home Connect: die Entity-IDs mit `bsh_common` stammen von ihr |
| `netzwerk/` | UniFi Network, [UniFi WAN](#unifi-wan) (optional), [UniFi UNAS](#unifi-unas-pro), [Arcane](#arcane-docker), Homematic(IP) Local for OpenCCU (HACS), Uptime Kuma |
| `fahrzeuge/` | VW Group Connect (`vag_connect`), Tankerkönig, Waze Travel Time, Time & Date |
| `garten/` | Home Assistant Plant (`Olen/homeassistant-plant`, HACS), Zigbee, Shelly |
| `personen/` | Owlet Smart Sock (`LucasVollebergh/owlet`, HACS), Companion App |
| `flugradar/` | Flightradar24 (HACS) |
| `fussball/` | keine: Daten von OpenLigaDB direkt im Browser, ESPN über das Paket `fussball-espn-konfig.yaml`; Companion App für die Meldungen |
| `sicherheit/` | Homematic(IP) Local, UniFi Protect, UniFi Access, UniFi Network, Backup, Telegram Bot, Companion App |
| `sonstiges/` | UniFi Protect und WebRTC Camera (Kameras), [Claude Usage](#claude-usage) (HACS), WoW Charakter (`philf90/HA-WOW`, HACS, ab 0.3.0; welche Karte eine neuere Version braucht, steht in ihrem Kopf), Kalender des Abfallentsorgers (Müllabfuhr) |

Einige Karten brauchen zusätzlich Helfer, Template-Sensoren oder
Automationen. Sie stehen im Kopfkommentar der Datei, meist zum Kopieren.

## Installation

Die Schritte gelten für jede Datei; welche davon nötig sind, zeigt ihr
Kopfblock. Die Zeile `Einfuegen` nennt, wohin die Datei gehört.

1. **HACS-Karten und -Integrationen installieren**, die die Datei in
   `Karten` und `Voraussetzung` nennt (siehe [Voraussetzungen](#voraussetzungen)).
   Die Integrationen der Geräte einrichten; Hinweise zu einzelnen stehen
   unter [Integrationen einrichten](#integrationen-einrichten).
2. **Theme einrichten (empfohlen).** Die Karten lesen ihre Farben als
   CSS-Variablen (`var(--nachtblau-gruen, #a6d49e)`) mit dem dunklen
   Palettenwert als Rückfall. Ohne Theme sind sie also dunkel; erst das
   Theme `nachtblau` bringt den hellen Modus und färbt auch den
   Seitenhintergrund passend.
   1. [`nachtblau-theme-konfig.yaml`](dashboard/allgemein/nachtblau-theme-konfig.yaml)
      als `/config/themes/nachtblau.yaml` ablegen.
   2. In der `configuration.yaml` die Themes einbinden, falls noch nicht
      geschehen:

      ```yaml
      frontend:
        themes: !include_dir_merge_named themes
      ```

   3. Aktion `frontend.reload_themes` ausführen oder Home Assistant neu
      starten.
   4. Im Profil das Theme „nachtblau“ wählen oder für alle mit der Aktion
      `frontend.set_theme` (`name: nachtblau`) als Standard setzen. Hell
      oder dunkel wählt jeder Benutzer im Profil (System, Hell, Dunkel).

   Nicht umgestellt und damit in beiden Modi dunkel sind nur die
   Lichter-Varianten `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`
   und `lichter-slider-karte.yaml`.
3. **Templates einfügen.** Viele Karten und alle Views nutzen gemeinsame
   Templates. Sie gehören einmalig in den Raw-Konfigurationseditor des
   Dashboards (Dashboard bearbeiten → ⋮ → *Raw-Konfigurationseditor*), auf
   oberster Ebene neben `views:`. Existiert der Block schon, nur die Einträge
   darunter ergänzen.
   - unter `decluttering_templates:` aus `navigation-templates.yaml`,
     `pflanzen-templates.yaml` und `kameras-templates.yaml`
   - unter `button_card_templates:` aus allen übrigen `*-templates.yaml`:
     `energie-templates.yaml`, `autos-templates.yaml`,
     `fahrzeiten-templates.yaml`, `tanken-templates.yaml`,
     `flugradar-templates.yaml`, `fussball-templates.yaml`,
     `hausgeraete-templates.yaml`, `heizung-templates.yaml`,
     `warnlage-templates.yaml`, `wetter-templates.yaml`,
     `docker-templates.yaml`, `sicherheit-templates.yaml`,
     `wow-templates.yaml`

   Welche Templates eine Karte braucht, steht in ihrer Zeile `Templates`.
4. **Platzhalter ersetzen.** Unverändert eingefügt bleibt eine Karte leer
   oder meldet „Entität nicht verfügbar“. Vorgehen von Hand oder mit Claude:
   [Platzhalter ersetzen](#platzhalter-ersetzen).
5. **Datei einfügen**, je nach Art:
   - **Karte** (`-karte`): Dashboard bearbeiten → Karte hinzufügen →
     *Manuell* → Inhalt der YAML-Datei einfügen.
   - **View** (`-view`): im Raw-Konfigurationseditor unter `views:`
     einfügen. `wetter-view.yaml`, `docker-view.yaml` und
     `netzwerk-view.yaml` binden ihre Karten per `!include` ein; das
     versteht nur ein Dashboard im YAML-Modus. Dafür die View zusammen mit
     den Karten, die sie einbindet, in einen Ordner im Konfigurationsordner
     kopieren, z. B. `dashboard/netzwerk/`, und das Dashboard in der
     `configuration.yaml` anlegen (der Schlüssel muss einen Bindestrich
     enthalten):

     ```yaml
     lovelace:
       dashboards:
         heim-dashboard:
           mode: yaml
           filename: heim.yaml
           title: Heim
     ```

     In `heim.yaml` stehen dann die Templates aus Schritt 3 und die Views:

     ```yaml
     views:
       - !include dashboard/netzwerk/netzwerk-view.yaml
     ```

     Der Pfad ist relativ zur Datei, die das `!include` enthält; die
     Includes in der View selbst zeigen auf Dateien im selben Ordner.
     Alternativ die eingebundenen Karten an Stelle der `!include`-Zeilen
     einsetzen.
   - **Konfiguration** (`-konfig`): gehört in die `configuration.yaml`. Die
     Pakete `docker-konfig.yaml`, `unifi-kabel-clients-konfig.yaml`,
     `fussball-espn-konfig.yaml`, `fussball-meldungen-konfig.yaml` und
     `wachmodus-konfig.yaml` unter `homeassistant: packages:`, z. B.:

     ```yaml
     homeassistant:
       packages:
         docker: !include dashboard/netzwerk/docker-konfig.yaml
     ```

     Die Template-Sensoren aus `autos-passat-konfig.yaml` direkt unter
     `template:`:

     ```yaml
     template: !include dashboard/fahrzeuge/autos-passat-konfig.yaml
     ```

     Danach Home Assistant neu starten. Das Theme
     `nachtblau-theme-konfig.yaml` ist in Schritt 2 beschrieben.
   - **Ressource** (`unifi-netzplan-card.js`): nach
     `/config/www/unifi-netzplan-card.js` kopieren, dann Einstellungen →
     Dashboards → *Ressourcen* → Ressource hinzufügen: URL
     `/local/unifi-netzplan-card.js`, Typ *JavaScript-Modul*. Danach
     `unifi-netzplan-karte.yaml` als Karte einfügen. Vor Home Assistant
     2026.6 sind die Ressourcen nur mit dem *Erweiterten Modus* im
     Benutzerprofil sichtbar; seit 2026.6 gibt es den Modus nicht mehr.
6. **Prüfen:** Unter Einstellungen → Werkzeuge → Zustände stichprobenartig
   nachsehen, ob die Entitäten der Karte existieren (vor Home Assistant
   2026.8 hieß der Bereich „Entwicklerwerkzeuge“). Zeigt Lovelace „Custom
   element doesn't exist“, fehlt eine HACS-Karte oder die Ressource.

Die Karten sind für Handys gebaut (360 px Breite wie Galaxy S25, gegengeprüft
bei 402 px wie iPhone 17 Pro, siehe [`DESIGN.md`](DESIGN.md), Abschnitt
„Bildschirmbreiten“).

## Integrationen einrichten

Hinweise zu Integrationen, deren Einrichtung über den Standarddialog
hinausgeht.

### UniFi WAN

Optional für den UniFi-Netzplan und `unifi-leitungen-karte.yaml`: die
Integration [UniFi WAN](https://github.com/holdestmade/Unifi-WAN). Sie liefert
je Internetleitung IPv4, IPv6 und Erreichbarkeit, die die offizielle
UniFi-Integration nicht bereitstellt. Sie steht nicht im HACS-Standardkatalog:
in HACS unter *Benutzerdefinierte Repositories* mit Typ *Integration*
hinzufügen. Zur Einrichtung braucht sie einen lokalen API-Schlüssel der
UniFi-Konsole (Einstellungen → Control Plane → Integrationen). Den
automatischen Speedtest in ihren Optionen abschalten, sonst testet sie
standardmäßig stündlich.

### Kabel-Clients im UniFi-Netzplan

Optional: das Paket `unifi-kabel-clients-konfig.yaml`. Es fragt alle 5 Minuten
die Controller-API ab und legt `sensor.unifi_kabel_clients` mit Switch und Port
je Kabel-Client an, was die offizielle Integration nicht liefert. Einbinden
unter `homeassistant: packages:` in der `configuration.yaml`; URL und lokaler
API-Schlüssel stehen in der `secrets.yaml` (Details im Dateikopf).

### UniFi UNAS Pro

Für `unifi-unas-pro-karte.yaml`: die Integration
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

### Arcane (Docker)

Für die Docker-Karten (`docker-karte.yaml` und die übrigen `docker-*-karte.yaml`)
und die Docker-View (`docker-view.yaml`): die Integration
[Arcane](https://github.com/ProfessorQuantumUniverse/Arcane-HA)
(HACS-Standardkatalog, ab Home Assistant 2025.2) und eine laufende
[Arcane](https://github.com/getarcaneapp/arcane)-Instanz auf dem
Docker-Host. Home Assistant spricht nur mit der Arcane-API; der
Docker-Socket muss dafür nicht im Netz offen stehen. Einrichtung:

1. In Arcane unter *Settings → API keys* einen Schlüssel anlegen und der
   Rolle dahinter (*Settings → Roles*) die Rechte geben. Anzeigen:
   `environments:list`, `containers:list`, `projects:list`,
   `images:list`, `volumes:list`, `networks:list`, `system:read`;
   Steuern zusätzlich `containers:start`, `containers:stop`,
   `containers:restart`, `containers:redeploy` (Image-Updates
   installieren), `projects:deploy`, `projects:down`,
   `projects:restart`. Für die Docker-View außerdem `system:upgrade`
   (Arcane selbst aktualisieren) und `system:prune` (Ungenutztes
   aufräumen). Welche Rechte fehlen, zeigt die Integration unter
   *Konfigurieren → Berechtigungen des API-Keys*.
2. In HACS *Arcane* herunterladen, Home Assistant neu starten.
3. Einstellungen → Geräte & Dienste → Integration hinzufügen → *Arcane*:
   die Adresse, unter der Arcane direkt erreichbar ist (die Integration
   folgt keinen Weiterleitungen), und den Schlüssel.
4. Nur für die Docker-View: unter *Konfigurieren → Abfrage* „CPU, RAM
   und Festplatte des Hosts“ einschalten und unter *Steuerung* den Prune
   Button auf „Alle ungenutzten Images, Netzwerke und Build Cache“
   stellen; die Diagnose-Sensoren
   Docker-Version, Arcane Version und Host Arbeitsspeicher gesamt
   aktivieren. Ereignisse, Absturzmeldung und „Alle aktualisieren“
   kommen aus dem Paket `docker-konfig.yaml`.

CPU und Arbeitsspeicher je Container liefert die Integration nicht, nur
für den ganzen Host.

### Claude Usage

Für die Claude-Nutzungskarte (`claude-nutzung-karte.yaml`): die Integration
[Claude Usage](https://github.com/trickv/hass-claude-usage)
(HACS-Standardkatalog). Sie liest die Limits eines Claude-Abos (Pro/Max):
Session (5 h), Woche über alle Modelle, Wochenlimits je Modell und
Extra-Nutzung, jeweils mit Auslastung in Prozent und Reset-Zeitpunkt.
Einrichtung: in HACS *Claude Usage* herunterladen, Home Assistant neu
starten, Einstellungen → Geräte & Dienste → Integration hinzufügen →
*Claude Usage*; der angezeigte Link öffnet die Anmeldung bei Anthropic,
danach den Code (Form `xxxx#yyyy`) in den Dialog einfügen. Der
Gerätename trägt Kontoname und Plan, deshalb stehen die Entity-IDs im
Repo als Platzhalter `sensor.claude_usage_konto_*`.

Die Integration fragt den inoffiziellen Endpunkt ab, den auch Claude Code
für `/usage` nutzt; Anthropic dokumentiert ihn nicht, eine offizielle
Schnittstelle für Abo-Limits gibt es nicht. Das Abfrageintervall bei den
voreingestellten 300 s lassen: häufigere Abfragen führen zu einer Sperre
von etwa 24 h, in der auch claude.ai und Claude Code keine Nutzung mehr
anzeigen.

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
| `person.bewohner` | Personen-Entity | Einstellungen → Personen | `fahrzeiten-karte.yaml`, `person-presence-karte.yaml`, `sicherheit-templates.yaml`, `wachmodus-konfig.yaml`, `doku/karten-basemap-carto.md` |
| `sensor.iphone_*` | Sensoren der Companion App; `iphone` steht für den Gerätenamen | Einstellungen → Geräte & Dienste → Mobile App → Gerät | `gesundheit-view.yaml`, `person-presence-karte.yaml` |
| `notify.mobile_app_iphone` | Benachrichtigungen an dasselbe Gerät | Einstellungen → Werkzeuge → Aktionen, Suche `notify.mobile_app_` | `docker-konfig.yaml`, `flugradar-view.yaml`, `fussball-meldungen-konfig.yaml`, `fussball-view.yaml`, `garten-karte.yaml`, `hausgeraete.html`, `wachmodus-konfig.yaml` |
| `<breite>`, `<laenge>` | Koordinaten von Zuhause | Einstellungen → Werkzeuge → Zustände, `zone.home` (Attribute `latitude`, `longitude`) | `flugradar-view.yaml` |
| `sensor.pv_anlage_*` | Sensoren der PV-/Solarbank-Anlage (in Grafana ohne `sensor.`) | Einstellungen → Geräte & Dienste → Integration der Anlage | `energie-flow-karte.yaml`, `energie-monatsbilanz-karte.yaml`, `energie-solarbank-pv-karte.yaml`, `energie-templates.yaml`, `energie-verbraucher-karte.yaml`, `energiefluss.html`, `grafana/README.md`, `grafana/energie-dashboard.json`; in `archiv/`: `energie-autarkie-karte.yaml`, `energie-diagramme-karte.yaml`, `energie-flow-leiste-karte.yaml`, `energie-pv-karte.yaml` |
| `AB - CD 123`, `AB - EF 456` | Kennzeichen, reiner Anzeigetext | – | `autos-animation.html`, `autos-karte-v4.yaml`, `autos-karten-v2.html`, `autos-passat-konfig.yaml`; in `archiv/`: `autos-karte-v2.yaml`, `autos-karte-v3.yaml`, `autos-karte.yaml` |
| `passat_fenster_kombiniert`, `passat_tueren_kombiniert` | `unique_id` der Template-Sensoren | bisherige `unique_id` übernehmen, sonst legt HA neue Entities an | `autos-passat-konfig.yaml` |
| `seriennr_geschirrspueler`, `seriennr_waschmaschine`, `seriennr_trockner` | Seriennummer des Home-Connect-Geräts am Anfang der Entity-ID (`sensor.seriennr_…_bsh_common_…`) | Einstellungen → Geräte & Dienste → Home Connect Alt → Gerät → Entitäten | `geschirrspueler-karte.yaml`, `trockner-karte.yaml`, `waschmaschine-karte.yaml` |
| `*_seriennr`, `*_seriennr_1`, `*_seriennr_2` | Seriennummer des Geräts in der Entity-ID (Homematic IP, Owlet); `_1`/`_2` trennen zwei Geräte desselben Modells | Einstellungen → Geräte & Dienste → Integration → Gerät → Entitäten | `garten-karte.yaml`, `homematic-view.yaml`, `owlet-smart-sock-karte.yaml`, `sicherheit-templates.yaml`, `temperaturen-karte-v2.yaml`, `wachmodus-konfig.yaml`; in `archiv/`: `homematic-karte.yaml`, `temperaturen-karte.yaml` |
| `*_mac` | MAC-Adresse des Shelly-Geräts in der Entity-ID | Einstellungen → Geräte & Dienste → Shelly → Gerät → Entitäten | `garten-karte.yaml`, `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`, `lichter-raum-karte.yaml`, `lichter-slider-karte.yaml`; in `archiv/`: `fenster-lichter-uebersicht-karte.yaml` |
| `fin_passat`, `fin_touran` | Fahrgestellnummer in der Entity-ID: V2 (`volkswagencarnet`) mit voller FIN, V3 (`vag_connect`) mit deren letzten 6 Stellen | Einstellungen → Geräte & Dienste → Integration des Fahrzeugs → Gerät → Entitäten | `autos-animation.html`, `autos-karte-v4.yaml`, `autos-karten-v2.html`; in `archiv/`: `autos-karte-v2.yaml`, `autos-karte-v3.yaml` |
| `ieee_adresse` | IEEE-Adresse des Zigbee-Geräts (`0x…`), solange die Entity nicht umbenannt ist | Einstellungen → Geräte & Dienste → Zigbee-Integration → Gerät | `pflanzen-view.yaml`; in `archiv/`: `pflanzen-flower-karte.yaml` |
| `kind_1`, `kind_2` | Vorname eines Kindes in der Entity-ID (`sensor.temperatur_kind_1_*`, `light.kind_2`, `light.kinderzimmer_kind_2_namenslicht`); `1`/`2` entsprechen den Anzeigenamen „Kinderzimmer 1“/„Kinderzimmer 2“ | Einstellungen → Geräte & Dienste → Entitäten, nach Raum oder Gerät suchen | `homematic-view.yaml`, `kameras-view.yaml`, `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`, `lichter-raum-karte.yaml`, `lichter-slider-karte.yaml`, `sicherheit-templates.yaml`, `temperaturen-karte-v2.yaml`; in `archiv/`: `fenster-lichter-uebersicht-karte.yaml`, `temperaturen-karte.yaml` |
| `weather.wohnort` | Wetter-Entity des Wohnorts (Vorhersage, Bedingung fürs Icon) | Einstellungen → Geräte & Dienste → Deutscher Wetterdienst (HACS, `dwd_weather`) → Station → Entität `weather.*` | `welcome-banner-karte.yaml`, `wetter-karte-v2.yaml`; in `archiv/`: `wetter-karte.yaml` |
| `sensor.warnregion_*` | Sensoren der DWD-Wetterwarnungen (`…_aktuelle_warnstufe`, `…_vorwarnstufe`); `warnregion` steht für den Namen der Warnregion | Einstellungen → Geräte & Dienste → DWD Weather Warnings → Region → Entitäten | `meteoalarm-karte.yaml`, `warnlage-templates.yaml`, `wetter-view.yaml` |
| `wow_charakter` | Charaktername und Realm in den Entity-IDs der HACS-Integration WoW Charakter (`sensor.<charakter>_<realm>_level`, `image.<charakter>_<realm>_avatar`) | Einstellungen → Geräte & Dienste → WoW Charakter → Charakter → Entitäten | `wow-arsenal-karte.yaml`, `wow-berufe-karte.yaml`, `wow-mythic-karte.yaml`, `wow-raid-karte.yaml`, `wow-ruf-karte.yaml`, `wow-sammlung-karte.yaml`, `wow-werte-karte.yaml` |
| `sensor.claude_usage_konto_*` | Sensoren der HACS-Integration Claude Usage (`…_session_usage`, `…_weekly_reset_time`, `…_weekly_<modell>_limit_usage`); `konto` steht für Kontoname und Plan aus dem Gerätenamen (`claude_usage_<name>_<plan>`) | Einstellungen → Geräte & Dienste → Claude Usage → Gerät → Entitäten | `claude-nutzung-karte.yaml`, `claude-nutzung.html` |
| `VG Wohnort` | Verbandsgemeinde im Titel der Abfuhrtermine (`Restmüll in VG Wohnort`). Die trash-card in `muellabfuhr-karte.yaml` (archiv) ordnet die Termine über den vollen Titel den Tonnen zu; `muellabfuhr-karte-v2.yaml` erkennt die Tonne am Stichwort (Bio, Papier, Restmüll …) und nennt den Platzhalter nur im Beispiel im Kopfkommentar | Kalender des Abfallentsorgers (`calendar.mull`) → Titel eines Termins, der Teil nach „in“ | `muellabfuhr-karte-v2.yaml`; in `archiv/`: `muellabfuhr-karte.yaml` |
| `telegram_eintrag` | Config-Entry-ID des Telegram-Bots (`config_entry_id` bei `telegram_bot.send_message`) | Automationseditor → Aktion „Telegram Bot: Nachricht senden“ → Bot auswählen; Home Assistant setzt die ID selbst ein | `wachmodus-konfig.yaml` |
| `sensor.tankstelle_1_*` bis `sensor.tankstelle_4_*`, Name `Tankstelle 1` bis `Tankstelle 4` | Tankstelle aus der Tankerkönig-Integration. HA bildet die Entity-ID aus Marke und Adresse (`sensor.…_diesel`, `…_super`, `…_super_e10`, `binary_sensor.…_status`); der Anzeigename steht frei im Template | Einstellungen → Geräte & Dienste → Tankerkönig → Tankstelle → Entitäten | `tanken-templates.yaml` |
| `benutzer_id_1`, `benutzer_id_2` | ID eines Home-Assistant-Benutzers in `visible:` (View) und `condition: user` (Karte); `1` und `2` trennen zwei Benutzer. Unersetzt sind die betroffenen Views und Karten für niemanden sichtbar | View- bzw. Karteneditor → *Sichtbarkeit* → Benutzer auswählen, Home Assistant setzt die ID selbst ein | `docker-view.yaml`, `gesundheit-view.yaml`, `kameras-view.yaml`, `navbar-karte.yaml`, `navigation-templates.yaml`, `netzwerk-view.yaml`; in `archiv/`: `kameras-karte.yaml` |
| `DEIN_EMBED_KEY` | API-Schlüssel der Google Maps Embed API für die Routenkarte im Popup. Unersetzt zeigt das Popup statt der Karte einen Hinweis | Google Cloud Console → APIs & Dienste → Anmeldedaten; nur für „Maps Embed API“ freigeben und auf die Adressen der Instanz beschränken | `fahrzeiten-karte.yaml`, `fahrzeiten-templates.yaml` |
| `sensor.wlan_heim_clients`, `image.wlan_heim_qr_code`, `switch.wlan_heim_aktiviert`, dasselbe mit `wlan_gast` | Entitäten der UniFi-Integration je WLAN (Sensor „Clients“, Bild „QR-Code“, Schalter „Aktiviert“); HA bildet die ID aus dem Netznamen (SSID), beim Clients-Sensor teils ohne `_clients`. Bild und Schalter legt die Integration nur an, wenn ihr Konto in der Network-App die Site-Rolle admin hat; das Bild ist standardmäßig deaktiviert. Unersetzt bleibt die Karte ohne Code | Einstellungen → Geräte & Dienste → UniFi Network → Gerät des WLANs (Modell „UniFi WLAN“) → Entitäten | `wlan-karte-v2.yaml` |
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
→ `sensor.<eigener_gerätename>_`. Danach unter Einstellungen → Werkzeuge →
Zustände stichprobenartig prüfen, ob die IDs existieren.

**Mit Claude:** Claude Code in diesem Repo starten, die Home-Assistant-
Verbindung (MCP) aktivieren und z. B. sagen: *„Bereite
`gesundheit-view.yaml` für meine Instanz vor.“* Der Projekt-Skill
[`.claude/skills/platzhalter-einsetzen`](.claude/skills/platzhalter-einsetzen/SKILL.md)
sucht die echten IDs in der Instanz, legt die Zuordnung zur Bestätigung vor
und erzeugt eine angepasste Fassung in `lokal/`. Ins Dashboard schreibt Claude
nur nach ausdrücklicher Freigabe.

Die echten Werte gehören nicht ins Repo. `lokal/` ist deshalb in
`.gitignore` eingetragen.

## Nachtblau-Stil

- abgeleitet von der Owlet-Smart-Sock-Karte (`owlet-smart-sock-karte.yaml`)
- gemeinsame Kartenhülle, Palette (Grundtöne `#a6d49e`, `#f2f5f8`, `#6e7988`) und Typografie
- rundlich-quadratische Icon-Kacheln, die sich nach Zustand färben
- umgesetzt fast durchgängig mit `custom:button-card`; Styles werden innerhalb
  einer Datei über YAML-Anker geteilt
- Spezialkarten (Kamera-Stream, Diagramme, Pflanzen …) bleiben
  funktional erhalten und bekommen nur die Nachtblau-Hülle
- verbindlich beschrieben in [`DESIGN.md`](DESIGN.md); die Farbwerte stehen in
  [`design/palette.yaml`](design/palette.yaml) und werden in der CI geprüft
- hieß bis Oktober 2026 „Owlet-Stil“; Umstellung einer bestehenden Instanz:
  [`doku/umbenennung-nachtblau.md`](doku/umbenennung-nachtblau.md)
- Banner oben im README: `design/banner-dunkel.svg` und `design/banner-hell.svg`
  in der Kartenhülle, Farben aus der Palette bzw. dem hellen Theme, die Leiste
  zeigt die Bereichsfarben der oberen Navigation. Die CI prüft SVG-Dateien nicht; ändert
  sich ein Palettenwert, die Banner von Hand nachziehen.
- Social Preview des Repos (Bild für geteilte Links): Quelle
  `design/social-preview.svg`, daraus ein PNG mit 1280 × 640 px rendern
  (Schrift Inter) und von Hand unter Settings → Social preview hochladen. Das
  PNG liegt nicht im Repo, weil die Prüfungen jede Datei als Text lesen.

**Eigene Karten im Nachtblau-Stil:** Farben nur aus der Palette und als
Theme-Variable mit dem dunklen Wert als Rückfall, z. B.
`var(--nachtblau-gruen, #a6d49e)`; Tönungen mit
`color-mix(in srgb, var(--nachtblau-gruen, #a6d49e) 12%, transparent)`.
Welche Farbe welche Rolle hat (Flächen, Text, Status, Akzente) und wie Hülle
und Kacheln aufgebaut sind, steht in [`DESIGN.md`](DESIGN.md). Das Theme
erzeugt `python ci/gen_theme.py` aus der Palette; es wird nicht von Hand
geändert.

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
| [`allgemein/`](dashboard/allgemein/) | `nachtblau-theme-konfig.yaml`, `navbar-karte.yaml`, `navigation-templates.yaml`, `top-navigation-karte.yaml`, `welcome-banner-karte.yaml` | – | `banner-hell.html`, `home-kacheln.html` |
| [`energie/`](dashboard/energie/) | `energie-flow-karte.yaml`, `energie-monatsbilanz-karte.yaml`, `energie-solarbank-pv-karte.yaml`, `energie-templates.yaml`, `energie-verbraucher-karte.yaml`, `energie-zaehler-karte.yaml` | `energie-autarkie-karte.yaml`, `energie-diagramme-karte.yaml`, `energie-flow-leiste-karte.yaml`, `energie-pv-karte.yaml`, `energie-verbrauch-uebersicht-karte.yaml`, `gas-wasser-karte.yaml` | `energiefluss.html` |
| [`klima/`](dashboard/klima/) | `heizung-templates.yaml`, `meteoalarm-karte.yaml`, `pollenflug-karte.yaml`, `temperaturen-karte-v2.yaml`, `thermostate-karte-v3.yaml`, `warnlage-templates.yaml`, `wetter-karte-v2.yaml`, `wetter-templates.yaml`, `wetter-view.yaml` | `temperaturen-karte.yaml`, `thermostate-karte-v2.yaml`, `thermostate-karte.yaml`, `wetter-karte.yaml` | `wetter-animiert.html` |
| [`licht/`](dashboard/licht/) | `fenster-karte.yaml`, `fenster-lichter-karte.yaml`, `haustuer-ereignis-karte.yaml`, `haustuer-lock-karte.yaml`, `lichter-glow-karte.yaml`, `lichter-mushroom-karte.yaml`, `lichter-raum-karte.yaml`, `lichter-slider-karte.yaml` | `fenster-lichter-uebersicht-karte.yaml` | – |
| [`hausgeraete/`](dashboard/hausgeraete/) | `geschirrspueler-karte.yaml`, `hausgeraete-templates.yaml`, `trockner-karte.yaml`, `waschmaschine-karte.yaml` | `staubsauger-karte.yaml` | `hausgeraete.html` |
| [`netzwerk/`](dashboard/netzwerk/) | `docker-container-karte.yaml`, `docker-ereignisse-karte.yaml`, `docker-host-karte.yaml`, `docker-karte.yaml`, `docker-konfig.yaml`, `docker-projekte-karte.yaml`, `docker-speicher-karte.yaml`, `docker-templates.yaml`, `docker-uebersicht-karte.yaml`, `docker-updates-karte.yaml`, `docker-verlauf-karte.yaml`, `docker-view.yaml`, `homematic-view.yaml`, `netzwerk-view.yaml`, `system-karte.yaml`, `unifi-kabel-clients-konfig.yaml`, `unifi-leitungen-karte.yaml`, `unifi-netzplan-card.js`, `unifi-netzplan-karte.yaml`, `unifi-netzwerk-status-karte.yaml`, `unifi-udm-system-karte-v2.yaml`, `unifi-unas-pro-karte.yaml`, `unifi-verlauf-karte.yaml`, `wlan-karte-v2.yaml` | `homematic-karte.yaml`, `unifi-udm-system-karte.yaml`, `wlan-karte.yaml` | – |
| [`fahrzeuge/`](dashboard/fahrzeuge/) | `autos-karte-v4.yaml`, `autos-passat-konfig.yaml`, `autos-templates.yaml`, `fahrzeiten-karte.yaml`, `fahrzeiten-templates.yaml`, `tanken-karte.yaml`, `tanken-templates.yaml` | `autos-karte-v2.yaml`, `autos-karte-v3.yaml`, `autos-karte.yaml` | `autos-animation.html`, `autos-karten-v2.html` |
| [`garten/`](dashboard/garten/) | `garten-karte.yaml`, `pflanzen-templates.yaml`, `pflanzen-view.yaml` | `pflanzen-flower-karte.yaml`, `pflanzen-status-karte.yaml` | – |
| [`personen/`](dashboard/personen/) | `gesundheit-view.yaml`, `owlet-smart-sock-karte.yaml`, `person-presence-karte.yaml` | – | – |
| [`flugradar/`](dashboard/flugradar/) | `flugradar-templates.yaml`, `flugradar-view.yaml` | – | – |
| [`fussball/`](dashboard/fussball/) | `fussball-espn-konfig.yaml`, `fussball-meldungen-konfig.yaml`, `fussball-templates.yaml`, `fussball-view.yaml` | – | – |
| [`sicherheit/`](dashboard/sicherheit/) | `sicherheit-templates.yaml`, `sicherheit-view.yaml`, `wachmodus-konfig.yaml` | – | – |
| [`sonstiges/`](dashboard/sonstiges/) | `claude-nutzung-karte.yaml`, `kameras-templates.yaml`, `kameras-view.yaml`, `muellabfuhr-karte-v2.yaml`, `wow-arsenal-karte.yaml`, `wow-berufe-karte.yaml`, `wow-charaktere-karte.yaml`, `wow-mythic-karte.yaml`, `wow-raid-karte.yaml`, `wow-ruf-karte.yaml`, `wow-sammlung-karte.yaml`, `wow-spielwelt-karte.yaml`, `wow-templates.yaml`, `wow-werte-karte.yaml` | `kameras-karte.yaml`, `muellabfuhr-karte.yaml` | `claude-nutzung.html` |
| [`grafana/`](grafana/) | `energie-dashboard.json`, `proxmox-pbs-dashboard.json`, `proxmox-ve-dashboard.json` | – | `proxmox-mockups.html`, `proxmox-mockups.md` |
| [`doku/`](doku/) | `karten-basemap-carto.md`, `proxmox-haos-secure-boot-warnung.md`, `proxmox-haos-speicher-erweitern.md`, `umbenennung-2026-10.md`, `umbenennung-nachtblau.md` | – | – |
<!-- index:end -->

Varianten (`lichter-raum-…`, `lichter-glow-…`) sind gleichwertige
Alternativen. Versionen (`-v2`, `-v3`) lösen ihre Vorgängerin ab; die
Vorgängerin liegt dann in `archiv/` und bekommt nur noch Änderungen, die alle
Dateien betreffen (Palette, Anonymisierung). Der Kommentarkopf der neueren
Datei erklärt den Unterschied.

Die HTML-Dateien in den Ordnern `entwuerfe/` sind Design-Entwürfe und werden
direkt im Browser geöffnet.

Jede Datei beginnt mit einem festen Kopfblock: Art, Bereich, Status, die
genutzten HACS-Karten (**Karten**), die nötigen Templates mit ihrer Datei
(**Templates**), wie sie eingefügt wird (**Einfuegen**) und ihre
**Platzhalter**. Integrationen und weitere Voraussetzungen stehen im Text
darunter unter **Voraussetzung**. Aufbau: [`ci/README.md`](ci/README.md),
Abschnitt „Dateikopf“.

## Grafana

| Dashboard | UID | Datenquelle | Doku |
|---|---|---|---|
| `energie-dashboard.json` | `ha-energie` | InfluxDB 2 | [grafana/README.md](grafana/README.md) |
| `proxmox-ve-dashboard.json` | `proxmox-ve` | InfluxDB 2 | [grafana/proxmox-dashboards.md](grafana/proxmox-dashboards.md) |
| `proxmox-pbs-dashboard.json` | `proxmox-pbs` | InfluxDB 2 + PBS-API (Infinity) | [grafana/proxmox-dashboards.md](grafana/proxmox-dashboards.md) |

Voraussetzungen und Import beschreibt die Doku je Dashboard. Dazu:

- `ha_statistics_backfill.py` überträgt vorhandene Langzeitstatistiken aus
  Home Assistant nach InfluxDB 2, damit das Energie-Dashboard auch rückwirkend
  Daten zeigt.
- `proxmox_dashboards.py` erzeugt die beiden Proxmox-Dashboards. Änderungen
  gehören in den Generator, nicht ins JSON.

## Notizen

- [`umbenennung-2026-10.md`](doku/umbenennung-2026-10.md) – alte Dateinamen
  und ihr neuer Ort nach dem Umzug in die Bereichsordner
- [`umbenennung-nachtblau.md`](doku/umbenennung-nachtblau.md) – Umstellung
  einer bestehenden Instanz vom Owlet- auf den Nachtblau-Stil
- [`karten-basemap-carto.md`](doku/karten-basemap-carto.md) – „API KEY REQUIRED“
  auf allen Karten im Frontend
- [`proxmox-haos-secure-boot-warnung.md`](doku/proxmox-haos-secure-boot-warnung.md) –
  Proxmox-Warnung `ms-cert=2023k` beim Start der HA-VM
- [`proxmox-haos-speicher-erweitern.md`](doku/proxmox-haos-speicher-erweitern.md) –
  Festplatte von Home Assistant OS unter Proxmox vergrößern

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
- dass das Theme zur Palette passt (`ci/gen_theme.py`)
- Farben nur aus der Palette (`ci/check_palette.py`) und einen Teil der Regeln für Handybreiten (`ci/check_mobil.py`)
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
