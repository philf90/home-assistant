# Grafana-Dashboards: Proxmox VE und Proxmox Backup Server

Zwei importfertige Dashboards für **Grafana OSS**:

| Datei | UID | Datenquellen |
|---|---|---|
| `proxmox-ve-dashboard.json` | `proxmox-ve` | InfluxDB 2 |
| `proxmox-pbs-dashboard.json` | `proxmox-pbs` | InfluxDB 2 **und** PBS-API über Infinity |

Erzeugt werden sie von `proxmox_dashboards.py`. Das JSON lässt sich danach problemlos
in der Grafana-UI weiterbearbeiten – wer den Generator nutzt, sollte Änderungen aber
dort nachziehen, sonst gehen sie beim nächsten Lauf verloren.

```bash
cd grafana && python3 proxmox_dashboards.py
```

Alle Queries sind gegen ein reales Datenmodell geprüft, nicht gegen die Dokumentation.
Die Feldnamen unterscheiden sich zwischen PVE- und PBS-Versionen; die Fallstricke sind
in `proxmox-mockups.md` dokumentiert und stehen zusätzlich als Panel-Beschreibung an
jedem betroffenen Panel (Mauszeiger auf das ⓘ im Panel-Titel).

## Voraussetzungen

### Beide Systeme: Metric Server

`Datacenter → Metric Server` (PVE) bzw. `Configuration → Metric Server` (PBS),
Typ **InfluxDB**, Protokoll **HTTP** (nicht UDP), Intervall 10 s.

**Getrennte Buckets verwenden.** Die Dashboards gehen von `proxmox` und
`proxmox-backup` aus – beides ist oben im Dashboard als Variable änderbar.

### Nur PBS: Infinity-Plugin und API-Token

Task-, Snapshot- und GC-Daten liefert der Metric Server **nicht**. Dafür braucht es
das Plugin `yesoreyeram-infinity-datasource`:

```yaml
environment:
  GF_PLUGINS_PREINSTALL: yesoreyeram-infinity-datasource
```

Am PBS unter `Configuration → Access Control` einen Token anlegen und ihm im Reiter
**Permissions** die Rolle `Audit` auf dem Pfad `/` mit *Propagate* zuweisen.

> Mit aktiver **Privilege Separation** – der Voreinstellung – hat ein frisch angelegter
> Token **keinerlei** Rechte, bis diese Zuweisung existiert. Auch dann nicht, wenn er
> auf `root@pam` läuft. Das ist die häufigste Ursache für `403`.

Warum `Audit` auf `/` und nicht enger: Die Dashboards brauchen `/admin/datastore/...`
**und** `/nodes/localhost/tasks`. Ein `DatastoreAudit` auf `/datastore` deckt die Tasks
nicht ab. `Audit` ist rein lesend.

In Grafana die Infinity-Datenquelle so konfigurieren:

| Abschnitt | Feld | Wert |
|---|---|---|
| URL, Headers & Params | Base URL | `https://<pbs>:8007` |
| Authentication | Auth type | `API Key` |
| | Key | `Authorization` |
| | Value | `PBSAPIToken=<user>@<realm>!<token>:<secret>` |
| | Add to | `Header` |
| Security | Allowed hosts | `https://<pbs>:8007` |
| Network | Skip TLS Verify | an (selbstsigniertes Zertifikat) |

Drei Stolpersteine:

* Zwischen Token-ID und Secret steht ein **Doppelpunkt**. Bei Proxmox VE ist an
  derselben Stelle ein Gleichheitszeichen – wer von einem PVE-Beispiel abschreibt,
  landet bei „no authentication credentials provided".
* **Allowed hosts ist Pflicht**, sobald eine Authentifizierung konfiguriert ist.
* Als Auth type **`API Key`** wählen, nicht `Bearer Token`. Bei Bearer sendet Infinity
  `Authorization: Bearer PBSAPIToken=…`, damit kann PBS nichts anfangen.

### Wenn die API-Panels leer bleiben

**Zuerst den Custom Health Check aktivieren.** Ohne ihn prüft Infinity beim
*Save & test* die Zugangsdaten überhaupt nicht – ein grünes „Data source is working"
bedeutet dann nur, dass das Plugin geladen ist. Unter **Health check** →
*Enable custom health check*, URL `https://<pbs>:8007/api2/json/version`. Ab da ist
grün eine echte Aussage, und man kann Änderungen einzeln durchprobieren, ohne ins
Dashboard zu wechseln.

