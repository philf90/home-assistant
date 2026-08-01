#!/usr/bin/env python3
"""Backfill der Home-Assistant-Langzeitstatistiken nach InfluxDB 2.

Die `influxdb`-Integration von Home Assistant schreibt ab ihrer Aktivierung, kennt
aber keine Historie. Dieses Skript liest die bereits vorhandenen Langzeitstatistiken
(`recorder/statistics_during_period`) ueber die WebSocket-API aus und schreibt sie im
exakt gleichen Datenmodell nach InfluxDB 2 - Measurement = Einheit, Feld = `value`,
Tags = `domain` / `entity_id` / `friendly_name` / ...

Damit funktionieren die Panels des Grafana-Dashboards `energie-dashboard.json` auch
rueckwirkend.

Benoetigt: pip install websocket-client
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

try:
    import websocket  # websocket-client
except ImportError:  # pragma: no cover
    sys.exit("Fehlendes Paket. Bitte installieren mit:  pip install websocket-client")


# --------------------------------------------------------------------------- Hilfen

def log(msg: str = "") -> None:
    print(msg, flush=True)


def fail(msg: str) -> "NoReturn":  # noqa: F821
    sys.exit(f"FEHLER: {msg}")


def parse_time(value) -> datetime:
    """HA liefert `start`/`end` je nach Version als Epoch-Millisekunden oder ISO-String."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def parse_date_arg(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        fail(f"Ungueltiges Datum: {value!r} (erwartet z. B. 2024-01-01 oder 2024-01-01T00:00:00)")
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def esc_measurement(value: str) -> str:
    return value.replace(",", r"\,").replace(" ", r"\ ")


def esc_tag(value: str) -> str:
    return value.replace(",", r"\,").replace("=", r"\=").replace(" ", r"\ ")


def object_id(entity_id: str) -> str:
    return entity_id.split(".", 1)[1] if "." in entity_id else entity_id


def domain_of(entity_id: str) -> str:
    return entity_id.split(".", 1)[0] if "." in entity_id else ""


# ------------------------------------------------------------------- Home Assistant

