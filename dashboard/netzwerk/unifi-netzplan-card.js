// ============================================================================
// UniFi-Netzplan – custom:unifi-netzplan-card
// ----------------------------------------------------------------------------
// Art:           ressource
// Bereich:       netzwerk
// Status:        aktiv
// Einfuegen:     nach /config/www/,
//                Ressource /local/unifi-netzplan-card.js (JavaScript-Modul)
// Platzhalter:   keine
// ============================================================================
/*
 * UniFi-Netzplan – custom:unifi-netzplan-card (Prototyp)
 *
 * Zeichnet die Topologie des UniFi-Netzes als Baum, live aus den Entitaeten
 * der offiziellen UniFi-Network-Integration. Fuer die Topologie braucht es
 * keine weitere Integration und keinen zweiten Controller-Zugang.
 *
 * Woher die Verbindungen kommen:
 *   - Geraet -> uebergeordnetes Geraet: Sensor "Uplink-MAC"
 *     (translation_key device_uplink_mac). Zeigt die MAC auf einen Access
 *     Point, ist die Anbindung Funk-Mesh (abgeleitet, gepunktete Linie).
 *   - WLAN-Client -> Access Point: Attribut ap_mac am device_tracker.
 *   - Kabel-Client -> Switch und Port: liefert die Integration NICHT. Mit
 *     `wired_entity` liest die Karte die Zuordnung aus einem Sensor, den
 *     unifi-kabel-clients-konfig.yaml aus der Controller-API fuellt. Ohne ihn (oder
 *     fuer dort fehlende Clients) landen Kabel-Clients im Sammelknoten,
 *     ausser sie sind per `pins` einem Geraet fest zugeordnet.
 *   - WAN-Leitungen: liefert die Integration nicht als Topologie, deshalb
 *     per `wan` konfiguriert. IP-Adressen und Erreichbarkeit je Leitung
 *     kommen optional aus einer zweiten Integration (z. B. "UniFi WAN" aus
 *     HACS), die Karte liest nur deren Entitaeten.
 *
 * Installation:
 *   1. Datei nach /config/www/unifi-netzplan-card.js kopieren.
 *   2. Einstellungen -> Dashboards -> Ressourcen -> Ressource hinzufuegen:
 *      URL /local/unifi-netzplan-card.js, Typ "JavaScript-Modul".
 *   3. Karte einfuegen, Beispiel: unifi-netzplan-karte.yaml
 *
 * Optionen (alle optional):
 *   title                 Kartentitel (Standard "Netzplan")
 *   wan                   Liste der Internetleitungen: name, detail, primary,
 *                         entity (Status: binary_sensor oder Messwert),
 *                         device (device_tracker des Modems),
 *                         internet_entity (binary_sensor Erreichbarkeit; wenn
 *                         gesetzt, bestimmt er den Status, entity liefert dann
 *                         nur noch den Messwert),
 *                         ip_entity / ip6_entity (Sensor mit der IPv4 / IPv6
 *                         der Leitung; Adressen aus 100.64.0.0/10 werden als
 *                         CGNAT markiert)
 *   inactive              device_tracker von Geraeten, die bewusst getrennt
 *                         sind: grau statt rot, zaehlen nicht als Stoerung.
 *                         Meldet sich das Geraet wieder, erscheint es normal.
 *   hide_inactive         true blendet diese Geraete ganz aus
 *   hide                  device_tracker, die nie angezeigt werden sollen
 *                         (Infrastruktur oder Clients). Geraete, die der
 *                         Controller nicht mehr meldet (Zustand mit
 *                         restored: true), blendet die Karte selbst aus.
 *   wired_entity          Sensor mit Attribut ports: { client_mac: [switch_mac,
 *                         port] }. Kabel-Clients erscheinen dann aufklappbar
 *                         am Switch, mit Portnummer.
 *   pins                  device_tracker eines Kabel-Clients -> device_tracker
 *                         des Switches/Gateways, an dem er haengt (geht vor
 *                         wired_entity)
 *   labels                device_tracker -> angezeigter Name
 *   show_offline_clients  true zeigt auch abwesende Clients (Standard false)
 *   expand                Liste von device_trackern, deren Clients beim Laden
 *                         aufgeklappt sind; "lan:<device_tracker>" fuer die
 *                         Kabel-Clients eines Geraets, "wired" fuer den
 *                         Sammelknoten, "wan" fuer alle Internetleitungen
 */

const UNP_VERSION = '0.5.1';
const MAC_RE = /^([0-9a-f]{2}:){5}[0-9a-f]{2}$/i;
// Shared Address Space nach RFC 6598, Adressen hinter Carrier-Grade-NAT
const CGNAT_RE = /^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\./;
const BAND = { ng: '2,4 GHz', na: '5 GHz', '6e': '6 GHz' };
const KIND_ORDER = { gateway: 0, switch: 1, ap: 2, other: 3 };
const ICON = {
  gateway: 'mdi:router-network',
  switch: 'mdi:switch',
  ap: 'mdi:access-point',
  other: 'mdi:lan',
  wired: 'mdi:ethernet',
  wlan: 'mdi:wifi',
  wan: 'mdi:web',
  cluster: 'mdi:lan-pending',
};

