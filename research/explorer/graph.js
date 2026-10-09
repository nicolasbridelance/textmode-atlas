// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
// Preserved scientific WebGL room; mounted by the single museum UI.
window.mountMuseumGraph = function(root, locale, workHref) {


const $ = (id) => root.querySelector("#" + id);
const t = (en, fr) => locale === "fr" ? fr : en;
let disposed = false;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const KINDS = {coloured_blocks: [255, 95, 160], blocks: [176, 186, 210], coloured_text: [80, 200, 255],
  text: [236, 232, 214]};
const YEAR_STOPS = [[1990, [70, 40, 170]], [1994, [47, 107, 255]], [1997, [36, 212, 200]],
  [2001, [142, 240, 90]], [2008, [255, 210, 58]], [2015, [255, 107, 61]], [2026, [255, 61, 168]]];
const MODES = {ink: "ink", community: "community", year: "year", kind: "kind", centrality: "centrality"};
const THUMB_ZOOM = 3.2;     // zoom (log2, from the overview) above which works show as thumbnails
const MAX_THUMBS = 180;   // icons share one texture atlas: keep it under GPU limits
const HIDDEN = 8;           // alpha of works a filter leaves out
const GLOW = 18;           // alpha of a work at rest: added up, dense regions glow without burning out
const ADDITIVE = {blend: true, blendColorOperation: "add", blendColorSrcFactor: "src-alpha",
  blendColorDstFactor: "one", blendAlphaOperation: "add", blendAlphaSrcFactor: "one",
  blendAlphaDstFactor: "one", depthWriteEnabled: false, depthCompare: "always"};

const S = {mode: "ink", year: null, playing: null, find: "", community: null, selected: null,
  hover: null, thumbs: [], view: null};
let N, E, C, n, deckgl, out, inn, positions, base, nearestPos, webColour;

function ramp(stops, v) {
  if (v <= stops[0][0]) return stops[0][1];
  for (let i = 1; i < stops.length; i++) {
    const [b, cb] = stops[i], [a, ca] = stops[i - 1];
    if (v <= b) { const t = (v - a) / (b - a); return ca.map((x, k) => Math.round(x + t * (cb[k] - x))); }
  }
  return stops[stops.length - 1][1];
}
const heat = (t) => ramp([[0, [40, 30, 90]], [0.35, [180, 40, 160]], [0.7, [255, 140, 40]], [1, [255, 250, 210]]], t);

async function load() {
  const [nodes, edges, comms] = await Promise.all([
    fetch("/api/graph/nodes").then((r) => r.json()),
    fetch("/api/graph/edges").then((r) => r.arrayBuffer()),
    fetch("/api/graph/communities").then((r) => r.json())]);
  N = nodes; C = comms.communities; n = N.sha256.length;
  if (!n) throw new Error("No visible graph nodes");
  E = new Uint32Array(edges);
  out = Array.from({length: n}, () => []); inn = Array.from({length: n}, () => []);
  for (let i = 0; i < E.length; i += 2) { out[E[i]].push(E[i + 1]); inn[E[i + 1]].push(E[i]); }
  positions = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { positions[i * 3] = N.x[i]; positions[i * 3 + 1] = -N.y[i]; }
  // Each work's tie to its nearest (edges come by source, then rank): the web seen from afar,
  // 84,000 lines; the ties of a selected work are drawn on demand.
  nearestPos = {s: new Float32Array(n * 3), t: new Float32Array(n * 3)};
  for (let i = 0; i < n; i++) {
    const t = out[i][0] ?? i;
    nearestPos.s.set(positions.subarray(i * 3, i * 3 + 3), i * 3);
    nearestPos.t.set(positions.subarray(t * 3, t * 3 + 3), i * 3);
  }
  communityGeometry();
  $("stats").textContent = `${n.toLocaleString()} ${t("works", "œuvres")} · ${(E.length / 2).toLocaleString()} ${t("links", "liens")} · `
    + `${C.length} ${t("communities. Features v1, train packs. Computed proximity; original graph measures.", "communautés. Features v1, packs d’apprentissage. Proximité calculée ; mesures du graphe d’origine.")}`;
  $("loading").remove();
}

function communityGeometry() {
  const k = C.length, sx = new Float64Array(k), sy = new Float64Array(k), cnt = new Float64Array(k);
  const ink = Array.from({length: k}, () => [0, 0, 0]);
  for (let i = 0; i < n; i++) {
    const c = N.community[i]; sx[c] += positions[i * 3]; sy[c] += positions[i * 3 + 1]; cnt[c]++;
    for (let j = 0; j < 3; j++) ink[c][j] += N.ink[i * 3 + j];
  }
  C.forEach((c, i) => {
    c.cx = sx[i] / cnt[i]; c.cy = sy[i] / cnt[i];
    const m = ink[i].map((v) => v / cnt[i]), peak = Math.max(...m, 1);
    c.colour = m.map((v) => Math.round(Math.min(255, v * 235 / peak)));
  });
  // Frame the mass, not the strays: a few isolated works sit far from everything.
  const xs = Float64Array.from(N.x).sort(), ys = Float64Array.from(N.y, (v) => -v).sort();
  const q = (a, p) => a[Math.floor(p * (a.length - 1))];
  S.bounds = [q(xs, 0.005), q(ys, 0.005), q(xs, 0.995), q(ys, 0.995)];
  S.extent = Math.max(S.bounds[2] - S.bounds[0], S.bounds[3] - S.bounds[1]);
}

function nodeColour(i) {
  switch (S.mode) {
    case "community": return C[N.community[i]].colour;
    case "year": return N.year[i] ? ramp(YEAR_STOPS, N.year[i]) : [90, 90, 100];
    case "kind": return KINDS[N.kind[i]] || [255, 200, 80];
    case "centrality": return heat(Math.min(1, Math.sqrt(N.in_degree[i] / 60)));
    default: return [N.ink[i * 3], N.ink[i * 3 + 1], N.ink[i * 3 + 2]];
  }
}

function matches(i) {
  if (S.community !== null && N.community[i] !== S.community) return 0;
  if (S.find) {
    const f = S.find;
    const hit = [N.group[i], N.author[i], N.pack[i]].some((v) => v && v.toLowerCase().includes(f));
    if (!hit) return 0;
  }
  if (S.year !== null) {
    if (!N.year[i] || N.year[i] > S.year) return 0;
    return N.year[i] === S.year ? 2 : 1;   // this year's works flare, earlier ones remain
  }
  return 1;
}

function colours() {
  const filtering = S.community !== null || S.find || S.year !== null;
  const fill = new Uint8Array(n * 4);
  for (let i = 0; i < n; i++) {
    const [r, g, b] = nodeColour(i), m = matches(i);
    const alpha = !filtering ? GLOW : m === 2 ? 255 : m === 1 ? (S.year !== null ? GLOW : 150) : HIDDEN - 2;
    fill.set(m === 2 ? [Math.min(255, r + 60), Math.min(255, g + 60), Math.min(255, b + 60), alpha] : [r, g, b, alpha], i * 4);
  }
  base = fill;
  webColour = new Uint8Array(n * 4);
  for (let i = 0; i < n; i++) webColour.set([fill[i * 4], fill[i * 4 + 1], fill[i * 4 + 2], Math.round(fill[i * 4 + 3] * 0.55)], i * 4);
}

function radius() {
  const r = new Float32Array(n), unit = S.extent / 2600;
  for (let i = 0; i < n; i++) r[i] = unit * (1 + Math.sqrt(N.in_degree[i]) / 2.5);
  return r;
}
let radii;

function layers() {
  const zoom = S.view ? S.view.zoom - S.zoom0 : 0;
  const thumbs = zoom >= THUMB_ZOOM;
  const sel = S.selected;
  const ls = [
    new deck.LineLayer({id: "nearest", data: {length: n, attributes: {
          getSourcePosition: {value: nearestPos.s, size: 3}, getTargetPosition: {value: nearestPos.t, size: 3},
          getColor: {value: webColour, size: 4, normalized: true}}},
        widthUnits: "pixels", getWidth: 1, parameters: ADDITIVE,
        updateTriggers: {getColor: [S.mode, S.year, S.find, S.community]}}),
    new deck.ScatterplotLayer({id: "works", data: {length: n, attributes: {
        getPosition: {value: positions, size: 3}, getFillColor: {value: base, size: 4, normalized: true},
        getRadius: {value: radii, size: 1}}},
      radiusUnits: "common", radiusMinPixels: 0.7, radiusMaxPixels: thumbs ? 4 : 40, antialiasing: true,
      parameters: ADDITIVE, pickable: true, autoHighlight: false,
      updateTriggers: {getFillColor: [S.mode, S.year, S.find, S.community]}}),
  ];
  if (sel !== null) {
    const ties = [...out[sel].map((j) => [sel, j, 1]), ...inn[sel].filter((j) => !out[sel].includes(j)).map((j) => [j, sel, 0])];
    ls.push(new deck.LineLayer({id: "ties", data: ties,
      getSourcePosition: (d) => positions.subarray(d[0] * 3, d[0] * 3 + 3),
      getTargetPosition: (d) => positions.subarray(d[1] * 3, d[1] * 3 + 3),
      getColor: (d) => d[2] ? [85, 255, 255, 230] : [255, 85, 255, 150], getWidth: 1.6, widthUnits: "pixels",
      parameters: ADDITIVE}));
    ls.push(new deck.ScatterplotLayer({id: "ring", data: [sel, ...out[sel]],
      getPosition: (i) => positions.subarray(i * 3, i * 3 + 3), getRadius: (i) => i === sel ? 9 : 5,
      radiusUnits: "pixels", stroked: true, filled: false, getLineColor: (i) => i === sel ? [255, 255, 255, 255] : [85, 255, 255, 200],
      lineWidthUnits: "pixels", getLineWidth: 1.4}));
  }
  if (thumbs && S.thumbs.length) {
    const h = S.extent / 260;
    ls.push(new deck.IconLayer({id: "thumbs", data: S.thumbs,
      getPosition: (i) => positions.subarray(i * 3, i * 3 + 3),
      getIcon: (i) => ({url: `/image/icon/${N.sha256[i]}`, id: N.sha256[i], width: 160, height: 100}),
      getSize: h, sizeUnits: "common", sizeMinPixels: 14, sizeMaxPixels: 140,
      textureParameters: {minFilter: "nearest", magFilter: "nearest"},
      pickable: true, parameters: {depthCompare: "always"}}));
  } else {
    ls.push(new deck.TextLayer({id: "names", data: C.filter((c) => c.works >= 150),
      getPosition: (c) => [c.cx, c.cy, 0], getText: (c) => `#${c.community} ${c.name.split(" · ")[0]}`,
      getColor: (c) => [...c.colour, 235],
      extensions: [new deck.CollisionFilterExtension()], collisionEnabled: true,
      getCollisionPriority: (c) => Math.round(Math.log10(c.works) * 200), collisionTestProps: {sizeScale: 1.6},
      getSize: (c) => 10 + Math.min(5, Math.log10(c.works) * 1.4), sizeUnits: "pixels",
      fontFamily: "ui-monospace, monospace", characterSet: "auto", fontWeight: 500,
      background: true, getBackgroundColor: [2, 3, 8, 170], backgroundPadding: [5, 2],
      getTextAnchor: "middle", getAlignmentBaseline: "center", pickable: true,
      updateTriggers: {getColor: [S.mode]}}));
  }
  return ls;
}

function redraw() { deckgl.setProps({layers: layers()}); }

let thumbTimer = 0;
function refreshThumbs() {
  clearTimeout(thumbTimer);
  thumbTimer = setTimeout(() => {
    if (!S.view || S.view.zoom - S.zoom0 < THUMB_ZOOM) { S.thumbs = []; redraw(); return; }
    const vp = deckgl.getViewports()[0];
    const [minX, minY, maxX, maxY] = vp.getBounds();
    const seen = [];
    for (let i = 0; i < n; i++) {
      const x = positions[i * 3], y = positions[i * 3 + 1];
      if (x >= minX && x <= maxX && y >= minY && y <= maxY && base[i * 4 + 3] > HIDDEN) seen.push(i);
    }
    seen.sort((a, b) => N.in_degree[b] - N.in_degree[a]);
    S.thumbs = seen.slice(0, MAX_THUMBS);
    redraw();
  }, 140);
}

function fitView(bounds, pad = 0.9) {
  const [minX, minY, maxX, maxY] = bounds, w = root.clientWidth, h = root.clientHeight;
  const zoom = Math.log2(Math.min(w / (maxX - minX || 1), h / (maxY - minY || 1)) * pad);
  return {target: [(minX + maxX) / 2, (minY + maxY) / 2, 0], zoom, transitionDuration: 900,
    transitionInterpolator: new deck.LinearInterpolator(["target", "zoom"])};
}
function flyTo(view) { S.view = {...S.view, ...view}; deckgl.setProps({initialViewState: {...view}}); }

function tooltip(info) {
  const tip = $("tip");
  const i = pickIndex(info);
  if (i === null || i === undefined || i < 0) { tip.style.display = "none"; return; }
  tip.innerHTML = `<img src="/image/best/${N.sha256[i]}" alt=""><div><b>${esc(N.title[i] || N.path[i])}</b><br>`
    + `${esc(N.author[i] || "?")} / ${esc(N.group[i] || "?")}<br>${esc(N.pack[i])} · ${N.year[i] ?? "?"} · `
    + `<span style="color:rgb(${C[N.community[i]].colour})">#${N.community[i]}</span></div>`;
  tip.style.display = "block";
  const x = Math.min(info.x + 18, window.innerWidth - 270), y = Math.min(info.y + 18, window.innerHeight - 260);
  tip.style.left = x + "px"; tip.style.top = y + "px";
}

function pickIndex(info) {
  if (!info.layer) return null;
  if (info.layer.id === "works") return info.index;
  if (info.layer.id === "thumbs") return info.object;
  return null;
}

async function select(i, fly = false) {
  S.selected = i; redraw();
  $("comms").classList.remove("open");
  const side = $("side"), c = C[N.community[i]];
  if (fly) flyTo({target: [positions[i * 3], positions[i * 3 + 1], 0], zoom: Math.max(S.view.zoom, S.zoom0 + THUMB_ZOOM + 0.6),
    transitionDuration: 900, transitionInterpolator: new deck.LinearInterpolator(["target", "zoom"])});
  side.innerHTML = `<button class="btn close" data-close="side">✕</button>
    <h2>${esc(N.title[i] || N.path[i])}</h2>
    <div class="meta">${esc(N.author[i] || "?")} / ${esc(N.group[i] || "?")} · ${esc(N.pack[i])} · ${N.year[i] ?? "?"} · ${esc(N.archive[i])}<br>
    ${esc(N.path[i])} · ${t("chosen among the nearest by", "choisie parmi les plus proches par")} ${N.in_degree[i]} ${t("works", "œuvres")}</div>
    <div class="art"><img src="/image/full/${N.sha256[i]}" alt=""></div>
    <h3>${t("Nearby works", "Œuvres proches")}</h3><div class="thumbs">${out[i].map((j) =>
      `<img src="/image/best/${N.sha256[j]}" data-i="${j}" title="${esc(N.path[j])} · ${esc(N.group[j] || "?")} · ${N.year[j] ?? "?"}" alt="">`).join("")}</div>
    <h3>${t("Community", "Communauté")}</h3>${card(c)}
    <div class="row" style="margin-top:12px"><a class="btn" href="${workHref(N.sha256[i])}" style="text-decoration:none">${t("Open this work", "Ouvrir cette œuvre")}</a></div>`;
  side.classList.add("open");
  wireThumbs(side);
}
const closeSide = () => { $("side").classList.remove("open"); S.selected = null; redraw(); };

function wireThumbs(root) {
  for (const button of root.querySelectorAll("[data-close]")) { button.setAttribute("aria-label", t("Close", "Fermer")); button.onclick = () => button.dataset.close === "side" ? closeSide() : $(button.dataset.close).classList.remove("open"); }
  for (const img of root.querySelectorAll("img[data-i]")) img.onclick = (e) => { e.stopPropagation(); select(+img.dataset.i, true); };
  for (const el of root.querySelectorAll(".card[data-c]")) { el.tabIndex = 0; el.setAttribute("role", "button"); el.onclick = () => focusCommunity(+el.dataset.c); el.onkeydown = (event) => { if (event.key === "Enter") { event.stopPropagation(); focusCommunity(+el.dataset.c); } }; }
}

const index = () => { const m = new Map(); N.sha256.forEach((s, i) => m.set(s, i)); return m; };
let bySha;
function thumb(sha) { const i = bySha.get(sha); return i === undefined ? "" : `<img src="/image/best/${sha}" data-i="${i}" alt="" title="${esc(N.path[i])} · ${esc(N.group[i] || "?")} · ${N.year[i] ?? "?"}">`; }

function card(c) {
  const y = c.years ? `${c.years[1]}–${c.years[3]} (${t("median", "médiane")} ${c.years[2]})` : t("undated", "non datée");
  const tight = c.spread < 2.5 ? t("tight","resserrée") : c.spread < 4.2 ? t("moderate","modérée") : t("loose","dispersée");
  const kinds = Object.entries(c.kinds).map(([k, v]) => `${k.replace("_", " ")} ${Math.round(100 * v / (c.original_works ?? c.works))}%`).join(", ");
  return `<div class="card${S.community === c.community ? " on" : ""}" data-c="${c.community}">
    <div class="head"><span class="dot" style="color:rgb(${c.colour});background:rgb(${c.colour})"></span>
      <span class="name">#${c.community} ${esc(c.name)}</span><span class="n">${c.works.toLocaleString()}</span></div>
    <div class="facts">${y} · ${kinds}<br>${tight} (${t("spread", "dispersion")} ${c.spread}) · ${esc(c.groups.slice(0, 3).join(", "))}</div>
    <div class="arch">${thumb(c.archetype)}${c.typical.map(thumb).join("")}</div>
    <div class="axis">${c.axis.from_works.map(thumb).join("")}<span>↔</span>${c.axis.to_works.map(thumb).join("")}</div>
    <div class="axis-words"><em>${esc(c.axis.from || "–")}</em><span>${Math.round(c.axis.variance_share * 100)}% ${t("of variation", "de variation")}</span><em style="text-align:right">${esc(c.axis.to || "–")}</em></div>
    <div class="sig">${t("Archetype first, then typical works; below, both ends of the main axis. Named by", "Archétype, puis œuvres typiques ; en dessous, les extrémités de l’axe principal. Nom calculé par")} ${esc(c.named_by)}.</div>
  </div>`;
}

function openCommunities() {
  const p = $("comms");
  p.innerHTML = `<button class="btn close" data-close="comms">✕</button>
    <h2>${C.length} ${t("communities", "communautés")}</h2>
    <p>${t("Found by Leiden on the nearest-work graph. Archetypes, typical works and main axes describe the original training graph; examples are limited to display-eligible works. Names are computed descriptions.", "Communautés calculées par Leiden sur le graphe de proximité. Archétypes, œuvres typiques et axes décrivent le graphe d’apprentissage d’origine ; les exemples respectent les droits d’affichage. Les noms sont des descriptions calculées.")}</p>
    ${C.map(card).join("")}`;
  $("side").classList.remove("open");
  p.classList.add("open");
  wireThumbs(p);
}

function focusCommunity(c) {
  S.community = S.community === c ? null : c; colours();
  if (S.community !== null) {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    const xs = [], ys = [];
    for (let i = 0; i < n; i++) if (N.community[i] === c) { xs.push(positions[i * 3]); ys.push(positions[i * 3 + 1]); }
    xs.sort((a, b) => a - b); ys.sort((a, b) => a - b);
    const q = (a, p) => a[Math.floor(p * (a.length - 1))];
    minX = q(xs, 0.02); maxX = q(xs, 0.98); minY = q(ys, 0.02); maxY = q(ys, 0.98);
    flyTo(fitView([minX, minY, maxX, maxY], 0.7));
  }
  for (const el of root.querySelectorAll(".card[data-c]")) el.classList.toggle("on", +el.dataset.c === S.community);
  redraw(); refreshThumbs();
}

function legend() {
  const L = $("legend");
  const grad = (stops, a, b) => `linear-gradient(90deg, ${stops.map(([v, c]) => `rgb(${c}) ${100 * (v - a) / (b - a)}%`).join(", ")})`;
  const text = {
    ink: t('Each work glows in the colours it is drawn with: its foreground colours mixed by cell count, black left out.', 'Chaque œuvre prend les couleurs de son encre, pondérées par le nombre de cellules, sans le noir.'),
    community: t(`The ${C.length} communities in their works’ mean ink. Open them to see their archetypes.`, `Les ${C.length} communautés dans l’encre moyenne de leurs œuvres. Ouvrez-les pour voir les archétypes.`),
    year: t("Year of the pack, from 16colo's filing.", 'Année du pack, selon le classement de l’archive.'),
    kind: t('Content kind, from colours and block share (works v2).', 'Type de contenu calculé selon les couleurs et la proportion de blocs.'),
    centrality: t('How many works have this one among their 10 nearest: typicality, not importance.', 'Nombre d’œuvres dont celle-ci est un voisin proche dans le graphe d’origine : une mesure de typicalité.'),
  }[S.mode];
  let body = "";
  if (S.mode === "year") body = `<div class="ramp" style="background:${grad(YEAR_STOPS, 1990, 2026)}"></div><div class="ends"><span>1990</span><span>2008</span><span>2026</span></div>`;
  if (S.mode === "centrality") body = `<div class="ramp" style="background:${grad([[0, heat(0)], [0.35, heat(0.35)], [0.7, heat(0.7)], [1, heat(1)]], 0, 1)}"></div><div class="ends"><span>0</span><span>15</span><span>60+</span></div>`;
  if (S.mode === "kind") body = Object.entries(KINDS).map(([k, c]) => `<span class="sw"><i style="background:rgb(${c})"></i>${k.replace("_", " ")}</span>`).join("");
  L.innerHTML = `${text}${body}`;
}

function setMode(m) {
  S.mode = m; colours(); legend(); redraw();
  for (const b of $("modes").children) b.setAttribute("aria-pressed", String(b.dataset.m === m));
}

function play() {
  if (S.playing) { clearInterval(S.playing); S.playing = null; $("play").textContent = "▶"; return; }
  $("play").textContent = "❚❚";
  let y = S.year && S.year < 2026 ? S.year : 1989;
  S.playing = setInterval(() => {
    y += 1; if (y > 2026) { clearInterval(S.playing); S.playing = null; $("play").textContent = "▶"; return; }
    setYear(y);
  }, 650);
}
function setYear(y) {
  S.year = y >= 2026 && !S.playing ? null : y; $("slider").value = y; $("year").textContent = S.year ?? t("all", "toutes");
  colours(); redraw(); refreshThumbs();
}

async function main() {
  await load(); if (disposed) return; bySha = index(); radii = radius(); colours();
  for (const m of Object.keys(MODES)) {
    const b = document.createElement("button"); b.textContent = ({ink:t("ink","encre"),community:t("community","communauté"),year:t("year","année"),kind:t("kind","contenu"),centrality:t("centrality","centralité")})[m]; b.dataset.m = m; b.onclick = () => setMode(m);
    $("modes").append(b);
  }
  const start = fitView(S.bounds, 0.86);
  S.view = start; S.zoom0 = start.zoom;
  deckgl = new deck.Deck({
    parent: $("map"), views: new deck.OrthographicView({id: "o", flipY: false}),
    initialViewState: start, controller: {scrollZoom: {speed: 0.02, smooth: true}, inertia: 300},
    onViewStateChange: ({viewState}) => { S.view = viewState; refreshThumbs(); return viewState; },
    getCursor: ({isHovering}) => isHovering ? "pointer" : "grab",
    onHover: tooltip,
    onClick: (info) => {
      if (info.layer && info.layer.id === "names") { focusCommunity(info.object.community); return; }
      const i = pickIndex(info); if (i !== null && i !== undefined) select(i);
    },
    layers: [],
  });
  setMode("ink");
  $("find").oninput = (e) => { S.find = e.target.value.trim().toLowerCase(); colours(); redraw(); refreshThumbs(); };
  $("slider").oninput = (e) => setYear(+e.target.value);
  $("play").onclick = play;
  $("openComms").onclick = openCommunities;
  $("reset").onclick = () => { S.community = null; S.find = ""; $("find").value = ""; setYear(2026); flyTo(fitView(S.bounds, 0.86)); closeSide(); };
  const keydown = (e) => {
    if (e.target.closest("input, select, textarea, button, a")) return;
    if (e.key === " ") { e.preventDefault(); play(); }
    if (e.key === "Escape") { closeSide(); $("comms").classList.remove("open"); }
    if (e.key === "c") openCommunities();
  };
  root.addEventListener("keydown", keydown);
}
main().catch(() => { const loading = $("loading"); if (loading) loading.textContent = t("Constellation unavailable", "Constellation indisponible"); });
return () => { disposed = true; clearTimeout(thumbTimer); clearInterval(S.playing); if (deckgl) deckgl.finalize(); };

};
