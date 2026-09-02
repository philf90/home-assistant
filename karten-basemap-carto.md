# Karten in Home Assistant: "API KEY REQUIRED" von CARTO

Betrifft: **jede** Karte im Frontend – Personen-Dialog (`more-info`), Karten-Karte
(`type: map`), Karten-Dashboard, Zonen-Editor, Geräte-Tracker.
Stand dieser Notiz: 2026-09-02, Instanz auf **Core 2026.8.3 / HA OS 18.2**.

## Symptom

Über den Kartenkacheln steht diagonal `API KEY REQUIRED` und
`carto.com/basemaps/apikey`. Die Karte funktioniert weiterhin (zoomen, Marker,
Zonen) – der Text ist von CARTO **direkt in die Kachel-Bilder gerendert**, also
kein Fehler der eigenen Installation. Cache leeren, App neu installieren oder
HACS-Karten aktualisieren ändert deshalb nichts.

## Ursache

Bis einschließlich Core 2026.8.3 holt das Frontend die Hintergrundkarte fest
verdrahtet von CARTO:

```
https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png
```

(Quelle: `src/common/dom/setup-leaflet-map.ts` im Frontend-Release `20260729.7`,
das zu Core 2026.8.3 gehört.)

CARTO verlangt seit August 2026 für diese Raster-Basemaps einen API-Key und
brennt ohne Key das Wasserzeichen in die Kacheln. Da die URL im
JavaScript-Bundle steht, gibt es in 2026.8.3 **kein Eingabefeld, keine Option
in `configuration.yaml` und keinen Schalter in den Einstellungen**, um einen Key
zu hinterlegen.

Gemeldet als [core#180277](https://github.com/home-assistant/core/issues/180277),
[core#180818](https://github.com/home-assistant/core/issues/180818) und
[frontend#53800](https://github.com/home-assistant/frontend/issues/53800).

## Lösung: Update auf Core 2026.9

Home Assistant hat CARTO ersetzt – PR
[frontend#53816](https://github.com/home-assistant/frontend/pull/53816)
"Replace CARTO raster tiles with OpenStreetMap vector tiles".

Neu ist die System-Integration **`map_tiles`** (`ha_release: 2026.9`), die
OpenStreetMap-Vektorkacheln über die eigene HA-Instanz proxyt und im RAM cacht
(max. 32 MB). Laut Doku: *"This integration is automatically loaded by Home
Assistant and requires no configuration."*

* Kein API-Key, keine Registrierung, nichts einzutragen.
* Enthalten ab `2026.9.0b9` (Core-Abhängigkeit `home-assistant-frontend==20260826.4`).
* Update über **Einstellungen → System → Updates → Home Assistant Core**.

Technische Details der neuen Lösung (aus `homeassistant/components/map_tiles/`):

| Punkt | Wert |
|---|---|
| Vektorkacheln | `https://vector.openstreetmap.org` (Shortbread-Style) |
| Raster-Fallback | `https://tile.openstreetmap.org` |
| Zugriffsschutz | rotierendes Token (`map_tiles/access_token`, Wechsel alle 30 min) |
| Cache | In-Memory, 32 MB, Kacheln 7 Tage |

### Voraussetzungen nach dem Update

1. **Ausgehende Verbindung vom HA-Server** (nicht mehr nur vom Browser!) nach
   `vector.openstreetmap.org` und `tile.openstreetmap.org`, jeweils TCP 443.
   Bei restriktiver Firewall/DNS-Filterung in der UniFi freigeben.
2. **WebGL2 im Browser** für die Vektorkarte; fehlt es (alte Tablets, iOS < 15),
   schaltet HA automatisch auf Raster-Kacheln um.
3. Das Kartenbild sieht danach anders aus – OSM-Stil statt CARTO "Voyager",
   Dark Mode über einen eigenen Style statt CSS-Invertierung.

### Vor dem Update: Speicherplatz prüfen

Die Instanz ist mit **27,3 von 30,8 GB** belegt (≈ 3,5 GB frei). Ein Core-Update
zieht ein neues Container-Image und legt vorher ein Backup an. Reserve schaffen:

* Alte Backups löschen – vorhanden sind u. a. `core_2024.12.4` (531 MB) und
  `core_2024.12.3` (488 MB) von Dezember 2024 sowie fünf automatische Backups
  à ≈ 1,3 GB.
* Recorder-Datenbank: aktuell ≈ 3,1 GB (SQLite). Ggf. `purge_keep_days` senken.

## Übergangslösung, falls kein Update möglich

Der CARTO-Key ist kostenlos: Anfrage über
<https://carto.com/basemaps/apikey/>. Kein CARTO-Konto nötig, es werden
E-Mail-Adresse, die Domain, auf der die Karten laufen, und der Verwendungszweck
abgefragt; der Key kommt sofort per Mail. Fair-Use-Grenze ≈ 5 Mio.
Kachelabrufe/Monat. Angehängt wird er als Query-Parameter:

```
https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=DEIN_KEY
```

(Genaue Schreibweise so verwenden, wie CARTO sie in der Bestätigungsmail nennt.)

**Wichtige Einschränkung:** In HA 2026.8.3 gibt es keinen Ort, an dem dieser Key
für die eingebaute Karte hinterlegt werden kann. Nutzbar ist er nur mit einer
Custom-Karte, z. B. `map-card` ([nathan-gs/ha-map-card](https://github.com/nathan-gs/ha-map-card),
in HACS verfügbar):

```yaml
type: custom:map-card
entities:
  - person.philipp
tile_layer_url: https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=DEIN_KEY
tile_layer_attribution: >-
  &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>,
  &copy; <a href="https://carto.com/attributions">CARTO</a>
```

Ganz ohne Key geht auch direkt OpenStreetMap – das ist derselbe Anbieter, den
2026.9 verwendet:

```yaml
tile_layer_url: https://tile.openstreetmap.org/{z}/{x}/{y}.png
```

Das ersetzt aber nur Karten auf Dashboards. Der Kartenausschnitt im
Personen-Dialog aus dem Screenshot bleibt CARTO und behält das Wasserzeichen,
weil er fest im Frontend steckt. Deshalb ist das Update der einzige vollständige
Weg.

CARTO baut Raster- auf Vektorkacheln um; die Raster-Basemaps laufen langfristig
aus. Eine CARTO-Lösung wäre also ohnehin nur eine Zwischenstation.
