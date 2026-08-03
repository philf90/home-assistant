#!/usr/bin/env python3
"""Generator für die beiden Proxmox-Grafana-Dashboards.

Erzeugt:
    proxmox-ve-dashboard.json   (UID proxmox-ve)
    proxmox-pbs-dashboard.json  (UID proxmox-pbs)

Alle Queries sind gegen das reale Datenmodell geprüft – siehe proxmox-mockups.md.
Die wichtigsten Eigenheiten, die hier eingebaut sind:

PVE
  * cpustat: nur ``cpu`` und ``wait`` sind Verhältnisse (0–1), alles andere sind
    kumulative Jiffie-Zähler.
  * cpustat enthält für ``object=nodes`` KEINE pressure*-Felder. PSI gibt es nur
    je Gast.
  * blockstat ist auf Node-Ebene ein statfs, kein IO-Zähler.
  * ``status`` ist ein String ("running"), die vCPU-Zahl heißt ``cpus``.
  * nics: der Uplink muss gefiltert werden, sonst summiert das Panel den Verkehr
    über tap*/fwbr*/fwln*/fwpr* mehrfach.

PBS
  * Datastore-Belegung liegt in ``blockstat``, erkennbar am Tag ``datastore``.
    ``object`` steht bei allen Serien auf "host" und taugt nicht als Filter.
  * ``iowait`` ist ein Zähler, die Prozentzahl heißt ``iowait_percent``.
  * Das Netzfeld heißt ``send``, die Thread-Zahl ``cpu_count``.
  * Task-, Snapshot- und GC-Daten kommen aus der API (Infinity), nicht aus Influx.
"""

import json

# --------------------------------------------------------------------------
# Bausteine
# --------------------------------------------------------------------------

DS = {"type": "influxdb", "uid": "${DS}"}
API = {"type": "yesoreyeram-infinity-datasource", "uid": "${DS_API}"}

GREEN, YELLOW, ORANGE, RED = "green", "#EAB839", "orange", "red"


class Layout:
    """Vergibt gridPos zeilenweise auf dem 24-Spalten-Raster."""

    def __init__(self):
        self.y = 0
        self.x = 0
        self.row_h = 0

    def place(self, w, h):
        if self.x + w > 24:
            self.y += self.row_h
            self.x = 0
            self.row_h = 0
        pos = {"h": h, "w": w, "x": self.x, "y": self.y}
        self.x += w
        self.row_h = max(self.row_h, h)
        return pos

    def newline(self):
        if self.x:
            self.y += self.row_h
            self.x = 0
            self.row_h = 0


def thresholds(steps):
    return {"mode": "absolute", "steps": [{"color": c, "value": v} for c, v in steps]}


TH_USAGE = thresholds([(GREEN, None), (YELLOW, 60), (ORANGE, 78), (RED, 90)])
TH_OK = thresholds([(GREEN, None)])


def flux(query, ref="A"):
    return {"datasource": DS, "refId": ref, "query": query.strip()}


def infinity(url, root, columns, ref="A", params=None):
    t = {
        "datasource": API,
        "refId": ref,
        "type": "json",
        "source": "url",
        "format": "table",
        "parser": "backend",
        "url": url,
        "url_options": {"method": "GET", "data": ""},
        "root_selector": root,
        "columns": columns,
    }
    if params:
        t["url_options"]["params"] = [{"key": k, "value": v} for k, v in params]
    return t


def col(selector, text, ctype="string"):
    return {"selector": selector, "text": text, "type": ctype}


_id = [0]


def nid():
    _id[0] += 1
    return _id[0]


def row(title, lay, collapsed=False):
    lay.newline()
    p = {
        "id": nid(),
        "type": "row",
        "title": title,
        "collapsed": collapsed,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": lay.y},
        "panels": [],
    }
    lay.y += 1
    return p


def stat(title, targets, lay, w=3, h=5, unit="none", dec=None, th=None,
         desc="", graph="none", text_mode="auto", mappings=None, calc="lastNotNull",
         transforms=None, fields=""):
    return {
        "id": nid(),
        "type": "stat",
        "title": title,
        "description": desc,
        "datasource": targets[0].get("datasource", DS),
        "gridPos": lay.place(w, h),
        "targets": targets,
        "transformations": transforms or [],
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "thresholds"},
                "unit": unit,
                "decimals": dec,
                "mappings": mappings or [],
                "thresholds": th or TH_OK,
            },
            "overrides": [],
        },
        "options": {
            "colorMode": "value",
            "graphMode": graph,
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {"calcs": [calc], "fields": fields, "values": False},
            "textMode": text_mode,
            "wideLayout": True,
        },
    }


def filter_eq(field, value, include=True):
    return {"id": "filterByValue", "options": {
        "type": "include" if include else "exclude", "match": "all",
        "filters": [{"fieldName": field,
                     "config": {"id": "equal", "options": {"value": value}}}]}}


def timeseries(title, targets, lay, w=8, h=8, unit="none", dec=None, desc="",
               fill=10, stack=False, mx=None, mn=0, legend_calcs=None,
               overrides=None, points=False):
    return {
        "id": nid(),
        "type": "timeseries",
        "title": title,
        "description": desc,
        "datasource": DS,
        "gridPos": lay.place(w, h),
        "targets": targets,
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "decimals": dec,
                "min": mn,
                "max": mx,
                "color": {"mode": "palette-classic"},
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "lineWidth": 2,
                    "fillOpacity": fill,
                    "showPoints": "never" if not points else "auto",
                    "spanNulls": True,
                    "stacking": {"group": "A", "mode": "normal" if stack else "none"},
                    "axisPlacement": "auto",
                    "gradientMode": "none",
                },
                "thresholds": TH_OK,
                "mappings": [],
            },
            "overrides": overrides or [],
        },
        "options": {
            "legend": {
                "displayMode": "table",
                "placement": "bottom",
                "showLegend": True,
                "calcs": legend_calcs or ["mean", "max", "lastNotNull"],
            },
            "tooltip": {"mode": "multi", "sort": "desc"},
        },
    }


