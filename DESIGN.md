# Owlet-Stil – Design-Guide

Verbindliche Regeln für alle Karten und Views in diesem Repo. Die Farbwerte
selbst stehen in [`design/palette.yaml`](design/palette.yaml); diese Datei
erklärt, wofür sie gedacht sind und wie die Bausteine aussehen.

**Verbindlich heißt:** `ci/check_palette.py` (Karten) und `ci/check_grafana.py`
(Grafana) lassen keine Farbe durch, die nicht in `design/palette.yaml` steht. Die Prüfung läuft in der CI bei jedem Push und
Pull Request und lokal per pre-commit (siehe [`ci/README.md`](ci/README.md)).

## Geltungsbereich

| Bereich | Geprüft | Anmerkung |
|---|---|---|
| Karten und Views (`*.yaml`, `*.js` außerhalb von `ci/` und `design/`) | ja | Hex, `rgb()`, `rgba()` mit festen Zahlen |
| Grafana (`grafana/*.json`) | ja | `color`, `fixedColor`, `iconColor`; Grafana-Farbnamen außer `text` und `transparent` sind nicht erlaubt |
| Entwurfsseiten (`*-vorschlaege.html`) | nein | Mockups, keine Karten |
| Dashboards in der Instanz | nein | werden in der HA-Oberfläche bearbeitet; die CI sieht sie nicht |

Nicht prüfbar sind Farben, die erst zur Laufzeit entstehen
(`rgba(${r},${g},${b},…)`, `accent + '29'`), benannte CSS-Farben und die
*Bedeutung* einer Farbe. Ob Grün wirklich „OK“ heißt, bleibt Sache des Reviews.

## Grundprinzip

- Dunkler Navy-Grund (Farbton ~220°, Helligkeit 13–15 %).
- Akzente in einem Pastellband: Helligkeit 63–76 %, Kontrast auf dem Grund
  mindestens 5,5:1.
- Kühle Grautöne (Farbton 210–217°).
- Zustände färben Icon, Wert und Kachel, nie die ganze Karte.

## Bausteine

**Kartenhülle** – jede Karte, auch Spezialkarten (Kamera, Sankey, Power-Flow):

```css
background: linear-gradient(180deg, #1b2231 0%, #171d29 55%);
border: 1px solid rgba(255,255,255,0.05);
border-radius: 22px;
box-shadow: 0 18px 44px -22px rgba(0,0,0,0.7);
```

**Unterkachel** – Gruppen innerhalb der Hülle:

```css
background: rgba(255,255,255,0.028);
border: 1px solid rgba(255,255,255,0.06);
border-radius: 16px;   /* kleine Kacheln 13px */
```

**Icon-Kachel** – rundlich-quadratisch, 42–46 px, Radius 13–14 px. Grund und
Rand aus der Zustandsfarbe: `accent + '29'` (16 %) und `accent + '3d'` (24 %),
Icon in der vollen Farbe.

**Gefüllte Kachel** – für „an/läuft“, wie die Lichtkachel: Verlauf von der
aufgehellten zur vollen Farbe, Schrift und Icon in der passenden dunklen Farbe
(`schrift_auf_fuellung` in der Palette), Rand und Leuchten
(`0 0 14px -3px`) in der Farbe mit 0,5 Deckkraft. Dieselbe Füllung markiert
auch einen kritischen Messwert, etwa eine Raumtemperatur über 30 °C (siehe
„Temperaturstufen“). Rot hat in der Palette keine aufgehellte Stufe und bleibt
deshalb ohne Verlauf.

| Füllung | Schrift | Kontrast |
|---|---|---|
| Amber `#e6b566` (Verlauf ab `#f2cf93`) | `#3a2c12` | 7,2:1 |
| Grün `#a6d49e` | `#1d3320` | 8,1:1 |
| Blau `#7fb3d5` | `#132a3c` | 6,5:1 |
| Rot `#f0736a` | `#3d1512` | 5,6:1 |
| Violett `#b399d4` | `#2a1b3d` | 6,4:1 |
| Türkis `#7fd0d5` | `#103436` | 7,6:1 |

## Farbrollen

### Flächen

| Farbe | Rolle |
|---|---|
| `#1b2231` → `#171d29` | Kartenhülle (Verlauf) |
| `#222b3c` | erhöhte Fläche: Popups, Dropdowns, Hover |
| `#10151d` | vertiefte Fläche: Diagramme, Kamerarahmen, Log-Ausgaben |
| `#3a4453` | Zustand „aus“: Bogen, Rand im Leerlauf, neutrale Icon-Kachel |
| `#000000` | nur Schrift-Schatten und Video-Hintergrund |