class HomeAssistant:
    """Duenner Client fuer die WebSocket- und REST-API von Home Assistant."""

    def __init__(self, url: str, token: str, insecure: bool = False, timeout: int = 120):
        self.base = url.rstrip("/")
        self.token = token
        self.insecure = insecure
        self.timeout = timeout
        self.ws = None
        self._msg_id = 0

    # -- WebSocket ---------------------------------------------------------

    def _ws_url(self) -> str:
        parts = urllib.parse.urlsplit(self.base)
        scheme = "wss" if parts.scheme == "https" else "ws"
        return urllib.parse.urlunsplit((scheme, parts.netloc, "/api/websocket", "", ""))

    def connect(self) -> None:
        sslopt = {"cert_reqs": ssl.CERT_NONE} if self.insecure else None
        try:
            self.ws = websocket.create_connection(
                self._ws_url(), timeout=self.timeout, sslopt=sslopt
            )
        except Exception as exc:
            fail(f"WebSocket-Verbindung zu {self._ws_url()} fehlgeschlagen: {exc}")

        hello = json.loads(self.ws.recv())
        if hello.get("type") != "auth_required":
            fail(f"Unerwartete Begruessung von Home Assistant: {hello}")

        self.ws.send(json.dumps({"type": "auth", "access_token": self.token}))
        auth = json.loads(self.ws.recv())
        if auth.get("type") != "auth_ok":
            fail(f"Authentifizierung abgelehnt: {auth.get('message', auth)}")
        log(f"  Verbunden mit Home Assistant {auth.get('ha_version', '?')}")

    def close(self) -> None:
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None

    def command(self, payload: dict):
        """Sendet ein WS-Kommando und liefert das `result`-Feld der Antwort."""
        self._msg_id += 1
        msg_id = self._msg_id
        self.ws.send(json.dumps({"id": msg_id, **payload}))

        while True:
            raw = self.ws.recv()
            if not raw:
                fail("Verbindung von Home Assistant unerwartet geschlossen")
            msg = json.loads(raw)
            if msg.get("id") != msg_id or msg.get("type") != "result":
                continue  # Events oder Antworten anderer Kommandos ueberspringen
            if not msg.get("success", False):
                err = msg.get("error", {})
                fail(f"{payload['type']} fehlgeschlagen: {err.get('code')} {err.get('message')}")
            return msg.get("result")

    def list_statistic_ids(self) -> dict:
        rows = self.command({"type": "recorder/list_statistic_ids"}) or []
        return {row["statistic_id"]: row for row in rows}

    def energy_prefs(self) -> dict:
        return self.command({"type": "energy/get_prefs"}) or {}

    def statistics(self, statistic_ids, start: datetime, end: datetime, period: str) -> dict:
        return self.command({
            "type": "recorder/statistics_during_period",
            "start_time": start.astimezone(timezone.utc).isoformat(),
            "end_time": end.astimezone(timezone.utc).isoformat(),
            "statistic_ids": list(statistic_ids),
            "period": period,
        }) or {}

    # -- REST --------------------------------------------------------------

    def states(self) -> dict:
        req = urllib.request.Request(
            f"{self.base}/api/states",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        ctx = ssl._create_unverified_context() if self.insecure else None
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                rows = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            fail(f"GET /api/states: HTTP {exc.code} {exc.reason}")
        except Exception as exc:
            fail(f"GET /api/states: {exc}")
        return {row["entity_id"]: row for row in rows}


# ------------------------------------------------------------------------ InfluxDB

class Influx:
    """Schreibt Line Protocol und fuehrt Flux-Queries gegen InfluxDB 2 aus."""

    def __init__(self, url: str, token: str, org: str, bucket: str,
                 insecure: bool = False, timeout: int = 120, dry_run: bool = False):
        self.base = url.rstrip("/")
        self.token = token
        self.org = org
        self.bucket = bucket
        self.insecure = insecure
        self.timeout = timeout
        self.dry_run = dry_run
        self.written = 0

    def _ctx(self):
        return ssl._create_unverified_context() if self.insecure else None

    def write(self, lines) -> None:
        lines = list(lines)
        if not lines:
            return
        self.written += len(lines)
        if self.dry_run:
            return

        query = urllib.parse.urlencode(
            {"org": self.org, "bucket": self.bucket, "precision": "s"}
        )
        req = urllib.request.Request(
            f"{self.base}/api/v2/write?{query}",
            data="\n".join(lines).encode("utf-8"),
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "text/plain; charset=utf-8",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx()).close()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:800]
            fail(f"Influx-Write: HTTP {exc.code} {exc.reason}\n{body}")
        except Exception as exc:
            fail(f"Influx-Write: {exc}")

    def query_rows(self, flux: str):
        """Fuehrt eine Flux-Query aus und liefert die Zeilen als Liste von dicts."""
        body = json.dumps({
            "query": flux,
            "dialect": {"header": True, "annotations": []},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base}/api/v2/query?{urllib.parse.urlencode({'org': self.org})}",
            data=body,
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/csv",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx()) as resp:
                text = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:400]
            log(f"  ! Influx-Query fehlgeschlagen (HTTP {exc.code}): {body}")
            return []
        except Exception as exc:
            log(f"  ! Influx-Query fehlgeschlagen: {exc}")
            return []
        return [row for row in csv.DictReader(io.StringIO(text)) if row.get("_time")]


# ---------------------------------------------------------------- Entity-Ermittlung

