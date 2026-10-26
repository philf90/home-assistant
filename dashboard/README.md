<!-- Erzeugt von ci/gen_index.py aus den Kopfbloecken der Dateien. Nicht von Hand aendern, sondern die Koepfe pflegen und `python ci/gen_index.py` laufen lassen. -->

# Dashboard-Dateien

Alle Karten, Views, Templates, Konfig-Dateien und Entwürfe nach Bereich. Titel, Karten, Platzhalter und Status stammen aus dem Kopfblock jeder Datei (Aufbau: [`ci/README.md`](../ci/README.md), Abschnitt „Dateikopf“). Wie die Dateien eingefügt werden und was die Platzhalter bedeuten, steht im [README](../README.md).

## allgemein

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`navbar-karte.yaml`](allgemein/navbar-karte.yaml) | karte | Navbar – schwebende Navigation unten | button-card, navbar-card | `benutzer_id_1/benutzer_id_2` | aktiv |
| [`navigation-templates.yaml`](allgemein/navigation-templates.yaml) | templates | Navigation – Decluttering-Templates top_navigation und floating_navbar | button-card, navbar-card | `benutzer_id_1/benutzer_id_2` | aktiv |
| [`owlet-theme-konfig.yaml`](allgemein/owlet-theme-konfig.yaml) | konfig | Owlet-Theme – Farben fuer den hellen und den dunklen Modus | – | – | aktiv |
| [`top-navigation-karte.yaml`](allgemein/top-navigation-karte.yaml) | karte | Top-Navigation – Launcher-Raster | button-card | – | aktiv |
| [`welcome-banner-karte.yaml`](allgemein/welcome-banner-karte.yaml) | karte | Begruessungs-Banner mit Wetterszene | button-card | `weather.wohnort` | aktiv |
| [`banner-hell.html`](allgemein/entwuerfe/banner-hell.html) | entwurf | Begruessungs-Banner im hellen Modus – Entwurf und Kontrastrechnung | – | – | Entwurf zu `welcome-banner-karte.yaml` |
| [`home-kacheln.html`](allgemein/entwuerfe/home-kacheln.html) | entwurf | Kachel-Vorschlaege fuer die Home-Ansicht | – | – | Entwurf |

## energie

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`energie-flow-karte.yaml`](energie/energie-flow-karte.yaml) | karte | Energiefluss – animiertes Diagramm mit Autarkie | button-card, card-mod | `sensor.pv_anlage_*` | aktiv |
| [`energie-monatsbilanz-karte.yaml`](energie/energie-monatsbilanz-karte.yaml) | karte | Monatsbilanz Strom – Netzbezug, Solarertrag, Autarkie je Monat | apexcharts-card, auto-entities, button-card, card-mod | `sensor.pv_anlage_*` | aktiv |
| [`energie-solarbank-pv-karte.yaml`](energie/energie-solarbank-pv-karte.yaml) | karte | Solarbank & PV | button-card, card-mod | `sensor.pv_anlage_*` | aktiv |
| [`energie-templates.yaml`](energie/energie-templates.yaml) | templates | Energie – button-card-Templates der Energie-View | – | `sensor.pv_anlage_*` | aktiv |
| [`energie-verbraucher-karte.yaml`](energie/energie-verbraucher-karte.yaml) | karte | Verbraucher – Leistung, kWh heute und Anteil | button-card, card-mod | `sensor.pv_anlage_*` | aktiv |
| [`energie-zaehler-karte.yaml`](energie/energie-zaehler-karte.yaml) | karte | Zaehler – Strom und Gas | button-card, card-mod | – | aktiv |
| [`energiefluss.html`](energie/entwuerfe/energiefluss.html) | entwurf | Energiefluss neu gedacht – Entwurf und Messwerte | – | `sensor.pv_anlage_*` | Entwurf zu `energie-flow-karte.yaml` |
| [`energie-autarkie-karte.yaml`](energie/archiv/energie-autarkie-karte.yaml) | karte | Autarkie-Ring | button-card, card-mod | `sensor.pv_anlage_*` | archiv, ersetzt durch `energie-flow-karte.yaml` |
| [`energie-diagramme-karte.yaml`](energie/archiv/energie-diagramme-karte.yaml) | karte | Energie-Diagramme – Sankey und Power-Flow | button-card, card-mod, power-flow-card-plus, sankey-chart | `sensor.pv_anlage_*` | archiv |
| [`energie-flow-leiste-karte.yaml`](energie/archiv/energie-flow-leiste-karte.yaml) | karte | Energiefluss – Verbraucher-Leiste (Konzept B) | button-card, card-mod | `sensor.pv_anlage_*` | archiv, ersetzt durch `energie-flow-karte.yaml` |
| [`energie-pv-karte.yaml`](energie/archiv/energie-pv-karte.yaml) | karte | Energie & PV – Akku-Ring und Live-Kacheln | button-card, card-mod | `sensor.pv_anlage_*` | archiv, ersetzt durch `energie-solarbank-pv-karte.yaml` |
| [`energie-verbrauch-uebersicht-karte.yaml`](energie/archiv/energie-verbrauch-uebersicht-karte.yaml) | karte | Verbrauchs-Uebersicht – Verbraucher live und Top-Verbraucher | button-card, card-mod | – | archiv, ersetzt durch `energie-verbraucher-karte.yaml` |
| [`gas-wasser-karte.yaml`](energie/archiv/gas-wasser-karte.yaml) | karte | Gas- und Wasserverbrauch | button-card, card-mod | – | archiv, ersetzt durch `energie-zaehler-karte.yaml` |