Popups bekommen `#222b3c`, nicht den Kartengrund – sonst verschwimmen sie mit
der Karte darunter.

### Text

| Farbe | Kontrast | Rolle |
|---|---|---|
| `#f2f5f8` | 14,5:1 | Primärtext, Messwerte |
| `#e7ecf3` | 13,4:1 | Titel, Kopfzeilen |
| `#b4c0cf` | 8,6:1 | helle Labels, Hinweistext, Kartenbeschriftung |
| `#8794a5` | 5,2:1 | Sekundärtext und **jede kleine Schrift**, auch inaktive Zustände |
| `#6e7988` | 3,6:1 | **nie für Text** – nur Icons, inaktive Symbole, Dekoration |

`#6e7988` erreicht für normale Schrift nicht die 4,5:1 aus WCAG AA. Text, auch
grauer Text für „aus“ oder „keine Daten“, steht deshalb immer in `#8794a5`.
Färbt eine Variable Text und Icon zugleich, bekommt sie `#8794a5`.

Weiß kommt nur mit Deckkraft vor (`rgba(255,255,255,…)`); deckend ist das
Text-Weiß `#f2f5f8`.

### Status

| Farbe | Bedeutung |
|---|---|
| `#a6d49e` Grün | OK, geschlossen, Akku gut, positive Werte |
| `#e6b566` Amber | Hinweis, Warnung, offen (unkritisch) |
| `#e7936e` Koralle-Orange | erhöht – Stufe zwischen Amber und Rot |
| `#f0736a` Rot | kritisch, Alarm, Netzbezug, Akku leer |
| `#3a4453` / `#6e7988` | aus, inaktiv, keine Daten (Fläche, Icon) – als Text `#8794a5` |

Koralle-Orange liegt nah an Amber und Rot. Wer sie verwendet, schreibt die Stufe
immer auch als Text dazu.

### Temperaturstufen

Raumtemperaturen bekommen Statusfarben nach einem grünen Bereich je Raum, keinen
Farbverlauf (`temperaturen-button-card-v2.yaml`, Variablen `t_min`/`t_max`):

| Stufe | Farbe | Darstellung |
|---|---|---|
| unter dem Bereich | Blau `#7fb3d5` | getönte Pille (0,12 / 0,24) |
| im Bereich | Grün `#a6d49e` | getönte Pille |
| über dem Bereich bis 30 °C | Amber `#e6b566` | getönte Pille |
| über 30 °C | Rot `#f0736a` | gefüllte Pille, Schrift `#3d1512` (5,6:1) |
| Nebenraum ohne Bereich | Hellgrau `#b4c0cf` | getönte Pille, keine Bewertung |
| außen unter 0 °C (Frost) | Blau `#7fb3d5` | getönt |
| außen 0 bis unter 25 °C | Wolkengrau `#cdd6e0` | getönt |
| außen ab 25 °C (Sommertag) | Amber `#e6b566` | getönt |
| außen ab 30 °C (heißer Tag) | Rot `#f0736a` | Pille gefüllt, Kachel getönt |
| keine Daten | `#8794a5` | ohne Tönung, Rand Weiß 0,06 |

Die Bereiche folgen den Richtwerten des Umweltbundesamts (Wohnen 20 °C,
Schlafen 17–20 °C, Küche 18–20 °C, Bad 20–23 °C) mit dem WHO-Mindestwert
18 °C als Untergrenze für Kinderzimmer. Rot beginnt bei 30 °C, weil die ASR A3.5
dort Maßnahmen verlangt; die 26-°C-Empfehlung der ASR deckt Amber ab.
Die Außentemperatur folgt den klimatologischen Kenntagen des Deutschen
Wetterdienstes (Frosttag, Sommertag, heißer Tag), bewertet wird der aktuelle,
auf eine Nachkommastelle gerundete Messwert. In der Wetter-Karte steht der Wert
immer in `#f2f5f8`, Rot tönt dort nur Kachel und Icon; in der Pille ist Rot
gefüllt. Die Luftfeuchte außen ist ein Info-Wert in Blau ohne Bewertung, weil
der Komfortbereich von etwa 30–65 % für Innenräume gilt.
Koralle-Orange entfällt hier, weil in der Pille kein Platz für die Stufe als
Text ist. Rote Schrift auf roter Tönung erreicht als 13,5-px-Schrift nur
4,37:1 auf `#1b2231`, deshalb ist die kritische Stufe gefüllt.

### Akzente und Bereiche

