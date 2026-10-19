---
name: platzhalter-einsetzen
description: Anonymisierte Platzhalter (person.bewohner, sensor.iphone_*, notify.mobile_app_iphone, sensor.pv_anlage_*, weather.wohnort, sensor.warnregion_*, Tankstellen (tankstelle_<n>), Verbandsgemeinde (VG Wohnort), Kennzeichen, unique_id, Seriennummern/MAC/FIN/IEEE/Vornamen in Entity-IDs, Benutzer-IDs) in einer Karte oder View aus diesem Repo durch die echten Entity-IDs der eigenen Home-Assistant-Instanz ersetzen. Verwenden, wenn eine Datei aus dem Repo in die Instanz uebernommen werden soll, wenn eine eingefuegte Karte leer bleibt oder "Entitaet nicht verfuegbar" meldet, und bevor neue oder geaenderte Dateien mit persoenlichen Angaben committet werden.
---

# Platzhalter einsetzen

Persoenliche Angaben sind im Repo anonymisiert. Die Platzhalter existieren in
keiner Instanz. Diese Anleitung beschreibt, wie sie fuer die eigene Instanz
aufgeloest werden, ohne dass die echten Werte ins Repo gelangen.

Die verbindliche Liste der Platzhalter steht in `design/platzhalter.yaml`
(id, Suchmuster, Bedeutung, wo die echte ID zu finden ist), erklaert in
`README.md`, Abschnitt "Platzhalter ersetzen". Zuerst dort lesen; diese Datei
wiederholt sie nicht.

## Grundregeln

- Echte Werte (Namen, Geraetenamen, Adresse, Kennzeichen, echte Entity-IDs
  mit Personenbezug) **nie** ins Repo schreiben: nicht in Dateien, nicht in
  Commit-Nachrichten, nicht in PR-Texten oder PR-Kommentaren.
- Angepasste Fassungen nur unter `lokal/` ablegen (in `.gitignore`) oder
  direkt in die Instanz schreiben, nie im Repo-Dateibaum daneben.
- Keine Entity-ID raten. Jede Zuordnung stammt aus der Instanz oder vom
  Nutzer und wird vor der Verwendung bestaetigt.

## Ablauf: Datei fuer die Instanz vorbereiten

1. **Platzhalter in der Zieldatei finden.** Die Zeile `Platzhalter:` im
   Kopfblock der Datei lesen und die Datei mit den Mustern aus
   `design/platzhalter.yaml` durchsuchen, z. B.:
   `grep -nE 'person\.bewohner|sensor\.iphone_|notify\.mobile_app_iphone|pv_anlage_|AB - (CD 123|EF 456)|passat_(fenster|tueren)_kombiniert|<breite>|<laenge>|seriennr|shelly[a-z0-9]*_mac|fin_(passat|touran)|ieee_adresse|kind_[12]|benutzer_id_[12]|weather\.wohnort|sensor\.warnregion_|[Tt]ankstelle[ _][1-4]|VG Wohnort' <datei>`
   Fuer jeden Treffer die Suffixe notieren (z. B. `battery_level`,
   `hausbedarf`).

2. **Echte IDs ermitteln.**
   - Mit Home-Assistant-MCP: per `ha_search` nach den Suffixen suchen
     (z. B. `query="battery_level"`, `domain_filter="sensor"`; Personen mit
     `domain_filter="person"`). Ein Praefix gilt nur dann als gefunden, wenn
     er **alle** Suffixe der Datei abdeckt. Danach mit `ha_get_state` (Liste)
     pruefen, dass jede Ziel-ID existiert und nicht `unavailable` ist.
   - Ohne MCP oder bei mehreren Kandidaten: den Nutzer nach dem Praefix
     fragen (z. B. "Wie heisst dein Geraet in der Mobile-App-Integration?").
   - `unique_id` in `autos-passat-konfig.yaml`: die bisherige `unique_id`
     aus der eigenen Konfiguration erfragen. Eine neue `unique_id` legt in HA
     eine neue Entity an.
   - Kennzeichen sind reiner Anzeigetext: den Nutzer fragen oder leer lassen.
   - `benutzer_id_1`/`benutzer_id_2` in `visible:` / `condition: user`:
     Benutzer-IDs der Instanz. Den Nutzer fragen, welcher Benutzer jeweils
     gemeint ist, oder ihn bitten, den Benutzer im View- bzw. Karteneditor
     unter *Sichtbarkeit* auszuwaehlen (HA setzt die ID dann selbst ein).

3. **Zuordnung vorlegen.** Tabelle Platzhalter -> echte ID mit Anzahl der
   Ersetzungen zeigen und Bestaetigung abwarten.

4. **Angepasste Fassung erzeugen** unter `lokal/<dateiname>`, nur durch
   Ersetzen der bestaetigten Praefixe. Danach erneut mit dem grep aus
   Schritt 1 pruefen: In `lokal/` darf kein Platzhalter uebrig sein.

5. **In die Instanz uebernehmen** (nur auf ausdrueckliche Anweisung):
   - Standard: Der Nutzer fuegt `lokal/<datei>` selbst ein (Karte
     hinzufuegen -> Manuell, bzw. Raw-Konfigurationseditor).
   - Per MCP: vorher den Best-Practices-Skill des Home-Assistant-MCP lesen,
     das Ziel-Dashboard mit `ha_config_get_dashboard` laden, die Aenderung
     zeigen und erst nach Freigabe mit `ha_config_set_dashboard` (Modus
     `patch` oder `python_transform`, mit `config_hash`) schreiben.
     `ha_config_set_dashboard` bearbeitet nur Dashboards im Storage-Modus;
     Views mit `!include` liegen in YAML-Dashboards und werden als Datei
     im HA-Konfigurationsordner gepflegt.

## Ablauf: Aenderungen am Repo

- Neue oder geaenderte Karten verwenden die vorhandenen Platzhalter.
- Taucht eine neue persoenliche Angabe auf, einen neutralen Platzhalter
  einfuehren: zuerst in `design/platzhalter.yaml` eintragen, dann die Zeile
  `Platzhalter:` im Kopfblock der Datei ergaenzen und
  `python ci/gen_index.py` laufen lassen (erzeugt die Tabelle im README). `ci/check_kopf.py` meldet Dateien, deren
  Kopfzeile nicht zu den gefundenen Platzhaltern passt.
- Vor jedem Commit `git diff --cached` auf echte Werte pruefen, die in
  dieser Sitzung aufgeloest wurden, und `lokal/` darf nicht gestaged sein
  (`git status --short lokal/` muss leer sein).
