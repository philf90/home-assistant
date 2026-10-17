# Umbenennung Oktober 2026

Im Oktober 2026 sind alle Karten, Views und Entwürfe aus dem Wurzelverzeichnis
in Bereichsordner unter `dashboard/` umgezogen und nach einem einheitlichen
Schema umbenannt worden. Abgelöste Fassungen liegen seitdem in `archiv/`.
Wer eine Datei unter ihrem alten Namen sucht, findet sie hier.

Am Inhalt der Dateien hat sich durch den Umzug nur geändert, was auf andere
Dateien verweist: Kommentare und die `!include`-Zeilen der Netzwerk-View.
Die Historie einer Datei zeigt
`git log --follow <neuer Pfad>`.

Diese Liste nennt absichtlich Namen, die es nicht mehr gibt; `ci/check_verweise.py`
prüft sie deshalb nicht.

| Alter Name | Neuer Pfad |
|---|---|
| `autos-animation-button-card-templates.yaml` | `dashboard/fahrzeuge/autos-templates.yaml` |
| `autos-animation-vorschlaege.html` | `dashboard/fahrzeuge/entwuerfe/autos-animation.html` |
| `autos-button-card-v2.yaml` | `dashboard/fahrzeuge/archiv/autos-karte-v2.yaml` |
| `autos-button-card-v3.yaml` | `dashboard/fahrzeuge/archiv/autos-karte-v3.yaml` |
| `autos-button-card-v4.yaml` | `dashboard/fahrzeuge/autos-karte-v4.yaml` |
| `autos-button-card.yaml` | `dashboard/fahrzeuge/archiv/autos-karte.yaml` |
| `autos-karten-v2-vorschlaege.html` | `dashboard/fahrzeuge/entwuerfe/autos-karten-v2.html` |
| `decluttering-templates.yaml` | `dashboard/allgemein/navigation-templates.yaml` |
| `energie-autarkie-button-card.yaml` | `dashboard/energie/archiv/energie-autarkie-karte.yaml` |
| `energie-button-card-templates.yaml` | `dashboard/energie/energie-templates.yaml` |
| `energie-diagramme-button-card.yaml` | `dashboard/energie/archiv/energie-diagramme-karte.yaml` |
| `energie-flow-button-card.yaml` | `dashboard/energie/energie-flow-karte.yaml` |
| `energie-flow-leiste-button-card.yaml` | `dashboard/energie/archiv/energie-flow-leiste-karte.yaml` |
| `energie-monatsbilanz-card.yaml` | `dashboard/energie/energie-monatsbilanz-karte.yaml` |
| `energie-pv-button-card.yaml` | `dashboard/energie/archiv/energie-pv-karte.yaml` |
| `energie-solarbank-pv-button-card.yaml` | `dashboard/energie/energie-solarbank-pv-karte.yaml` |
| `energie-verbrauch-uebersicht-button-card.yaml` | `dashboard/energie/archiv/energie-verbrauch-uebersicht-karte.yaml` |
| `energie-verbraucher-button-card.yaml` | `dashboard/energie/energie-verbraucher-karte.yaml` |
| `energie-zaehler-button-card.yaml` | `dashboard/energie/energie-zaehler-karte.yaml` |
| `energiefluss-vorschlaege.html` | `dashboard/energie/entwuerfe/energiefluss.html` |
| `fenster-button-card.yaml` | `dashboard/licht/fenster-karte.yaml` |
| `fenster-lichter-button-card.yaml` | `dashboard/licht/fenster-lichter-karte.yaml` |
| `fenster-lichter-uebersicht-button-card.yaml` | `dashboard/licht/fenster-lichter-uebersicht-karte.yaml` |
| `flugradar-button-card-templates.yaml` | `dashboard/flugradar/flugradar-templates.yaml` |
| `flugradar-view.yaml` | `dashboard/flugradar/flugradar-view.yaml` |
| `fussball-button-card-templates.yaml` | `dashboard/fussball/fussball-templates.yaml` |
| `fussball-view.yaml` | `dashboard/fussball/fussball-view.yaml` |
| `garten-button-card.yaml` | `dashboard/garten/garten-karte.yaml` |
| `gas-wasser-button-card.yaml` | `dashboard/energie/archiv/gas-wasser-karte.yaml` |
| `geschirrspueler-button-card.yaml` | `dashboard/hausgeraete/geschirrspueler-karte.yaml` |
| `gesundheit-view.yaml` | `dashboard/personen/gesundheit-view.yaml` |
| `grafana/proxmox-mockups.html` | `grafana/entwuerfe/proxmox-mockups.html` |
| `grafana/proxmox-mockups.md` | `grafana/entwuerfe/proxmox-mockups.md` |
| `hausgeraete-animation-button-card-templates.yaml` | `dashboard/hausgeraete/hausgeraete-templates.yaml` |
| `hausgeraete-vorschlaege.html` | `dashboard/hausgeraete/entwuerfe/hausgeraete.html` |
| `haustuer-ereignis-button-card.yaml` | `dashboard/licht/haustuer-ereignis-karte.yaml` |
| `haustuer-lock-button-card.yaml` | `dashboard/licht/haustuer-lock-karte.yaml` |
| `heizung-animation-button-card-templates.yaml` | `dashboard/klima/heizung-templates.yaml` |
| `home-kacheln-vorschlaege.html` | `dashboard/allgemein/entwuerfe/home-kacheln.html` |
| `homematic-button-card.yaml` | `dashboard/netzwerk/homematic-karte.yaml` |
| `kameras-button-card.yaml` | `dashboard/sonstiges/kameras-karte.yaml` |
| `karten-basemap-carto.md` | `doku/karten-basemap-carto.md` |
| `lichter-glow-card.yaml` | `dashboard/licht/lichter-glow-karte.yaml` |
| `lichter-mushroom-card.yaml` | `dashboard/licht/lichter-mushroom-karte.yaml` |
| `lichter-raum-card.yaml` | `dashboard/licht/lichter-raum-karte.yaml` |
| `lichter-slider-button-card.yaml` | `dashboard/licht/lichter-slider-karte.yaml` |
| `meteoalarm-button-card.yaml` | `dashboard/klima/meteoalarm-karte.yaml` |
| `muellabfuhr-trash-card-v2.yaml` | `dashboard/sonstiges/muellabfuhr-karte-v2.yaml` |
| `muellabfuhr-trash-card.yaml` | `dashboard/sonstiges/archiv/muellabfuhr-karte.yaml` |
| `navbar-card.yaml` | `dashboard/allgemein/navbar-karte.yaml` |
| `netzwerk-view.yaml` | `dashboard/netzwerk/netzwerk-view.yaml` |
| `owlet-smart-sock-button-card.yaml` | `dashboard/personen/owlet-smart-sock-karte.yaml` |
| `person-presence-button-card.yaml` | `dashboard/personen/person-presence-karte.yaml` |
| `pflanzen-decluttering-templates.yaml` | `dashboard/garten/pflanzen-templates.yaml` |
| `pflanzen-flower-card.yaml` | `dashboard/garten/archiv/pflanzen-flower-karte.yaml` |
| `pflanzen-status-button-card.yaml` | `dashboard/garten/archiv/pflanzen-status-karte.yaml` |
| `pflanzen-view.yaml` | `dashboard/garten/pflanzen-view.yaml` |
| `pollenflug-button-card.yaml` | `dashboard/klima/pollenflug-karte.yaml` |
| `proxmox-haos-secure-boot-warnung.md` | `doku/proxmox-haos-secure-boot-warnung.md` |
| `proxmox-haos-speicher-erweitern.md` | `doku/proxmox-haos-speicher-erweitern.md` |
| `staubsauger-button-card.yaml` | `dashboard/hausgeraete/staubsauger-karte.yaml` |
| `system-button-card.yaml` | `dashboard/netzwerk/system-karte.yaml` |
| `temperaturen-button-card-v2.yaml` | `dashboard/klima/temperaturen-karte-v2.yaml` |
| `temperaturen-button-card.yaml` | `dashboard/klima/archiv/temperaturen-karte.yaml` |
| `template-autos-passat.yaml` | `dashboard/fahrzeuge/autos-passat-konfig.yaml` |
| `thermostate-button-card-v2.yaml` | `dashboard/klima/archiv/thermostate-karte-v2.yaml` |
| `thermostate-button-card-v3.yaml` | `dashboard/klima/thermostate-karte-v3.yaml` |
| `thermostate-button-card.yaml` | `dashboard/klima/archiv/thermostate-karte.yaml` |
| `top-navigation-button-card.yaml` | `dashboard/allgemein/top-navigation-karte.yaml` |
| `trockner-button-card.yaml` | `dashboard/hausgeraete/trockner-karte.yaml` |
| `unifi-kabel-clients.yaml` | `dashboard/netzwerk/unifi-kabel-clients-konfig.yaml` |
| `unifi-leitungen-button-card.yaml` | `dashboard/netzwerk/unifi-leitungen-karte.yaml` |
| `unifi-netzplan-card.js` | `dashboard/netzwerk/unifi-netzplan-card.js` |
| `unifi-netzplan-card.yaml` | `dashboard/netzwerk/unifi-netzplan-karte.yaml` |
| `unifi-netzwerk-status-button-card.yaml` | `dashboard/netzwerk/unifi-netzwerk-status-karte.yaml` |
| `unifi-udm-system-button-card-v2.yaml` | `dashboard/netzwerk/unifi-udm-system-karte-v2.yaml` |
| `unifi-udm-system-button-card.yaml` | `dashboard/netzwerk/archiv/unifi-udm-system-karte.yaml` |
| `unifi-unas-pro-button-card.yaml` | `dashboard/netzwerk/unifi-unas-pro-karte.yaml` |
| `unifi-verlauf-expander-card.yaml` | `dashboard/netzwerk/unifi-verlauf-karte.yaml` |
| `waschmaschine-button-card.yaml` | `dashboard/hausgeraete/waschmaschine-karte.yaml` |
| `welcome-banner-button-card.yaml` | `dashboard/allgemein/welcome-banner-karte.yaml` |
| `wetter-animation-button-card-templates.yaml` | `dashboard/klima/wetter-templates.yaml` |
| `wetter-animiert-vorschlaege.html` | `dashboard/klima/entwuerfe/wetter-animiert.html` |
| `wetter-button-card.yaml` | `dashboard/klima/wetter-karte.yaml` |
| `wlan-expander-card.yaml` | `dashboard/netzwerk/wlan-karte.yaml` |