def entities_from_energy_prefs(prefs: dict) -> list:
    """Zieht alle statistic_ids aus der Energie-Konfiguration von Home Assistant."""
    keys = (
        "stat_energy_from", "stat_energy_to", "stat_rate",
        "stat_cost", "stat_compensation", "stat_consumption",
    )
    found = []
    blocks = list(prefs.get("energy_sources", []))
    blocks += list(prefs.get("device_consumption", []))
    blocks += list(prefs.get("device_consumption_water", []))
    for block in blocks:
        for key in keys:
            value = block.get(key)
            # Externe Statistiken nutzen ":" statt "." und haben keine Entity.
            if isinstance(value, str) and "." in value and ":" not in value:
                if value not in found:
                    found.append(value)
    return found


def build_tags(entity_id: str, state: dict, static_tags: dict,
               tag_attributes) -> dict:
    """Baut den Tag-Satz so, wie ihn die influxdb-Integration schreiben wuerde."""
    attrs = (state or {}).get("attributes", {})
    tags = {
        "domain": domain_of(entity_id),
        "entity_id": object_id(entity_id),
    }
    for attr in tag_attributes:
        value = attrs.get(attr)
        if value not in (None, ""):
            tags[attr] = str(value)
    tags.update(static_tags)
    return tags


# ------------------------------------------------------------------- Tag-Pruefung

def check_tags(influx: Influx, targets: dict, measurement_of: dict, lookback: str) -> bool:
    """Vergleicht die geplanten Tags mit den bereits live geschriebenen Punkten.

    Weichen die Tags ab, entstehen in InfluxDB zwei getrennte Serien fuer dieselbe
    Entity. increase()/difference() im Dashboard wuerden dann an der Nahtstelle
    zwischen Backfill und Live-Daten springen. Das ist die haeufigste Fehlerquelle,
    deshalb wird sie vor dem Schreiben geprueft.
    """
    log("\n[3/5] Abgleich mit vorhandenen Live-Daten")
    mismatches = 0
    checked = 0

    for entity_id, tags in targets.items():
        flux = (
            f'from(bucket: "{influx.bucket}")\n'
            f"  |> range(start: {lookback})\n"
            f'  |> filter(fn: (r) => r._field == "value")\n'
            f'  |> filter(fn: (r) => r.entity_id == "{object_id(entity_id)}")\n'
            f"  |> last()\n"
            f"  |> limit(n: 1)\n"
        )
        rows = influx.query_rows(flux)
        if not rows:
            continue

        checked += 1
        row = rows[0]
        live_tags = {
            key: value for key, value in row.items()
            if key and not key.startswith("_") and key not in ("result", "table") and value
        }
        live_measurement = row.get("_measurement", "")
        planned_measurement = measurement_of[entity_id]

        problems = []
        if live_measurement != planned_measurement:
            problems.append(
                f"Measurement live={live_measurement!r} geplant={planned_measurement!r}"
            )
        for key in sorted(set(live_tags) | set(tags)):
            live = live_tags.get(key)
            planned = tags.get(key)
            if live != planned:
                problems.append(f"Tag {key}: live={live!r} geplant={planned!r}")

        if problems:
            mismatches += 1
            log(f"  ! {entity_id}")
            for problem in problems:
                log(f"      {problem}")

    if checked == 0:
        log("  Keine Live-Daten im Bucket gefunden - Abgleich uebersprungen.")
        log("  (Normal, wenn die influxdb-Integration noch nicht laeuft.)")
        return True
    if mismatches:
        log(f"\n  {mismatches} von {checked} Entities weichen ab.")
        log("  Backfill und Live-Daten wuerden getrennte Serien bilden.")
        log("  Bitte --tag / --tag-attribute an die influxdb-Konfiguration anpassen")
        log("  oder mit --no-check bewusst ueberspringen.")
        return False

    log(f"  {checked} Entities geprueft, Tags stimmen ueberein.")
    return True


# ------------------------------------------------------------------------- Backfill