| Farbe | Bereich |
|---|---|
| `#7fb3d5` Blau | Home, Standard-Akzent, Info-Werte |
| `#e6b566` Amber | Lichter |
| `#77d4d0` / `#7fd0d5` Türkis | Verbrauch, Hausgeräte |
| `#79b8c9` Petrol | Heizung |
| `#b399d4` Violett | Geräte, Netzwerk, Homematic |
| `#f0736a` Rot | Kamera |
| `#bdd27f` Limette | Garten |
| `#a6d49e` Grün | Pflanzen |
| `#cdd6e0` Wolkengrau | Wetter |
| `#8794a5` Grau | Auto |
| `#e6c15a` Sonnengelb | PV und Solar |
| `#89d2b0` Mint | Einspeisung, Autarkie, Eigenverbrauch |
| `#8ea2e6` Indigo | Nacht, Schlaf, Abwesenheits- und Urlaubsmodus, Szenen |
| `#e6a0c4` Rosé | Personen und Gesundheit |

Einspeisung bekommt in neuen Karten Mint statt Grün, damit „Energie fließt
raus“ nicht wie „Zustand in Ordnung“ aussieht.

### Tönungen

Getönte Akzentfarben nutzen nur diese Deckkraft-Stufen:

| Stufe | Deckkraft | Hex-Suffix | Einsatz |
|---|---|---|---|
| Fläche | 0,12 | `1f` | getönter Kachel- und Pillengrund |
| Icon-Kachel | 0,16 | `29` | Grund der Icon-Kachel, hebt sie von einer getönten Fläche ab |
| Schein | 0,18 | `2e` | weicher Farbschatten, Ring um Statuspunkte |
| Rand | 0,24 | `3d` | Rand getönter Kacheln und Pillen |
| Leuchten | 0,5 | `80` | Glow, Rand aktiver (gefüllter) Kacheln |

Ausgenommen sind Füllungen ab 0,65 (z. B. das rote Live-Badge), Weiß und Schwarz
mit Deckkraft sowie Textfarben mit Deckkraft.

### Grafana

Gleiche Rollen wie in den Karten, als Hex-Wert statt Grafana-Farbname:

| Verwendung | Farbe |
|---|---|
| Schwellwerte ok / Hinweis / erhöht / kritisch | `#a6d49e` / `#e6b566` / `#e7936e` / `#f0736a` |
| Autarkie ab 85 % (oberste Stufe) | `#89d2b0` Mint |
| Netzbezug, Netzbezugsleistung | `#f0736a` |
| PV | `#e6c15a` |
| Hausverbrauch, Annotationen | `#7fb3d5` |
| Gas | `#e6b566` |
| Kosten | `#b399d4` |
| Zählerstände | `text` (Theme-Textfarbe) |

Die Proxmox-Dashboards entstehen aus `grafana/proxmox_dashboards.py`; Farben
dort über die Konstanten `GREEN`, `YELLOW`, `ORANGE`, `RED`, `BLUE` setzen und
das JSON neu erzeugen.

### Sonderfarben

An einen Zweck gebunden, nur dort verwenden (Status `sonder` in der Palette):

- **Owlet-Identität:** Dragonfruit `#ff4696` auf Night Violet (`#1e1033`,
  `#241542`, `#3a1f5c`, Rand `#4b2e7a`). Keine Statusfarbe.
- **Personen:** Avatar-Platzhalter `#4a5a74`→`#33404f` (neutral) und
  `#6d5480`→`#4a3a5c` (zweite Person).
- **Fußball:** Vereinsrot `#e30613`, Tor `#ff8a80`, Vereinshülle
  `#2a1418`→`#1f1013`.
- **Flugradar:** Hervorhebung `#f2c94c`.
- **Wetterwarnungen:** offizielle DWD-Stufenfarben (`#7c8ba1`, `#f2c500`,
  `#fb9a12`, `#e6480e`, `#c0392b`) und `#4ade80` für „aktiv“. Nicht anpassen.

## Animierte Hintergründe

