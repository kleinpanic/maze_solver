import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdir, readFile } from "node:fs/promises";
import { extname, join, resolve } from "node:path";

import { chromium } from "playwright";

const contentTypes = {
  ".css": "text/css",
  ".html": "text/html",
  ".json": "application/json",
  ".js": "text/javascript",
  ".svg": "image/svg+xml",
};

function serveDist() {
  const root = resolve("dist");
  const server = createServer(async (request, response) => {
    const path = new URL(request.url, "http://127.0.0.1").pathname;
    const file = path === "/" ? "index.html" : path.replace(/^\/+/, "");
    try {
      const data = await readFile(join(root, file));
      response.writeHead(200, { "content-type": contentTypes[extname(file)] ?? "application/octet-stream" });
      response.end(data);
    } catch {
      response.writeHead(404);
      response.end("not found");
    }
  });
  return new Promise((resolveServer) => {
    server.listen(0, "127.0.0.1", () => resolveServer(server));
  });
}

async function screenshot(page, name) {
  const directory = process.env.SMOKE_SCREENSHOT_DIR;
  if (!directory) return;
  await mkdir(directory, { recursive: true });
  await page.screenshot({ path: join(directory, name), fullPage: true });
}

const server = await serveDist();
const { port } = server.address();
let browser;

try {
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });

  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#roadmapSummary")?.textContent.includes("implemented/tracked"));
  const roadmapRows = await page.locator(".roadmap-row").count();
  assert.ok(roadmapRows >= 80, "algorithm roadmap should track a broad 2D solver catalog");
  const solverButtons = await page.locator("[data-algorithm]").count();
  assert.ok(solverButtons >= 80, "roadmap algorithms should be exposed as runnable solver buttons");
  assert.equal(await page.locator("#density").count(), 0, "wall density should not be exposed as a misleading control");
  assert.equal(await page.locator("#rows").inputValue(), "41", "default rows should show a richer first maze");
  assert.equal(await page.locator("#cols").inputValue(), "61", "default columns should show a richer first maze");
  assert.equal(await page.locator("#speed").inputValue(), "44", "default speed should be brisk enough for larger mazes");
  await page.fill("#rows", "21");
  await page.fill("#cols", "25");
  await page.evaluate(() => {
    document.querySelector("#speed").value = "60";
  });

  const generators = await page.$$eval("#generator option", (options) =>
    options.map((option) => option.value || option.textContent),
  );
  for (const generator of generators) {
    await page.selectOption("#generator", { label: generator });
    await page.fill("#seed", "707");
    await page.click("#generate");
    await page.click('[data-algorithm="Dijkstra"]');
    await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
      timeout: 15_000,
    });
    const firstSeed = await page.locator("#seed").inputValue();
    await page.click('[data-algorithm="BFS"]');
    await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
      timeout: 15_000,
    });
    const secondSeed = await page.locator("#seed").inputValue();
    assert.notEqual(firstSeed, secondSeed, `${generator} solver buttons should restart with a fresh maze`);
    await page.click("#run");
    await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
      timeout: 15_000,
    });
    const pathLength = Number(await page.locator("#pathLength").innerText());
    const openCells = Number(await page.locator("#openCells").innerText());
    assert.ok(pathLength > 0, `${generator} should produce a BFS path`);
    assert.ok(openCells >= pathLength, `${generator} open cells should cover its path`);
  }

  for (const algorithm of ["Theta*", "Jump Point Search", "D* Lite", "RRT*", "Ant Colony Optimization", "SAT Path Encoding"]) {
    await page.click(`[data-algorithm="${algorithm}"]`);
    await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
      timeout: 15_000,
    });
    const pathLength = Number(await page.locator("#pathLength").innerText());
    assert.ok(pathLength > 0, `${algorithm} should render a real path`);
  }
  await page.click('[data-algorithm="SAT Path Encoding"]');
  await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
    timeout: 15_000,
  });
  assert.ok(
    !(await page.locator("#mathSummary").innerText()).includes("No mathematical breakdown"),
    "catalog algorithms should render an educational math breakdown",
  );

  await screenshot(page, "webui-smoke-desktop.png");
  await page.setViewportSize({ width: 390, height: 900 });
  await screenshot(page, "webui-smoke-mobile.png");
  assert.deepEqual(errors, []);
  console.log(`validated ${generators.length} generators on ephemeral port ${port}`);
} finally {
  await browser?.close();
  await new Promise((resolveClose) => server.close(resolveClose));
}