## klima

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`heizung-templates.yaml`](klima/heizung-templates.yaml) | templates | Heizungs-Animation – button-card-Template owlet_heizung_fx | – | – | aktiv |
| [`meteoalarm-karte.yaml`](klima/meteoalarm-karte.yaml) | karte | DWD-Wetterwarnung | button-card | `sensor.warnregion_*` | aktiv |
| [`pollenflug-karte.yaml`](klima/pollenflug-karte.yaml) | karte | Pollenflug-Index | button-card | – | aktiv |
| [`temperaturen-karte-v2.yaml`](klima/temperaturen-karte-v2.yaml) | karte | Temperaturen v2 – Raumliste mit 24-h-Sparkline | button-card, card-mod | `*_seriennr`, `kind_1/kind_2` | aktiv |
| [`thermostate-karte-v3.yaml`](klima/thermostate-karte-v3.yaml) | karte | Thermostate v3 – radiale Regler mit Animation und Fenster offen | button-card, card-mod | – | aktiv |
| [`warnlage-templates.yaml`](klima/warnlage-templates.yaml) | templates | Warnlage – Popups fuer DWD-Warnungen und Pollenflug | button-card | `sensor.warnregion_*` | aktiv |
| [`wetter-karte-v2.yaml`](klima/wetter-karte-v2.yaml) | karte | Wetter v2 – eine Karte mit Wetter, Wind und Sonne | button-card | `weather.wohnort` | aktiv |
| [`wetter-templates.yaml`](klima/wetter-templates.yaml) | templates | Wetter-Animation – button-card-Template owlet_wetter_fx | – | – | aktiv |
| [`wetter-view.yaml`](klima/wetter-view.yaml) | view | Wetter – komplette Ansicht | button-card, card-mod, decluttering-card | `sensor.warnregion_*` | aktiv |
| [`wetter-animiert.html`](klima/entwuerfe/wetter-animiert.html) | entwurf | Wetter-Animationen – Entwurf und Kontrastrechnung | – | – | Entwurf zu `wetter-templates.yaml` |
| [`temperaturen-karte.yaml`](klima/archiv/temperaturen-karte.yaml) | karte | Raum-Temperaturen v1 | button-card, card-mod | `*_seriennr`, `kind_1/kind_2` | archiv, ersetzt durch `temperaturen-karte-v2.yaml` |
| [`thermostate-karte-v2.yaml`](klima/archiv/thermostate-karte-v2.yaml) | karte | Thermostate v2 – radiale Soll-Regler | button-card, card-mod | – | archiv, ersetzt durch `thermostate-karte-v3.yaml` |
| [`thermostate-karte.yaml`](klima/archiv/thermostate-karte.yaml) | karte | Thermostate v1 | button-card, card-mod | – | archiv, ersetzt durch `thermostate-karte-v2.yaml` |
| [`wetter-karte.yaml`](klima/archiv/wetter-karte.yaml) | karte | Wetter – animierte Szene, Kennzahlen, Vorhersage | button-card | `weather.wohnort` | archiv, ersetzt durch `wetter-karte-v2.yaml` |

