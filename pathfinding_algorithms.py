# pathfinding_algorithms.py

from collections import deque
import heapq

def get_adjacent_cells(cell, maze):
    row, col = cell
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    neighbors = []
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < maze.shape[0] and 0 <= c < maze.shape[1] and maze[r][c] == 0:
            neighbors.append((r, c))
    return neighbors

def bfs_generator(maze, start, end):
    queue = deque([start])
    visited = set()
    visited.add(start)
    parent = {}
    steps = 0

    while queue:
        current = queue.popleft()
        steps += 1
        yield ('visit', current, steps)
        if current == end:
            break
        for neighbor in get_adjacent_cells(current, maze):
            if neighbor not in visited:
                queue.append(neighbor)
                visited.add(neighbor)
                parent[neighbor] = current
                yield ('enqueue', neighbor, steps)

    # Reconstruct path
    path = []
    if end in parent:
        cell = end
        while cell != start:
            path.append(cell)
            cell = parent[cell]
        path.append(start)
        path.reverse()
        for cell in path:
            yield ('path', cell, steps)
    yield ('done', None, steps)

def dfs_generator(maze, start, end):
    stack = [start]
    visited = set()
    visited.add(start)
    parent = {}
    steps = 0

    while stack:
        current = stack.pop()
        steps += 1
        yield ('visit', current, steps)
        if current == end:
            break
        for neighbor in reversed(get_adjacent_cells(current, maze)):
            if neighbor not in visited:
                stack.append(neighbor)
                visited.add(neighbor)
                parent[neighbor] = current
                yield ('enqueue', neighbor, steps)

    # Reconstruct path
    path = []
    if end in parent:
        cell = end
        while cell != start:
            path.append(cell)
            cell = parent[cell]
        path.append(start)
        path.reverse()
        for cell in path:
            yield ('path', cell, steps)
    yield ('done', None, steps)

def a_star_generator(maze, start, end):
    heap = []
    heapq.heappush(heap, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    steps = 0

    while heap:
        _, current = heapq.heappop(heap)
        steps += 1
        yield ('visit', current, steps)
        if current == end:
            break
        for neighbor in get_adjacent_cells(current, maze):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score_neighbor = tentative_g + heuristic(neighbor, end)
                f_score[neighbor] = f_score_neighbor
                heapq.heappush(heap, (f_score_neighbor, neighbor))
                yield ('enqueue', neighbor, steps)

    # Reconstruct path
    path = []
    if end in came_from:
        cell = end
        while cell != start:
            path.append(cell)
            cell = came_from[cell]
        path.append(start)
        path.reverse()
        for cell in path:
            yield ('path', cell, steps)
    yield ('done', None, steps)

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

