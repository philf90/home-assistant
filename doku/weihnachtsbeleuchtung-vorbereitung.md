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
- **Gruppe `light.weihnachtsbeleuchtung`** („Weihnachtsbeleuchtung“): seit
  2026-11-23, Gruppen-Helfer, Typ Licht, mit allen vier Lichtern direkt (nicht
  über die Fenster-Gruppe), `all: false`, Bereich Wohnzimmer, Label
  `weihnachten`, Icon `mdi:pine-tree`. Gedacht für die Sprachsteuerung,
  Abschnitt „Alexa“; keine Karte schaltet sie.
- **Alle Lichter:** Die vier Lichter sind Mitglieder von `light.alle_lichter`
  (jetzt 15); `sensor.lichter_an` zählt sie mit. Die beiden Gruppen sind nicht
  Mitglied und werden nicht gezählt.

## Ziele für Automationen

Ein Ziel mit Bereich und Label ergibt die **Vereinigung**, nicht die
Schnittmenge. Deshalb gibt es für die Fenster eine Gruppe statt eines
weiteren Labels.

| Ziel | Erfasst |
|---|---|
| `label_id: weihnachten` | alle vier Lichter (über die Geräte) und beide Gruppen |
| Gruppe Weihnachtsbeleuchtung | alle vier Lichter |
| Gruppe Weihnachtsfenster | die drei Fenster-Lichter |
| `light.*` des Tannenbaums | nur den Baum |

Automationen heißen `Weihnachten: …`, bekommen Kategorie `Steuerung`, Label
`weihnachten` und Bereich Wohnzimmer, solange sie nur das Wohnzimmer betreffen.

Templates, die mit `label_devices('weihnachten')` und `label_entities()` zählen
(Muster aus `CONTRIBUTING.md`, Regel 6), erfassen auch die Gruppen. Wer Lichter
zählt, nimmt Gruppen mit `entity_id`-Attribut heraus.

## Automationen

Seit 2026-11-23, alle mit Kategorie `Steuerung`, Label `weihnachten`,
Bereich Wohnzimmer. Ziel ist `label_id: weihnachten`, also Baum und Fenster.

| Automation | Auslöser | Bedingung |
|---|---|---|
| `automation.weihnachten_beleuchtung_bei_dammerung_an` | `illuminance.crossed_threshold` auf `sensor.wetterstation_pro_beleuchtungsstarke`, unter der Schwelle, 10 min lang; dazu 14:00, Neustart und Rückfall 20 min nach Sonnenuntergang (`id: rueckfall`) | Saison an, 14:00 bis 22:30 und Helligkeit unter der Schwelle (`illuminance.is_value`); beim Rückfall und ab 20 min nach Sonnenuntergang ohne Helligkeit |
| `automation.weihnachten_beleuchtung_um_22_30_aus` | 22:30; Neustart | beim Neustart nur zwischen 22:30 und 06:30 |
| `automation.weihnachten_beleuchtung_morgens_an` | 06:30; Neustart | Saison an, 06:30 bis 10:00 und vor Sonnenaufgang oder Helligkeit unter `input_number.weihnachten_ausschalt_helligkeit` |
| `automation.weihnachten_beleuchtung_morgens_aus` | `illuminance.crossed_threshold` über `input_number.weihnachten_ausschalt_helligkeit`, 10 min lang (`id: hell`); Nachholen 60 min nach Sonnenaufgang; spätestens 10:00; Neustart | 06:30 bis 10:00 und Helligkeit über der Schwelle; um 10:00 und bis 14:00 ohne Helligkeit; nach einem Neustart zwischen 14:00 und 20 min nach Sonnenuntergang, wenn die Helligkeit über der **Einschalt**-Schwelle liegt |
| `automation.weihnachten_saison_umschalten` | `input_boolean.weihnachtssaison` an oder aus (nicht aus `unavailable`/`unknown`); Neustart | – (siehe Hauptschalter) |
| `automation.weihnachten_beleuchtung_ausserhalb_der_saison_aus` | eines der vier Lichter wird `on` (Status-Auslöser nur mit `to`); Neustart | Saison aus und mindestens eines der vier Lichter an (siehe Hauptschalter) |

- **Schwelle** im Helfer `input_number.weihnachten_einschalt_helligkeit`
  (Kategorie Einstellung, 0 bis 500 lx), seit 2026-11-27 auf **150 lx**
  (vorher 50 lx, Abschnitt „Warum 150 lx“). Der
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
  Rückfall bliebe das Licht dann aus (nachgelesen im Quellcode von HA-Core, Trigger-Helfer
  `entity_trigger`, Stand 23.11.2026). Das
  Gerät war vom 13. bis 23.11. 39-mal kurz `unavailable` (im Mittel rund
  70 s), am 23.11. viermal zwischen 16:18 und 16:29.