## licht

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`fenster-karte.yaml`](licht/fenster-karte.yaml) | karte | Fenster & Tueren – Status | button-card | – | aktiv |
| [`fenster-lichter-karte.yaml`](licht/fenster-lichter-karte.yaml) | karte | Fenster & Lichter – Kachel | button-card | – | aktiv |
| [`haustuer-ereignis-karte.yaml`](licht/haustuer-ereignis-karte.yaml) | karte | Haustuer-Ereignis | button-card | – | aktiv |
| [`haustuer-lock-karte.yaml`](licht/haustuer-lock-karte.yaml) | karte | Haustuer-Schloss | button-card | – | aktiv |
| [`lichter-glow-karte.yaml`](licht/lichter-glow-karte.yaml) | karte | Lichter – Variante Glow-Kacheln | button-card, card-mod | `*_mac`, `kind_1/kind_2` | aktiv |
| [`lichter-mushroom-karte.yaml`](licht/lichter-mushroom-karte.yaml) | karte | Lichter & Steckdosen – Variante Mushroom | button-card, card-mod, mushroom-entity-card, mushroom-light-card | `*_mac`, `kind_1/kind_2` | aktiv |
| [`lichter-raum-karte.yaml`](licht/lichter-raum-karte.yaml) | karte | Lichter – Variante Raum-Karten | button-card, card-mod | `*_mac`, `kind_1/kind_2` | aktiv |
| [`lichter-slider-karte.yaml`](licht/lichter-slider-karte.yaml) | karte | Lichter & Steckdosen – Variante Slider | button-card, card-mod, slider-button-card | `*_mac`, `kind_1/kind_2` | aktiv |
| [`fenster-lichter-uebersicht-karte.yaml`](licht/archiv/fenster-lichter-uebersicht-karte.yaml) | karte | Fenster & Tueren, Lichter & Steckdosen – grosse Ansicht | bubble-card, button-card, card-mod | `*_mac`, `kind_1/kind_2` | archiv |

## hausgeraete

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`geschirrspueler-karte.yaml`](hausgeraete/geschirrspueler-karte.yaml) | karte | Geschirrspueler (Home Connect) | button-card | `seriennr_<geraet>` | aktiv |
| [`hausgeraete-templates.yaml`](hausgeraete/hausgeraete-templates.yaml) | templates | Hausgeraete-Animation – button-card-Template owlet_geraete_fx | – | – | aktiv |
| [`trockner-karte.yaml`](hausgeraete/trockner-karte.yaml) | karte | Trockner (Home Connect) | button-card | `seriennr_<geraet>` | aktiv |
| [`waschmaschine-karte.yaml`](hausgeraete/waschmaschine-karte.yaml) | karte | Waschmaschine (Home Connect) | button-card | `seriennr_<geraet>` | aktiv |
| [`hausgeraete.html`](hausgeraete/entwuerfe/hausgeraete.html) | entwurf | Hausgeraete-View – Verbindung und Animation | – | `notify.mobile_app_iphone` | Entwurf zu `hausgeraete-templates.yaml` |
| [`staubsauger-karte.yaml`](hausgeraete/archiv/staubsauger-karte.yaml) | karte | Staubsauger mit Karte | button-card, mushroom-vacuum-card, xiaomi-vacuum-map-card | – | archiv |

