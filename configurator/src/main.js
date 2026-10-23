import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { gunzipSync, strToU8, zipSync } from "fflate";

const BED = 256;          // Bambu A1 / P1 bed; the layout is centred on it
const GAP = 8;
const PARTS = "./parts/";

// ---- i18n -----------------------------------------------------------------
const params = new URLSearchParams(location.search);
const lang = params.get("lang") || (navigator.language || "en").slice(0, 2);
const RU = lang === "ru";
const T = RU ? {
  home: "Mitya Labs", title: "Конфигуратор Skladen 2", sub: "Выберите детали и скачайте файл для печати",
  lid: "Крышка", frame: "Рамка", base: "База",
  rib: "Рёбра прижима, мм", ribHint: "Высота ребра над стенкой кармана. Начните с 0.60.",
  tab: "Язычки кнопок, мм", tabHint: "Тоньше — мягче нажим на кнопку телефона.",
  logo: "Логотип", none: "Без", recess: "Вставка", through: "Насквозь",
  logoHint: "Вставка и «насквозь» печатаются вторым цветом, нужен 3MF.",
  frameKind: "Вид", open: "С вырезом", closed: "Закрытая",
  frameHint: "Закрытая рамка — для крышки с язычками (по умолчанию).",
  nut: "Гайка", din: "DIN 934", plain: "Простая (мелкий карман)",
  sw: "Переключатель клавиатуры", shuttle: "Толкатель", window: "Окно + пробка",
  finger: "Пальцы, мм", proud: "Выступ штока, мм", clr: "Зазор пробки, мм",
  swHint: "Размеры толкателя не измерены: напечатайте набор и оставьте подходящий.",
  summary: "В комплекте", empty: "Ничего не выбрано",
  stl: "Скачать STL", mf: "Скачать 3MF",
  stlNote: "STL: все детали одним файлом, один цвет.", mfNote: "3MF: каждая деталь — отдельный объект, вставка логотипа — вторая часть. Что не влезло на один стол, лежит на следующем; в слайсере можно разложить заново.",
  parts: { lid: "Крышка", inlay: "Вставка логотипа", frame: "Рамка", base: "База", shuttle: "Толкатель", plug: "Пробка" },
} : {
  home: "Mitya Labs", title: "Skladen 2 Configurator", sub: "Pick the parts, download a print file",
  lid: "Lid", frame: "Frame", base: "Base",
  rib: "Crush ribs, mm", ribHint: "How far a rib stands off the pocket wall. Start with 0.60.",
  tab: "Button tongues, mm", tabHint: "Thinner is a softer push on the phone's key.",
  logo: "Logo", none: "None", recess: "Inlay", through: "Through",
  logoHint: "Inlay and through are printed in a second colour: use 3MF.",
  frameKind: "Kind", open: "With cut-out", closed: "Closed",
  frameHint: "The closed frame goes with the lid's tongues (the default).",
  nut: "Nut", din: "DIN 934", plain: "Plain (shallow pocket)",
  sw: "Keyboard power switch", shuttle: "Shuttle", window: "Window + plug",
  finger: "Fingers, mm", proud: "Stem proud, mm", clr: "Plug clearance, mm",
  swHint: "The shuttle's size is not measured: print the set and keep what fits.",
  summary: "In the kit", empty: "Nothing selected",
  stl: "Download STL", mf: "Download 3MF",
  stlNote: "STL: all parts in one file, one colour.", mfNote: "3MF: each part is its own object, the logo inlay a second part. What does not fit one bed lies on the next; the slicer can arrange it again.",
  parts: { lid: "Lid", inlay: "Logo inlay", frame: "Frame", base: "Base", shuttle: "Shuttle", plug: "Plug" },
};
document.documentElement.lang = RU ? "ru" : "en";
document.title = T.title;
if (params.get("theme")) document.documentElement.dataset.theme = params.get("theme");

// ---- state ----------------------------------------------------------------
const DEFAULTS = {
  lid: "1", rib: "0.60", tab: "1.0", logo: "recess",
  frame: "1", frameKind: "closed",
  base: "1", nut: "din934", sw: "window", finger: "1.0", proud: "1.0", clr: "0.10",
};
const state = { ...DEFAULTS };
for (const k of Object.keys(DEFAULTS)) {
  const v = new URLSearchParams(location.hash.slice(1)).get(k);
  if (v !== null) state[k] = v;
}

