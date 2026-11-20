#!/usr/bin/env python3
"""Routen und Sichtbarkeit gegen design/routen.yaml pruefen.

Jedes Sprungziel der Navigation und jeder View hat in design/routen.yaml genau
eine Klasse (admin, person, alle). Diese Pruefung findet die Sprungziele und
Views in den Lovelace-Dateien und vergleicht ihre Bedingungen mit der Klasse.
Regeln und Begruendung: CONTRIBUTING.md, Abschnitt "Routen und Sichtbarkeit".

Erkannt werden als Sprungziel:
  - navigate-Aktionen (tap_action, hold_action, double_tap_action) mit
    navigation_path, auch als '[[[ return variables.pfad; ]]]' mit
    variables.pfad an derselben Karte
  - url-Aktionen, deren url_path mit "/" beginnt
  - url der Routen einer custom:navbar-card
  - Dienstaufrufe (perform-action) aus dem Abschnitt dienste
und als View eine Datei bzw. ein Eintrag unter views mit path.

Als Bedingung zaehlt, an der Karte selbst oder an einer umschliessenden:
  - hidden: '[[[ return !user.is_admin; ]]]'          -> Rolle admin
  - type: conditional bzw. visibility mit condition: user -> Konten
Andere Bedingungen (Zustand, Bildschirm, ...) bleiben unberuecksichtigt.

Aufruf:
  python ci/check_routen.py                  alle Lovelace-Dateien ausser archiv/
  python ci/check_routen.py <datei> ...      nur diese Dateien
  python ci/check_routen.py --json <abzug> --dashboard <url_path>
                            [--konto benutzer_id_1=<id> ...]
      Abzug eines Dashboards aus der Instanz (JSON mit "config" oder die
      Konfiguration selbst). Ohne --konto wird bei Konten nur geprueft, dass
      eine Bedingung da ist; mit --konto auch, dass es die richtigen Konten
      sind. Echte IDs nie committen; die Ausgabe nennt keine IDs.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from check_yaml import HALoader, Placeholder
from dateien import REPO_ROOT, dateien

REGISTER = REPO_ROOT / "design" / "routen.yaml"
KLASSEN = ("admin", "person", "alle")
AKTIONEN = ("tap_action", "hold_action", "double_tap_action")
NUR_ADMIN = re.compile(r"\[\[\[\s*return\s*!\s*user\.is_admin\s*;?\s*\]\]\]")
VARIABLEN_PFAD = re.compile(r"\[\[\[\s*return\s+variables\.pfad\s*;?\s*\]\]\]")
KONTO = re.compile(r"benutzer_id_[12]")


class Register:
    def __init__(self, daten: dict) -> None:
        self.fehler: list[str] = []
        self.admin_konten = frozenset(daten.get("admin_konten") or [])
        self.routen: dict[str, dict] = daten.get("routen") or {}
        self.dienste: dict[str, dict] = daten.get("dienste") or {}
        if not self.admin_konten:
            self.fehler.append("admin_konten fehlt oder ist leer")
        for konto in self.admin_konten:
            if not KONTO.fullmatch(str(konto)):
                self.fehler.append(f"admin_konten: {konto!r} ist kein Platzhalter benutzer_id_1/2")
        for name, gruppe in (("routen", self.routen), ("dienste", self.dienste)):
            for schluessel, eintrag in gruppe.items():
                self._eintrag_pruefen(name, schluessel, eintrag)
        self.genutzt: set[str] = set()

    def _eintrag_pruefen(self, gruppe: str, schluessel: str, eintrag: object) -> None:
        ort = f"{gruppe}.{schluessel}"
        if not isinstance(eintrag, dict):
            self.fehler.append(f"{ort}: Eintrag muss eine Zuordnung sein")
            return
        klasse = eintrag.get("klasse")
        if klasse not in KLASSEN:
            self.fehler.append(f"{ort}: klasse {klasse!r}, erlaubt {', '.join(KLASSEN)}")
        if gruppe == "routen":
            if not str(schluessel).startswith("/"):
                self.fehler.append(f"{ort}: Route beginnt nicht mit /")
            if not eintrag.get("grund"):
                self.fehler.append(f"{ort}: grund fehlt")
        konten = eintrag.get("konten")
        if klasse == "person":
            if not konten or not all(KONTO.fullmatch(str(k)) for k in konten):
                self.fehler.append(f"{ort}: person braucht konten aus benutzer_id_1/benutzer_id_2")
        elif konten is not None:
            self.fehler.append(f"{ort}: konten nur bei klasse person")

    def route(self, pfad: str) -> tuple[str, dict] | None:
        pfad = normalisieren(pfad)
        if pfad in self.routen:
            self.genutzt.add(pfad)
            return pfad, self.routen[pfad]
        for schluessel, eintrag in self.routen.items():
            if schluessel.endswith("/*"):
                basis = schluessel[:-2]
                if pfad == basis or pfad.startswith(basis + "/"):
                    self.genutzt.add(schluessel)
                    return schluessel, eintrag
        return None

    def view(self, view_pfad: str, dashboard: str | None) -> list[tuple[str, dict]]:
        if dashboard:
            treffer = self.route(f"/{dashboard}/{view_pfad}")
            return [treffer] if treffer else []
        treffer = [
            (s, e)
            for s, e in self.routen.items()
            if not s.endswith("/*") and s.rstrip("/").split("/")[-1] == view_pfad
        ]
        for s, _ in treffer:
            self.genutzt.add(s)
        return treffer


def normalisieren(pfad: str) -> str:
    pfad = pfad.split("#", 1)[0].split("?", 1)[0]
    return pfad.rstrip("/") or "/"


def bedingungen_der_karte(knoten: dict) -> list[tuple[str, frozenset | None]]:
    """Bedingungen nach Rolle oder Konto, die an diesem Knoten haengen."""
    gefunden: list[tuple[str, frozenset | None]] = []
    hidden = knoten.get("hidden")
    if isinstance(hidden, str) and NUR_ADMIN.fullmatch(hidden.strip()):
        gefunden.append(("admin", None))
    elif isinstance(hidden, str) and "user." in hidden:
        gefunden.append(("unbekannt", None))
    listen = []
    if knoten.get("type") == "conditional":
        listen.append(knoten.get("conditions"))
    listen.append(knoten.get("visibility"))
    for liste in listen:
        for konten in benutzer_bedingungen(liste):
            gefunden.append(("person", konten))
    return gefunden


def benutzer_bedingungen(liste) -> list[frozenset]:
    ergebnis = []
    if not isinstance(liste, list):
        return ergebnis
    for bedingung in liste:
        if not isinstance(bedingung, dict):
            continue
        if bedingung.get("condition") == "user":
            ergebnis.append(frozenset(bedingung.get("users") or []))
        elif bedingung.get("condition") == "and":
            ergebnis.extend(benutzer_bedingungen(bedingung.get("conditions")))
    return ergebnis


class Pruefung:
    def __init__(self, register: Register, konten: dict[str, str] | None, json_modus: bool) -> None:
        self.register = register
        self.konten = konten or {}
        self.json_modus = json_modus
        self.fehler: list[str] = []
        self.ziele = 0

    # -- Konten ---------------------------------------------------------------
    def soll_konten(self, platzhalter) -> frozenset | None:
        """Erwartete Konten so, wie sie in der geprueften Datei stehen."""
        if not self.json_modus:
            return frozenset(platzhalter)
        if not self.konten:
            return None  # nur pruefen, dass eine Bedingung da ist
        return frozenset(self.konten.get(p, f"<{p} ohne --konto>") for p in platzhalter)

    def konten_text(self, konten) -> str:
        rueck = {v: k for k, v in self.konten.items()}
        namen = sorted(
            rueck.get(k, k if KONTO.fullmatch(str(k)) else "<anderes Konto>") for k in konten
        )
        return ", ".join(namen) or "keine"

    # -- Sprungziele ----------------------------------------------------------
    def ziel(self, ort: str, art: str, wert: str, bedingungen: list) -> None:
        self.ziele += 1
        treffer = self.register.route(wert)
        if not treffer:
            self.fehler.append(
                f"{ort}: {art} {wert} hat keine Klasse, in design/routen.yaml eintragen"
            )
            return
        schluessel, eintrag = treffer
        self.klasse_pruefen(ort, f"{art} {wert}", eintrag, bedingungen, schluessel)

    def klasse_pruefen(
        self, ort: str, was: str, eintrag: dict, bedingungen: list, schluessel: str
    ) -> None:
        klasse = eintrag.get("klasse")
        rolle = [b for b in bedingungen if b[0] == "admin"]
        personen = [b for b in bedingungen if b[0] == "person"]
        unbekannt = [b for b in bedingungen if b[0] == "unbekannt"]
        if unbekannt:
            self.fehler.append(
                f"{ort}: {was}: hidden fragt user ab, aber nicht in der Form "
                "'[[[ return !user.is_admin; ]]]'"
            )
        if klasse == "alle":
            if rolle or personen:
                self.fehler.append(
                    f"{ort}: {was} ist Klasse alle ({schluessel}), hat aber eine Bedingung nach "
                    "Rolle oder Konto; Bedingung entfernen oder Klasse aendern"
                )
        elif klasse == "admin":
            if not rolle:
                self.fehler.append(
                    f"{ort}: {was} ist Klasse admin ({schluessel}), es fehlt "
                    "hidden: '[[[ return !user.is_admin; ]]]'"
                )
            if personen:
                self.fehler.append(
                    f"{ort}: {was} ist Klasse admin, Bedingung nach Konto statt Rolle"
                )
        elif klasse == "person":
            if rolle:
                self.fehler.append(
                    f"{ort}: {was} ist Klasse person, Bedingung nach Rolle statt Konto"
                )
            if not personen:
                self.fehler.append(
                    f"{ort}: {was} ist Klasse person ({schluessel}), es fehlt eine "
                    "Bedingung condition: user"
                )
                return
            soll = self.soll_konten(eintrag.get("konten") or [])
            for _, ist in personen:
                if not ist:
                    self.fehler.append(f"{ort}: {was}: condition: user ohne Konten")
                elif soll is not None and ist != soll:
                    self.fehler.append(
                        f"{ort}: {was}: Konten {self.konten_text(ist)}, laut design/routen.yaml "
                        f"{self.konten_text(eintrag.get('konten') or [])}"
                    )

    # -- Views ----------------------------------------------------------------
    def view(self, ort: str, view: dict, dashboard: str | None) -> None:
        pfad = view.get("path")
        if not isinstance(pfad, str):
            return
        treffer = self.register.view(pfad, dashboard)
        if not treffer:
            self.fehler.append(
                f"{ort}: View {pfad} hat keine Klasse, in design/routen.yaml eintragen"
            )
            return
        if len(treffer) > 1:
            namen = ", ".join(s for s, _ in treffer)
            self.fehler.append(f"{ort}: View {pfad} passt auf mehrere Routen ({namen})")
            return
        schluessel, eintrag = treffer[0]
        klasse = eintrag.get("klasse")
        sichtbar = view.get("visible", True)
        konten = None
        if isinstance(sichtbar, list):
            konten = frozenset(
                x.get("user") for x in sichtbar if isinstance(x, dict) and x.get("user")
            )
        if klasse == "alle":
            if sichtbar is not True:
                self.fehler.append(
                    f"{ort}: View {pfad} ist Klasse alle ({schluessel}), visible entfernen"
                )
            return
        if klasse == "admin":
            platzhalter = self.register.admin_konten
        else:
            platzhalter = eintrag.get("konten") or []
        soll = self.soll_konten(platzhalter)
        if not konten:
            self.fehler.append(
                f"{ort}: View {pfad} ist Klasse {klasse} ({schluessel}), es fehlt visible mit "
                f"{', '.join(sorted(platzhalter))}"
            )
        elif soll is not None and konten != soll:
            self.fehler.append(
                f"{ort}: View {pfad}: visible mit {self.konten_text(konten)}, laut "
                f"design/routen.yaml {', '.join(sorted(platzhalter))}"
            )

    # -- Durchlauf ------------------------------------------------------------
    def durchlaufen(self, knoten, ort: str, pfad: str, bedingungen: list) -> None:
        if isinstance(knoten, Placeholder):
            knoten = knoten.value
        if isinstance(knoten, list):
            for i, kind in enumerate(knoten):
                self.durchlaufen(kind, ort, f"{pfad}[{i}]", bedingungen)
            return
        if not isinstance(knoten, dict):
            return
        bedingungen = bedingungen + bedingungen_der_karte(knoten)
        stelle = f"{ort}:{pfad or '/'}"
        for schluessel in AKTIONEN:
            aktion = knoten.get(schluessel)
            if isinstance(aktion, dict):
                self.aktion(f"{stelle}.{schluessel}", aktion, knoten, bedingungen)
        if knoten.get("type") == "custom:navbar-card":
            for i, route in enumerate(knoten.get("routes") or []):
                if isinstance(route, dict) and isinstance(route.get("url"), str):
                    self.ziel(
                        f"{stelle}.routes[{i}]", "url", route["url"],
                        bedingungen + bedingungen_der_karte(route),
                    )
        # Auch in Aktionen hinein: Popups (browser_mod) tragen dort ganze Karten.
        for schluessel, kind in knoten.items():
            unterpfad = f"{pfad}.{schluessel}" if pfad else str(schluessel)
            self.durchlaufen(kind, ort, unterpfad, bedingungen)

    def aktion(self, ort: str, aktion: dict, karte: dict, bedingungen: list) -> None:
        art = aktion.get("action")
        if art == "navigate":
            ziel = aktion.get("navigation_path")
            if not isinstance(ziel, str):
                return
            if VARIABLEN_PFAD.fullmatch(ziel.strip()):
                ziel = (karte.get("variables") or {}).get("pfad")
                if not isinstance(ziel, str):
                    self.fehler.append(
                        f"{ort}: navigation_path ueber variables.pfad, "
                        "aber die Karte hat kein variables.pfad"
                    )
                    return
            elif "[[" in ziel or "{{" in ziel:
                self.fehler.append(
                    f"{ort}: navigation_path {ziel!r} ist nicht auswertbar; festen Pfad oder "
                    "'[[[ return variables.pfad; ]]]' mit variables.pfad verwenden"
                )
                return
            if ziel.startswith("#"):
                return
            self.ziel(ort, "navigation_path", ziel, bedingungen)
        elif art == "url":
            ziel = aktion.get("url_path")
            if isinstance(ziel, str) and ziel.startswith("/"):
                self.ziel(ort, "url_path", ziel, bedingungen)
        elif art in ("perform-action", "call-service"):
            dienst = aktion.get("perform_action") or aktion.get("service")
            if isinstance(dienst, str) and dienst in self.register.dienste:
                self.ziele += 1
                eintrag = self.register.dienste[dienst]
                self.klasse_pruefen(ort, f"Dienst {dienst}", eintrag, bedingungen, dienst)


def laden_yaml(pfad: Path):
    loader = HALoader(pfad.read_text(encoding="utf-8"))
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()


def ist_view(pfad: Path, daten) -> bool:
    return (
        isinstance(daten, dict)
        and isinstance(daten.get("path"), str)
        and re.search(r"-view(-v\d+)?\.yaml$", pfad.name) is not None
    )


def argumente(argv: list[str]) -> tuple[list[str], str | None, str | None, dict[str, str]]:
    dateien_arg, abzug, dashboard, konten = [], None, None, {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--json", "--dashboard", "--konto"):
            if i + 1 >= len(argv):
                raise SystemExit(f"{a} braucht einen Wert")
            wert = argv[i + 1]
            if a == "--json":
                abzug = wert
            elif a == "--dashboard":
                dashboard = wert
            else:
                platzhalter, _, konto = wert.partition("=")
                if not KONTO.fullmatch(platzhalter) or not konto:
                    raise SystemExit("--konto erwartet benutzer_id_1=<id> oder benutzer_id_2=<id>")
                konten[platzhalter] = konto
            i += 2
        else:
            dateien_arg.append(a)
            i += 1
    return dateien_arg, abzug, dashboard, konten


def main(argv: list[str]) -> int:
    dateien_arg, abzug, dashboard, konten = argumente(argv)
    register = Register(yaml.safe_load(REGISTER.read_text(encoding="utf-8")) or {})
    for fehler in register.fehler:
        print(f"FEHLER  design/routen.yaml: {fehler}")
    if register.fehler:
        return 1

    if abzug:
        if not dashboard:
            raise SystemExit("--json braucht --dashboard <url_path>")
        daten = json.loads(Path(abzug).read_text(encoding="utf-8"))
        config = daten.get("config", daten) if isinstance(daten, dict) else daten
        pruefung = Pruefung(register, konten, json_modus=True)
        pruefung.durchlaufen(config, dashboard, "", [])
        for i, view in enumerate(config.get("views") or []):
            if isinstance(view, dict):
                pruefung.view(f"{dashboard}:views[{i}]", view, dashboard)
        anzahl = f"Dashboard {dashboard}"
    else:
        pfade = [Path(a) for a in dateien_arg] or [
            p for p in dateien("lovelace") if "archiv" not in p.parts
        ]
        pruefung = Pruefung(register, None, json_modus=False)
        for pfad in pfade:
            try:
                ort = pfad.resolve().relative_to(REPO_ROOT).as_posix()
            except ValueError:
                ort = str(pfad)
            daten = laden_yaml(pfad)
            pruefung.durchlaufen(daten, ort, "", [])
            if ist_view(pfad, daten):
                pruefung.view(ort, daten, None)
        anzahl = f"{len(pfade)} Datei(en)"
        if not dateien_arg:
            ungenutzt = sorted(set(register.routen) - register.genutzt)
            if ungenutzt:
                print(
                    "Hinweis: nur in der Instanz genutzt (kein Sprungziel und kein View im Repo): "
                    + ", ".join(ungenutzt)
                )

    for fehler in dict.fromkeys(pruefung.fehler):
        print(f"FEHLER  {fehler}")
    probleme = len(set(pruefung.fehler))
    print(f"\n{anzahl} geprueft, {pruefung.ziele} Ziel(e), {probleme} Problem(e) gefunden.")
    return 1 if pruefung.fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
