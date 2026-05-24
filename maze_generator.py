import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from maze_solver.algorithms import is_solvable
from maze_solver.generation import (
    GENERATION_REGISTRY,
    aldous_broder_maze,
    binary_tree_maze,
    generate_maze,
    hunt_and_kill_maze,
    kruskal_maze,
    prim_maze,
    recursive_backtracker_maze,
    sidewinder_maze,
    wilson_maze,
)
from maze_solver.grid import adjacent_cells as get_adjacent_cells

__all__ = [
    "GENERATION_REGISTRY",
    "aldous_broder_maze",
    "binary_tree_maze",
    "generate_maze",
    "get_adjacent_cells",
    "hunt_and_kill_maze",
    "is_solvable",
    "kruskal_maze",
    "prim_maze",
    "recursive_backtracker_maze",
    "sidewinder_maze",
    "wilson_maze",
]
