# Live Activities (iOS) / Live Updates (Android)

Analyse der Instanz: **welche Entitäten eignen sich**, und **wie es implementiert wird**.
Stand: HA Core 2026.9.2 · geprüft am 14.09.2026 gegen die Live-Instanz.

Fertige Automationen: [`live-activities-hausgeraete.yaml`](live-activities-hausgeraete.yaml)

---

## 1. Voraussetzungen (in dieser Instanz erfüllt)

| Anforderung | Status |
| --- | --- |
| HA Core ≥ 2026.7.0 | ✅ 2026.9.2 |
| iOS ≥ 17.2 | ✅ `notify.mobile_app_philipps_iphone17pro` (iPhone 17 Pro → Dynamic Island) |
| Android ≥ 16 | ⚠️ prüfen: `notify.mobile_app_samsung_s25`, `notify.mobile_app_s23_annalena` |
| Companion-App | ⚠️ Feature ist in **Labs/Beta** – iOS: *Einstellungen → Live Activities* |

**iPad kann keine Live Activities** (Apple-Limitierung). `notify.mobile_app_ipad_pro_philipp`
und `notify.mobile_app_ipad_von_philipp_2` scheiden damit aus.

---

## 2. Primär: Hausgeräte (Siemens / Home Connect)

Alle drei Geräte hängen an der HACS-Integration `home_connect_alt` und liefern exakt
die Felder, die eine Live Activity braucht. Entity-IDs sind die Home-Connect-HA-IDs.

| Gerät | Entity-Präfix `sensor.<ID>_…` | Eignung |
| --- | --- | --- |
| Waschmaschine | `484090394196000250` | ⭐⭐⭐ |
| Trockner | `463120392821005583` | ⭐⭐⭐ |
| Geschirrspüler | `013120394858001191` | ⭐⭐⭐ |

### Die relevanten Entitäten pro Gerät

| Zweck | Entity | Bemerkung |
| --- | --- | --- |
| **Trigger-Quelle** | `sensor.<ID>_bsh_common_status_operationstate` | nur 4–6 Wechsel pro Zyklus → ideal |
| **Countdown** | `sensor.<ID>_bsh_common_option_remainingprogramtime` | `device_class: timestamp` → direkt als `when` nutzbar |
| Fortschritt % | `sensor.<ID>_bsh_common_option_programprogress` | **nicht als Trigger** – siehe Abschnitt 4 |
| Programmname | `sensor.<ID>_active_program` / `_selected_program` | Enum, z. B. `LaundryCare.Dryer.Program.Towels` |
| Prozessphase | `sensor.<ID>_laundrycare_common_option_processphase` | nur Waschmaschine + Trockner |
| Tür (Ende erkennen) | `binary_sensor.<ID>_bsh_common_status_doorstate` | „ausgeräumt“ → Activity beenden |
| Verbindung | `binary_sensor.<ID>_connected` | Guard gegen `unavailable`-Flattern |

### Gemessene Zustandsfolge (Historie, 10 Tage)

```
Inactive → Ready → Run → Finished → Ready → Inactive
```

Reale Zyklen aus der Instanz:

| Gerät | Lauf | Dauer |
| --- | --- | --- |
| Waschmaschine | 13.09. 11:40 → 13:32 | 112 min |
| Trockner | 13.09. 11:36 → 14:14 | 158 min |
| Trockner | 13.09. 14:25 → 16:30 | 125 min |
| Geschirrspüler | 12.09. 22:27 → 23:30 | 63 min |

Laufzeiten von 1–2,5 h liegen komfortabel unter dem **8-Stunden-Limit** von Apple.

---

## 3. Zwei Fallstricke, die in dieser Instanz real auftreten

### 3.1 `unavailable`-Flattern der Home-Connect-Cloud

Am 08./09.09. wechselten alle drei Geräte **15–18×** zwischen `Inactive` und `unavailable`.
Ein Trigger ohne `to:`-Einschränkung würde daraus je einen Push machen und das
iOS-Push-Budget verbrennen (danach starten neue Activities **stillschweigend nicht mehr**).