- **Rückfall:** 20 min nach Sonnenuntergang schaltet die Automation ein, ohne
  die Helligkeit zu prüfen, damit auch ein gerade ausgefallener Sensor nicht
  blockiert. Zu diesem Zeitpunkt zeigte der Sensor vom 18. bis 23.11.
  höchstens 4,2 lx. Wer das Licht davor von Hand ausschaltet, bekommt es zum
  Rückfall wieder eingeschaltet.

### Warum 150 lx

Am 27.11. war es mit 50 lx zu spät: Die Beleuchtung wurde um 16:34:38 von
Hand eingeschaltet, weil es draußen schon recht dunkel war; die Station maß
37 lx (davor 62,9 lx um 16:29). Die Automation hätte erst um 16:43:53
geschaltet. Einschaltzeit je Schwelle einschließlich 10 Minuten Wartezeit,
aus den 5-Minuten-Höchstwerten der Langzeitstatistik (bis zu 5 Minuten zu
spät geschätzt); am 27.11. aus den Einzelwerten:

| Tag | 50 lx | 100 lx | 150 lx | 200 lx |
|---|---|---|---|---|
| 18.11. | 17:00 (Rückfall greift vorher) | 16:25 | 16:20 | 16:20 |
| 19.11. | 16:40 | 16:30 | 16:25 | 16:25 |
| 20.11. | 16:45 | 15:50 | 15:50 | 15:50 |
| 21.11. | 16:50 | 16:45 | 16:40 | 16:30 |
| 22.11. | 16:35 | 16:30 | 16:20 | 16:15 |
| 23.11. | 16:50 | 16:45 | 16:35 | 16:30 |
| 24.11. | 16:45 | 16:40 | 16:30 | 16:25 |
| 25.11. | 16:35 | 16:30 | 16:25 | 16:00 |
| 26.11. (trüb) | 16:15 | 16:00 | 15:50 | 15:40 |
| 27.11. | 16:43:53 | 16:37:03 | 16:31:17 | 16:26:42 |

150 lx hätte am 27.11. gut 3 Minuten vor dem Einschalten von Hand
geschaltet und schaltet an klaren Tagen etwa 16:20 bis 16:40. Folge: An
trüben oder kurz dunklen Nachmittagen kommt das Licht früher (20.11. und
26.11. gegen 15:50). Die Schwelle gilt auch für den Neustart-Zweig von
„morgens aus“ (Abschnitt Neustartsicher); der passt sich mit an.

### Bisher: warum 50 lx (bis 2026-11-27)

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

## Morgens

Seit 2026-11-23 geht die Beleuchtung um **06:30** an und nach Sonnenaufgang
wieder aus, sobald es hell genug ist. Schwelle im Helfer
`input_number.weihnachten_ausschalt_helligkeit` (Kategorie Einstellung, Einheit
`lx`), seit 2026-11-24 auf **500 lx** (vorher 50 lx wie abends); ein
eigener Helfer, damit morgens und abends getrennt einstellbar sind. 500 lx ist
zugleich das Maximum des Helfers. Für das Einschalten um 06:30 ändert der
Wert nichts: Die Sonne geht Ende November nach 07:40 auf, „morgens an“ greift
schon über „vor Sonnenaufgang“, und um 07:30 lag die Helligkeit an allen
ausgewerteten Tagen unter 1 lx. Der Wert entscheidet also nur, wann das Licht
ausgeht.

**Warum 500 lx:** Mit 50 lx ging das Licht kurz nach dem Hellwerden aus
(am 24.11. um 08:01); gewünscht ist morgens mehr Atmosphäre, auch bei den
Werten vom 24.11. gegen 08:30 (473 lx). Ab wann der Wert mindestens
10 Minuten über der Schwelle blieb (5-Minuten-Mittel der Langzeitstatistik,
Fenster 07:30 bis 10:30; das Licht geht rund 10 Minuten später aus):

