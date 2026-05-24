const WALL = 1;
const OPEN = 0;

function openNeighbors(cell, maze) {
  const [row, col] = cell;
  return [
    [row - 1, col],
    [row + 1, col],
    [row, col - 1],
    [row, col + 1],
  ].filter(([r, c]) => maze[r]?.[c] === OPEN);
}

function mazeStatistics(maze) {
  if (!maze) {
    return { open: 0, walls: 0, wallRatio: 0, deadEnds: 0, junctions: 0, corridors: 0, corridorBias: "0.00" };
  }
  let open = 0;
  let walls = 0;
  let deadEnds = 0;
  let junctions = 0;
  let corridors = 0;
  const start = "1,1";
  const goal = `${maze.length - 2},${maze[0].length - 2}`;
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) {
      if (maze[row][col] === WALL) {
        walls += 1;
        continue;
      }
      open += 1;
      const id = `${row},${col}`;
      const degree = openNeighbors([row, col], maze).length;
      if (degree === 2) corridors += 1;
      if (id !== start && id !== goal && degree <= 1) deadEnds += 1;
      if (degree >= 3) junctions += 1;
    }
  }
  const total = open + walls;
  return {
    open,
    walls,
    wallRatio: total ? Math.round((walls / total) * 100) : 0,
    deadEnds,
    junctions,
    corridors,
    corridorBias: open ? (corridors / open).toFixed(2) : "0.00",
  };
}

export { mazeStatistics, openNeighbors };