def bargauge(title, targets, lay, w=8, h=8, unit="percent", dec=1, th=None, desc=""):
    return {
        "id": nid(),
        "type": "bargauge",
        "title": title,
        "description": desc,
        "datasource": targets[0].get("datasource", DS),
        "gridPos": lay.place(w, h),
        "targets": targets,
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "decimals": dec,
                "min": 0,
                "max": 100,
                "color": {"mode": "thresholds"},
                "thresholds": th or TH_USAGE,
                "mappings": [],
            },
            "overrides": [],
        },
        "options": {
            "displayMode": "lcd",
            "orientation": "horizontal",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "showUnfilled": True,
            "valueMode": "color",
        },
    }


def table(title, targets, lay, w=24, h=10, overrides=None, transforms=None, desc=""):
    return {
        "id": nid(),
        "type": "table",
        "title": title,
        "description": desc,
        "datasource": targets[0].get("datasource", DS),
        "gridPos": lay.place(w, h),
        "targets": targets,
        "transformations": transforms or [],
        "fieldConfig": {
            "defaults": {
                "custom": {"align": "auto", "cellOptions": {"type": "auto"}},
                "mappings": [],
                "thresholds": TH_OK,
            },
            "overrides": overrides or [],
        },
        "options": {"showHeader": True, "footer": {"show": False}},
    }


def textpanel(title, content, lay, w=8, h=8):
    return {
        "id": nid(),
        "type": "text",
        "title": title,
        "gridPos": lay.place(w, h),
        "options": {"mode": "markdown", "content": content},
    }


def ov(field, props):
    return {
        "matcher": {"id": "byName", "options": field},
        "properties": [{"id": k, "value": v} for k, v in props.items()],
    }


def gauge_cell(th=None):
    return {
        "unit": "percent",
        "decimals": 1,
        "max": 100,
        "min": 0,
        "custom.cellOptions": {"type": "gauge", "mode": "gradient"},
        "thresholds": th or TH_USAGE,
    }


# --------------------------------------------------------------------------
# Dashboard 1 – Proxmox VE
# --------------------------------------------------------------------------

def build_ve():
    lay = Layout()
    panels = []

    # ---- Node-Status ----------------------------------------------------
    panels.append(row("Node", lay))

    panels.append(stat(
        "Node", [flux('''
from(bucket: "${bucket}")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "system" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r._field == "uptime")
  |> last()
  |> map(fn: (r) => ({ r with _value: 1.0 }))
''')], lay, w=3, h=5, text_mode="value",
        desc="Es gibt kein Statusfeld für den Node. Online heißt: In den letzten "
             "5 Minuten kam ein Datenpunkt. Kein Wert = Metrikkette unterbrochen.",
        mappings=[
            {"type": "value", "options": {"1": {"text": "Online", "color": "green", "index": 0}}},
            {"type": "special", "options": {"match": "null", "result": {
                "text": "Offline", "color": "red", "index": 1}}},
        ]))

    panels.append(stat(
        "Uptime", [flux('''
from(bucket: "${bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "system" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r._field == "uptime")
  |> last()
''')], lay, w=3, h=5, unit="s", dec=0))

    panels.append(stat(
        "CPU", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r._field == "cpu")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: r._value * 100.0 }))
''')], lay, w=3, h=5, unit="percent", dec=1, th=TH_USAGE, graph="area",
        desc="Feld cpustat.cpu, ein Bruch von 0–1. Die Felder user/system/iowait "
             "sind dagegen kumulative Zähler und hier bewusst nicht verwendet."))

    panels.append(stat(
        "RAM", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "memory" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}")
  |> filter(fn: (r) => r._field == "memused" or r._field == "memtotal")
  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({ _time: r._time,
       _value: float(v: r.memused) / float(v: r.memtotal) * 100.0 }))
''')], lay, w=3, h=5, unit="percent", dec=1, th=TH_USAGE, graph="area",
        desc="Enthält den ZFS ARC. Der ist Cache, kein Verbrauch – siehe Panel "
             "Arbeitsspeicher, wo er als eigene Fläche steht."))

    panels.append(stat(
        "Load 1 min", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r._field == "avg1")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
''')], lay, w=3, h=5, dec=2, graph="area",
        desc="Zur Einordnung immer gegen cpustat.cpus lesen – siehe Panel Load Average."))

    panels.append(stat(
        "IO-Wartezeit", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r._field == "wait")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: r._value * 100.0 }))
''')], lay, w=3, h=5, unit="percent", dec=2, graph="area",
        th=thresholds([(GREEN, None), (YELLOW, 5), (ORANGE, 10), (RED, 15)]),
        desc="Der Node liefert kein PSI. wait ist der nächstbeste Wert: Anteil der "
             "CPU-Zeit, die auf IO gewartet wird."))

    panels.append(stat(
        "Laufende Gäste", [flux('''
from(bucket: "${bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "system")
  |> filter(fn: (r) => r.object == "qemu" or r.object == "lxc")
  |> filter(fn: (r) => r._field == "status")
  |> last()
  |> filter(fn: (r) => r._value == "running")
  |> group()
  |> count()
''')], lay, w=3, h=5, dec=0,
        desc="status ist ein String (\"running\"), keine 1. Ein Vergleich gegen die "
             "Zahl 1 liefert dauerhaft 0."))

    panels.append(stat(
        "Wurzeldateisystem", [flux('''
from(bucket: "${bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "blockstat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r._field == "per")
  |> last()
''')], lay, w=3, h=5, unit="percent", dec=0, th=TH_USAGE,
        desc="blockstat ist bei PVE ein statfs des Wurzeldateisystems, kein IO-Zähler."))

    # ---- Auslastung -----------------------------------------------------
    panels.append(row("Auslastung", lay))

    panels.append(timeseries(
        "CPU-Auslastung", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}")
  |> filter(fn: (r) => r._field == "cpu" or r._field == "wait")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: r._value * 100.0 }))
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=12, h=9, unit="percent", dec=2, fill=15,
        desc="cpu und wait sind die einzigen Verhältniszahlen in cpustat. Für eine "
             "Aufschlüsselung nach user/system/iowait müssten die Zähler über "
             "difference() gegen total normalisiert werden."))

    panels.append(timeseries(
        "Arbeitsspeicher", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "memory" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}")
  |> filter(fn: (r) => r._field == "memused" or r._field == "arcsize")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({ _time: r._time,
       "Gäste + Dienste": r.memused - r.arcsize,
       "ZFS ARC": r.arcsize }))
