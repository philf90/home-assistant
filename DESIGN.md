# Owlet-Stil – Design-Guide

Verbindliche Regeln für alle Karten und Views in diesem Repo. Die Farbwerte
selbst stehen in [`design/palette.yaml`](design/palette.yaml); diese Datei
erklärt, wofür sie gedacht sind und wie die Bausteine aussehen.

**Verbindlich heißt:** `ci/check_palette.py` (Karten) und `ci/check_grafana.py`
(Grafana) lassen keine Farbe durch, die nicht in `design/palette.yaml` steht.
Die Werte des hellen Modus sind nur im erzeugten Theme erlaubt (siehe
„Heller Modus“). Die Prüfung läuft in der CI bei jedem Push und
Pull Request und lokal per pre-commit (siehe [`ci/README.md`](ci/README.md)).

## Geltungsbereich

| Bereich | Geprüft | Anmerkung |
|---|---|---|
| Karten und Views (`*.yaml`, `*.js` außerhalb von `ci/` und `design/`) | ja | Hex, `rgb()`, `rgba()` mit festen Zahlen |
| Grafana (`grafana/*.json`) | ja | `color`, `fixedColor`, `iconColor`; Grafana-Farbnamen außer `text` und `transparent` sind nicht erlaubt |
| Entwurfsseiten (`entwuerfe/*.html`) | nein | Mockups, keine Karten |
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
Farbverlauf (`temperaturen-karte-v2.yaml`, Variablen `t_min`/`t_max`):

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

## Heller Modus

Jede Rolle der Palette hat einen Wert für den hellen Modus. Die Werte stehen
in `design/palette.yaml` unter `hell_farben` (neue Werte mit Name und Zweck)
und `theme` (jede Variable mit ihrem dunklen und hellen Wert). Daraus erzeugt
`python ci/gen_theme.py` das Theme
[`owlet-theme-konfig.yaml`](dashboard/allgemein/owlet-theme-konfig.yaml) mit
`modes: dark` und `modes: light`. Welcher Modus gilt, wählt jeder Benutzer im
Profil oder im More-Menü (System, Hell, Dunkel).

**Stand:** Palette und Theme stehen. Umgestellt sind die schwebende
Navigationsleiste und ihr More-Menü (`navigation-templates.yaml` und
`navbar-karte.yaml`), die obere Navigation (Template `top_navigation` und
`top-navigation-karte.yaml`) sowie von der Home-View
`haustuer-ereignis-karte.yaml`, `person-presence-karte.yaml`,
`fenster-lichter-karte.yaml`, `haustuer-lock-karte.yaml`,
`pollenflug-karte.yaml`, `wlan-karte.yaml`, `muellabfuhr-karte-v2.yaml`,
`meteoalarm-karte.yaml` und `welcome-banner-karte.yaml` samt Wetteranimation
(siehe „Animierte Hintergründe“), dazu die Wetter-View (`wetter-karte.yaml`)
und von der Lichter-View `fenster-karte.yaml` und `lichter-raum-karte.yaml`
(erste gefüllte Kachel mit `owlet-fuellung-rand-amber` und
`owlet-leuchten-amber`), von der Energie-View die Templates
(`energie-templates.yaml`), `energie-verbraucher-karte.yaml`,
`energie-zaehler-karte.yaml` und `energie-solarbank-pv-karte.yaml`. Die
Owlet-Karte bleibt als Identitätshülle dunkel.
Die übrigen Karten tragen noch die festen dunklen Werte und werden
schrittweise umgestellt; bis dahin bleiben sie in beiden Modi dunkel.

### Karten umstellen

- Jede Farbe als Theme-Variable mit dem **dunklen Palettenwert als
  Rückfall**: `var(--owlet-gruen, #a6d49e)`. Ohne Theme `owlet` sieht die
  Karte so aus wie bisher.
- Tönungen über `color-mix`:
  `color-mix(in srgb, var(--owlet-gruen, #a6d49e) 12%, transparent)`.