## netzwerk

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`docker-container-karte.yaml`](netzwerk/docker-container-karte.yaml) | karte | Docker-Container – alle Container nach Compose-Projekt gruppiert | auto-entities, button-card, card-mod, expander-card | – | aktiv |
| [`docker-ereignisse-karte.yaml`](netzwerk/docker-ereignisse-karte.yaml) | karte | Docker-Ereignisse – Logbuch der Container und Push bei Absturz | button-card, card-mod | – | aktiv |
| [`docker-host-karte.yaml`](netzwerk/docker-host-karte.yaml) | karte | Docker-Host – Status, CPU, RAM, Disk und Versionen | button-card, card-mod | – | aktiv |
| [`docker-karte.yaml`](netzwerk/docker-karte.yaml) | karte | Docker – Container eines Docker-Hosts ueber Arcane | auto-entities, button-card, card-mod, expander-card | – | aktiv |
| [`docker-konfig.yaml`](netzwerk/docker-konfig.yaml) | konfig | Docker – Ereignisse, Absturzmeldung und Sammel-Update fuer die Docker-View | – | `notify.mobile_app_iphone` | aktiv |
| [`docker-projekte-karte.yaml`](netzwerk/docker-projekte-karte.yaml) | karte | Docker-Projekte – Compose-Projekte mit Start/Stop und Neustart | auto-entities, button-card, card-mod, expander-card | – | aktiv |
| [`docker-speicher-karte.yaml`](netzwerk/docker-speicher-karte.yaml) | karte | Docker-Speicher – Images, Volumes, Netzwerke und Aufraeumen | button-card, card-mod | – | aktiv |
| [`docker-templates.yaml`](netzwerk/docker-templates.yaml) | templates | Docker – button-card-Templates owlet_docker_* (Zeilen, Kopf, Kennzahlen) | button-card | – | aktiv |
| [`docker-uebersicht-karte.yaml`](netzwerk/docker-uebersicht-karte.yaml) | karte | Docker-Übersicht – Kennzahlen und "Braucht Aufmerksamkeit" | auto-entities, button-card, card-mod | – | aktiv |
| [`docker-updates-karte.yaml`](netzwerk/docker-updates-karte.yaml) | karte | Docker-Updates – Image-Updates der Container und von Arcane | auto-entities, button-card, card-mod | – | aktiv |
| [`docker-verlauf-karte.yaml`](netzwerk/docker-verlauf-karte.yaml) | karte | Docker-Verlauf – Container und Image-Speicher ueber 7 Tage | apexcharts-card, button-card, card-mod | – | aktiv |
| [`docker-view.yaml`](netzwerk/docker-view.yaml) | view | Docker – komplette Ansicht | decluttering-card | `benutzer_id_1/benutzer_id_2` | aktiv |
| [`homematic-view.yaml`](netzwerk/homematic-view.yaml) | view | Homematic IP – komplette Ansicht | button-card, card-mod, decluttering-card | `*_seriennr`, `kind_1/kind_2` | aktiv |
| [`netzwerk-view.yaml`](netzwerk/netzwerk-view.yaml) | view | Netzwerk – komplette Ansicht | decluttering-card | `benutzer_id_1/benutzer_id_2` | aktiv |
| [`system-karte.yaml`](netzwerk/system-karte.yaml) | karte | System – Home Assistant und Proxmox-VM | button-card, card-mod, uptime-card | – | aktiv |
| [`unifi-kabel-clients-konfig.yaml`](netzwerk/unifi-kabel-clients-konfig.yaml) | konfig | UniFi-Kabel-Clients – Switch und Port je Kabel-Client | – | – | aktiv |
| [`unifi-leitungen-karte.yaml`](netzwerk/unifi-leitungen-karte.yaml) | karte | Leitungen & Durchsatz | apexcharts-card, button-card, card-mod | – | aktiv |
| [`unifi-netzplan-card.js`](netzwerk/unifi-netzplan-card.js) | ressource | UniFi-Netzplan – custom:unifi-netzplan-card | – | – | aktiv |
| [`unifi-netzplan-karte.yaml`](netzwerk/unifi-netzplan-karte.yaml) | karte | UniFi-Netzplan – Karte | unifi-netzplan-card | – | aktiv |
| [`unifi-netzwerk-status-karte.yaml`](netzwerk/unifi-netzwerk-status-karte.yaml) | karte | Netzwerk-Status – Kopf der Netzwerk-View | button-card | – | aktiv |
| [`unifi-udm-system-karte-v2.yaml`](netzwerk/unifi-udm-system-karte-v2.yaml) | karte | UDM SE System v2 – CPU, RAM, Temperatur, PoE | button-card, card-mod | – | aktiv |
| [`unifi-unas-pro-karte.yaml`](netzwerk/unifi-unas-pro-karte.yaml) | karte | UNAS Pro – Speicher, CPU, RAM, Schaechte | button-card, card-mod | – | aktiv |
| [`unifi-verlauf-karte.yaml`](netzwerk/unifi-verlauf-karte.yaml) | karte | Netzwerk-Verlauf – aufklappbar | apexcharts-card, button-card, card-mod, expander-card, uptime-card | – | aktiv |
| [`wlan-karte-v2.yaml`](netzwerk/wlan-karte-v2.yaml) | karte | WLAN – Netzliste mit QR-Pop-ups | bubble-card, button-card, card-mod | `wlan_heim/wlan_gast` | aktiv |
| [`homematic-karte.yaml`](netzwerk/archiv/homematic-karte.yaml) | karte | Homematic IP / OpenCCU | button-card, card-mod, homematicip-system-health-card | `*_seriennr` | archiv, ersetzt durch `homematic-view.yaml` |
| [`unifi-udm-system-karte.yaml`](netzwerk/archiv/unifi-udm-system-karte.yaml) | karte | UDM SE Systemzustand v1 | button-card, card-mod | – | archiv, ersetzt durch `unifi-udm-system-karte-v2.yaml` |
| [`wlan-karte.yaml`](netzwerk/archiv/wlan-karte.yaml) | karte | WLAN-QR – aufklappbar | button-card, card-mod, expander-card | – | archiv, ersetzt durch `wlan-karte-v2.yaml` |

