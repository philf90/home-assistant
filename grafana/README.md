# Grafana-Dashboard: Energie – Home Assistant

`energie-dashboard.json` ist ein fertiges Grafana-Dashboard, das die Energiedaten aus
Home Assistant aus einer **InfluxDB-2**-Datenquelle auswertet. Es deckt Strom (Netzbezug,
PV, Autarkie, Kosten), die zehn gemessenen Einzelverbraucher und Gas ab. Wasser ist
bewusst nicht enthalten.

Alle verwendeten Panel-Typen sind in **Grafana OSS (kostenlos)** enthalten.

## Voraussetzung

Die `influxdb`-Integration in Home Assistant muss die Energiesensoren nach InfluxDB 2
schreiben. Erwartetes Datenmodell (Standard der Integration mit
`measurement_attr: unit_of_measurement`):

| Element | Wert |
|---|---|
| `_measurement` | die Einheit, also `kWh`, `W`, `m³` |
| `_field` | `value` |
| Tag `entity_id` | Entity **ohne** Domain-Präfix, z. B. `pool_energy` |
| Tag `domain` | `sensor` |

Minimalkonfiguration in `configuration.yaml`:

```yaml
influxdb:
  api_version: 2
  host: !secret influxdb_host
  port: 8086
  ssl: false
  verify_ssl: false
  organization: !secret influxdb_org
  bucket: !secret influxdb_bucket
  token: !secret influxdb_token
  max_retries: 3
  precision: s
  measurement_attr: unit_of_measurement
  tags:
    source: hass
  tags_attributes:
    - friendly_name
    - device_class
  include:
    entities:
      - sensor.hmip_esi_stromzahler_energiezahler_ch2
      - sensor.hmip_esi_gaszahler_gas_volumen
      - sensor.system_muhlweg_tagliche_pv_1
      - sensor.system_muhlweg_tagliche_pv_2
      - sensor.smart_meter_netzbezug
      - sensor.shelly_plugs_gen3_waschmaschine_switch_0_energy
      - sensor.shelly_plugs_gen3_trockner_switch_0_energy
      - sensor.shelly_plugs_kuhlschrank_switch_0_energy
      - sensor.shelly_plugs_spulmaschine_switch_0_energy
      - sensor.stromverbrauch_poe_power_daily
      - sensor.garten_energy
      - sensor.pool_energy
      - sensor.garage_energy
      - sensor.shelly_plus_1pm_heizung_switch_0_energy
      - sensor.shelly_outdoor_plugs_pool_switch_0_energy
```

Die `include`-Whitelist ist wichtig – ohne sie schreibt Home Assistant jede Entity nach
Influx. Nach dem Eintragen ist ein **Neustart** von Home Assistant nötig, die Integration
ist nicht reload-fähig.

## Import in Grafana

1. **Dashboards → New → Import**
2. `energie-dashboard.json` hochladen oder den Inhalt einfügen
3. Import bestätigen
4. Oben prüfen, dass die Variable **Datenquelle** auf `influxdb-homeassistant` steht

Die Dashboard-UID ist `ha-energie`. Ein erneuter Import mit derselben UID überschreibt
das Dashboard, statt ein zweites anzulegen.

## Variablen

| Variable | Standard | Bedeutung |
|---|---|---|
| `DS` | `influxdb-homeassistant` | InfluxDB-2-Datasource |
| `bucket` | `homeassistant` | Influx-Bucket |
| `price_kwh` | `0.3223` | Arbeitspreis Strom in €/kWh |
| `price_gas` | `0.111` | Arbeitspreis Gas in €/m³ |
| `res` | `auto` | Aggregationsfenster der Verlaufsdiagramme |
| `m_energy` | `kWh` | Measurement-Name für Energie (versteckt) |
| `m_power` | `W` | Measurement-Name für Leistung (versteckt) |
| `m_gas` | `m³` | Measurement-Name für Gas (versteckt) |

Die drei Preise und Measurement-Namen sind bewusst als Variablen ausgeführt: Bei einer
Tarifänderung reicht eine Anpassung oben im Dashboard, es muss keine Query editiert
werden. Die versteckten `m_*`-Variablen findest du unter
**Dashboard settings → Variables**; sie sind nur relevant, falls du in Home Assistant
`measurement_attr: entity_id` statt `unit_of_measurement` konfiguriert hast.

## Inhalt

**⚡ Live & Heute** – aktuelle Netzleistung (Stat mit Sparkline), Netzbezug, PV-Ertrag,
Hausverbrauch und Stromkosten des laufenden Tages, Autarkiegrad als Gauge.

**📈 Verlauf & Lastprofil** – Leistungsverlauf (Timeseries mit Schwellenlinien),
Leistungsverteilung (Histogram), Energiebilanz je Tag (gestapelte Barchart),
Energiemix (Donut), Lastprofil (Heatmap).

