import numpy as np
import pytest

from maze_solver.algorithms import (
    ALGORITHM_REGISTRY,
    SOLVER_REGISTRY,
    a_star_generator,
    bellman_ford_generator,
    bfs_generator,
    bfs_path,
    bidirectional_bfs_generator,
    dead_end_filling_generator,
    dfs_generator,
    dijkstra_generator,
    flood_fill_generator,
    greedy_best_first_generator,
    ida_star_generator,
    iddfs_generator,
    lee_generator,
    left_hand_rule_generator,
    pledge_generator,
    random_mouse_generator,
    right_hand_rule_generator,
    spfa_generator,
    tremaux_generator,
    uniform_cost_generator,
)
from maze_solver.web_server import find_available_port


def path_from(events):
    return [cell for action, cell, _steps in events if action == "path"]


def assert_valid_path(maze, path, start, end):
    assert path[0] == start
    assert path[-1] == end
    assert all(maze[cell] == 0 for cell in path)
    for current, neighbor in zip(path, path[1:], strict=False):
        assert abs(current[0] - neighbor[0]) + abs(current[1] - neighbor[1]) == 1


def test_registry_includes_expected_algorithms():
    assert {
        "BFS",
        "Lee",
        "DFS",
        "Flood Fill",
        "A*",
        "IDA*",
        "Dijkstra",
        "UCS",
        "SPFA",
        "Bidirectional BFS",
        "Greedy Best-First",
        "Left-Hand Rule",
        "Right-Hand Rule",
        "Tremaux",
        "Pledge",
        "IDDFS",
        "Bellman-Ford",
        "Dead-End Filling",
        "Random Mouse",
    } <= set(ALGORITHM_REGISTRY)
    assert set(ALGORITHM_REGISTRY) == set(SOLVER_REGISTRY)
    assert ALGORITHM_REGISTRY["Dijkstra"].weighted is True
    assert ALGORITHM_REGISTRY["BFS"].time_complexity == "O(V + E)"


def test_web_server_finds_available_port():
    port = find_available_port("127.0.0.1", 49152, max_attempts=100)
    assert 49152 <= port < 49252


def test_bfs_finds_shortest_path_on_unweighted_grid():
    maze = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )
    path = path_from(list(bfs_generator(maze, (1, 1), (4, 5))))
    assert path == bfs_path(maze, (1, 1), (4, 5))
    assert len(path) == 8


def test_dijkstra_matches_bfs_for_unit_weight_maze():
    maze = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    bfs = path_from(list(bfs_generator(maze, (1, 1), (3, 1))))
    dijkstra = path_from(list(dijkstra_generator(maze, (1, 1), (3, 1))))
    assert dijkstra == bfs


def test_weighted_optimal_solvers_match_bfs_for_unit_weights():
    maze = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )
    expected = bfs_path(maze, (1, 1), (4, 5))
    for solver in (
        uniform_cost_generator,
        spfa_generator,
        lee_generator,
        flood_fill_generator,
        bidirectional_bfs_generator,
        iddfs_generator,
        bellman_ford_generator,
    ):
        path = path_from(list(solver(maze, (1, 1), (4, 5))))
        assert_valid_path(maze, path, (1, 1), (4, 5))
        assert len(path) == len(expected)


def test_dijkstra_rejects_negative_weights():
    maze = np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ]
    )
    events = dijkstra_generator(maze, (1, 1), (1, 1), weight=lambda _a, _b: -1)
    assert path_from(list(events)) == [(1, 1)]

    maze = np.array(
        [
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1],
        ]
    )
    with pytest.raises(ValueError):
        list(dijkstra_generator(maze, (1, 1), (1, 2), weight=lambda _a, _b: -1))


def test_a_star_matches_bfs_on_unit_grid():
    maze = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )
    assert path_from(list(a_star_generator(maze, (1, 1), (4, 5)))) == bfs_path(maze, (1, 1), (4, 5))


def test_ida_star_matches_bfs_on_unit_grid():
    maze = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )
    path = path_from(list(ida_star_generator(maze, (1, 1), (4, 5))))
    assert_valid_path(maze, path, (1, 1), (4, 5))
    assert len(path) == len(bfs_path(maze, (1, 1), (4, 5)))


def test_non_optimal_solvers_return_valid_path_when_reachable():
    maze = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    for solver in (
        dfs_generator,
        greedy_best_first_generator,
        dead_end_filling_generator,
        left_hand_rule_generator,
        right_hand_rule_generator,
        tremaux_generator,
        pledge_generator,
        random_mouse_generator,
    ):
        path = path_from(list(solver(maze, (1, 1), (3, 1))))
        assert_valid_path(maze, path, (1, 1), (3, 1))