## fahrzeuge

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`autos-karte-v4.yaml`](fahrzeuge/autos-karte-v4.yaml) | karte | Autos v4 – mit Animationen | button-card, card-mod | `kennzeichen`, `fin_*` | aktiv |
| [`autos-passat-konfig.yaml`](fahrzeuge/autos-passat-konfig.yaml) | konfig | Passat – kombinierte Fenster- und Tueren-Sensoren | – | `kennzeichen`, `passat_*_kombiniert` | aktiv |
| [`autos-templates.yaml`](fahrzeuge/autos-templates.yaml) | templates | Auto-Animation – button-card-Template owlet_auto_fx | – | – | aktiv |
| [`fahrzeiten-karte.yaml`](fahrzeuge/fahrzeiten-karte.yaml) | karte | Fahrzeiten – Waze-Fahrzeit je angemeldeter Person, Route im Popup | button-card | `person.bewohner`, `DEIN_EMBED_KEY` | aktiv |
| [`fahrzeiten-templates.yaml`](fahrzeuge/fahrzeiten-templates.yaml) | templates | Fahrzeiten – Waze-Fahrzeit je angemeldeter Person, Routen-Popup | button-card | `DEIN_EMBED_KEY` | aktiv |
| [`tanken-karte.yaml`](fahrzeuge/tanken-karte.yaml) | karte | Tanken – guenstigster Diesel in der Naehe | button-card | – | aktiv |
| [`tanken-templates.yaml`](fahrzeuge/tanken-templates.yaml) | templates | Tanken – Spritpreise aus Tankerkoenig, Bibliothek und Popup | apexcharts-card, button-card, card-mod | `tankstelle_<n>` | aktiv |
| [`autos-animation.html`](fahrzeuge/entwuerfe/autos-animation.html) | entwurf | Auto-View: Animationen – Entwurf und Datenlage | – | `kennzeichen`, `fin_*` | Entwurf zu `autos-karte-v4.yaml`, `autos-templates.yaml` |
| [`autos-karten-v2.html`](fahrzeuge/entwuerfe/autos-karten-v2.html) | entwurf | Auto-Karten v2 – Entwurf | – | `kennzeichen`, `fin_*` | Entwurf zu `autos-karte-v2.yaml` |
| [`autos-karte-v2.yaml`](fahrzeuge/archiv/autos-karte-v2.yaml) | karte | Autos v2 – Volkswagen Connect (volkswagencarnet) | button-card, card-mod | `kennzeichen`, `fin_*` | archiv, ersetzt durch `autos-karte-v3.yaml` |
| [`autos-karte-v3.yaml`](fahrzeuge/archiv/autos-karte-v3.yaml) | karte | Autos v3 – VW Group Connect (vag_connect) | button-card, card-mod | `kennzeichen`, `fin_*` | archiv, ersetzt durch `autos-karte-v4.yaml` |
| [`autos-karte.yaml`](fahrzeuge/archiv/autos-karte.yaml) | karte | Autos v1 | button-card, card-mod | `kennzeichen` | archiv, ersetzt durch `autos-karte-v2.yaml` |

