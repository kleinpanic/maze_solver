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
    adjacent_cells,
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
    "Growing Tree": GenerationInfo(
        key="Growing Tree",
        name="Growing Tree",
        family="Configurable frontier growth",
        produces_perfect_maze=True,
        notes="Blends recursive-backtracker and Prim-like behavior by varying frontier cell selection.",
        references=("Classical growing-tree maze generation.",),
    ),
    "Eller": GenerationInfo(
        key="Eller",
        name="Eller's Algorithm",
        family="Row-wise set merging",
        produces_perfect_maze=True,
        notes="Builds one row at a time while maintaining set connectivity constraints.",
        references=("Eller's row-wise perfect maze algorithm.",),
    ),
    "Recursive Division": GenerationInfo(
        key="Recursive Division",
        name="Recursive Division",
        family="Wall subdivision",
        produces_perfect_maze=False,
        notes="Starts open and recursively adds walls with one passage through each division.",
        references=("Classical recursive division maze generation.",),
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
        _connect_open_components(maze, rng)
        if _all_passages_reachable_from_start(maze) and is_solvable(maze, default_start(), default_goal(maze)):
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
        "Growing Tree": growing_tree_maze,
        "Eller": eller_maze,
        "Recursive Division": recursive_division_maze,
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


def growing_tree_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    active = [default_start()]
    maze[default_start()] = PASSAGE

    while active:
        index = len(active) - 1 if rng.random() < 0.7 else rng.randrange(len(active))
        current = active[index]
        neighbors = [(cell, wall) for cell, wall in two_step_neighbors(current, rows, cols) if maze[cell] == WALL]
        if not neighbors:
            active.pop(index)
            continue
        next_cell, wall = rng.choice(neighbors)
        maze[wall] = PASSAGE
        maze[next_cell] = PASSAGE
        active.append(next_cell)
    return maze


def eller_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = _blank(rows, cols)
    cell_cols = list(range(1, cols - 1, 2))
    sets: dict[int, int] = {}
    next_set = 1

    for row in range(1, rows - 1, 2):
        last_row = row >= rows - 2
        for col in cell_cols:
            maze[row, col] = PASSAGE
            if col not in sets:
                sets[col] = next_set
                next_set += 1

        for left, right in zip(cell_cols, cell_cols[1:], strict=False):
            should_join = last_row or rng.choice([True, False])
            if should_join and sets[left] != sets[right]:
                maze[row, left + 1] = PASSAGE
                old_set = sets[right]
                new_set = sets[left]
                sets = {col: (new_set if set_id == old_set else set_id) for col, set_id in sets.items()}

        if last_row:
            continue

        next_sets: dict[int, int] = {}
        for set_id in set(sets.values()):
            members = [col for col, member_set in sets.items() if member_set == set_id]
            rng.shuffle(members)
            vertical_count = rng.randint(1, len(members))
            for col in members[:vertical_count]:
                maze[row + 1, col] = PASSAGE
                maze[row + 2, col] = PASSAGE
                next_sets[col] = set_id
        sets = next_sets
    return maze


def recursive_division_maze(rows: int, cols: int, rng: random.Random) -> np.ndarray:
    maze = np.zeros((rows, cols), dtype=int)
    maze[0, :] = WALL
    maze[-1, :] = WALL
    maze[:, 0] = WALL
    maze[:, -1] = WALL

    def divide(top: int, bottom: int, left: int, right: int) -> None:
        height = bottom - top + 1
        width = right - left + 1
        if height < 3 or width < 3:
            return

        horizontal = height > width if height != width else rng.choice([True, False])
        if horizontal:
            wall_row = rng.choice(list(range(top + 1, bottom, 2)))
            passage_col = rng.choice(list(range(left, right + 1, 2)))
            for col in range(left, right + 1):
                maze[wall_row, col] = WALL
            maze[wall_row, passage_col] = PASSAGE
            divide(top, wall_row - 1, left, right)
            divide(wall_row + 1, bottom, left, right)
        else:
            wall_col = rng.choice(list(range(left + 1, right, 2)))
            passage_row = rng.choice(list(range(top, bottom + 1, 2)))
            for row in range(top, bottom + 1):
                maze[row, wall_col] = WALL
            maze[passage_row, wall_col] = PASSAGE
            divide(top, bottom, left, wall_col - 1)
            divide(top, bottom, wall_col + 1, right)

    divide(1, rows - 2, 1, cols - 2)
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


def _reachable_passages(maze: np.ndarray, start: Cell) -> set[Cell]:
    if maze[start] != PASSAGE:
        return set()
    queue = [start]
    seen = {start}
    for cell in queue:
        for neighbor in adjacent_cells(cell, maze):
            if neighbor in seen:
                continue
            seen.add(neighbor)
            queue.append(neighbor)
    return seen


def _open_components(maze: np.ndarray, excluded: set[Cell]) -> list[set[Cell]]:
    components: list[set[Cell]] = []
    remaining = {
        (row, col)
        for row in range(maze.shape[0])
        for col in range(maze.shape[1])
        if maze[row, col] == PASSAGE and (row, col) not in excluded
    }
    while remaining:
        start = next(iter(remaining))
        component = _reachable_passages(maze, start)
        component &= remaining
        components.append(component)
        remaining -= component
    return components


def _carve_corridor_between(maze: np.ndarray, a: Cell, b: Cell, rng: random.Random) -> None:
    row, col = a
    target_row, target_col = b
    axes = ("row", "col") if rng.choice([True, False]) else ("col", "row")

    def carve_row() -> None:
        nonlocal row
        step = 1 if target_row >= row else -1
        for next_row in range(row, target_row + step, step):
            maze[next_row, col] = PASSAGE
        row = target_row

    def carve_col() -> None:
        nonlocal col
        step = 1 if target_col >= col else -1
        for next_col in range(col, target_col + step, step):
            maze[row, next_col] = PASSAGE
        col = target_col

    for axis in axes:
        if axis == "row":
            carve_row()
        else:
            carve_col()


def _connect_open_components(maze: np.ndarray, rng: random.Random) -> None:
    reachable = _reachable_passages(maze, default_start())
    components = _open_components(maze, reachable)
    while components:
        component = min(
            components,
            key=lambda cells: min(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a in reachable for b in cells),
        )
        main_cell, component_cell = min(
            ((a, b) for a in reachable for b in component),
            key=lambda pair: abs(pair[0][0] - pair[1][0]) + abs(pair[0][1] - pair[1][1]),
        )
        _carve_corridor_between(maze, main_cell, component_cell, rng)
        reachable = _reachable_passages(maze, default_start())
        components = _open_components(maze, reachable)


def _all_passages_reachable_from_start(maze: np.ndarray) -> bool:
    reachable = _reachable_passages(maze, default_start())
    open_cells = {
        (row, col) for row in range(maze.shape[0]) for col in range(maze.shape[1]) if maze[row, col] == PASSAGE
    }
    return open_cells <= reachable
