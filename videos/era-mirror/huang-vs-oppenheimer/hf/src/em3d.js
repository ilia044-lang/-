// Era Mirror 3D reconstructions. Every scene is a pure function of time: make(canvas) -> render(t).
import * as THREE from "three";

function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const lerp = (a, b, t) => a + (b - a) * t;
const clamp01 = (t) => Math.max(0, Math.min(1, t));
const ease = (t) => { t = clamp01(t); return t * t * (3 - 2 * t); };
const easeOut = (t) => 1 - Math.pow(1 - clamp01(t), 3);

function base(canvas, bg) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: false });
  renderer.setPixelRatio(1);
  renderer.setSize(canvas.width, canvas.height, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.5;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(bg);
  const camera = new THREE.PerspectiveCamera(38, canvas.width / canvas.height, 0.1, 400);
  return { renderer, scene, camera };
}
const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.85, metalness: 0.05, ...o });
const glow = (color, opacity = 1) => new THREE.MeshBasicMaterial({ color, transparent: opacity < 1, opacity, depthWrite: false, blending: THREE.AdditiveBlending });
let _soft = null;
function softTex() {
  if (_soft) return _soft;
  const c = document.createElement("canvas"); c.width = c.height = 256;
  const g = c.getContext("2d"), gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.35, "rgba(255,255,255,0.45)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  _soft = new THREE.CanvasTexture(c); return _soft;
}
const soft = (color, opacity) => new THREE.MeshBasicMaterial({ color, map: softTex(), transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending });
function box(w, h, d, m, x = 0, y = 0, z = 0) {
  const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
  b.position.set(x, y, z);
  return b;
}
// camera path: keys = [{t, p:[x,y,z], l:[x,y,z]}], smooth between keys
function camAt(camera, keys, t) {
  let i = 0;
  while (i < keys.length - 2 && t > keys[i + 1].t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const k = b.t === a.t ? 0 : ease((t - a.t) / (b.t - a.t));
  camera.position.set(lerp(a.p[0], b.p[0], k), lerp(a.p[1], b.p[1], k), lerp(a.p[2], b.p[2], k));
  camera.lookAt(lerp(a.l[0], b.l[0], k), lerp(a.l[1], b.l[1], k), lerp(a.l[2], b.l[2], k));
  if (a.f || b.f) { camera.fov = lerp(a.f || 38, b.f || 38, k); camera.updateProjectionMatrix(); }
}

// ---------- 1943 night street: a parked car under one lit window ----------
function street(canvas, opt = {}) {
  const { renderer, scene, camera } = base(canvas, 0x05070c);
  scene.fog = new THREE.FogExp2(0x070a12, 0.028);
  const r = rng(1943);
  scene.add(new THREE.HemisphereLight(0x4a5a80, 0x0a0c12, 1.1));
  const moon = new THREE.DirectionalLight(0x7f95c8, 0.55); moon.position.set(-8, 14, 6); scene.add(moon);

  // road + sidewalks
  scene.add(box(120, 0.1, 14, mat(0x0c0e13, { roughness: 0.35, metalness: 0.3 }), 0, -0.05, 0));
  scene.add(box(120, 0.3, 5, mat(0x1a1c22), 0, 0.1, -9.5));
  scene.add(box(120, 0.3, 5, mat(0x1a1c22), 0, 0.1, 9.5));
  // wet reflections: soft streaks under lamps
  // row houses on the far side (z = -14), one hero house at x = 2
  const winDark = mat(0x07090d, { roughness: 0.9 });
  const houses = new THREE.Group(); scene.add(houses);
  let heroWin = null, heroGlow = null;
  for (let i = -7; i <= 7; i++) {
    const w = 7.2, h = 9 + Math.floor(r() * 3) * 1.6, x = i * 7.4;
    const tone = [0x23211f, 0x2a2622, 0x1f2226, 0x262220][Math.floor(r() * 4)];
    houses.add(box(w, h, 8, mat(tone), x, h / 2 + 0.25, -16));
    // cornice
    houses.add(box(w + 0.2, 0.35, 8.3, mat(0x15151a), x, h + 0.35, -16));
    // stoop
    houses.add(box(1.6, 0.9, 1.6, mat(0x17181c), x - 1.8, 0.7, -11.6));
    houses.add(box(1.1, 2.3, 0.15, mat(0x0c0d10), x - 1.8, 2.3, -11.95));
    for (let fy = 0; fy < 3; fy++) for (let fx = 0; fx < 3; fx++) {
      const wx = x - 2.1 + fx * 2.1, wy = 2.6 + fy * 2.7;
      if (fy === 0 && fx === 0) continue;
      const hero = i === 0 && fy === 1 && fx === 1;
      const lit = hero || (!opt.dark && r() < 0.03 && Math.abs(i) > 1);
      houses.add(box(1.25, 1.75, 0.2, mat(0x101116), wx, wy, -11.96));
      const pane = new THREE.Mesh(new THREE.PlaneGeometry(1.05, 1.55), lit ? new THREE.MeshBasicMaterial({ color: hero ? 0xffc46b : 0x8a6a3a }) : winDark);
      pane.position.set(wx, wy, -11.84); houses.add(pane);
      if (hero) {
        heroWin = pane;
        // curtain silhouette + cross frame
        houses.add(box(0.06, 1.55, 0.05, mat(0x1a1208), wx, wy, -11.8));
        houses.add(box(1.05, 0.06, 0.05, mat(0x1a1208), wx, wy + 0.1, -11.8));
        heroGlow = new THREE.Mesh(new THREE.PlaneGeometry(9, 9), soft(0xffa94a, 0.5));
        heroGlow.position.set(wx, wy, -11.7); houses.add(heroGlow);
        const wl = new THREE.PointLight(0xffb463, 26, 16, 1.8); wl.position.set(wx, wy, -10.6); scene.add(wl);
        houses.userData.heroLight = wl;
      }
    }
  }
  // street lamps with light pools
  for (const x of [-24, -9, 8, 24]) {
    scene.add(box(0.14, 5.4, 0.14, mat(0x0d0e12), x, 2.9, -7.4));
    scene.add(box(1.2, 0.1, 0.12, mat(0x0d0e12), x + 0.55, 5.55, -7.4));
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.2, 12, 12), new THREE.MeshBasicMaterial({ color: 0xfff0cf }));
    bulb.position.set(x + 1.1, 5.4, -7.4); scene.add(bulb);
    const halo = new THREE.Mesh(new THREE.PlaneGeometry(5, 5), soft(0xffd9a0, 0.55)); halo.position.copy(bulb.position); halo.position.z += 0.3; scene.add(halo);
    const pl = new THREE.PointLight(0xffd7a1, 70, 22, 1.7); pl.position.set(x + 1.1, 5.1, -7.2); scene.add(pl);
    const pool = new THREE.Mesh(new THREE.PlaneGeometry(11, 11), soft(0xffcf8f, 0.42));
    pool.rotation.x = -Math.PI / 2; pool.position.set(x + 1.1, 0.02, -6.6); scene.add(pool);
  }
  // the sedan (1940s silhouette), parked near side, facing +x
  const car = new THREE.Group(); scene.add(car); car.position.set(-3.2, 0, 5.2);
  const paint = mat(0x2c3442, { roughness: 0.38, metalness: 0.15 });
  const carRim = new THREE.PointLight(0x8fb0ff, 30, 12, 1.5); carRim.position.set(-6.5, 3.4, 9); scene.add(carRim);
  const carKey = new THREE.PointLight(0xffd7a1, 22, 11, 1.5); carKey.position.set(1.5, 3.4, 9.5); scene.add(carKey);
  const ell = (sx, sy, sz, m, x, y, z) => { const e = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), m); e.scale.set(sx, sy, sz); e.position.set(x, y, z); car.add(e); return e; };
  car.add(box(4.5, 0.5, 1.75, paint, 0, 0.72, 0));
  ell(1.55, 0.46, 0.86, paint, 1.45, 1.0, 0);   // hood
  ell(1.2, 0.5, 0.86, paint, -1.75, 0.98, 0);    // trunk
  const glass = new THREE.MeshStandardMaterial({ color: 0x06090f, roughness: 0.08, metalness: 0.5 });
  ell(1.32, 0.66, 0.85, paint, -0.3, 1.36, 0);   // cabin
  for (const sz of [0.8, -0.8]) { car.add(box(0.72, 0.36, 0.14, glass, 0.18, 1.52, sz)); car.add(box(0.62, 0.36, 0.14, glass, -0.72, 1.52, sz)); }
  const ws = box(0.1, 0.4, 1.2, glass, 0.86, 1.5, 0); ws.rotation.z = -0.5; car.add(ws);
  for (const [fx, fz] of [[1.5, 0.92], [1.5, -0.92], [-1.5, 0.92], [-1.5, -0.92]]) {
    const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.26, 24), mat(0x050506, { roughness: 0.6 }));
    wh.rotation.x = Math.PI / 2; wh.position.set(fx, 0.42, fz); car.add(wh);
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.28, 16), mat(0xa9afb8, { metalness: 0.8, roughness: 0.3 }));
    hub.rotation.x = Math.PI / 2; hub.position.set(fx, 0.42, fz); car.add(hub);
    ell(0.72, 0.42, 0.3, paint, fx, 0.74, fz);
  }
  car.add(box(0.12, 0.12, 1.9, mat(0xb9bec6, { metalness: 0.9, roughness: 0.3 }), 2.75, 0.55, 0));
  car.add(box(0.12, 0.12, 1.9, mat(0xb9bec6, { metalness: 0.9, roughness: 0.3 }), -2.75, 0.55, 0));
  for (const hz of [0.6, -0.6]) { const hl = new THREE.Mesh(new THREE.SphereGeometry(0.16, 14, 14), mat(0x6f757d, { metalness: 0.7, roughness: 0.25 })); hl.position.set(2.72, 0.98, hz); car.add(hl); }
  const ember = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 8), new THREE.MeshBasicMaterial({ color: 0xff5a1f })); ember.position.set(0.3, 1.5, 0.9); car.add(ember);
  const emberGlow = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.1), soft(0xff5a1f, 0.6)); emberGlow.rotation.y = 0.5; emberGlow.position.copy(ember.position); car.add(emberGlow);
  // drifting mist cards
  const mist = [];
  for (let i = 0; i < 14; i++) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(34, 7), soft(0x6f7f9c, 0.07));
    m.position.set(-40 + r() * 80, 1.2 + r() * 2.5, -8 + r() * 12); m.userData = { x: m.position.x, s: 0.25 + r() * 0.5 }; scene.add(m); mist.push(m);
  }
  const sky = new THREE.Color();
  return (t, o = {}) => {
    const dawn = clamp01(o.dawn || 0);
    sky.setRGB(lerp(0.02, 0.36, dawn), lerp(0.027, 0.3, dawn), lerp(0.047, 0.34, dawn));
    scene.background = sky; scene.fog.color.copy(sky); scene.fog.density = lerp(0.028, 0.02, dawn);
    moon.intensity = lerp(0.55, 1.5, dawn); moon.color.setRGB(lerp(0.5, 1, dawn), lerp(0.58, 0.8, dawn), lerp(0.78, 0.66, dawn));
    const flick = 0.55 + 0.45 * Math.max(0, Math.sin(t * 0.9)) ** 6; // slow drags on the cigarette
    emberGlow.material.opacity = 0.12 + 0.4 * flick; ember.scale.setScalar(0.8 + flick * 0.7);
    const winOn = o.windowOff != null ? 1 - clamp01((t - o.windowOff) / 0.25) : 1;
    heroWin.material.color.setRGB(lerp(0.04, 1, winOn), lerp(0.047, 0.77, winOn), lerp(0.07, 0.42, winOn));
    heroGlow.material.opacity = 0.5 * winOn; houses.userData.heroLight.intensity = 26 * winOn;
    for (const m of mist) m.position.x = m.userData.x + t * m.userData.s;
    camAt(camera, o.cam, t);
    renderer.render(scene, camera);
  };
}