| Tag | 50 lx | 200 lx | 300 lx | 500 lx |
|---|---|---|---|---|
| 18.11. | 07:55 | 09:00 | 09:35 | 10:15 |
| 19.11. | 08:35 | 09:20 | 09:25 | 10:20 |
| 20.11. | 08:20 | 08:40 | 08:50 | 09:10 |
| 21.11. | 07:55 | 08:15 | 08:20 | 08:55 |
| 22.11. | 08:15 | 08:45 | 08:55 | 09:40 |
| 23.11. | 07:55 | 08:20 | 08:40 | 08:50 |
| 24.11. | 07:55 | 08:10 | 08:15 | nach 08:30 |

Mit 500 lx geht das Licht an klaren Tagen gegen 09:00 bis 09:50 aus; an
trüben Tagen (18. und 19.11.) erst durch die Obergrenze um 10:00, die bleibt.

Bisher, mit 50 lx: erste Zeit, ab der der Wert über 50 lx blieb (Verlauf
18. bis 23.11., Sonnenaufgang gerechnet für den Heimstandort, am 24.11. laut
Home Assistant 07:51):


| Tag | Sonnenaufgang | über 50 lx | Abstand |
|---|---|---|---|
| 23.11. | 07:48 | 07:53 | +5 min |
| 22.11. | 07:47 | 08:13 | +26 min |
| 21.11. | 07:45 | 07:57 | +12 min |
| 20.11. | 07:44 | 08:22 | +38 min |
| 19.11. | 07:42 | 08:34 | +52 min |
| 18.11. | 07:41 | 07:56 | +15 min |

Mit 10 Minuten Wartezeit ging das Licht bei 50 lx also 15 bis 62 Minuten
nach Sonnenaufgang aus, Ende November etwa zwischen 08:05 und 09:00. Am 19.11.
(trüb) pendelte der Wert von 08:25 bis 08:40 um 50 lx; die Wartezeit hält
das Licht an, bis der Wert 10 Minuten darüber bleibt. Mit 100 lx ginge das
Licht 2 bis 16 Minuten später aus, am 19.11. erst nach 09:00.

- **Nachholen:** 60 min nach Sonnenaufgang prüft die Automation noch einmal
  die Helligkeit, falls ein kurzes `unavailable` die Wartezeit abgebrochen hat
  (siehe Automationen). Mit 500 lx liegt der Wert dann (rund 08:50) oft noch
  darunter; dann bleibt das Licht an bis zum Überschreiten oder bis 10:00. Am 20.11. war der Sensor um 07:52 und 08:01 kurz
  `unavailable`.
- **Spätestens 10:00** geht die Beleuchtung aus, ohne die Helligkeit zu
  prüfen. Mitte bis Ende Dezember geht die Sonne um 08:14 bis 08:21 auf.
- Die Ausschalt-Automation prüft die Weihnachtssaison nicht: Wer ausschaltet,
  prüft nie.

## Neustartsicher

Jede der vier Licht-Automationen hat einen Start-Auslöser und holt nach, was
während eines Neustarts verpasst wurde. Die Bedingungen hängen nicht nur am
Sensor, weil der beim Start oft noch `unavailable` ist:

| Neustart zwischen | Wirkung |
|---|---|
| 06:30 und 10:00 | an, wenn Saison an und vor Sonnenaufgang oder unter der Morgenschwelle |
| 06:30 und 10:00 | aus, wenn über der Morgenschwelle |
| 10:00 und 14:00 | aus |
| 14:00 und 20 min nach Sonnenuntergang | aus, wenn über der Abendschwelle (seit 2026-11-24, „morgens aus“) |
| 14:00 und 22:30 | an, wenn Saison an und unter der Abendschwelle oder 20 min nach Sonnenuntergang vorbei |
| 22:30 und 06:30 | aus |
| jederzeit, Saison aus | aus, wenn ein Stecker an ist („außerhalb der Saison aus“) |

Dazu: Die Helfer haben kein `initial` und behalten ihren Wert; die
Automationen haben eine `id`, Home Assistant behält damit, ob sie aktiv sind;
„Weihnachten: Saison umschalten“ gleicht beim Start den Zustand aller vier
Licht-Automationen an den Hauptschalter an. Eine laufende 10-Minuten-Wartezeit
geht beim Neustart verloren; der Start-Auslöser fängt das ab. Folge: Ein
Neustart in diesen Zeitfenstern schaltet auch Licht wieder ein oder aus, das
von Hand anders geschaltet wurde.

