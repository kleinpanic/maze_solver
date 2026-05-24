import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from maze_solver.algorithms import (
    ALGORITHM_REGISTRY,
    SOLVER_REGISTRY,
    a_star_generator,
    bellman_ford_generator,
    bfs_generator,
    bidirectional_bfs_generator,
    dead_end_filling_generator,
    dfs_generator,
    dijkstra_generator,
    flood_fill_generator,
    greedy_best_first_generator,
    heuristic,
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
from maze_solver.grid import adjacent_cells as get_adjacent_cells

__all__ = [
    "ALGORITHM_REGISTRY",
    "SOLVER_REGISTRY",
    "a_star_generator",
    "bellman_ford_generator",
    "bidirectional_bfs_generator",
    "bfs_generator",
    "dead_end_filling_generator",
    "dfs_generator",
    "dijkstra_generator",
    "flood_fill_generator",
    "get_adjacent_cells",
    "greedy_best_first_generator",
    "heuristic",
    "iddfs_generator",
    "lee_generator",
    "left_hand_rule_generator",
    "pledge_generator",
    "random_mouse_generator",
    "right_hand_rule_generator",
    "spfa_generator",
    "tremaux_generator",
    "uniform_cost_generator",
]
