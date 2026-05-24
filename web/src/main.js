const WALL = 1;
const OPEN = 0;

const algorithms = {
  BFS: {
    name: "Breadth-First Search",
    optimal: "Yes",
    weighted: "No",
    notes: "Shortest path by edge count in unweighted mazes.",
  },
  DFS: {
    name: "Depth-First Search",
    optimal: "No",
    weighted: "No",
    notes: "Explores deeply first; useful contrast against shortest-path solvers.",
  },
  "A*": {
    name: "A* Search",
    optimal: "Yes",
    weighted: "Yes",
    notes: "Uses Manhattan distance as an admissible heuristic on 4-neighbor grids.",
  },
  Dijkstra: {
    name: "Dijkstra's Algorithm",
    optimal: "Yes",
    weighted: "Yes",
    notes: "Finds shortest paths with non-negative edge costs.",
  },
};

let state = {
  maze: null,
  algorithm: "BFS",
  path: [],
  visited: new Set(),
  frontier: new Set(),
  events: [],
  timer: null,
  step: 0,
};

const canvas = document.querySelector("#mazeCanvas");
const context = canvas.getContext("2d");
const controls = {
  generator: document.querySelector("#generator"),
  rows: document.querySelector("#rows"),
  cols: document.querySelector("#cols"),
  seed: document.querySelector("#seed"),
  density: document.querySelector("#density"),
  speed: document.querySelector("#speed"),
  generate: document.querySelector("#generate"),
  run: document.querySelector("#run"),
  status: document.querySelector("#status"),
  algorithmName: document.querySelector("#algorithmName"),
  algorithmNotes: document.querySelector("#algorithmNotes"),
  pathLength: document.querySelector("#pathLength"),
  visitedCount: document.querySelector("#visitedCount"),
  frontierPeak: document.querySelector("#frontierPeak"),
  stepCount: document.querySelector("#stepCount"),
  comparisonRows: document.querySelector("#comparisonRows"),
  algorithmGroup: document.querySelector("#algorithmGroup"),
};

function key(cell) {
  return `${cell[0]},${cell[1]}`;
}

function rng(seed) {
  let value = seed >>> 0;
  return () => {
    value = (1664525 * value + 1013904223) >>> 0;
    return value / 4294967296;
  };
}

function odd(value) {
  const normalized = Math.max(5, Number(value) || 5);
  return normalized % 2 === 0 ? normalized + 1 : normalized;
}

function neighbors(cell, maze) {
  const [row, col] = cell;
  return [
    [row - 1, col],
    [row + 1, col],
    [row, col - 1],
    [row, col + 1],
  ].filter(([r, c]) => maze[r]?.[c] === OPEN);
}

function twoStep(cell, rows, cols) {
  const [row, col] = cell;
  return [
    [[row - 2, col], [row - 1, col]],
    [[row + 2, col], [row + 1, col]],
    [[row, col - 2], [row, col - 1]],
    [[row, col + 2], [row, col + 1]],
  ].filter(([[r, c]]) => r > 0 && c > 0 && r < rows - 1 && c < cols - 1);
}

function blank(rows, cols) {
  return Array.from({ length: rows }, () => Array.from({ length: cols }, () => WALL));
}

function generateRecursive(rows, cols, random) {
  const maze = blank(rows, cols);
  const stack = [[1, 1]];
  maze[1][1] = OPEN;
  while (stack.length) {
    const current = stack[stack.length - 1];
    const options = twoStep(current, rows, cols).filter(([[r, c]]) => maze[r][c] === WALL);
    if (!options.length) {
      stack.pop();
      continue;
    }
    const [next, wall] = options[Math.floor(random() * options.length)];
    maze[wall[0]][wall[1]] = OPEN;
    maze[next[0]][next[1]] = OPEN;
    stack.push(next);
  }
  return maze;
}