def run_backfill(ha: HomeAssistant, influx: Influx, entities: list, meta: dict,
                 targets: dict, measurement_of: dict, start: datetime, end: datetime,
                 period: str, chunk_days: int, batch_size: int) -> dict:
    log(f"\n[4/5] Uebertragung {start:%Y-%m-%d} bis {end:%Y-%m-%d} (Periode: {period})")

    stats = {"points": 0, "skipped_no_value": 0, "chunks": 0}
    per_entity = {entity_id: 0 for entity_id in entities}
    cursor = start

    while cursor < end:
        chunk_end = min(cursor + timedelta(days=chunk_days), end)
        stats["chunks"] += 1
        result = ha.statistics(entities, cursor, chunk_end, period)

        lines = []
        chunk_points = 0
        for entity_id, rows in result.items():
            tags = targets.get(entity_id)
            if tags is None:
                continue
            measurement = esc_measurement(measurement_of[entity_id])
            tag_str = ",".join(
                f"{esc_tag(k)}={esc_tag(v)}" for k, v in tags.items() if v
            )
            prefix = f"{measurement},{tag_str}" if tag_str else measurement
            use_mean = meta.get(entity_id, {}).get("prefer_mean", False)

            for row in rows:
                value = row.get("mean") if use_mean else row.get("state")
                if value is None:
                    # Fallback: Zaehlerstand fehlt -> Mittelwert, und umgekehrt.
                    value = row.get("state") if use_mean else row.get("mean")
                if value is None:
                    stats["skipped_no_value"] += 1
                    continue
                ts = int(parse_time(row["start"]).timestamp())
                lines.append(f"{prefix} value={float(value)} {ts}")
                chunk_points += 1
                per_entity[entity_id] = per_entity.get(entity_id, 0) + 1

                if len(lines) >= batch_size:
                    influx.write(lines)
                    lines = []

        influx.write(lines)
        stats["points"] += chunk_points
        marker = "." if chunk_points else "-"
        log(f"  {marker} {cursor:%Y-%m-%d} bis {chunk_end:%Y-%m-%d}: "
            f"{chunk_points:>8,} Punkte".replace(",", "."))
        cursor = chunk_end

    stats["per_entity"] = per_entity
    return stats


