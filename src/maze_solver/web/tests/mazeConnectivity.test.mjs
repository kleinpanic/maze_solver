import assert from "node:assert/strict";
import test from "node:test";

import { connectOpenComponents, isFullyConnected, openCellKeys, reachableOpenCells } from "../src/mazeConnectivity.js";
import { applyBraidedTopology, softenSolidWallBlocks } from "../src/mazeTopology.js";

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

function seededRandom() {
  let value = 431;
  return () => {
    value = (1664525 * value + 1013904223) >>> 0;
    return value / 4294967296;
  };
}

function hasOpenTwoByTwo(maze) {
  for (let row = 0; row < maze.length - 1; row += 1) {
    for (let col = 0; col < maze[0].length - 1; col += 1) {
      if (
        maze[row][col] === 0 &&
        maze[row + 1][col] === 0 &&
        maze[row][col + 1] === 0 &&
        maze[row + 1][col + 1] === 0
      ) {
        return true;
      }
    }
  }
  return false;
}

test("browser topology shaping keeps generated mazes connected and avoids open 2x2 blocks", () => {
  const random = seededRandom();
  const maze = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1],
  ];

  applyBraidedTopology(maze, 0.55, random);
  softenSolidWallBlocks(maze, random);
  connectOpenComponents(maze, random);

  assert.equal(isFullyConnected(maze), true);
  assert.equal(hasOpenTwoByTwo(maze), false);
});