Wetter-Karte, Wind-Karte und Begrüßungs-Banner haben eine animierte Ebene
hinter dem Inhalt (Template `owlet_wetter_fx` in
`wetter-animation-button-card-templates.yaml`, Entwurf und Rechnung in
`wetter-animiert-vorschlaege.html`). Die Hausgeräte-Karten haben sie nur,
solange ein Programm läuft, pausiert (eingefroren) oder gerade fertig ist
(Template `owlet_geraete_fx` in `hausgeraete-animation-button-card-templates.yaml`,
Entwurf in `hausgeraete-vorschlaege.html`): Wasser in Blau, Luft in Weiß mit
Deckkraft, „Fertig“ in Türkis; die Wasserwelle der Waschmaschine bleibt im
unteren Innenabstand und liegt damit nie hinter Text. Die Thermostat-Kacheln
der Heizung (Template `owlet_heizung_fx` in
`heizung-animation-button-card-templates.yaml`, genutzt von
`thermostate-button-card-v3.yaml`) bewegen sich nur in der Lücke unten im
Bogen (50 × 32 px), also nie hinter Text: Wärmewellen in Amber, solange der
Raum heizt, in drei Stufen nach Ventilöffnung; bei offenem Fenster ein
Luftzug in Wolkengrau, der dreimal durchläuft und dann steht. „Fenster offen“
steht als Zustand in Blau (6,54:1 auf der Kachel). Eine Ebene hinter der
ganzen Karte gibt es dort bewusst nicht: 8 Kacheln mit je drei Textzeilen
würden überladen. Die Auto-Karte (Template `owlet_auto_fx` in
`autos-animation-button-card-templates.yaml`, genutzt von
`autos-button-card-v4.yaml`, Entwurf und Datenlage in
`autos-animation-vorschlaege.html`) bewegt aus demselben Grund nur
Icon-Kacheln, Ringe außen herum und das Fahrzeugbild: Die Tank-Kachel füllt
sich mit leichter Welle bis zum Tankstand, die Füllung in der Stufe „Rand“
(0,24), damit das Symbol darauf 3:1 hält; knappe oder fällige Werte und ein
offenes Schloss zeigen zwei Ringe, die dreimal laufen und dann als Schein
stehen bleiben; unter 4 °C funkeln Eiskristalle in Weiß mit Deckkraft am
Bildrand. Das Energiefluss-Diagramm (`energie-flow-button-card.yaml`, Entwurf
und Messwerte in `energiefluss-vorschlaege.html`) bewegt nur die Leitungen:
Lichtstriche in der Farbe der Quelle bzw. des Verbrauchers auf einer Spur in
der Stufe „Fläche“ (0,12), Breite und Tempo logarithmisch nach Leistung in
sechs Stufen. Weil die Karte bei jedem Sensor-Update neu zeichnet (gemessen
etwa alle 2 s), hängt die Phase an der Uhrzeit (negativer
`animation-delay`); sonst begänne der Fluss jedes Mal von vorn. Nur die
Quelle mit dem größten Anteil sendet einen Puls-Ring aus. Inaktive Leitungen
sind gestrichelt in Weiß mit Deckkraft und stehen still. Dafür gilt zusätzlich:

- Nur Palettenfarben mit den Deckkraft-Stufen oben; Wolken, Nebel und Wind in
  Wolkengrau (Wind in der Wind-Karte in Türkis), Regen in Blau, Sonne in
  Sonnengelb, Nacht in Indigo, Unwetter in Rot, Sterne, Schnee und Blitz in
  Weiß mit Deckkraft.
- Die Kachel „Bedingung“ der Wetter-Karte zeigt die Farbe ihrer Szene, damit
  Kachel und Hintergrund übereinstimmen. Ausnahmen: Gewitter in Amber (Warnung)
  sowie Schnee, Schneeregen und Hagel in Türkis. Weiß mit Deckkraft trägt als
  Kachelfarbe nicht, und Eis `#cfe3f2` wäre neben Wolkengrau kaum zu
  unterscheiden (ΔE 5,9).
- Kleine Schrift auf animiertem Grund steht in `#b4c0cf` statt `#8794a5`.
- Kleine Schrift muss im schlechtesten Fall (alle Flächen einer Szene
  übereinander) 4,5:1 halten. Wo das nicht reicht, wird die Animation hinter
  der Schrift gedämpft: im Banner hinter der Datumszeile auf 45 %, in den
  Kacheln der Wetter-Karte über einen Schutzgrund `#171d29` mit 0,62
  Deckkraft (Animation dort zu 38 % sichtbar).
- Text links im Banner bleibt ohne Animation; die Ebene beginnt erst rechts
  neben dem gemessenen Text.
- Blitze höchstens 3 pro Sekunde (WCAG 2.3.1); verwendet wird ein Doppelblitz
  alle 8 s.
- „Bewegung reduzieren“ am Gerät zeigt ein Standbild derselben Szene.

## Eine neue Farbe aufnehmen

1. Prüfen, ob eine vorhandene Farbe die Rolle schon abdeckt. Die Meldung von
   `ci/check_palette.py` nennt den nächsten Palettenwert.
2. Neue Akzente bleiben im Pastellband (Helligkeit 63–76 %) und erreichen auf
   `#1b2231` mindestens 4,5:1, wenn sie Text färben.
3. Eintrag in `design/palette.yaml` mit `hex`, `name`, `status` und `zweck`.
4. Rolle hier in `DESIGN.md` ergänzen.
