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
  await page.waitForFunction(() => document.querySelector("#roadmapSummary")?.textContent.includes("known-applicable"));
  const roadmapSummary = await page.locator("#roadmapSummary").innerText();
  assert.match(roadmapSummary, /85\/12\d known-applicable 2D algorithms covered/);
  assert.match(roadmapSummary, /\d+ researched candidates remain queued/);
  const roadmapRows = await page.locator(".roadmap-row").count();
  assert.ok(roadmapRows >= 120);
  const solverButtons = await page.locator("[data-algorithm]").count();
  assert.ok(solverButtons >= 80);
  assert.match(await page.locator("#algorithmCount").innerText(), new RegExp(`^${solverButtons}/${solverButtons}\\b`));
  await page.fill("#algorithmSearch", "dijkstra");
  assert.equal(await page.locator('[data-algorithm="Dijkstra"]').count(), 1);
  assert.match(await page.locator('[data-algorithm="Dijkstra"] em').innerText(), /native|projected/i);
  assert.ok(Number((await page.locator("#algorithmCount").innerText()).split("/")[0]) < solverButtons);
  await page.click("#clearAlgorithmFilters");
  await page.selectOption("#familyFilter", { label: "Weighted shortest path" });
  assert.equal(await page.locator('[data-algorithm="Dijkstra"]').count(), 1);
  await page.click("#clearAlgorithmFilters");
  assert.equal(await page.locator("[data-algorithm]").count(), solverButtons);
  assert.equal(await page.locator("#density").count(), 0);
  assert.equal(await page.locator("#rows").inputValue(), "41");
  assert.equal(await page.locator("#cols").inputValue(), "61");
  assert.equal(await page.locator("#speed").inputValue(), "44");
  assert.equal(await page.locator("#randomizeOnAlgorithm").isChecked(), false);
  assert.equal(await page.locator("#inspectorMathSummary").count(), 1);
  assert.equal(await page.locator(".algorithm-anatomy").count(), 1);
  assert.equal(await page.locator("#algorithmExecutionBadge").innerText(), "native");
  assert.match(await page.locator("#anatomyFrontier").innerText(), /queue|frontier/i);
  assert.equal(await page.locator(".trace-legend").count(), 1);
  assert.equal(await page.locator(".trace-legend span").count(), 6);
  const legendColors = await page.$$eval(".trace-legend i", (items) => items.map((item) => getComputedStyle(item).backgroundColor));
  assert.deepEqual(legendColors, [
    "rgb(69, 224, 142)",
    "rgb(239, 84, 84)",
    "rgb(121, 214, 242)",
    "rgb(240, 184, 77)",
    "rgb(169, 139, 255)",
    "rgb(216, 79, 214)",
  ]);
  const clippedButtons = await page.$$eval("[data-algorithm]", (buttons) =>
    buttons.filter((button) => button.scrollHeight > button.clientHeight + 1 || button.scrollWidth > button.clientWidth + 1).length,
  );
  assert.equal(clippedButtons, 0);
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
    assert.equal(firstSeed, secondSeed);
    await page.click("#run");
    await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
      timeout: 15_000,
    });
    const pathLength = Number(await page.locator("#pathLength").innerText());
    const openCells = Number(await page.locator("#openCells").innerText());
    assert.ok(pathLength > 0);
    assert.ok(openCells >= pathLength);
  }
  await page.check("#randomizeOnAlgorithm");
  const beforeRandomizedSwitchSeed = await page.locator("#seed").inputValue();
  await page.click('[data-algorithm="Dijkstra"]');
  await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
    timeout: 15_000,
  });
  assert.notEqual(await page.locator("#seed").inputValue(), beforeRandomizedSwitchSeed);
  await page.uncheck("#randomizeOnAlgorithm");
  await page.fill("#rows", "999");
  await page.fill("#cols", "1000");
  await page.click("#generate");
  assert.equal(await page.locator("#rows").inputValue(), "81");
  assert.equal(await page.locator("#cols").inputValue(), "101");

  for (const algorithm of [
    "Flood Fill",
    "IDDFS",
    "Dead-End Filling",
    "Random Mouse",
    "Reverse BFS",
    "Field D*",
    "Potential Field",
    "Fast Sweeping Method",
    "Value Iteration",
    "Policy Iteration",
    "Theta*",
    "Jump Point Search",
    "D* Lite",
    "RRT*",
    "Ant Colony Optimization",
    "SAT Path Encoding",
  ]) {
    await page.click(`[data-algorithm="${algorithm}"]`);
    await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
      timeout: 15_000,
    });
    const pathLength = Number(await page.locator("#pathLength").innerText());
    assert.ok(pathLength > 0);
  }
  await page.click('[data-algorithm="Flood Fill"]');
  await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
    timeout: 15_000,
  });
  const reversePixels = await page.evaluate(() => {
    const canvas = document.querySelector("#mazeCanvas");
    const data = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height).data;
    let count = 0;
    for (let index = 0; index < data.length; index += 4) {
      const purple = data[index] === 169 && data[index + 1] === 139 && data[index + 2] === 255;
      const pink = data[index] === 255 && data[index + 1] === 139 && data[index + 2] === 212;
      if (purple || pink) count += 1;
    }
    return count;
  });
  assert.ok(reversePixels > 0);
  await page.click('[data-algorithm="SAT Path Encoding"]');
  await page.waitForFunction(() => document.querySelector("#status")?.textContent === "complete", null, {
    timeout: 15_000,
  });
  assert.ok(!(await page.locator("#mathSummary").innerText()).includes("No mathematical breakdown"));

  await screenshot(page, "webui-smoke-desktop.png");
  await page.setViewportSize({ width: 390, height: 900 });
  await screenshot(page, "webui-smoke-mobile.png");
  assert.deepEqual(errors, []);
  console.log(`validated ${generators.length} generators on ephemeral port ${port}`);
} finally {
  await browser?.close();
  await new Promise((resolveClose) => server.close(resolveClose));
}
