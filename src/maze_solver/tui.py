from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable

from maze_solver.algorithms import ALGORITHM_REGISTRY, SOLVER_REGISTRY
from maze_solver.catalog import algorithm_catalog, catalog_summary
from maze_solver.generation import GENERATION_REGISTRY, generate_maze
from maze_solver.grid import Cell, default_goal, default_start
from maze_solver.stats import complexity_score, format_complexity_score, maze_statistics, run_statistics

ANSI = {
    "reset": "\033[0m",
    "wall": "\033[38;5;238m",
    "open": "\033[38;5;250m",
    "start": "\033[38;5;48m",
    "goal": "\033[38;5;203m",
    "path": "\033[38;5;201m",
    "visited": "\033[38;5;117m",
    "frontier": "\033[38;5;214m",
    "label": "\033[38;5;116m",
    "strong": "\033[1m",
}


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.catalog:
        print_catalog(args)
        return

    maze, seed = generate_maze(
        args.rows,
        args.cols,
        generation_algorithm=args.generator,
        seed=args.seed,
        dead_ends=args.dead_ends,
        branching_factor=args.branching_factor,
        connectedness=args.connectedness,
    )
    start = default_start()
    goal = default_goal(maze)
    events = list(SOLVER_REGISTRY[args.algorithm](maze, start, goal))
    path = [cell for action, cell, _steps in events if action == "path" and cell is not None]
    visited = {cell for action, cell, _steps in events if action == "visit" and cell is not None}
    frontier = {cell for action, cell, _steps in events if action == "enqueue" and cell is not None}
    steps = events[-1][2] if events else 0
    use_color = args.color == "always" or (args.color == "auto" and sys.stdout.isatty())
    info = ALGORITHM_REGISTRY[args.algorithm]
    maze_stats = maze_statistics(maze, start, goal)
    run_stats = run_statistics(maze, path, visited, frontier, steps, len(events))
    score = format_complexity_score(complexity_score(info, maze_stats, max(1, len(path))))
    implemented, tracked = catalog_summary()

    print(f"Maze Solver TUI | {args.generator} | {args.algorithm} | seed {seed}")
    print(
        f"{info.name} | {info.family} | time={info.time_complexity} | "
        f"space={info.space_complexity} | optimal={info.optimal} | complete={info.complete}"
    )
    print(
        f"catalog={implemented}/{tracked} implemented/tracked | V={maze_stats.vertices} E={maze_stats.edges} bound={score}"
    )
    if args.legend:
        print("Legend: S=start G=goal *=path +=frontier .=visited █=wall")
    print(render_maze(maze, start, goal, path, visited, frontier, color=use_color))
    print(
        f"path={run_stats.path_length} visited={run_stats.visited} frontier={run_stats.frontier} "
        f"steps={run_stats.steps} events={run_stats.events} coverage={run_stats.coverage:.1%} "
        f"work_factor={run_stats.work_factor:.2f}"
    )
    print(
        f"maze=open={maze_stats.vertices} walls={maze_stats.walls} wall_ratio={maze_stats.wall_ratio:.1%} "
        f"dead_ends={maze_stats.dead_ends} junctions={maze_stats.junctions} "
        f"corridor_bias={maze_stats.corridor_bias:.2f}"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run maze generation and solving in the terminal.")
    parser.add_argument("--rows", type=int, default=21)
    parser.add_argument("--cols", type=int, default=41)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--dead-ends", type=int, default=6)
    parser.add_argument("--branching-factor", type=int, default=5)
    parser.add_argument("--connectedness", type=int, default=75)
    parser.add_argument("--generator", choices=tuple(GENERATION_REGISTRY), default="Recursive Backtracker")
    parser.add_argument("--algorithm", choices=tuple(ALGORITHM_REGISTRY), default="BFS")
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    parser.add_argument("--legend", action="store_true")
    parser.add_argument("--catalog", action="store_true", help="Print the tracked maze-solving algorithm catalog.")
    parser.add_argument("--catalog-search", default="", help="Filter catalog rows by name, family, or notes.")
    parser.add_argument("--catalog-family", default="", help="Filter catalog rows by exact family.")
    parser.add_argument("--catalog-optimal", choices=("yes", "no"), default=None)
    parser.add_argument("--catalog-complete", choices=("yes", "no"), default=None)
    parser.add_argument("--catalog-weighted", choices=("yes", "no"), default=None)
    parser.add_argument("--catalog-sort", choices=("name", "family", "time", "space"), default="family")
    return parser.parse_args(argv)


def print_catalog(args: argparse.Namespace) -> None:
    implemented, tracked = catalog_summary()
    print(f"Maze Solver Algorithm Catalog | {implemented}/{tracked} implemented/tracked")

    rows = list(algorithm_catalog())
    query = args.catalog_search.casefold()
    if query:
        rows = [
            entry
            for entry in rows
            if query
            in f"{entry['name']} {entry['family']} {entry['notes']} {entry['time']} {entry['space']}".casefold()
        ]
    if args.catalog_family:
        rows = [entry for entry in rows if entry["family"] == args.catalog_family]
    for attr, expected in (
        ("optimal", args.catalog_optimal),
        ("complete", args.catalog_complete),
        ("weighted", args.catalog_weighted),
    ):
        if expected is None:
            continue
        wanted = expected == "yes"
        rows = [entry for entry in rows if _catalog_info(entry).format(attr) == str(wanted)]
    rows.sort(key=lambda entry: (entry[args.catalog_sort], entry["name"]))

    for entry in rows:
        info = _catalog_info(entry)
        print(
            f"{entry['status']:11} | {entry['name']} | {entry['family']} | "
            f"optimal={info.format('optimal')} | complete={info.format('complete')} | weighted={info.format('weighted')} | "
            f"time={entry['time']} | space={entry['space']}"
        )


class _CatalogInfo:
    def __init__(self, entry: dict[str, str]):
        self.entry = entry
        self.info = ALGORITHM_REGISTRY.get(entry["name"])
        if entry["name"] == "Uniform-Cost Search":
            self.info = ALGORITHM_REGISTRY.get("UCS")

    def format(self, attr: str) -> str:
        if self.info is not None:
            return str(getattr(self.info, attr))
        if attr == "weighted":
            return str(
                any(
                    token in self.entry["name"] or token in self.entry["family"]
                    for token in ("Dijkstra", "Weighted", "Cost", "A*")
                )
            )
        if attr == "optimal":
            return str(
                any(
                    token in self.entry["name"]
                    for token in ("A*", "Dijkstra", "BFS", "D*", "Floyd", "Johnson", "Theta", "JPS", "Integer")
                )
            )
        if attr == "complete":
            return str(
                not any(
                    token in self.entry["name"] for token in ("Hill", "Bug", "Random", "Genetic", "Annealing", "Tabu")
                )
            )
        raise ValueError(attr)


def _catalog_info(entry: dict[str, str]) -> _CatalogInfo:
    return _CatalogInfo(entry)


def paint(symbol: str, role: str, color: bool) -> str:
    if not color:
        return symbol
    return f"{ANSI[role]}{symbol}{ANSI['reset']}"


def render_maze(
    maze,
    start: Cell,
    goal: Cell,
    path: Iterable[Cell],
    visited: Iterable[Cell],
    frontier: Iterable[Cell],
    color: bool = False,
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
                parts.append(paint("S", "start", color))
            elif cell == goal:
                parts.append(paint("G", "goal", color))
            elif cell in path_cells:
                parts.append(paint("*", "path", color))
            elif cell in frontier_cells:
                parts.append(paint("+", "frontier", color))
            elif cell in visited_cells:
                parts.append(paint(".", "visited", color))
            elif maze[cell] == 1:
                parts.append(paint("█", "wall", color))
            else:
                parts.append(" ")
        lines.append("".join(parts))
    return "\n".join(lines)