Lücke bis 2026-11-24: „morgens aus“ schaltete nach einem Neustart nur bis
12:00 aus, „bei Dämmerung an“ schaltet nur ein. War Home Assistant um 10:00
nicht erreichbar und kam erst nach 12:00 zurück, blieb die Beleuchtung bis
22:30 an. Geschlossen über den Start-Auslöser von „morgens aus“: 10:00 bis
14:00 immer aus, 14:00 bis 20 min nach Sonnenuntergang aus, wenn die
Helligkeit über der Einschalt-Schwelle liegt. Dieselbe Schwelle und dieselbe
Sonnengrenze prüft „bei Dämmerung an“ beim Start mit umgekehrtem Ergebnis,
deshalb schalten die beiden beim Start nie gegeneinander, auch wenn die
beiden Schwellen später verschieden eingestellt werden. Ist der Sensor beim
Start `unavailable`, passiert nachmittags nichts.

Geprüft am 2026-11-24:

- Teilbedingungen um 08:28 einzeln ausgewertet: „vor Sonnenuntergang +20 min“
  und „über der Einschalt-Schwelle“ wahr (409 lx); mit Versatz −10 h falsch,
  der Versatz wirkt also wie gedacht nach hinten. Der Zweig 14:00 bis
  Sonnenuntergang lässt sich vor 14:00 nicht als Ganzes testen.
- Handstart mit Bedingungen um 08:28: Lauf beendet ohne Fehler, Licht war
  schon aus.
- Echte Neustarts am Morgen (Starts um 07:29 und 07:44): „morgens an“ lief
  durch (Licht blieb an), „um 22:30 aus“, „bei Dämmerung an“, „morgens aus“
  und „außerhalb der Saison aus“ endeten an ihren Bedingungen, „Saison
  umschalten“ glich ab. Um 08:01 schaltete „morgens aus“ über die Helligkeit
  aus.

## Hauptschalter

Seit 2026-11-23 schaltet `input_boolean.weihnachtssaison` (Name
„Weihnachtssaison“, Kategorie Einstellung, Label `weihnachten`, kein
`initial`) die Saison. Er wird nur von Hand gesetzt; Plan und Entscheidungen
stehen im Dokument „Plan: Hauptschalter Weihnachtsbeleuchtung“.

| Stelle | Saison an | Saison aus |
|---|---|---|
| die vier Licht-Automationen (abends an, 22:30 aus, morgens an, morgens aus) | aktiviert | deaktiviert (`automation.turn_off`, `stop_actions: true`) |
| Baum und Fenster beim Umschalten | an, wenn es zwischen 06:30 und 10:00 oder zwischen 14:00 und 22:30 dunkel ist | sofort aus |
| Baum und Fenster einschalten (Alexa, Assist, Karte, Shelly-Taste oder -App) | möglich | sofort wieder aus |
| Raum-Reiter-Karte, Wohnzimmer | Schalter Tannenbaum und Fenster sichtbar und gezählt (Feld `sichtbar`) | ausgeblendet, nicht gezählt |
| `sensor.lichter_an` | zählt die Weihnachtslichter mit | zählt sie nicht |

- **Umschalten:** Die Automation „Weihnachten: Saison umschalten“ (Modus
  `queued`) zielt per `entity_id` auf die vier Licht-Automationen, nicht per
  Label, weil sie das Label selbst trägt. Beim Einschalten startet sie die
  Dämmerungs- und die Morgen-Einschalt-Automation mit `skip_condition: false`;
  deren Bedingungen entscheiden, ob Licht angeht. Beim Start von Home
  Assistant gleicht sie nur den Zustand der Automationen ab und schaltet kein
  Licht.
- **Sicherheitsbedingung:** Beide Einschalt-Automationen prüfen zusätzlich
  „Saison an“, falls jemand sie von Hand aktiviert. Die Ausschalt-Automationen prüfen
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
  Rückfrage. Seit 2026-11-24 mit Fußzeile zur Alexa-Freigabe (Abschnitt
  „Alexa“).
- **Außerhalb der Saison aus:** Die Automation „Weihnachten: Beleuchtung
  außerhalb der Saison aus“ bleibt immer aktiv; „Saison umschalten“ fasst sie
  nicht an. Geht eines der vier Lichter an, während die Saison aus ist,
  schaltet sie alle Lichter mit Label `weihnachten` aus. Der Status-Auslöser
  nennt nur `to: on` und kein `from`, damit er auch greift, wenn ein Stecker
  aus `unavailable` im Zustand an zurückkommt; der Neustart-Auslöser fängt
  einen Stecker ab, der während des Neustarts angegangen ist. Modus `queued`
  (max. 10): Schaltet jemand die Gruppe ein, kommen vier Auslöser fast
  gleichzeitig, und keiner darf verloren gehen. `continue_on_error`, falls ein
  Stecker gerade nicht erreichbar ist. Folge: Außerhalb der Saison lässt sich
  die Beleuchtung gar nicht einschalten, auch nicht zum Testen beim Aufbau;
  dafür zuerst den Hauptschalter einschalten.