# ----------------------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Uebertraegt Home-Assistant-Langzeitstatistiken nach InfluxDB 2.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Beispiel:\n"
            "  export HA_TOKEN=... INFLUX_TOKEN=...\n"
            "  python3 ha_statistics_backfill.py \\\n"
            "      --ha-url http://homeassistant.local:8123 \\\n"
            "      --influx-url http://192.168.1.50:8086 \\\n"
            "      --influx-org meine-org --influx-bucket homeassistant \\\n"
            "      --start 2023-01-01 --exclude sensor.watermeter_value --dry-run\n"
        ),
    )

    ha_group = parser.add_argument_group("Home Assistant")
    ha_group.add_argument("--ha-url", default=os.environ.get("HA_URL"),
                          help="Basis-URL, z. B. http://homeassistant.local:8123 "
                               "(oder Umgebungsvariable HA_URL)")
    ha_group.add_argument("--ha-token", default=os.environ.get("HA_TOKEN"),
                          help="Long-Lived Access Token (oder HA_TOKEN)")

    influx_group = parser.add_argument_group("InfluxDB 2")
    influx_group.add_argument("--influx-url", default=os.environ.get("INFLUX_URL"),
                              help="z. B. http://192.168.1.50:8086 (oder INFLUX_URL)")
    influx_group.add_argument("--influx-token", default=os.environ.get("INFLUX_TOKEN"),
                              help="API-Token mit Schreib- und Leserecht (oder INFLUX_TOKEN)")
    influx_group.add_argument("--influx-org", default=os.environ.get("INFLUX_ORG"),
                              help="Organisation (oder INFLUX_ORG)")
    influx_group.add_argument("--influx-bucket",
                              default=os.environ.get("INFLUX_BUCKET", "homeassistant"),
                              help="Ziel-Bucket (Standard: homeassistant)")

    scope = parser.add_argument_group("Umfang")
    scope.add_argument("--entity", action="append", default=[], metavar="ENTITY_ID",
                       help="Nur diese Entity uebertragen, mehrfach angebbar. "
                            "Ohne Angabe wird die Energie-Konfiguration von HA gelesen.")
    scope.add_argument("--exclude", action="append", default=[], metavar="ENTITY_ID",
                       help="Entity ausschliessen, mehrfach angebbar")
    scope.add_argument("--start", default="", metavar="DATUM",
                       help="Startzeitpunkt, z. B. 2023-01-01 (Standard: vor 3 Jahren)")
    scope.add_argument("--end", default="", metavar="DATUM",
                       help="Endzeitpunkt (Standard: jetzt). Setze hier den Zeitpunkt, "
                            "ab dem die influxdb-Integration live schreibt.")
    scope.add_argument("--period", default="hour", choices=["5minute", "hour", "day", "month"],
                       help="Statistik-Aufloesung (Standard: hour)")

    schema = parser.add_argument_group("Datenmodell")
    schema.add_argument("--tag", action="append", default=["source=hass"], metavar="K=V",
                        help="Statischer Tag, passend zum Block `tags:` der "
                             "influxdb-Integration (Standard: source=hass)")
    schema.add_argument("--tag-attribute", action="append", default=None, metavar="ATTR",
                        help="Attribut als Tag uebernehmen, passend zu "
                             "`tags_attributes:` (Standard: friendly_name, device_class)")

    behaviour = parser.add_argument_group("Verhalten")
    behaviour.add_argument("--dry-run", action="store_true",
                           help="Nichts schreiben, nur zaehlen und berichten")
    behaviour.add_argument("--no-check", action="store_true",
                           help="Tag-Abgleich mit vorhandenen Live-Daten ueberspringen")
    behaviour.add_argument("--check-only", action="store_true",
                           help="Nur Verbindung und Tag-Abgleich pruefen, nichts uebertragen")
    behaviour.add_argument("--chunk-days", type=int, default=30, metavar="N",
                           help="Groesse der Abfragefenster in Tagen (Standard: 30)")
    behaviour.add_argument("--batch-size", type=int, default=5000, metavar="N",
                           help="Zeilen pro Influx-Write (Standard: 5000)")
    behaviour.add_argument("--insecure", action="store_true",
                           help="TLS-Zertifikate nicht pruefen (selbstsignierte Zertifikate)")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    missing = [name for name, value in (
        ("--ha-url / HA_URL", args.ha_url),
        ("--ha-token / HA_TOKEN", args.ha_token),
        ("--influx-url / INFLUX_URL", args.influx_url),
        ("--influx-token / INFLUX_TOKEN", args.influx_token),
        ("--influx-org / INFLUX_ORG", args.influx_org),
    ) if not value]
    if missing:
        fail("Fehlende Angaben: " + ", ".join(missing))

    tag_attributes = args.tag_attribute
    if tag_attributes is None:
        tag_attributes = ["friendly_name", "device_class"]

    static_tags = {}
    for item in args.tag:
        if "=" not in item:
            fail(f"--tag erwartet KEY=VALUE, bekommen: {item!r}")
        key, value = item.split("=", 1)
        static_tags[key.strip()] = value.strip()

    end = parse_date_arg(args.end) if args.end else datetime.now(timezone.utc)
    end = end.replace(minute=0, second=0, microsecond=0)
    start = parse_date_arg(args.start) if args.start else end - timedelta(days=3 * 365)
    if start >= end:
        fail(f"--start ({start:%Y-%m-%d}) liegt nicht vor --end ({end:%Y-%m-%d})")

    ha = HomeAssistant(args.ha_url, args.ha_token, insecure=args.insecure)
    influx = Influx(args.influx_url, args.influx_token, args.influx_org,
                    args.influx_bucket, insecure=args.insecure, dry_run=args.dry_run)

    log("[1/5] Verbindung zu Home Assistant")
    ha.connect()

    try:
        # ---------------------------------------------------- Entities bestimmen
        log("\n[2/5] Entities und Einheiten ermitteln")
        if args.entity:
            entities = list(dict.fromkeys(args.entity))
            log(f"  {len(entities)} Entities per --entity vorgegeben")
        else:
            entities = entities_from_energy_prefs(ha.energy_prefs())
            log(f"  {len(entities)} Entities aus der Energie-Konfiguration gelesen")

        for excluded in args.exclude:
            if excluded in entities:
                entities.remove(excluded)
                log(f"  - ausgeschlossen: {excluded}")

        if not entities:
            fail("Keine Entities zu uebertragen.")

        statistic_ids = ha.list_statistic_ids()
        states = ha.states()

        targets, measurement_of, meta = {}, {}, {}
        for entity_id in list(entities):
            info = statistic_ids.get(entity_id)
            if info is None:
                log(f"  ! {entity_id}: keine Langzeitstatistik vorhanden - uebersprungen")
                entities.remove(entity_id)
                continue

            state = states.get(entity_id)
            if state is None:
                log(f"  ! {entity_id}: Entity existiert nicht mehr - uebersprungen")
                entities.remove(entity_id)
                continue

            unit = state.get("attributes", {}).get("unit_of_measurement")
            if not unit:
                log(f"  ! {entity_id}: keine unit_of_measurement - uebersprungen")
                entities.remove(entity_id)
                continue

            stat_unit = info.get("statistics_unit_of_measurement")
            if stat_unit and stat_unit != unit:
                log(f"  ! {entity_id}: Statistik in {stat_unit!r}, Entity in {unit!r}. "
                    f"Es wird NICHT umgerechnet.")

            # has_sum -> Zaehlerstand (`state`), sonst Messwert (`mean`).
            prefer_mean = not info.get("has_sum", False)
            meta[entity_id] = {"prefer_mean": prefer_mean}
            measurement_of[entity_id] = unit
            targets[entity_id] = build_tags(entity_id, state, static_tags, tag_attributes)

            kind = "Mittelwert" if prefer_mean else "Zaehlerstand"
            log(f"  + {entity_id:<52} {unit:<5} {kind}")

        if not entities:
            fail("Keine uebertragbaren Entities uebrig.")

        # ---------------------------------------------------------- Tag-Abgleich
        if args.no_check:
            log("\n[3/5] Tag-Abgleich uebersprungen (--no-check)")
        elif not check_tags(influx, targets, measurement_of, f"-{max(args.chunk_days, 30)}d"):
            if not args.check_only:
                return 1

        if args.check_only:
            log("\nNur Pruefung gewuenscht (--check-only) - nichts uebertragen.")
            return 0

        # ------------------------------------------------------------- Backfill
        stats = run_backfill(ha, influx, entities, meta, targets, measurement_of,
                             start, end, args.period, args.chunk_days, args.batch_size)

    finally:
        ha.close()

    # ------------------------------------------------------------------ Bericht
    log("\n[5/5] Ergebnis")
    for entity_id, count in sorted(stats["per_entity"].items(), key=lambda i: -i[1]):
        log(f"  {count:>9,} Punkte  {entity_id}".replace(",", "."))
    total = f"{stats['points']:,}".replace(",", ".")
    log(f"\n  {total} Punkte in {stats['chunks']} Abfragefenstern")
    if stats["skipped_no_value"]:
        log(f"  {stats['skipped_no_value']} Statistikzeilen ohne Wert uebersprungen")
    if args.dry_run:
        log("\n  --dry-run: es wurde nichts nach InfluxDB geschrieben.")
    else:
        log(f"\n  Geschrieben nach {args.influx_url} / Bucket {args.influx_bucket}.")
        log("  Ein erneuter Lauf mit denselben Parametern ueberschreibt dieselben")
        log("  Punkte, es entstehen keine Duplikate.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit("\nAbgebrochen.")