- Weiß mit Deckkraft wird nach seiner Rolle zur Flächenvariable, Rückfall
  ist deren dunkler Wert. Abweichende Deckkräfte rücken auf die nächste Stufe
  (im Dunklen höchstens 0,02 Unterschied):

  | Weiß mit Deckkraft als | Deckkraft | Variable |
  |---|---|---|
  | Rand | bis 0,055 | `owlet-huelle-rand` (0,05) |
  | Rand, Trennlinie | darüber (0,06–0,08) | `owlet-unterkachel-rand` (0,06) |
  | Fläche | unter 0,04 | `owlet-unterkachel` (0,028) |
  | Fläche | ab 0,04 | `owlet-neutral-kachel` (0,05) |
  | Schrift (0,55–0,66) | – | dunkel unverändert, hell `owlet-text-sekundaer` über den Schalter (unten) |

  Schrift aus Navy mit Deckkraft hielte hell keine 4,5:1 (Navy 0,55 auf der
  Hülle 3,9:1), deshalb dort der Sekundärtext.
- **Schalter `owlet-dunkel-anteil`** (dunkel `100%`, hell `0%`, Abschnitt
  `theme.schalter` der Palette): `color-mix(in srgb, A var(--owlet-dunkel-anteil, 100%), B)`
  ist dunkel A und hell B. Für Farben, die nur dunkel als Ton taugen, etwa ein
  Ton als Schrift auf doppelter Tönung (Müll: „abends rausstellen“, sonst
  4,13:1) oder die DWD-Farben.
- Gleich bleibende Farben (Füllungen, Schrift auf Füllung, Sonderfarben,
  Schwarz für Abdunklung und Schatten) bleiben als Hex-Wert stehen.
- `color-mix` braucht einen aktuellen Browser (Chrome/WebView 111,
  Safari 16.2, Firefox 113).

### Grundprinzip

- Heller, kühler Grund: Seite `#e6eaf0`, Kartenhülle als Verlauf
  `#fafbfd` → `#f3f5f8`. Die Grautöne haben den Farbton der dunklen
  (OKLCH etwa 255°).
- Akzente im **Tiefband**: Jeder Akzent behält den OKLCH-Farbton seines
  dunklen Gegenstücks, die Sättigung steigt um den Faktor 1,3 (höchstens
  Chroma 0,15), die Helligkeit sinkt, bis Schrift auf der eigenen Tönung 0,12
  mindestens 4,6:1 hält. Ergebnis: OKLCH-Helligkeit 0,49–0,52, auf der Hülle
  5,41–5,53:1.
- Den Farbton höchstens um 5° verschieben, und nur, wenn ein Farbpaar sonst
  schlechter unterscheidbar wäre als im dunklen Modus: Blau +3,2°,
  Petrol +4,7°, Sonnengelb +4,6°.
- **Navy statt Weiß:** Ränder, Innenflächen und Schatten entstehen aus
  `#171d29` mit Deckkraft, so wie dunkel aus Weiß mit Deckkraft. Weiß ist nur
  als erhöhte Fläche (Popups) deckend erlaubt.
- Zustände färben Icon, Wert und Kachel, nie die ganze Karte.
- **Identitätshüllen bleiben dunkel:** Owlet-Karte (Night Violet) und
  Vereinshülle im Fußball-View behalten in beiden Modi Hülle und Farben.

**Gemessen** wird nach WCAG 2.x im ungünstigsten Fall aus Hülle oben, Hülle
unten, Unterkachel (Navy 0,03 über der Hülle = `#eceff2`) und Popup
`#ffffff`; Akzente zusätzlich gegen ihre eigene Tönung 0,12. Maßgeblich ist
fast immer die Unterkachel. Die dunklen Werte sind wie oben auf `#1b2231`
gemessen.

### Flächen und Text

| Rolle | Dunkel | Hell | Hell, Kontrast | Variable |
|---|---|---|---|---|
| Seitengrund | `#171d29` | `#e6eaf0` | – | `owlet-seite` |
| Kartenhülle oben / unten | `#1b2231` / `#171d29` | `#fafbfd` / `#f3f5f8` | – | `owlet-huelle-oben`, `-unten` |
| Rand der Hülle | Weiß 0,05 | Navy 0,06 | – | `owlet-huelle-rand` |
| Schatten | Schwarz 0,7 | Navy 0,30 | – | `owlet-schatten` |
| Unterkachel / Rand | Weiß 0,028 / 0,06 | Navy 0,03 / 0,07 | – | `owlet-unterkachel`, `-rand` |
| Neutrale Icon-Kachel | Weiß 0,05 | Navy 0,05 | – | `owlet-neutral-kachel` |
| Erhöhte Fläche | `#222b3c` | `#ffffff` | – | `owlet-flaeche-erhoeht` |
| Vertiefte Fläche | `#10151d` | `#e9edf2` | – | `owlet-flaeche-vertieft` |
| Zustand aus | `#3a4453` | `#b4c0cf` | 1,69:1 (dunkel 1,62:1) | `owlet-aus` |
| Primärtext | `#f2f5f8` | `#171d29` | 14,62:1 | `owlet-text` |
| Titel | `#e7ecf3` | `#1b2231` | 13,79:1 | `owlet-titel` |
| Labels | `#b4c0cf` | `#3a4453` | 8,54:1 | `owlet-label` |
| Sekundärtext, jede kleine Schrift | `#8794a5` | `#586475` | 5,21:1 | `owlet-text-sekundaer` |
| Muted, **nie Text** | `#6e7988` | `#6e7988` | 3,83:1 | `owlet-muted` |

