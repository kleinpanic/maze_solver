# Maze Solver

Maze Solver is a grid-graph pathfinding lab with a shared Python algorithm core, a Tkinter GUI, a terminal UI, and a static WebUI published on GitHub Pages.

- Live WebUI: https://kleinpanic.github.io/maze_solver/
- Repository: https://github.com/kleinpanic/maze_solver
- Release history: https://github.com/kleinpanic/maze_solver/releases

## Wiki Map

- [Architecture](Architecture): package layout, interfaces, and shared data flow.
- [Algorithms](Algorithms): solver and generator catalog policy.
- [Backlog](Backlog): how issues map to implemented algorithms and researched 2D backlog entries.
- [Operations](Operations): CI, Pages, releases, security checks, and wiki publishing.

## Current Shape

The project uses a package-first layout under `src/maze_solver`. Algorithm metadata lives with the implementations, tests read the same catalogs as the interfaces, and the WebUI consumes the same JSON catalog published with the Python package.

The core expectation is simple: every maze should be solvable, every solver claim should be testable, and every public interface should explain the math well enough to be useful as an educational tool.
