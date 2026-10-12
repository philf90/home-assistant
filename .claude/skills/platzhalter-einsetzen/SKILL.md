---
name: platzhalter-einsetzen
description: Anonymisierte Platzhalter (person.bewohner, sensor.iphone_*, notify.mobile_app_iphone, sensor.pv_anlage_*, Kennzeichen, unique_id) in einer Karte oder View aus diesem Repo durch die echten Entity-IDs der eigenen Home-Assistant-Instanz ersetzen. Verwenden, wenn eine Datei aus dem Repo in die Instanz uebernommen werden soll, wenn eine eingefuegte Karte leer bleibt oder "Entitaet nicht verfuegbar" meldet, und bevor neue oder geaenderte Dateien mit persoenlichen Angaben committet werden.
---

# Platzhalter einsetzen

Persoenliche Angaben sind im Repo anonymisiert. Die Platzhalter existieren in
keiner Instanz. Diese Anleitung beschreibt, wie sie fuer die eigene Instanz
aufgeloest werden, ohne dass die echten Werte ins Repo gelangen.

Die verbindliche Liste der Platzhalter steht in `README.md`, Abschnitt
"Platzhalter ersetzen". Zuerst dort lesen; diese Datei wiederholt sie nicht.

## Grundregeln

- Echte Werte (Namen, Geraetenamen, Adresse, Kennzeichen, echte Entity-IDs
  mit Personenbezug) **nie** ins Repo schreiben: nicht in Dateien, nicht in
  Commit-Nachrichten, nicht in PR-Texten oder PR-Kommentaren.
- Angepasste Fassungen nur unter `lokal/` ablegen (in `.gitignore`) oder
  direkt in die Instanz schreiben, nie im Repo-Dateibaum daneben.
- Keine Entity-ID raten. Jede Zuordnung stammt aus der Instanz oder vom
  Nutzer und wird vor der Verwendung bestaetigt.

## Ablauf: Datei fuer die Instanz vorbereiten

1. **Platzhalter in der Zieldatei finden.** Kopfkommentar
   `HINWEIS PLATZHALTER` lesen und die Datei durchsuchen:
   `grep -nE 'person\.bewohner|sensor\.iphone_|notify\.mobile_app_iphone|pv_anlage_|AB - (CD 123|EF 456)|passat_(fenster|tueren)_kombiniert|<breite>|<laenge>' <datei>`
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
   - `unique_id` in `template-autos-passat.yaml`: die bisherige `unique_id`
     aus der eigenen Konfiguration erfragen. Eine neue `unique_id` legt in HA
     eine neue Entity an.
   - Kennzeichen sind reiner Anzeigetext: den Nutzer fragen oder leer lassen.
   - Benutzer-IDs in `visible:` / `condition: user` sind instanzgebunden.
     Bei Abweichung den Nutzer bitten, sie im Karteneditor unter
     *Sichtbarkeit* neu auszuwaehlen.

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
  einfuehren, den Kopfkommentar `HINWEIS PLATZHALTER` der Datei ergaenzen
  und die Tabelle in `README.md` erweitern.
- Vor jedem Commit `git diff --cached` auf echte Werte pruefen, die in
  dieser Sitzung aufgeloest wurden, und `lokal/` darf nicht gestaged sein
  (`git status --short lokal/` muss leer sein).