const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function classify(model) {
  const m = String(model || '').toUpperCase();
  if (/^(UDM|UDR|UCG|UXG|UGW|UX7?$|EFG|UDW)/.test(m)) return 'gateway';
  if (/^(US|USW|USL|USP|USM|USF|USXG|ECS)/.test(m)) return 'switch';
  if (/^(UAP|U6|U7|UK|E7|UWB|UBB|UDB|UMBB)/.test(m)) return 'ap';
  return 'other';
}

class UnifiNetzplanCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._expanded = new Set();
    this._last = '';
    this._uniCache = { src: null, list: [] };
    this.shadowRoot.addEventListener('click', (ev) => this._onClick(ev));
    this.shadowRoot.addEventListener('keydown', (ev) => {
      if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.closest('[data-more],[data-toggle]')) {
        ev.preventDefault();
        this._onClick(ev);
      }
    });
  }

  setConfig(config) {
    if (!config) throw new Error('Keine Konfiguration');
    if (config.wan !== undefined && !Array.isArray(config.wan)) throw new Error('wan muss eine Liste sein');
    for (const key of ['inactive', 'hide', 'expand']) {
      if (config[key] !== undefined && !Array.isArray(config[key])) throw new Error(`${key} muss eine Liste sein`);
    }
    for (const key of ['pins', 'labels']) {
      if (config[key] !== undefined && (typeof config[key] !== 'object' || Array.isArray(config[key]))) {
        throw new Error(`${key} muss eine Zuordnung (Schluessel: Wert) sein`);
      }
    }
    this._config = { title: 'Netzplan', ...config };
    this._expanded = new Set(config.expand || []);
    if (this._expanded.has('wan')) (config.wan || []).forEach((_, i) => this._expanded.add(`wan:${i}`));
    if (config.wired_entity !== undefined && typeof config.wired_entity !== 'string') throw new Error('wired_entity muss eine Entitaet sein');
    this._last = '';
    if (this._hass) this._update();
  }

  set hass(hass) {
    this._hass = hass;
    this._update();
  }

  getCardSize() {
    return 9;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6, rows: 'auto' };
  }

  static getStubConfig() {
    return { title: 'Netzplan' };
  }

  // ------------------------------------------------------------ Datenmodell

  _unifiEntities() {
    const all = this._hass.entities;
    if (!all) return [];
    // hass.entities wird nur bei Registeraenderungen neu erzeugt.
    if (this._uniCache.src !== all) {
      this._uniCache = { src: all, list: Object.values(all).filter((e) => e.platform === 'unifi') };
    }
    return this._uniCache.list;
  }

  _model() {
    const hass = this._hass;
    const cfg = this._config;
    const st = hass.states;
    const devices = hass.devices || {};
    const labels = cfg.labels || {};
    const inactive = new Set(cfg.inactive || []);
    const hide = new Set(cfg.hide || []);
    const uni = this._unifiEntities();

    const byDev = new Map();
    for (const e of uni) {
      if (!e.device_id) continue;
      if (!byDev.has(e.device_id)) byDev.set(e.device_id, []);
      byDev.get(e.device_id).push(e);
    }
    const pick = (list, tk, fallback) => list.find((e) => e.translation_key === tk) || list.find(fallback);
    const num = (id) => {
      const s = id && st[id];
      const v = s ? parseFloat(s.state) : NaN;
      return Number.isFinite(v) ? v : null;
    };

    // 1. Infrastruktur: Geraete mit Uplink- oder Zustandssensor
    const nodes = new Map(); // mac -> node
    const infraDevs = new Set();
    for (const [devId, list] of byDev) {
      const up = pick(list, 'device_uplink_mac', (e) => e.entity_id.startsWith('sensor.') && e.entity_id.endsWith('_uplink_mac'));
      const stateS = pick(list, 'device_state', () => false);
      if (!up && !stateS) continue;
      const dev = devices[devId] || {};
      const conn = (dev.connections || []).find((c) => c[0] === 'mac');
      const connMac = conn ? String(conn[1]).toLowerCase() : '';
      // An einem Geraet koennen neben dem echten Tracker verwaiste Client-Tracker
      // haengen (restored: true). Den lebenden mit passender MAC bevorzugen.
      const trackers = list.filter((e) => e.entity_id.startsWith('device_tracker.'));
      const live = (e) => st[e.entity_id] && !st[e.entity_id].attributes.restored;
      const tracker = trackers.find((e) => live(e) && String(st[e.entity_id].attributes.mac || '').toLowerCase() === connMac)
        || trackers.find(live) || trackers[0];
      const tState = tracker && st[tracker.entity_id];
      const mac = String((tState && tState.attributes.mac) || connMac).toLowerCase();
      if (!MAC_RE.test(mac)) continue;
      infraDevs.add(devId);
      const id = tracker ? tracker.entity_id : (stateS || up).entity_id;
      // restored: HA haelt die Entitaet nur noch aus dem Register vor, der
      // Controller kennt das Geraet nicht mehr (z. B. ausgemusterte Hardware).
      // Massgeblich ist der Zustandssensor des Geraets, nicht ein einzelner Tracker.
      const probe = (stateS && st[stateS.entity_id]) || tState;
      if (hide.has(id) || (probe && probe.attributes.restored)) continue;

      const upState = up && st[up.entity_id];
      const uplink = upState && MAC_RE.test(upState.state) ? upState.state.toLowerCase() : null;
      const raw = stateS && st[stateS.entity_id] ? st[stateS.entity_id].state : null;
      let status;
      // inactive gilt nur, solange das Geraet wirklich getrennt ist
      if (raw === 'connected') status = 'ok';
      else if (inactive.has(id)) status = 'off';
      else if (raw === 'disconnected' || raw === 'unavailable') status = 'bad';
      else if (raw && raw !== 'unknown') status = 'warn';
      else status = tState && tState.state === 'home' ? 'ok' : 'bad';

      const clientsS = pick(list, 'device_clients', (e) => e.entity_id.startsWith('sensor.') && e.entity_id.endsWith('_clients'));
      if (status === 'off' && cfg.hide_inactive) continue;
      nodes.set(mac, {
        id,
        mac,
        name: labels[id] || dev.name_by_user || dev.name || (tState && tState.attributes.friendly_name) || id,
        model: dev.model || '',
        kind: classify(dev.model),
        ip: tState ? tState.attributes.ip : null,
        state: raw || (tState && tState.state) || 'unbekannt',
        status,
        hasUplinkSensor: !!up,
        uplink,
        clientsSensor: clientsS ? num(clientsS.entity_id) : null,
        children: [],
        wlan: [],
        lan: [],
        pinned: [],
      });
    }

    // 2. Baum aus den Uplink-MACs
    const roots = [];
    for (const n of nodes.values()) {
      const parent = n.uplink && nodes.get(n.uplink);
      if (parent && parent !== n) {
        n.mesh = parent.kind === 'ap';
        parent.children.push(n);
      } else if (!n.hasUplinkSensor) {
        n.kind = n.kind === 'other' ? 'gateway' : n.kind;
        roots.push(n);
      } else {
        n.orphan = true; // Uplink zeigt auf ein Geraet, das HA nicht kennt
      }
    }
    if (!roots.length) {
      const first = [...nodes.values()].find((n) => n.orphan) || [...nodes.values()][0];
      if (first) { first.orphan = false; roots.push(first); }
    }
    for (const n of nodes.values()) if (n.orphan) roots[0].children.push(n);

    // Zyklen abfangen: nur Knoten, die von einer Wurzel erreichbar sind
    const seen = new Set();
    const walk = (n, depth) => {
      if (seen.has(n) || depth > 12) return false;
      seen.add(n);
      n.children = n.children.filter((c) => walk(c, depth + 1));
      return true;
    };
    roots.forEach((r) => walk(r, 0));

    // 3. Clients
    const byTracker = new Map([...nodes.values()].map((n) => [n.id, n]));
    const wanDevs = new Set((cfg.wan || []).map((w) => w.device).filter(Boolean));
    const pins = cfg.pins || {};
    const wiredS = cfg.wired_entity && st[cfg.wired_entity];
    const ports = (wiredS && wiredS.attributes.ports) || {};
    const wired = [];
    let wlanCount = 0;
    let lanCount = 0;
    for (const e of uni) {
      if (!e.entity_id.startsWith('device_tracker.')) continue;
      if (e.device_id && infraDevs.has(e.device_id)) continue;
      if (wanDevs.has(e.entity_id) || hide.has(e.entity_id)) continue;
      const s = st[e.entity_id];
      if (!s) continue;
      const online = s.state === 'home';
      if (!online && !cfg.show_offline_clients) continue;
      const a = s.attributes;
      const ap = a.ap_mac ? String(a.ap_mac).toLowerCase() : null;
      const port = !ap && Array.isArray(ports[String(a.mac || '').toLowerCase()]) ? ports[String(a.mac).toLowerCase()] : null;
      // friendly_name ist bei Clients oft "Geraet Geraet", daher Geraetename zuerst
      const dev = (e.device_id && devices[e.device_id]) || {};
      const c = {
        id: e.entity_id,
        name: labels[e.entity_id] || e.name || dev.name_by_user || dev.name || a.friendly_name || e.entity_id,
        ip: a.ip || '',
        band: BAND[a.radio] || '',
        wlan: !!ap,
        mac: String(a.mac || '').toLowerCase(),
        sw: port ? String(port[0]).toLowerCase() : null,
        port: port && port[1] != null ? port[1] : null,
        online,
      };
      if (ap) wlanCount++; else lanCount++;
      const pinTarget = pins[e.entity_id] && byTracker.get(pins[e.entity_id]);
      const swNode = port && nodes.get(String(port[0]).toLowerCase());
      if (pinTarget) pinTarget.pinned.push(c);
      else if (ap && nodes.get(ap)) nodes.get(ap).wlan.push(c);
      else if (swNode) swNode.lan.push(c);
      else wired.push(c);
    }

    // Haengt ein Kabel-Client an einem anderen Client statt an einem Switch
    // (z. B. ein Access-Leser am Access-Hub), kommt er zum Switch dieses Clients.
    const lanOf = new Map();
    for (const n of nodes.values()) for (const c of n.lan) lanOf.set(c.mac, [n, c]);
    for (let i = wired.length - 1; i >= 0; i--) {
      const hit = wired[i].sw && lanOf.get(wired[i].sw);
      if (!hit) continue;
      Object.assign(wired[i], { via: hit[1].name, port: hit[1].port });
      hit[0].lan.push(wired[i]);
      wired.splice(i, 1);
    }

    const byName = (a, b) => a.name.localeCompare(b.name, 'de');
    const sortTree = (n) => {
      n.children.sort((a, b) => (KIND_ORDER[a.kind] - KIND_ORDER[b.kind]) || (a.status === 'off') - (b.status === 'off') || byName(a, b));
      n.wlan.sort(byName);
      n.lan.sort((a, b) => (a.port ?? 999) - (b.port ?? 999) || byName(a, b));
      n.pinned.sort(byName);
      n.children.forEach(sortTree);
    };
    roots.forEach(sortTree);
    wired.sort(byName);

    const infra = [...nodes.values()];
    const wan = this._wanModel();
    return {
      roots,
      wired,
      wiredMapped: !!wiredS,
      wlanCount,
      lanCount,
      total: infra.length,
      ok: infra.filter((n) => n.status === 'ok').length,
      off: infra.filter((n) => n.status === 'off').length,
      bad: infra.filter((n) => n.status === 'bad' || n.status === 'warn').length,
      wanBad: wan.filter((w) => w.status === 'bad').length,
      wan,
    };
  }

  _wanModel() {
    const st = this._hass.states;
    const known = (id) => {
      const s = id && st[id];
      return s && !['unknown', 'unavailable', ''].includes(s.state) ? s.state : '';
    };
    return (this._config.wan || []).map((w, i) => {
      const s = w.entity && st[w.entity];
      let status = 'none';
      let value = '';
      if (s) {
        const v = parseFloat(s.state);
        if (s.state === 'on') status = 'ok';
        else if (s.state === 'off' || s.state === 'unavailable') status = 'bad';
        else if (Number.isFinite(v)) {
          status = 'ok';
          value = `${s.state.replace('.', ',')} ${s.attributes.unit_of_measurement || ''}`.trim();
        } else status = 'warn';
      }
      const net = w.internet_entity && st[w.internet_entity];
      if (net) status = net.state === 'on' ? 'ok' : net.state === 'off' || net.state === 'unavailable' ? 'bad' : 'warn';
      const ip = known(w.ip_entity);
      const d = w.device && st[w.device];
      return {
        key: `wan:${i}`,
        name: w.name || 'WAN',
        detail: w.detail || '',
        primary: !!w.primary,
        status,
        value,
        ip,
        cgnat: CGNAT_RE.test(ip),
        ip6: known(w.ip6_entity),
        moreDetail: w.entity || w.internet_entity || null,
        moreIp: w.ip_entity || null,
        moreIp6: w.ip6_entity || null,
        modem: d ? { id: w.device, name: (this._config.labels || {})[w.device] || d.attributes.friendly_name, ok: d.state === 'home' } : null,
      };
    });
  }

  // ---------------------------------------------------------------- Ausgabe

  _update() {
    if (!this._config || !this._hass) return;
    let model;
    try {
      model = this._model();
    } catch (err) {
      this._renderError(err);
      return;
    }
    // Der Klappzustand gehoert nicht in die Signatur: _toggle aendert das DOM
    // direkt, ein Neuaufbau uebernimmt den Zustand aus _expanded.
    const sig = JSON.stringify(model);
    if (sig === this._last) return;
    this._last = sig;
    this._render(model);
  }

  _renderError(err) {
    this.shadowRoot.innerHTML = `<ha-card><div style="padding:16px">UniFi-Netzplan: ${esc(err.message)}</div></ha-card>`;
  }

  // Ein <ul> mit Linien. items: { html(last), hidden }. "last" markiert den
  // letzten sichtbaren Eintrag, damit die senkrechte Linie dort endet.
  _list(items) {
    if (!items.length) return '';
    let lastIdx = -1;
    items.forEach((it, i) => { if (!it.hidden) lastIdx = i; });
    return `<ul>${items.map((it, i) => it.html(i === lastIdx)).join('')}</ul>`;
  }

  _node(n, extra = [], last = false) {
    const open = this._expanded.has(n.id);
    const lanKey = `lan:${n.id}`;
    const lanOpen = this._expanded.has(lanKey);
    const tag = n.status === 'off' ? '<span class="tag">inaktiv</span>' : n.mesh ? '<span class="tag mesh">Mesh</span>' : '';
    const pills = [];
    if (n.lan.length) {
      pills.push(`<span class="pill" role="button" tabindex="0" data-toggle="${esc(lanKey)}" aria-expanded="${lanOpen}" title="Kabel-Clients ein-/ausklappen"><ha-icon icon="${ICON.wired}"></ha-icon>${n.lan.length}<span class="chev">${lanOpen ? '▴' : '▾'}</span></span>`);
    } else if (n.kind !== 'ap' && !n.wlan.length && n.clientsSensor != null && n.status !== 'off') {
      pills.push(`<span class="pill quiet" title="Kabel-Clients direkt an diesem Geraet (Sensor Clients)"><ha-icon icon="${ICON.wired}"></ha-icon>${n.clientsSensor}</span>`);
    }
    if (n.kind === 'ap' || n.wlan.length) {
      const gap = n.clientsSensor != null && n.clientsSensor > n.wlan.length + n.lan.length ? `<span class="gap">+${n.clientsSensor - n.wlan.length - n.lan.length}</span>` : '';
      pills.push(n.wlan.length
        ? `<span class="pill" role="button" tabindex="0" data-toggle="${esc(n.id)}" aria-expanded="${open}" title="WLAN-Clients ein-/ausklappen"><ha-icon icon="${ICON.wlan}"></ha-icon>${n.wlan.length}${gap}<span class="chev">${open ? '▴' : '▾'}</span></span>`
        : `<span class="pill quiet"><ha-icon icon="${ICON.wlan}"></ha-icon>0${gap}</span>`);
    }
    // Beim Gateway ist ip die Adresse der Ausfall-Hauptleitung (Uplink), nicht zwingend die,
    // ueber die der Verkehr laeuft. WAN-Adressen gehoeren deshalb an die Leitungen (ip_entity).
    const meta = [n.model, n.kind === 'gateway' ? '' : n.ip].filter(Boolean).join(' · ');
    const body = `
      <div class="node k-${n.kind} s-${n.status}" data-more="${esc(n.id)}" role="button" tabindex="0" title="${esc(n.state)}">
        <span class="ico"><ha-icon icon="${ICON[n.kind]}"></ha-icon></span>
        <span class="txt"><span class="nm"><span class="nt">${esc(n.name)}</span>${tag}</span><span class="mt">${esc(meta)}</span></span>
        ${pills.join('')}<span class="dot"></span>
      </div>`;
    // Clients stehen immer im DOM und werden nur ein-/ausgeblendet:
    // Aufklappen baut die Karte nicht neu auf (kein Fokus- oder Scrollverlust).
    // Clients zuerst: Aufgeklappte erscheinen direkt unter dem angetippten
    // Geraet, nicht erst unter dessen ganzem Teilbaum.
    const sub = this._list([
      ...n.lan.map((c) => ({ html: (l) => this._leaf(c, 'lan', l, !lanOpen), hidden: !lanOpen })),
      ...n.wlan.map((c) => ({ html: (l) => this._leaf(c, 'wlan', l, !open), hidden: !open })),
      ...n.pinned.map((c) => ({ html: (l) => this._leaf(c, 'pin', l) })),
      ...n.children.map((c) => ({ html: (l) => this._node(c, [], l) })),
      ...extra.map((html) => ({ html })),
    ]);
    const cls = [n.mesh ? 'mesh' : '', n.status === 'off' ? 'off' : '', last ? 'last' : ''].join(' ');
    return `<li class="${cls}">${body}${sub}</li>`;
  }

  _leaf(c, how, last = false, hidden = false) {
    const meta = [c.port != null ? `Port ${c.port}` : '', c.via ? `über ${c.via}` : '', c.ip, c.band, how === 'pin' ? 'fest zugeordnet' : ''].filter(Boolean).join(' · ');
    // wl/wd: Gruppe, die ein Klapp-Knopf ein- und ausblendet (WLAN bzw. Kabel)
    const cls = ['leaf', how === 'wlan' ? 'air wl' : '', how === 'lan' ? 'wd' : '', last ? 'last' : ''].join(' ');
    return `<li class="${cls}"${hidden ? ' hidden' : ''}>
      <div class="client ${c.online ? '' : 'away'}" data-more="${esc(c.id)}" role="button" tabindex="0">
        <ha-icon icon="${c.wlan ? ICON.wlan : ICON.wired}"></ha-icon>
        <span class="txt"><span class="nm">${esc(c.name)}</span><span class="mt">${esc(meta)}</span></span>
      </div></li>`;
  }

  _wiredNode(list, mapped, last = false) {
    if (!list.length) return '';
    const open = this._expanded.has('wired');
    const rows = this._list(list.map((c) => ({ html: (l) => this._leaf(c, 'lan', l, !open), hidden: !open })));
    return `<li class="unknown ${last ? 'last' : ''}">
      <div class="node k-cluster s-none">
        <span class="ico"><ha-icon icon="${ICON.cluster}"></ha-icon></span>
        <span class="txt"><span class="nm"><span class="nt">${mapped ? 'Kabel-Clients ohne Switch' : 'Kabel-Clients'}</span></span><span class="mt">${mapped ? 'Nicht in der Zuordnung der Controller-API' : 'Switch und Port liefert die Integration nicht'}</span></span>
        <span class="pill" role="button" tabindex="0" data-toggle="wired" aria-expanded="${open}"><ha-icon icon="${ICON.wired}"></ha-icon>${list.length}<span class="chev">${open ? '▴' : '▾'}</span></span>
      </div>${rows}</li>`;
  }

  // Kompakt: Name, Rolle, Messwert, Status. Aufgeklappt: Details, Adressen,
  // Modem; jede Zeile oeffnet den Mehr-Info-Dialog ihrer Entitaet.
  _wanRow(wan) {
    if (!wan.length) return '';
    const line = (html, ent, cls = '') => (html
      ? `<span class="mt ${cls}"${ent ? ` data-more="${esc(ent)}" role="button" tabindex="0"` : ''}>${html}</span>`
      : '');
    const chips = wan.map((w) => {
      const open = this._expanded.has(w.key);
      const cg = w.cgnat ? ' <span class="cg" title="Carrier-Grade-NAT: geteilte Adresse des Anbieters, nicht die öffentliche IPv4">CGNAT</span>' : '';
      const body = [
        line(esc(w.detail), w.moreDetail),
        line(w.ip ? esc(w.ip) + cg : '', w.moreIp, 'ip'),
        line(esc(w.ip6), w.moreIp6, 'ip ip6'),
        w.modem ? line(`Modem ${esc(w.modem.name)}: ${w.modem.ok ? 'erreichbar' : 'nicht erreichbar'}`, w.modem.id) : '',
      ].join('');
      const act = body
        ? `data-toggle="${w.key}" aria-expanded="${open}" title="Details ein-/ausklappen"`
        : (w.moreDetail ? `data-more="${esc(w.moreDetail)}"` : '');
      return `<div class="wan ${w.primary ? 'primary' : 'standby'} s-${w.status}">
        <div class="wan-head" ${act} ${act ? 'role="button" tabindex="0"' : ''}>
          <ha-icon class="wico" icon="${ICON.wan}"></ha-icon>
          <span class="nm"><span class="nt">${esc(w.name)}</span><span class="tag">${w.primary ? 'aktiv' : 'Backup'}</span></span>
          ${w.value ? `<span class="val">${esc(w.value)}</span>` : ''}
          ${w.status !== 'none' ? '<span class="dot"></span>' : ''}
          ${body ? `<span class="chev">${open ? '▴' : '▾'}</span>` : ''}
        </div>
        ${body ? `<div class="wan-body"${open ? '' : ' hidden'}>${body}</div>` : ''}
      </div>`;
    });
    return `<div class="wanrow">${chips.join('')}</div>`;
  }

  _render(m) {
    const faults = m.bad + m.wanBad;
    const health = faults
      ? `<span class="badge bad">${faults} gestört</span>`
      : `<span class="badge ok">${m.ok}/${m.total - m.off} online</span>`;
    const tree = m.roots.length
      ? m.roots.map((r, i) => this._node(r, i === 0 && m.wired.length ? [(l) => this._wiredNode(m.wired, m.wiredMapped, l)] : [])).join('')
      : '<li class="empty">Keine Geräte der UniFi-Integration gefunden.</li>';

    this.shadowRoot.innerHTML = `
      <style>${UnifiNetzplanCard.styles}</style>
      <ha-card>
        <div class="head">
          <span class="hico"><ha-icon icon="mdi:sitemap-outline"></ha-icon></span>
          <span class="txt"><span class="title">${esc(this._config.title)}</span>
            <span class="mt">${m.total} Geräte${m.off ? ` · ${m.off} inaktiv` : ''} · ${m.wlanCount} WLAN · ${m.lanCount} LAN</span></span>
          ${health}
        </div>
        ${this._wanRow(m.wan)}
        <ul class="tree ${m.wan.length ? 'fed' : ''}">${tree}</ul>
        <div class="legend">
          <span><i class="ln"></i>Uplink laut Sensor</span>
          <span><i class="ln ln-dotted"></i>Funk-Mesh</span>
          <span><i class="ln ln-dashed"></i>Zuordnung unbekannt</span>
        </div>
      </ha-card>`;
  }

  // Auf- und Zuklappen nur per Attribut, ohne Neuaufbau: der angetippte
  // Knoten bleibt im DOM, Fokus und Scrollposition bleiben erhalten.
  _toggle(t) {
    const id = t.dataset.toggle;
    const open = !this._expanded.has(id);
    if (open) this._expanded.add(id);
    else this._expanded.delete(id);
    t.setAttribute('aria-expanded', String(open));
    const chev = t.querySelector('.chev');
    if (chev) chev.textContent = open ? '▴' : '▾';
    if (id.startsWith('wan:')) {
      const body = t.closest('.wan').querySelector('.wan-body');
      if (body) body.hidden = !open;
      return;
    }
    const li = t.closest('li');
    const ul = li && li.querySelector(':scope > ul');
    if (!ul) return;
    const group = id === 'wired' || id.startsWith('lan:') ? 'wd' : 'wl';
    for (const c of ul.querySelectorAll(`:scope > li.${group}`)) c.hidden = !open;
    const vis = [...ul.children].filter((c) => !c.hidden);
    for (const c of ul.children) c.classList.toggle('last', c === vis[vis.length - 1]);
  }

  _onClick(ev) {
    const t = ev.target.closest('[data-toggle]');
    if (t) {
      ev.stopPropagation();
      this._toggle(t);
      return;
    }
    const m = ev.target.closest('[data-more]');
    if (m) {
      ev.stopPropagation();
      this.dispatchEvent(new CustomEvent('hass-more-info', { detail: { entityId: m.dataset.more }, bubbles: true, composed: true }));
    }
  }
}

