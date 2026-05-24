import assert from "node:assert/strict";
import test from "node:test";

import { mazeStatistics } from "../src/mazeStats.js";

test("mazeStatistics counts open cells, walls, junctions, and corridor bias", () => {
  const maze = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
  ];

  assert.deepEqual(mazeStatistics(maze), {
    open: 8,
    walls: 17,
    wallRatio: 68,
    deadEnds: 0,
    junctions: 0,
    corridors: 8,
    corridorBias: "1.00",
  });
});

test("mazeStatistics excludes protected endpoints from dead-end pressure", () => {
  const maze = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1],
  ];

  assert.equal(mazeStatistics(maze).deadEnds, 0);
});