## garten

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`garten-karte.yaml`](garten/garten-karte.yaml) | karte | Garten – Pool, Bewaesserung, Maehroboter | button-card, card-mod | `notify.mobile_app_iphone`, `*_seriennr`, `*_mac` | aktiv |
| [`pflanzen-templates.yaml`](garten/pflanzen-templates.yaml) | templates | Pflanzen – Decluttering-Template owlet_pflanze | apexcharts-card, button-card, card-mod | – | aktiv |
| [`pflanzen-view.yaml`](garten/pflanzen-view.yaml) | view | Pflanzen – komplette Ansicht | button-card, decluttering-card | `ieee_adresse` | aktiv |
| [`pflanzen-flower-karte.yaml`](garten/archiv/pflanzen-flower-karte.yaml) | karte | Pflanzen mit flower-card | card-mod, flower-card | `ieee_adresse` | archiv, ersetzt durch `pflanzen-view.yaml` |
| [`pflanzen-status-karte.yaml`](garten/archiv/pflanzen-status-karte.yaml) | karte | Pflanzen-Status – Ampel-Liste | button-card, card-mod | – | archiv, ersetzt durch `pflanzen-view.yaml` |

## personen

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`gesundheit-view.yaml`](personen/gesundheit-view.yaml) | view | Gesundheit – komplette Ansicht | apexcharts-card, button-card, card-mod, decluttering-card | `sensor.iphone_*`, `benutzer_id_1/benutzer_id_2` | aktiv |
| [`owlet-smart-sock-karte.yaml`](personen/owlet-smart-sock-karte.yaml) | karte | Owlet Smart Sock – Referenz des Owlet-Stils | button-card, card-mod | `*_seriennr` | aktiv |
| [`person-presence-karte.yaml`](personen/person-presence-karte.yaml) | karte | Personen-Praesenz | button-card | `person.bewohner`, `sensor.iphone_*` | aktiv |

## flugradar

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`flugradar-templates.yaml`](flugradar/flugradar-templates.yaml) | templates | Flugradar – button-card-Templates | – | – | aktiv |
| [`flugradar-view.yaml`](flugradar/flugradar-view.yaml) | view | Fluege – komplette Ansicht | apexcharts-card, bubble-card, button-card, card-mod, decluttering-card | `notify.mobile_app_iphone`, `<breite>/<laenge>` | aktiv |