UnifiNetzplanCard.styles = `
  :host {
    --unp-bg: linear-gradient(180deg, #1b2231 0%, #171d29 55%);
    --unp-fg: #f2f5f8; --unp-muted: #8794a5; --unp-line: rgba(255,255,255,0.10);
    --unp-tile: rgba(255,255,255,0.028); --unp-tile-line: rgba(255,255,255,0.06);
    --unp-ok: #a6d49e; --unp-warn: #e6b566; --unp-bad: #f0736a; --unp-info: #7fb3d5;
    --unp-edge: rgba(255,255,255,0.18);
    --unp-ico: 34px; --unp-pad: 6px; --unp-indent: 18px;
    container-type: inline-size; display: block;
  }
  @container (max-width: 460px) {
    ha-card { --unp-ico: 26px; --unp-pad: 3px; --unp-indent: 10px; padding-inline: 12px; }
    .node .mt { display: none; }
    /* Status steckt schon in der Farbe des Geraetesymbols; der Punkt kostet Platz */
    .node .dot { display: none; }
  }
  ha-card {
    display: block;
    background: var(--unp-bg); color: var(--unp-fg);
    border: 1px solid rgba(255,255,255,0.05); border-radius: 22px;
    box-shadow: 0 18px 44px -22px rgba(0,0,0,0.7);
    padding: 16px 18px 12px; overflow: hidden;
  }
  ha-icon { --mdc-icon-size: 20px; display: inline-flex; }
  [hidden] { display: none !important; }
  .txt { display: flex; flex-direction: column; min-width: 0; flex: 1; }
  .nm { font-size: 14px; font-weight: 700; letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 6px; min-width: 0; }
  /* Der Name kuerzt sich, die Markierung (Mesh, inaktiv, aktiv) bleibt ganz */
  .nt { overflow: hidden; text-overflow: ellipsis; min-width: 0; }
  .mt { font-size: 11.5px; color: var(--unp-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .head { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
  .head .mt { white-space: normal; }
  .hico { width: 44px; height: 44px; border-radius: 13px; display: grid; place-items: center; flex: none;
    background: rgba(166,212,158,0.12); border: 1px solid rgba(166,212,158,0.24); color: var(--unp-ok); }
  .title { font-size: 17px; font-weight: 700; letter-spacing: -0.02em; }
  .badge { font-size: 12.5px; font-weight: 700; padding: 6px 12px; border-radius: 12px; white-space: nowrap; }
  .badge.ok { color: var(--unp-ok); background: #a6d49e1f; border: 1px solid #a6d49e3d; }
  .badge.bad { color: var(--unp-bad); background: #f0736a1f; border: 1px solid #f0736a3d; }

  .wanrow { display: flex; flex-wrap: wrap; gap: 8px; }
  .wan { display: flex; flex-direction: column; padding: 7px 12px; border-radius: 14px;
    background: var(--unp-tile); border: 1px solid var(--unp-tile-line); flex: 1 1 210px; min-width: 0; }
  .wan.primary { border-color: #a6d49e3d; }
  .wan.standby { border-style: dashed; }
  .wan-head { display: flex; align-items: center; gap: 9px; min-height: 26px; cursor: pointer; }
  .wan-head .nm { flex: 1; }
  .wico { --mdc-icon-size: 18px; color: var(--unp-info); flex: none; }
  .wan .val { font-size: 12px; color: var(--unp-muted); white-space: nowrap; font-variant-numeric: tabular-nums; }
  .wan .chev { font-size: 10px; color: var(--unp-muted); }
  .wan-body { display: flex; flex-direction: column; gap: 1px; padding: 3px 0 2px 27px; }
  .wan-body [data-more] { cursor: pointer; }
  .wan-body [data-more]:hover { color: var(--unp-fg); }
  .wan .ip { font-variant-numeric: tabular-nums; }
  .wan .ip6 { white-space: normal; overflow-wrap: anywhere; }
  .wan .cg { font-size: 10px; font-weight: 700; color: var(--unp-warn); }

  ul { list-style: none; margin: 0; padding: 0; }
  .tree { margin-top: 6px; }
  .tree li { position: relative; padding: 4px 0 0 var(--unp-indent); }
  .tree > li { padding-left: 0; }
  .tree.fed > li { padding-top: 14px; }
  .tree.fed > li::before { content: ''; position: absolute; left: calc(var(--unp-pad) + var(--unp-ico) / 2 - 1px); top: 0; height: 14px; border-left: 2px solid var(--unp-edge); }
  .tree ul { margin-left: calc(var(--unp-pad) + var(--unp-ico) / 2 - 1px); }
  .tree ul > li::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; border-left: 2px solid var(--unp-edge); }
  .tree ul > li.last::before { bottom: auto; height: 27px; }
  .tree ul > li::after { content: ''; position: absolute; left: 0; top: 27px; width: calc(var(--unp-indent) - 2px); border-top: 2px solid var(--unp-edge); }
  .tree ul > li.leaf::after { top: 24px; }
  .tree ul > li.leaf.last::before { height: 24px; }
  .tree li.mesh::after, .tree li.mesh::before, .tree li.air::after { border-style: dotted; }
  .tree li.unknown::after, .tree li.off::after { border-top-style: dashed; }

  .node { display: flex; align-items: center; gap: 9px; padding: 6px 9px 6px var(--unp-pad); border-radius: 14px; cursor: pointer;
    background: var(--unp-tile); border: 1px solid var(--unp-tile-line); min-height: 34px; }
  .node:hover, .wan:hover, .client:hover { border-color: rgba(255,255,255,0.16); }
  .node .ico { width: var(--unp-ico); height: var(--unp-ico); border-radius: 10px; display: grid; place-items: center; flex: none; }
  .s-ok .ico { color: var(--unp-ok); background: #a6d49e1f; border: 1px solid #a6d49e3d; }
  .s-warn .ico { color: var(--unp-warn); background: #e6b5661f; border: 1px solid #e6b5663d; }
  .s-bad .ico { color: var(--unp-bad); background: #f0736a1f; border: 1px solid #f0736a3d; }
  .s-off .ico, .s-none .ico { color: var(--unp-muted); background: rgba(255,255,255,0.04); border: 1px dashed var(--unp-line); }
  .s-off { opacity: 0.65; border-style: dashed; }
  .k-cluster { border-style: dashed; }
  .dot { width: 9px; height: 9px; border-radius: 50%; flex: none; background: var(--unp-muted); }
  .s-ok .dot { background: var(--unp-ok); box-shadow: 0 0 0 3px #a6d49e2e; }
  .s-warn .dot { background: var(--unp-warn); box-shadow: 0 0 0 3px #e6b5662e; }
  .s-bad .dot { background: var(--unp-bad); box-shadow: 0 0 0 3px #f0736a2e; }
  .s-off .dot { background: transparent; border: 1.5px solid var(--unp-muted); }
  .tag { flex: none; font-size: 10.5px; font-weight: 700; padding: 1px 6px; border-radius: 6px; color: var(--unp-muted); border: 1px solid var(--unp-line); }
  .tag.mesh { color: var(--unp-warn); border-color: #e6b5663d; }
  .wan.primary .tag { color: var(--unp-ok); border-color: #a6d49e3d; }

  .pill { display: inline-flex; align-items: center; gap: 4px; font-size: 12.5px; font-weight: 700; padding: 4px 9px; border-radius: 10px;
    color: var(--unp-ok); background: #a6d49e1f; border: 1px solid #a6d49e3d; cursor: pointer; white-space: nowrap; font-variant-numeric: tabular-nums; }
  .pill ha-icon { --mdc-icon-size: 15px; }
  .pill + .pill { margin-left: -3px; }
  .pill.quiet { color: var(--unp-muted); background: transparent; border-color: var(--unp-line); cursor: default; }
  .pill .gap { color: var(--unp-warn); font-weight: 600; margin-left: 2px; }
  .pill .chev { font-size: 10px; margin-left: 2px; }

  .client { display: flex; align-items: center; gap: 9px; padding: 4px 8px; border-radius: 10px; cursor: pointer; border: 1px solid transparent; }
  .client ha-icon { --mdc-icon-size: 16px; color: var(--unp-muted); }
  .client .nm { font-size: 13px; font-weight: 600; }
  .client.away { opacity: 0.5; }

  .legend { display: flex; flex-wrap: wrap; gap: 6px 16px; margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--unp-line); font-size: 11.5px; color: var(--unp-muted); }
  .legend span { display: inline-flex; align-items: center; gap: 7px; }
  .ln { width: 22px; border-top: 2px solid var(--unp-edge); display: inline-block; }
  .ln-dotted { border-top-style: dotted; } .ln-dashed { border-top-style: dashed; }
  [role="button"]:focus-visible { outline: 2px solid var(--unp-info); outline-offset: 2px; }
  .empty { color: var(--unp-muted); padding: 8px 0; }
`;

if (!customElements.get('unifi-netzplan-card')) {
  customElements.define('unifi-netzplan-card', UnifiNetzplanCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: 'unifi-netzplan-card',
    name: 'UniFi-Netzplan',
    description: 'Topologie des UniFi-Netzes aus der UniFi-Network-Integration',
  });
  console.info(`%c UNIFI-NETZPLAN-CARD %c ${UNP_VERSION} `, 'background:#a6d49e;color:#171d29;font-weight:700', 'color:#a6d49e');
}
