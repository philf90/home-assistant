# Mockups: Grafana-Dashboards für Proxmox VE und Proxmox Backup Server

`proxmox-mockups.html` ist eine einzelne, in sich geschlossene HTML-Datei mit zwei
Dashboard-Entwürfen: **Proxmox Virtual Environment** und **Proxmox Backup Server**.

Es sind **Mockups, keine importierbaren Dashboards**. Die Zahlen sind plausibel
erfunden und werden im Browser deterministisch erzeugt. Aufbau, Panel-Typen und die
hinterlegten Queries entsprechen dem, was mit **Grafana OSS** und einer
**InfluxDB-2**-Datenquelle tatsächlich baubar ist.

## Ansehen

Datei im Browser öffnen – keine Abhängigkeiten, kein Server, keine Netzwerkzugriffe:

```bash
xdg-open grafana/proxmox-mockups.html
```

Bedienung:

| Element | Wirkung |
|---|---|
| Reiter oben | wechselt zwischen VE- und PBS-Dashboard |
| **Query** (erscheint beim Zeigen auf ein Panel) | öffnet die zugehörige Flux-Abfrage bzw. den API-Endpunkt |
| Zeilentitel (*Node-Status*, *Datastores*, …) | klappt die Zeile auf und zu, wie in Grafana |
| Mauszeiger über einem Diagramm | Fadenkreuz mit Tooltip über alle Serien |
| **Dark / Light** oben rechts | schaltet zwischen Grafanas beiden Themes |

Unter den Dashboards steht ein Abschnitt **„Was zum Nachbauen nötig ist"** mit
Datenmodell, API-Konfiguration und Alarmvorschlägen.

## Voraussetzungen für den echten Aufbau

### Metrik-Server (beide Systeme)

`Datacenter → Metric Server` (PVE) bzw. `Configuration → Metric Server` (PBS),
Typ **InfluxDB**:

| Feld | Wert |
|---|---|
| Protocol | `HTTP` – **nicht** UDP, das kann Influx 2 nicht |
| Server / Port | Influx-Host / `8086` |
| Organization / Bucket | z. B. `proxmox` |
| Token | API-Token mit Schreibrecht |
| Interval | `10` s |

Ein **eigener Bucket** ist sinnvoll: Proxmox schreibt mit anderen Tag-Sätzen als die
Home-Assistant-Integration, und eine getrennte Retention hält die Datenbank klein.

### Datenmodell (PVE 9, gegen den Quellcode geprüft)

Tag-Sätze aus `PVE/Status/InfluxDB.pm`, Feldgruppen aus `PVE/Service/pvestatd.pm`.
Der Measurement-Name ist der Name des verschachtelten Schlüssels; flache Schlüssel
landen in `system`.

| Measurement | Tags | Felder (Auswahl) |
|---|---|---|
| `system` | `object=nodes`, `host`=Node | `uptime` |
| `cpustat` | `object=nodes` | `user`, `system`, `iowait`, `idle`, `nice`, `sum`, `wait`, `avg1`, `avg5`, `avg15`, `cpus`, **plus die PSI-Werte** |
| `memory` | `object=nodes` | `memtotal`, `memused`, `memfree`, `memshared`, `memavailable`, `arcsize`, `swap*` |
| `nics` | `object=nodes`, `instance` | `receive`, `transmit` |
| `blockstat` | `object=nodes` | `read_bytes`, `write_bytes`, `read_ios`, `write_ios` |
| `system` | `object=storages`, `nodename`, `host`=Storage-ID, `type` | `total`, `used` |
| `system` | `object=qemu\|lxc`, `vmid`, `nodename`, `host`=Gastname | `cpu`, `maxcpu`, `mem`, `maxmem`, `disk`, `maxdisk`, `netin`, `netout`, `diskread`, `diskwrite`, `uptime`, `status`, `template`, `name` |
| `system` | `object=qemu\|lxc` | `pressurecpusome`, `pressurecpufull`, `pressureiosome`, `pressureiofull`, `pressurememorysome`, `pressurememoryfull` *(ab PVE 9)* |

**Die häufigste Fehlannahme:** Es gibt **kein** Measurement `pressure`. Die PSI-Werte des
Nodes schreibt `pvestatd` direkt in den `cpustat`-Hash, die der Gäste als flache
`pressure*`-Felder nach `system`. Viele fertige Community-Dashboards filtern auf
`_measurement == "pressure"` und zeigen deshalb dauerhaft ein leeres Panel.