- **Nicht umgesetzt:** Schalter nach Datum setzen. Der richtige Moment ist der
  Auf- und Abbau der Beleuchtung, kein Datum.

Test am 2026-11-23 um 19:51: Saison aus → beide Automationen `off`, Baum und
Fenster aus, `sensor.lichter_an` von 4 auf 1; Saison an → beide `on`, Baum und
Fenster an (dunkel, vor 22:30), `sensor.lichter_an` 5. Abgleich beim Start
durch Handstart der Umschalt-Automation geprüft, ohne Neustart.

Test am 2026-11-23 um 21:41: Saison aus → Lichter aus, die vier
Licht-Automationen `off`, „außerhalb der Saison aus“ `on`; Gruppe
`light.weihnachtsbeleuchtung` eingeschaltet (wie per Alexa) → vier Läufe,
alle vier Stecker nach rund 0,2 s wieder aus; Saison an → Lichter an, alle
Automationen `on`, die vier neuen Läufe enden an der Bedingung (Saison an).
Neustart-Auslöser nicht getestet.

## Alexa

Seit 2026-11-23 ist nur die Gruppe `light.weihnachtsbeleuchtung` an Alexa
übergeben (Home Assistant Cloud, Sprachassistenten → Alexa); Alexa übernimmt
den Namen „Weihnachtsbeleuchtung“. Die vier Lichter und die Fenster-Gruppe
bleiben für Alexa ausgeschaltet, damit Alexa bei „Weihnachtsbeleuchtung …“
nicht zwischen Gruppe und „Weihnachtsbeleuchtung Tannenbaum“ usw. wählen muss.
Für Assist sind alle freigegeben, wie bisher.

- „Alexa, schalte die Weihnachtsbeleuchtung ein/aus“ schaltet alle vier
  Stecker. Nur an/aus: die Stecker haben keine Helligkeit.
- Kein eigener Eintrag in `sensor.lichter_an`, `light.alle_lichter` oder der
  Lichter-Karte. Geprüft am 2026-11-23 nach dem Anlegen: Die Gruppe steht
  nicht in der Zählliste von `sensor.lichter_an`; der Sensor zählte 5, die
  vier Weihnachtslichter und ein weiteres eingeschaltetes Licht.
- Außerhalb der Saison geht die Beleuchtung nach dem Einschalten per Alexa
  sofort wieder aus (Automation „außerhalb der Saison aus“, Abschnitt
  Hauptschalter).

### Freigabe beim Auf- und Abbau von Hand

Der Hauptschalter schaltet die Alexa-Freigabe nicht mit. Beim Abbau die
Freigabe von „Weihnachtsbeleuchtung“ unter Einstellungen → Sprachassistenten →
Alexa ausschalten, beim Aufbau wieder einschalten. Die Fußzeile der Karte
`dashboard/licht/weihnachten-karte.yaml` erinnert daran; den tatsächlichen
Stand der Freigabe kann sie nicht lesen.

Geprüft am 2026-11-24, warum keine Automation das übernimmt:

- Home Assistant ändert die Freigabe nur über den Websocket-Befehl
  `homeassistant/expose_entity` (nur für Admins). Es gibt dafür keine Aktion,
  auch keinen REST-Endpunkt (HA-Core, Quellcode `exposed_entities` und `api`;
  in der Instanz liefert die Suche nach „expose“ unter allen Aktionen keinen
  Treffer).
- Die Zusatzintegration Spook (v5.11.1) bringt `homeassistant.expose_entity`
  und `homeassistant.unexpose_entity` mit; sie rufen dieselbe interne Funktion
  auf wie die Einstellungsseite. Eine Änderung meldet Home Assistant Cloud
  nach 1 s an Amazon (`DeleteReport` bzw. `AddOrUpdateReport`).
- Nicht umgesetzt: Spook bringt rund 160 weitere Aktionen, Auslöser und
  Bedingungen, eigene Entitäten und Reparaturmeldungen mit, ist nicht vom
  Home-Assistant-Projekt unterstützt und hängt an internen Funktionen, die ein
  Update ändern kann. Für zwei Handgriffe im Jahr lohnt das nicht.

## Noch offen

- Lichter-Karten: Nur die Raum-Reiter-Karte zeigt Baum und Fenster; die
  anderen Varianten führen ihre Lichter einzeln auf.
