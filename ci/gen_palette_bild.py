#!/usr/bin/env python3
"""Erzeugt das Paletten-Schaubild fuer das README aus design/palette.yaml.

Zwei PNG-Dateien, eine je GitHub-Theme: design/palette-rollen-dunkel.png und
design/palette-rollen-hell.png. Jede zeigt alle Rollen aus ROLLEN mit ihrem
Wert im dunklen und im hellen Modus (Abschnitt "theme" der Palette) und ihrer
Verwendung; nur der Bildgrund folgt dem Theme.

Gerendert wird mit Chromium ueber Playwright (Node), danach auf 256 Farben
reduziert. Die Farbtabelle enthaelt jeden Palettenwert im Bild exakt, jeder
Bildpunkt bekommt den naechstgelegenen Eintrag: Farbmuster und Schrift behalten
ihren Hex-Wert, nur Kantenglaettung wird angenaehert.

Nur lokal, nicht in der CI. Braucht: node mit dem Paket playwright (Chromium),
die Schrift Inter, Python mit pyyaml, numpy und Pillow.

Aufruf:
  python ci/gen_palette_bild.py     schreibt beide Bilder neu
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

import numpy as np
import yaml
from dateien import REPO_ROOT
from PIL import Image

PALETTE_FILE = REPO_ROOT / "design" / "palette.yaml"
ZIEL = REPO_ROOT / "design" / "palette-rollen-{modus}.png"
MODI = ("dunkel", "hell")

# Rollen im Bild: Gruppe, Spalte (0 links, 1 rechts) und je Rolle
# (Theme-Variable ohne "nachtblau-", Anzeigename, Verwendung). Die Verwendung
# ist die Kurzfassung von "zweck" in der Palette.
ROLLEN = [
    ("Status", 0, [
        ("gruen", "Grün", "OK, geschlossen, Akku gut"),
        ("amber", "Amber", "Hinweis, Warnung, offen"),
        ("koralle", "Koralle", "erhöht, immer mit Text"),
        ("rot", "Rot", "kritisch, Alarm, Netzbezug"),
    ]),
    ("Text", 0, [
        ("text", "Primärtext", "Primärtext, Messwerte"),
        ("titel", "Titel", "Titel, Kopfzeilen"),
        ("label", "Label", "Labels, Hinweise"),
        ("text-sekundaer", "Sekundär", "jede kleine Schrift"),
        ("muted", "Muted", "nur Icons, nie Text"),
    ]),
    ("Flächen", 0, [
        ("seite", "Seitengrund", "Grund der Seite"),
        ("huelle-oben", "Kartenhülle", "Hülle, Verlauf oben"),
        ("flaeche-erhoeht", "Erhöht", "Popups, Hover"),
        ("flaeche-vertieft", "Vertieft", "Diagramme, Logs"),
        ("aus", "Zustand aus", "Bogen aus, Leerlauf"),
    ]),
    ("Akzente", 1, [
        ("blau", "Blau", "Home, Standard-Akzent, Info"),
        ("tuerkis", "Türkis", "Verbraucher, Hausgeräte"),
        ("tuerkis-hell", "Türkis hell", "Navigation Verbrauch"),
        ("petrol", "Petrol", "Heizung"),
        ("violett", "Violett", "Geräte, Netzwerk, Kosten"),
        ("limette", "Limette", "Garten, Bewässerung"),
        ("mint", "Mint", "Einspeisung, Autarkie"),
        ("indigo", "Indigo", "Nacht, Schlaf, Abwesenheit"),
        ("rose", "Rose", "Personen, Gesundheit"),
        ("wolkengrau", "Wolkengrau", "Wetter"),
        ("sonnengelb", "Sonnengelb", "PV und Solar"),
        ("licht-an", "Licht an", "Licht an: Text, Rand"),
    ]),
]

# Bildaufbau (Hintergrund, Huelle, Schrift) aus diesen Theme-Variablen
BASIS = ("seite", "huelle-oben", "huelle-unten", "huelle-rand", "schatten", "titel", "label",
         "text-sekundaer")

# Rand der Muster: Weiss bzw. Kartenhuelle-Schwarz mit Deckkraft (DESIGN.md)
MUSTER_RAND = {"dunkel": "rgba(255, 255, 255, 0.14)", "hell": "rgba(23, 29, 41, 0.16)"}
CHIP_RAND = {"dunkel": "rgba(255, 255, 255, 0.08)", "hell": "rgba(23, 29, 41, 0.10)"}

RENDERER = r"""
const { chromium } = require('playwright');
const [html, png] = process.argv.slice(1);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 880, height: 900 }, deviceScaleFactor: 2 });
  await p.goto('file://' + html);
  await p.evaluate(() => document.fonts.ready);
  await (await p.$('.buehne')).screenshot({ path: png });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def theme_werte() -> dict[str, dict[str, str]]:
    palette = yaml.safe_load(PALETTE_FILE.read_text(encoding="utf-8"))
    return {v["name"].removeprefix("nachtblau-"): {m: v[m] for m in MODI}
            for v in palette["theme"]["variablen"]}