''')], lay, w=12, h=9, unit="bytes", stack=True, fill=40,
        desc="Der ARC ist Cache und wird bei Bedarf sofort freigegeben – deshalb "
             "eine eigene Stapelfläche und nicht Teil von 'belegt'."))

    panels.append(timeseries(
        "Load Average", [
            flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}")
  |> filter(fn: (r) => r._field =~ /^avg(1|5|15)$/)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''', "A"),
            flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r._field == "cpus")
  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
  |> map(fn: (r) => ({ _time: r._time, "CPU-Threads": r._value }))
''', "B"),
        ], lay, w=8, h=9, dec=2, fill=0,
        desc="Die Thread-Zahl kommt aus cpustat.cpus und wandert damit automatisch "
             "mit, wenn du CPUs umbaust. Load oberhalb dieser Linie heißt: Prozesse "
             "warten tatsächlich auf CPU-Zeit.",
        overrides=[ov("CPU-Threads", {
            "custom.lineStyle": {"fill": "dash", "dash": [8, 6]},
            "color": {"mode": "fixed", "fixedColor": "red"},
            "custom.fillOpacity": 0,
        })]))

    panels.append(timeseries(
        "Netzwerk ${nic}", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "nics" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}" and r.instance == "${nic}")
  |> filter(fn: (r) => r._field == "receive" or r._field == "transmit")
  |> derivative(unit: 1s, nonNegative: true)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=8, h=9, unit="Bps", fill=15,
        desc="Der Interface-Filter ist Pflicht: Der Node meldet neben dem Uplink auch "
             "vmbr0, die VLANs und je Gast tap*/fwbr*/fwln*/fwpr*. Ohne Filter wird "
             "derselbe Verkehr mehrfach summiert."))

    panels.append(timeseries(
        "ZFS ARC gegen arcmax", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "memory" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}")
  |> filter(fn: (r) => r._field == "arcsize" or r._field == "arcmax")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=8, h=9, unit="bytes", fill=15,
        desc="Liegt arcsize dauerhaft an arcmax, ist der ARC gedeckelt und kann nicht "
             "wachsen. Das ist eine Konfigurationsentscheidung, keine Auslastung.",
        overrides=[ov("arcmax", {
            "custom.lineStyle": {"fill": "dash", "dash": [8, 6]},
            "color": {"mode": "fixed", "fixedColor": "red"},
            "custom.fillOpacity": 0,
        })]))

    # ---- Storage --------------------------------------------------------
    panels.append(row("Storage", lay))

    panels.append(bargauge(
        "Belegung je Storage", [flux('''
from(bucket: "${bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "system" and r.object == "storages")
  |> filter(fn: (r) => r._field == "used" or r._field == "total")
  |> last()
  |> keep(columns: ["_field", "_value", "host"])
  |> group()
  |> pivot(rowKey: ["host"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({ _time: now(), _field: r.host,
       _value: float(v: r.used) / float(v: r.total) * 100.0 }))
  |> group(columns: ["_field"])
''')], lay, w=8, h=9,
        desc="Der Tag host trägt bei object=storages die Storage-ID, nicht den "
             "Hostnamen."))

    panels.append(timeseries(
        "Auslastung je Storage", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "system" and r.object == "storages")
  |> filter(fn: (r) => r._field == "used" or r._field == "total")
  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
  |> pivot(rowKey: ["_time", "host"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({ _time: r._time, _field: r.host,
       _value: float(v: r.used) / float(v: r.total) * 100.0 }))
  |> group(columns: ["_field"])
''')], lay, w=8, h=9, unit="percent", dec=1, mx=100, fill=0,
        desc="Bewusst Prozent statt Byte: Storages mit 27 TiB und 450 GiB sind in "
             "absoluten Zahlen im selben Diagramm nicht vergleichbar."))

    panels.append(timeseries(
        "Wurzeldateisystem", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "blockstat" and r.object == "nodes")
  |> filter(fn: (r) => r.host == "${node}")
  |> filter(fn: (r) => r._field == "used" or r._field == "blocks")
  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=8, h=9, unit="bytes", fill=15,
        desc="blocks = Gesamtgröße, used = belegt. Die su_*- und user_*-Varianten "
             "sind identisch, solange keine Root-Reserve gesetzt ist.",
        overrides=[ov("blocks", {
            "custom.lineStyle": {"fill": "dash", "dash": [8, 6]},
            "color": {"mode": "fixed", "fixedColor": "red"},
            "custom.fillOpacity": 0,
        })]))

    panels.append(table(
        "Storages", [flux('''
from(bucket: "${bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "system" and r.object == "storages")
  |> filter(fn: (r) => r._field == "used" or r._field == "total"
                    or r._field == "avail")
  |> last()
  |> keep(columns: ["_field", "_value", "host", "type"])
  |> group()
  |> pivot(rowKey: ["host", "type"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({
       Storage: r.host,
       Typ: r.type,
       Belegt: r.used,
       Gesamt: r.total,
       Frei: r.avail,
       Auslastung: float(v: r.used) / float(v: r.total) * 100.0 }))
  |> sort(columns: ["Auslastung"], desc: true)
''')], lay, w=24, h=8,
        transforms=[{"id": "organize", "options": {
            "excludeByName": {"_start": True, "_stop": True, "_time": True,
                              "result": True, "table": True}}}],
        overrides=[
            ov("Auslastung", gauge_cell()),
            ov("Belegt", {"unit": "bytes"}),
            ov("Gesamt", {"unit": "bytes"}),
            ov("Frei", {"unit": "bytes"}),
        ]))

    # ---- Gäste ----------------------------------------------------------
    panels.append(row("Gäste", lay))

    panels.append(table(
        "Alle Gäste", [
            flux('''
from(bucket: "${bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "system")
  |> filter(fn: (r) => r.object == "qemu" or r.object == "lxc")
  |> filter(fn: (r) => contains(value: r._field, set: [
       "cpu", "cpus", "mem", "maxmem", "memhost",
       "netin", "netout", "diskread", "diskwrite", "uptime"]))
  |> last()
  |> keep(columns: ["_field", "_value", "vmid", "host", "object"])
  |> group()
  |> pivot(rowKey: ["vmid", "host", "object"], columnKey: ["_field"],
           valueColumn: "_value")
  |> map(fn: (r) => ({
       VMID: r.vmid,
       Name: r.host,
       Typ: r.object,
       CPU: r.cpu * 100.0,
       vCPU: r.cpus,
       RAM: float(v: r.mem) / float(v: r.maxmem) * 100.0,
       "RAM Host": r.memhost,
       "Disk gelesen": r.diskread,
       "Disk geschrieben": r.diskwrite,
       "Netz ein": r.netin,
       "Netz aus": r.netout,
       Uptime: r.uptime }))
  |> sort(columns: ["CPU"], desc: true)
''', "A"),
            # status ist ein String und muss getrennt geholt werden, sonst
            # kollidiert _value beim group() zwischen string und float
            flux('''
from(bucket: "${bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "system")
  |> filter(fn: (r) => r.object == "qemu" or r.object == "lxc")
  |> filter(fn: (r) => r._field == "status")
  |> last()
  |> keep(columns: ["_value", "vmid"])
  |> group()
  |> rename(columns: {_value: "Status", vmid: "VMID"})
''', "B"),
        ], lay, w=24, h=12,
        desc="CPU ist relativ zu den eigenen vCPUs des Gastes. disk und maxdisk sind "
             "bei QEMU-VMs stets 0 und deshalb nicht enthalten – der Host sieht nicht "
             "in das Gastdateisystem hinein.",
        transforms=[
            {"id": "joinByField", "options": {"byField": "VMID", "mode": "outer"}},
            {"id": "organize", "options": {"excludeByName": {
                "_start": True, "_stop": True, "_time": True,
                "result": True, "table": True}}},
        ],
        overrides=[
            ov("CPU", gauge_cell()),
            ov("RAM", gauge_cell()),
            ov("RAM Host", {"unit": "bytes"}),
            ov("Disk gelesen", {"unit": "bytes"}),
            ov("Disk geschrieben", {"unit": "bytes"}),
            ov("Netz ein", {"unit": "bytes"}),
            ov("Netz aus", {"unit": "bytes"}),
            ov("Uptime", {"unit": "s", "decimals": 0}),
            ov("Status", {"mappings": [{"type": "value", "options": {
                "running": {"color": "green", "index": 0, "text": "running"},
                "stopped": {"color": "text", "index": 1, "text": "stopped"}}}],
                "custom.cellOptions": {"type": "color-text"}}),
        ]))

    panels.append(timeseries(
        "CPU je Gast", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "system")
  |> filter(fn: (r) => r.object == "qemu" or r.object == "lxc")
  |> filter(fn: (r) => r._field == "cpu")
  |> filter(fn: (r) => r.vmid =~ /^${guest:regex}$/)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ _time: r._time, _field: r.host, _value: r._value * 100.0 }))
  |> group(columns: ["_field"])