function generatePrim(rows, cols, random) {
  const maze = blank(rows, cols);
  const frontier = twoStep([1, 1], rows, cols);
  maze[1][1] = OPEN;
  while (frontier.length) {
    const index = Math.floor(random() * frontier.length);
    const [cell, wall] = frontier.splice(index, 1)[0];
    if (maze[cell[0]][cell[1]] === OPEN) continue;
    maze[wall[0]][wall[1]] = OPEN;
    maze[cell[0]][cell[1]] = OPEN;
    frontier.push(...twoStep(cell, rows, cols).filter(([[r, c]]) => maze[r][c] === WALL));
  }
  return maze;
}

function generateKruskal(rows, cols, random) {
  const maze = blank(rows, cols);
  const parent = new Map();
  const cells = [];
  for (let row = 1; row < rows - 1; row += 2) {
    for (let col = 1; col < cols - 1; col += 2) {
      const cell = [row, col];
      const id = key(cell);
      cells.push(cell);
      parent.set(id, id);
      maze[row][col] = OPEN;
    }
  }
  const find = (id) => {
    while (parent.get(id) !== id) {
      parent.set(id, parent.get(parent.get(id)));
      id = parent.get(id);
    }
    return id;
  };
  const walls = [];
  for (const cell of cells) {
    for (const [next, wall] of twoStep(cell, rows, cols)) {
      if (key(cell) < key(next)) walls.push([cell, next, wall]);
    }
  }
  walls.sort(() => random() - 0.5);
  for (const [a, b, wall] of walls) {
    const rootA = find(key(a));
    const rootB = find(key(b));
    if (rootA !== rootB) {
      parent.set(rootB, rootA);
      maze[wall[0]][wall[1]] = OPEN;
    }
  }
  return maze;
}

function generateMaze() {
  const rows = odd(controls.rows.value);
  const cols = odd(controls.cols.value);
  controls.rows.value = rows;
  controls.cols.value = cols;
  const random = rng(Number(controls.seed.value) || 2026);
  const generator = controls.generator.value;
  const maze =
    generator === "Prim's"
      ? generatePrim(rows, cols, random)
      : generator === "Kruskal"
        ? generateKruskal(rows, cols, random)
        : generateRecursive(rows, cols, random);
  const density = Number(controls.density.value);
  for (let r = 1; r < rows - 1; r++) {
    for (let c = 1; c < cols - 1; c++) {
      if ((r === 1 && c === 1) || (r === rows - 2 && c === cols - 2)) continue;
      if (maze[r][c] === OPEN && random() < density * 0.03) maze[r][c] = WALL;
    }
  }
  maze[1][1] = OPEN;
  maze[rows - 2][cols - 2] = OPEN;
  state = { ...state, maze, path: [], visited: new Set(), frontier: new Set(), events: [], step: 0 };
  draw();
  updateMetrics();
}

function reconstruct(parent, start, end) {
  const path = [];
  let cursor = key(end);
  if (key(start) === key(end)) return [start];
  if (!parent.has(cursor)) return [];
  while (cursor !== key(start)) {
    const cell = cursor.split(",").map(Number);
    path.push(cell);
    cursor = parent.get(cursor);
  }
  path.push(start);
  return path.reverse();
}

