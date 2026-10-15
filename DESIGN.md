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
| Karten und Views (`*.yaml`, `*.js` im Wurzelverzeichnis) | ja | Hex, `rgb()`, `rgba()` mit festen Zahlen |
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
(`0 0 14px -3px`) in der Farbe mit 0,5 Deckkraft.

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
`wetter-animiert-vorschlaege.html`). Dafür gilt zusätzlich:

- Nur Palettenfarben mit den Deckkraft-Stufen oben; Wolken, Nebel und Wind in
  Wolkengrau, Regen in Blau, Sonne in Sonnengelb, Nacht in Indigo, Unwetter in
  Rot, Sterne, Schnee und Blitz in Weiß mit Deckkraft.
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