const OPTIONS = {
  rib: ["0.50", "0.60", "0.70"], tab: ["0.8", "1.0", "1.2"],
  finger: ["0.5", "1.0", "1.5"], proud: ["0.5", "1.0", "1.5", "2.0", "3.0"],
  clr: ["0.05", "0.10", "0.15"],
};

/** The kit: one entry per thing that prints, each a list of meshes sharing one position. */
function kit() {
  const out = [];
  if (state.lid === "1") {
    const meshes = [{ key: `lid-r${state.rib}-t${state.tab}-${state.logo}`, role: "lid" }];
    if (state.logo !== "none") meshes.push({ key: state.logo === "recess" ? "inlay-recess" : "inlay-through", role: "inlay" });
    out.push({ id: "lid", name: T.parts.lid, meshes, anchor: 0, label: `${T.parts.lid}: ${state.rib} / ${state.tab}` });
  }
  if (state.frame === "1") {
    out.push({ id: "frame", name: T.parts.frame, meshes: [{ key: `frame-${state.frameKind === "closed" ? "closed" : "open"}`, role: "frame" }], anchor: 0, label: `${T.parts.frame}: ${T[state.frameKind]}` });
  }
  if (state.base === "1") {
    out.push({ id: "base", name: T.parts.base, meshes: [{ key: `base-${state.nut}-${state.sw}`, role: "base" }], anchor: 0, label: `${T.parts.base}: ${state.nut === "din934" ? T.din : T.plain}` });
    if (state.sw === "shuttle") {
      out.push({ id: "shuttle", name: T.parts.shuttle, meshes: [{ key: `shuttle-f${state.finger}-p${state.proud}`, role: "small" }], anchor: 0, label: `${T.parts.shuttle}: ${state.finger} / ${state.proud}` });
    } else {
      out.push({ id: "plug", name: T.parts.plug, meshes: [{ key: `plug-c${state.clr}`, role: "small" }], anchor: 0, label: `${T.parts.plug}: ${state.clr}` });
    }
  }
  return out;
}

// ---- data -----------------------------------------------------------------
let manifest;
const cache = new Map();

function load(key) {
  if (!cache.has(key)) {
    cache.set(key, fetch(`${PARTS}${key}.bin.gz`).then(async (r) => {
      if (!r.ok) throw new Error(`${key}: ${r.status}`);
      let raw = new Uint8Array(await r.arrayBuffer());
      if (raw[0] === 0x1f && raw[1] === 0x8b) raw = gunzipSync(raw);   // a server may have decoded it already
      const dv = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
      const nv = dv.getUint32(0, true), nt = dv.getUint32(4, true);
      const pos = new Float32Array(raw.buffer.slice(raw.byteOffset + 8, raw.byteOffset + 8 + nv * 12));
      const idx = new Uint32Array(raw.buffer.slice(raw.byteOffset + 8 + nv * 12, raw.byteOffset + 8 + nv * 12 + nt * 12));
      return { pos, idx };
    }));
  }
  return cache.get(key);
}

// ---- layout ---------------------------------------------------------------
const STRIDE = BED * 1.2;   // plates sit a fifth of a bed apart, as in Bambu Studio

/** Shelf packing onto as many beds as it takes, biggest first. Each entry gets its plate
 *  and the offset that puts its own bounding-box corner there; plates are laid in a row. */
