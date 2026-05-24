import numpy as np

from maze_solver.algorithms import bfs_path, is_solvable
from maze_solver.generation import GENERATION_REGISTRY, generate_maze
from maze_solver.grid import default_goal, default_start


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