Primärtext, Titel, Labels, Zustand aus und Muted sind vorhandene
Palettenwerte; neu sind nur die Flächen und der Sekundärtext. Auf dem
Seitengrund hält der Sekundärtext 4,98:1.

### Status und Akzente

| Farbe | Dunkel | Hell | Auf Tönung 0,12 | Auf Hülle | Icon auf Icon-Kachel |
|---|---|---|---|---|---|
| Grün | `#a6d49e` | `#38702e` | 4,64:1 | 5,45:1 | 4,39:1 |
| Amber | `#e6b566` | `#855c04` | 4,64:1 | 5,45:1 | 4,38:1 |
| Koralle-Orange | `#e7936e` | `#a94302` | 4,63:1 | 5,51:1 | 4,37:1 |
| Rot | `#f0736a` | `#ae3c38` | 4,62:1 | 5,49:1 | 4,33:1 |
| Blau | `#7fb3d5` | `#266994` | 4,61:1 | 5,45:1 | 4,38:1 |
| Türkis | `#7fd0d5` | `#016f74` | 4,60:1 | 5,45:1 | 4,35:1 |
| Türkis hell | `#77d4d0` | `#016f74` | 4,60:1 | 5,45:1 | 4,35:1 |
| Petrol | `#79b8c9` | `#066d86` | 4,60:1 | 5,43:1 | 4,32:1 |
| Violett | `#b399d4` | `#76559c` | 4,62:1 | 5,42:1 | 4,35:1 |
| Limette | `#bdd27f` | `#5a6b04` | 4,61:1 | 5,43:1 | 4,38:1 |
| Mint | `#89d2b0` | `#00714f` | 4,66:1 | 5,53:1 | 4,40:1 |
| Indigo | `#8ea2e6` | `#4b5eb1` | 4,63:1 | 5,44:1 | 4,38:1 |
| Rosé | `#e6a0c4` | `#994776` | 4,62:1 | 5,47:1 | 4,37:1 |
| Wolkengrau | `#cdd6e0` | `#5b6571` | 4,64:1 | 5,42:1 | 4,39:1 |
| Eis | `#cfe3f2` | `#506778` | 4,62:1 | 5,41:1 | 4,37:1 |
| Nachtgrau | `#9aa7bd` | `#35435c` | 7,51:1 | 9,12:1 | 7,03:1 |
| Sonnengelb | `#e6c15a` | `#776202` | 4,61:1 | 5,44:1 | 4,36:1 |

Die Variablen heißen wie die Farbe: `owlet-gruen`, `owlet-amber`,
`owlet-koralle`, `owlet-rot`, `owlet-blau` usw. Alle Tieftöne dürfen Text
färben.

- **Licht an** (`#f0c274`) hat keinen eigenen hellen Wert: `owlet-licht-an`
  ist hell Amber `#855c04`. Schon dunkel liegen beide nur ΔE00 3,2
  auseinander.
- **Türkis hell** hat keinen eigenen hellen Wert: `owlet-tuerkis-hell` ist
  hell `#016f74` wie Türkis. Getrennt lägen beide nur ΔE00 3,2 auseinander
  (dunkel 4,0).
- **Nachtgrau** ist bewusst tiefer gesetzt. Im Tiefband allein läge es nur
  ΔE00 5,8 neben Wolkengrau (dunkel 13,3); jetzt sind es 13,2.