// ---------- 1954 hearing room (Building T-3 was a temporary office: plain, no courtroom fittings) ----------
function room(canvas) {
  const { renderer, scene, camera } = base(canvas, 0x0b0907);
  scene.fog = new THREE.FogExp2(0x0d0a07, 0.03);
  scene.add(new THREE.HemisphereLight(0x8a7a62, 0x120d08, 0.5));
  const wallM = mat(0x4a4234), floorM = mat(0x2a2118, { roughness: 0.55 }), wood = mat(0x4a2f1b, { roughness: 0.5 }), dark = mat(0x16120e);
  scene.add(box(22, 0.1, 16, floorM, 0, -0.05, 0));
  scene.add(box(22, 7, 0.2, wallM, 0, 3.5, -8));
  scene.add(box(0.2, 7, 16, wallM, -11, 3.5, 0));
  scene.add(box(0.2, 7, 16, wallM, 11, 3.5, 0));
  scene.add(box(22, 0.2, 16, mat(0x2b261f), 0, 7, 0));
  // tall windows with blinds on the left wall, light shafts
  for (const z of [-4.5, 0, 4.5]) {
    const pane = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 4), new THREE.MeshBasicMaterial({ color: 0xf2dcae }));
    pane.rotation.y = Math.PI / 2; pane.position.set(-10.88, 3.7, z); scene.add(pane);
    for (let i = 0; i < 13; i++) scene.add(box(0.06, 0.16, 2.7, dark, -10.8, 1.85 + i * 0.31, z));
    const shaft = new THREE.Mesh(new THREE.PlaneGeometry(13, 5), soft(0xffd9a0, 0.16));
    shaft.position.set(-6.4, 2.2, z); shaft.rotation.set(0, 0, -0.42); scene.add(shaft);
    const sl = new THREE.SpotLight(0xffd7a0, 120, 22, 0.5, 0.7, 1.4); sl.position.set(-10.5, 5, z); sl.target.position.set(-1, 0, z * 0.6); scene.add(sl, sl.target);
  }
  const key = new THREE.PointLight(0xffe2b8, 40, 18, 1.6); key.position.set(0, 6.2, 0); scene.add(key);
  // the board's long table at the back (T shape head), three chairs behind it
  scene.add(box(8.5, 0.14, 1.7, wood, 0, 1.5, -5.2));
  for (const x of [-4, 4]) scene.add(box(0.14, 1.5, 1.5, wood, x, 0.75, -5.2));
  const figure = (x, z, rot, color = 0x070605) => {
    const g = new THREE.Group(); const m = new THREE.MeshStandardMaterial({ color, roughness: 0.9 });
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.34, 0.62, 6, 14), m); torso.position.y = 1.72; g.add(torso);
    const hd = new THREE.Mesh(new THREE.SphereGeometry(0.21, 16, 16), m); hd.position.y = 2.5; g.add(hd);
    const sh = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.72, 4, 10), m); sh.rotation.z = Math.PI / 2; sh.position.y = 2.06; g.add(sh);
    g.add(box(0.75, 0.1, 0.75, dark, 0, 1.0, 0)); g.add(box(0.75, 1.1, 0.1, dark, 0, 1.6, -0.36));
    for (const [lx, lz] of [[-0.3, -0.3], [0.3, -0.3], [-0.3, 0.3], [0.3, 0.3]]) g.add(box(0.07, 1.0, 0.07, dark, lx, 0.5, lz));
    g.position.set(x, 0, z); g.rotation.y = rot; scene.add(g); return g;
  };
  for (const x of [-2.6, 0, 2.6]) figure(x, -6.3, 0);
  // counsel tables facing each other, left = prosecution, right = defense
  scene.add(box(1.6, 0.12, 5.4, wood, -4.6, 1.4, 0.4)); scene.add(box(1.6, 0.12, 5.4, wood, 4.6, 1.4, 0.4));
  for (const z of [-1.2, 1.6]) { figure(-5.9, z, Math.PI / 2); figure(5.9, z, -Math.PI / 2); }
  // witness chair in the middle, facing the board; leather sofa behind it against the back area
  const witness = figure(0, -1.2, Math.PI, 0x070605);
  const sofa = new THREE.Group(); scene.add(sofa); sofa.position.set(0, 0, 4.6);
  const leather = mat(0x3b2415, { roughness: 0.42 });
  sofa.add(box(3.6, 0.5, 1.2, leather, 0, 0.6, 0)); sofa.add(box(3.6, 0.9, 0.3, leather, 0, 1.2, 0.5));
  sofa.add(box(0.3, 0.75, 1.2, leather, -1.8, 0.9, 0)); sofa.add(box(0.3, 0.75, 1.2, leather, 1.8, 0.9, 0));
  // papers + stenotype
  const paper = new THREE.MeshStandardMaterial({ color: 0xe9dfc8, roughness: 0.9 });
  const r = rng(54);
  for (let i = 0; i < 16; i++) { const p = box(0.5, 0.012 + r() * 0.05, 0.66, paper, -3.6 + r() * 7.2, 1.6, -5.6 + r() * 0.8); p.rotation.y = (r() - 0.5) * 0.6; scene.add(p); }
  for (let i = 0; i < 9; i++) { const p = box(0.5, 0.02 + r() * 0.25, 0.66, paper, -4.9 + r() * 0.6, 1.5, -1.6 + r() * 4); p.rotation.y = (r() - 0.5) * 0.5; scene.add(p); }
  scene.add(box(0.6, 0.02, 0.8, paper, 4.5, 1.48, 0.2));
  // dust motes in the shafts
  const dust = new THREE.Group(); scene.add(dust);
  for (let i = 0; i < 90; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(0.018, 6, 6), glow(0xffe0b0, 0.5)); d.position.set(-9 + r() * 9, 0.6 + r() * 4.6, -6 + r() * 12); d.userData = { y: d.position.y, s: 0.05 + r() * 0.1, p: r() * 6 }; dust.add(d); }
  const doorM = mat(0x2d2218);
  scene.add(box(2.0, 4.2, 0.12, doorM, 7.5, 2.1, -7.86));
  return (t, o = {}) => {
    for (const d of dust.children) d.position.y = d.userData.y + Math.sin(t * d.userData.s * 4 + d.userData.p) * 0.3;
    key.intensity = o.dim != null ? lerp(40, 9, clamp01(o.dim)) : 40;
    camAt(camera, o.cam, t);
    renderer.render(scene, camera);
  };
}

