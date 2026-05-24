"""Maze generation and pathfinding toolkit."""

from maze_solver.algorithms import (
    ALGORITHM_REGISTRY,
    a_star_generator,
    bfs_generator,
    dfs_generator,
    dijkstra_generator,
)
from maze_solver.generation import GENERATION_REGISTRY, generate_maze

__all__ = [
    "ALGORITHM_REGISTRY",
    "GENERATION_REGISTRY",
    "a_star_generator",
    "bfs_generator",
    "dfs_generator",
    "dijkstra_generator",
    "generate_maze",
]
