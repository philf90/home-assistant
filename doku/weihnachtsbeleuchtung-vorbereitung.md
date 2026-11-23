# Weihnachten: Beleuchtung mit vier Shelly Plug M Gen3

Betrifft: vier neue Shelly Plug M Gen3 im Wohnzimmer, einer für den
Tannenbaum, drei für die Fensterbeleuchtung. Sie ersetzen den Hue Smart Plug
`light.hue_smart_plug_1` („Tannenbaum“). Er ist aus der Hue-Bridge, aus der
Instanz und aus allen Lichter-Karten entfernt, auch aus dem Archiv.
Stand dieser Notiz: 2026-11-23. Regeln: `CONTRIBUTING.md`, Abschnitt
„Labels, Bereiche und Kategorien“; Register: `design/labels.yaml`.

## Stand in der Instanz

Eingerichtet am 2026-11-23. Alle vier Geräte liegen im Bereich Wohnzimmer und
tragen am **Gerät** die Labels `licht` und `weihnachten`; die Entitäten selbst
tragen keine Labels. Nicht `fenster`: das ist der Gerätetyp für
Fensterkontakte.

| Gerät | Licht (`switch_as_x`) | Schalter (ausgeblendet) |
|---|---|---|
| Weihnachtsbeleuchtung Tannenbaum | `light.weihnachtsbeleuchtung_tannenbaum` | `switch.weihnachtsbeleuchtung_tannenbaum` |
| Weihnachtsbeleuchtung Fenster WZ links | `light.weihnachtsbeleuchtung_fenster_wz_links` | `switch.weihnachtsbeleuchtung_fenster_wz_links` |
| Weihnachtsbeleuchtung Fenster WZ rechts | `light.weihnachtsbeleuchtung_fenster_wz_rechts` | `switch.weihnachtsbeleuchtung_fenster_wz_rechts` |
| Weihnachtsbeleuchtung Fenster WZ Hof | `light.weihnachtsbeleuchtung_fenster_wz_hof` | `switch.weihnachtsbeleuchtung_fenster_wz_hof` |

- **Schalter als Licht:** je Stecker ein Helfer „Schalter als anderer
  Entitätstyp“ mit Typ Licht, wie bei der Lichterkette im Garten. Der Helfer
  blendet den Schalter aus; Automationen und Karten nutzen die
  `light.*`-Entität.
- **Gruppe `light.weihnachtsfenster`** („Weihnachtsfenster“): Gruppen-Helfer,
  Typ Licht, mit den drei Fenster-Lichtern, `all: false` (an, sobald eines an
  ist). Bereich Wohnzimmer, Label `weihnachten` an der Gruppen-Entität, wie
  `licht` an `light.alle_lichter`.
- **Alle Lichter:** Die vier Lichter sind Mitglieder von `light.alle_lichter`
  (jetzt 15); `sensor.lichter_an` zählt sie mit.

## Ziele für Automationen

Ein Ziel mit Bereich und Label ergibt die **Vereinigung**, nicht die
Schnittmenge. Deshalb gibt es für die Fenster eine Gruppe statt eines
weiteren Labels.

| Ziel | Erfasst |
|---|---|
| `label_id: weihnachten` | alle vier Lichter (über die Geräte) und die Gruppe |
| Gruppe Weihnachtsfenster | die drei Fenster-Lichter |
| `light.*` des Tannenbaums | nur den Baum |

Automationen heißen `Weihnachten: …`, bekommen Kategorie `Steuerung`, Label
`weihnachten` und Bereich Wohnzimmer, solange sie nur das Wohnzimmer betreffen.

Templates, die mit `label_devices('weihnachten')` und `label_entities()` zählen
(Muster aus `CONTRIBUTING.md`, Regel 6), erfassen auch die Gruppe. Wer Lichter
zählt, nimmt Gruppen mit `entity_id`-Attribut heraus.

## Automationen

Seit 2026-11-23, beide mit Kategorie `Steuerung`, Label `weihnachten`,
Bereich Wohnzimmer. Ziel ist `label_id: weihnachten`, also Baum und Fenster.

| Automation | Auslöser | Bedingung |
|---|---|---|
| `automation.weihnachten_beleuchtung_bei_dammerung_an` | `illuminance.crossed_threshold` auf `sensor.wetterstation_pro_beleuchtungsstarke`, unter der Schwelle, 10 min lang; dazu 14:00, Neustart und Rückfall 20 min nach Sonnenuntergang (`id: rueckfall`) | Saison an, 14:00 bis 22:30 und Helligkeit unter der Schwelle (`illuminance.is_value`); beim Rückfall ohne Helligkeit |
| `automation.weihnachten_beleuchtung_um_22_30_aus` | 22:30 | – |
| `automation.weihnachten_saison_umschalten` | `input_boolean.weihnachtssaison` an oder aus (nicht aus `unavailable`/`unknown`); Neustart | – (siehe Hauptschalter) |

- **Schwelle** im Helfer `input_number.weihnachten_einschalt_helligkeit`
  (Kategorie Einstellung, 0 bis 500 lx), eingestellt auf **50 lx**. Der
  Helfer braucht die Einheit `lx`, sonst reagieren Auslöser und Bedingung
  nicht.
- Die Auslöser 14:00 und Neustart holen das Einschalten nach, wenn es dann
  schon dunkel ist; ohne sie bliebe das Licht aus, wenn die Schwelle vor
  14:00 oder während eines Neustarts unterschritten wird. Ein Neustart
  zwischen 14:00 und 22:30 schaltet deshalb auch Licht wieder ein, das von
  Hand ausgeschaltet wurde.