→ **Gegenmittel:** immer explizit `to: "BSH.Common.EnumType.OperationState.…"` triggern.
`unavailable` ist dann nie ein Trigger-Ziel.

### 3.2 Start-Flattern des Trockners

```
13.09. 11:36:07  Run
13.09. 11:36:09  Ready      ← 2 Sekunden
13.09. 11:36:09  Run
```

→ **Gegenmittel:** `for: "00:00:05"` auf den Start-Trigger. Der erste Run-Blitz feuert
nicht mehr, der echte Start nach 5 s schon.

---

## 4. Warum `programprogress` kein Trigger sein darf

Gemessen an einem Waschgang vom 13.09.: der Sensor läuft **jede Minute um 1 % hoch**,
**113 Zustandsänderungen** in einem einzigen Zyklus.

Die Companion-Doku führt genau das unter „❌ Avoid – reacting to a fast-changing sensor“.
113 Pushes pro Waschgang → iOS drosselt und verwirft die Updates.

**Die Lösung braucht gar keine Zwischen-Pushes:**

```yaml
chronometer: true                  # Timer tickt auf dem Gerät
when: <Unix-Timestamp der Restzeit> # aus remainingprogramtime
progress_bar_direction: increasing  # Balken füllt sich von selbst mit
```

Damit entstehen **4–6 Pushes pro Zyklus** statt 113 — Countdown und Fortschrittsbalken
laufen lokal auf dem iPhone weiter.

---

## 5. Weitere sinnvolle Kandidaten in dieser Instanz

| Kandidat | Entitäten | Bewertung |
| --- | --- | --- |
| **Saugroboter** | `vacuum.roborock_s6_maxv`, `sensor.roborock_s6_maxv_status`, `…_aktueller_raum`, `…_batterie` | ⭐⭐⭐ Klassischer Live-Activity-Fall: definierter Anfang/Ende, 30–60 min, `Aktueller Raum` als `critical_text`. Keine Restzeit → `chronometer` als Count-**up**. |
| **Mähroboter** | `lawn_mower.a2`, `sensor.a2_state`, `sensor.a2_battery_level` | ⭐⭐⭐ Wie Saugroboter, zusätzlich Akkustand als `progress`. Nur saisonal relevant. |
| **Bewässerung** | `valve.bewasserung_vorne/mitte/hinten`, `input_boolean.bewasserung_garten` | ⭐⭐ Kurze, klar begrenzte Läufe – `chronometer` mit fester Laufzeit, keine Restzeit-Entity nötig. |
| **Paketzustellung** | `input_boolean.paket_vor_der_tur`, `input_datetime.paket_erkannt_um`, `event.haustur_paket` | ⭐⭐ In der Doku explizit als Anwendungsfall genannt. Count-**up** seit `paket_erkannt_um`, Ende beim Hereinholen. |
| **Alarmanlage** | `alarm_control_panel.udm_se_alarm_manager` | ⭐⭐ `arming`/`pending` sind kurze, dringende Zustände – genau wofür die Dynamic Island gedacht ist. Aktuell `disarmed`. |
| **Backup** | `ha_manage_backup` / Backup-Sensoren | ⭐ Läuft meist nachts, niemand schaut hin. |
| **Müllabfuhr** | `calendar.mull`, `sensor.muell_termine` | ⭐ Eher eine normale Benachrichtigung am Vorabend. Eine Live Activity über 8 h abzubrennen lohnt nicht. |
| **E-Auto-Ladung** | – | ❌ **Nicht anwendbar.** Beide VW sind Diesel (`adblue_reichweite`); `elektrische_reichweite` ist `unavailable`, `calendar.…_ladeplan` ebenfalls. Zusätzlich hat `volkswagencarnet` offene Reauth-Reparaturen und alle Passat-Entitäten stehen auf `unavailable`. |
| **Energie / PV / Solarbank** | `sensor.solarbank_*`, Hausverbrauch | ❌ Dauerzustand ohne Anfang und Ende, dazu sekündlich wechselnde Werte. Genau der Anti-Pattern-Fall der Doku. Gehört auf ein Dashboard, nicht auf den Lockscreen. |
| **Temperaturen / Fenster / Lichter** | – | ❌ Kein Vorgang mit Verlauf – normale Benachrichtigungen sind hier richtig. |

