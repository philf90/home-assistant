/*
 * UniFi-Netzplan – custom:unifi-netzplan-card (Prototyp)
 *
 * Zeichnet die Topologie des UniFi-Netzes als Baum, live aus den Entitaeten
 * der offiziellen UniFi-Network-Integration. Keine weitere Integration, kein
 * zweiter Controller-Zugang.
 *
 * Woher die Verbindungen kommen:
 *   - Geraet -> uebergeordnetes Geraet: Sensor "Uplink-MAC"
 *     (translation_key device_uplink_mac). Zeigt die MAC auf einen Access
 *     Point, ist die Anbindung Funk-Mesh (abgeleitet, gepunktete Linie).
 *   - WLAN-Client -> Access Point: Attribut ap_mac am device_tracker.
 *   - Kabel-Client -> Switch: liefert die Integration NICHT. Diese Clients
 *     landen im Sammelknoten "Port unbekannt", ausser sie sind per `pins`
 *     einem Geraet fest zugeordnet.
 *   - WAN-Leitungen: liefert die Integration nicht als Topologie, deshalb
 *     per `wan` konfiguriert.
 *
 * Installation:
 *   1. Datei nach /config/www/unifi-netzplan-card.js kopieren.
 *   2. Einstellungen -> Dashboards -> Ressourcen -> Ressource hinzufuegen:
 *      URL /local/unifi-netzplan-card.js, Typ "JavaScript-Modul".
 *   3. Karte einfuegen, Beispiel: unifi-netzplan-card.yaml
 *
 * Optionen (alle optional):
 *   title                 Kartentitel (Standard "Netzplan")
 *   wan                   Liste der Internetleitungen: name, detail, primary,
 *                         entity (Status: binary_sensor oder Messwert),
 *                         device (device_tracker des Modems)
 *   inactive              device_tracker von Geraeten, die bewusst getrennt
 *                         sind: grau statt rot, zaehlen nicht als Stoerung.
 *                         Meldet sich das Geraet wieder, erscheint es normal.
 *   hide_inactive         true blendet diese Geraete ganz aus
 *   hide                  device_tracker, die nie angezeigt werden sollen
 *                         (Infrastruktur oder Clients). Geraete, die der
 *                         Controller nicht mehr meldet (Zustand mit
 *                         restored: true), blendet die Karte selbst aus.
 *   pins                  device_tracker eines Kabel-Clients -> device_tracker
 *                         des Switches/Gateways, an dem er haengt
 *   labels                device_tracker -> angezeigter Name
 *   show_offline_clients  true zeigt auch abwesende Clients (Standard false)
 *   expand                Liste von device_trackern, deren Clients beim Laden
 *                         aufgeklappt sind; "wired" fuer den Sammelknoten
 */