function solve(algorithm) {
  const maze = state.maze;
  const start = [1, 1];
  const end = [maze.length - 2, maze[0].length - 2];
  const frontier = [[0, start]];
  const queue = [start];
  const stack = [start];
  const parent = new Map();
  const visited = new Set([key(start)]);
  const events = [];
  const distances = new Map([[key(start), 0]]);

  const enqueue = (cell) => events.push(["enqueue", cell]);
  const visit = (cell) => events.push(["visit", cell]);

  while (queue.length || stack.length || frontier.length) {
    let current;
    if (algorithm === "DFS") current = stack.pop();
    else if (algorithm === "A*" || algorithm === "Dijkstra") current = frontier.sort((a, b) => a[0] - b[0]).shift()?.[1];
    else current = queue.shift();
    if (!current) break;
    visit(current);
    if (key(current) === key(end)) break;
    for (const next of neighbors(current, maze)) {
      const nextKey = key(next);
      if (algorithm === "A*" || algorithm === "Dijkstra") {
        const candidate = distances.get(key(current)) + 1;
        if (candidate >= (distances.get(nextKey) ?? Infinity)) continue;
        distances.set(nextKey, candidate);
        parent.set(nextKey, key(current));
        const heuristic = algorithm === "A*" ? Math.abs(next[0] - end[0]) + Math.abs(next[1] - end[1]) : 0;
        frontier.push([candidate + heuristic, next]);
        enqueue(next);
      } else if (!visited.has(nextKey)) {
        visited.add(nextKey);
        parent.set(nextKey, key(current));
        if (algorithm === "DFS") stack.push(next);
        else queue.push(next);
        enqueue(next);
      }
    }
  }
  const path = reconstruct(parent, start, end);
  for (const cell of path) events.push(["path", cell]);
  return events;
}

function run() {
  clearInterval(state.timer);
  state.events = solve(state.algorithm);
  state.path = [];
  state.visited = new Set();
  state.frontier = new Set();
  state.step = 0;
  controls.status.textContent = "running";
  const delay = Math.max(12, 260 - Number(controls.speed.value) * 4);
  state.timer = setInterval(() => {
    const event = state.events[state.step++];
    if (!event) {
      clearInterval(state.timer);
      controls.status.textContent = "complete";
      return;
    }
    const [type, cell] = event;
    if (type === "visit") state.visited.add(key(cell));
    if (type === "enqueue") state.frontier.add(key(cell));
    if (type === "path") state.path.push(cell);
    draw();
    updateMetrics();
  }, delay);
}

function draw() {
  const maze = state.maze;
  if (!maze) return;
  const rows = maze.length;
  const cols = maze[0].length;
  const cell = Math.min(canvas.width / cols, canvas.height / rows);
  context.fillStyle = "#f5f7fb";
  context.fillRect(0, 0, canvas.width, canvas.height);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const id = `${row},${col}`;
      context.fillStyle = maze[row][col] === WALL ? "#091017" : "#edf3f8";
      if (state.visited.has(id)) context.fillStyle = "#79d6f2";
      if (state.frontier.has(id)) context.fillStyle = "#f0b84d";
      if (state.path.some((pathCell) => key(pathCell) === id)) context.fillStyle = "#d84fd6";
      if (row === 1 && col === 1) context.fillStyle = "#45e08e";
      if (row === rows - 2 && col === cols - 2) context.fillStyle = "#ef5454";
      context.fillRect(col * cell, row * cell, Math.ceil(cell), Math.ceil(cell));
    }
  }
}

function updateMetrics() {
  const info = algorithms[state.algorithm];
  controls.algorithmName.textContent = info.name;
  controls.algorithmNotes.textContent = info.notes;
  controls.pathLength.textContent = state.path.length;
  controls.visitedCount.textContent = state.visited.size;
  controls.frontierPeak.textContent = state.frontier.size;
  controls.stepCount.textContent = state.step;
}

function renderComparison() {
  controls.comparisonRows.innerHTML = Object.entries(algorithms)
    .map(([key, info]) => `<tr><td>${key}</td><td>${info.optimal}</td><td>${info.weighted}</td></tr>`)
    .join("");
}

controls.algorithmGroup.addEventListener("click", (event) => {
  if (!(event.target instanceof HTMLButtonElement)) return;
  state.algorithm = event.target.dataset.algorithm;
  document.querySelectorAll("[data-algorithm]").forEach((button) => button.classList.toggle("active", button === event.target));
  updateMetrics();
});
controls.generate.addEventListener("click", generateMaze);
controls.run.addEventListener("click", run);
renderComparison();
generateMaze();

export { generateKruskal, generatePrim, generateRecursive, solve };
