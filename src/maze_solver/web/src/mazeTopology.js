const WALL = 1;
const OPEN = 0;

function key(cell) {
  return `${cell[0]},${cell[1]}`;
}

function shuffle(values, random) {
  for (let index = values.length - 1; index > 0; index -= 1) {
    const swap = Math.floor(random() * (index + 1));
    [values[index], values[swap]] = [values[swap], values[index]];
  }
  return values;
}

function hasOpenTwoByTwo(maze, row, col) {
  for (const top of [row - 1, row]) {
    for (const left of [col - 1, col]) {
      if (top < 0 || left < 0 || top + 1 >= maze.length || left + 1 >= maze[0].length) continue;
      if (
        maze[top][left] === OPEN &&
        maze[top + 1][left] === OPEN &&
        maze[top][left + 1] === OPEN &&
        maze[top + 1][left + 1] === OPEN
      ) {
        return true;
      }
    }
  }
  return false;
}

function isConnectorWall(maze, row, col) {
  const horizontal = maze[row][col - 1] === OPEN && maze[row][col + 1] === OPEN;
  const vertical = maze[row - 1]?.[col] === OPEN && maze[row + 1]?.[col] === OPEN;
  return horizontal !== vertical;
}

function openNeighborCount(maze, row, col) {
  return [
    [row - 1, col],
    [row + 1, col],
    [row, col - 1],
    [row, col + 1],
  ].filter(([r, c]) => maze[r]?.[c] === OPEN).length;
}

function hasSolidWallTwoByTwo(maze, row, col) {
  for (const top of [row - 1, row]) {
    for (const left of [col - 1, col]) {
      if (top <= 0 || left <= 0 || top + 1 >= maze.length - 1 || left + 1 >= maze[0].length - 1) continue;
      if (
        maze[top][left] === WALL &&
        maze[top + 1][left] === WALL &&
        maze[top][left + 1] === WALL &&
        maze[top + 1][left + 1] === WALL
      ) {
        return true;
      }
    }
  }
  return false;
}

function softenSolidWallBlocks(maze, random) {
  const candidates = [];
  for (let row = 1; row < maze.length - 1; row += 1) {
    for (let col = 1; col < maze[0].length - 1; col += 1) {
      if (maze[row][col] === WALL && openNeighborCount(maze, row, col) === 1 && hasSolidWallTwoByTwo(maze, row, col)) {
        candidates.push([row, col]);
      }
    }
  }
  shuffle(candidates, random);
  for (const [row, col] of candidates) {
    if (maze[row][col] !== WALL || openNeighborCount(maze, row, col) !== 1 || !hasSolidWallTwoByTwo(maze, row, col)) continue;
    maze[row][col] = OPEN;
    if (hasOpenTwoByTwo(maze, row, col)) maze[row][col] = WALL;
  }
}

function applyBraidedTopology(maze, density, random) {
  const rows = maze.length;
  const cols = maze[0].length;
  const protectedCells = new Set([key([1, 1]), key([rows - 2, cols - 2])]);
  const clampedDensity = Math.max(0, Math.min(1, density));
  const connectors = [];
  for (let row = 1; row < rows - 1; row += 1) {
    for (let col = 1; col < cols - 1; col += 1) {
      if (protectedCells.has(key([row, col]))) continue;
      if (maze[row][col] === WALL && isConnectorWall(maze, row, col)) connectors.push([row, col]);
    }
  }

  shuffle(connectors, random);
  let loopBudget = Math.floor((1 - clampedDensity) * connectors.length * 0.12) + 8;
  for (const [row, col] of connectors) {
    if (loopBudget <= 0) break;
    maze[row][col] = OPEN;
    if (hasOpenTwoByTwo(maze, row, col)) {
      maze[row][col] = WALL;
      continue;
    }
    loopBudget -= 1;
  }
}

export { applyBraidedTopology, hasOpenTwoByTwo, softenSolidWallBlocks };
