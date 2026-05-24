from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from maze_solver.algorithms import is_solvable
from maze_solver.grid import (
    PASSAGE,
    WALL,
    Cell,
    default_goal,
    default_start,
    iter_cells,
    normalize_dimensions,
    open_endpoints,
    two_step_neighbors,
)

MazeBuilder = Callable[[int, int, random.Random], np.ndarray]


@dataclass(frozen=True)
class GenerationInfo:
    key: str
    name: str
    family: str
    produces_perfect_maze: bool
    notes: str
    references: tuple[str, ...]


GENERATION_REGISTRY: dict[str, GenerationInfo] = {
    "Recursive Backtracker": GenerationInfo(
        key="Recursive Backtracker",
        name="Recursive Backtracker",
        family="Depth-first spanning tree",
        produces_perfect_maze=True,
        notes="Creates long corridors and strong backtracking behavior.",
        references=("Classical DFS maze generation.",),
    ),
    "Prim's": GenerationInfo(
        key="Prim's",
        name="Randomized Prim",
        family="Frontier spanning tree",
        produces_perfect_maze=True,
        notes="Creates bushier mazes with many short branches.",
        references=("Randomized adaptation of Prim-style spanning tree growth.",),
    ),
    "Kruskal": GenerationInfo(
        key="Kruskal",
        name="Randomized Kruskal",
        family="Disjoint-set spanning tree",
        produces_perfect_maze=True,
        notes="Carves by joining disjoint cell sets with shuffled walls.",
        references=("Randomized adaptation of Kruskal's minimum spanning tree algorithm.",),
    ),
    "Wilson": GenerationInfo(
        key="Wilson",
        name="Wilson's Algorithm",
        family="Uniform spanning tree",
        produces_perfect_maze=True,
        notes="Uses loop-erased random walks to sample uniform spanning trees.",
        references=("Wilson, loop-erased random walk uniform spanning trees.",),
    ),
    "Aldous-Broder": GenerationInfo(
        key="Aldous-Broder",
        name="Aldous-Broder",
        family="Uniform spanning tree",
        produces_perfect_maze=True,
        notes="Simple random walk uniform spanning tree algorithm; slow but mathematically useful.",
        references=("Aldous-Broder random walk spanning tree algorithm.",),
    ),
    "Hunt and Kill": GenerationInfo(
        key="Hunt and Kill",
        name="Hunt and Kill",
        family="Depth-first scan hybrid",
        produces_perfect_maze=True,
        notes="Walks until stuck, then scans for a new frontier cell.",
        references=("Classical hunt-and-kill maze generation.",),
    ),
    "Binary Tree": GenerationInfo(
        key="Binary Tree",
        name="Binary Tree",
        family="Directional side-biased generation",
        produces_perfect_maze=True,
        notes="Fast and simple; intentionally biased.",
        references=("Classical binary tree maze generation.",),
    ),
    "Sidewinder": GenerationInfo(
        key="Sidewinder",
        name="Sidewinder",
        family="Row-run generation",
        produces_perfect_maze=True,
        notes="Fast row-wise algorithm with visible directional texture.",
        references=("Classical sidewinder maze generation.",),
    ),
}


def generate_maze(
    rows: int,
    cols: int,
    generation_algorithm: str = "Recursive Backtracker",
    seed: int | None = None,
    wall_density: float = 0.3,
    dead_ends: int = 10,
    branching_factor: int = 3,
    connectedness: int = 70,
) -> tuple[np.ndarray, int]:
    rows, cols = normalize_dimensions(rows, cols)
    used_seed = seed if seed is not None else random.randint(0, 999_999)
    rng = random.Random(used_seed)
    builder = _builders().get(generation_algorithm)
    if builder is None:
        raise ValueError(f"Unknown generation algorithm: {generation_algorithm}")

    for _ in range(100):
        maze = builder(rows, cols, rng)
        _apply_loops_and_noise(maze, rng, wall_density, dead_ends, branching_factor, connectedness)
        open_endpoints(maze)
        if is_solvable(maze, default_start(), default_goal(maze)):
            return maze, used_seed

    raise RuntimeError("Unable to generate a solvable maze with the selected parameters.")


def _builders() -> dict[str, MazeBuilder]:
    return {
        "Recursive Backtracker": recursive_backtracker_maze,
        "Prim's": prim_maze,
        "Kruskal": kruskal_maze,
        "Wilson": wilson_maze,
        "Aldous-Broder": aldous_broder_maze,
        "Hunt and Kill": hunt_and_kill_maze,
        "Binary Tree": binary_tree_maze,
        "Sidewinder": sidewinder_maze,
    }


def _blank(rows: int, cols: int) -> np.ndarray:
    return np.ones((rows, cols), dtype=int)


def recursive_backtracker_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    stack = [default_start()]
    maze[default_start()] = PASSAGE

    while stack:
        current = stack[-1]
        neighbors = [(cell, wall) for cell, wall in two_step_neighbors(current, rows, cols) if maze[cell] == WALL]
        if not neighbors:
            stack.pop()
            continue
        next_cell, wall = rng.choice(neighbors)
        maze[wall] = PASSAGE
        maze[next_cell] = PASSAGE
        stack.append(next_cell)
    return maze


def prim_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    start = default_start()
    maze[start] = PASSAGE
    frontier: list[tuple[Cell, Cell]] = list(two_step_neighbors(start, rows, cols))

    while frontier:
        index = rng.randrange(len(frontier))
        cell, wall = frontier.pop(index)
        if maze[cell] == PASSAGE:
            continue
        maze[wall] = PASSAGE
        maze[cell] = PASSAGE
        frontier.extend(
            (next_cell, next_wall)
            for next_cell, next_wall in two_step_neighbors(cell, rows, cols)
            if maze[next_cell] == WALL
        )
    return maze