- Der Auslöser übergeht Wechsel, die von `unavailable` ausgehen. Ein
  `unavailable` während der 10 Minuten bricht die Wartezeit ab, und die
  Rückkehr unter die Schwelle zählt nicht als neues Unterschreiten; ohne
  Rückfall bliebe das Licht dann aus (nachgelesen in HA-Core,
  `homeassistant/helpers/trigger/entity_trigger.py`, Stand 23.11.2026). Das
  Gerät war vom 13. bis 23.11. 39-mal kurz `unavailable` (im Mittel rund
  70 s), am 23.11. viermal zwischen 16:18 und 16:29.
- **Rückfall:** 20 min nach Sonnenuntergang schaltet die Automation ein, ohne
  die Helligkeit zu prüfen, damit auch ein gerade ausgefallener Sensor nicht
  blockiert. Zu diesem Zeitpunkt zeigte der Sensor vom 18. bis 23.11.
  höchstens 4,2 lx. Wer das Licht davor von Hand ausschaltet, bekommt es zum
  Rückfall wieder eingeschaltet.

### Warum 50 lx

Der Sensor misst am Standort deutlich weniger als freier Himmel: Zum
Sonnenuntergang (23.11. etwa 16:37) zeigt er zwischen 1 und rund 90 lx, eine
halbe Stunde später rund 0,1 lx. Erste Zeit, ab der der Wert unter der Schwelle blieb
(Verlauf 18. bis 23.11.):

| Tag | 100 lx | 50 lx | 20 lx |
|---|---|---|---|
| 23.11. | 16:30 | 16:37 | 16:42 |
| 22.11. | 16:16 | 16:24 | 16:29 |
| 21.11. | 16:32 | 16:37 | 16:41 |
| 20.11. | 16:23 | 16:31 | 16:33 |
| 19.11. | 16:18 | 16:28 | 16:31 |
| 18.11. | 16:38 | 16:45 | 16:51 |

Mit 10 Minuten Wartezeit schalten 50 lx an klaren Tagen zwischen etwa
16:34 und 16:55 ein, also mit dem Sonnenuntergang. Kurze Einbrüche unter
50 lx (20.11. 15:46 bis 15:50, 18.11. 16:18 bis 16:26) lösen nicht aus;
100 lx hätte am 20.11. schon um 15:48 eingeschaltet. An trüben Tagen kommt
das Licht früher: Am 9.11. lag der Stundenmittelwert 15 bis 16 Uhr bei 45 lx,
am 16.11. 16 bis 17 Uhr bei 17 lx.

## Hauptschalter

Seit 2026-11-23 schaltet `input_boolean.weihnachtssaison` (Name
„Weihnachtssaison“, Kategorie Einstellung, Label `weihnachten`, kein
`initial`) die Saison. Er wird nur von Hand gesetzt; Plan und Entscheidungen
stehen im Dokument „Plan: Hauptschalter Weihnachtsbeleuchtung“.

| Stelle | Saison an | Saison aus |
|---|---|---|
| beide Weihnachts-Automationen | aktiviert | deaktiviert (`automation.turn_off`, `stop_actions: true`) |
| Baum und Fenster beim Umschalten | an, wenn es zwischen 14:00 und 22:30 dunkel ist | sofort aus |
| Raum-Reiter-Karte, Wohnzimmer | Schalter Tannenbaum und Fenster sichtbar und gezählt (Feld `sichtbar`) | ausgeblendet, nicht gezählt |
| `sensor.lichter_an` | zählt die Weihnachtslichter mit | zählt sie nicht |

- **Umschalten:** Die Automation „Weihnachten: Saison umschalten“ (Modus
  `queued`) zielt per `entity_id` auf die beiden Automationen, nicht per
  Label, weil sie das Label selbst trägt. Beim Einschalten startet sie die
  Dämmerungs-Automation mit `skip_condition: false`. Beim Start von Home
  Assistant gleicht sie nur den Zustand der Automationen ab und schaltet kein
  Licht.
- **Sicherheitsbedingung:** Die Dämmerungs-Automation prüft zusätzlich
  „Saison an“, falls jemand sie von Hand aktiviert. Die 22:30-Automation prüft
  den Schalter nicht: Wer ausschaltet, prüft nie.
- **Zählung:** Template-Helfer `sensor.lichter_an` (nur in der Instanz):

  ```jinja
  {% set weih = label_devices('weihnachten') | map('device_entities') | sum(start=[]) | select('match', '^light\.') | list %}
  {% set basis = expand('light.alle_lichter') | map(attribute='entity_id') | reject('in', weih) | list %}
  {% set ids = basis + (weih if is_state('input_boolean.weihnachtssaison', 'on') else []) %}
  {{ expand(ids) | selectattr('state', 'eq', 'on') | list | count }}
  ```

  Die vier Lichter bleiben Mitglieder von `light.alle_lichter`: Die
  Startseiten-Kachel „Licht & Fenster“ schaltet sie in der Saison mit.
- **Schalter im Dashboard:** `dashboard/licht/weihnachten-karte.yaml`, direkt
  unter der Lichter-Karte in der View „Licht & Fenster“, für alle Konten, mit
  Rückfrage.
- **Nicht umgesetzt:** Schalter nach Datum setzen. Der richtige Moment ist der
  Auf- und Abbau der Beleuchtung, kein Datum.

Test am 2026-11-23 um 19:51: Saison aus → beide Automationen `off`, Baum und
Fenster aus, `sensor.lichter_an` von 4 auf 1; Saison an → beide `on`, Baum und
Fenster an (dunkel, vor 22:30), `sensor.lichter_an` 5. Abgleich beim Start
durch Handstart der Umschalt-Automation geprüft, ohne Neustart.

## Noch offen

- Lichter-Karten: Nur die Raum-Reiter-Karte zeigt Baum und Fenster; die
  anderen Varianten führen ihre Lichter einzeln auf.