## fussball

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`fussball-espn-konfig.yaml`](fussball/fussball-espn-konfig.yaml) | konfig | Fussball – ESPN-Abruf fuer die Meldungen | – | – | aktiv |
| [`fussball-meldungen-konfig.yaml`](fussball/fussball-meldungen-konfig.yaml) | konfig | Fussball – Meldungen zum Lieblingsverein (Helfer, Skript, Automation) | – | `notify.mobile_app_iphone` | aktiv |
| [`fussball-templates.yaml`](fussball/fussball-templates.yaml) | templates | Fussball – button-card-Templates | – | – | aktiv |
| [`fussball-view.yaml`](fussball/fussball-view.yaml) | view | Fussball – komplette Ansicht | bubble-card, button-card, card-mod, decluttering-card | `notify.mobile_app_iphone` | aktiv |

## sicherheit

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`sicherheit-templates.yaml`](sicherheit/sicherheit-templates.yaml) | templates | Sicherheit – button-card-Templates | – | `person.bewohner`, `*_seriennr`, `kind_1/kind_2` | aktiv |
| [`sicherheit-view.yaml`](sicherheit/sicherheit-view.yaml) | view | Sicherheit – komplette Ansicht | button-card, card-mod, decluttering-card | – | aktiv |
| [`wachmodus-konfig.yaml`](sicherheit/wachmodus-konfig.yaml) | konfig | Sicherheit – Wachmodus und Meldungen (Helfer, Automationen) | – | `person.bewohner`, `notify.mobile_app_iphone`, `*_seriennr`, `telegram_eintrag` | aktiv |

## sonstiges

| Datei | Art | Titel | Karten | Platzhalter | Status |
|---|---|---|---|---|---|
| [`claude-nutzung-karte.yaml`](sonstiges/claude-nutzung-karte.yaml) | karte | Claude – Nutzungslimits des Abos | button-card | `sensor.claude_usage_konto_*` | aktiv |
| [`kameras-templates.yaml`](sonstiges/kameras-templates.yaml) | templates | Kameras – Decluttering-Template owlet_kamera_kachel | button-card, webrtc-camera | – | aktiv |
| [`kameras-view.yaml`](sonstiges/kameras-view.yaml) | view | Kameras – komplette Ansicht | button-card, card-mod, decluttering-card | `kind_1/kind_2`, `benutzer_id_1/benutzer_id_2` | aktiv |
| [`muellabfuhr-karte-v2.yaml`](sonstiges/muellabfuhr-karte-v2.yaml) | karte | Muellabfuhr v2 – Countdown | button-card, card-mod | `VG Wohnort` | aktiv |
| [`wow-arsenal-karte.yaml`](sonstiges/wow-arsenal-karte.yaml) | karte | WoW – Arsenal eines Charakters | button-card | `wow_charakter` | aktiv |
| [`wow-templates.yaml`](sonstiges/wow-templates.yaml) | templates | WoW – Bibliothek, Ausruestungsplatz und Item-Tooltip | button-card | – | aktiv |
| [`claude-nutzung.html`](sonstiges/entwuerfe/claude-nutzung.html) | entwurf | Claude – Nutzungslimits, Entwurf hell und dunkel | – | `sensor.claude_usage_konto_*` | Entwurf zu `claude-nutzung-karte.yaml` |
| [`kameras-karte.yaml`](sonstiges/archiv/kameras-karte.yaml) | karte | Kameras | button-card, card-mod, webrtc-camera | `benutzer_id_1/benutzer_id_2` | archiv, ersetzt durch `kameras-view.yaml` |
| [`muellabfuhr-karte.yaml`](sonstiges/archiv/muellabfuhr-karte.yaml) | karte | Muellabfuhr v1 – trash-card | button-card, card-mod, trash-card | `VG Wohnort` | archiv, ersetzt durch `muellabfuhr-karte-v2.yaml` |
