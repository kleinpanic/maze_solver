from __future__ import annotations

from collections.abc import Iterable

import numpy as np

Cell = tuple[int, int]

WALL = 1
PASSAGE = 0


def normalize_dimensions(rows: int, cols: int) -> tuple[int, int]:
    if rows < 3 or cols < 3:
        raise ValueError("Maze dimensions must be at least 3x3.")
    if rows % 2 == 0:
        rows += 1
    if cols % 2 == 0:
        cols += 1
    return rows, cols


def default_start() -> Cell:
    return (1, 1)


def default_goal(maze: np.ndarray) -> Cell:
    return (maze.shape[0] - 2, maze.shape[1] - 2)


def open_endpoints(maze: np.ndarray) -> None:
    maze[default_start()] = PASSAGE
    maze[default_goal(maze)] = PASSAGE


def adjacent_cells(cell: Cell, maze: np.ndarray) -> list[Cell]:
    row, col = cell
    neighbors: list[Cell] = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < maze.shape[0] and 0 <= nc < maze.shape[1] and maze[nr, nc] == PASSAGE:
            neighbors.append((nr, nc))
    return neighbors


def two_step_neighbors(cell: Cell, rows: int, cols: int) -> Iterable[tuple[Cell, Cell]]:
    row, col = cell
    for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        nr, nc = row + dr, col + dc
        if 0 < nr < rows - 1 and 0 < nc < cols - 1:
            wall = (row + dr // 2, col + dc // 2)
            yield (nr, nc), wall


def iter_cells(rows: int, cols: int) -> Iterable[Cell]:
    for row in range(1, rows, 2):
        for col in range(1, cols, 2):
            if row < rows - 1 and col < cols - 1:
                yield row, col
