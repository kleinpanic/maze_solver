const WALL = 1;
const OPEN = 0;

function cellKey(cell) {
  return `${cell[0]},${cell[1]}`;
}

function openNeighbors(cell, maze) {
  const [row, col] = cell;
  return [
    [row - 1, col],
    [row + 1, col],
    [row, col - 1],
    [row, col + 1],
  ].filter(([r, c]) => maze[r]?.[c] === OPEN);
}

function reachableOpenCells(maze, start = [1, 1]) {
  if (maze[start[0]]?.[start[1]] !== OPEN) return new Set();
  const queue = [start];
  const seen = new Set([cellKey(start)]);
  for (let index = 0; index < queue.length; index += 1) {
    for (const next of openNeighbors(queue[index], maze)) {
      const nextKey = cellKey(next);
      if (seen.has(nextKey)) continue;
      seen.add(nextKey);
      queue.push(next);
    }
  }
  return seen;
}

function openCellKeys(maze) {
  const cells = new Set();
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) {
      if (maze[row][col] === OPEN) cells.add(`${row},${col}`);
    }
  }
  return cells;
}

function componentFrom(maze, start, allowed) {
  const queue = [start];
  const seen = new Set([cellKey(start)]);
  for (let index = 0; index < queue.length; index += 1) {
    for (const next of openNeighbors(queue[index], maze)) {
      const nextKey = cellKey(next);
      if (!allowed.has(nextKey) || seen.has(nextKey)) continue;
      seen.add(nextKey);
      queue.push(next);
    }
  }
  return seen;
}

function disconnectedComponents(maze, reachable) {
  const remaining = openCellKeys(maze);
  for (const id of reachable) remaining.delete(id);
  const components = [];
  while (remaining.size) {
    const start = [...remaining][0].split(",").map(Number);
    const component = componentFrom(maze, start, remaining);
    components.push(component);
    for (const id of component) remaining.delete(id);
  }
  return components;
}

function carveCorridor(maze, a, b, random) {
  let [row, col] = a;
  const [targetRow, targetCol] = b;
  const axes = random() < 0.5 ? ["row", "col"] : ["col", "row"];
  for (const axis of axes) {
    if (axis === "row") {
      const step = targetRow >= row ? 1 : -1;
      for (; row !== targetRow; row += step) maze[row][col] = OPEN;
      maze[row][col] = OPEN;
    } else {
      const step = targetCol >= col ? 1 : -1;
      for (; col !== targetCol; col += step) maze[row][col] = OPEN;
      maze[row][col] = OPEN;
    }
  }
}

function distance(a, b) {
  return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
}

function connectOpenComponents(maze, random = Math.random) {
  let reachable = reachableOpenCells(maze);
  let components = disconnectedComponents(maze, reachable);
  while (components.length) {
    let best = null;
    const reachableCells = [...reachable].map((id) => id.split(",").map(Number));
    for (const component of components) {
      const componentCells = [...component].map((id) => id.split(",").map(Number));
      for (const mainCell of reachableCells) {
        for (const componentCell of componentCells) {
          const score = distance(mainCell, componentCell);
          if (!best || score < best.score) best = { mainCell, componentCell, score };
        }
      }
    }
    carveCorridor(maze, best.mainCell, best.componentCell, random);
    reachable = reachableOpenCells(maze);
    components = disconnectedComponents(maze, reachable);
  }
  return maze;
}

function isFullyConnected(maze) {
  const open = openCellKeys(maze);
  const reachable = reachableOpenCells(maze);
  for (const id of open) {
    if (!reachable.has(id)) return false;
  }
  return true;
}

export { connectOpenComponents, isFullyConnected, openCellKeys, reachableOpenCells };
