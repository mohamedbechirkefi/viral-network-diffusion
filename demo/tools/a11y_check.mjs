// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Offline and accessibility smoke check for the built demo, driven over the
// Chrome DevTools Protocol with no extra dependencies (Node 22 WebSocket).
// Usage: node tools/a11y_check.mjs [distDir] [--screenshots outDir]
// Checks: only same-origin requests; results render (no fail-closed panel);
// every focusable element reachable by Tab with a visible focus outline;
// WCAG AA text contrast in light and dark schemes; no horizontal scroll at
// 360 px; reduced-motion leaves no running animation; page works after the
// network is switched off (offline after first load).
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { readFile, mkdir, writeFile, mkdtemp, rm } from "node:fs/promises";
import { extname, join, resolve } from "node:path";
import { tmpdir } from "node:os";

const args = process.argv.slice(2);
const dist = resolve(args.find((a) => !a.startsWith("--")) ?? "dist");
const shotIdx = args.indexOf("--screenshots");
const shotDir = shotIdx >= 0 ? resolve(args[shotIdx + 1]) : null;
const CHROME = process.env.CHROME ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2" };

const server = createServer(async (req, res) => {
  const path = decodeURIComponent(new URL(req.url, "http://x").pathname);
  const file = join(dist, path.endsWith("/") ? path + "index.html" : path);
  if (!file.startsWith(dist)) { res.writeHead(403).end(); return; }
  try {
    const body = await readFile(file);
    res.writeHead(200, { "content-type": TYPES[extname(file)] ?? "application/octet-stream" }).end(body);
  } catch { res.writeHead(404).end(); }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const origin = `http://127.0.0.1:${server.address().port}`;

const profile = await mkdtemp(join(tmpdir(), "a11y-chrome-"));
const chrome = spawn(CHROME, ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check", "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
const wsUrl = await new Promise((ok, bad) => {
  let buf = "";
  chrome.stderr.on("data", (d) => { buf += d; const m = buf.match(/ws:\/\/[^\s]+/); if (m) ok(m[0]); });
  setTimeout(() => bad(new Error("Chrome did not start")), 15000);
});
const ver = await (await fetch(wsUrl.replace("ws://", "http://").replace(/\/devtools\/browser\/.*/, "/json/list"))).json();
const ws = new WebSocket(ver.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pending = new Map(); const events = [];
ws.addEventListener("message", (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } else events.push(d);
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJs = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails)); return r.result.result.value; };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const failures = []; const report = [];
const check = (name, ok, detail = "") => { report.push(`${ok ? "PASS" : "FAIL"} ${name}${detail ? ": " + detail : ""}`); if (!ok) failures.push(name); };

await send("Network.enable"); await send("Page.enable"); await send("Runtime.enable");
const load = async () => { await send("Page.navigate", { url: origin + "/" }); await sleep(1500); };

async function viewport(width, height, mobile) { await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile }); }
async function shot(name) {
  if (!shotDir) return;
  await mkdir(shotDir, { recursive: true });
  const r = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  await writeFile(join(shotDir, name + ".png"), Buffer.from(r.result.data, "base64"));
}

const CONTRAST = `(() => {
  const lum = (c) => { const v = c.map((x) => { x /= 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
  const parse = (s) => { const m = s.match(/[\\d.]+/g); return m ? m.map(Number) : null; };
  const bgOf = (el) => { for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c && (c.length < 4 || c[3] > 0.5)) return c.slice(0, 3); } return [255, 255, 255]; };
  const bad = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = walker.nextNode()); ) {
    const el = n.parentElement; if (!el || !n.textContent.trim()) continue;
    const st = getComputedStyle(el); if (st.visibility === "hidden" || st.display === "none" || el.closest(".skip")) continue;
    const fg = parse(st.color).slice(0, 3), bg = bgOf(el);
    const [a, b] = [lum(fg), lum(bg)].sort((x, y) => y - x); const ratio = (a + 0.05) / (b + 0.05);
    const size = parseFloat(st.fontSize), bold = Number(st.fontWeight) >= 700;
    const need = size >= 24 || (bold && size >= 18.66) ? 3 : 4.5;
    if (ratio < need && !el.closest("button:disabled")) bad.push(el.tagName + " " + ratio.toFixed(2) + " '" + n.textContent.trim().slice(0, 30) + "'");
  }
  return bad;
})()`;