function layout(items) {
  const boxes = items.map((it) => {
    const lid = manifest.parts[it.meshes[0].key];
    return { it, min: lid.min, w: lid.max[0] - lid.min[0], d: lid.max[1] - lid.min[1] };
  });
  const plates = [];
  for (const b of [...boxes].sort((p, q) => q.w * q.d - p.w * p.d)) {
    let spot = null;
    for (const [pi, plate] of plates.entries()) {
      const row = plate.rows.find((r) => r.w + GAP + b.w <= BED && b.d <= r.d);
      if (row) { spot = { pi, row }; break; }
      const used = plate.rows.reduce((s, r) => s + r.d + GAP, 0);
      if (used + b.d <= BED && b.w <= BED) { spot = { pi, row: null }; break; }
    }
    if (!spot) { plates.push({ rows: [] }); spot = { pi: plates.length - 1, row: null }; }
    const plate = plates[spot.pi];
    let row = spot.row;
    if (!row) { row = { w: 0, d: b.d, y: plate.rows.reduce((s, r) => s + r.d + GAP, 0), items: [] }; plate.rows.push(row); }
    b.plate = spot.pi; b.x = row.w; b.y = row.y;
    row.w += (row.items.length ? GAP : 0) + b.w;
    row.items.push(b);
  }
  plates.forEach((plate, pi) => {
    const w = Math.max(...plate.rows.map((r) => r.w));
    const d = plate.rows.reduce((s, r) => s + r.d + GAP, -GAP);
    const ox = pi * STRIDE + (BED - w) / 2, oy = (BED - d) / 2;
    plate.rows.forEach((r) => {
      let x = 0;
      r.items.forEach((b) => { b.offset = [ox + x - b.min[0], oy + r.y - b.min[1], -b.min[2]]; x += b.w + GAP; });
    });
  });
  return { boxes, count: plates.length };
}

// ---- scene ----------------------------------------------------------------
const view = document.getElementById("view");
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
view.prepend(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 1, 3000);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI / 2 - 0.02;

scene.add(new THREE.HemisphereLight(0xffffff, 0x667066, 1.5));
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(-120, -200, 320);
scene.add(sun);

const beds = new THREE.Group();
scene.add(beds);
const bedMat = new THREE.MeshBasicMaterial({ color: 0x808a84, transparent: true, opacity: 0.16 });
const gridMat = new THREE.LineBasicMaterial({ color: 0x808a84, transparent: true, opacity: 0.25 });

function setBeds(n) {
  beds.clear();
  for (let i = 0; i < n; i++) {
    const bed = new THREE.Mesh(new THREE.PlaneGeometry(BED, BED), bedMat);
    bed.position.set(i * STRIDE + BED / 2, BED / 2, -0.05);
    const grid = new THREE.GridHelper(BED, 16);
    grid.material = gridMat;
    grid.rotation.x = Math.PI / 2;
    grid.position.set(i * STRIDE + BED / 2, BED / 2, 0);
    beds.add(bed, grid);
  }
}

let framedFor = 0;
function frame(n) {
  if (n === framedFor) return;
  framedFor = n;
  const cx = ((n - 1) * STRIDE + BED) / 2, span = Math.max(BED, (n - 1) * STRIDE + BED);
  controls.target.set(cx, BED / 2, 10);
  camera.position.set(cx - span * 0.25, BED / 2 - span * 1.15 - 60, span * 0.95 + 60);
}

const COLORS = { lid: 0x2f6fd0, inlay: 0x2fb36a, frame: 0xd9d9d2, base: 0x9aa39d, small: 0xe0a030 };
const mats = Object.fromEntries(Object.entries(COLORS).map(([k, c]) => [k, new THREE.MeshStandardMaterial({ color: c, flatShading: true, roughness: 0.55, metalness: 0.05 })]));
const content = new THREE.Group();
scene.add(content);

function resize() {
  const w = view.clientWidth, h = view.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(view);
resize();
(function tick() { controls.update(); renderer.render(scene, camera); requestAnimationFrame(tick); })();

let current = null;   // { items, boxes, meshes: Map<key, geometry data> } of what is shown
let token = 0;

async function refresh() {
  const mine = ++token;
  const items = kit();
  const loadingEl = document.getElementById("loading");
  loadingEl.classList.add("on");
  let data;
  try {
    data = await Promise.all(items.map((it) => Promise.all(it.meshes.map((m) => load(m.key)))));
  } catch (e) {
    console.error(e);
    return;
  }
  if (mine !== token) return;
  loadingEl.classList.remove("on");
  const { boxes, count } = layout(items);
  setBeds(Math.max(count, 1));
  frame(Math.max(count, 1));
  for (const c of [...content.children]) { content.remove(c); c.children.forEach((m) => m.geometry.dispose()); }
  boxes.forEach((b, i) => {
    const g = new THREE.Group();
    g.position.set(...b.offset);
    b.it.meshes.forEach((m, j) => {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.BufferAttribute(data[i][j].pos, 3));
      geo.setIndex(new THREE.BufferAttribute(data[i][j].idx, 1));
      geo.computeVertexNormals();
      g.add(new THREE.Mesh(geo, mats[m.role]));
    });
    content.add(g);
  });
  current = { boxes, data, items };
  document.getElementById("hud").textContent = RU
    ? `${count} ${count === 1 ? "стол" : count < 5 ? "стола" : "столов"} ${BED}×${BED}`
    : `${count} bed${count === 1 ? "" : "s"} of ${BED}×${BED}`;
  renderSummary(items);
  document.getElementById("dl-stl").disabled = document.getElementById("dl-3mf").disabled = items.length === 0;
  parent !== window && parent.postMessage({ type: "skladen-config", config: { ...state }, kit: items.map((i) => i.meshes.map((m) => m.key)) }, "*");
}

