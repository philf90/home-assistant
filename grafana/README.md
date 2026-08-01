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
  werden nicht automatisch übertragen.
* Der Dashboard-Link „Home Assistant – Energie" zeigt auf
  `http://homeassistant.local:8123/energy` und muss ggf. unter
  **Dashboard settings → Links** angepasst werden.

## Anpassen

Das JSON wurde mit einem Generator-Skript erzeugt, kann aber problemlos direkt in der
Grafana-UI weiterbearbeitet werden. Kommen weitere Verbraucher dazu, müssen sie an drei
Stellen ergänzt werden: in der `include`-Liste in `configuration.yaml` sowie in den
`names`- und `devices`-Blöcken am Anfang der Queries der Panels *Verbrauch je Gerät*,
*Detailtabelle* und *Geräteverbrauch je Tag*.