**🔌 Einzelverbraucher** – Verbrauch je Gerät (Bar Gauge im LCD-Modus), Anteil je Gerät
(Pie Chart), Detailtabelle mit Verbrauch, Kosten und Anteil inkl. Summenzeile,
Tagesverbrauch aller Geräte gestapelt.

**🔥 Gas** – Verbrauch und Kosten heute und im Zeitraum, beide Zählerstände,
Tagesverbrauch (Barchart) und Zählerstandsverlauf.

**ℹ️ Kennzahlen, Daten & Hinweise** – Ø Netzbezug pro Tag, Summen und Autarkie über den
gewählten Zeitraum, Tabelle zur Datenqualität (Alter des letzten Messwerts je Sensor)
und ein Text-Panel mit der Erklärung des Rechenwegs.

## Rechenweg

Alle Energiesensoren sind Zählerstände (`total_increasing` bzw. `total`). Der Verbrauch
entsteht durch Differenzbildung – genau wie es die Energie-View in Home Assistant mit den
Langzeitstatistiken tut:

* **Zählerstände** (`increase()` / `difference()`) – `increase()` bügelt Zähler-Resets
  glatt, z. B. wenn ein Shelly neu startet.
* **Tagesgrenzen** liegen dank
  `option location = timezone.location(name: "Europe/Berlin")` auf lokaler Mitternacht,
  nicht auf UTC-Mitternacht.
* **Tagesdiagramme** fragen intern zwei Tage mehr ab und filtern anschließend zurück,
  damit auch der erste Tag des Zeitraums einen vollständigen Differenzwert bekommt.

## Bekannte Einschränkungen

* Die beiden PV-Sensoren sind **Tageszähler** und werden über das Tagesmaximum
  ausgewertet, nicht über eine Differenz.
* In der Energie-Konfiguration ist **keine Einspeisung** hinterlegt. Der Autarkiegrad
  geht deshalb davon aus, dass die gesamte PV-Erzeugung selbst verbraucht wird, und
  Hausverbrauch = Netzbezug + PV.
* Die Summe der Einzelverbraucher ist kleiner als der Hausverbrauch, weil nicht alle
  Verbraucher gemessen werden.
* Die Daten beginnen mit der Aktivierung der `influxdb`-Integration. Es gibt **keine
  rückwirkende Historie** – die bestehenden Langzeitstatistiken aus Home Assistant
  werden nicht automatisch übertragen. Dafür gibt es `ha_statistics_backfill.py`
  (siehe unten).
* Der Dashboard-Link „Home Assistant – Energie" zeigt auf
  `http://homeassistant.local:8123/energy` und muss ggf. unter
  **Dashboard settings → Links** angepasst werden.

## Anpassen

Das JSON wurde mit einem Generator-Skript erzeugt, kann aber problemlos direkt in der
Grafana-UI weiterbearbeitet werden. Kommen weitere Verbraucher dazu, müssen sie an drei
Stellen ergänzt werden: in der `include`-Liste in `configuration.yaml` sowie in den
`names`- und `devices`-Blöcken am Anfang der Queries der Panels *Verbrauch je Gerät*,
*Detailtabelle* und *Geräteverbrauch je Tag*.

---

# Backfill: `ha_statistics_backfill.py`

Überträgt die bereits vorhandenen **Langzeitstatistiken** aus Home Assistant nach
InfluxDB 2, damit das Dashboard auch rückwirkend Daten zeigt. Ohne Backfill beginnen
die Kurven erst mit der Aktivierung der `influxdb`-Integration.

Das Skript liest über die WebSocket-API `recorder/statistics_during_period` und schreibt
die Werte im **exakt gleichen Datenmodell**, das die Integration live verwendet.

## Installation

```bash
pip install websocket-client
```

Das ist die einzige Abhängigkeit – der Rest ist Python-Standardbibliothek. Getestet mit
Python 3.9+.

## Token besorgen

**Home Assistant:** Profil → ganz unten → *Long-Lived Access Tokens* → *Create Token*.

**InfluxDB:** *Load Data → API Tokens*. Der Token braucht **Lese- und Schreibrecht** auf
den Bucket – Lesen für den Tag-Abgleich vor dem Schreiben.

## Verwendung

Zugangsdaten am besten als Umgebungsvariablen setzen, damit sie nicht in der
Shell-History landen:

```bash
export HA_URL=http://homeassistant.local:8123
export HA_TOKEN='eyJhbGciOi...'
export INFLUX_URL=http://192.168.1.50:8086
export INFLUX_TOKEN='abcDEF...=='
export INFLUX_ORG=meine-org
export INFLUX_BUCKET=homeassistant
```

**Schritt 1 – Verbindung und Datenmodell prüfen** (schreibt nichts):

```bash
python3 ha_statistics_backfill.py --check-only --exclude sensor.watermeter_value
```

**Schritt 2 – Probelauf** (zählt die Punkte, schreibt nichts):

