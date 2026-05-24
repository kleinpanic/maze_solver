import random

import numpy as np

from maze_solver.algorithms import bfs_path, is_solvable
from maze_solver.generation import GENERATION_REGISTRY, _connect_open_components, generate_maze
from maze_solver.grid import default_goal, default_start


def reachable_cells(maze):
    start = default_start()
    queue = [start]
    seen = {start}
    for row, col in queue:
        for next_cell in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
            nr, nc = next_cell
            if not (0 <= nr < maze.shape[0] and 0 <= nc < maze.shape[1]):
                continue
            if maze[nr, nc] != 0 or next_cell in seen:
                continue
            seen.add(next_cell)
            queue.append(next_cell)
    return seen


def test_generation_registry_exposes_researched_algorithms():
    assert {
        "Recursive Backtracker",
        "Prim's",
        "Kruskal",
        "Wilson",
        "Aldous-Broder",
        "Hunt and Kill",
        "Binary Tree",
        "Sidewinder",
        "Growing Tree",
        "Eller",
        "Recursive Division",
    } <= set(GENERATION_REGISTRY)


def test_generators_are_solvable_and_open_endpoints():
    for algorithm in GENERATION_REGISTRY:
        maze, used_seed = generate_maze(15, 15, generation_algorithm=algorithm, seed=1234)
        assert used_seed == 1234
        assert maze.shape == (15, 15)
        assert set(np.unique(maze)) <= {0, 1}
        assert maze[default_start()] == 0
        assert maze[default_goal(maze)] == 0
        assert is_solvable(maze, default_start(), default_goal(maze)), algorithm


def test_generation_is_reproducible_with_seed():
    maze_a, seed_a = generate_maze(17, 17, generation_algorithm="Kruskal", seed=2026)
    maze_b, seed_b = generate_maze(17, 17, generation_algorithm="Kruskal", seed=2026)
    assert seed_a == seed_b == 2026
    assert np.array_equal(maze_a, maze_b)


def test_generated_path_exists_for_all_algorithms():
    for algorithm in GENERATION_REGISTRY:
        maze, _ = generate_maze(11, 13, generation_algorithm=algorithm, seed=77)
        path = bfs_path(maze, default_start(), default_goal(maze))
        assert path[0] == default_start()
        assert path[-1] == default_goal(maze)


def test_generation_noise_preserves_one_reachable_open_component():
    for algorithm in GENERATION_REGISTRY:
        for seed in (7, 77, 707):
            maze, _ = generate_maze(
                21,
                25,
                generation_algorithm=algorithm,
                seed=seed,
                wall_density=0.7,
                dead_ends=30,
                branching_factor=12,
                connectedness=90,
            )
            open_cells = set(zip(*np.where(maze == 0), strict=False))
            assert open_cells <= reachable_cells(maze), (algorithm, seed)


def test_connect_open_components_repairs_prebroken_maze():
    maze = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )

    _connect_open_components(maze, random.Random(0))

    open_cells = set(zip(*np.where(maze == 0), strict=False))
    assert open_cells <= reachable_cells(maze)


def test_connected_generation_handles_minimum_odd_sizes():
    for size in (3, 5):
        maze, _ = generate_maze(size, size, generation_algorithm="Recursive Backtracker", seed=11)
        open_cells = set(zip(*np.where(maze == 0), strict=False))
        assert open_cells <= reachable_cells(maze)