const UNP_VERSION = '0.2.0';
const MAC_RE = /^([0-9a-f]{2}:){5}[0-9a-f]{2}$/i;
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
      const tracker = list.find((e) => e.entity_id.startsWith('device_tracker.'));
      const dev = devices[devId] || {};
      const tState = tracker && st[tracker.entity_id];
      const conn = (dev.connections || []).find((c) => c[0] === 'mac');
      const mac = String((tState && tState.attributes.mac) || (conn && conn[1]) || '').toLowerCase();
      if (!MAC_RE.test(mac)) continue;
      infraDevs.add(devId);
      const id = tracker ? tracker.entity_id : (stateS || up).entity_id;
      // restored: HA haelt die Entitaet nur noch aus dem Register vor, der
      // Controller kennt das Geraet nicht mehr (z. B. ausgemusterte Hardware).
      const probe = tState || (stateS && st[stateS.entity_id]);
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
      // friendly_name ist bei Clients oft "Geraet Geraet", daher Geraetename zuerst
      const dev = (e.device_id && devices[e.device_id]) || {};
      const c = {
        id: e.entity_id,
        name: labels[e.entity_id] || e.name || dev.name_by_user || dev.name || a.friendly_name || e.entity_id,
        ip: a.ip || '',
        band: BAND[a.radio] || '',
        wlan: !!ap,
        online,
      };
      if (ap) wlanCount++; else lanCount++;
      const pinTarget = pins[e.entity_id] && byTracker.get(pins[e.entity_id]);
      if (pinTarget) pinTarget.pinned.push(c);
      else if (ap && nodes.get(ap)) nodes.get(ap).wlan.push(c);
      else wired.push(c);
    }

    const byName = (a, b) => a.name.localeCompare(b.name, 'de');
    const sortTree = (n) => {
      n.children.sort((a, b) => (KIND_ORDER[a.kind] - KIND_ORDER[b.kind]) || (a.status === 'off') - (b.status === 'off') || byName(a, b));
      n.wlan.sort(byName);
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
    return (this._config.wan || []).map((w) => {
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
      const d = w.device && st[w.device];
      return {
        name: w.name || 'WAN',
        detail: w.detail || '',
        primary: !!w.primary,
        status,
        value,
        more: w.entity || w.device || null,
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
    const sig = JSON.stringify(model) + [...this._expanded].join('|');
    if (sig === this._last) return;
    this._last = sig;
    this._render(model);
  }

  _renderError(err) {
    this.shadowRoot.innerHTML = `<ha-card><div style="padding:16px">UniFi-Netzplan: ${esc(err.message)}</div></ha-card>`;
  }

  _node(n, extra = []) {
    const kids = n.children.length + n.pinned.length + extra.length + (this._expanded.has(n.id) ? n.wlan.length : 0);
    const tag = n.status === 'off' ? '<span class="tag">inaktiv</span>' : n.mesh ? '<span class="tag mesh">Mesh</span>' : '';
    let pill = '';
    if (n.kind === 'ap' || n.wlan.length) {
      const open = this._expanded.has(n.id);
      const gap = n.clientsSensor != null && n.clientsSensor > n.wlan.length ? `<span class="gap">+${n.clientsSensor - n.wlan.length}</span>` : '';
      pill = n.wlan.length
        ? `<span class="pill" role="button" tabindex="0" data-toggle="${esc(n.id)}" aria-expanded="${open}" title="WLAN-Clients ein-/ausklappen"><ha-icon icon="${ICON.wlan}"></ha-icon>${n.wlan.length}${gap}<span class="chev">${open ? '▴' : '▾'}</span></span>`
        : `<span class="pill quiet"><ha-icon icon="${ICON.wlan}"></ha-icon>0${gap}</span>`;
    } else if (n.clientsSensor != null && n.status !== 'off') {
      pill = `<span class="pill quiet" title="Kabel-Clients direkt an diesem Geraet (Sensor Clients)"><ha-icon icon="${ICON.wired}"></ha-icon>${n.clientsSensor}</span>`;
    }
    // Beim Gateway ist ip die oeffentliche WAN-Adresse; welche Leitung, verraet die Integration nicht.
    const meta = [n.model, n.kind === 'gateway' ? '' : n.ip].filter(Boolean).join(' · ');
    const body = `
      <div class="node k-${n.kind} s-${n.status}" data-more="${esc(n.id)}" role="button" tabindex="0" title="${esc(n.state)}">
        <span class="ico"><ha-icon icon="${ICON[n.kind]}"></ha-icon></span>
        <span class="txt"><span class="nm">${esc(n.name)}${tag}</span><span class="mt">${esc(meta)}</span></span>
        ${pill}<span class="dot"></span>
      </div>`;
    let sub = '';
    if (kids) {
      const items = [
        ...n.children.map((c) => this._node(c)),
        ...n.pinned.map((c) => this._leaf(c, 'pin')),
        ...(this._expanded.has(n.id) ? n.wlan.map((c) => this._leaf(c, 'wlan')) : []),
        ...extra,
      ];
      sub = `<ul>${items.join('')}</ul>`;
    }
    const cls = [n.mesh ? 'mesh' : '', n.status === 'off' ? 'off' : ''].join(' ');
    return `<li class="${cls}">${body}${sub}</li>`;
  }

  _leaf(c, how) {
    const meta = [c.ip, c.band, how === 'pin' ? 'fest zugeordnet' : ''].filter(Boolean).join(' · ');
    return `<li class="leaf ${how === 'wlan' ? 'air' : ''}">
      <div class="client ${c.online ? '' : 'away'}" data-more="${esc(c.id)}" role="button" tabindex="0">
        <ha-icon icon="${c.wlan ? ICON.wlan : ICON.wired}"></ha-icon>
        <span class="txt"><span class="nm">${esc(c.name)}</span><span class="mt">${esc(meta)}</span></span>
      </div></li>`;
  }

  _wiredNode(list) {
    if (!list.length) return '';
    const open = this._expanded.has('wired');
    const rows = open ? `<ul>${list.map((c) => this._leaf(c, 'lan')).join('')}</ul>` : '';
    return `<li class="unknown">
      <div class="node k-cluster s-none">
        <span class="ico"><ha-icon icon="${ICON.cluster}"></ha-icon></span>
        <span class="txt"><span class="nm">Kabel-Clients</span><span class="mt">Switch und Port liefert die Integration nicht</span></span>
        <span class="pill" role="button" tabindex="0" data-toggle="wired" aria-expanded="${open}"><ha-icon icon="${ICON.wired}"></ha-icon>${list.length}<span class="chev">${open ? '▴' : '▾'}</span></span>
      </div>${rows}</li>`;
  }

  _wanRow(wan) {
    if (!wan.length) return '';
    const chips = wan.map((w) => {
      const modem = w.modem
        ? `<span class="mt" data-more="${esc(w.modem.id)}" role="button" tabindex="0">Modem ${esc(w.modem.name)}: ${w.modem.ok ? 'erreichbar' : 'nicht erreichbar'}</span>`
        : '';
      return `<div class="wan ${w.primary ? 'primary' : 'standby'} s-${w.status}" ${w.more ? `data-more="${esc(w.more)}" role="button" tabindex="0"` : ''}>
        <span class="ico"><ha-icon icon="${ICON.wan}"></ha-icon></span>
        <span class="txt"><span class="nm">${esc(w.name)}<span class="tag">${w.primary ? 'aktiv' : 'Reserve'}</span></span>
          <span class="mt">${esc([w.detail, w.value].filter(Boolean).join(' · '))}</span>${modem}</span>
        ${w.status !== 'none' ? '<span class="dot"></span>' : ''}
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
      ? m.roots.map((r, i) => this._node(r, i === 0 && m.wired.length ? [this._wiredNode(m.wired)] : [])).join('')
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

  _onClick(ev) {
    const t = ev.target.closest('[data-toggle]');
    if (t) {
      ev.stopPropagation();
      const id = t.dataset.toggle;
      if (this._expanded.has(id)) this._expanded.delete(id);
      else this._expanded.add(id);
      this._last = '';
      this._update();
      const again = this.shadowRoot.querySelector(`[data-toggle="${CSS.escape(id)}"]`);
      if (again) again.focus();
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
    --unp-fg: #f2f5f8; --unp-muted: #6e7988; --unp-line: rgba(255,255,255,0.10);
    --unp-tile: rgba(255,255,255,0.028); --unp-tile-line: rgba(255,255,255,0.06);
    --unp-ok: #a6d49e; --unp-warn: #e6b566; --unp-bad: #f0736a; --unp-info: #7fb3d5;
    --unp-edge: rgba(255,255,255,0.18);
    --unp-ico: 34px; --unp-pad: 6px; --unp-indent: 26px;
    container-type: inline-size; display: block;
  }
  @container (max-width: 460px) {
    ha-card { --unp-ico: 28px; --unp-pad: 4px; --unp-indent: 16px; padding-inline: 12px; }
    .node .mt { display: none; }
  }
  ha-card {
    display: block;
    background: var(--unp-bg); color: var(--unp-fg);
    border: 1px solid rgba(255,255,255,0.05); border-radius: 22px;
    box-shadow: 0 18px 44px -22px rgba(0,0,0,0.7);
    padding: 16px 18px 12px; overflow: hidden;
  }
  ha-icon { --mdc-icon-size: 20px; display: inline-flex; }
  .txt { display: flex; flex-direction: column; min-width: 0; flex: 1; }
  .nm { font-size: 14px; font-weight: 700; letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 6px; }
  .mt { font-size: 11.5px; color: var(--unp-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .head { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
  .head .mt { white-space: normal; }
  .hico { width: 44px; height: 44px; border-radius: 13px; display: grid; place-items: center; flex: none;
    background: rgba(166,212,158,0.12); border: 1px solid rgba(166,212,158,0.2); color: var(--unp-ok); }
  .title { font-size: 17px; font-weight: 700; letter-spacing: -0.02em; }
  .badge { font-size: 12.5px; font-weight: 700; padding: 6px 12px; border-radius: 12px; white-space: nowrap; }
  .badge.ok { color: var(--unp-ok); background: #a6d49e22; border: 1px solid #a6d49e3d; }
  .badge.bad { color: var(--unp-bad); background: #f0736a22; border: 1px solid #f0736a3d; }

  .wanrow { display: flex; flex-wrap: wrap; gap: 8px; }
  .wan { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 14px; cursor: pointer;
    background: var(--unp-tile); border: 1px solid var(--unp-tile-line); flex: 1 1 210px; min-width: 0; }
  .wan.primary { border-color: #a6d49e66; }
  .wan.standby { border-style: dashed; }
  .wan .ico { color: var(--unp-info); }

  ul { list-style: none; margin: 0; padding: 0; }
  .tree { margin-top: 6px; }
  .tree li { position: relative; padding: 4px 0 0 var(--unp-indent); }
  .tree > li { padding-left: 0; }
  .tree.fed > li { padding-top: 14px; }
  .tree.fed > li::before { content: ''; position: absolute; left: calc(var(--unp-pad) + var(--unp-ico) / 2 - 1px); top: 0; height: 14px; border-left: 2px solid var(--unp-edge); }
  .tree ul { margin-left: calc(var(--unp-pad) + var(--unp-ico) / 2 - 1px); }
  .tree ul > li::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; border-left: 2px solid var(--unp-edge); }
  .tree ul > li:last-child::before { bottom: auto; height: 27px; }
  .tree ul > li::after { content: ''; position: absolute; left: 0; top: 27px; width: calc(var(--unp-indent) - 2px); border-top: 2px solid var(--unp-edge); }
  .tree ul > li.leaf::after { top: 24px; }
  .tree ul > li.leaf:last-child::before { height: 24px; }
  .tree li.mesh::after, .tree li.mesh::before, .tree li.air::after { border-style: dotted; }
  .tree li.unknown::after, .tree li.off::after { border-top-style: dashed; }

  .node { display: flex; align-items: center; gap: 11px; padding: 6px 10px 6px var(--unp-pad); border-radius: 14px; cursor: pointer;
    background: var(--unp-tile); border: 1px solid var(--unp-tile-line); min-height: 34px; }
  .node:hover, .wan:hover, .client:hover { border-color: rgba(255,255,255,0.16); }
  .node .ico { width: var(--unp-ico); height: var(--unp-ico); border-radius: 10px; display: grid; place-items: center; flex: none; }
  .s-ok .ico { color: var(--unp-ok); background: #a6d49e22; border: 1px solid #a6d49e3a; }
  .s-warn .ico { color: var(--unp-warn); background: #e6b56622; border: 1px solid #e6b5663a; }
  .s-bad .ico { color: var(--unp-bad); background: #f0736a22; border: 1px solid #f0736a3a; }
  .s-off .ico, .s-none .ico { color: var(--unp-muted); background: rgba(255,255,255,0.04); border: 1px dashed var(--unp-line); }
  .s-off { opacity: 0.65; border-style: dashed; }
  .k-cluster { border-style: dashed; }
  .dot { width: 9px; height: 9px; border-radius: 50%; flex: none; background: var(--unp-muted); }
  .s-ok .dot { background: var(--unp-ok); box-shadow: 0 0 0 3px #a6d49e28; }
  .s-warn .dot { background: var(--unp-warn); box-shadow: 0 0 0 3px #e6b56628; }
  .s-bad .dot { background: var(--unp-bad); box-shadow: 0 0 0 3px #f0736a28; }
  .s-off .dot { background: transparent; border: 1.5px solid var(--unp-muted); }
  .tag { font-size: 10.5px; font-weight: 700; padding: 1px 6px; border-radius: 6px; color: var(--unp-muted); border: 1px solid var(--unp-line); }
  .tag.mesh { color: var(--unp-warn); border-color: #e6b5664d; }
  .wan.primary .tag { color: var(--unp-ok); border-color: #a6d49e4d; }

  .pill { display: inline-flex; align-items: center; gap: 4px; font-size: 12.5px; font-weight: 700; padding: 4px 9px; border-radius: 10px;
    color: var(--unp-ok); background: #a6d49e18; border: 1px solid #a6d49e33; cursor: pointer; white-space: nowrap; font-variant-numeric: tabular-nums; }
  .pill ha-icon { --mdc-icon-size: 15px; }
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
