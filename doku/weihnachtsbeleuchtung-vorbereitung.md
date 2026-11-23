# Weihnachten: Beleuchtung mit vier Shelly Plug M Gen3

Betrifft: vier neue Shelly Plug M Gen3 im Wohnzimmer, einer für den
Tannenbaum, drei für die Fensterbeleuchtung. Sie ersetzen den Hue Smart Plug
`light.hue_smart_plug_1` („Tannenbaum“). Er ist aus der Hue-Bridge, aus der
Instanz und aus den Lichter-Karten entfernt; nur die Archivfassung
`fenster-lichter-uebersicht-karte.yaml` nennt ihn noch.
Stand dieser Notiz: 2026-11-23. Regeln: `CONTRIBUTING.md`, Abschnitt
„Labels, Bereiche und Kategorien“; Register: `design/labels.yaml`.

## Was schon steht

| Was | Stand |
|---|---|
| Bereich | `wohnzimmer` (Erdgeschoss) gibt es. Kein neuer Bereich. |
| Label `licht` | gibt es; alle vier Stecker bekommen es. |
| Label `weihnachten` | neu, Thema. Im Register eingetragen und in der Instanz angelegt. Erfasst vorerst nur die vier Stecker, ihre Gruppe und die Automationen. |
| Kategorie | `Steuerung` für Automationen gibt es. |

Die Gruppe kann erst angelegt werden, wenn die Stecker eingebunden sind: Der
Gruppen-Helfer nimmt nur vorhandene Entitäten auf.

## Wenn die Stecker eingebunden sind

1. **Einbinden** über die Shelly-Integration, Bereich Wohnzimmer. Gerätenamen
   ohne „Shelly“ und Modell, etwa „Tannenbaum“ und je Fenster ein Name nach
   seiner Lage.
2. **Schalter als Licht:** je Stecker den Helfer „Schalter als anderer
   Entitätstyp“ (`switch_as_x`) mit Typ Licht anlegen, wie bei der Lichterkette
   im Garten. Der Helfer blendet den Schalter aus; Automationen und Karten
   nutzen die `light.*`-Entität.
3. **Labels am Gerät,** nicht an den Entitäten: `licht` und `weihnachten`.
   Nicht `fenster`; das ist der Gerätetyp für Fensterkontakte.
4. **Gruppe „Weihnachtsfenster“:** Gruppen-Helfer, Typ Licht, mit den drei
   Fenster-Lichtern, `all: false` (an, sobald eines an ist). Bereich
   Wohnzimmer, Label `weihnachten` an der Gruppen-Entität, wie `licht` an
   `light.alle_lichter`.
5. **Alle Lichter:** die vier `light.*`-Entitäten in die Gruppe
   `light.alle_lichter` aufnehmen (Optionen des Gruppen-Helfers). Damit zählt
   `sensor.lichter_an` sie mit.

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
