import assert from "node:assert/strict";
import test from "node:test";

import { solveHadlockEvents } from "../src/hadlock.js";

function pathFrom(events) {
  return events.filter(([type]) => type === "path").map(([_type, cell]) => cell);
}

test("solveHadlockEvents returns a shortest path around detours", () => {
  const maze = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
  ];

  const path = pathFrom(solveHadlockEvents(maze, [1, 1], [4, 5]));

  assert.deepEqual(path[0], [1, 1]);
  assert.deepEqual(path.at(-1), [4, 5]);
  assert.equal(path.length, 8);
});

test("solveHadlockEvents returns no path for disconnected cells", () => {
  const maze = [
    [1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1],
  ];

  assert.deepEqual(pathFrom(solveHadlockEvents(maze, [1, 1], [1, 3])), []);
});
