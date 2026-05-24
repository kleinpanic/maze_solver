import assert from "node:assert/strict";
import test from "node:test";

import { connectOpenComponents, isFullyConnected, openCellKeys, reachableOpenCells } from "../src/mazeConnectivity.js";

function fixedRandom() {
  return 0;
}

test("isFullyConnected detects open islands that start-goal checks can miss", () => {
  const maze = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
  ];

  assert.ok(reachableOpenCells(maze).size < openCellKeys(maze).size);
  assert.equal(isFullyConnected(maze), false);
});

test("connectOpenComponents carves unreachable open regions back into the maze", () => {
  const maze = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
  ];

  connectOpenComponents(maze, fixedRandom);

  assert.equal(isFullyConnected(maze), true);
  assert.equal(reachableOpenCells(maze).size, openCellKeys(maze).size);
});