Der Statuscode sagt, wo der Fehler sitzt:

| Code | Bedeutung |
|---|---|
| **401** | PBS konnte nicht authentifizieren. Der Header fehlt, ist unvollständig oder das Secret ist veraltet. Die Verbindung selbst steht – URL, TLS und Allowed hosts sind in Ordnung, sonst käme kein HTTP-Status zurück. |
| **403** | Authentifiziert, aber ohne Rechte. Das ist die fehlende ACL-Zuweisung bei aktiver Privilege Separation. |
| kein Statuscode | Die Anfrage kommt gar nicht an: falscher Host, TLS-Fehler oder fehlender Allowed-hosts-Eintrag. |

Den Token an der Authentication-Sektion vorbei testen: Unter **Health check** →
*Add header* einen Header `Authorization` mit dem vollständigen `PBSAPIToken=…`-Wert
eintragen. Wird der Check damit grün, stimmt der Token und der Fehler liegt in der
Authentication-Sektion. Bleibt er rot, ist der Token selbst das Problem.

## Import

**Dashboards → New → Import**, Datei hochladen, bestätigen. Danach oben die Variablen
prüfen. Ein erneuter Import mit derselben UID überschreibt das Dashboard, statt ein
zweites anzulegen.

## Variablen

**Proxmox VE**

| Variable | Bedeutung |
|---|---|
| `DS` | InfluxDB-2-Datenquelle |
| `bucket` | Influx-Bucket, Standard `proxmox` |
| `node` | Node, aus `object=nodes` ermittelt |
| `nic` | Uplink-Interface. Vorgefiltert auf `en*`, `eth*`, `bond*`, `vmbr*` |
| `guest` | Gast-Auswahl für die drei Gast-Diagramme, mehrfach wählbar |

Die `nic`-Variable ist kein Komfort, sondern nötig: Ein PVE-Node meldet neben dem
Uplink auch `vmbr0`, die VLAN-Interfaces und je Gast ein Quartett aus `tap*`, `fwbr*`,
`fwln*` und `fwpr*`. Ohne Filter summiert das Netzwerk-Panel denselben Verkehr mehrfach.

**Proxmox Backup Server**

| Variable | Bedeutung |
|---|---|
| `DS` | InfluxDB-2-Datenquelle |
| `DS_API` | Infinity-Datenquelle gegen die PBS-API |
| `bucket_pbs` | Influx-Bucket, Standard `proxmox-backup` |
| `datastore` | Datastore für die Snapshot-Tabelle |
| `nic_pbs` | Interface, vorgefiltert auf `en*`, `eth*`, `bond*` |

## Inhalt

### Proxmox VE

* **Node** – Erreichbarkeit, Uptime, CPU, RAM, Load, IO-Wartezeit, laufende Gäste,
  Wurzeldateisystem
* **Auslastung** – CPU (`cpu` und `wait`), Arbeitsspeicher mit ZFS ARC als eigener
  Stapelfläche, Load Average mit datengetriebener Schwellenlinie aus `cpustat.cpus`,
  Netzwerk, ARC gegen `arcmax`
* **Storage** – Belegung je Storage, Auslastungsverlauf in Prozent, Wurzeldateisystem,
  Storage-Tabelle mit Typ und Füllstand
* **Gäste** – Tabelle aller Gäste mit CPU, RAM, Host-RAM, IO und Status, dazu CPU, RAM
  und **IO-Pressure** je Gast
* **Diagnose** – Datenaktualität je Quelle, Lesehilfe

### Proxmox Backup Server

* **Backup-Lage** – letztes erfolgreiches Backup, fehlgeschlagene Tasks,
  Dedup-Faktor, prognostiziertes Volllaufdatum, defekte Chunks, ausstehender GC-Platz
* **Datastore** – Belegung, Verlauf, täglicher Zuwachs, Statustabelle
* **Backup-Jobs** – Task-Historie mit berechneter Dauer, Snapshot-Tabelle mit
  Verifikationsstatus, Backup-Dauer je Ziel
