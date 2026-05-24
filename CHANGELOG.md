# Changelog

## 0.1.2

- Fixed desktop WebUI canvas alignment so the maze stays visible near the top of the stage beside the full comparison table.

## 0.1.1

- Expanded the solver catalog with Lee, Flood Fill, SPFA, left-hand and right-hand wall followers, Tremaux, Pledge, and Random Mouse.
- Added WebUI Big-O, space complexity, completeness, optimality, coverage, work-factor, event-count, and open-cell metrics.
- Changed the WebUI to generate a fresh random solvable maze on first load while keeping explicit seeds reproducible.
- Improved high-speed WebUI animation by batching events for larger algorithm traces.
- Added automated GitHub releases for version tags with Python and WebUI artifacts.

## 0.1.0

- Added a packaged maze core with registries for solver and generator algorithms.
- Added solver coverage for BFS, DFS, A*, Dijkstra, UCS, Bidirectional BFS, Greedy Best-First, IDDFS, Bellman-Ford, and Dead-End Filling.
- Added generator coverage for Recursive Backtracker, Randomized Prim, Kruskal, Wilson, Aldous-Broder, Hunt and Kill, Binary Tree, Sidewinder, Growing Tree, Eller, and Recursive Division.
- Added a terminal interface for deterministic runs and compact ASCII output.
- Added a static Tailwind and Canvas WebUI for GitHub Pages.
- Added Python CI, Pages deployment, dependency monitoring, and security scanning workflows.
