# Changelog

## 0.2.4

- Added Hadlock's detour-number maze-routing algorithm across the Python core, GUI/TUI registries, WebUI solver museum, tests, and documentation.
- Added the Hadlock mathematical breakdown so users can compare detour minimization against BFS, Lee routing, A*, and IDA*.

## 0.2.3

- Added a WebUI generation model panel with family, perfect-maze claim, complexity, mathematical model, bias, invariant, and procedure notes for every maze generator.
- Added live maze-structure metrics for wall ratio, dead ends, junctions, and corridor bias so generation algorithms can be compared visually and numerically.
- Updated documentation to expose generator complexity and theory beside the solver catalog.

## 0.2.2

- Expanded the WebUI generator catalog with Wilson, Aldous-Broder, Hunt and Kill, and Eller's algorithm so the browser museum matches the Python generator core.
- Kept generated WebUI mazes solvable by running the existing deterministic seed retry path across the full generator set.

## 0.2.1

- Added Iterative Deepening A* across the Python core, terminal UI, desktop GUI selector, WebUI solver museum, tests, and documentation.
- Added the IDA* mathematical breakdown to compare heuristic contour search against A*, IDDFS, and Dijkstra.

## 0.2.0

- Added a WebUI math breakdown panel with graph model, cost model, recurrence, invariant, procedure, and instrumentation notes for each solver.
- Rethemed the Tkinter GUI with algorithm metadata, clearer runtime controls, and higher-contrast maze visualization colors.
- Added TUI algorithm metadata, optional ANSI color output, and an explicit legend for terminal runs.

## 0.1.3

- Added versioned WebUI asset URLs so GitHub Pages clients pick up the latest CSS and JavaScript immediately after deployment.

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