* **PBS-Host** – CPU, RAM, Load, Disk-Durchsatz, Netzwerk
* **Diagnose** – Datenaktualität, Grenzen des Dashboards

## Entscheidungen, die im JSON stecken

* **Die Volllauf-Prognose kommt von PBS selbst.** `estimated-full-date` aus
  `/api2/json/status/datastore-usage` ist belastbarer als eine lineare Fortschreibung
  über die letzten Tage, weil PBS die eigene Verlaufskurve kennt. Eine selbstgebaute
  Regression kann daneben liegen, sobald ein Garbage-Collect ins Fenster fällt.
* **Der Dedup-Faktor wird nicht aus der Snapshot-Liste gerechnet.**
  `gc-status.index-data-bytes / gc-status.disk-bytes` steht fertig in derselben
  Antwort.
* **Defekte Chunks als eigene Kachel.** `gc-status.still-bad` zählt Chunks, die der
  letzte Garbage-Collect als beschädigt erkannt und nicht reparieren konnte. Alles
  über 0 bedeutet beschädigte Backups – die Zahl steht in keinem Standard-Dashboard
  und ist die einzige, die stille Datenkorruption sichtbar macht.
* **„Letztes Backup" filtert auf `worker_type = backup` und `status = OK`.** Ohne
  beide Filter zeigt die Kachel den letzten beliebigen Task – auch einen `logrotate` –
  und behauptet damit ein Backup, das es nicht gab.
* **Schwellenfarben stehen nie allein**, überall daneben der Wert oder ein Statuswort.
* **Ein Panel „Datenaktualität" pro Dashboard.** Der häufigste Fehlerfall ist nicht
  die kaputte VM, sondern der Metric Server, der seit Tagen nichts mehr schreibt –
  während Grafana unbeirrt den letzten bekannten Wert anzeigt.
* **Keine Dual-Axis-Panels.** Wo zwei Größen unterschiedlich skalieren, stehen zwei
  Panels nebeneinander oder es wird auf Prozent normiert.

## Vorgeschlagene Alarme

| Regel | Bedingung | Warum |
|---|---|---|
| Kein Backup | jüngster `backup`-Task mit `status=OK` älter als 36 h | fängt auch „Job läuft, schlägt aber still fehl" |
| Defekte Chunks | `gc-status.still-bad` > 0 | stille Datenkorruption |
| Datastore-Reichweite | `estimated-full-date` weniger als 21 Tage entfernt | Vorwarnzeit für neue Platten |
| Verifikation | Snapshot ohne `verification.state = ok` älter als 14 Tage | ein unverifiziertes Backup ist eine Vermutung |
| Metrik-Stille | letzter Datenpunkt `object=nodes` älter als 5 min | erkennt Node-Ausfall *und* kaputte Metrikkette |
| Kein Sync | kein `sync`-Task in 7 Tagen | erkennt, dass es keine zweite Kopie gibt |
| IO-Pressure | `pressureiosome` eines Gastes > 15 % für 10 min | zeigt überlastete Platten früher als SMART |

## Bekannte Grenzen

* **Disk-Durchsatz des PVE-Nodes ist nicht darstellbar.** `blockstat` ist dort ein
  `statfs` des Wurzeldateisystems, kein IO-Zähler. Wer echten Durchsatz braucht,
  kommt an Telegraf mit `[[inputs.diskio]]` auf dem Node nicht vorbei.
* **PSI gibt es nur je Gast, nicht für den Node.** Für den Node bleibt `cpustat.wait`.
* **`disk` und `maxdisk` sind bei QEMU-VMs stets 0** – eine Spalte „Disk-Belegung je
  Gast" ist für VMs nicht befüllbar.
* **PBS schreibt kein `uptime`.**
* **SMART-Werte** liefert weder Influx noch die API. Dafür braucht es `smartctl` plus
  Telegraf auf dem jeweiligen Host.
* **`object=lxc` ist ungetestet.** Auf dem Referenzsystem laufen ausschließlich
  QEMU-VMs. Die Queries filtern auf `qemu` *oder* `lxc`, sollten also funktionieren –
  geprüft ist es nicht.
* **Restore-Tests** kann kein Dashboard ersetzen.