// ---------- 2026 chip: one die, camera dives into it ----------
function chip(canvas) {
  const { renderer, scene, camera } = base(canvas, 0x02060a);
  scene.fog = new THREE.FogExp2(0x02060a, 0.035);
  scene.add(new THREE.HemisphereLight(0x3c6f86, 0x020406, 0.6));
  const keyL = new THREE.DirectionalLight(0xffe2bd, 1.6); keyL.position.set(6, 9, 4); scene.add(keyL);
  const rim = new THREE.DirectionalLight(0x49d1ff, 1.4); rim.position.set(-7, 4, -6); scene.add(rim);
  const r = rng(2026);
  // board
  scene.add(box(40, 0.3, 40, mat(0x06141a, { roughness: 0.6, metalness: 0.2 }), 0, -0.4, 0));
  const traces = new THREE.Group(); scene.add(traces);
  for (let i = 0; i < 70; i++) {
    const horiz = r() < 0.5, len = 3 + r() * 12;
    const tr = box(horiz ? len : 0.05, 0.02, horiz ? 0.05 : len, new THREE.MeshBasicMaterial({ color: 0x0f4a5c }), -18 + r() * 36, -0.23, -18 + r() * 36);
    traces.add(tr);
  }
  // package + die
  const pkg = box(9, 0.5, 9, mat(0x0d1a20, { roughness: 0.5, metalness: 0.5 }), 0, 0, 0); scene.add(pkg);
  const lid = box(6.4, 0.25, 6.4, mat(0x8f999f, { roughness: 0.46, metalness: 0.9 }), 0, 0.38, 0); scene.add(lid);
  const die = new THREE.Group(); scene.add(die); die.position.y = 0.52;
  const cells = [];
  for (let ix = 0; ix < 14; ix++) for (let iz = 0; iz < 14; iz++) {
    const h = 0.03 + r() * 0.12;
    const c = box(0.36, h, 0.36, new THREE.MeshStandardMaterial({ color: 0x0c2b36, emissive: 0x1fb6e8, emissiveIntensity: 0, roughness: 0.4, metalness: 0.6 }), -2.73 + ix * 0.42, h / 2, -2.73 + iz * 0.42);
    c.userData = { ph: r() * 6.28, d: Math.hypot(ix - 6.5, iz - 6.5) }; die.add(c); cells.push(c);
  }
  // pins around the package
  for (let i = 0; i < 40; i++) for (const s of [-1, 1]) {
    scene.add(box(0.1, 0.1, 0.5, mat(0xc9a24a, { metalness: 1, roughness: 0.35 }), -4.4 + i * 0.225, -0.22, s * 4.75));
    scene.add(box(0.5, 0.1, 0.1, mat(0xc9a24a, { metalness: 1, roughness: 0.35 }), s * 4.75, -0.22, -4.4 + i * 0.225));
  }
  return (t, o = {}) => {
    const open = ease((t - (o.open || 1.2)) / 1.4);
    lid.position.y = 0.38 + open * 5; lid.rotation.z = open * 0.35; lid.position.x = open * 16;
    for (const c of cells) {
      const wave = Math.max(0, Math.sin(t * 1.6 - c.userData.d * 0.55 + c.userData.ph * 0.15));
      c.material.emissiveIntensity = open * (0.08 + 0.75 * wave * wave);
    }
    camAt(camera, o.cam, t);
    renderer.render(scene, camera);
  };
}