''')], lay, w=8, h=9, unit="percent", dec=1, fill=0,
        desc="Prozent der dem Gast zugewiesenen vCPUs, nicht des Nodes."))

    panels.append(timeseries(
        "RAM je Gast", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "system")
  |> filter(fn: (r) => r.object == "qemu" or r.object == "lxc")
  |> filter(fn: (r) => r._field == "mem" or r._field == "maxmem")
  |> filter(fn: (r) => r.vmid =~ /^${guest:regex}$/)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> pivot(rowKey: ["_time", "vmid", "host"], columnKey: ["_field"],
           valueColumn: "_value")
  |> map(fn: (r) => ({ _time: r._time, _field: r.host,
       _value: float(v: r.mem) / float(v: r.maxmem) * 100.0 }))
  |> group(columns: ["_field"])
''')], lay, w=8, h=9, unit="percent", dec=1, mx=100, fill=0,
        desc="mem entspricht ballooninfo.total_mem minus free_mem, ist also der "
             "tatsächliche Verbrauch im Gast – nicht die vom Host zugeteilte Menge."))

    panels.append(timeseries(
        "IO-Pressure je Gast", [flux('''
from(bucket: "${bucket}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "system")
  |> filter(fn: (r) => r.object == "qemu" or r.object == "lxc")
  |> filter(fn: (r) => r._field == "pressureiosome")
  |> filter(fn: (r) => r.vmid =~ /^${guest:regex}$/)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ _time: r._time, _field: r.host, _value: r._value }))
  |> group(columns: ["_field"])
''')], lay, w=8, h=9, unit="percent", dec=1, fill=0,
        desc="Anteil der Zeit, in der dieser Gast auf IO wartete. Gibt es nur je Gast – "
             "für den Node liefert der Metric Server kein PSI. Beantwortet als "
             "einziges Panel die Frage, WELCHER Gast die Platte blockiert."))

    # ---- Diagnose -------------------------------------------------------
    panels.append(row("Diagnose", lay))

    panels.append(table(
        "Datenaktualität je Quelle", [flux('''
from(bucket: "${bucket}")
  |> range(start: -24h)
  |> filter(fn: (r) => r._field == "uptime" or r._field == "total")
  |> group(columns: ["object", "host"])
  |> last()
  |> map(fn: (r) => ({
       Quelle: r.object + " / " + r.host,
       "Letzter Datenpunkt": r._time,
       "Alter": float(v: int(v: now()) - int(v: r._time)) / 1000000000.0 }))
  |> group()
  |> sort(columns: ["Alter"], desc: true)
''')], lay, w=12, h=9,
        desc="Grafana zeigt ohne Weiteres den letzten bekannten Wert – auch wenn er "
             "drei Tage alt ist. Dieses Panel ist die Gegenprobe.",
        transforms=[{"id": "organize", "options": {"excludeByName": {
            "_start": True, "_stop": True, "result": True, "table": True}}}],
        overrides=[ov("Alter", {"unit": "s", "decimals": 0, "thresholds": thresholds(
            [(GREEN, None), (YELLOW, 60), (RED, 300)]),
            "custom.cellOptions": {"type": "color-text"}})]))

    panels.append(textpanel("Lesehilfe", VE_NOTES, lay, w=12, h=9))

    return dashboard(
        uid="proxmox-ve",
        title="Proxmox VE",
        description="Node, Storages und Gäste des Proxmox-VE-Servers aus InfluxDB 2.",
        tags=["proxmox"],
        panels=panels,
        templating=[
            var_datasource("DS", "influxdb", "InfluxDB (Proxmox)"),
            var_constant("bucket", "proxmox", "Bucket"),
            var_query("node", "Node", '''
import "influxdata/influxdb/schema"
schema.tagValues(bucket: "${bucket}", tag: "host",
  predicate: (r) => r.object == "nodes")
'''),
            var_query("nic", "Uplink-Interface", '''
import "influxdata/influxdb/schema"
schema.tagValues(bucket: "${bucket}", tag: "instance",
  predicate: (r) => r._measurement == "nics" and r.object == "nodes")
''', regex="/^(en|eth|bond|vmbr)/"),
            var_query("guest", "Gast", '''
import "influxdata/influxdb/schema"
schema.tagValues(bucket: "${bucket}", tag: "vmid")
''', multi=True, include_all=True),
        ],
        links=[{"asDropdown": True, "icon": "dashboard", "includeVars": True,
                "keepTime": True, "tags": ["proxmox"], "targetBlank": False,
                "title": "Proxmox-Dashboards", "tooltip": "", "type": "dashboards",
                "url": ""}],
    )