Die exakten Feldnamen trotzdem einmal gegenprüfen:

```flux
import "influxdata/influxdb/schema"

schema.measurements(bucket: "proxmox")
schema.fieldKeys(bucket: "proxmox", predicate: (r) => r._measurement == "cpustat")
schema.tagKeys(bucket: "proxmox",   predicate: (r) => r._measurement == "system")
```

### PBS: die entscheidende Lücke

Der PBS-Metric-Server liefert **nur Host- und Datastore-Metriken**. Nicht enthalten sind:

* Task-Ergebnisse, Backup-Dauer, übertragene Datenmenge
* Snapshot-Zahlen, Dedup-Faktor
* Verifikations- und Garbage-Collect-Status

Alle Panels, die im Mockup mit **PBS-API** gekennzeichnet sind, brauchen deshalb eine
zweite Datenquelle: das kostenlose **Infinity**-Plugin gegen die PBS-API, mit einem
API-Token der Rolle `Audit`.

```
URL     https://pbs.example.local:8007
Header  Authorization: PBSAPIToken=grafana@pbs!readonly:<secret>

GET /api2/json/admin/datastore/{store}/status      → Belegung, Zähler, GC-Status
GET /api2/json/admin/datastore/{store}/snapshots   → Snapshots inkl. verification.state
GET /api2/json/nodes/localhost/tasks?limit=200     → Task-Historie
```

SMART-Werte der Platten liefert keine der beiden Quellen. Wer sie im Dashboard will,
braucht `smartctl` plus Telegraf auf dem jeweiligen Host.

## Grafana-Plugins

**Genau ein Plugin ist wirklich nötig.** Alles andere im Mockup läuft mit Bordmitteln
von Grafana OSS.

| Plugin | ID | Wofür hier | Urteil |
|---|---|---|---|
| Infinity | `yesoreyeram-infinity-datasource` | PBS-API: Tasks, Snapshots, Verifikation, Dedup, GC | **Pflicht** – ohne bleibt die halbe PBS-Seite leer. Wird von Grafana Labs selbst gepflegt. |
| Business Text | `marcusolsson-dynamictext-panel` | Task-Historie als HTML/Handlebars statt starrer Tabelle | Nice to have, sobald du JSON aus der PBS-API frei formatieren willst |
| Image Renderer | `grafana-image-renderer` | Graph-Bilder in Alarm-Benachrichtigungen | Sinnvoll bei Alarmen – als **eigener Container**, nicht im Grafana-Image |
| Business Calendar | `marcusolsson-calendar-panel` | Backup-Kalender als Monatsansicht | Optional – *Status history* ist Bordmittel und dichter |
| Business Charts | `volkovlabs-echarts-panel` | Sankey und exotische Formen | Hier kein Anlass – du schreibst ECharts-JSON von Hand |

`GF_INSTALL_PLUGINS` ist seit Grafana 12 abgekündigt, die aktuelle Variable heißt
`GF_PLUGINS_PREINSTALL`:

```yaml
services:
  grafana:
    image: grafana/grafana-oss:latest
    environment:
      GF_PLUGINS_PREINSTALL: yesoreyeram-infinity-datasource,marcusolsson-dynamictext-panel
      GF_RENDERING_SERVER_URL: http://renderer:8081/render
      GF_RENDERING_CALLBACK_URL: http://grafana:3000/
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

  renderer:                       # nur nötig, wenn Alarme Bilder mitschicken sollen
    image: grafana/grafana-image-renderer:latest
    restart: unless-stopped

volumes:
  grafana-data:
```

Version pinnen geht mit `plugin-id@1.2.3`. Das Altverhalten erzwingt man mit
`GF_INSTALL_PLUGINS_FORCE=true` – besser ist die Migration.

Drei häufig nachinstallierte Plugins sind überflüssig geworden:

| Statt Plugin | nimm Bordmittel | im Mockup |
|---|---|---|
| `natel-discrete-panel`, `flant-statusmap-panel` | **State timeline** / **Status history** | Backup-Kalender, Gast-Status über Zeit |
| Trendline- und Forecast-Plugins | Transformation **Trendline** (seit Grafana 12.1 regulär in OSS) | Fortschreibung der Datastore-Belegung |
| `grafana-polystat-panel` | **Canvas** oder **Bar gauge** mit Schwellen | Belegung je Storage, Top-Listen |