- **Unterscheidbarkeit** der engsten Paare, ΔE00 dunkel → hell: Amber/
  Sonnengelb 6,4 → 7,2, Türkis/Petrol 8,3 → 8,8, Blau/Petrol 7,4 → 8,3,
  Blau/Indigo 10,7 → 10,9, Violett/Indigo 13,0 → 12,5, Eis/Wolkengrau
  4,6 → 4,4.

### Tönungen und gefüllte Kachel

Die Deckkraft-Stufen gelten unverändert (Fläche 0,12, Icon-Kachel 0,16,
Schein 0,18, Rand 0,24, Leuchten 0,5), angewendet auf den Tiefton. Mit
Variablen entsteht die Tönung über `color-mix`:
`color-mix(in srgb, var(--owlet-gruen) 12%, transparent)`.

Gefüllte Kacheln behalten Füllung und Schrift auf Füllung, damit auch deren
Kontrast (5,6–8,1:1). Anders sind nur Rand und Leuchten:

| | Dunkel | Hell | Variable |
|---|---|---|---|
| Rand | Pastell 0,5 | Tiefton deckend | `owlet-fuellung-rand-<farbe>` |
| Leuchten (`0 0 14px -3px`) | Pastell 0,5 | Tiefton 0,5 | `owlet-leuchten-<farbe>` |

Der dunkle Rand erreicht auf heller Hülle nur 2,10–2,23:1, der deckende
Tiefton 5,42–5,49:1. Die Füllung allein hebt sich nur mit 1,53–2,61:1 von
der Hülle ab; die Kante trägt also der Rand. Varianten gibt es für Amber
(Lichtkachel), Grün, Blau, Rot, Violett und Türkis.

### Sonderfarben im hellen Modus

| Farbe | Regel | Messwert hell |
|---|---|---|
| Owlet-Identität, Vereinshülle | Hülle bleibt dunkel, Inhalt nutzt die dunkle Palette; Tor `#ff8a80` nur dort | Tor auf heller Hülle 2,09:1 |
| Dragonfruit `#ff4696` | bleibt unverändert, auch als Abwesend-Rand der Personenkarte; dort nur Zusatzsignal, der Zustand steht immer auch als Text, Icon und Badge da (WCAG 1.4.11 verlangt 3:1 nur für Grafiken, die allein den Zustand zeigen) | 2,93–3,09:1 auf der Hülle, 2,65:1 zum Seitengrund |
| Avatar-Platzhalter | unverändert, eigene Fläche | – |
| Vereinsrot `#e30613` | nur als Fläche mit weißer Schrift | Weiß darauf 4,88:1, als Schrift 4,47:1 |
| Flugradar-Gelb `#f2c94c` | nur auf dunklem Kartengrund | 1,45:1 |
| DWD-Stufen 0–4 | nur als Fläche; Schrift Navy (Stufe 0–2) bzw. Weiß (Stufe 4); Stufe 3 nur große, fette Schrift ab 18,66 px | Navy 4,87 · 10,26 · 7,82 · 4,26; Weiß Stufe 3 3,96, Stufe 4 5,44 |
| Warnung aktiv `#4ade80` | nur als Punkt mit Text daneben | 1,60:1 |

**DWD-Karte** (`meteoalarm-karte.yaml`): Die Integration liefert eigene
Farben, nicht die Palettenwerte (Stufe 1 beobachtet als `#ffeb3b`). Deshalb
gilt hell über den Schalter:

- Icon-Kachel deckend in der DWD-Farbe, Icon in Navy `#171d29` oder Hell
  `#f2f5f8`, je nachdem was gegen die Farbe mehr Kontrast hat (gerechnet in
  der Karte).
- Stufen- und „aktiv“-Pille: Tönung 0,12 und Rand 0,24 der DWD-Farbe,
  Schrift `owlet-text`.
- Gemessen (Chromium, Stufen `#ffeb3b`, `#fb9a12`, `#e6480e`, `#c0392b`):
  Icon 13,82 · 7,82 · 4,26 · 4,97:1, Pillenschrift 13,63–16,45:1.
- Dunkel stehen Icon und Schrift im DWD-Ton auf seiner Tönung, solange er
  dort 3:1 (Icon) bzw. 4,5:1 (Schrift) hält; sonst in Hell `#f2f5f8`. Die
  Karte rechnet das aus der gelieferten Farbe (Funktion `lesbar`), die
  Fläche bleibt immer im DWD-Ton. Gemessen mit `#e6480e`: Pillenschrift
  3,60 → 13,05:1, Icon bleibt im Ton (3,45:1); mit `#c0392b`: Schrift
  2,71 → 13,46:1, Icon 2,63 → 13,06:1. Stufe 1 und 2 bleiben im Ton.
