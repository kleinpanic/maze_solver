const WALL = 1;
const OPEN = 0;

const algorithms = {
  BFS: {
    name: "Breadth-First Search",
    family: "Unweighted graph search",
    optimal: "Yes",
    weighted: "No",
    time: "O(V + E)",
    notes: "Shortest path by edge count in unweighted mazes.",
  },
  DFS: {
    name: "Depth-First Search",
    family: "Graph traversal",
    optimal: "No",
    weighted: "No",
    time: "O(V + E)",
    notes: "Explores deeply first; useful contrast against shortest-path solvers.",
  },
  "A*": {
    name: "A* Search",
    family: "Heuristic shortest path",
    optimal: "Yes",
    weighted: "Yes",
    time: "O(E log V)",
    notes: "Uses Manhattan distance as an admissible heuristic on 4-neighbor grids.",
  },
  Dijkstra: {
    name: "Dijkstra's Algorithm",
    family: "Weighted shortest path",
    optimal: "Yes",
    weighted: "Yes",
    time: "O((V + E) log V)",
    notes: "Finds shortest paths with non-negative edge costs.",
  },
  UCS: {
    name: "Uniform-Cost Search",
    family: "Weighted shortest path",
    optimal: "Yes",
    weighted: "Yes",
    time: "O((V + E) log V)",
    notes: "Expands the cheapest known path first; equivalent to Dijkstra on this grid.",
  },
  "Bidirectional BFS": {
    name: "Bidirectional BFS",
    family: "Meet-in-the-middle search",
    optimal: "Yes",
    weighted: "No",
    time: "O(b^(d/2))",
    notes: "Searches from start and goal simultaneously until the waves meet.",
  },
  "Greedy Best-First": {
    name: "Greedy Best-First Search",
    family: "Heuristic graph search",
    optimal: "No",
    weighted: "No",
    time: "O(E log V)",
    notes: "Chases the cell with the smallest Manhattan distance to the goal.",
  },
  IDDFS: {
    name: "Iterative Deepening DFS",
    family: "Depth-limited search",
    optimal: "Yes",
    weighted: "No",
    time: "O(b^d)",
    notes: "Repeats DFS with larger depth limits to keep memory low.",
  },
  "Bellman-Ford": {
    name: "Bellman-Ford",
    family: "Dynamic programming",
    optimal: "Yes",
    weighted: "Yes",
    time: "O(VE)",
    notes: "Relaxes every edge repeatedly, making shortest-path work visible.",
  },
  "Dead-End Filling": {
    name: "Dead-End Filling",
    family: "Maze reduction",
    optimal: "No",
    weighted: "No",
    time: "O(V + E)",
    notes: "Prunes cul-de-sacs before tracing through the remaining corridors.",
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

function generateGrowingTree(rows, cols, random) {
  const maze = blank(rows, cols);
  const active = [[1, 1]];
  maze[1][1] = OPEN;
  while (active.length) {
    const index = random() < 0.7 ? active.length - 1 : Math.floor(random() * active.length);
    const current = active[index];
    const options = twoStep(current, rows, cols).filter(([[r, c]]) => maze[r][c] === WALL);
    if (!options.length) {
      active.splice(index, 1);
      continue;
    }
    const [next, wall] = options[Math.floor(random() * options.length)];
    maze[wall[0]][wall[1]] = OPEN;
    maze[next[0]][next[1]] = OPEN;
    active.push(next);
  }
  return maze;
}

function generateBinaryTree(rows, cols, random) {
  const maze = blank(rows, cols);
  for (let row = 1; row < rows - 1; row += 2) {
    for (let col = 1; col < cols - 1; col += 2) {
      maze[row][col] = OPEN;
      const options = [];
      if (row > 1) options.push([row - 1, col]);
      if (col < cols - 2) options.push([row, col + 1]);
      if (options.length) {
        const [r, c] = options[Math.floor(random() * options.length)];
        maze[r][c] = OPEN;
      }
    }
  }
  return maze;
}

function generateSidewinder(rows, cols, random) {
  const maze = blank(rows, cols);
  for (let row = 1; row < rows - 1; row += 2) {
    let run = [];
    for (let col = 1; col < cols - 1; col += 2) {
      maze[row][col] = OPEN;
      run.push([row, col]);
      const atEast = col >= cols - 2;
      const atNorth = row === 1;
      if (!atEast && (atNorth || random() < 0.5)) {
        maze[row][col + 1] = OPEN;
      } else {
        const [memberRow, memberCol] = run[Math.floor(random() * run.length)];
        if (!atNorth) maze[memberRow - 1][memberCol] = OPEN;
        run = [];
      }
    }
  }
  return maze;
}

function generateRecursiveDivision(rows, cols, random) {
  const maze = Array.from({ length: rows }, (_, row) =>
    Array.from({ length: cols }, (_, col) => (row === 0 || col === 0 || row === rows - 1 || col === cols - 1 ? WALL : OPEN)),
  );
  const oddRange = (start, end) => {
    const values = [];
    for (let value = start; value <= end; value += 2) values.push(value);
    return values;
  };
  const evenRange = (start, end) => {
    const values = [];
    for (let value = start; value <= end; value += 2) values.push(value);
    return values;
  };
  const pick = (values) => values[Math.floor(random() * values.length)];
  const divide = (top, bottom, left, right) => {
    if (bottom - top < 2 || right - left < 2) return;
    const horizontal = bottom - top > right - left || (bottom - top === right - left && random() < 0.5);
    if (horizontal) {
      const wallRow = pick(evenRange(top + 1, bottom - 1));
      const passageCol = pick(oddRange(left, right));
      for (let col = left; col <= right; col++) maze[wallRow][col] = WALL;
      maze[wallRow][passageCol] = OPEN;
      divide(top, wallRow - 1, left, right);
      divide(wallRow + 1, bottom, left, right);
    } else {
      const wallCol = pick(evenRange(left + 1, right - 1));
      const passageRow = pick(oddRange(top, bottom));
      for (let row = top; row <= bottom; row++) maze[row][wallCol] = WALL;
      maze[passageRow][wallCol] = OPEN;
      divide(top, bottom, left, wallCol - 1);
      divide(top, bottom, wallCol + 1, right);
    }
  };
  divide(1, rows - 2, 1, cols - 2);
  return maze;
}

function generateMaze() {
  const rows = odd(controls.rows.value);
  const cols = odd(controls.cols.value);
  controls.rows.value = rows;
  controls.cols.value = cols;
  const random = rng(Number(controls.seed.value) || 2026);
  const generator = controls.generator.value;
  const generators = {
    "Recursive Backtracker": generateRecursive,
    "Prim's": generatePrim,
    Kruskal: generateKruskal,
    "Growing Tree": generateGrowingTree,
    "Binary Tree": generateBinaryTree,
    Sidewinder: generateSidewinder,
    "Recursive Division": generateRecursiveDivision,
  };
  const maze = generators[generator](rows, cols, random);
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

  if (algorithm === "Bidirectional BFS") return solveBidirectional(maze, start, end);
  if (algorithm === "IDDFS") return solveIddfs(maze, start, end);
  if (algorithm === "Bellman-Ford") return solveBellmanFord(maze, start, end);
  if (algorithm === "Dead-End Filling") return solveDeadEndFilling(maze, start, end);

  while (queue.length || stack.length || frontier.length) {
    let current;
    if (algorithm === "DFS") current = stack.pop();
    else if (["A*", "Dijkstra", "UCS", "Greedy Best-First"].includes(algorithm)) {
      current = frontier.sort((a, b) => a[0] - b[0]).shift()?.[1];
    }
    else current = queue.shift();
    if (!current) break;
    visit(current);
    if (key(current) === key(end)) break;
    for (const next of neighbors(current, maze)) {
      const nextKey = key(next);
      if (["A*", "Dijkstra", "UCS", "Greedy Best-First"].includes(algorithm)) {
        const candidate = distances.get(key(current)) + 1;
        if (algorithm !== "Greedy Best-First" && candidate >= (distances.get(nextKey) ?? Infinity)) continue;
        if (algorithm === "Greedy Best-First" && distances.has(nextKey)) continue;
        distances.set(nextKey, candidate);
        parent.set(nextKey, key(current));
        const h = Math.abs(next[0] - end[0]) + Math.abs(next[1] - end[1]);
        const priority = algorithm === "A*" ? candidate + h : algorithm === "Greedy Best-First" ? h : candidate;
        frontier.push([priority, next]);
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

function solveBidirectional(maze, start, end) {
  const events = [];
  const forward = [start];
  const backward = [end];
  const forwardSeen = new Set([key(start)]);
  const backwardSeen = new Set([key(end)]);
  const forwardParent = new Map();
  const backwardParent = new Map();
  let meeting = null;
  const expand = (queue, ownSeen, otherSeen, parent) => {
    const layerSize = queue.length;
    for (let i = 0; i < layerSize; i += 1) {
      const current = queue.shift();
      events.push(["visit", current]);
      for (const next of neighbors(current, maze)) {
        const nextKey = key(next);
        if (ownSeen.has(nextKey)) continue;
        ownSeen.add(nextKey);
        parent.set(nextKey, key(current));
        queue.push(next);
        events.push(["enqueue", next]);
        if (otherSeen.has(nextKey)) return next;
      }
    }
    return null;
  };
  while (forward.length && backward.length && !meeting) {
    meeting = expand(forward, forwardSeen, backwardSeen, forwardParent) ?? expand(backward, backwardSeen, forwardSeen, backwardParent);
  }
  if (meeting) {
    const path = reconstruct(forwardParent, start, meeting);
    let cursor = key(meeting);
    while (cursor !== key(end)) {
      cursor = backwardParent.get(cursor);
      path.push(cursor.split(",").map(Number));
    }
    for (const cell of path) events.push(["path", cell]);
  }
  return events;
}

function solveIddfs(maze, start, end) {
  const events = [];
  const maxDepth = maze.flat().filter((value) => value === OPEN).length;
  for (let limit = 0; limit <= maxDepth; limit += 1) {
    const stack = [[start, [start]]];
    while (stack.length) {
      const [current, path] = stack.pop();
      events.push(["visit", current]);
      if (key(current) === key(end)) {
        for (const cell of path) events.push(["path", cell]);
        return events;
      }
      if (path.length - 1 >= limit) continue;
      const pathKeys = new Set(path.map(key));
      for (const next of neighbors(current, maze).reverse()) {
        if (pathKeys.has(key(next))) continue;
        stack.push([next, [...path, next]]);
        events.push(["enqueue", next]);
      }
    }
  }
  return events;
}

function solveBellmanFord(maze, start, end) {
  const events = [];
  const vertices = [];
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) if (maze[row][col] === OPEN) vertices.push([row, col]);
  }
  const distance = new Map(vertices.map((cell) => [key(cell), Infinity]));
  const parent = new Map();
  distance.set(key(start), 0);
  for (let pass = 0; pass < vertices.length - 1; pass += 1) {
    let changed = false;
    for (const current of vertices) {
      if (distance.get(key(current)) === Infinity) continue;
      events.push(["visit", current]);
      for (const next of neighbors(current, maze)) {
        const candidate = distance.get(key(current)) + 1;
        if (candidate >= distance.get(key(next))) continue;
        distance.set(key(next), candidate);
        parent.set(key(next), key(current));
        changed = true;
        events.push(["enqueue", next]);
      }
    }
    if (!changed) break;
  }
  for (const cell of reconstruct(parent, start, end)) events.push(["path", cell]);
  return events;
}

function solveDeadEndFilling(maze, start, end) {
  const events = [];
  const remaining = new Set();
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) if (maze[row][col] === OPEN) remaining.add(`${row},${col}`);
  }
  const protectedCells = new Set([key(start), key(end)]);
  const degree = (cell, allowed) => neighbors(cell, maze).filter((next) => allowed.has(key(next))).length;
  const queue = [...remaining].map((id) => id.split(",").map(Number)).filter((cell) => !protectedCells.has(key(cell)) && degree(cell, remaining) <= 1);
  const removed = new Set();
  while (queue.length) {
    const current = queue.shift();
    const currentKey = key(current);
    if (removed.has(currentKey) || protectedCells.has(currentKey)) continue;
    const allowed = new Set([...remaining].filter((id) => !removed.has(id)));
    if (degree(current, allowed) > 1) continue;
    removed.add(currentKey);
    events.push(["visit", current]);
    for (const next of neighbors(current, maze)) {
      if (!removed.has(key(next)) && !protectedCells.has(key(next)) && degree(next, allowed) <= 1) {
        queue.push(next);
        events.push(["enqueue", next]);
      }
    }
  }
  const reduced = maze.map((row) => [...row]);
  for (const id of removed) {
    const [row, col] = id.split(",").map(Number);
    reduced[row][col] = WALL;
  }
  state.maze = reduced;
  const pathEvents = solve("BFS");
  for (const event of pathEvents.filter(([type]) => type === "path")) events.push(event);
  state.maze = maze;
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
    .map(([key, info]) => `<tr><td>${key}</td><td>${info.family}</td><td>${info.optimal}</td><td>${info.time}</td></tr>`)
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
