#!/usr/bin/env node
// Browser verification of a Vite-built site: direct Playwright API, no server.
// All HTTP requests are fulfilled from Ferrari's own dist folder; external
// requests are blocked. Only a screenshot and JSON report are written.
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("/srv/projects/skill-universal/.runtime/npm/playwright/node_modules/playwright");

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

    // Real keyboard probes in the SAME browser. Focus checks are read-only;
    // activation is restricted to explicit demo/test opt-in markers, never
    // arbitrary buttons/forms on a user's website.
    const interactions = {
      mode: "Playwright keyboard; opt-in data-ferrari-test controls only",
      focusable_count: 0,
      tab_forward: "not_tested", shift_tab_back: "not_tested",
      button_enter: "not_requested", button_space: "not_requested",
      link_enter: "not_requested", form_enter: "not_requested",
      findings: [],
    };
    const focusable = page.locator(
      'a[href]:visible,button:visible:not([disabled]),' +
      'input:visible:not([disabled]):not([type=hidden]),' +
      'select:visible:not([disabled]),textarea:visible:not([disabled])'
    );
    interactions.focusable_count = await focusable.count();
    if (interactions.focusable_count >= 2) {
      const first = await focusable.first().elementHandle();
      try {
        await focusable.first().focus();
        await page.keyboard.press("Tab");
        const moved = await page.evaluate(el =>
          document.activeElement !== el && document.activeElement !== document.body, first);
        await page.keyboard.press("Shift+Tab");
        const restored = await page.evaluate(el => document.activeElement === el, first);
        interactions.tab_forward = moved ? "passed" : "finding";
        interactions.shift_tab_back = restored ? "passed" : "finding";
        if (!moved) interactions.findings.push("Tab did not advance focus");
        if (!restored) interactions.findings.push("Shift+Tab did not return focus");
      } finally {
        await first.dispose();
      }
    }

    const button = page.locator('button[data-ferrari-test="button"]:visible');
    const buttonCount = await button.count();
    if (buttonCount > 1) interactions.findings.push("Multiple opt-in test buttons; no activation");
    if (buttonCount === 1) {
      await button.focus();
      const before = Number(await button.getAttribute("data-ferrari-activations") || "0");
      await page.keyboard.press("Enter");
      const afterEnter = Number(await button.getAttribute("data-ferrari-activations") || "0");
      interactions.button_enter = afterEnter === before + 1 ? "passed" : "finding";
      // The app can intentionally move focus on Enter (e.g. reset -> search).
      // Test Space independently by refocusing the SAME opt-in button.
      await button.focus();
      await page.keyboard.press("Space");
      const afterSpace = Number(await button.getAttribute("data-ferrari-activations") || "0");
      interactions.button_space = afterSpace === afterEnter + 1 ? "passed" : "finding";
      if (interactions.button_enter !== "passed") interactions.findings.push("Opt-in button did not react to Enter");
      if (interactions.button_space !== "passed") interactions.findings.push("Opt-in button did not react to Space");
    }

    const link = page.locator('a[data-ferrari-test="link"][href^="#"]:visible');
    const linkCount = await link.count();
    if (linkCount > 1) interactions.findings.push("Multiple opt-in test links; no activation");
    if (linkCount === 1) {
      const expected = await link.getAttribute("href");
      await link.focus();
      await page.keyboard.press("Enter");
      const actual = await page.evaluate(() => location.hash);
      interactions.link_enter = expected && expected !== "#" && actual === expected ? "passed" : "finding";
      if (interactions.link_enter !== "passed") interactions.findings.push("Opt-in anchor did not navigate via Enter");
    }

    const form = page.locator('form[data-ferrari-test="form"]:visible');
    const formCount = await form.count();
    if (formCount > 1) interactions.findings.push("Multiple opt-in test forms; no activation");
    if (formCount === 1) {
      const field = form.locator('input:not([type=hidden]):not([disabled])').first();
      if (await field.count()) {
        await field.fill("Ferrari fase 6");
        await field.press("Enter");
        const submitted = await form.getAttribute("data-ferrari-submitted");
        interactions.form_enter = submitted === "yes" ? "passed" : "finding";
      } else {
        interactions.form_enter = "finding";
      }
      if (interactions.form_enter !== "passed") interactions.findings.push("Opt-in form did not submit via Enter");
    }
    interactions.status = interactions.findings.length ? "findings" : "clear";
    data.interactions = interactions;

    // Inspect ALL local link destinations without activating arbitrary controls.
    // This cannot prove backend routing or external websites. It DOES detect
    // obvious dead links, fake "#" placeholders, javascript: and missing anchors.
    const navigation = {
      mode: "DOM and Ferrari-owned dist inspection; no arbitrary clicks",
      links_total: 0, internal_files_verified: 0,
      fragments_verified: 0, external_unverified: 0,
      spa_routes_unverified: 0, schemes_unverified: 0,
      findings: [],
    };
    const hrefs = await page.locator("a[href]").evaluateAll(nodes =>
      nodes.slice(0, 240).map(node => node.getAttribute("href") || ""));
    navigation.links_total = await page.locator("a[href]").count();
    if (navigation.links_total > 240) {
      navigation.findings.push("Too many links to verify within 240-link limit");
    }
    const pageIds = new Set(await page.locator("[id]").evaluateAll(nodes =>
      nodes.map(node => node.id).filter(Boolean)));
    for (const raw of hrefs) {
      const href = raw.trim();
      if (!href || href === "#" || /^javascript:/i.test(href)) {
        navigation.findings.push("Non-functional link destination: " + href.slice(0, 100));
        continue;
      }
      let destination;
      try { destination = new URL(href, page.url()); }
      catch {
        navigation.findings.push("Malformed link destination: " + href.slice(0, 100));
        continue;
      }
      if (["mailto:", "tel:"].includes(destination.protocol)) {
        navigation.schemes_unverified++;
        continue;
      }
      if (destination.protocol !== "http:" || destination.host !== "ferrari.invalid") {
        navigation.external_unverified++;
        continue;
      }
      if (destination.pathname === "/" && destination.hash &&
          !destination.search) {
        let id;
        try { id = decodeURIComponent(destination.hash.slice(1)); }
        catch { id = ""; }
        if (!id || !pageIds.has(id)) {
          navigation.findings.push("Missing in-page anchor: " + href.slice(0, 100));
        } else {
          navigation.fragments_verified++;
        }
        continue;
      }
      let relative;
      try { relative = decodeURIComponent(destination.pathname); }
      catch {
        navigation.findings.push("Malformed internal link path: " + href.slice(0, 100));
        continue;
      }
      if (relative.includes("\\") || relative.includes("\0")) {
        navigation.findings.push("Unsafe internal link path: " + href.slice(0, 100));
        continue;
      }
      const extension = path.extname(relative).toLowerCase();
      const servedPath = relative.endsWith("/") ? relative + "index.html" : relative;
      if (!extension && !relative.endsWith("/") && relative !== "/") {
        // A history-API SPA route can be legitimate, but this check cannot
        // assert that its application router handles the path.
        navigation.spa_routes_unverified++;
        continue;
      }
      const local = path.resolve(root, "." + servedPath);
      if (!local.startsWith(root + path.sep) ||
          !fs.existsSync(local) || !fs.statSync(local).isFile()) {
        navigation.findings.push("Missing local navigation target: " + href.slice(0, 100));
      } else {
        navigation.internal_files_verified++;
      }
    }
    navigation.status = navigation.findings.length ? "findings" : "clear";
    data.navigation = navigation;

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
