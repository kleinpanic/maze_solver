from __future__ import annotations

import heapq
from collections import deque
from collections.abc import Callable, Generator
from dataclasses import dataclass
from itertools import count
from typing import Literal

import numpy as np

from maze_solver.grid import Cell, adjacent_cells

Action = Literal["visit", "enqueue", "path", "done"]
SolverEvent = tuple[Action, Cell | None, int]
WeightFunction = Callable[[Cell, Cell], float]


@dataclass(frozen=True)
class AlgorithmInfo:
    key: str
    name: str
    family: str
    weighted: bool
    optimal: bool
    complete: bool
    time_complexity: str
    space_complexity: str
    notes: str
    references: tuple[str, ...]


ALGORITHM_REGISTRY: dict[str, AlgorithmInfo] = {
    "BFS": AlgorithmInfo(
        key="BFS",
        name="Breadth-First Search",
        family="Unweighted graph search",
        weighted=False,
        optimal=True,
        complete=True,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        notes="Shortest path by edge count in unweighted mazes.",
        references=("Cormen et al., Introduction to Algorithms, graph traversal.",),
    ),
    "DFS": AlgorithmInfo(
        key="DFS",
        name="Depth-First Search",
        family="Graph traversal",
        weighted=False,
        optimal=False,
        complete=True,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        notes="Useful exploration baseline; does not guarantee shortest paths.",
        references=("Classical graph traversal.",),
    ),
    "A*": AlgorithmInfo(
        key="A*",
        name="A* Search",
        family="Heuristic shortest path",
        weighted=True,
        optimal=True,
        complete=True,
        time_complexity="O(E log V) with a binary heap",
        space_complexity="O(V)",
        notes="Optimal with an admissible, consistent heuristic. Manhattan distance fits 4-neighbor unit grids.",
        references=("Hart, Nilsson, Raphael, 1968.",),
    ),
    "Dijkstra": AlgorithmInfo(
        key="Dijkstra",
        name="Dijkstra's Algorithm",
        family="Weighted shortest path",
        weighted=True,
        optimal=True,
        complete=True,
        time_complexity="O((V + E) log V) with a binary heap",
        space_complexity="O(V)",
        notes="Shortest paths for graphs with non-negative edge weights.",
        references=("Dijkstra, 1959.",),
    ),
}


def reconstruct_path(parent: dict[Cell, Cell], start: Cell, end: Cell) -> list[Cell]:
    if start == end:
        return [start]
    if end not in parent:
        return []
    path = [end]
    current = end
    while current != start:
        current = parent[current]
        path.append(current)
    path.reverse()
    return path


def bfs_path(maze: np.ndarray, start: Cell, end: Cell) -> list[Cell]:
    queue: deque[Cell] = deque([start])
    visited = {start}
    parent: dict[Cell, Cell] = {}

    while queue:
        current = queue.popleft()
        if current == end:
            return reconstruct_path(parent, start, end)
        for neighbor in adjacent_cells(current, maze):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
    return []


def is_solvable(maze: np.ndarray, start: Cell, end: Cell) -> bool:
    return bool(bfs_path(maze, start, end))


def bfs_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    queue: deque[Cell] = deque([start])
    visited = {start}
    parent: dict[Cell, Cell] = {}
    steps = 0

    while queue:
        current = queue.popleft()
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break
        for neighbor in adjacent_cells(current, maze):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
                yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def dfs_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    stack = [start]
    visited = {start}
    parent: dict[Cell, Cell] = {}
    steps = 0

    while stack:
        current = stack.pop()
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break
        for neighbor in reversed(adjacent_cells(current, maze)):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)
                yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def dijkstra_generator(
    maze: np.ndarray,
    start: Cell,
    end: Cell,
    weight: WeightFunction | None = None,
) -> Generator[SolverEvent, None, None]:
    weight = weight or (lambda _current, _neighbor: 1.0)
    tie_breaker = count()
    heap: list[tuple[float, int, Cell]] = [(0.0, next(tie_breaker), start)]
    distance: dict[Cell, float] = {start: 0.0}
    parent: dict[Cell, Cell] = {}
    settled: set[Cell] = set()
    steps = 0

    while heap:
        current_distance, _, current = heapq.heappop(heap)
        if current in settled:
            continue
        settled.add(current)
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break

        for neighbor in adjacent_cells(current, maze):
            edge_weight = weight(current, neighbor)
            if edge_weight < 0:
                raise ValueError("Dijkstra requires non-negative edge weights.")
            candidate = current_distance + edge_weight
            if candidate < distance.get(neighbor, float("inf")):
                distance[neighbor] = candidate
                parent[neighbor] = current
                heapq.heappush(heap, (candidate, next(tie_breaker), neighbor))
                yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def a_star_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    tie_breaker = count()
    heap: list[tuple[float, int, Cell]] = [(heuristic(start, end), next(tie_breaker), start)]
    came_from: dict[Cell, Cell] = {}
    g_score: dict[Cell, float] = {start: 0.0}
    closed: set[Cell] = set()
    steps = 0

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in closed:
            continue
        closed.add(current)
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break

        for neighbor in adjacent_cells(current, maze):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                heapq.heappush(heap, (tentative_g + heuristic(neighbor, end), next(tie_breaker), neighbor))
                yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(came_from, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def heuristic(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
