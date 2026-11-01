# Bewässerung: Frostschutz im Winter

Betrifft: Gartenbewässerung mit Brunnenpumpe hinter einem Shelly Outdoor Plug
S Gen3 und drei Bewässerungsaktoren ELV-SH-WSM (Homematic IP), Karte
[`garten-karte.yaml`](../dashboard/garten/garten-karte.yaml).
Stand dieser Notiz: 2026-11-01, Instanz auf **Core 2026.10.4**.

## Worum es geht

Im Winter sind die Ventile abgebaut und die Gartenleitung ist entleert.
Gefährdet bleibt die fest im Brunnen verbaute Pumpe: Läuft sie versehentlich
an, füllt sie die leere Leitung wieder mit Wasser, das gefrieren kann.

Der Helfer `input_boolean.bewasserung_frostschutz` ist der Hauptschalter dafür.
Er wird **nur von Hand** geschaltet; keine Automation setzt ihn.

## Schutzschichten

| Schicht | Wirkung | Grenze |
|---|---|---|
| Pumpe abgesteckt | fördert sicher nichts, egal was schaltet | Handgriff im Herbst und im Frühjahr |
| Shelly: Einschaltzustand nach Stromausfall `off`, kein „Automatisch ein“, keine Zeitpläne auf dem Gerät | Pumpe läuft nach Netzwiederkehr nicht von selbst an | gilt ganzjährig; Taste, App und HA schalten weiter |
| Automation „Bewässerung: Frostschutz-Sperre“ | schaltet die Pumpe bei Frostschutz sofort wieder aus, schließt geöffnete Ventile, meldet jeden Versuch | wirkt erst nach dem Einschalten, siehe Messung |
| Bedingung im „Zonen-Timer“ | ein geöffnetes Ventil startet bei Frostschutz weder Pumpe noch Timer | nur der Weg über die Ventile |
| Garten-Karte | Kacheln nehmen bei Frostschutz kein Tippen an | nur die Karte |
| Pumpe nicht für Assist freigegeben | Sprachbefehl findet die Pumpe nicht | – |

Home Assistant kann einen Schaltbefehl nicht ablehnen, und die Shelly-API nennt
keine Einstellung, die Befehle aus App, Cloud oder API sperrt (`in_locked` gilt
nur für die Taste). Software hält einen Anlauf deshalb nur kurz. Null Liter
garantiert nur die abgesteckte Pumpe.

**Regel für Automationen:** Wer Pumpe oder Ventil einschaltet, prüft den
Frostschutz. Wer ausschaltet oder schließt, prüft ihn nie; sonst fällt genau
die Abschaltung weg, die im Winter schützt.

## Messwerte

- Test am 01.11.2026 mit abgesteckter Pumpe: Shelly per HA eingeschaltet, laut
  HA nach **0,106 s** wieder aus (Zeit zwischen den beiden Zustandsmeldungen;
  das Relais kann etwas länger geschlossen gewesen sein).
- Pumpe ≈ 1,2 kW, Durchfluss je Zone 15–21 L/min (Monatsmaxima Mai bis
  Oktober 2026). Rechnerisch fördert die Pumpe bei 20 L/min in 1 s etwa
  0,3 L. Ohne Ventil kann sie mehr fördern; maßgeblich ist das Typenschild.

## Herbst

1. Letzte Bewässerung.
2. **Frostschutz einschalten** (Karte, Rückfrage bestätigen). Push „Frostschutz
   an“ abwarten. Ab jetzt fördert die Pumpe auch während der folgenden Arbeiten
   nichts.
3. Ventile abbauen: Wasserhahn zu, Gerät abnehmen, Filterdichtung reinigen.
   Lagern trocken und so, dass Restwasser abfließen kann. Die Batterien bleiben
   drin, damit HA die Lagertemperatur sieht (die ELV-Anleitung sieht vor, das
   Batteriefach zu entnehmen).
4. Gartenleitung entlüften und entleeren.
5. **Pumpe im Pumpenhaus abstecken.**

## Frühjahr

1. Leitung anschließen. Batteriestand der Ventile prüfen
   (`binary_sensor.*_batterie`), bei Bedarf tauschen; laut ELV hält ein Satz
   typisch 1 Jahr. Ventile montieren.
2. **Pumpe einstecken.** Der Frostschutz ist noch an und hält sie aus.
3. **Frostschutz ausschalten** (Karte, Rückfrage bestätigen).
4. Testbewässerung, jede Zone mehrfach schalten, um Ablagerungen auszuspülen;
   Leitung auf Dichtheit prüfen.

## Ventile in der Garage

Laut ELV ist der Bewässerungsaktor „nicht frostsicher und muss vor
Frosteinbruch demontiert und frostsicher gelagert werden. Der Aktor stellt
unter 5 °C den Betrieb ein und schließt automatisch.“ Die eigene Frostfunktion
schützt also die Bewässerung, nicht das Gerät. Für Frostschäden übernimmt ELV
keine Haftung.

Die Automation „Bewässerung: Frostwarnung Ventillager“ meldet bei Frostschutz,
wenn eines der Geräte 30 min unter 3 °C misst (Auflösung 1 °C). Sie schaltet
nichts. Die Karte zeigt die Temperatur in den Ventilkacheln, ab 2 °C abwärts in
Amber. Ein `numeric_state`-Trigger löst nur beim Unterschreiten aus; eine
angehobene Schwelle über dem aktuellen Wert testet ihn deshalb nicht.

## Abnahme

| Test | Ergebnis 01.11.2026 |
|---|---|
| Frostschutz einschalten, Push „Frostschutz an“ | bestanden |
| Shelly per HA einschalten | bestanden, 0,106 s |
| Assist kennt die Pumpe nicht | bestanden (Freigabe aus) |
| Ventil in der Garage per HA öffnen | bestanden: zu nach 0,36 s, Zonen-Timer hielt an der Bedingung |
| Shelly-App, Taste, HA-Neustart mit eingeschaltetem Shelly, Stromausfall | offen, vor Ort |
| Frostwarnung | Text und Bedingung geprüft, Auslösung erst bei Kälte |

## Quellen

- ELV, Bau- und Bedienungsanleitung ELV-SH-WSM:
  <https://media.elv.com/file/254669_elv_sh_wsm.pdf>,
  <https://media.elv.com/file/161647_km.pdf>
- Shelly API, Switch (`initial_state`, `auto_on`, `auto_off`, `in_locked`):
  <https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Switch/>
- Shelly API, Outdoor Plug S Gen3:
  <https://shelly-api-docs.shelly.cloud/gen2/Devices/Gen3/ShellyOutdoorPlugSG3>