// ---------- the closed door ----------
function door(canvas) {
  const { renderer, scene, camera } = base(canvas, 0x040506);
  scene.fog = new THREE.FogExp2(0x040506, 0.05);
  scene.add(new THREE.HemisphereLight(0x55606f, 0x0a0a0c, 1.4));
  const wall = mat(0x2c3037), floor = mat(0x0e0f12, { roughness: 0.3, metalness: 0.4 });
  scene.add(box(30, 0.1, 30, floor, 0, -0.05, 6));
  scene.add(box(13, 9, 0.4, wall, -8.5, 4.5, 0)); scene.add(box(13, 9, 0.4, wall, 8.5, 4.5, 0)); scene.add(box(4, 4, 0.4, wall, 0, 7, 0));
  const dm = mat(0x4a3424, { roughness: 0.5 });
  const d = box(3.9, 4.95, 0.18, dm, 0, 2.5, 0.02); scene.add(d);
  for (const [x, y] of [[-0.9, 3.6], [0.9, 3.6], [-0.9, 1.4], [0.9, 1.4]]) scene.add(box(1.4, 1.6, 0.06, mat(0x5a402c), x, y, 0.13));
  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 16), mat(0xb89a5a, { metalness: 1, roughness: 0.3 })); knob.position.set(1.55, 2.4, 0.22); scene.add(knob);
  // light leaking under and around the door
  const leak = new THREE.Mesh(new THREE.PlaneGeometry(3.9, 0.06), new THREE.MeshBasicMaterial({ color: 0xfff1cf })); leak.position.set(0, 0.03, 0.12); scene.add(leak);
  const spill = new THREE.Mesh(new THREE.PlaneGeometry(8, 8), soft(0xffd79a, 0.5)); spill.rotation.x = -Math.PI / 2; spill.position.set(0, 0.02, 2.6); scene.add(spill);
  const sl = new THREE.PointLight(0xffd7a0, 16, 9, 1.8); sl.position.set(0, 0.3, 1.2); scene.add(sl);
  const top = new THREE.SpotLight(0xa9c4ff, 420, 30, 0.5, 0.8, 1.3); top.position.set(0, 8.5, 6); top.target.position.set(0, 2.4, 0); scene.add(top, top.target);
  return (t, o = {}) => {
    const breathe = 0.85 + 0.15 * Math.sin(t * 0.7);
    spill.material.opacity = 0.5 * breathe; sl.intensity = 16 * breathe;
    camAt(camera, o.cam, t);
    renderer.render(scene, camera);
  };
}

window.EM3D = { street, room, chip, door };