VE_NOTES = """\
### Was welche Zahl bedeutet

* **CPU des Gastes** ist relativ zu seinen eigenen vCPUs, nicht zum Node.
  `100 %` bei einem Gast mit 4 vCPU heißt: 4 Threads des Nodes.
* **RAM des Nodes** enthält den ZFS **ARC**. Der ist Cache, kein Verbrauch, und wird
  bei Bedarf sofort freigegeben – deshalb im Panel *Arbeitsspeicher* eine eigene
  Stapelfläche.
* **Load** ohne Bezug zur Thread-Zahl ist wertlos. Die gestrichelte Linie kommt aus
  `cpustat.cpus` und wandert bei einem CPU-Umbau automatisch mit.
* **`mem` gegen `memhost`**: `mem` ist die Sicht im Gast, `memhost` der Verbrauch des
  QEMU-Prozesses auf dem Node. Für „passt der Gast noch in den Node" zählt `memhost`.

### Fallen im Datenmodell

* In `cpustat` sind **nur `cpu` und `wait` Verhältnisse** (0–1). `user`, `system`,
  `iowait`, `idle` und `total` sind kumulative Jiffie-Zähler.
* **PSI gibt es nur je Gast**, nicht für den Node. Für den Node bleibt `wait`.
* **`blockstat` ist auf Node-Ebene ein `statfs`**, kein IO-Zähler – Disk-Durchsatz des
  Nodes ist mit dem Metric Server nicht darstellbar. Auf Gast-Ebene ist dasselbe
  Measurement dagegen die volle QEMU-Blockstatistik.
* **`status` ist ein String** (`"running"`), keine 1. Die vCPU-Zahl heißt `cpus`.
* **`disk` und `maxdisk` sind bei QEMU-VMs stets 0.**

### Wenn ein Panel leer bleibt

Feldnamen unterscheiden sich zwischen PVE-Versionen. Gegenprobe:

```
import "influxdata/influxdb/schema"
schema.fieldKeys(bucket: "proxmox",
  predicate: (r) => r._measurement == "cpustat")
```
"""


# --------------------------------------------------------------------------
# Dashboard 2 – Proxmox Backup Server
# --------------------------------------------------------------------------

