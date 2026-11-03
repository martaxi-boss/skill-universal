#!/usr/bin/env node
// Browser verification of a Vite-built site: direct Playwright API, no server.
// All HTTP requests are fulfilled from Ferrari's own dist folder; external
// requests are blocked. Only a screenshot and JSON report are written.
"use strict";
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { chromium } = require(path.join(
  os.homedir(), ".local/share/motor-ferrari/.runtime/npm/playwright/node_modules/playwright"
));

async function main() {
  if (process.argv.length !== 5) throw new Error("Expected: DIST SCREENSHOT REPORT");
  const root = fs.realpathSync(process.argv[2]);
  const screenshot = path.resolve(process.argv[3]);
  const reportPath = path.resolve(process.argv[4]);
  if (!fs.statSync(root).isDirectory()) throw new Error("Vite dist must be a directory");
  if (!fs.existsSync(path.join(root, "index.html"))) throw new Error("Missing dist/index.html");
  const mime = {
    ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8", ".json": "application/json",
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".webp": "image/webp", ".ico": "image/x-icon",
    ".woff": "font/woff", ".woff2": "font/woff2",
  };
  const data = {
    engine: "Playwright Chromium headless shell",
    scope: "locally fulfilled Vite files; external requests blocked; no backend",
    status: "failed", viewport: {width: 1280, height: 720},
    served_assets: [], blocked_external: [], console_errors: [], page_errors: [],
  };
  let browser;
  try {
    browser = await chromium.launch({headless: true, timeout: 20000});
    const context = await browser.newContext({
      viewport: data.viewport, serviceWorkers: "block", acceptDownloads: false,
    });
    await context.route("**/*", async route => {
      const url = route.request().url();
      let parsed;
      try { parsed = new URL(url); } catch { await route.abort(); return; }
      if (parsed.protocol !== "http:" || parsed.host !== "ferrari.invalid") {
        data.blocked_external.push(url.slice(0, 180));
        await route.abort();
        return;
      }
      let relative;
      try { relative = decodeURIComponent(parsed.pathname); }
      catch { await route.abort(); return; }
      if (relative.includes("\\") || relative.includes("\0")) {
        await route.abort(); return;
      }
      const requested = relative === "/" ? "/index.html" : relative;
      let file = path.resolve(root, "." + requested);
      if (!file.startsWith(root + path.sep)) { await route.abort(); return; }
      if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
        if (!path.extname(file)) file = path.join(root, "index.html");
        else { await route.fulfill({status: 404, body: "Not Found"}); return; }
      }
      const ext = path.extname(file).toLowerCase();
      if (!mime[ext]) { await route.abort(); return; }
      data.served_assets.push(path.relative(root, file).replaceAll(path.sep, "/"));
      await route.fulfill({status: 200, contentType: mime[ext], body: fs.readFileSync(file)});
    });
    if (typeof context.routeWebSocket === "function") {
      await context.routeWebSocket("**/*", ws => ws.close());
    }
    const page = await context.newPage();
    page.on("pageerror", error => data.page_errors.push(String(error.message).slice(0, 240)));
    page.on("console", message => {
      if (message.type() === "error") data.console_errors.push(message.text().slice(0, 240));
    });
    const response = await page.goto("http://ferrari.invalid/", {waitUntil: "networkidle", timeout: 25000});
    if (!response || response.status() !== 200) throw new Error("Browser did not load index.html");
    const body = await page.locator("body").innerText({timeout: 10000});
    if (!body.trim()) throw new Error("Browser rendered an empty body");
    data.title = (await page.title()).slice(0, 160);
    data.body_text_chars = body.length;
    data.dom_ready = await page.evaluate(() => document.readyState);
    data.demo_js_ready = await page.locator("#app").count() ?
      await page.locator("#app").getAttribute("data-ready") : null;
    data.browser_version = browser.version();
    if (data.page_errors.length || data.console_errors.length) throw new Error("Browser page errors reported");
    await page.screenshot({path: screenshot, fullPage: true, timeout: 15000});
    if (fs.statSync(screenshot).size < 100) throw new Error("Empty screenshot");
    data.screenshot_bytes = fs.statSync(screenshot).size;
    data.status = data.blocked_external.length ? "partial_external_assets_blocked" : "passed";
    fs.writeFileSync(reportPath, JSON.stringify(data, null, 2) + "\n", {mode: 0o600});
    if (data.status !== "passed") throw new Error("Site attempted external network requests");
    await context.close();
  } finally {
    if (browser) await browser.close();
  }
}

main().catch(error => { console.error("FERRARI_BROWSER_CHECK_FAILED=" + String(error.message)); process.exit(1); });
