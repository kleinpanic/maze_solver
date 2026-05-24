# Changelog

## 0.2.14

- Added a WebUI algorithm anatomy panel with frontier policy, cost model,
  guarantee, trace origin, and native/projected execution badges.
- Fixed the WebUI trace legend so start, goal, visited, frontier, goal-wave,
  and path colors match the canvas rendering.
- Made projected WebUI solver math copy explicit about projection status instead
  of presenting complexity fields as direct equations.
- Cancelled pending Tkinter solver callbacks before rerunning a new GUI
  algorithm, preventing old solver events from interleaving with new runs.

## 0.2.13

- Added searchable, filterable desktop GUI algorithm browsing across the full
  shared solver catalog.
- Added GUI math/research metadata and a speed slider for desktop runs.
- Fixed `python -m maze_solver.tui` execution for terminal catalog use.
- Changed WebUI solver switching to preserve the current maze by default, with
  an explicit fresh-maze toggle for randomized comparisons.
- Added a compact WebUI math card in the inspector, accessibility metadata, and
  row/column clamping.
- Replaced the WebUI tracked-roadmap framing with a known-applicable 2D coverage
  counter: 85 implemented renditions out of 128 researched solver candidates,
  with the remaining algorithms shown as backlog.

## 0.2.12

- Added distinct goal-origin trace coloring for reverse wave solvers and their
  projected catalog variants.
- Bounded IDDFS animation work so the browser stays responsive on museum-size
  mazes.
- Reworked Dead-End Filling and Random Mouse rendering so they keep the maze
  stable while still showing a valid solution path.
- Tightened solver button labels and speed stepping for cleaner interaction.

## 0.2.11

- Added searchable and family-filtered WebUI solver browsing so the full
  algorithm museum is easier to inspect and compare.
- Added TUI catalog search/filter flags for terminal-side algorithm discovery.
- Changed GUI algorithm selection to rerun on the current maze instead of
  silently generating a different maze.

## 0.2.10

- Updated the GitHub Pages browser title and top navigation branding to match
  the Maze Solver Museum presentation.

## 0.2.9

- Removed the misleading wall-density control from WebUI, GUI, and TUI defaults; maze texture is now shaped internally by the generator profile.
- Raised the default visual complexity with larger first-run mazes, Prim-style browser generation, stronger texture shaping, and faster default animation.

## 0.2.8

- Added generated mathematical breakdown panels for every catalog-projected WebUI solver so the full algorithm museum has runnable traces and educational notes.
- Extended the Playwright smoke test to assert catalog algorithms do not fall back to placeholder math copy.

## 0.2.7

- Converted the full 85-entry algorithm catalog from planned coverage to implemented runnable renditions across Python, GUI/TUI selection, and the WebUI solver gallery.
- Added projected finite-grid adapters for any-angle, grid-pruning, incremental replanning, sampling, robotics, metaheuristic, and constraint-solving families so every catalog entry produces an actual maze trace.
- Updated catalog tests to assert every catalog algorithm has a runnable solver and returns a valid path on a solvable maze.
- Expanded WebUI solver controls from the original 20 buttons to the full catalog, with representative Playwright coverage for newly implemented families.

## 0.2.6

- Added an 85-entry machine-readable 2D maze/path-planning algorithm roadmap and tests that enforce catalog breadth plus implemented solver parity.
- Updated the WebUI so solver buttons generate a fresh maze and run immediately, while showing calculated graph bounds from current `V`, `E`, path depth, and solver complexity family.
- Improved the WebUI layout with a larger maze stage, compact controls, roadmap summary, collapsed comparison tables, and desktop/mobile Playwright validation.
- Added TUI maze texture stats, graph/work telemetry, calculated bound estimates, and a `--catalog` roadmap view.
- Upgraded the Tkinter GUI with restart-on-algorithm-selection behavior, a graph telemetry panel, centered square-cell rendering, and calculated bound estimates.

## 0.2.5

- Added a connected-open-component repair pass to Python and WebUI maze generation so noise/loop shaping cannot leave unreachable open islands.
- Added generation tests that assert all open cells remain reachable from the start under high wall-density and dead-end pressure.
- Added WebUI connectivity utilities and tests so browser generation uses the same graph-level invariant.
- Added an ephemeral-port Playwright smoke test to CI and releases so WebUI generator validation avoids fixed-port conflicts.

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
