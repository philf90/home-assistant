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

## Noch offen

- Schaltzeiten: fester Zeitplan (Helfer „Zeitplan“), Sonnenuntergang oder
  beides; Ausschaltzeit.
- Saison: Automationen nach Weihnachten ausschalten oder ein Hauptschalter
  als Helfer (Kategorie Einstellung).
- Lichter-Karten: Die neuen Lichter stehen in keiner Karte; die Karten führen
  ihre Lichter einzeln auf.
