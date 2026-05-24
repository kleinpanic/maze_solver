from __future__ import annotations

import argparse
from collections.abc import Iterable

from maze_solver.algorithms import (
    ALGORITHM_REGISTRY,
    a_star_generator,
    bfs_generator,
    dfs_generator,
    dijkstra_generator,
)
from maze_solver.generation import GENERATION_REGISTRY, generate_maze
from maze_solver.grid import Cell, default_goal, default_start

SOLVERS = {
    "BFS": bfs_generator,
    "DFS": dfs_generator,
    "A*": a_star_generator,
    "Dijkstra": dijkstra_generator,
}


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    maze, seed = generate_maze(
        args.rows,
        args.cols,
        generation_algorithm=args.generator,
        seed=args.seed,
        wall_density=args.wall_density,
        dead_ends=args.dead_ends,
        branching_factor=args.branching_factor,
        connectedness=args.connectedness,
    )
    start = default_start()
    goal = default_goal(maze)
    events = list(SOLVERS[args.algorithm](maze, start, goal))
    path = [cell for action, cell, _steps in events if action == "path" and cell is not None]
    visited = {cell for action, cell, _steps in events if action == "visit" and cell is not None}
    frontier = {cell for action, cell, _steps in events if action == "enqueue" and cell is not None}
    steps = events[-1][2] if events else 0

    print(f"Maze Solver TUI | {args.generator} | {args.algorithm} | seed {seed}")
    print(render_maze(maze, start, goal, path, visited, frontier))
    print(f"path={len(path)} visited={len(visited)} frontier={len(frontier)} steps={steps}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run maze generation and solving in the terminal.")
    parser.add_argument("--rows", type=int, default=21)
    parser.add_argument("--cols", type=int, default=41)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--wall-density", type=float, default=0.2)
    parser.add_argument("--dead-ends", type=int, default=6)
    parser.add_argument("--branching-factor", type=int, default=5)
    parser.add_argument("--connectedness", type=int, default=75)
    parser.add_argument("--generator", choices=tuple(GENERATION_REGISTRY), default="Recursive Backtracker")
    parser.add_argument("--algorithm", choices=tuple(ALGORITHM_REGISTRY), default="BFS")
    return parser.parse_args(argv)


def render_maze(
    maze,
    start: Cell,
    goal: Cell,
    path: Iterable[Cell],
    visited: Iterable[Cell],
    frontier: Iterable[Cell],
) -> str:
    path_cells = set(path)
    visited_cells = set(visited)
    frontier_cells = set(frontier)
    lines: list[str] = []
    for row in range(maze.shape[0]):
        parts: list[str] = []
        for col in range(maze.shape[1]):
            cell = (row, col)
            if cell == start:
                parts.append("S")
            elif cell == goal:
                parts.append("G")
            elif cell in path_cells:
                parts.append("*")
            elif cell in frontier_cells:
                parts.append("+")
            elif cell in visited_cells:
                parts.append(".")
            elif maze[cell] == 1:
                parts.append("█")
            else:
                parts.append(" ")
        lines.append("".join(parts))
    return "\n".join(lines)