- Kleine Schrift auf Chips im Popup in Label-Grau (dunkel 3,95 → 6,60:1).

### Noch offen

- **Animierte Hintergründe:** Die Wetteranimation ist umgestellt (Banner,
  Wetter- und Wind-Karte). Die Animationen von Hausgeräten, Heizung, Auto
  und Energiefluss (Luft, Eis, inaktive Leitungen in Weiß mit Deckkraft)
  brauchen eigene Regeln.
- **Grafana** hat ein eigenes helles Theme; die Schwellwertfarben sind dort
  nicht gemessen.
- **Gedämpfte Kacheln** (`opacity: 0.55`): kleine Schrift fällt auf 2,27:1
  hell und 2,58:1 dunkel. Besser über Muted-Icon und Sekundärtext dämpfen.
- **Schon vor der Umstellung zu schwach, dunkel:** das Datum in der
  Müllkarte (4,03:1) und die Icons in den Kacheln der Wetter-Karte im
  schlechtesten Fall (alle Wolken übereinander, 2,60:1 bei Sekundär-Grau,
  9 Kombinationen aus Szene und Kachelfarbe unter 3:1). Hell halten sie
  dank Schutzgrund 0,70 mindestens 3,06:1.

## Animierte Hintergründe

Wetter-Karte, Wind-Karte und Begrüßungs-Banner haben eine animierte Ebene
hinter dem Inhalt (Template `owlet_wetter_fx` in
`wetter-templates.yaml`, Entwurf und Rechnung in
`wetter-animiert.html`). Die Hausgeräte-Karten haben sie nur,
solange ein Programm läuft, pausiert (eingefroren) oder gerade fertig ist
(Template `owlet_geraete_fx` in `hausgeraete-templates.yaml`,
Entwurf in `hausgeraete.html`): Wasser in Blau, Luft in Weiß mit
Deckkraft, „Fertig“ in Türkis; die Wasserwelle der Waschmaschine bleibt im
unteren Innenabstand und liegt damit nie hinter Text. Die Thermostat-Kacheln
der Heizung (Template `owlet_heizung_fx` in
`heizung-templates.yaml`, genutzt von
`thermostate-karte-v3.yaml`) bewegen sich nur in der Lücke unten im
Bogen (50 × 32 px), also nie hinter Text: Wärmewellen in Amber, solange der
Raum heizt, in drei Stufen nach Ventilöffnung; bei offenem Fenster ein
Luftzug in Wolkengrau, der dreimal durchläuft und dann steht. „Fenster offen“
steht als Zustand in Blau (6,54:1 auf der Kachel). Eine Ebene hinter der
ganzen Karte gibt es dort bewusst nicht: 8 Kacheln mit je drei Textzeilen
würden überladen. Die Auto-Karte (Template `owlet_auto_fx` in
`autos-templates.yaml`, genutzt von
`autos-karte-v4.yaml`, Entwurf und Datenlage in
`autos-animation.html`) bewegt aus demselben Grund nur
Icon-Kacheln, Ringe außen herum und das Fahrzeugbild: Die Tank-Kachel füllt
sich mit leichter Welle bis zum Tankstand, die Füllung in der Stufe „Rand“
(0,24), damit das Symbol darauf 3:1 hält; knappe oder fällige Werte und ein
offenes Schloss zeigen zwei Ringe, die dreimal laufen und dann als Schein
stehen bleiben; unter 4 °C funkeln Eiskristalle in Weiß mit Deckkraft am
Bildrand. Das Energiefluss-Diagramm (`energie-flow-karte.yaml`, Entwurf
und Messwerte in `energiefluss.html`) bewegt nur die Leitungen:
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
  der Schrift gedämpft: im Banner die ganze Wetterspalte rechts (Icon,
  Temperatur, Datum) auf 45 %, in den Kacheln der Wetter-Karte über einen
  Schutzgrund in Hüllenfarbe (`owlet-huelle-unten`), dunkel 0,62, hell 0,70
  (Animation dort zu 38 % bzw. 30 % sichtbar; hell halten so auch die Icons
  3:1, gerechnet in jeder Kombination aus Szene und Kachelfarbe).