def build_pbs():
    lay = Layout()
    panels = []

    usage_cols = [
        col("gc-status.index-data-bytes", "Logisch", "number"),
        col("gc-status.disk-bytes", "Auf Platte", "number"),
        col("gc-status.pending-bytes", "Wartet auf GC", "number"),
        col("gc-status.removed-bytes", "Letzter GC frei", "number"),
        col("gc-status.still-bad", "Defekte Chunks", "number"),
        col("estimated-full-date", "Voll am", "timestamp_epoch_s"),
        col("avail", "Frei", "number"),
        col("total", "Gesamt", "number"),
        col("used", "Belegt", "number"),
    ]

    # ---- Backup-Lage ----------------------------------------------------
    panels.append(row("Backup-Lage", lay))

    task_cols = [
        col("starttime", "Beginn", "timestamp_epoch_s"),
        col("starttime", "_start", "number"),
        col("endtime", "_end", "number"),
        col("worker_type", "Typ"),
        col("worker_id", "Ziel"),
        col("status", "Status"),
        col("user", "Benutzer"),
    ]
    tasks_target = infinity(
        "/api2/json/nodes/localhost/tasks", "data", task_cols,
        params=[("limit", "500"), ("since", "${__from:date:seconds}")])

    panels.append(stat(
        "Letztes Backup", [dict(tasks_target, refId="A")], lay, w=4, h=5,
        unit="dateTimeFromNow", text_mode="value", calc="max", fields="/^Beginn$/",
        transforms=[filter_eq("Typ", "backup"), filter_eq("Status", "OK")],
        desc="Jüngster erfolgreich beendeter Backup-Task. Die beiden Filter sind "
             "wichtig: Ohne sie zeigt die Kachel den letzten beliebigen Task – auch "
             "einen logrotate – und behauptet damit ein Backup, das es nicht gab."))

    panels.append(stat(
        "Fehlgeschlagene Tasks", [dict(tasks_target, refId="A")], lay, w=4, h=5,
        dec=0, calc="count", fields="/^Status$/",
        th=thresholds([(GREEN, None), (RED, 1)]),
        transforms=[filter_eq("Status", "OK", include=False)],
        desc="Alle Tasks im gewählten Zeitraum, deren Status nicht OK ist – "
             "Backups ebenso wie Verifikation, Prune und Garbage-Collect."))

    usage_target = infinity("/api2/json/status/datastore-usage", "data", usage_cols)

    panels.append(stat(
        "Dedup-Faktor", [dict(usage_target, refId="A")], lay, w=4, h=5,
        unit="none", dec=2, fields="/^Dedup$/",
        transforms=[{"id": "calculateField", "options": {
            "alias": "Dedup", "mode": "binary",
            "binary": {"left": "Logisch", "operator": "/", "right": "Auf Platte"},
            "replaceFields": False}}],
        desc="Logische Größe aller Indizes geteilt durch den belegten Chunk-Store – "
             "beide Werte stehen fertig in gc-status. Ein Rechenweg über die "
             "Snapshot-Liste ist nicht nötig."))

    panels.append(stat(
        "Voll am", [dict(usage_target, refId="A")], lay, w=4, h=5,
        unit="dateTimeFromNow", text_mode="value", fields="/^Voll am$/",
        desc="PBS rechnet die Prognose selbst und liefert sie als "
             "estimated-full-date. Das ist belastbarer als eine lineare "
             "Fortschreibung über die letzten 14 Tage, weil PBS die eigene "
             "Verlaufskurve kennt."))

    panels.append(stat(
        "Defekte Chunks", [dict(usage_target, refId="A")], lay, w=4, h=5,
        dec=0, th=thresholds([(GREEN, None), (RED, 1)]), fields="/^Defekte Chunks$/",
        desc="gc-status.still-bad: Chunks, die der letzte Garbage-Collect als "
             "beschädigt erkannt und NICHT reparieren konnte. Alles über 0 bedeutet "
             "beschädigte Backups."))

    panels.append(stat(
        "Wartet auf Garbage-Collect", [dict(usage_target, refId="A")], lay, w=4, h=5,
        unit="bytes", fields="/^Wartet auf GC$/",
        desc="gc-status.pending-bytes: So viel Platz gibt der nächste GC-Lauf frei. "
             "Wächst der Wert dauerhaft, läuft die Aufräumkette nicht."))

    # ---- Datastore ------------------------------------------------------
    panels.append(row("Datastore", lay))

    panels.append(bargauge(
        "Belegung je Datastore", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "blockstat")
  |> filter(fn: (r) => exists r.datastore)
  |> filter(fn: (r) => r._field == "used" or r._field == "total")
  |> last()
  |> keep(columns: ["_field", "_value", "datastore"])
  |> group()
  |> pivot(rowKey: ["datastore"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({ _time: now(), _field: r.datastore,
       _value: float(v: r.used) / float(v: r.total) * 100.0 }))
  |> group(columns: ["_field"])
''')], lay, w=8, h=9,
        desc="Die Belegung liegt in blockstat, nicht in einem Measurement disk. "
             "Unterschieden wird über die Existenz des Tags datastore – object steht "
             "bei allen Serien auf \"host\"."))

    panels.append(timeseries(
        "Belegungsverlauf", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "blockstat")
  |> filter(fn: (r) => exists r.datastore)
  |> filter(fn: (r) => r._field == "used" or r._field == "total")
  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
  |> pivot(rowKey: ["_time", "datastore"], columnKey: ["_field"],
           valueColumn: "_value")
  |> map(fn: (r) => ({ _time: r._time, _field: r.datastore, _value: r.used }))
  |> group(columns: ["_field"])
''')], lay, w=16, h=9, unit="bytes", fill=10,
        desc="Für die Prognose nicht nötig, die liefert PBS als estimated-full-date "
             "in der Kachel oben. Dieses Panel zeigt den tatsächlichen Verlauf inkl. "
             "der Sprünge nach jedem Garbage-Collect."))

    panels.append(timeseries(
        "Täglicher Zuwachs", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "blockstat")
  |> filter(fn: (r) => exists r.datastore and r._field == "used")
  |> aggregateWindow(every: 1d, fn: last, createEmpty: false)
  |> difference(nonNegative: false)
  |> map(fn: (r) => ({ _time: r._time, _field: r.datastore, _value: r._value }))
  |> group(columns: ["_field"])
''')], lay, w=12, h=8, unit="bytes", fill=60, mn=None,
        desc="nonNegative bewusst auf false: Ein Tag mit deutlich negativem Zuwachs "
             "ist ein Garbage-Collect. Verschwinden diese Ausschläge, läuft die "
             "Aufräumkette nicht mehr und der Datastore wächst still bis zum Anschlag."))

    panels.append(table(
        "Datastore-Status", [dict(usage_target, refId="A")], lay, w=12, h=8,
        desc="Kommt vollständig aus /api2/json/status/datastore-usage.",
        overrides=[
            ov("Logisch", {"unit": "bytes"}),
            ov("Auf Platte", {"unit": "bytes"}),
            ov("Wartet auf GC", {"unit": "bytes"}),
            ov("Letzter GC frei", {"unit": "bytes"}),
            ov("Frei", {"unit": "bytes"}),
            ov("Gesamt", {"unit": "bytes"}),
            ov("Belegt", {"unit": "bytes"}),
            ov("Defekte Chunks", {"thresholds": thresholds([(GREEN, None), (RED, 1)]),
                                  "custom.cellOptions": {"type": "color-text"}}),
        ]))

    # ---- Backup-Jobs ----------------------------------------------------
    panels.append(row("Backup-Jobs", lay))

    dur_transforms = [
        {"id": "calculateField", "options": {
            "alias": "Dauer", "mode": "binary",
            "binary": {"left": "_end", "operator": "-", "right": "_start"},
            "replaceFields": False}},
        {"id": "organize", "options": {"excludeByName": {"_start": True, "_end": True}}},
    ]

    panels.append(table(
        "Task-Historie", [dict(tasks_target, refId="A")], lay, w=14, h=11,
        desc="worker_type kennt bei PBS die Werte backup, verificationjob, "
             "garbage_collection, prunejob, logrotate und aptupdate. Ein sync-Task "
             "erscheint nur, wenn ein Sync-Job auf ein zweites Ziel eingerichtet ist.",
        transforms=dur_transforms + [
            {"id": "sortBy", "options": {"fields": {},
                                         "sort": [{"field": "Beginn", "desc": True}]}}],
        overrides=[
            ov("Dauer", {"unit": "s", "decimals": 0}),
            ov("Status", {"mappings": [{"type": "value", "options": {
                "OK": {"color": "green", "index": 0}}},
                {"type": "special", "options": {"match": "empty", "result": {
                    "color": "text", "index": 1, "text": "läuft"}}}],
                "custom.cellOptions": {"type": "color-text"}}),
        ]))

    panels.append(table(
        "Snapshots", [infinity(
            "/api2/json/admin/datastore/${datastore}/snapshots", "data", [
                col("backup-type", "Typ"),
                col("backup-id", "ID"),
                col("backup-time", "Zeitpunkt", "timestamp_epoch_s"),
                col("comment", "Bezeichnung"),
                col("size", "Größe logisch", "number"),
                col("verification.state", "Verifikation"),
                col("owner", "Besitzer"),
                col("protected", "Geschützt"),
            ])], lay, w=10, h=11,
        desc="verification.state ist \"ok\", \"failed\" – oder fehlt, wenn der "
             "Snapshot nie geprüft wurde. Ein unverifiziertes Backup ist eine "
             "Vermutung, kein Backup.",
        transforms=[{"id": "sortBy", "options": {
            "fields": {}, "sort": [{"field": "Zeitpunkt", "desc": True}]}}],
        overrides=[
            ov("Größe logisch", {"unit": "bytes"}),
            ov("Verifikation", {"mappings": [
                {"type": "value", "options": {
                    "ok": {"color": "green", "index": 0},
                    "failed": {"color": "red", "index": 1}}},
                {"type": "special", "options": {"match": "empty", "result": {
                    "color": "orange", "index": 2, "text": "nie geprüft"}}}],
                "custom.cellOptions": {"type": "color-text"}}),
        ]))

    panels.append(table(
        "Backup-Dauer je Ziel", [dict(tasks_target, refId="A")], lay, w=24, h=8,
        desc="Dauer = endtime − starttime. Die API liefert keine fertige Dauer.",
        transforms=dur_transforms + [
            {"id": "filterByValue", "options": {"type": "include", "match": "all",
             "filters": [{"fieldName": "Typ", "config": {
                 "id": "equal", "options": {"value": "backup"}}}]}},
            {"id": "groupBy", "options": {"fields": {
                "Ziel": {"aggregations": [], "operation": "groupby"},
                "Dauer": {"aggregations": ["lastNotNull", "max", "mean"],
                          "operation": "aggregate"}}}},
        ],
        overrides=[
            ov("Dauer (lastNotNull)", {"unit": "s", "decimals": 0,
                                       "custom.cellOptions": {"type": "gauge",
                                                              "mode": "gradient"}}),
            ov("Dauer (max)", {"unit": "s", "decimals": 0}),
            ov("Dauer (mean)", {"unit": "s", "decimals": 0}),
        ]))

    # ---- PBS-Host -------------------------------------------------------
    panels.append(row("PBS-Host", lay))

    panels.append(timeseries(
        "CPU-Auslastung", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat")
  |> filter(fn: (r) => r._field == "cpu" or r._field == "iowait_percent")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: r._value * 100.0 }))
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=8, h=8, unit="percent", dec=2, fill=15,
        desc="Nicht iowait nehmen – das ist ein kumulativer Zähler. Die auswertbare "
             "Prozentzahl heißt iowait_percent. Steigt sie stärker als cpu, limitiert "
             "die Platte und eine schnellere CPU bringt nichts."))

    panels.append(timeseries(
        "Arbeitsspeicher", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "memory")
  |> filter(fn: (r) => r._field == "memused" or r._field == "memavailable")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=8, h=8, unit="bytes", fill=15,
        desc="PBS nutzt für Verifikation und GC viel Page-Cache. memused sieht dann "
             "hoch aus, obwohl der Speicher jederzeit freigegeben werden kann – "
             "memavailable ist die ehrlichere Zahl."))

    panels.append(timeseries(
        "Load Average", [
            flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat")
  |> filter(fn: (r) => r._field =~ /^avg(1|5|15)$/)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''', "A"),
            flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "cpustat" and r._field == "cpu_count")
  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
  |> map(fn: (r) => ({ _time: r._time, "CPU-Threads": r._value }))