**Faustregel:** Eine Live Activity lohnt sich, wenn ein Vorgang einen **klaren Anfang, ein
absehbares Ende und eine Laufzeit zwischen ~5 min und 8 h** hat. Alles Dauerhafte gehört
aufs Dashboard, alles Punktuelle in eine normale Push-Nachricht.

---

## 6. Feldreferenz (Companion-App)

`title` und `message` stehen auf der **oberen** `data:`-Ebene, alles andere im **verschachtelten**
`data.data:`-Block.

| Feld | Typ | Bedeutung |
| --- | --- | --- |
| `tag` | string | **Pflicht.** Identität der Activity, max. 64 Zeichen. Gleicher Tag = Update statt neuer Activity. |
| `live_update` | bool | `true` startet bzw. aktualisiert die Live Activity. |
| `title` | string | Kopfzeile. Wird beim Start gesetzt und **kann später nicht mehr geändert werden**. Auf Android Pflicht. |
| `message` | string | Fließtext. Wird von `chronometer` verdrängt. |
| `critical_text` | string | Kurztext. Wird von `progress` verdrängt; in der Dynamic Island immer sichtbar. |
| `progress` / `progress_max` | int | Fortschrittsbalken. |
| `chronometer` | bool | Live-Timer. Benötigt `when`. |
| `when` | number | Unix-Timestamp – oder Sekunden ab jetzt, wenn `when_relative: true`. |
| `when_relative` | bool | `when` als Sekunden ab jetzt interpretieren. |
| `notification_icon` | string | MDI-Slug, z. B. `mdi:washing-machine`. |
| `notification_icon_color` | string | *(iOS)* Hex-Farbe für Icon und Balken. |
| `color` | string | *(Android)* Hex-Farbe für das Icon. |
| `progress_bar_direction` | string | *(iOS)* `increasing` / `decreasing`. |
| `background_color` / `text_color` | string | *(iOS)* Farben der Lockscreen-Karte. Default schwarz. |
| `url` | string | *(iOS)* Ziel beim Antippen, z. B. `/lovelace/hausarbeit`. Gilt **nur für das Update, mit dem es gesendet wird**. |
| `silent` | bool | *(iOS)* Update ohne Ton, niedrigere Priorität. Beim Start wirkungslos. |

**Beenden** – identisch auf iOS und Android:

```yaml
- action: notify.mobile_app_philipps_iphone17pro
  data:
    message: "clear_notification"
    data:
      tag: waschmaschine
```

---

## 7. Schnelltest ohne Automation

*Entwicklerwerkzeuge → Aktionen → YAML-Modus:*

```yaml
action: notify.mobile_app_philipps_iphone17pro
data:
  title: "Waschmaschine"
  message: "Testlauf"
  data:
    tag: test-live-activity
    live_update: true
    chronometer: true
    when: 600
    when_relative: true
    progress_bar_direction: increasing
    notification_icon: mdi:washing-machine
    notification_icon_color: "#2196F3"
```

Aufräumen nicht vergessen – sonst zählt der Testlauf gegen das Push-to-Start-Budget:

```yaml
action: notify.mobile_app_philipps_iphone17pro
data:
  message: "clear_notification"
  data:
    tag: test-live-activity
```

> **Warnung zum Testen:** Wiederholtes Starten und Beenden verbraucht das
> Push-to-Start-Budget von iOS. Ist es leer, starten neue Activities **stillschweigend
> nicht mehr** – die Automation meldet Erfolg, HA loggt nichts, das Gerät bleibt still.
> Das Budget füllt sich nach Minuten bis Stunden von selbst wieder auf; ein Neustart
> des iPhones hilft nicht.

---

## Quellen

- [Live Activities and Live Updates – Home Assistant Companion Docs](https://companion.home-assistant.io/docs/notifications/live-activities/)
- [Native iOS Live Activities (ActivityKit) support – Discussion #3828](https://github.com/orgs/home-assistant/discussions/3828)
- [Apple: Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities#Understand-constraints)
