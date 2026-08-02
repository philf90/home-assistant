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

### Datenmodell vor dem Bau prüfen

Die Feldnamen unterscheiden sich zwischen PVE-Versionen. Einmal im Influx-Data-Explorer:

```flux
import "influxdata/influxdb/schema"

schema.measurements(bucket: "proxmox")
schema.fieldKeys(bucket: "proxmox", predicate: (r) => r._measurement == "cpustat")
schema.tagKeys(bucket: "proxmox",   predicate: (r) => r._measurement == "system")
```

Die im Mockup angenommenen Measurements, Tags und Felder stehen vollständig in der
HTML-Datei im Abschnitt *Datenmodell*.

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

## Inhalt der Dashboards

**Proxmox VE**

* *Node-Status* – acht Stat-Kacheln: Erreichbarkeit, Uptime, CPU, RAM, Load, IO-Wait,
  laufende Gäste, Root-Dateisystem
* *Auslastung des Nodes* – CPU nach Typ (gestapelt), RAM inkl. ZFS ARC als eigene
  Fläche, Load Average mit Schwellenlinie auf der Thread-Zahl, Pressure Stall,
  Netzwerkdurchsatz
* *Storage* – Belegung je Storage als Bar Gauge, Disk-Durchsatz, ARC-Größe und eine
  Tabelle **Storage-Reichweite** mit Ø Zuwachs pro Tag und Restlaufzeit
* *Gäste* – Tabelle aller VMs und Container mit CPU, RAM, Disk- und Netz-IO, dazu CPU-
  und RAM-Verlauf der Top 4
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