''', "B"),
        ], lay, w=8, h=8, dec=2, fill=0,
        desc="Die Thread-Zahl heißt bei PBS cpu_count, bei PVE cpus. Wer Panels "
             "zwischen den Dashboards kopiert, läuft genau hier auf.",
        overrides=[ov("CPU-Threads", {
            "custom.lineStyle": {"fill": "dash", "dash": [8, 6]},
            "color": {"mode": "fixed", "fixedColor": "red"},
            "custom.fillOpacity": 0})]))

    panels.append(timeseries(
        "Disk-Durchsatz", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "blockstat")
  |> filter(fn: (r) => not exists r.datastore)
  |> filter(fn: (r) => r._field == "read_bytes" or r._field == "write_bytes")
  |> derivative(unit: 1s, nonNegative: true)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=12, h=8, unit="Bps", fill=15,
        desc="Der datastore-Filter ist Pflicht: blockstat liegt zweimal vor, mit und "
             "ohne datastore-Tag. Liegen Datastore und Wurzeldateisystem auf demselben "
             "Gerät, sind beide Serien identisch und würden doppelt gezeichnet."))

    panels.append(timeseries(
        "Netzwerk ${nic_pbs}", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "nics" and r.instance == "${nic_pbs}")
  |> filter(fn: (r) => r._field == "receive" or r._field == "send")
  |> derivative(unit: 1s, nonNegative: true)
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> keep(columns: ["_time", "_value", "_field"])
''')], lay, w=12, h=8, unit="Bps", fill=15,
        desc="Das Feld heißt bei PBS send, nicht transmit. Ein Backup-Ziel empfängt "
             "viel und sendet wenig – kippt das Verhältnis, läuft vermutlich ein "
             "Restore oder ein Sync-Job."))

    # ---- Diagnose -------------------------------------------------------
    panels.append(row("Diagnose", lay))

    panels.append(table(
        "Datenaktualität je Quelle", [flux('''
from(bucket: "${bucket_pbs}")
  |> range(start: -24h)
  |> filter(fn: (r) => r._field == "total" or r._field == "memtotal")
  |> group(columns: ["_measurement", "datastore"])
  |> last()
  |> map(fn: (r) => ({
       Quelle: r._measurement + (if exists r.datastore then " / " + r.datastore else ""),
       "Letzter Datenpunkt": r._time,
       "Alter": float(v: int(v: now()) - int(v: r._time)) / 1000000000.0 }))
  |> group()
  |> sort(columns: ["Alter"], desc: true)
''')], lay, w=12, h=9,
        transforms=[{"id": "organize", "options": {"excludeByName": {
            "_start": True, "_stop": True, "result": True, "table": True}}}],
        overrides=[ov("Alter", {"unit": "s", "decimals": 0, "thresholds": thresholds(
            [(GREEN, None), (YELLOW, 60), (RED, 300)]),
            "custom.cellOptions": {"type": "color-text"}})]))

    panels.append(textpanel("Grenzen dieses Dashboards", PBS_NOTES, lay, w=12, h=9))

    return dashboard(
        uid="proxmox-pbs",
        title="Proxmox Backup Server",
        description="Backup-Lage, Datastore und Host des PBS aus InfluxDB 2 und der PBS-API.",
        tags=["proxmox"],
        panels=panels,
        templating=[
            var_datasource("DS", "influxdb", "InfluxDB (Proxmox)"),
            var_datasource("DS_API", "yesoreyeram-infinity-datasource", "PBS-API (Infinity)"),
            var_constant("bucket_pbs", "proxmox-backup", "Bucket"),
            var_query("datastore", "Datastore", '''
import "influxdata/influxdb/schema"
schema.tagValues(bucket: "${bucket_pbs}", tag: "datastore")
'''),
            var_query("nic_pbs", "Interface", '''
import "influxdata/influxdb/schema"
schema.tagValues(bucket: "${bucket_pbs}", tag: "instance",
  predicate: (r) => r._measurement == "nics")
''', regex="/^(en|eth|bond)/"),
        ],
        links=[{"asDropdown": True, "icon": "dashboard", "includeVars": True,
                "keepTime": True, "tags": ["proxmox"], "targetBlank": False,
                "title": "Proxmox-Dashboards", "tooltip": "", "type": "dashboards",
                "url": ""}],
    )