```bash
python3 ha_statistics_backfill.py \
    --start 2023-01-01 \
    --exclude sensor.watermeter_value \
    --dry-run
```

**Schritt 3 – echter Lauf:**

```bash
python3 ha_statistics_backfill.py \
    --start 2023-01-01 \
    --exclude sensor.watermeter_value
```

Ein erneuter Lauf mit denselben Parametern ist **unschädlich**: InfluxDB überschreibt
Punkte mit identischem Measurement, Tag-Satz und Zeitstempel, es entstehen keine
Duplikate.

## Wichtige Optionen

| Option | Bedeutung |
|---|---|
| `--entity ENTITY_ID` | Nur diese Entity, mehrfach angebbar. Ohne Angabe wird die Energie-Konfiguration von HA ausgelesen. |
| `--exclude ENTITY_ID` | Entity ausschließen, mehrfach angebbar |
| `--start`, `--end` | Zeitraum, z. B. `2023-01-01`. Standard: letzte 3 Jahre bis jetzt. |
| `--period` | `5minute`, `hour` (Standard), `day`, `month` |
| `--tag K=V` | Statischer Tag, muss zum Block `tags:` der Integration passen (Standard `source=hass`) |
| `--tag-attribute ATTR` | Attribut als Tag, muss zu `tags_attributes:` passen (Standard `friendly_name`, `device_class`) |
| `--dry-run` | Nichts schreiben, nur zählen |
| `--check-only` | Nur Verbindung und Tag-Abgleich prüfen |
| `--no-check` | Tag-Abgleich überspringen |
| `--chunk-days N` | Größe der Abfragefenster, Standard 30 |
| `--insecure` | TLS-Zertifikate nicht prüfen |

Vollständige Hilfe: `python3 ha_statistics_backfill.py --help`

## Der Tag-Abgleich

Vor dem Schreiben vergleicht das Skript die geplanten Tags mit einem echten Live-Punkt
aus dem Bucket. **Das ist die wichtigste Sicherung des Skripts.**

Weicht auch nur ein Tag ab – etwa weil in `configuration.yaml` ein anderer
`tags_attributes`-Block steht – entstehen in InfluxDB **zwei getrennte Serien für
dieselbe Entity**. `increase()` und `difference()` im Dashboard laufen dann pro Serie und
springen genau an der Nahtstelle zwischen Backfill und Live-Daten. Der Fehler fällt erst
Wochen später auf.

Findet das Skript eine Abweichung, bricht es ab und zeigt die Differenz an:

```
  ! sensor.pool_energy
      Tag friendly_name: live='Sonos Pool' geplant='Pool energy'
```

Passe dann `--tag` / `--tag-attribute` an die `influxdb`-Konfiguration an. Ist der Bucket
noch leer, weil die Integration noch nicht läuft, wird der Abgleich übersprungen – dann
solltest du die Integration vorher aktivieren, damit es etwas zum Vergleichen gibt.

## Welcher Wert wird geschrieben

| Sensortyp | Statistikfeld | Beispiel |
|---|---|---|
| Zählerstände (`has_sum`) | `state` – der reale Zählerstand am Ende der Stunde | Netzbezug, Gas, PV, alle Shellys |
| Messwerte (`has_mean`) | `mean` – Stundenmittelwert | `sensor.smart_meter_netzbezug` (W) |

Bewusst **nicht** das Feld `sum`: Das Dashboard bildet die Differenz selbst, genau wie
bei den Live-Daten. `state` ist derselbe Wert, den die Integration live geschrieben
hätte – dadurch passen Backfill und Live-Daten lückenlos aneinander.

Der Zeitstempel ist der **Beginn** der Statistikperiode. Damit liefert
`aggregateWindow(every: 1d, fn: last)` im Dashboard den Zählerstand um Mitternacht und
die Tagesdifferenzen stimmen exakt.

## Einschränkungen des Backfills

* **Auflösung:** Langzeitstatistiken sind stündlich. Der Leistungsverlauf, das Histogram
  und die Heatmap wirken im Backfill-Zeitraum deutlich gröber als bei Live-Daten.
  `--period 5minute` geht nur für die letzten Tage – HA hält Kurzzeitstatistiken nur
  begrenzt vor.
* **Keine Einheitenumrechnung:** Weicht `statistics_unit_of_measurement` von der
  aktuellen `unit_of_measurement` der Entity ab (z. B. weil ein Sensor früher in Wh
  gemeldet hat), warnt das Skript und schreibt den Wert unverändert.
* **Überlappung mit Live-Daten:** Backfill und laufende Integration können sich zeitlich
  überschneiden, das schadet nicht. Wenn du es sauber trennen willst, setze `--end` auf
  den Zeitpunkt, ab dem die Integration schreibt.
* Entities ohne Langzeitstatistik oder ohne `unit_of_measurement` werden mit Hinweis
  übersprungen.
