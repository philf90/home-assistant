# Umbenennung Owlet-Stil → Nachtblau-Stil

Seit Oktober 2026 heißt der Stil des Repos **Nachtblau-Stil**, vorher
Owlet-Stil. „Owlet“ ist in den USA eine eingetragene Marke (Owlet Baby Care Inc.
für Babyphone, Schréder S.A. für Lichtsteuerung); für den Stil wird der Name
deshalb nicht mehr verwendet. Farben, Bausteine und Regeln sind unverändert,
geändert haben sich nur Namen.

Diese Liste nennt absichtlich Namen, die es nicht mehr gibt; `ci/check_verweise.py`
prüft sie deshalb nicht.

## Was gleich bleibt

Alles, was das Gerät Owlet Smart Sock meint:

- die Karte `dashboard/personen/owlet-smart-sock-karte.yaml`
- die Entity-IDs `sensor.owlet_sock_*`, die die Integration erzeugt
- die Identitätsfarben dieser Karte (Dragonfruit, Night Violet) in
  `design/palette.yaml`

## Alt → neu

| Alt | Neu |
|---|---|
| Theme `owlet` (`/config/themes/owlet.yaml`) | Theme `nachtblau` (`/config/themes/nachtblau.yaml`) |
| `dashboard/allgemein/owlet-theme-konfig.yaml` | `dashboard/allgemein/nachtblau-theme-konfig.yaml` |
| CSS-Variablen `--owlet-*` | `--nachtblau-*`, Rest des Namens gleich (`--owlet-gruen` → `--nachtblau-gruen`) |
| Templates `owlet_*` | `nachtblau_*`, Rest des Namens gleich (`owlet_auto_fx` → `nachtblau_auto_fx`) |
| Bibliotheken `window.__owlet*` | `window.__nachtblau*` (`__owletFz` → `__nachtblauFz`) |
| localStorage `owletFahrtStart:…`, `owletFahrtZiel:…` | `nachtblauFahrtStart:…`, `nachtblauFahrtZiel:…`; die Fahrzeiten-Karte übernimmt alte Werte beim ersten Lesen |
| Skill `.claude/skills/owlet-design` | `.claude/skills/nachtblau-design` |
| pre-commit-Hook `owlet-palette` | `nachtblau-palette` |

Umbenannte Templates: `auto_fx`, `docker_aufklapper`, `docker_kopf`,
`docker_kpi`, `docker_messwert`, `docker_projekt`, `docker_titel`,
`docker_update`, `docker_zeile`, `dwd_popup`, `fahrzeit_popup`, `fahrzeiten`,
`geraete_fx`, `heizung_fx`, `kamera_kachel`, `pflanze`, `pollen_popup`,
`tanken_popup`, `tankstellen`, `wetter_fx`, jeweils mit `owlet_` davor (alt)
bzw. `nachtblau_` (neu).

## Instanz umstellen

Die Karten tragen zu jeder Variablen den dunklen Wert als Rückfall
(`var(--nachtblau-gruen, #a6d49e)`). Eine noch nicht neu eingefügte Karte sieht
im dunklen Modus deshalb unverändert aus; nur im hellen Modus fehlen ihr die
hellen Werte, bis sie neu eingefügt ist.

1. `nachtblau-theme-konfig.yaml` als `/config/themes/nachtblau.yaml` ablegen,
   Aktion `frontend.reload_themes` ausführen.
2. Im Profil das Theme `nachtblau` wählen, oder für alle mit
   `frontend.set_theme` (name: `nachtblau`).
3. Je Dashboard die Template-Dateien und die Karten, die sie nutzen,
   **gemeinsam** neu einfügen. Eine Karte mit `template: owlet_auto_fx` zeigt
   einen Fehler, sobald nur noch `nachtblau_auto_fx` existiert. Betroffen sind:
   - Fahrzeuge: `autos-templates.yaml` mit `autos-karte-v4.yaml`,
     `fahrzeiten-templates.yaml` mit `fahrzeiten-karte.yaml`,
     `tanken-templates.yaml` mit `tanken-karte.yaml`
   - Garten: `pflanzen-templates.yaml` mit `pflanzen-view.yaml`
   - Hausgeräte: `hausgeraete-templates.yaml` mit `geschirrspueler-karte.yaml`,
     `trockner-karte.yaml`, `waschmaschine-karte.yaml`
   - Klima: `heizung-templates.yaml`, `warnlage-templates.yaml`,
     `wetter-templates.yaml` mit `thermostate-karte-v3.yaml`,
     `meteoalarm-karte.yaml`, `pollenflug-karte.yaml`, `wetter-karte-v2.yaml`,
     `wetter-view.yaml` und `welcome-banner-karte.yaml` (allgemein)
   - Netzwerk: `docker-templates.yaml` mit allen `docker-*-karte.yaml`
   - Sonstiges: `kameras-templates.yaml` mit `kameras-view.yaml`
4. Die übrigen Karten nach und nach neu einfügen; bis dahin fehlt ihnen nur
   der helle Modus.
5. Wenn kein Dashboard mehr `owlet` enthält (Rohkonfiguration durchsuchen,
   ausgenommen `owlet_sock` und die Smart-Sock-Karte): `/config/themes/owlet.yaml`
   löschen und `frontend.reload_themes` ausführen.
