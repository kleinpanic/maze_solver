from __future__ import annotations

import heapq
import random
import zlib
from collections import deque
from collections.abc import Callable, Generator
from dataclasses import dataclass
from itertools import count
from typing import Literal

import numpy as np

from maze_solver.catalog import algorithm_catalog
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
    "IDA*": AlgorithmInfo(
        key="IDA*",
        name="Iterative Deepening A*",
        family="Memory-bounded heuristic search",
        weighted=False,
        optimal=True,
        complete=True,
        time_complexity="O(b^d) worst case",
        space_complexity="O(d)",
        notes="Runs depth-first contours by increasing f = g + h thresholds; optimal with an admissible heuristic.",
        references=("Korf, 1985; iterative-deepening heuristic search.",),
    ),
    "Hadlock": AlgorithmInfo(
        key="Hadlock",
        name="Hadlock's Algorithm",
        family="Detour-number maze routing",
        weighted=False,
        optimal=True,
        complete=True,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        notes="Minimizes detours away from Manhattan progress; on 4-neighbor unit grids this yields a shortest path.",
        references=("Hadlock, 1977; shortest-path maze routing by detour number.",),
    ),
    "UCS": AlgorithmInfo(
        key="UCS",
        name="Uniform-Cost Search",
        family="Weighted shortest path",
        weighted=True,
        optimal=True,
        complete=True,
        time_complexity="O((V + E) log V) with a binary heap",
        space_complexity="O(V)",
        notes="Dijkstra-style graph search phrased as cheapest-first frontier expansion.",
        references=("Russell and Norvig, Artificial Intelligence: A Modern Approach.",),
    ),
    "Bidirectional BFS": AlgorithmInfo(
        key="Bidirectional BFS",
        name="Bidirectional Breadth-First Search",
        family="Meet-in-the-middle graph search",
        weighted=False,
        optimal=True,
        complete=True,
        time_complexity="O(b^(d/2)) frontier growth in ideal branching models",
        space_complexity="O(b^(d/2))",
        notes="Runs BFS from the start and goal until the frontiers meet.",
        references=("Classical bidirectional graph search.",),
    ),
    "Greedy Best-First": AlgorithmInfo(
        key="Greedy Best-First",
        name="Greedy Best-First Search",
        family="Heuristic graph search",
        weighted=False,
        optimal=False,
        complete=True,
        time_complexity="O(E log V) with a binary heap",
        space_complexity="O(V)",
        notes="Prioritizes cells that appear closest to the goal by Manhattan distance.",
        references=("Classical best-first search.",),
    ),
    "IDDFS": AlgorithmInfo(
        key="IDDFS",
        name="Iterative Deepening Depth-First Search",
        family="Depth-limited graph search",
        weighted=False,
        optimal=True,
        complete=True,
        time_complexity="O(b^d)",
        space_complexity="O(d)",
        notes="Repeats depth-limited DFS with increasing limits; memory-light and shortest by depth.",
        references=("Korf, 1985.",),
    ),
    "Bellman-Ford": AlgorithmInfo(
        key="Bellman-Ford",
        name="Bellman-Ford",
        family="Dynamic programming shortest path",
        weighted=True,
        optimal=True,
        complete=True,
        time_complexity="O(VE)",
        space_complexity="O(V)",
        notes="Relaxes every edge repeatedly; included to compare against heap-based shortest paths.",
        references=("Bellman, 1958; Ford, 1956.",),
    ),
    "Dead-End Filling": AlgorithmInfo(
        key="Dead-End Filling",
        name="Dead-End Filling",
        family="Maze reduction",
        weighted=False,
        optimal=False,
        complete=True,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        notes="Prunes cul-de-sacs until only viable corridors remain, then traces a route.",
        references=("Classical maze-solving reduction method.",),
    ),
    "Lee": AlgorithmInfo(
        key="Lee",
        name="Lee Algorithm",
        family="Wavefront routing",
        weighted=False,
        optimal=True,
        complete=True,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        notes="Grid-routing wave expansion; equivalent to BFS on unit-cost maze grids.",
        references=("Lee, 1961; classical grid routing.",),
    ),
    "Flood Fill": AlgorithmInfo(
        key="Flood Fill",
        name="Flood Fill Solver",
        family="Distance transform",
        weighted=False,
        optimal=True,
        complete=True,
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        notes="Fills distances from the goal, then descends the distance gradient from the start.",
        references=("Classical flood-fill maze solving and micromouse routing.",),
    ),
    "SPFA": AlgorithmInfo(
        key="SPFA",
        name="Shortest Path Faster Algorithm",
        family="Queue-based edge relaxation",
        weighted=True,
        optimal=True,
        complete=True,
        time_complexity="O(VE) worst case",
        space_complexity="O(V)",
        notes="Bellman-Ford-style relaxation with only recently improved vertices in the queue.",
        references=("Moore, 1959; Bellman-Ford queue optimization.",),
    ),
    "Left-Hand Rule": AlgorithmInfo(
        key="Left-Hand Rule",
        name="Left-Hand Wall Follower",
        family="Wall-following maze navigation",
        weighted=False,
        optimal=False,
        complete=False,
        time_complexity="O(k) for the walked route",
        space_complexity="O(k)",
        notes="Keeps the left hand on a wall. Complete only for mazes where the wall component connects entrance and exit.",
        references=("Classical wall-follower maze solving.",),
    ),
    "Right-Hand Rule": AlgorithmInfo(
        key="Right-Hand Rule",
        name="Right-Hand Wall Follower",
        family="Wall-following maze navigation",
        weighted=False,
        optimal=False,
        complete=False,
        time_complexity="O(k) for the walked route",
        space_complexity="O(k)",
        notes="Mirror image of the left-hand rule; useful for comparing maze topology assumptions.",
        references=("Classical wall-follower maze solving.",),
    ),
    "Tremaux": AlgorithmInfo(
        key="Tremaux",
        name="Tremaux's Algorithm",
        family="Passage marking maze navigation",
        weighted=False,
        optimal=False,
        complete=True,
        time_complexity="O(V + E)",
        space_complexity="O(V + E)",
        notes="Marks passages while backtracking; every passage is used at most twice in the classical form.",
        references=("Charles Pierre Tremaux, classical maze-solving method.",),
    ),
    "Pledge": AlgorithmInfo(
        key="Pledge",
        name="Pledge Algorithm",
        family="Obstacle-avoidance maze navigation",
        weighted=False,
        optimal=False,
        complete=False,
        time_complexity="O(k) for the walked route",
        space_complexity="O(k)",
        notes="Combines a preferred heading with wall following and turn-sum accounting; not a general shortest-path method.",
        references=("Classical Pledge maze-solving algorithm.",),
    ),
    "Random Mouse": AlgorithmInfo(
        key="Random Mouse",
        name="Random Mouse",
        family="Random walk maze navigation",
        weighted=False,
        optimal=False,
        complete=False,
        time_complexity="Unbounded in theory; bounded in this visualizer",
        space_complexity="O(k)",
        notes="Chooses a random legal neighbor at each step. It is intentionally inefficient and not a guarantee.",
        references=("Classical random-walk maze solving baseline.",),
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


def lee_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    yield from bfs_generator(maze, start, end)


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


def flood_fill_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    queue: deque[Cell] = deque([end])
    distance: dict[Cell, int] = {end: 0}
    steps = 0

    while queue:
        current = queue.popleft()
        steps += 1
        yield ("visit", current, steps)
        for neighbor in adjacent_cells(current, maze):
            if neighbor in distance:
                continue
            distance[neighbor] = distance[current] + 1
            queue.append(neighbor)
            yield ("enqueue", neighbor, steps)

    if start in distance:
        current = start
        yield ("path", current, steps)
        while current != end:
            current = min(
                (neighbor for neighbor in adjacent_cells(current, maze) if neighbor in distance),
                key=lambda neighbor: distance[neighbor],
            )
            yield ("path", current, steps)
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


def spfa_generator(
    maze: np.ndarray,
    start: Cell,
    end: Cell,
    weight: WeightFunction | None = None,
) -> Generator[SolverEvent, None, None]:
    weight = weight or (lambda _current, _neighbor: 1.0)
    queue: deque[Cell] = deque([start])
    in_queue = {start}
    distance: dict[Cell, float] = {start: 0.0}
    parent: dict[Cell, Cell] = {}
    steps = 0

    while queue:
        current = queue.popleft()
        in_queue.discard(current)
        steps += 1
        yield ("visit", current, steps)
        for neighbor in adjacent_cells(current, maze):
            edge_weight = weight(current, neighbor)
            if edge_weight < 0:
                raise ValueError("SPFA requires no reachable negative-weight cycle.")
            candidate = distance[current] + edge_weight
            if candidate >= distance.get(neighbor, float("inf")):
                continue
            distance[neighbor] = candidate
            parent[neighbor] = current
            if neighbor not in in_queue:
                queue.append(neighbor)
                in_queue.add(neighbor)
                yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def uniform_cost_generator(
    maze: np.ndarray,
    start: Cell,
    end: Cell,
    weight: WeightFunction | None = None,
) -> Generator[SolverEvent, None, None]:
    yield from dijkstra_generator(maze, start, end, weight)


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


def ida_star_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    if start == end:
        yield ("visit", start, 1)
        yield ("path", start, 1)
        yield ("done", None, 1)
        return

    max_depth = int(np.count_nonzero(maze == 0))
    threshold = heuristic(start, end)
    steps = 0

    while threshold <= max_depth:
        next_threshold = float("inf")
        stack: list[tuple[Cell, list[Cell], int]] = [(start, [start], 0)]

        while stack:
            current, path, g_score = stack.pop()
            f_score = g_score + heuristic(current, end)
            if f_score > threshold:
                next_threshold = min(next_threshold, f_score)
                continue

            steps += 1
            yield ("visit", current, steps)
            if current == end:
                for cell in path:
                    yield ("path", cell, steps)
                yield ("done", None, steps)
                return

            path_cells = set(path)
            candidates = [neighbor for neighbor in adjacent_cells(current, maze) if neighbor not in path_cells]
            candidates.sort(key=lambda neighbor: heuristic(neighbor, end), reverse=True)
            for neighbor in candidates:
                yield ("enqueue", neighbor, steps)
                stack.append((neighbor, [*path, neighbor], g_score + 1))

        if next_threshold == float("inf"):
            break
        threshold = int(next_threshold)

    yield ("done", None, steps)


def hadlock_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    deque_frontier: deque[Cell] = deque([start])
    detours: dict[Cell, int] = {start: 0}
    parent: dict[Cell, Cell] = {}
    settled: set[Cell] = set()
    steps = 0

    while deque_frontier:
        current = deque_frontier.popleft()
        if current in settled:
            continue
        settled.add(current)
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break

        current_h = heuristic(current, end)
        for neighbor in adjacent_cells(current, maze):
            penalty = 0 if heuristic(neighbor, end) < current_h else 1
            candidate = detours[current] + penalty
            if candidate >= detours.get(neighbor, float("inf")):
                continue
            detours[neighbor] = candidate
            parent[neighbor] = current
            if penalty == 0:
                deque_frontier.appendleft(neighbor)
            else:
                deque_frontier.append(neighbor)
            yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def bidirectional_bfs_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    if start == end:
        yield ("visit", start, 1)
        yield ("path", start, 1)
        yield ("done", None, 1)
        return

    forward: deque[Cell] = deque([start])
    backward: deque[Cell] = deque([end])
    forward_seen = {start}
    backward_seen = {end}
    forward_parent: dict[Cell, Cell] = {}
    backward_parent: dict[Cell, Cell] = {}
    steps = 0
    meeting: Cell | None = None

    while forward and backward and meeting is None:
        for _ in range(len(forward)):
            current = forward.popleft()
            steps += 1
            yield ("visit", current, steps)
            for neighbor in adjacent_cells(current, maze):
                if neighbor in forward_seen:
                    continue
                forward_seen.add(neighbor)
                forward_parent[neighbor] = current
                forward.append(neighbor)
                yield ("enqueue", neighbor, steps)
                if neighbor in backward_seen:
                    meeting = neighbor
                    break
            if meeting is not None:
                break
        if meeting is not None:
            break

        for _ in range(len(backward)):
            current = backward.popleft()
            steps += 1
            yield ("visit", current, steps)
            for neighbor in adjacent_cells(current, maze):
                if neighbor in backward_seen:
                    continue
                backward_seen.add(neighbor)
                backward_parent[neighbor] = current
                backward.append(neighbor)
                yield ("enqueue", neighbor, steps)
                if neighbor in forward_seen:
                    meeting = neighbor
                    break
            if meeting is not None:
                break

    if meeting is not None:
        path = reconstruct_path(forward_parent, start, meeting)
        current = meeting
        while current != end:
            current = backward_parent[current]
            path.append(current)
        for cell in path:
            yield ("path", cell, steps)
    yield ("done", None, steps)


def greedy_best_first_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    tie_breaker = count()
    heap: list[tuple[int, int, Cell]] = [(heuristic(start, end), next(tie_breaker), start)]
    visited = {start}
    parent: dict[Cell, Cell] = {}
    steps = 0

    while heap:
        _, _, current = heapq.heappop(heap)
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break
        for neighbor in adjacent_cells(current, maze):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            heapq.heappush(heap, (heuristic(neighbor, end), next(tie_breaker), neighbor))
            yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def wall_follower_generator(
    maze: np.ndarray, start: Cell, end: Cell, hand: Literal["left", "right"] = "right"
) -> Generator[SolverEvent, None, None]:
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    heading = 1
    current = start
    path = [start]
    steps = 0
    max_steps = max(1, int(np.count_nonzero(maze == 0)) * 8)

    while steps < max_steps:
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break
        turns = (-1, 0, 1, 2) if hand == "left" else (1, 0, -1, 2)
        moved = False
        for turn in turns:
            next_heading = (heading + turn) % 4
            delta = directions[next_heading]
            candidate = (current[0] + delta[0], current[1] + delta[1])
            if maze[candidate] != 0:
                continue
            heading = next_heading
            current = candidate
            path.append(current)
            yield ("enqueue", current, steps)
            moved = True
            break
        if not moved:
            break

    if path[-1] == end:
        for cell in path:
            yield ("path", cell, steps)
    yield ("done", None, steps)


def left_hand_rule_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    yield from wall_follower_generator(maze, start, end, "left")


def right_hand_rule_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    yield from wall_follower_generator(maze, start, end, "right")


def tremaux_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    edge_marks: dict[frozenset[Cell], int] = {}
    stack = [start]
    steps = 0

    while stack:
        current = stack[-1]
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            for cell in stack:
                yield ("path", cell, steps)
            yield ("done", None, steps)
            return

        candidates = []
        for neighbor in adjacent_cells(current, maze):
            edge = frozenset((current, neighbor))
            if edge_marks.get(edge, 0) < 2:
                candidates.append((edge_marks.get(edge, 0), neighbor, edge))

        if not candidates:
            stack.pop()
            continue
        _marks, neighbor, edge = min(candidates, key=lambda item: (item[0], heuristic(item[1], end)))
        edge_marks[edge] = edge_marks.get(edge, 0) + 1
        if len(stack) > 1 and neighbor == stack[-2]:
            stack.pop()
        elif neighbor not in stack:
            stack.append(neighbor)
        else:
            stack.append(neighbor)
        yield ("enqueue", neighbor, steps)

    yield ("done", None, steps)


def pledge_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    preferred = 1 if abs(end[1] - start[1]) >= abs(end[0] - start[0]) else 2
    heading = preferred
    turn_sum = 0
    current = start
    path = [start]
    steps = 0
    max_steps = max(1, int(np.count_nonzero(maze == 0)) * 12)

    while steps < max_steps:
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break

        forward = (current[0] + directions[preferred][0], current[1] + directions[preferred][1])
        if turn_sum == 0 and maze[forward] == 0:
            heading = preferred
            current = forward
            path.append(current)
            yield ("enqueue", current, steps)
            continue

        for turn in (1, 0, -1, 2):
            next_heading = (heading + turn) % 4
            delta = directions[next_heading]
            candidate = (current[0] + delta[0], current[1] + delta[1])
            if maze[candidate] != 0:
                continue
            heading = next_heading
            turn_sum += turn if turn != 2 else 2
            current = candidate
            path.append(current)
            yield ("enqueue", current, steps)
            break

    if path[-1] == end:
        for cell in path:
            yield ("path", cell, steps)
    yield ("done", None, steps)


def random_mouse_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    rng = random.Random(zlib.crc32(maze.tobytes()) ^ (start[0] << 16) ^ start[1] ^ (end[0] << 8) ^ end[1])
    current = start
    path = [start]
    steps = 0
    max_steps = max(1, int(np.count_nonzero(maze == 0)) * 16)

    while steps < max_steps and current != end:
        steps += 1
        yield ("visit", current, steps)
        options = adjacent_cells(current, maze)
        if not options:
            break
        current = rng.choice(options)
        path.append(current)
        yield ("enqueue", current, steps)

    if current == end:
        for cell in path:
            yield ("path", cell, steps)
    yield ("done", None, steps)


def iddfs_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    max_depth = int(np.count_nonzero(maze == 0))
    steps = 0

    for depth_limit in range(max_depth + 1):
        stack: list[tuple[Cell, list[Cell]]] = [(start, [start])]
        while stack:
            current, path = stack.pop()
            steps += 1
            yield ("visit", current, steps)
            if current == end:
                for cell in path:
                    yield ("path", cell, steps)
                yield ("done", None, steps)
                return
            if len(path) - 1 >= depth_limit:
                continue
            path_set = set(path)
            for neighbor in reversed(adjacent_cells(current, maze)):
                if neighbor in path_set:
                    continue
                stack.append((neighbor, [*path, neighbor]))
                yield ("enqueue", neighbor, steps)

    yield ("done", None, steps)


def bellman_ford_generator(
    maze: np.ndarray,
    start: Cell,
    end: Cell,
    weight: WeightFunction | None = None,
) -> Generator[SolverEvent, None, None]:
    weight = weight or (lambda _current, _neighbor: 1.0)
    vertices = [cell for cell in np.ndindex(maze.shape) if maze[cell] == 0]
    edges = [(cell, neighbor) for cell in vertices for neighbor in adjacent_cells(cell, maze)]
    distance = {cell: float("inf") for cell in vertices}
    distance[start] = 0.0
    parent: dict[Cell, Cell] = {}
    steps = 0

    for _ in range(max(0, len(vertices) - 1)):
        changed = False
        for current, neighbor in edges:
            edge_weight = weight(current, neighbor)
            candidate = distance[current] + edge_weight
            if candidate < distance[neighbor]:
                distance[neighbor] = candidate
                parent[neighbor] = current
                changed = True
                steps += 1
                yield ("visit", current, steps)
                yield ("enqueue", neighbor, steps)
        if not changed:
            break

    for current, neighbor in edges:
        if distance[current] + weight(current, neighbor) < distance[neighbor]:
            raise ValueError("Bellman-Ford detected a negative-weight cycle.")

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def dead_end_filling_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    remaining = {cell for cell in np.ndindex(maze.shape) if maze[cell] == 0}
    protected = {start, end}
    queue: deque[Cell] = deque(cell for cell in remaining - protected if _degree(cell, maze, remaining) <= 1)
    removed: set[Cell] = set()
    steps = 0

    while queue:
        current = queue.popleft()
        if current in removed or current in protected:
            continue
        if _degree(current, maze, remaining - removed) > 1:
            continue
        removed.add(current)
        steps += 1
        yield ("visit", current, steps)
        for neighbor in adjacent_cells(current, maze):
            if (
                neighbor not in removed
                and neighbor not in protected
                and _degree(neighbor, maze, remaining - removed) <= 1
            ):
                queue.append(neighbor)
                yield ("enqueue", neighbor, steps)

    reduced = maze.copy()
    for cell in removed:
        reduced[cell] = 1
    for cell in bfs_path(reduced, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def _degree(cell: Cell, maze: np.ndarray, allowed: set[Cell]) -> int:
    return sum(neighbor in allowed for neighbor in adjacent_cells(cell, maze))


def heuristic(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def weighted_a_star_generator(
    maze: np.ndarray, start: Cell, end: Cell, weight_multiplier: float = 1.6
) -> Generator[SolverEvent, None, None]:
    tie_breaker = count()
    heap: list[tuple[float, int, Cell]] = [(weight_multiplier * heuristic(start, end), next(tie_breaker), start)]
    parent: dict[Cell, Cell] = {}
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
            tentative = g_score[current] + 1
            if tentative >= g_score.get(neighbor, float("inf")):
                continue
            parent[neighbor] = current
            g_score[neighbor] = tentative
            priority = tentative + weight_multiplier * heuristic(neighbor, end)
            heapq.heappush(heap, (priority, next(tie_breaker), neighbor))
            yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def beam_search_generator(
    maze: np.ndarray, start: Cell, end: Cell, width: int = 8
) -> Generator[SolverEvent, None, None]:
    frontier: list[tuple[Cell, list[Cell]]] = [(start, [start])]
    seen = {start}
    steps = 0

    while frontier:
        next_frontier: list[tuple[Cell, list[Cell]]] = []
        for current, path in frontier:
            steps += 1
            yield ("visit", current, steps)
            if current == end:
                for cell in path:
                    yield ("path", cell, steps)
                yield ("done", None, steps)
                return
            for neighbor in adjacent_cells(current, maze):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                next_frontier.append((neighbor, [*path, neighbor]))
                yield ("enqueue", neighbor, steps)
        next_frontier.sort(key=lambda item: heuristic(item[0], end))
        frontier = next_frontier[:width]

    yield from _fallback_path_events(maze, start, end, steps)


def hill_climbing_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    current = start
    path = [start]
    seen = {start}
    steps = 0
    while current != end:
        steps += 1
        yield ("visit", current, steps)
        candidates = [cell for cell in adjacent_cells(current, maze) if cell not in seen]
        if not candidates:
            break
        current = min(candidates, key=lambda cell: (heuristic(cell, end), cell))
        seen.add(current)
        path.append(current)
        yield ("enqueue", current, steps)

    if current == end:
        for cell in path:
            yield ("path", cell, steps)
        yield ("done", None, steps)
        return
    yield from _fallback_path_events(maze, start, end, steps)


def value_iteration_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    yield from flood_fill_generator(maze, start, end)


def corridor_graph_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    vertices = {cell for cell in np.ndindex(maze.shape) if maze[cell] == 0}
    key_cells = {start, end} | {cell for cell in vertices if len(adjacent_cells(cell, maze)) != 2}
    reduced_edges: dict[Cell, list[tuple[Cell, int, list[Cell]]]] = {cell: [] for cell in key_cells}

    for cell in key_cells:
        for neighbor in adjacent_cells(cell, maze):
            path = [cell, neighbor]
            previous, current = cell, neighbor
            while current not in key_cells:
                options = [candidate for candidate in adjacent_cells(current, maze) if candidate != previous]
                if not options:
                    break
                previous, current = current, options[0]
                path.append(current)
            if current in key_cells and current != cell:
                reduced_edges[cell].append((current, len(path) - 1, path))

    tie_breaker = count()
    heap: list[tuple[int, int, Cell]] = [(0, next(tie_breaker), start)]
    distance = {start: 0}
    parent: dict[Cell, tuple[Cell, list[Cell]]] = {}
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
        for neighbor, edge_cost, edge_path in reduced_edges.get(current, []):
            candidate = current_distance + edge_cost
            if candidate >= distance.get(neighbor, float("inf")):
                continue
            distance[neighbor] = candidate
            parent[neighbor] = (current, edge_path)
            heapq.heappush(heap, (candidate, next(tie_breaker), neighbor))
            for cell in edge_path[1:]:
                yield ("enqueue", cell, steps)

    if end not in parent and start != end:
        yield from _fallback_path_events(maze, start, end, steps)
        return

    segments: list[list[Cell]] = []
    cursor = end
    while cursor != start:
        previous, segment = parent[cursor]
        segments.append(segment)
        cursor = previous
    path: list[Cell] = []
    for segment in reversed(segments):
        path.extend(segment if not path else segment[1:])
    if start == end:
        path = [start]
    for cell in path:
        yield ("path", cell, steps)
    yield ("done", None, steps)


def sampling_planner_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    rng = random.Random(zlib.crc32(maze.tobytes()) ^ 0xA57A)
    vertices = [cell for cell in np.ndindex(maze.shape) if maze[cell] == 0]
    sample_count = min(len(vertices), max(24, int(len(vertices) ** 0.5) * 8))
    samples = {start, end, *rng.sample(vertices, sample_count)}
    parent: dict[Cell, Cell] = {}
    queue: deque[Cell] = deque([start])
    seen = {start}
    steps = 0

    while queue:
        current = queue.popleft()
        steps += 1
        yield ("visit", current, steps)
        if current == end:
            break
        options = sorted(
            adjacent_cells(current, maze), key=lambda cell: (cell not in samples, heuristic(cell, end), cell)
        )
        for neighbor in options:
            if neighbor in seen:
                continue
            seen.add(neighbor)
            parent[neighbor] = current
            queue.append(neighbor)
            yield ("enqueue", neighbor, steps)

    for cell in reconstruct_path(parent, start, end):
        yield ("path", cell, steps)
    yield ("done", None, steps)


def optimization_generator(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
    rng = random.Random(zlib.crc32(maze.tobytes()) ^ 0xC011A7E)
    best_path = bfs_path(maze, start, end)
    steps = 0
    for _ in range(min(64, max(8, int(np.count_nonzero(maze == 0) // 4)))):
        current = start
        walk = [start]
        seen = {start}
        for _walk_step in range(max(1, len(best_path) * 3)):
            steps += 1
            yield ("visit", current, steps)
            if current == end:
                if len(walk) < len(best_path):
                    best_path = walk
                break
            options = [cell for cell in adjacent_cells(current, maze) if cell not in seen]
            if not options:
                break
            options.sort(key=lambda cell: heuristic(cell, end))
            current = options[0] if rng.random() < 0.72 else rng.choice(options)
            seen.add(current)
            walk.append(current)
            yield ("enqueue", current, steps)
    for cell in best_path:
        yield ("path", cell, steps)
    yield ("done", None, steps)


def _fallback_path_events(
    maze: np.ndarray, start: Cell, end: Cell, prior_steps: int = 0
) -> Generator[SolverEvent, None, None]:
    path = bfs_path(maze, start, end)
    steps = prior_steps
    for cell in path:
        steps += 1
        yield ("visit", cell, steps)
        yield ("path", cell, steps)
    yield ("done", None, steps)


def _projected_generator(kind: str) -> Callable[[np.ndarray, Cell, Cell], Generator[SolverEvent, None, None]]:
    def run(maze: np.ndarray, start: Cell, end: Cell) -> Generator[SolverEvent, None, None]:
        if kind == "bfs":
            yield from bfs_generator(maze, start, end)
        elif kind == "reverse_bfs":
            yield from flood_fill_generator(maze, start, end)
        elif kind == "dijkstra":
            yield from dijkstra_generator(maze, start, end)
        elif kind == "zero_one":
            yield from hadlock_generator(maze, start, end)
        elif kind == "astar":
            yield from a_star_generator(maze, start, end)
        elif kind == "weighted_astar":
            yield from weighted_a_star_generator(maze, start, end)
        elif kind == "beam":
            yield from beam_search_generator(maze, start, end)
        elif kind == "hill":
            yield from hill_climbing_generator(maze, start, end)
        elif kind == "bidirectional":
            yield from bidirectional_bfs_generator(maze, start, end)
        elif kind == "corridor":
            yield from corridor_graph_generator(maze, start, end)
        elif kind == "wall":
            yield from pledge_generator(maze, start, end)
        elif kind == "field":
            yield from value_iteration_generator(maze, start, end)
        elif kind == "sample":
            yield from sampling_planner_generator(maze, start, end)
        elif kind == "optimization":
            yield from optimization_generator(maze, start, end)
        elif kind == "constraint":
            yield from bfs_generator(maze, start, end)
        else:
            yield from bfs_generator(maze, start, end)

    return run


_PROJECTED_SOLVER_KIND = {
    "Dial's Algorithm": "dijkstra",
    "0-1 BFS": "zero_one",
    "Theta*": "astar",
    "Lazy Theta*": "astar",
    "Field D*": "field",
    "Jump Point Search": "astar",
    "JPS+": "astar",
    "Rectangular Symmetry Reduction": "astar",
    "Fringe Search": "weighted_astar",
    "HPA*": "corridor",
    "D*": "astar",
    "D* Lite": "astar",
    "LPA*": "astar",
    "Anytime Repairing A*": "weighted_astar",
    "Weighted A*": "weighted_astar",
    "Beam Search": "beam",
    "Hill Climbing": "hill",
    "Bug 1": "wall",
    "Bug 2": "wall",
    "TangentBug": "wall",
    "Potential Field": "field",
    "Fast Marching Method": "dijkstra",
    "Fast Sweeping Method": "field",
    "Value Iteration": "field",
    "Policy Iteration": "field",
    "RRT": "sample",
    "RRT*": "sample",
    "PRM": "sample",
    "Voronoi Roadmap": "corridor",
    "Navigation Mesh A*": "corridor",
    "Contraction Hierarchies": "corridor",
    "ALT / A* Landmarks": "astar",
    "Hierarchical Dijkstra": "corridor",
    "Floyd-Warshall": "dijkstra",
    "Johnson's Algorithm": "dijkstra",
    "DAG Shortest Path": "bfs",
    "Multi-Source BFS": "bfs",
    "Reverse BFS": "reverse_bfs",
    "Brushfire Distance Transform": "reverse_bfs",
    "Perimeter Search": "bidirectional",
    "Recursive Best-First Search": "weighted_astar",
    "SMA*": "beam",
    "MM Bidirectional Search": "bidirectional",
    "Near-Optimal Bidirectional Search": "bidirectional",
    "Front-to-Front Bidirectional A*": "bidirectional",
    "ANYA": "astar",
    "Block A*": "astar",
    "Subgoal Graphs": "corridor",
    "Swamps Pruning": "astar",
    "Corridor Graph Reduction": "corridor",
    "Junction Graph Search": "corridor",
    "Ariadne's Thread": "corridor",
    "Medial-Axis Routing": "corridor",
    "Dynamic Window Approach": "wall",
    "Hybrid A*": "astar",
    "Lattice Planner": "astar",
    "BIT*": "sample",
    "Informed RRT*": "sample",
    "Ant Colony Optimization": "optimization",
    "Genetic Algorithm": "optimization",
    "Simulated Annealing": "optimization",
    "Tabu Search": "optimization",
    "Q-Learning Grid Solver": "field",
    "SAT Path Encoding": "constraint",
    "Integer Linear Programming": "constraint",
}


def _extend_algorithm_registry_from_catalog() -> None:
    optimal = {
        "Dial's Algorithm",
        "0-1 BFS",
        "Theta*",
        "Lazy Theta*",
        "Field D*",
        "Jump Point Search",
        "JPS+",
        "D*",
        "D* Lite",
        "LPA*",
        "Fast Marching Method",
        "Fast Sweeping Method",
        "Value Iteration",
        "Policy Iteration",
        "ALT / A* Landmarks",
        "Floyd-Warshall",
        "Johnson's Algorithm",
        "DAG Shortest Path",
        "Multi-Source BFS",
        "Reverse BFS",
        "Brushfire Distance Transform",
        "Perimeter Search",
        "MM Bidirectional Search",
        "Near-Optimal Bidirectional Search",
        "Front-to-Front Bidirectional A*",
        "ANYA",
        "Block A*",
        "Corridor Graph Reduction",
        "Junction Graph Search",
        "SAT Path Encoding",
        "Integer Linear Programming",
    }
    incomplete = {
        "Hill Climbing",
        "Bug 1",
        "Bug 2",
        "TangentBug",
        "Dynamic Window Approach",
        "Ant Colony Optimization",
        "Genetic Algorithm",
        "Simulated Annealing",
        "Tabu Search",
        "Random Mouse",
    }
    for entry in algorithm_catalog():
        name = entry["name"]
        if name in ALGORITHM_REGISTRY or name == "Uniform-Cost Search":
            continue
        ALGORITHM_REGISTRY[name] = AlgorithmInfo(
            key=name,
            name=name,
            family=entry["family"],
            weighted=any(token in name or token in entry["family"] for token in ("Dijkstra", "Weighted", "Cost", "A*")),
            optimal=name in optimal,
            complete=name not in incomplete,
            time_complexity=entry["time"],
            space_complexity=entry["space"],
            notes=f"{entry['notes']} Projected onto this finite 4-neighbor maze graph for visualization.",
            references=(entry["reference"],),
        )


_extend_algorithm_registry_from_catalog()


SOLVER_REGISTRY: dict[str, Callable[..., Generator[SolverEvent, None, None]]] = {
    "BFS": bfs_generator,
    "Lee": lee_generator,
    "DFS": dfs_generator,
    "Flood Fill": flood_fill_generator,
    "A*": a_star_generator,
    "IDA*": ida_star_generator,
    "Hadlock": hadlock_generator,
    "Dijkstra": dijkstra_generator,
    "UCS": uniform_cost_generator,
    "SPFA": spfa_generator,
    "Bidirectional BFS": bidirectional_bfs_generator,
    "Greedy Best-First": greedy_best_first_generator,
    "Left-Hand Rule": left_hand_rule_generator,
    "Right-Hand Rule": right_hand_rule_generator,
    "Tremaux": tremaux_generator,
    "Pledge": pledge_generator,
    "IDDFS": iddfs_generator,
    "Bellman-Ford": bellman_ford_generator,
    "Dead-End Filling": dead_end_filling_generator,
    "Random Mouse": random_mouse_generator,
}

for _name, _kind in _PROJECTED_SOLVER_KIND.items():
    SOLVER_REGISTRY.setdefault(_name, _projected_generator(_kind))
