const WALL = 1;
const OPEN = 0;

function key(cell) {
  return `${cell[0]},${cell[1]}`;
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

function solveHadlockEvents(maze, start, end) {
  const events = [];
  const deque = [start];
  const detours = new Map([[key(start), 0]]);
  const parent = new Map();
  const settled = new Set();
  const h = (cell) => Math.abs(cell[0] - end[0]) + Math.abs(cell[1] - end[1]);

  while (deque.length) {
    const current = deque.shift();
    const currentKey = key(current);
    if (settled.has(currentKey)) continue;
    settled.add(currentKey);
    events.push(["visit", current]);
    if (currentKey === key(end)) break;
    const currentH = h(current);
    for (const next of neighbors(current, maze)) {
      const nextKey = key(next);
      const penalty = h(next) < currentH ? 0 : 1;
      const candidate = detours.get(currentKey) + penalty;
      if (candidate >= (detours.get(nextKey) ?? Infinity)) continue;
      detours.set(nextKey, candidate);
      parent.set(nextKey, currentKey);
      if (penalty === 0) deque.unshift(next);
      else deque.push(next);
      events.push(["enqueue", next]);
    }
  }
  for (const cell of reconstruct(parent, start, end)) events.push(["path", cell]);
  return events;
}

export { solveHadlockEvents };
