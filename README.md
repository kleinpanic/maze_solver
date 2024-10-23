# Python Maze Solver

## Overview

This Python Maze Solver is a graphical maze generation and solving application built using `Tkinter` for the user interface. The program generates mazes with adjustable parameters such as maze size, branching factor, number of dead ends, wall density, and overall connectedness. Once generated, the user can solve the maze using various pathfinding algorithms including Breadth-First Search (BFS), Depth-First Search (DFS), and A* Search. 

## Features

- **Maze Generation Algorithms**: Generate mazes using **Recursive Backtracker** and **Prim's Algorithm**.
- **Adjustable Maze Parameters**:
  - **Rows and Columns**: Control the dimensions of the maze (supports strict 1:1 and 1:2 ratios).
  - **Dead Ends**: Adjust the number of dead ends in the maze.
  - **Branching Factor**: Increase or decrease the number of branches off the main path.
  - **Connectedness**: Control how much of the maze is connected to the main path, from 10% to 90%.
  - **Wall Density**: Add random walls to increase the maze's complexity.
- **Solvability**: All mazes are guaranteed to be solvable using one of the pathfinding algorithms.
- **Seed-Based Generation**: Allows users to input a seed for reproducibility or use an auto-generated seed.
- **Pathfinding Algorithms**:
  - **Breadth-First Search (BFS)**: Explores the maze layer by layer, guaranteeing the shortest path.
  - **Depth-First Search (DFS)**: Explores deep paths before backtracking, resulting in longer paths.
  - **A* Search**: A heuristic-based algorithm that combines features of both BFS and DFS.
- **Real-Time Visualization**: Watch the maze being solved step-by-step, with visual indications of visited cells, the frontier, and the final path.
- **User-Controlled Timer**: The timer starts when the user initiates the solving process and stops once the solution is found.
- **Interactive Stop**: The solving process can be stopped at any time by pressing the stop button.

## Usage

### Getting Started

The program requires no external dependencies (except tkinter), so just clone the repository and run the `main.py` file:

```bash
python3 main.py
```

### Adjusting Maze Parameters

- **Rows/Columns**: Input the desired number of rows and columns for the maze. The program ensures a strict 1:1 or 1:2 ratio for proper visualization.
- **Dead Ends**: Adjust the number of dead ends in the maze using the slider.
- **Branching Factor**: Adjust the number of branches from the main path using the slider.
- **Connectedness**: Control the percentage of the maze connected to the main path. The slider ranges from 10% to 90%, with 70% being the default.
- **Wall Density**: Adjust how many walls are randomly added to the maze. Higher wall density increases the maze's complexity.
- **Seed**: If left blank, a random seed is generated and shown. If you provide a seed, it will generate the same maze every time.
  
### Pathfinding Algorithms

Once the maze is generated, select a pathfinding algorithm from the dropdown:

- **BFS**: Finds the shortest path by exploring all neighboring nodes evenly.
- **DFS**: Searches deep into the maze, often producing longer paths due to its depth-first nature.
- **A* Search**: Combines the exploration of BFS with heuristic guidance for faster results.

Click **Start** to begin solving the maze. The maze will be solved step by step, with different colors representing the visited cells, the frontier, and the final path.

### Stopping the Solver

The **Stop** button halts the solving process at any point. The solver will stop gracefully, and you can generate or solve a new maze afterward.

### Exiting the Program

You can exit the program by pressing `Q` or `Esc` to cleanly quit the application at any point.

## Code Overview

### `main.py`

This is the entry point for the application. It sets up the Tkinter user interface and connects it with the maze generation and solving functionalities. 

Key features:
- **MazeSolverApp Class**: Manages the UI, timer, maze generation, and maze solving processes.
- **Maze Generation and Solving**: When you click **Generate Maze**, it spawns a new thread to avoid freezing the UI. Clicking **Start** initiates the solving process in a step-by-step manner.
- **Stop Functionality**: The `stop_requested` flag is used to gracefully interrupt the solving process.

### `maze_generator.py`

Handles maze generation using the **Recursive Backtracker** and **Prim's Algorithm**. Key parameters such as dead ends, branching factor, wall density, and connectedness are handled here to create custom mazes.

Key features:
- **Recursive Backtracker**: This is a depth-first maze generation algorithm that carves out a perfect maze (i.e., no loops) by backtracking whenever it hits a dead end.
- **Prim's Algorithm**: An algorithm that grows a maze from a starting point by adding walls around it, randomly selecting walls, and carving new paths.
- **Solvability Check**: Every generated maze is checked for solvability using BFS. If the maze is unsolvable, it is regenerated.

### `pathfinding_algorithms.py`

Implements three pathfinding algorithms for solving mazes:

- **BFS Generator**: Implements a breadth-first search that explores the maze layer by layer, ensuring the shortest path is found.
- **DFS Generator**: A depth-first search that dives deep into one path before backtracking, often producing longer paths.
- **A* Generator**: Uses the Manhattan distance heuristic to prioritize paths that are closer to the goal.

Each algorithm is implemented as a generator, which yields intermediate steps for real-time visualization.

### `render.py`

Handles the Tkinter UI and the canvas drawing logic. It updates the maze visualization, including marking visited cells, frontier cells, and the final path.

Key features:
- **Maze Visualization**: Displays the maze and highlights the solving process.
- **Controls**: Manages sliders, buttons, and input fields for configuring the maze generation and solving process.

## Algorithms Explained

### Recursive Backtracker

This algorithm works by starting at a random cell, then carving a path through the maze by choosing random directions. When it encounters a dead end, it backtracks to the last point where it has unvisited neighbors. The result is a "perfect" maze with no loops.

### Prim's Algorithm

Prim's algorithm starts from a single point and iteratively carves out a maze by adding walls to a list and randomly choosing walls to break through, creating paths as it grows the maze.

### Breadth-First Search (BFS)

BFS explores all possible paths equally in every direction, layer by layer. It guarantees the shortest path in an unweighted maze. BFS uses a queue to keep track of the cells to visit next.

### Depth-First Search (DFS)

DFS works by exploring one path as deeply as possible before backtracking to explore other paths. It uses a stack to keep track of the cells it needs to explore.

### A* Search

A* is a heuristic search algorithm that combines the features of BFS and DFS. It uses a heuristic (in this case, the Manhattan distance) to prioritize paths that are closer to the goal, making it faster and more efficient for finding optimal paths.

