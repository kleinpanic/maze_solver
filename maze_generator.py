import numpy as np
import random
from collections import deque

def generate_maze(rows, cols, generation_algorithm="Recursive Backtracker", seed=None, wall_density=0.3, dead_ends=10, branching_factor=3, connectedness=70):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    else:
        seed = random.randint(0, 999999)  # Generate a random seed if not provided
    
    # Adjust wall density and complexity based on difficulty
    adjusted_wall_density = min(wall_density, 0.7)  # Cap wall density for solvability

    maze = None
    is_solved = False

    # Use a loop to regenerate maze if unsolvable
    while not is_solved:
        if generation_algorithm == "Recursive Backtracker":
            maze = recursive_backtracker_maze(rows, cols, adjusted_wall_density, dead_ends, branching_factor, connectedness)
        elif generation_algorithm == "Prim's":
            maze = prim_maze(rows, cols, adjusted_wall_density, dead_ends, branching_factor, connectedness)
        else:
            raise ValueError(f"Unknown generation algorithm: {generation_algorithm}")

        # Check if the generated maze is solvable
        is_solved = is_solvable(maze, (1, 1), (rows - 2, cols - 2))

    return maze, seed  # Return the generated maze along with the seed

def recursive_backtracker_maze(rows, cols, wall_density, dead_ends, branching_factor, connectedness):
    maze = np.ones((rows, cols), dtype=int)

    # Initialize the stack with the starting point
    stack = [(1, 1)]
    maze[1][1] = 0  # Start point

    # Track the main path
    main_path = []

    while stack:
        r, c = stack[-1]
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        carved = False

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows-1 and 0 < nc < cols-1 and maze[nr][nc] == 1:
                maze[nr - dr//2][nc - dc//2] = 0  # Remove wall between
                maze[nr][nc] = 0  # Mark the next cell as a passage
                stack.append((nr, nc))
                carved = True
                main_path.append((nr, nc))
                break

        if not carved:
            stack.pop()  # Backtrack if no carving was possible

    # Ensure connectedness to the main path
    required_connections = int(len(main_path) * (connectedness / 100))
    for _ in range(required_connections):
        r, c = random.choice(main_path)
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and maze[nr][nc] == 1:
                maze[nr - dr // 2][nc - dc // 2] = 0  # Remove wall between
                maze[nr][nc] = 0  # Create a connection to the main path
                break

    # Create branches based on branching_factor
    for _ in range(branching_factor):
        if len(main_path) > 2:
            r, c = random.choice(main_path)
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 < nr < rows-1 and 0 < nc < cols-1 and maze[nr][nc] == 1:
                    maze[nr - dr//2][nc - dc//2] = 0  # Remove wall between
                    maze[nr][nc] = 0  # Create a branch
                    break

    # Create dead ends based on dead_ends
    for _ in range(dead_ends):
        r, c = random.randint(1, rows-2), random.randint(1, cols-2)
        if maze[r][c] == 0:
            maze[r][c] = 1  # Add a dead end

    # Add random walls based on wall_density
    for r in range(1, rows-1):
        for c in range(1, cols-1):
            if maze[r][c] == 0 and random.random() < wall_density * 0.1:
                maze[r][c] = 1  # Add wall

    return maze

def prim_maze(rows, cols, wall_density, dead_ends, branching_factor, connectedness):
    maze = np.ones((rows, cols), dtype=int)
    start_r, start_c = 1, 1
    maze[start_r][start_c] = 0
    walls = []
    main_path = [(start_r, start_c)]  # Track the main path
    
    def add_walls(r, c):
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows-1 and 0 < nc < cols-1 and maze[nr][nc] == 1:
                walls.append((nr, nc, r, c))
    
    add_walls(start_r, start_c)
    
    while walls:
        idx = random.randint(0, len(walls)-1)
        wall = walls.pop(idx)
        wr, wc, pr, pc = wall
        opposite_r, opposite_c = wr + (wr - pr), wc + (wc - pc)
        if 0 < opposite_r < rows-1 and 0 < opposite_c < cols-1:
            if maze[opposite_r][opposite_c] == 1:
                maze[wr][wc] = 0
                maze[opposite_r][opposite_c] = 0
                main_path.append((opposite_r, opposite_c))
                add_walls(opposite_r, opposite_c)

    # Ensure connectedness to the main path
    required_connections = int(len(main_path) * (connectedness / 100))
    for _ in range(required_connections):
        r, c = random.choice(main_path)
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and maze[nr][nc] == 1:
                maze[nr - dr // 2][nc - dc // 2] = 0  # Remove wall between
                maze[nr][nc] = 0  # Create a connection to the main path
                break

    # Create branches based on branching_factor
    for _ in range(branching_factor):
        if len(main_path) > 2:
            r, c = random.choice(main_path)
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 < nr < rows-1 and 0 < nc < cols-1 and maze[nr][nc] == 1:
                    maze[nr - dr//2][nc - dc//2] = 0  # Remove wall between
                    maze[nr][nc] = 0  # Create a branch
                    break

    # Create dead ends based on dead_ends
    for _ in range(dead_ends):
        r, c = random.randint(1, rows-2), random.randint(1, cols-2)
        if maze[r][c] == 0:
            maze[r][c] = 1  # Add a dead end

    # Add random walls based on wall_density
    for r in range(1, rows-1):
        for c in range(1, cols-1):
            if maze[r][c] == 0 and random.random() < wall_density * 0.1:
                maze[r][c] = 1  # Add wall 

    return maze

def is_solvable(maze, start, end):
    queue = deque([start])
    visited = set([start])
    while queue:
        current = queue.popleft()
        if current == end:
            return True
        for neighbor in get_adjacent_cells(current, maze):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False

# Helper to get adjacent cells
def get_adjacent_cells(cell, maze):
    row, col = cell
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    neighbors = []
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < maze.shape[0] and 0 <= c < maze.shape[1] and maze[r][c] == 0:
            neighbors.append((r, c))
    return neighbors