- Icon und große Schrift auf animiertem Grund halten 3:1. Im Banner standen
  sie bis zur Ruhezone rechts auf der vollen Szene und fielen dunkel in
  6 von 16 Szenen darunter (Unwetter 1,72:1); mit Ruhezone mindestens
  3,10:1 dunkel und 3,74:1 hell.
- Text links im Banner bleibt ohne Animation; die Ebene beginnt erst rechts
  neben dem gemessenen Text.
- Blitze höchstens 3 pro Sekunde (WCAG 2.3.1); verwendet wird ein Doppelblitz
  alle 8 s.
- „Bewegung reduzieren“ am Gerät zeigt ein Standbild derselben Szene.

### Wetteranimation im hellen Modus

Entwurf, Vorschau und Rechnung: `banner-hell.html`. Jedes Element nimmt hell
den Tiefton seiner Rolle; die Deckkraft wird mit einem festen Faktor so
erhöht, dass es sich so stark von der Hülle abhebt wie dunkel (Kontrast
Element zu Hülle, dunkel auf `#1b2231`, hell auf `#fafbfd`).

| Element | Dunkel | Hell | Faktor |
|---|---|---|---|
| Wolke, Nebel | Wolkengrau | Wolkengrau hell | × 1,8 |
| Regenwolke | Muted | Muted | × 1 |
| Sonne, Strahlen | Sonnengelb | Sonnengelb (Mitte 0,6, Strahlen 0,5) | × 2,5 / × 4,2 |
| Nachtschein | Indigo | Indigo hell | × 1,28 |
| Sterne | Weiß 0,5 | Nachtgrau hell | × 1,54 |
| Regentropfen | Blau | Blau hell | × 1,33 |
| Schneeflocken | Weiß 0,5 | Eis hell | × 1,88 |
| Hagel | Wolkengrau 0,5 | Wolkengrau hell | × 1,62 |
| Blitz | Weiß 0,18 | Sonnengelb 0,72 | × 4 |
| Unwetterschein | Rot | Rot hell | × 1 |
| Windschlieren | Türkis / Wolkengrau | Türkis hell / Wolkengrau hell | × 1,48 / × 1,7 |

- **Ausnahmen:** Sonne und Blitz bleiben Sonnengelb statt Tiefton (der wirkt
  oliv, ein abgedunkelter Blitz wie ein Schatten). Sie erreichen hell nicht
  die dunkle Abhebung: Sonnenmitte 1,36:1 statt 1,74:1, Blitz 1,44:1 statt
  1,78:1; deckend wären höchstens 1,68:1 möglich.
- **Umschalten nur mit Opt-in:** Das Template liest `--wx-dunkel`
  (Rückfall 100 %). Eine Karte schaltet die hellen Regeln ein, indem sie in
  `styles.card` `--wx-dunkel: var(--owlet-dunkel-anteil, 100%)` setzt. Ohne
  den Eintrag bleibt die Animation in beiden Modi dunkel (geprüft: 0 von
  931 Elementen weichen ab).
- **Deckkraft per Faktor:** `opacity: calc(var(--o) * (180% - 0.8 * var(--wx-d)))`
  ist dunkel `--o`, hell `--o × 1,8`; Farben wählt `color-mix` mit
  `var(--wx-d)`.

## Eine neue Farbe aufnehmen

1. Prüfen, ob eine vorhandene Farbe die Rolle schon abdeckt. Die Meldung von
   `ci/check_palette.py` nennt den nächsten Palettenwert.
2. Neue Akzente bleiben im Pastellband (Helligkeit 63–76 %) und erreichen auf
   `#1b2231` mindestens 4,5:1, wenn sie Text färben.
3. Eintrag in `design/palette.yaml` mit `hex`, `name`, `status` und `zweck`.
4. Hellen Wert festlegen (Abschnitt „Heller Modus“): Tiefband-Wert unter
   `hell_farben` aufnehmen und die Rolle unter `theme.variablen` mit
   `dunkel` und `hell` eintragen, dann `python ci/gen_theme.py`. Bleibt die
   Farbe in beiden Modi gleich (Füllung, Sonderfarbe), entfällt das.
5. Rolle hier in `DESIGN.md` ergänzen.