## Inhalt der Dashboards

**Proxmox VE**

* *Node-Status* – acht Stat-Kacheln: Erreichbarkeit, Uptime, CPU, RAM, Load, IO-Wait,
  laufende Gäste, Root-Dateisystem
* *Auslastung des Nodes* – CPU nach Typ (gestapelt), RAM inkl. ZFS ARC als eigene
  Fläche, Load Average mit Schwellenlinie auf der Thread-Zahl, Pressure Stall,
  Netzwerkdurchsatz
* *Storage* – Belegung je Storage als Bar Gauge, Disk-Durchsatz, ARC-Größe und eine
  Tabelle **Storage-Reichweite** mit Ø Zuwachs pro Tag und Restlaufzeit
* *Gäste* – Tabelle aller VMs und Container mit CPU, RAM, Disk- und Netz-IO, dazu
  CPU-, RAM- und **IO-Pressure**-Verlauf der Top 4. Der PSI je Gast ist neu ab PVE 9
  und beantwortet als einziges Panel die Frage, *welcher* Gast auf IO wartet.
* *Diagnose* – Datenaktualität je Quelle und ein Textpanel mit Lesehilfe

**Proxmox Backup Server**

* *Backup-Lage* – letztes Backup, Fehler in 24 h, Snapshots, Dedup-Faktor,
  Verifikation, Garbage-Collect
* *Datastores* – Belegung, Verlauf über 30 Tage mit gestrichelter 30-Tage-Fortschreibung,
  täglicher Zuwachs, Reichweiten-Tabelle
* *Backup-Jobs* – Backup-Kalender als Statusmatrix (Ziel × Tag), Backup-Dauer je Ziel,
  Task-Historie, Aufbewahrungsregeln
* *PBS-Host* – CPU, RAM, Load, Disk- und Netzdurchsatz der Maschine selbst
* *Diagnose* – Datenaktualität und die Grenzen des Dashboards

## Gestalterische Entscheidungen

* **Reichweite statt reiner Belegung.** „78 % voll" ist erst dann eine Information, wenn
  danebensteht, dass das in 40 Tagen 100 % sind. Die Prognose ist eine lineare
  Fortschreibung über 14 Tage – simpel genug, um sie in zwei Zeilen zu erklären.
* **Schwellenfarben nie allein.** Grün/Gelb/Rot steht immer neben einer Zahl oder einem
  Statuswort, sonst ist das Dashboard rot-grün-blind nicht lesbar.
* **Serienfarben ≠ Statusfarben.** Blau, Gelb, Grün und Violett sind für Zeitreihen mit
  mehreren Serien reserviert, die Schwellenrampe für Zustände. Die Serienpalette ist
  gegen Farbfehlsichtigkeit und Kontrast geprüft (Grafanas eigene semi-dark-Töne).
* **Ein Panel „Datenaktualität" pro Dashboard.** Der häufigste Fehlerfall ist nicht die
  kaputte VM, sondern der Metric Server, der seit Tagen nichts mehr schreibt – während
  Grafana unbeirrt den letzten bekannten Wert anzeigt.
* **Keine Dual-Axis-Panels.** Zwei Y-Achsen in einem Diagramm erzeugen beliebige
  Scheinkorrelationen. Wo zwei Größen zusammengehören, aber unterschiedlich skalieren,
  stehen zwei Panels nebeneinander.

## Vorgeschlagene Alarme

| Regel | Bedingung |
|---|---|
| Kein Backup | letzter erfolgreicher Backup-Task älter als 36 h |
| Datastore-Reichweite | prognostizierte Restlaufzeit < 21 Tage |
| Verifikation | Snapshot ohne `verify: ok` älter als 14 Tage |
| Metrik-Stille | letzter Datenpunkt `object=nodes` älter als 5 min |
| Storage-Füllstand | belegt > 90 % für 15 min |
| IO-Wait | Node-`iowait` > 15 % für 10 min |

## Nächster Schritt

Aus den Mockups lassen sich importierbare `*.json`-Dashboards erzeugen – analog zu
`energie-dashboard.json`. Sinnvoll ist das erst, wenn das Datenmodell mit
`schema.fieldKeys()` gegen die eigene Influx geprüft ist, weil die Feldnamen je nach
PVE- und PBS-Version abweichen.
