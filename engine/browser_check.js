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

    // Responsive CSS viewport check, using the SAME browser and page.
    // This does not claim Android device emulation or WCAG certification.
    await page.setViewportSize({width: 390, height: 844});
    const mobile = await page.evaluate(() => {
      const elements = selector => [...document.querySelectorAll(selector)];
      const named = el => Boolean(
        (el.getAttribute("aria-label") || "").trim() ||
        (el.getAttribute("aria-labelledby") || "").trim() ||
        (el.textContent || "").trim() ||
        (el.getAttribute("title") || "").trim() ||
        (el.querySelector("img[alt]")?.getAttribute("alt") || "").trim()
      );
      const hasLabel = el => Boolean(
        (el.getAttribute("aria-label") || "").trim() ||
        (el.getAttribute("aria-labelledby") || "").trim() ||
        el.labels?.length || el.closest("label")
      );
      const width = Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth || 0);
      return {
        viewport_meta_present: Boolean(document.querySelector('meta[name="viewport"]')),
        horizontal_overflow_px: Math.max(0, width - document.documentElement.clientWidth),
        html_lang: document.documentElement.getAttribute("lang") || "",
        headings_found: elements("h1,h2,h3,h4,h5,h6").length,
        images_missing_alt: elements("img:not([alt])").length,
        buttons_missing_name: elements("button,[role=button]").filter(el => !named(el)).length,
        links_missing_name: elements("a[href]").filter(el => !named(el)).length,
        fields_missing_label: elements("input:not([type=hidden]),select,textarea").filter(el => !hasLabel(el)).length,
      };
    });
    mobile.viewport = {width: 390, height: 844};
    mobile.mode = "CSS viewport resize; not actual mobile-device emulation";
    mobile.demo_js_ready = await page.locator("#app").count() ?
      await page.locator("#app").getAttribute("data-ready") : null;
    mobile.findings = [];
    if (!mobile.viewport_meta_present) mobile.findings.push("No viewport meta tag");
    if (!mobile.html_lang.trim()) mobile.findings.push("Missing HTML lang");
    if (mobile.horizontal_overflow_px > 0) mobile.findings.push("Horizontal overflow at 390px viewport");
    for (const [field, label] of [
      ["images_missing_alt", "Images missing alt attribute"],
      ["buttons_missing_name", "Buttons missing accessible name"],
      ["links_missing_name", "Links missing accessible name"],
      ["fields_missing_label", "Form fields missing label"],
    ]) {
      if (mobile[field]) mobile.findings.push(label + ": " + mobile[field]);
    }
    const mobileScreenshot = path.join(path.dirname(screenshot), "browser-mobile.png");
    await page.screenshot({path: mobileScreenshot, fullPage: true, timeout: 15000});
    if (fs.statSync(mobileScreenshot).size < 100) throw new Error("Empty mobile screenshot");
    mobile.screenshot_bytes = fs.statSync(mobileScreenshot).size;
    mobile.spotcheck_status = mobile.findings.length ? "findings" : "clear";
    data.mobile = mobile;

    // Diagnostics are reported even when a page has usability findings;
    // passing here means the browser executed, not that WCAG was certified.
    data.status = data.blocked_external.length ? "partial_external_assets_blocked" : "passed";
    fs.writeFileSync(reportPath, JSON.stringify(data, null, 2) + "\n", {mode: 0o600});
    if (data.status !== "passed" || data.page_errors.length || data.console_errors.length) {
      throw new Error("Browser test detected blocked requests or page errors");
    }
    await context.close();
  } finally {
    if (browser) await browser.close();
  }
}

main().catch(error => { console.error("FERRARI_BROWSER_CHECK_FAILED=" + String(error.message)); process.exit(1); });