def rgba(hex_: str, deckkraft: float) -> str:
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {deckkraft})"


def ring(farbe: str, groesse: int) -> str:
    """Icon-Ring statt Schriftprobe, fuer Muted (nie Text)."""
    return (f'<span style="width:{groesse}px;height:{groesse}px;border-radius:50%;'
            f'border:2.5px solid {farbe}"></span>')


def chip(gruppe: str, key: str, farbe: str, modus: str, w: dict) -> str:
    """Muster einer Rolle auf der Kartenhuelle des Modus."""
    if gruppe == "Text":
        innen = (ring(farbe, 15) if key == "muted" else
                 f'<span style="font-size:15px;font-weight:700;color:{farbe}">Aa</span>')
    elif gruppe == "Flächen":
        innen = (f'<span style="width:22px;height:22px;border-radius:7px;background:{farbe};'
                 f'border:1px solid {MUSTER_RAND[modus]}"></span>')
    else:
        innen = (f'<span style="width:18px;height:18px;border-radius:50%;background:{farbe};'
                 f'box-shadow:0 0 0 4px {rgba(farbe, 0.18)}"></span>')
    return (f'<div class="chip" style="background:{w["huelle-oben"][modus]};'
            f'border:1px solid {CHIP_RAND[modus]}">{innen}</div>')


def gruppe_html(name: str, rollen: list, w: dict) -> str:
    zeilen = []
    for key, anzeige, zweck in rollen:
        zeilen.append(
            '<div class="zeile">'
            + "".join(chip(name, key, w[key][m], m, w) for m in MODI)
            + f'<div class="rolle"><div class="name">{escape(anzeige)}</div>'
            f'<div class="zweck">{escape(zweck)}</div></div>'
            f'<div class="hex">{w[key]["dunkel"]}<br>{w[key]["hell"]}</div></div>')
    return ('<div class="gkopf"><span class="lk">dunkel</span><span class="lk">hell</span>'
            f'<h2>{escape(name)}</h2></div><div class="liste">{"".join(zeilen)}</div>')


def seite(modus: str, w: dict) -> str:
    t = {k: w[k][modus] for k in BASIS}
    spalten = ["", ""]
    for name, spalte, rollen in ROLLEN:
        spalten[spalte] += gruppe_html(name, rollen, w)
    # Legende: je Modus ein Badge im Look seiner Muster (Huelle, Label, Rand)
    badges = "".join(
        f'<div class="modus" style="background:{w["huelle-oben"][m]};color:{w["label"][m]};'
        f'border:1px solid {CHIP_RAND[m]}">{name}</div>'
        for m, name in (("dunkel", "Dunkler Modus"), ("hell", "Heller Modus")))
    return f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{background:{t['seite']};font-family:Inter,sans-serif;-webkit-font-smoothing:antialiased}}
.buehne{{width:880px;padding:20px;background:{t['seite']}}}
.huelle{{border-radius:24px;padding:26px 26px 28px;border:1px solid {t['huelle-rand']};
  background:linear-gradient(180deg,{t['huelle-oben']} 0%,{t['huelle-unten']} 55%);
  box-shadow:0 18px 44px -22px {t['schatten']}}}
.kopf{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px}}
.eyebrow{{font-size:12px;font-weight:600;letter-spacing:1.6px;color:{t['text-sekundaer']};
  text-transform:uppercase}}
h1{{font-family:'Inter Display',Inter,sans-serif;font-size:26px;font-weight:700;
  letter-spacing:-0.3px;color:{t['titel']};margin-top:4px}}
