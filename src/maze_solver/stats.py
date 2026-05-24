from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from maze_solver.algorithms import AlgorithmInfo
from maze_solver.grid import Cell, adjacent_cells, default_goal, default_start


@dataclass(frozen=True)
class MazeStats:
    vertices: int
    edges: int
    walls: int
    wall_ratio: float
    dead_ends: int
    junctions: int
    corridors: int
    corridor_bias: float


@dataclass(frozen=True)
class RunStats:
    path_length: int
    visited: int
    frontier: int
    steps: int
    events: int
    coverage: float
    work_factor: float


def maze_statistics(maze: np.ndarray, start: Cell | None = None, goal: Cell | None = None) -> MazeStats:
    start = start or default_start()
    goal = goal or default_goal(maze)
    vertices = 0
    walls = 0
    dead_ends = 0
    junctions = 0
    corridors = 0
    edge_degree_total = 0

    for row in range(maze.shape[0]):
        for col in range(maze.shape[1]):
            cell = (row, col)
            if maze[cell] == 1:
                walls += 1
                continue
            vertices += 1
            degree = len(adjacent_cells(cell, maze))
            edge_degree_total += degree
            if cell not in {start, goal} and degree <= 1:
                dead_ends += 1
            if degree == 2:
                corridors += 1
            if degree >= 3:
                junctions += 1

    total = vertices + walls
    return MazeStats(
        vertices=vertices,
        edges=edge_degree_total // 2,
        walls=walls,
        wall_ratio=(walls / total) if total else 0,
        dead_ends=dead_ends,
        junctions=junctions,
        corridors=corridors,
        corridor_bias=(corridors / vertices) if vertices else 0,
    )


def run_statistics(
    maze: np.ndarray,
    path: set[Cell] | list[Cell],
    visited: set[Cell],
    frontier: set[Cell],
    steps: int,
    events: int,
) -> RunStats:
    vertices = max(1, maze_statistics(maze).vertices)
    path_length = len(path)
    return RunStats(
        path_length=path_length,
        visited=len(visited),
        frontier=len(frontier),
        steps=steps,
        events=events,
        coverage=len(visited) / vertices,
        work_factor=(len(visited) / path_length) if path_length else 0,
    )


def complexity_score(info: AlgorithmInfo, maze_stats: MazeStats, path_depth: int = 1) -> int | None:
    """Estimate the dominant asymptotic term for the current maze graph."""
    v = max(1, maze_stats.vertices)
    e = max(1, maze_stats.edges)
    depth = max(1, path_depth)
    branching = max(2, round((2 * e) / v))
    time = info.time_complexity

    if "Unbounded" in time:
        return None
    if "V + E) log V" in time or "E log V" in time:
        return round((v + e) * math.log2(max(2, v)))
    if "V + E" in time:
        return v + e
    if "VE" in time:
        return v * e
    if "b^(d/2)" in time:
        return round(branching ** max(1, math.ceil(depth / 2)))
    if "b^d" in time:
        return min(10**12, branching ** min(depth, 40))
    if "O(k)" in time:
        return max(depth, v)
    return None


def format_complexity_score(score: int | None) -> str:
    if score is None:
        return "unbounded"
    if score >= 1_000_000_000:
        return f"{score / 1_000_000_000:.1f}B"
    if score >= 1_000_000:
        return f"{score / 1_000_000:.1f}M"
    if score >= 1_000:
        return f"{score / 1_000:.1f}K"
    return str(score)
