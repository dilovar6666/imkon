import assert from "node:assert/strict";
import { chromium } from "playwright-core";

const baseUrl = process.env.IMKON_PREVIEW_URL ?? "http://127.0.0.1:5175";
const browser = await chromium.launch({
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  headless: true,
});

try {
  const page = await browser.newPage();
  await page.goto(baseUrl);
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  const result = await page.evaluate(async () => {
    const assets = [...document.querySelectorAll("script[src],link[rel=stylesheet]")]
      .map(element => element.src || element.href)
      .filter(url => url.includes("/assets/"));
    await Promise.all(assets.map(url => fetch(url)));
    const cacheNames = await caches.keys();
    const entries = (await Promise.all(cacheNames.map(async name => (await caches.open(name)).keys())))
      .flat()
      .map(request => new URL(request.url).pathname);
    return { controlled: Boolean(navigator.serviceWorker.controller), assets, cacheNames, entries };
  });
  assert.ok(result.controlled, "Service worker must control the production page");
  assert.ok(result.assets.length > 0, "Production page must load static assets");
  assert.ok(result.assets.every(asset => result.entries.includes(new URL(asset).pathname)), "Static assets must be cached");
  assert.ok(result.entries.every(entry => entry.startsWith("/assets/") || entry === "/icon.svg"), "Private pages and API responses must not be cached");
  console.log(`PWA static cache passed: ${result.entries.length} safe entries`);
} finally {
  await browser.close();
}