// ---- export ---------------------------------------------------------------
/** Triangles of one mesh, moved by its group's offset: [x,y,z]*3 per triangle. */
function placed(boxIndex, meshIndex) {
  const { pos, idx } = current.data[boxIndex][meshIndex];
  const [dx, dy, dz] = current.boxes[boxIndex].offset;
  const v = new Float32Array(pos.length);
  for (let i = 0; i < pos.length; i += 3) { v[i] = pos[i] + dx; v[i + 1] = pos[i + 1] + dy; v[i + 2] = pos[i + 2] + dz; }
  return { v, idx };
}

function stl() {
  const meshes = current.boxes.flatMap((b, i) => b.it.meshes.map((_, j) => placed(i, j)));
  const nt = meshes.reduce((s, m) => s + m.idx.length / 3, 0);
  const buf = new ArrayBuffer(84 + nt * 50);
  const dv = new DataView(buf);
  new TextEncoder().encodeInto("Skladen 2 configurator", new Uint8Array(buf, 0, 80));
  dv.setUint32(80, nt, true);
  let o = 84;
  for (const { v, idx } of meshes) {
    for (let t = 0; t < idx.length; t += 3) {
      const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
      const ux = v[b] - v[a], uy = v[b + 1] - v[a + 1], uz = v[b + 2] - v[a + 2];
      const wx = v[c] - v[a], wy = v[c + 1] - v[a + 1], wz = v[c + 2] - v[a + 2];
      let nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx;
      const l = Math.hypot(nx, ny, nz) || 1;
      nx /= l; ny /= l; nz /= l;
      for (const f of [nx, ny, nz, v[a], v[a + 1], v[a + 2], v[b], v[b + 1], v[b + 2], v[c], v[c + 1], v[c + 2]]) { dv.setFloat32(o, f, true); o += 4; }
      o += 2;
    }
  }
  return new Blob([buf], { type: "model/stl" });
}

function threeMF() {
  const f = (n) => Math.round(n * 1e4) / 1e4;
  let id = 0;
  const res = [], items = [];
  current.boxes.forEach((b, i) => {
    const ids = b.it.meshes.map((m, j) => {
      const { v, idx } = placed(i, j);
      const vs = [];
      for (let k = 0; k < v.length; k += 3) vs.push(`<vertex x="${f(v[k])}" y="${f(v[k + 1])}" z="${f(v[k + 2])}"/>`);
      const ts = [];
      for (let k = 0; k < idx.length; k += 3) ts.push(`<triangle v1="${idx[k]}" v2="${idx[k + 1]}" v3="${idx[k + 2]}"/>`);
      const name = m.role === "inlay" ? T.parts.inlay : b.it.name;
      res.push(`<object id="${++id}" name="${name}" type="model"><mesh><vertices>${vs.join("")}</vertices><triangles>${ts.join("")}</triangles></mesh></object>`);
      return id;
    });
    if (ids.length === 1) { items.push(ids[0]); return; }
    res.push(`<object id="${++id}" name="${b.it.name}" type="model"><components>${ids.map((x) => `<component objectid="${x}"/>`).join("")}</components></object>`);
    items.push(id);
  });
  const xml = `<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>${res.join("")}</resources><build>${items.map((x) => `<item objectid="${x}"/>`).join("")}</build></model>`;
  const zip = zipSync({
    "[Content_Types].xml": strToU8('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'),
    "_rels/.rels": strToU8('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'),
    "3D/3dmodel.model": strToU8(xml),
  }, { level: 6 });
  return new Blob([zip], { type: "model/3mf" });
}