def kruskal_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    parent: dict[Cell, Cell] = {}

    def find(cell: Cell) -> Cell:
        parent.setdefault(cell, cell)
        if parent[cell] != cell:
            parent[cell] = find(parent[cell])
        return parent[cell]

    def union(a: Cell, b: Cell) -> bool:
        root_a, root_b = find(a), find(b)
        if root_a == root_b:
            return False
        parent[root_b] = root_a
        return True

    cells = list(iter_cells(rows, cols))
    for cell in cells:
        maze[cell] = PASSAGE
        parent[cell] = cell

    walls: list[tuple[Cell, Cell, Cell]] = []
    for cell in cells:
        for neighbor, wall in two_step_neighbors(cell, rows, cols):
            if cell < neighbor:
                walls.append((cell, neighbor, wall))
    rng.shuffle(walls)

    for a, b, wall in walls:
        if union(a, b):
            maze[wall] = PASSAGE
    return maze


def wilson_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    cells = list(iter_cells(rows, cols))
    in_tree = {rng.choice(cells)}
    maze[next(iter(in_tree))] = PASSAGE

    while len(in_tree) < len(cells):
        start = rng.choice([cell for cell in cells if cell not in in_tree])
        path = [start]
        positions = {start: 0}
        current = start

        while current not in in_tree:
            next_cell, _ = rng.choice(list(two_step_neighbors(current, rows, cols)))
            if next_cell in positions:
                loop_start = positions[next_cell]
                path = path[: loop_start + 1]
                positions = {cell: index for index, cell in enumerate(path)}
            else:
                path.append(next_cell)
                positions[next_cell] = len(path) - 1
            current = next_cell

        _carve_path(maze, path)
        in_tree.update(path)
    return maze


def aldous_broder_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    cells = list(iter_cells(rows, cols))
    current = rng.choice(cells)
    visited = {current}
    maze[current] = PASSAGE

    while len(visited) < len(cells):
        next_cell, wall = rng.choice(list(two_step_neighbors(current, rows, cols)))
        if next_cell not in visited:
            maze[wall] = PASSAGE
            maze[next_cell] = PASSAGE
            visited.add(next_cell)
        current = next_cell
    return maze


def hunt_and_kill_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    current: Cell | None = default_start()
    maze[current] = PASSAGE

    while current is not None:
        unvisited = [(cell, wall) for cell, wall in two_step_neighbors(current, rows, cols) if maze[cell] == WALL]
        if unvisited:
            next_cell, wall = rng.choice(unvisited)
            maze[wall] = PASSAGE
            maze[next_cell] = PASSAGE
            current = next_cell
            continue

        current = None
        for cell in iter_cells(rows, cols):
            if maze[cell] == PASSAGE:
                continue
            visited_neighbors = [
                (neighbor, wall) for neighbor, wall in two_step_neighbors(cell, rows, cols) if maze[neighbor] == PASSAGE
            ]
            if visited_neighbors:
                neighbor, wall = rng.choice(visited_neighbors)
                maze[cell] = PASSAGE
                maze[wall] = PASSAGE
                current = cell
                break
    return maze


def binary_tree_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    for cell in iter_cells(rows, cols):
        maze[cell] = PASSAGE
        row, col = cell
        candidates: list[Cell] = []
        if row > 1:
            candidates.append((row - 1, col))
        if col < cols - 2:
            candidates.append((row, col + 1))
        if candidates:
            maze[rng.choice(candidates)] = PASSAGE
    return maze


def sidewinder_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    for row in range(1, rows - 1, 2):
        run: list[Cell] = []
        for col in range(1, cols - 1, 2):
            cell = (row, col)
            maze[cell] = PASSAGE
            run.append(cell)
            at_eastern_boundary = col >= cols - 2
            at_northern_boundary = row == 1
            carve_east = not at_eastern_boundary and (at_northern_boundary or rng.choice([True, False]))
            if carve_east:
                maze[(row, col + 1)] = PASSAGE
            else:
                member = rng.choice(run)
                if not at_northern_boundary:
                    maze[(member[0] - 1, member[1])] = PASSAGE
                run = []
    return maze


def _carve_path(maze: np.ndarray, path: list[Cell]) -> None:
    for index, cell in enumerate(path):
        maze[cell] = PASSAGE
        if index == 0:
            continue
        prev = path[index - 1]
        wall = ((cell[0] + prev[0]) // 2, (cell[1] + prev[1]) // 2)
        maze[wall] = PASSAGE


def _apply_loops_and_noise(
    maze: np.ndarray,
    rng: random.Random,
    wall_density: float,
    dead_ends: int,
    branching_factor: int,
    connectedness: int,
) -> None:
    protected = {default_start(), default_goal(maze)}
    openness = max(0, min(100, connectedness)) / 100
    extra_openings = int(branching_factor * openness)
    interior_walls = [
        (row, col)
        for row in range(1, maze.shape[0] - 1)
        for col in range(1, maze.shape[1] - 1)
        if maze[row, col] == WALL and (row, col) not in protected
    ]
    rng.shuffle(interior_walls)
    for cell in interior_walls[:extra_openings]:
        maze[cell] = PASSAGE

    passage_cells = [
        (row, col)
        for row in range(1, maze.shape[0] - 1)
        for col in range(1, maze.shape[1] - 1)
        if maze[row, col] == PASSAGE and (row, col) not in protected
    ]
    rng.shuffle(passage_cells)
    closing_budget = min(
        len(passage_cells), max(0, dead_ends // 3) + int(max(0.0, min(wall_density, 1.0)) * len(passage_cells) * 0.03)
    )
    for cell in passage_cells[:closing_budget]:
        maze[cell] = WALL