try {
  // 1. Desktop load, light scheme.
  await viewport(1280, 900, false);
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
  await load();
  const errPanel = await evalJs(`!!document.querySelector('[role=alert]')`);
  const nResults = await evalJs(`document.querySelectorAll('#results article').length`);
  check("results render (no fail-closed panel)", !errPanel && nResults > 0, `${nResults} experiment panels`);
  await shot("desktop-light");
  const badLight = await evalJs(CONTRAST);
  check("text contrast, light scheme (WCAG AA)", badLight.length === 0, badLight.slice(0, 5).join("; "));

  // 2. Dark scheme.
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
  await sleep(300);
  const badDark = await evalJs(CONTRAST);
  check("text contrast, dark scheme (WCAG AA)", badDark.length === 0, badDark.slice(0, 5).join("; "));
  await shot("desktop-dark");
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });

  // 3. Keyboard: Tab through the page, every focusable element reached with a visible outline.
  const focusable = await evalJs(`[...document.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea,summary,[tabindex]:not([tabindex="-1"])')].filter(e => e.getClientRects().length).length`);
  await evalJs(`document.activeElement && document.activeElement.blur(), window.scrollTo(0,0), 0`);
  const seen = new Set(); let noOutline = [];
  for (let i = 0; i < focusable + 5; i++) {
    await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    const info = await evalJs(`(() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e); return { key: e.tagName + '|' + (e.id || e.textContent.trim().slice(0, 20)) + '|' + [...e.parentNode.children].indexOf(e), outline: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0 }; })()`);
    if (info) { seen.add(info.key); if (!info.outline) noOutline.push(info.key); }
  }
  check("keyboard reaches every focusable element", seen.size >= focusable, `${seen.size} reached of ${focusable}`);
  check("visible focus indicator", noOutline.length === 0, noOutline.slice(0, 5).join("; "));

  // 4. Mobile width.
  await viewport(360, 780, true); await load();
  const overflow = await evalJs(`document.documentElement.scrollWidth - document.documentElement.clientWidth`);
  check("no horizontal page scroll at 360 px", overflow <= 0, `overflow ${overflow}px`);
  await shot("mobile-light");

  // 5. Reduced motion.
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  await load();
  const anims = await evalJs(`document.getAnimations().filter(a => a.playState === 'running').length`);
  check("reduced motion: no running animations", anims === 0, `${anims} running`);

  // 6. Requests: same origin only.
  const urls = events.filter((e) => e.method === "Network.requestWillBeSent").map((e) => e.params.request.url);
  const foreign = [...new Set(urls.filter((u) => !u.startsWith(origin) && !u.startsWith("data:") && !u.startsWith("blob:")))];
  check("no request leaves the local origin", foreign.length === 0, foreign.slice(0, 5).join(", "));

  // 7. Offline after first load: cut the network, run the sandbox, page stays usable.
  await send("Network.emulateNetworkConditions", { offline: true, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  const stillThere = await evalJs(`document.querySelectorAll('#results article').length`);
  const sandbox = await evalJs(`(async () => { const b = [...document.querySelectorAll('#sandbox button')].find(x => /run/i.test(x.textContent)); if (!b) return 'no run button'; b.click(); for (let i = 0; i < 100; i++) { await new Promise(r => setTimeout(r, 100)); const o = document.querySelector('#sandbox [aria-live]'); if (o && o.textContent.trim()) return o.textContent.trim(); } return 'timeout'; })()`);
  check("offline after first load: results stay, sandbox runs", stillThere > 0 && !/fail|timeout|no run/i.test(sandbox), sandbox.slice(0, 80));
} finally {
  ws.close(); chrome.kill(); server.close();
  await sleep(300); await rm(profile, { recursive: true, force: true }).catch(() => {});
}
console.log(report.join("\n"));
console.log(failures.length ? `A11Y-CHECK FAIL (${failures.length})` : "A11Y-CHECK PASS");
process.exit(failures.length ? 1 : 0);