function fileName(ext) {
  const bits = [];
  if (state.lid === "1") bits.push(`lid-r${state.rib}-t${state.tab}-logo-${state.logo}`);
  if (state.frame === "1") bits.push(`frame-${state.frameKind}`);
  if (state.base === "1") bits.push(`base-${state.nut}-` + (state.sw === "shuttle" ? `shuttle-f${state.finger}-p${state.proud}` : `window-c${state.clr}`));
  return `skladen2-${bits.join("_")}.${ext}`;
}

function download(blob, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
}

// ---- panel ----------------------------------------------------------------
const panel = document.getElementById("panel");

function seg(name, values, labels) {
  return `<div class="seg" role="group">${values.map((v, i) =>
    `<button type="button" data-k="${name}" data-v="${v}" aria-pressed="${state[name] === v}">${labels ? labels[i] : v}</button>`).join("")}</div>`;
}
function row(label, body, hint) {
  return `<div class="row"><span class="lbl">${label}</span>${body}${hint ? `<p class="hint">${hint}</p>` : ""}</div>`;
}
function group(key, title, body) {
  return `<fieldset class="group ${state[key] === "1" ? "" : "off"}"><header><span>${title}</span>
    <label class="switch"><input type="checkbox" data-t="${key}" ${state[key] === "1" ? "checked" : ""} aria-label="${title}"><span></span></label></header>${body}</fieldset>`;
}

function renderPanel() {
  panel.innerHTML = `
    <a class="home" href="https://mitya-labs.github.io/${RU ? "" : "en/"}" target="_top">← ${T.home}</a>
    <h1>${T.title}<small>${T.sub}</small></h1>
    ${group("lid", T.lid,
      row(T.rib, seg("rib", OPTIONS.rib), T.ribHint) +
      row(T.tab, seg("tab", OPTIONS.tab), T.tabHint) +
      row(T.logo, seg("logo", ["none", "recess", "through"], [T.none, T.recess, T.through]), T.logoHint))}
    ${group("frame", T.frame,
      row(T.frameKind, seg("frameKind", ["closed", "open"], [T.closed, T.open]), T.frameHint))}
    ${group("base", T.base,
      row(T.nut, seg("nut", ["din934", "plain"], [T.din, T.plain])) +
      row(T.sw, seg("sw", ["window", "shuttle"], [T.window, T.shuttle])) +
      (state.sw === "shuttle"
        ? row(T.finger, seg("finger", OPTIONS.finger)) + row(T.proud, seg("proud", OPTIONS.proud), T.swHint)
        : row(T.clr, seg("clr", OPTIONS.clr))))}
    <div class="export">
      <strong>${T.summary}</strong>
      <ul class="summary" id="summary"></ul>
      <div class="buttons">
        <button class="btn" id="dl-stl" type="button">${T.stl}</button>
        <button class="btn alt" id="dl-3mf" type="button">${T.mf}</button>
      </div>
      <p class="hint">${T.stlNote}<br>${T.mfNote}</p>
    </div>`;
}

function renderSummary(items) {
  const ul = document.getElementById("summary");
  const lines = items.flatMap((it) => [it.label, ...(it.meshes.some((m) => m.role === "inlay") ? [T.parts.inlay] : [])]);
  ul.innerHTML = lines.length ? lines.map((l) => `<li>${l}</li>`).join("") : `<li>${T.empty}</li>`;
}

function sync() {
  try { history.replaceState(null, "", "#" + new URLSearchParams(state)); } catch { /* sandboxed iframe */ }
  renderPanel();
  refresh();
}

panel.addEventListener("click", (e) => {
  const b = e.target.closest("button[data-k]");
  if (b) { state[b.dataset.k] = b.dataset.v; sync(); return; }
  if (e.target.id === "dl-stl") download(stl(), fileName("stl"));
  if (e.target.id === "dl-3mf") download(threeMF(), fileName("3mf"));
});
panel.addEventListener("change", (e) => {
  const t = e.target.dataset.t;
  if (t) { state[t] = e.target.checked ? "1" : "0"; sync(); }
});

fetch(`${PARTS}manifest.json`).then((r) => r.json()).then((m) => { manifest = m; sync(); });