PBS_NOTES = """\
### Kommt nicht aus InfluxDB

Der Metric Server des PBS liefert **nur Host- und Datastore-Metriken**. Alle Panels mit
Task-, Snapshot- oder GC-Bezug hängen an der PBS-API über das **Infinity**-Plugin:

* Task-Ergebnisse, Backup-Dauer, übertragene Datenmenge
* Snapshot-Zahlen, Dedup-Faktor, Verifikationsstatus
* Prune- und GC-Zeitpunkte
* **Uptime** – anders als PVE schreibt PBS kein `uptime`-Feld

Der API-Token braucht die Rolle `Audit` auf dem Pfad `/`. Mit aktiver
*Privilege Separation* hat ein frisch angelegter Token **keinerlei** Rechte, bis diese
Zuweisung existiert – das ist die häufigste Ursache für 403.

### Fallen im Influx-Datenmodell

* **Kein Measurement `disk`.** Die Datastore-Belegung liegt in `blockstat`.
* **`object` steht bei allen Serien auf `host`** und taugt nicht zur Unterscheidung.
  Der Datastore hängt an der Existenz des Tags `datastore`.
* **`iowait` ist ein Zähler**, auswertbar ist `iowait_percent`.
* **Das Netzfeld heißt `send`**, nicht `transmit`. Die Thread-Zahl heißt `cpu_count`,
  bei PVE dagegen `cpus`.
* `nics` führt die String-Felder `device` und `ty`, die bei Sammelabfragen über den
  ganzen Bucket eine Schema-Kollision auslösen.

### Was auch die API nicht liefert

* **SMART-Werte der Platten.** Dafür braucht es `smartctl` plus Telegraf auf dem Host.
* **Restore-Tests.** Kein Monitoring beantwortet, ob sich ein Backup wirklich
  zurückspielen lässt. Ein regelmäßiger Restore in eine Wegwerf-VM bleibt Handarbeit.

### Die vier Zeilen, die zusammen eine Sicherung ergeben

1. **Backup lief** – Kachel *Letztes Backup*
2. **Backup ist lesbar** – Spalte *Verifikation* in der Snapshot-Tabelle
3. **Backup bleibt bezahlbar** – Kachel *Voll am*
4. **Backup liegt woanders** – ein `sync`-Task in der Task-Historie

Fällt eine dieser Zeilen aus, ist die Sicherung unvollständig – auch wenn die anderen
drei grün sind. Erscheint in der Task-Historie nie ein `sync`, existiert kein zweites
Ziel: Alle Backups liegen dann auf genau einer Maschine.
"""


# --------------------------------------------------------------------------
# Variablen und Gerüst
# --------------------------------------------------------------------------

def var_datasource(name, dtype, label):
    return {"name": name, "label": label, "type": "datasource",
            "query": dtype, "current": {}, "hide": 0, "refresh": 1,
            "regex": "", "options": []}


def var_constant(name, value, label):
    return {"name": name, "label": label, "type": "textbox",
            "query": value, "current": {"text": value, "value": value},
            "hide": 0, "options": []}


def var_query(name, label, query, multi=False, include_all=False, regex=""):
    return {
        "name": name, "label": label, "type": "query",
        "datasource": DS,
        "query": query.strip(),
        "definition": query.strip().splitlines()[-1],
        "refresh": 1, "sort": 1, "regex": regex,
        "multi": multi, "includeAll": include_all,
        "allValue": ".*" if include_all else None,
        "current": {}, "options": [], "hide": 0,
    }


def dashboard(uid, title, description, tags, panels, templating, links):
    return {
        "annotations": {"list": [{
            "builtIn": 1,
            "datasource": {"type": "grafana", "uid": "-- Grafana --"},
            "enable": True, "hide": True,
            "iconColor": "rgba(0, 211, 255, 1)",
            "name": "Annotations & Alerts", "type": "dashboard"}]},
        "description": description,
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 1,
        "links": links,
        "panels": panels,
        "refresh": "1m",
        "schemaVersion": 39,
        "tags": tags,
        "templating": {"list": templating},
        "time": {"from": "now-24h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": title,
        "uid": uid,
        "version": 1,
        "weekStart": "monday",
    }


def main():
    for name, build in (("proxmox-ve-dashboard.json", build_ve),
                        ("proxmox-pbs-dashboard.json", build_pbs)):
        _id[0] = 0
        data = build()
        with open(name, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        n = sum(1 for p in data["panels"] if p["type"] != "row")
        print(f"{name}: {n} Panels")


if __name__ == "__main__":
    main()
