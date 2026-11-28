'use strict';
// CriterAI intro film. Every style is computed from time inside seek(t): no CSS transitions, no timers,
// no state carried between frames, so any frame renders the same way on its own.
(() => {
const DUR = 20.0;
const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------- timing (single source of truth)
const T = {
  // B1 hook
  swap2: 0.95, swap3: 1.90, rowsB: 0.95, rowsC: 1.90, accel: 1.90, conv: 2.56, dot: 2.86,
  // B2 turn
  check: 3.08, bloom: 3.13, ring: 3.32, markMove: 3.78, pill: 3.80, sendIn: 4.02, placeholder: 4.06,
  // B3 ask
  type: 4.44, curIn: 4.66, curPark: 5.12, press1: 5.27,
  // B4 answer
  morph: 5.36, tag: 5.72, title: 5.80, rows: 5.96, verifyIn: 6.42, composer2: 6.02,
  // B5 verify
  curGo: 7.42, push: 7.45, press2: 8.10, review: 8.18, ring2: 8.42, pull: 8.45, checks: 9.14, verified: 9.60, sweep: 10.35,
  // B6 payoff
  recede: 11.80, pay1: 12.00, pay2: 12.96, pay3: 13.90, stack: 14.70,
  // B7 brand + CTA
  carry: 15.98, aiMove: 16.08, aiSwap: 16.42, criter: 16.44, lring: 16.66, lcheck: 16.90, cta: 17.36, url: 17.46,
  cur3In: 18.12, press3: 18.72, shine: 19.25, mascot: 18.20,
};
const USE_MASCOT = new URLSearchParams(location.search).get('mascot') === '1'; // optional variant

// ---------------------------------------------------------------- math
const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const smooth = (x) => x * x * (3 - 2 * x);
function bez(x1, y1, x2, y2) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = (t) => ((ax * t + bx) * t + cx) * t;
  const sy = (t) => ((ay * t + by) * t + cy) * t;
  const dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
  return (x) => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 8; i++) {
      const e = sx(t) - x, d = dx(t);
      if (Math.abs(e) < 1e-7 || Math.abs(d) < 1e-7) break;
      t -= e / d;
    }
    if (!(t >= 0 && t <= 1) || Math.abs(sx(t) - x) > 1e-5) {
      let lo = 0, hi = 1; t = x;
      for (let i = 0; i < 40; i++) { if (sx(t) < x) lo = t; else hi = t; t = (lo + hi) / 2; }
    }
    return sy(t);
  };
}
// cubic-beziers from the Ozen skill (craft.md section 3)
const E = {
  linear: (x) => x,
  glide: bez(0.40, 0.67, 0.76, 1.00),
  softInOut: bez(0.35, 0.06, 0.65, 0.94),
  softLand: bez(0.28, 1.00, 0.72, 0.93),
  snapSettle: bez(0.14, 1.00, 0.24, 0.95),
  whip: bez(0.28, 0.67, 0.50, 1.00),
  gentleIn: bez(0.58, 0.00, 0.96, 0.95),
  accelExit: bez(0.40, 0.00, 0.67, 0.16),
  crashOut: bez(0.56, 0.00, 0.71, 0.00),
  popOver: bez(0.29, 0.12, 0.29, 1.41),
};
const tw = (t, t0, t1, a, b, e = E.glide) => lerp(a, b, e(inv(t0, t1, t)));
// closed-form damped spring step response (0 -> 1)
function stepR(tau, w, z) {
  if (tau <= 0) return 0;
  if (z >= 1) { const x = w * tau; return 1 - Math.exp(-x) * (1 + x); }
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * tau) * (Math.cos(wd * tau) + ((z * w) / wd) * Math.sin(wd * tau));
}
class Track { // many target changes = a sum of one spring per change
  constructor(v0) { this.v0 = v0; this.cur = v0; this.ev = []; }
  to(t, v, w = 14, z = 1) { if (v !== this.cur) { this.ev.push([t, v - this.cur, w, z]); this.cur = v; } return this; }
  at(t) { let v = this.v0; for (const [ti, d, w, z] of this.ev) v += d * stepR(t - ti, w, z); return v; }
}
const mixHex = (a, b, k) => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], k))).join(',')})`;
};
const px = (v) => `${v.toFixed(2)}px`;
const blurF = (b) => (b > 0.12 ? `blur(${b.toFixed(2)}px)` : 'none');
const disp = (el, on) => { const d = on ? '' : 'none'; if (el.style.display !== d) el.style.display = d; };
// entrance/exit helper: rises in from below with a blur, exits short and early upwards
function vis(t, tin, dur = 0.36, tout = null, dOut = 0.2, rise = 40, blur = 14) {
  const e = E.softLand(inv(tin, tin + dur, t));
  let o = smooth(inv(tin, tin + dur * 0.45, t)), b = (1 - e) * blur, dy = (1 - e) * rise;
  if (tout != null) { const x = E.accelExit(inv(tout, tout + dOut, t)); o *= 1 - x; b += x * blur; dy -= x * rise * 0.9; }
  return { o, b, dy, e };
}

// ---------------------------------------------------------------- elements
const el = {};
['stage', 'hookwrap', 'hook', 'dot', 'bloom', 'bloomring', 'checkglow', 'markhost', 'worldwrap', 'world', 'mark', 'ringPath', 'checkPath',
 'card', 'composer2', 'bubble', 'placeholder', 'caret', 'qtext', 'send', 'tag', 'atitle', 'rows', 'verify', 'vface1', 'vface2', 'vface3',
 'vringArc', 'vmark', 'sweep', 'pay1', 'pay2', 'pay3', 'pay3ai', 'pay3rest', 'payAI', 'lockup', 'lRingPath', 'lCheckPath', 'lCriterRect',
 'lCriterImg', 'lAiImg', 'lRingImg', 'lCheckImg', 'cta', 'ctaArrow', 'ctaCheck', 'ctaCheckPath', 'url', 'mascot', 'cursor', 'grain', 'ground-glow'].forEach((k) => { el[k] = $(k); });

// ---------------------------------------------------------------- hook content (the site's own marquee items)
const SETS = {
  A: ['Subclass 189 - Skilled Independent', 'Subclass 190 - Skilled Nominated', 'Subclass 491 - Skilled Work Regional', 'Subclass 500 - Student Visa',
      'Subclass 485 - Temporary Graduate', 'Subclass 482 - Skills in Demand', 'Subclass 186 - Employer Nomination Scheme', 'Subclass 820/801 - Partner Visa',
      'Subclass 600 - Visitor Visa', 'Subclass 407 - Training Visa', 'Subclass 462 - Work & Holiday', 'Subclass 408 - Temporary Activity'],
  B: ['CV', 'Enrolment letter', 'Skills assessment', 'IELTS test', 'Medical exams', 'Police clearances', 'State sponsorship', 'Partner points',
      'Work experience', 'English test scores'],
  C: ['Points-test calculation', 'EOI', 'State nomination', 'Invitation rounds', 'Refusal risk', 'Section 56 request', 'Genuine Student', 'Lodgement'],
};
const CLS = { A: 'pill', B: 'pill doc', C: 'pill next' };
// [y, depth (0 far, 1 mid, 2 near), dir, speed px/s, set, entrance time (-1 = from the start), label phase]
const ROWS = [
  [150, 0, +1, 55, 'A', -1, 0], [300, 2, -1, 120, 'A', -1, 3], [830, 1, +1, 85, 'A', -1, 6], [975, 0, -1, 50, 'A', -1, 9],
  [222, 1, -1, 100, 'B', T.rowsB, 2], [745, 2, +1, 140, 'B', T.rowsB, 5], [905, 2, -1, 130, 'B', T.rowsB + 0.08, 1],
  [72, 1, +1, 115, 'C', T.rowsC, 4], [395, 0, -1, 75, 'C', T.rowsC, 7], [680, 0, +1, 85, 'C', T.rowsC + 0.07, 2], [1028, 1, -1, 110, 'C', T.rowsC + 0.1, 0],
];
const DEPTH = [{ s: 0.74, b: 3.0, o: 0.34 }, { s: 0.92, b: 1.1, o: 0.6 }, { s: 1.12, b: 0, o: 0.92 }];
const rows = [];

// ---------------------------------------------------------------- answer rows
const ANSWER = ['Confirmation of Enrolment (CoE)', 'Genuine Student requirement', 'Evidence of funds', 'Overseas Student Health Cover'];
const answerRows = [];

// ---------------------------------------------------------------- geometry
// Mark: viewBox centre = ring centre (339, 332.5) of the 2000x667 lockup. D = displayed box size (520 units).
const MARK_SRC_C = [339, 332.5];
const markPt = (cx, cy, D, sx, sy) => [cx + ((sx - MARK_SRC_C[0]) * D) / 520, cy + ((sy - MARK_SRC_C[1]) * D) / 520];
const CHECK_START = [283, 305];
const TURN_D = 360;
const ICON = { x: 404, y: 540, D: 96 };
const AVATAR = { x: 462, y: 300, D: 92 };
const PILL = { l: 330, r: 1590, t: 478, b: 602 };
const CARD = { l: 410, r: 1510, t: 90, b: 990 };
const SEND_C = [1536, 540];
const QX = 470; // composer text left
const COL = 540; // answer column left
const ROW_Y0 = 400, ROW_DY = 76;
const VERIFY = { x: COL, y: 728, h: 82 };
const LOCK = { x: 462.5, y: 303.75, s: 0.5 }; // lockup canvas placement (visible logo centred at 960, 470)
const LOCK_AI = { cx: LOCK.x + 1673.5 * LOCK.s, cy: LOCK.y + 352.5 * LOCK.s, cap: 261 * LOCK.s };
const GROUP_C = [960, 548]; // end-card creep centre

// typing bursts (characters per 1/30 s): irregular, as the skill asks
const QUESTION = 'What do I need for my student visa?';
const BURSTS = [3, 2, 0, 3, 4, 1, 0, 3, 2, 3, 0, 2, 4, 3, 0, 2, 3];
const TYPE_END = T.type + BURSTS.length / 30;
const typedCount = (t) => {
  if (t < T.type) return 0;
  const f = Math.floor((t - T.type) * 30);
  let n = 0;
  for (let i = 0; i <= Math.min(f, BURSTS.length - 1); i++) n += BURSTS[i];
  return Math.min(n, QUESTION.length);
};

// measured at build time
const M = {};

// ---------------------------------------------------------------- camera
function camAt(t) {
  // log-zoom keyframes with per-segment eases
  const zk = [[0, 1], [4.16, 1], [T.press1 - 0.02, 1.17, E.softInOut], [T.morph + 0.02, 1.17], [T.morph + 0.62, 1.0, E.glide], [5.9, 1.0], [T.push, 1.03, E.linear], [T.push + 0.57, 1.16, E.glide], [T.pull, 1.16], [T.pull + 0.6, 1.0, E.softInOut], [T.recede, 1.04, E.linear]];
  const xk = [[0, 960], [T.push, 960], [T.push + 0.57, 790, E.glide], [T.pull, 790], [T.pull + 0.6, 960, E.softInOut], [T.recede, 945, E.linear]];
  const yk = [[0, 540], [5.9, 540], [T.push, 548, E.linear], [T.push + 0.57, 690, E.glide], [T.pull, 690], [T.pull + 0.6, 560, E.softInOut], [T.recede, 575, E.linear]];
  const kf = (keys, log) => {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [t1, v1, e] = keys[i];
      if (t <= t1) {
        const [t0, v0] = keys[i - 1];
        const k = (e || E.glide)(inv(t0, t1, t));
        return log ? Math.exp(lerp(Math.log(v0), Math.log(v1), k)) : lerp(v0, v1, k);
      }
    }
    return keys[keys.length - 1][1];
  };
  return { z: kf(zk, true), x: kf(xk), y: kf(yk) };
}
const toScreen = (c, wx, wy) => [960 + (wx - c.x) * c.z, 540 + (wy - c.y) * c.z];

// ---------------------------------------------------------------- build
function build() {
  // hook pills
  for (const [y, depth, dir, speed, set, tIn, phase] of ROWS) {
    const labels = SETS[set];
    const d = DEPTH[depth];
    const row = { y, depth, dir, speed, tIn, pills: [] };
    let x = 0, i = phase;
    const target = 2700 / d.s;
    while (x < target) {
      const p = document.createElement('div');
      p.className = CLS[set];
      p.innerHTML = `<i></i>${labels[i % labels.length]}`;
      el.hook.appendChild(p);
      const w = p.offsetWidth;
      row.pills.push({ el: p, cx: x + w / 2, w, k: ((i * 7919) % 13) / 13 });
      x += w + 22; i++;
    }
    row.x0 = dir > 0 ? -650 : -100;
    rows.push(row);
  }
  // answer rows
  ANSWER.forEach((txt, i) => {
    const r = document.createElement('div');
    r.className = 'row';
    r.innerHTML = `<div class="hl"></div><div class="num"><div class="fill"></div><b>${i + 1}</b>` +
      `<svg viewBox="0 0 30 30"><path d="M7.5 15.5 L12.8 20.8 L22.8 9.6" fill="none" stroke="#164f4d" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg></div>` +
      `<div class="txt">${txt}</div>`;
    el.rows.appendChild(r);
    const o = { el: r, hl: r.querySelector('.hl'), fill: r.querySelector('.fill'), b: r.querySelector('b'), path: r.querySelector('path') };
    o.len = o.path.getTotalLength();
    answerRows.push(o);
  });
  // measurements
  el.qtext.textContent = QUESTION;
  M.qW = el.qtext.offsetWidth; M.qH = el.qtext.offsetHeight;
  const cw = [];
  for (let n = 0; n <= QUESTION.length; n++) { el.qtext.textContent = QUESTION.slice(0, n); cw.push(el.qtext.offsetWidth); }
  M.caretX = cw;
  M.ring = el.ringPath.getTotalLength();
  M.check = el.checkPath.getTotalLength();
  M.lring = el.lRingPath.getTotalLength();
  M.lcheck = el.lCheckPath.getTotalLength();
  M.vW1 = el.vface1.offsetWidth; M.vW2 = el.vface2.offsetWidth; M.vW3 = el.vface3.offsetWidth;
  M.rowW = Math.max(...answerRows.map((r) => r.el.offsetWidth));
  el.vringArc.style.strokeDasharray = `${2 * Math.PI * 18}`;
  // payoff "AI" position at rest
  el.pay3.style.transform = 'translate(-50%, -50%)';
  const st = el.stage.getBoundingClientRect();
  const ra = el.pay3ai.getBoundingClientRect();
  M.aiRect = { x: ra.left - st.left, y: ra.top - st.top, w: ra.width, h: ra.height };
  el.payAI.style.transform = 'none';
  M.aiW = el.payAI.offsetWidth; M.aiH = el.payAI.offsetHeight;
  M.ctaW = el.cta.offsetWidth; M.ctaH = el.cta.offsetHeight; M.urlW = el.url.offsetWidth; M.urlH = el.url.offsetHeight;
  M.payW = [el.pay1.offsetWidth, el.pay2.offsetWidth, el.pay3.offsetWidth];
  M.ctaCheck = el.ctaCheckPath.getTotalLength();
}

// ---------------------------------------------------------------- B1 hook
const hookZoomEnd = 1.06;
function hookTarget() { // the check's first point, in hook-local coordinates
  const [sx, sy] = markPt(960, 540, TURN_D, CHECK_START[0], CHECK_START[1]);
  return [960 + (sx - 960) / hookZoomEnd, 540 + (sy - 540) / hookZoomEnd];
}
function sceneHook(t) {
  const on = t < 3.52;
  disp(el.hookwrap, on);
  if (!on) return;
  const zoom = 1 + (hookZoomEnd - 1) * E.softInOut(inv(0, T.conv + 0.3, t));
  el.hook.style.transform = `scale(${zoom.toFixed(5)})`;
  const [TX, TY] = hookTarget();
  const acc = Math.max(0, t - T.accel);
  for (const r of rows) {
    const d = DEPTH[r.depth];
    const shift = r.dir * r.speed * (t + 0.62 * acc * acc);
    let ent = 1, entX = 0;
    if (r.tIn > 0) { ent = E.softLand(inv(r.tIn, r.tIn + 0.42, t)); entX = -r.dir * (1 - ent) * 460; }
    for (const p of r.pills) {
      let x = r.x0 + p.cx * d.s + shift + entX, y = r.y;
      let sc = d.s, b = d.b + (1 - ent) * 9, o = d.o * smooth(ent);
      const c0 = T.conv + p.k * 0.07;
      const c = E.crashOut(inv(c0, c0 + 0.44, t));
      if (c > 0) {
        x = lerp(x, TX, c); y = lerp(y, TY, c);
        sc *= 1 - 0.96 * c;
        b += 12 * Math.sin(Math.PI * c);
        o *= 1 - smooth(inv(0.72, 1, c));
      }
      const vis_ = o > 0.01 && x > -600 && x < 2520;
      disp(p.el, vis_);
      if (!vis_) continue;
      p.el.style.transform = `translate(${px(x - p.w / 2)}, ${px(y - 32)}) scale(${sc.toFixed(4)})`;
      p.el.style.opacity = o.toFixed(3);
      p.el.style.filter = blurF(b);
    }
  }
  // the three questions, one slot, rising
  const lines = [[$('hl1'), -0.18, T.swap2], [$('hl2'), T.swap2 + 0.04, T.swap3], [$('hl3'), T.swap3 + 0.04, null]];
  for (const [e, tin, tout] of lines) {
    const v = vis(t, tin, 0.36, tout, 0.2, 64, 16);
    let x = 960, y = 540 + v.dy, sc = 1, o = v.o, b = v.b;
    if (tout == null) { // the last line is pulled into the point
      const c = E.crashOut(inv(T.conv + 0.06, T.conv + 0.46, t));
      x = lerp(960, TX, c); y = lerp(y, TY, c); sc = 1 - 0.97 * c; b += 10 * c; o *= 1 - smooth(inv(0.55, 0.92, c));
    }
    disp(e, o > 0.005);
    e.style.transform = `translate(-50%, -50%) translate(${px(x - 960)}, ${px(y - 540)}) scale(${sc.toFixed(4)})`;
    e.style.opacity = o.toFixed(3);
    e.style.filter = blurF(b);
  }
  // the gold point the noise collapses into
  const dIn = E.snapSettle(inv(T.dot, T.dot + 0.18, t)), dOut = inv(T.check + 0.02, T.check + 0.12, t);
  const [SX, SY] = markPt(960, 540, TURN_D, CHECK_START[0], CHECK_START[1]);
  disp(el.dot, dIn > 0 && dOut < 1);
  el.dot.style.transform = `translate(${px(SX)}, ${px(SY)}) scale(${(dIn * (1 + 0.6 * dOut)).toFixed(3)})`;
  el.dot.style.opacity = (1 - dOut).toFixed(3);
}

// ---------------------------------------------------------------- B2 turn: check, bloom, ring
function markState(t) {
  // position + size of the travelling mark (world space; the camera is identity until 5.9 s)
  if (t < T.markMove) {
    const creep = 1 + 0.035 * inv(T.check, T.markMove, t);
    return { x: 960, y: 540, D: TURN_D * creep };
  }
  if (t < T.morph + 0.04) {
    const k = E.glide(inv(T.markMove, T.markMove + 0.42, t));
    const D0 = TURN_D * 1.035;
    return { x: lerp(960, ICON.x, k), y: 540, D: Math.exp(lerp(Math.log(D0), Math.log(ICON.D), E.whip(inv(T.markMove, T.markMove + 0.38, t)))) };
  }
  const k = E.glide(inv(T.morph + 0.04, T.morph + 0.5, t));
  const arc = Math.sin(Math.PI * k) * -30;
  return { x: lerp(ICON.x, AVATAR.x, k) + arc * 0.3, y: lerp(ICON.y, AVATAR.y, k), D: lerp(ICON.D, AVATAR.D, k) };
}
function sceneTurn(t) {
  // bloom: the light from the check becomes the cream ground
  const br = 1260 * E.glide(inv(T.bloom, T.bloom + 0.37, t));
  const bOn = t > T.bloom && t < 3.52;
  disp(el.bloom, bOn); disp(el.bloomring, bOn);
  if (bOn) {
    for (const [e, r, o] of [[el.bloom, br, 1], [el.bloomring, br * 1.01, 1 - inv(T.bloom + 0.2, T.bloom + 0.37, t)]]) {
      e.style.width = e.style.height = px(2 * r);
      e.style.transform = `translate(${px(960 - r)}, ${px(540 - r)})`;
      e.style.opacity = o.toFixed(3);
    }
  }
  // gold glow behind the check
  const g = inv(T.check, T.check + 0.12, t) * (1 - inv(T.check + 0.25, T.check + 0.75, t));
  disp(el.checkglow, g > 0.003);
  el.checkglow.style.transform = `translate(960px, 540px) scale(${(0.5 + 0.7 * inv(T.check, T.check + 0.7, t)).toFixed(3)})`;
  el.checkglow.style.opacity = g.toFixed(3);

  // the mark: above the bloom while it grows, then part of the world
  const inWorld = t >= 3.55;
  const host = inWorld ? el.world : el.markhost;
  if (el.mark.parentNode !== host) host.appendChild(el.mark);
  const on = t >= T.check - 0.01 && t < T.recede + 1.2;
  disp(el.mark, on);
  if (!on) return;
  const m = markState(t);
  el.mark.style.transform = `translate(${px(m.x - m.D / 2)}, ${px(m.y - m.D / 2)}) scale(${(m.D / 520).toFixed(5)})`;
  const ck = E.glide(inv(T.check, T.check + 0.28, t));
  el.checkPath.style.strokeDasharray = `${M.check} ${M.check}`;
  el.checkPath.style.strokeDashoffset = `${(M.check * (1 - ck)).toFixed(2)}`;
  el.checkPath.style.display = ck > 0 ? '' : 'none';
  const rg = E.softInOut(inv(T.ring, T.ring + 0.42, t));
  el.ringPath.style.strokeDasharray = `${M.ring} ${M.ring}`;
  el.ringPath.style.strokeDashoffset = `${(M.ring * (1 - rg)).toFixed(2)}`;
}

// ---------------------------------------------------------------- B3/B4/B5 product
const morphT = new Track(0).to(T.morph, 1, 13, 1);
const cardTopT = new Track(PILL.t).to(T.morph, CARD.t, 16, 0.92);
const cardBotT = new Track(PILL.b).to(T.morph + 0.06, CARD.b, 11, 1);
const cardLT = new Track(PILL.l).to(T.morph + 0.02, CARD.l, 13, 1);
const cardRT = new Track(PILL.r).to(T.morph + 0.02, CARD.r, 13, 1);
const vWidth = (t) => {
  const a = stepR(t - T.review, 16, 0.9), b = stepR(t - T.verified, 16, 0.9);
  return M.vW1 + (M.vW2 - M.vW1) * a + (M.vW3 - M.vW2) * b;
};

function sceneProduct(t) {
  const on = t >= T.pill - 0.02 && t < 16.4;
  for (const k of ['card', 'composer2', 'bubble', 'placeholder', 'caret', 'qtext', 'send', 'tag', 'atitle', 'rows', 'verify']) disp(el[k], on);
  if (!on) return;
  const m = markState(Math.min(t, T.morph));
  // ---- the card: first the composer pill growing out of the mark, then the chat card
  let L, R, Tp, B, rad;
  if (t < T.morph) {
    L = m.x - 74;
    R = lerp(m.x + 74, PILL.r, stepR(t - (T.pill + 0.06), 15, 0.92));
    Tp = PILL.t; B = PILL.b; rad = 62;
  } else {
    L = cardLT.at(t); R = cardRT.at(t); Tp = cardTopT.at(t); B = cardBotT.at(t);
    rad = lerp(62, 36, clamp(morphT.at(t)));
  }
  const cardO = smooth(inv(T.pill, T.pill + 0.1, t));
  Object.assign(el.card.style, { width: px(R - L), height: px(B - Tp), borderRadius: px(rad), transform: `translate(${px(L)}, ${px(Tp)})`, opacity: cardO.toFixed(3) });

  // ---- placeholder, typed question, caret
  const n = typedCount(t);
  const ph = vis(t, T.placeholder, 0.3, null, 0.1, 10, 8);
  disp(el.placeholder, n === 0 && t < T.type + 0.01);
  el.placeholder.style.opacity = ph.o.toFixed(3);
  el.placeholder.style.filter = blurF(ph.b);
  el.qtext.textContent = QUESTION.slice(0, n);
  const mq = E.glide(inv(T.morph + 0.02, T.morph + 0.46, t));
  const qs = lerp(1, 40 / 44, mq);
  const qW1 = M.qW * (40 / 44);
  const bubbleR = CARD.r - 40, padX = 36;
  const qx1 = bubbleR - padX - qW1, qy1 = 178;
  const qx = lerp(QX, qx1, mq), qy = lerp(540, qy1, mq) - Math.sin(Math.PI * mq) * 18;
  el.qtext.style.transform = `translate(${px(qx)}, ${px(qy - M.qH / 2)}) scale(${qs.toFixed(4)})`;
  el.qtext.style.color = mixHex('#1a2332', '#ffffff', smooth(inv(T.morph + 0.16, T.morph + 0.32, t)));
  // caret: solid while typing, blinking after, gone on send
  const blinkOn = t < TYPE_END + 0.02 || ((t - TYPE_END) % 1.0) < 0.5;
  disp(el.caret, t >= T.placeholder + 0.12 && t < T.morph && blinkOn);
  el.caret.style.transform = `translate(${px(QX + M.caretX[n] + 6)}, ${px(540 - 26)})`;
  // teal bubble grows around the rising question
  const bp = E.softLand(inv(T.morph + 0.08, T.morph + 0.44, t));
  disp(el.bubble, bp > 0);
  if (bp > 0) {
    const w = M.qW * qs, h = M.qH * qs;
    const pad = padX * bp, padY = 24 * bp;
    Object.assign(el.bubble.style, { width: px(w + 2 * pad), height: px(h + 2 * padY), transform: `translate(${px(qx - pad)}, ${px(qy - h / 2 - padY)})`, opacity: smooth(inv(T.morph + 0.08, T.morph + 0.2, t)).toFixed(3) });
  }
  // send button
  const sIn = E.snapSettle(inv(T.sendIn, T.sendIn + 0.3, t));
  const press = 1 - 0.1 * Math.exp(-(((t - (T.press1 + 0.04)) / 0.05) ** 2));
  const sOut = inv(T.morph + 0.02, T.morph + 0.16, t);
  disp(el.send, sIn > 0 && sOut < 1);
  el.send.style.transform = `translate(${px(SEND_C[0] - 46)}, ${px(SEND_C[1] - 46)}) scale(${(lerp(0.55, 1, sIn) * press * (1 - 0.5 * sOut)).toFixed(4)})`;
  el.send.style.opacity = (smooth(inv(T.sendIn, T.sendIn + 0.1, t)) * (1 - sOut)).toFixed(3);
  el.send.style.background = t > T.press1 + 0.03 && t < T.morph + 0.2 ? '#164f4d' : '';

  // ---- answer
  const tg = vis(t, T.tag, 0.28, null, 0.1, 0, 8);
  const tgS = lerp(0.86, 1, E.snapSettle(inv(T.tag, T.tag + 0.28, t)));
  el.tag.style.transform = `translate(${px(COL)}, 268px) scale(${tgS.toFixed(4)})`;
  el.tag.style.opacity = tg.o.toFixed(3); el.tag.style.filter = blurF(tg.b);
  const at = vis(t, T.title, 0.34, null, 0.1, 16, 10);
  el.atitle.style.transform = `translate(${px(COL)}, ${px(336 + at.dy)})`;
  el.atitle.style.opacity = at.o.toFixed(3); el.atitle.style.filter = blurF(at.b);
  answerRows.forEach((r, i) => {
    const v = vis(t, T.rows + i * 0.11, 0.32, null, 0.1, 18, 9);
    r.el.style.transform = `translate(${px(COL)}, ${px(ROW_Y0 + i * ROW_DY + v.dy)})`;
    r.el.style.opacity = v.o.toFixed(3); r.el.style.filter = blurF(v.b);
    // verification: highlight wipe, number flips to a check
    const tc = T.checks + i * 0.12;
    const h = E.glide(inv(tc, tc + 0.26, t));
    r.hl.style.width = px(M.rowW + 40);
    r.hl.style.transform = `scaleX(${h.toFixed(4)})`;
    r.hl.style.opacity = (h > 0 ? 1 : 0).toString();
    const f = E.snapSettle(inv(tc, tc + 0.22, t));
    r.fill.style.transform = `scale(${f.toFixed(4)})`;
    r.fill.style.opacity = (f > 0 ? 1 : 0).toString();
    const nb = inv(tc, tc + 0.08, t);
    r.b.style.opacity = (1 - nb).toFixed(3); r.b.style.filter = blurF(nb * 6);
    const ckp = E.glide(inv(tc + 0.05, tc + 0.25, t));
    r.path.style.strokeDasharray = `${r.len} ${r.len}`;
    r.path.style.strokeDashoffset = `${(r.len * (1 - ckp)).toFixed(2)}`;
    r.path.style.display = ckp > 0 ? '' : 'none'; // no round-cap dot before the stroke starts
  });
  // ---- verify button -> review pill -> verified badge
  const vb = vis(t, T.verifyIn, 0.34, null, 0.1, 16, 10);
  const vpress = 1 - 0.045 * Math.exp(-(((t - (T.press2 + 0.05)) / 0.05) ** 2));
  const vw = vWidth(t);
  Object.assign(el.verify.style, {
    width: px(vw), transform: `translate(${px(VERIFY.x)}, ${px(VERIFY.y + vb.dy)}) scale(${vpress.toFixed(4)})`,
    opacity: vb.o.toFixed(3), filter: blurF(vb.b),
    background: t > T.press2 + 0.03 ? '#e8f5f1' : '#ffffff',
    borderColor: t > T.verified + 0.1 ? '#7ec8b8' : '#1b6b6d',
  });
  const f1 = vis(t, -1, 0.1, T.review - 0.02, 0.09, 0, 8);
  const f2 = vis(t, T.review + 0.06, 0.26, T.verified, 0.09, 12, 8);
  const f3 = vis(t, T.verified + 0.1, 0.3, null, 0.1, 12, 8);
  for (const [face, v] of [[el.vface1, f1], [el.vface2, f2], [el.vface3, f3]]) {
    disp(face, v.o > 0.004);
    face.style.opacity = v.o.toFixed(3); face.style.filter = blurF(v.b); face.style.transform = `translateY(${px(v.dy)})`;
  }
  const ringP = E.linear(inv(T.ring2, T.checks - 0.02, t));
  el.vringArc.style.strokeDashoffset = `${(2 * Math.PI * 18 * (1 - ringP)).toFixed(2)}`;
  el.vringArc.style.display = ringP > 0 ? '' : 'none';
  el.vmark.style.transform = `scale(${lerp(0.55, 1, E.snapSettle(inv(T.verified + 0.1, T.verified + 0.38, t))).toFixed(4)})`;
  const sw = inv(T.sweep, T.sweep + 0.6, t);
  disp(el.sweep, sw > 0 && sw < 1);
  el.sweep.style.transform = `translateX(${px(lerp(-220, vw + 40, E.softInOut(sw)))})`;
  // slim composer at the bottom (texture: it is a chat)
  const c2 = vis(t, T.composer2, 0.36, null, 0.1, 12, 6);
  Object.assign(el.composer2.style, { width: px(1020), height: px(78), transform: `translate(${px(450)}, ${px(884 + c2.dy)})`, opacity: (c2.o * 0.95).toFixed(3) });
}

// ---------------------------------------------------------------- B6 payoff, B7 brand
const markSpring = (t) => lerp(0.86, 1, stepR(t - (T.lcheck + 0.12), 30, 0.42)); // the film's one visible spring
function scenePayoff(t) {
  // the product sinks back while the line comes forward, and keeps drifting (a living background)
  const rc = E.glide(inv(T.recede, T.recede + 0.5, t));
  const drift = inv(T.recede + 0.5, T.carry + 0.6, t);
  const fade = inv(T.carry + 0.1, T.carry + 0.6, t);
  el.worldwrap.style.transformOrigin = '960px 540px';
  el.worldwrap.style.transform = `scale(${(lerp(1, 0.86, rc) - 0.03 * drift).toFixed(4)}) translateY(${px(rc * 40 + drift * 46)})`;
  el.worldwrap.style.filter = blurF(rc * 16);
  el.worldwrap.style.opacity = (lerp(1, 0.3, rc) * (1 - fade)).toFixed(3);

  // three phrases replace each other in one slot, then assemble into the site's stacked headline
  const creep = 1 + 0.03 * inv(T.pay1, T.carry, t);
  const st = E.glide(inv(T.stack, T.stack + 0.52, t));
  const place = (e, y, sc, v) => {
    disp(e, v.o > 0.004);
    const yy = 540 + (y - 540) * creep;
    e.style.transform = `translate(-50%, -50%) translateY(${px(yy - 540 + v.dy)}) scale(${(sc * creep).toFixed(4)})`;
    e.style.opacity = v.o.toFixed(3); e.style.filter = blurF(v.b);
  };
  const out = (v, tout) => { const x = E.accelExit(inv(tout, tout + 0.2, t)); return { o: v.o * (1 - x), b: v.b + x * 16, dy: v.dy - x * 30 }; };
  for (const [e, i, tin, tout] of [[el.pay1, 0, T.pay1, T.pay2 - 0.04], [el.pay2, 1, T.pay2 + 0.04, T.pay3 - 0.04]]) {
    if (t < T.stack) place(e, 540, 1, vis(t, tin, 0.4, tout, 0.22, 70, 18));
    else place(e, STACK_Y[i], STACK_S, out(vis(t, T.stack + 0.08 + i * 0.07, 0.44, null, 0.2, -36, 14), T.carry));
  }
  const v3 = vis(t, T.pay3 + 0.04, 0.4, null, 0.22, 70, 18);
  place(el.pay3, lerp(540, STACK_Y[2], st), lerp(1, STACK_S, st), v3);

  // B7: "delivered." and the first two lines leave, then "AI" travels into the wordmark
  const rest = E.accelExit(inv(T.carry, T.carry + 0.16, t));
  el.pay3rest.style.display = 'inline-block';
  el.pay3rest.style.opacity = (1 - rest).toFixed(3);
  el.pay3rest.style.filter = blurF(rest * 16);
  el.pay3rest.style.transform = `translate(${px(rest * 24)}, ${px(-rest * 46)})`;
  const carrying = t >= T.aiMove;
  el.pay3ai.style.visibility = carrying ? 'hidden' : 'visible';
  const k = E.glide(inv(T.aiMove, T.aiMove + 0.36, t));
  const xf = inv(T.aiSwap, T.aiSwap + 0.12, t); // teal serif "AI" dissolves into the logo's gold "AI"
  disp(el.payAI, carrying && xf < 1);
  if (carrying) {
    const a = M.aiRect;
    const sc3 = STACK_S * creep, y3 = 540 + (STACK_Y[2] - 540) * creep;
    const cx0 = 960 + (a.x + a.w / 2 - 960) * sc3, cy0 = y3 + (a.y + a.h / 2 - 540) * sc3;
    const sc = lerp(sc3, LOCK_AI.cap / (168 * 0.70), k);
    const cx = lerp(cx0, LOCK_AI.cx, k), cy = lerp(cy0, LOCK_AI.cy + AI_DY, k);
    el.payAI.style.transform = `translate(${px(cx - M.aiW / 2)}, ${px(cy - M.aiH / 2)}) scale(${sc.toFixed(4)})`;
    el.payAI.style.opacity = (1 - xf).toFixed(3);
    el.payAI.style.filter = blurF(xf * 9);
  }
}
const STACK_Y = [392, 540, 688], STACK_S = 0.76;
const AI_DY = 6; // optical: serif cap centre vs line box centre

function sceneBrand(t) {
  const on = t >= T.aiSwap - 0.02;
  disp(el.lockup, on); disp(el.cta, on); disp(el.url, on); disp(el.mascot, on && USE_MASCOT);
  if (!on) return;
  const creep = 1 + 0.016 * inv(T.cta, DUR, t);
  const g = (x, y) => [GROUP_C[0] + (x - GROUP_C[0]) * creep, GROUP_C[1] + (y - GROUP_C[1]) * creep];
  const [lx, ly] = g(LOCK.x, LOCK.y);
  el.lockup.style.transform = `translate(${px(lx)}, ${px(ly)}) scale(${(LOCK.s * creep).toFixed(5)})`;
  // logo "AI" materialises where the serif one dissolves
  const xf = inv(T.aiSwap, T.aiSwap + 0.12, t);
  el.lAiImg.style.opacity = xf.toFixed(3);
  el.lAiImg.style.filter = blurF((1 - xf) * 7);
  // "Criter" slides out from behind "AI"
  const cr = E.glide(inv(T.criter, T.criter + 0.4, t));
  el.lCriterRect.setAttribute('x', lerp(1500, 560, cr).toFixed(2));
  el.lCriterRect.setAttribute('width', lerp(0, 980, cr).toFixed(2));
  el.lCriterImg.setAttribute('x', ((1 - cr) * 140).toFixed(2));
  // the C closes, then the check lands last (the tick that completes the logo)
  const ms = markSpring(t);
  const mt = `translate(339 332.5) scale(${ms.toFixed(4)}) translate(-339 -332.5)`;
  el.lRingImg.setAttribute('transform', mt); el.lCheckImg.setAttribute('transform', mt);
  const rg = E.softInOut(inv(T.lring, T.lring + 0.4, t));
  el.lRingPath.style.strokeDasharray = `${M.lring} ${M.lring}`;
  el.lRingPath.style.strokeDashoffset = `${(M.lring * (1 - rg)).toFixed(2)}`;
  disp(el.lRingImg, rg > 0);
  const ck = E.glide(inv(T.lcheck, T.lcheck + 0.24, t));
  el.lCheckPath.style.strokeDasharray = `${M.lcheck} ${M.lcheck}`;
  el.lCheckPath.style.strokeDashoffset = `${(M.lcheck * (1 - ck)).toFixed(2)}`;
  disp(el.lCheckImg, ck > 0);
  // CTA row: button + URL, centred
  const rowW = M.ctaW + 40 + M.urlW;
  const x0 = 960 - rowW / 2;
  const cv = vis(t, T.cta, 0.42, null, 0.1, 28, 10);
  const press = 1 - 0.035 * Math.exp(-(((t - (T.press3 + 0.04)) / 0.05) ** 2));
  const [cx, cy] = g(x0, 652 + cv.dy);
  el.cta.style.transformOrigin = '50% 50%';
  el.cta.style.transform = `translate(${px(cx + (M.ctaW * (creep - 1)) / 2)}, ${px(cy + (M.ctaH * (creep - 1)) / 2)}) scale(${(creep * press).toFixed(5)})`;
  el.cta.style.opacity = cv.o.toFixed(3); el.cta.style.filter = blurF(cv.b);
  const flash = Math.exp(-(((t - (T.press3 + 0.06)) / 0.06) ** 2));
  el.cta.style.background = t > T.press3 + 0.03 ? mixHex('#164f4d', '#2f8b85', flash) : '';
  // the arrow becomes the check when pressed
  const sw = inv(T.press3 + 0.04, T.press3 + 0.14, t);
  el.ctaArrow.style.opacity = (1 - sw).toFixed(3);
  el.ctaArrow.style.filter = blurF(sw * 5);
  el.ctaArrow.style.transform = `translateX(${px(sw * 10)})`;
  const ckc = E.glide(inv(T.press3 + 0.08, T.press3 + 0.3, t));
  el.ctaCheckPath.style.strokeDasharray = `${M.ctaCheck} ${M.ctaCheck}`;
  el.ctaCheckPath.style.strokeDashoffset = `${(M.ctaCheck * (1 - ckc)).toFixed(2)}`;
  el.ctaCheck.style.opacity = ckc > 0 ? '1' : '0';
  el.ctaCheck.style.transform = `scale(${lerp(0.7, 1, E.snapSettle(inv(T.press3 + 0.08, T.press3 + 0.34, t))).toFixed(4)})`;
  const shine = el.cta.querySelector('.shine');
  const sh = inv(T.shine, T.shine + 0.6, t);
  shine.style.transform = `translateX(${px(lerp(-200, M.ctaW + 40, E.softInOut(sh)))})`;
  shine.style.opacity = sh > 0 && sh < 1 ? '1' : '0';
  const uv = vis(t, T.url, 0.42, null, 0.1, 28, 10);
  const [ux, uy] = g(x0 + M.ctaW + 40, 652 + (M.ctaH - M.urlH) / 2 + uv.dy);
  el.url.style.transformOrigin = '0 0';
  el.url.style.transform = `translate(${px(ux)}, ${px(uy)}) scale(${creep.toFixed(5)})`;
  el.url.style.opacity = uv.o.toFixed(3); el.url.style.filter = blurF(uv.b);
  M.ctaScreen = [cx + M.ctaW * 0.62 * creep, cy + M.ctaH * 0.62 * creep];
  // optional variant: Criter the snail says hello (?mascot=1)
  if (USE_MASCOT) {
    const mu = stepR(t - T.mascot, 13, 0.62);
    const rot = (1 - stepR(t - T.mascot - 0.05, 12, 0.5)) * -8;
    el.mascot.style.transform = `translate(${px(1480)}, ${px(1092 - 360 + (1 - mu) * 420)}) rotate(${rot.toFixed(3)}deg)`;
    el.mascot.style.opacity = (t > T.mascot ? 1 : 0).toString();
  }
}

// ---------------------------------------------------------------- cursor (screen space)
function cubic(p0, p1, p2, p3, k) {
  const u = 1 - k;
  return [0, 1].map((i) => u * u * u * p0[i] + 3 * u * u * k * p1[i] + 3 * u * k * k * p2[i] + k * k * k * p3[i]);
}
function sceneCursor(t, cam) {
  const act1 = t >= T.curIn && t < T.press2 + 0.85;
  const act3 = t >= T.cur3In && !USE_MASCOT;
  disp(el.cursor, act1 || act3);
  if (!(act1 || act3)) return;
  let p, s = 1, o = 1;
  if (act1) {
    const send = toScreen(cam, SEND_C[0] + 10, SEND_C[1] + 16);
    const rest1 = [1700, 830];
    const vt = toScreen(cam, VERIFY.x + 230, VERIFY.y + 52);
    if (t < T.curPark) {
      const k = E.softLand(inv(T.curIn, T.curPark, t));
      p = cubic([1800, 1020], [1760, 880], [send[0] + 40, send[1] + 160], send, k);
      s = lerp(1.7, 1, E.glide(inv(T.curIn, T.curPark, t)));
      o = smooth(inv(T.curIn, T.curIn + 0.08, t));
    } else if (t < T.morph + 0.06) {
      p = send;
    } else if (t < T.curGo) {
      const k = E.softInOut(inv(T.morph + 0.06, T.morph + 0.62, t));
      const a = toScreen(cam, SEND_C[0] + 10, SEND_C[1] + 16);
      p = [lerp(a[0], rest1[0], k), lerp(a[1], rest1[1], k)];
    } else if (t < T.press2 + 0.2) {
      const k = E.softLand(inv(T.curGo, T.press2 - 0.1, t));
      p = cubic(rest1, [rest1[0] - 180, rest1[1] - 110], [vt[0] + 280, vt[1] - 30], vt, k);
    } else {
      const k = E.accelExit(inv(T.press2 + 0.2, T.press2 + 0.8, t));
      p = [lerp(vt[0], 2050, k), lerp(vt[1], 1240, k)];
    }
  } else {
    const tgt = M.ctaScreen || [1000, 700];
    if (t < T.press3 - 0.12) {
      const k = E.glide(inv(T.cur3In, T.press3 - 0.14, t));
      p = cubic([1960, 1180], [1640, 1120], [tgt[0] + 300, tgt[1] + 260], tgt, k);
      s = lerp(2.6, 1, E.glide(inv(T.cur3In, T.press3 - 0.12, t)));
    } else {
      const k = E.softInOut(inv(T.press3 + 0.18, T.press3 + 1.3, t));
      p = [tgt[0] + 26 * k, tgt[1] + 34 * k]; // eases off the button after the press
    }
  }
  const squash = 1 - 0.18 * (Math.exp(-(((t - T.press1) / 0.035) ** 2)) + Math.exp(-(((t - T.press2) / 0.035) ** 2)) + Math.exp(-(((t - T.press3) / 0.035) ** 2)));
  el.cursor.style.transform = `translate(${px(p[0] - 6)}, ${px(p[1] - 4)}) scale(${(s * squash).toFixed(4)})`;
  el.cursor.style.opacity = o.toFixed(3);
  el.cursor.style.filter = 'drop-shadow(0 6px 10px rgba(7,27,28,0.25))';
}

// ---------------------------------------------------------------- seek
function seek(t) {
  t = clamp(t, 0, DUR);
  const cam = camAt(t);
  el.world.style.transform = `translate(960px, 540px) scale(${cam.z.toFixed(5)}) translate(${px(-cam.x)}, ${px(-cam.y)})`;
  el['ground-glow'].style.opacity = smooth(inv(3.4, 4.6, t)).toFixed(3);
  el['ground-glow'].style.transform = `translateX(${px((t - 3.4) * 9 - 60)})`;
  sceneHook(t);
  sceneTurn(t);
  sceneProduct(t);
  scenePayoff(t);
  sceneBrand(t);
  sceneCursor(t, cam);
  const f = Math.floor(t * 30);
  el.grain.style.backgroundPosition = `${(f * 73) % 256}px ${(f * 151) % 256}px`;
}

// ---------------------------------------------------------------- sound cues (exported for the mixer)
// Each cue: t (s), s (sound id in audio/mix.py), db (level offset), at: 'peak' puts the sound's measured peak on t,
// 'onset' puts its first transient on t (product-launch-motion's rule: place by the sound's own peak, not its file start).
const CUES = [
  // B1 hook: dark air, ticks on the phrase swaps, rows rushing in, the collapse
  { t: 0.0, s: 'air', db: 0, at: 'onset' },
  { t: T.swap2 + 0.02, s: 'tick', db: 0, at: 'peak' }, { t: T.rowsB + 0.1, s: 'whoosh', db: -4, at: 'peak' },
  { t: T.swap3 + 0.02, s: 'tick', db: 1, at: 'peak' }, { t: T.rowsC + 0.1, s: 'whoosh_b', db: -2, at: 'peak' },
  { t: T.conv + 0.5, s: 'riser', db: 0, at: 'peak' },
  // B2 turn: the check is drawn (pen + the brand chime), light blooms, the C closes
  { t: T.check, s: 'pen', db: 0, at: 'onset' }, { t: T.check + 0.01, s: 'chime', db: 0, at: 'onset' },
  { t: T.bloom, s: 'bloom', db: 0, at: 'onset' },
  { t: T.ring + 0.2, s: 'swish', db: -3, at: 'peak' },
  { t: T.pill + 0.08, s: 'pop', db: -2, at: 'onset' },
  // B3 ask
  { t: T.type, s: 'typing', db: 0, at: 'onset', dur: BURSTS.length / 30 + 0.04 },
  { t: T.press1, s: 'click', db: 0, at: 'peak' },
  { t: T.press1 + 0.03, s: 'send', db: -1, at: 'onset' },
  // B4 answer
  { t: T.tag, s: 'pop', db: -5, at: 'onset' },
  { t: T.rows, s: 'tick_small', db: 0, at: 'peak' }, { t: T.rows + 0.22, s: 'tick_small', db: -2, at: 'peak' }, { t: T.rows + 0.33, s: 'tick_small', db: -1, at: 'peak' },
  { t: T.verifyIn, s: 'pop', db: -7, at: 'onset' },
  // B5 verify: press, time passes, four checks, the verified badge
  { t: T.push + 0.22, s: 'push', db: 0, at: 'peak' },
  { t: T.press2, s: 'click', db: 1, at: 'peak' },
  { t: T.press2 + 0.04, s: 'morph', db: -2, at: 'onset' },
  { t: T.ring2, s: 'clock', db: 0, at: 'onset', dur: T.checks - T.ring2 },
  ...[0, 1, 2, 3].map((i) => ({ t: T.checks + 0.05 + i * 0.12, s: `check_${i + 1}`, db: 0, at: 'onset' })),
  { t: T.verified + 0.12, s: 'badge', db: 0, at: 'peak' },
  { t: T.sweep, s: 'shimmer', db: -2, at: 'onset' },
  // B6 payoff: sink back, three phrases land, the headline assembles
  { t: T.recede + 0.25, s: 'recede', db: 0, at: 'peak' },
  { t: T.pay1 + 0.06, s: 'thud', db: 0, at: 'peak' }, { t: T.pay2 + 0.1, s: 'thud', db: -1, at: 'peak' }, { t: T.pay3 + 0.1, s: 'thud', db: 0, at: 'peak' },
  { t: T.stack + 0.2, s: 'swish', db: -6, at: 'peak' },
  // B7 brand + CTA: carry, "Criter" slides out, the check lands (dip before it), CTA, press
  { t: T.carry + 0.08, s: 'swish', db: -5, at: 'peak' },
  { t: T.criter + 0.18, s: 'whoosh_b', db: -8, at: 'peak' },
  { t: T.lcheck + 0.06, s: 'logo_hit', db: 0, at: 'peak' }, { t: T.lcheck + 0.01, s: 'logo_chime', db: 0, at: 'onset' },
  { t: T.cta, s: 'pop', db: -2, at: 'onset' },
  ...(USE_MASCOT ? [{ t: T.mascot + 0.05, s: 'pop', db: 0, at: 'onset' }] : [
    { t: T.press3, s: 'click', db: 0, at: 'peak' }, { t: T.press3 + 0.08, s: 'small_chime', db: 0, at: 'onset' }]),
  { t: T.shine, s: 'shimmer_end', db: 0, at: 'onset' },
];
// moments the mix ducks for, so the ear finds the peak (the skill's 0.2-0.3 s of reduced sound before the biggest hit)
const DIPS = [{ t0: T.lcheck - 0.3, t1: T.lcheck + 0.02, db: -9 }];

// ---------------------------------------------------------------- boot
window.DUR = DUR;
window.T = T;
window.CUES = CUES;
window.DIPS = DIPS;
window.seek = seek;
window.READY = (async () => {
  await document.fonts.ready;
  await Promise.all([
    document.fonts.load('700 132px Gelasio'), document.fonts.load('italic 700 132px Gelasio'),
    document.fonts.load('500 44px Geist'), document.fonts.load('600 36px Geist'), document.fonts.load('400 34px Geist'),
  ]);
  const imgs = [...document.images].map((i) => (i.complete ? Promise.resolve() : new Promise((r) => { i.onload = r; i.onerror = r; })));
  await Promise.all(imgs);
  // svg <image> elements: preload their files
  await Promise.all(['assets/logo-ring.png', 'assets/logo-check.png', 'assets/logo-criter.png', 'assets/logo-ai.png'].map((src) => new Promise((r) => {
    const im = new Image(); im.onload = r; im.onerror = r; im.src = src;
  })));
  build();
  seek(0);
  return true;
})();
})();