.badges{{display:flex;gap:8px}}
.modus{{font-size:13px;font-weight:600;padding:5px 11px;border-radius:999px}}
.spalten{{display:grid;grid-template-columns:1fr 1fr;gap:0 32px}}
.gkopf{{display:grid;grid-template-columns:46px 46px 1fr;gap:10px;align-items:baseline;
  margin:20px 0 10px}}
.lk{{font-size:11px;color:{t['text-sekundaer']};text-align:center}}
h2{{font-size:11.5px;font-weight:600;letter-spacing:1.4px;text-transform:uppercase;
  color:{t['text-sekundaer']};padding-left:4px}}
.liste{{display:flex;flex-direction:column;gap:7px}}
.zeile{{display:grid;grid-template-columns:46px 46px 1fr auto;gap:8px 10px;align-items:center}}
.chip{{width:46px;height:34px;border-radius:10px;display:flex;align-items:center;
  justify-content:center}}
.rolle{{min-width:0;padding-left:4px}}
.name{{font-size:14px;font-weight:600;color:{t['titel']}}}
.zweck{{font-size:12.5px;color:{t['text-sekundaer']};line-height:1.35}}
.hex{{font-size:12px;color:{t['text-sekundaer']};font-feature-settings:'tnum';
  letter-spacing:0.2px;text-align:right;line-height:1.45}}
.fuss{{margin-top:20px;font-size:12px;color:{t['text-sekundaer']}}}
</style><div class="buehne"><div class="huelle">
<div class="kopf"><div><div class="eyebrow">Nachtblau-Palette</div>
<h1>Jede Rolle in beiden Modi</h1></div><div class="badges">{badges}</div></div>
<div class="spalten"><div>{spalten[0]}</div><div>{spalten[1]}</div></div>
<div class="fuss">Werte aus design/palette.yaml · Sonderfarben und Grafana-Töne dort im
Abschnitt farben</div></div></div>"""


def reduzieren(png: Path, pflicht: set[str], grund: set[str]) -> list[str]:
    """Auf 256 Farben reduzieren; jeder Pflicht- und Grundwert im Bild bleibt exakt.

    Gibt die Pflichtwerte zurueck, die im gerenderten Bild fehlen.
    """
    bild = np.asarray(Image.open(png).convert("RGB"))
    farben, index = np.unique(bild.reshape(-1, 3), axis=0, return_inverse=True)
    vorhanden = {"#%02x%02x%02x" % tuple(f) for f in farben}
    fest = [[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in sorted((pflicht | grund) & vorhanden)]
    frei = 256 - len(fest)
    rest = Image.fromarray(bild).quantize(frei, method=Image.Quantize.MEDIANCUT,
                                          dither=Image.Dither.NONE).getpalette()[:3 * frei]
    tabelle = np.vstack([np.array(fest, dtype=int).reshape(-1, 3),
                         np.array(rest, dtype=int).reshape(-1, 3)])
    abstand = ((farben[:, None, :].astype(int) - tabelle[None, :, :]) ** 2).sum(-1)
    neu = abstand.argmin(1)[index.ravel()].reshape(bild.shape[:2]).astype(np.uint8)
    ergebnis = Image.fromarray(neu, "P")
    ergebnis.putpalette(tabelle.astype(np.uint8).ravel().tolist())
    ergebnis.save(png, optimize=True)
    return sorted(pflicht - vorhanden)


def main() -> int:
    w = theme_werte()
    pflicht = {w[key][m] for _, _, rollen in ROLLEN for key, _, _ in rollen for m in MODI}
    grund = {w[key][m] for key in BASIS for m in MODI if w[key][m].startswith("#")}
    with tempfile.TemporaryDirectory() as tmp:
        for modus in MODI:
            html = Path(tmp) / f"{modus}.html"
            html.write_text(seite(modus, w), encoding="utf-8")
            ziel = Path(str(ZIEL).format(modus=modus))
            subprocess.run(["node", "-e", RENDERER, str(html), str(ziel)], check=True)
            fehlt = reduzieren(ziel, pflicht, grund)
            if fehlt:
                print(f"{ziel.name}: Werte fehlen im Bild: {', '.join(fehlt)}", file=sys.stderr)
                return 1
            breite, hoehe = Image.open(ziel).size
            groesse = ziel.stat().st_size // 1024
            print(f"{ziel.relative_to(REPO_ROOT)}: {breite} x {hoehe} px, {groesse} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
