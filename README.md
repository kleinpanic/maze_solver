# Python Maze Solver

[![CI](https://img.shields.io/github/actions/workflow/status/kleinpanic/maze_solver/ci.yml?branch=main&label=CI)](https://github.com/kleinpanic/maze_solver/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/github/actions/workflow/status/kleinpanic/maze_solver/pages.yml?branch=main&label=Pages)](https://github.com/kleinpanic/maze_solver/actions/workflows/pages.yml)
[![Security](https://img.shields.io/github/actions/workflow/status/kleinpanic/maze_solver/security.yml?branch=main&label=Security)](https://github.com/kleinpanic/maze_solver/actions/workflows/security.yml)
[![Wiki](https://img.shields.io/github/actions/workflow/status/kleinpanic/maze_solver/wiki.yml?branch=main&label=Wiki)](https://github.com/kleinpanic/maze_solver/actions/workflows/wiki.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](pyproject.toml)

Maze Solver is an interactive maze generation and pathfinding lab. It ships three interfaces over the same algorithm core:

- a Tkinter GUI for step-by-step desktop visualization,
- a terminal UI for reproducible command-line runs,
- a static Canvas WebUI designed for GitHub Pages: <https://kleinpanic.github.io/maze_solver/>.

The project treats mazes as grid graphs, where open cells are vertices and north/south/east/west moves are edges. Solver and generator metadata live beside the implementations, so the GUI, TUI, WebUI, tests, and documentation stay aligned as the catalog grows.

## Features

- Real-time visualization of visited cells, frontier cells, and final paths.
- Deterministic maze generation with seeds, perfect-maze topology by default, optional braided loops, and connected-open-component validation.
- Shared Python package under `src/maze_solver`.
- Browser-side educational WebUI with Canvas animation, researched complexity notes, calculated per-maze graph bounds, runtime metrics, per-solver math breakdowns, generator theory, maze-structure statistics, and 85 runnable renditions against a 128-algorithm known-applicable 2D coverage counter.
- Desktop GUI with algorithm metadata, restart-on-selection solving, runtime controls, graph telemetry, calculated bound estimates, and high-contrast visualization states.
- Terminal UI with reproducible runs, optional ANSI color, calculated graph/work statistics, and a `--catalog` view for the full roadmap.
- CI for Python 3.11, 3.12, and 3.13.
- GitHub Pages deployment from `src/maze_solver/web/dist`.
- Automated tagged releases for `v*` tags, including Python distributions and a zipped WebUI build.
- GitHub Wiki publishing from `docs/wiki` and issue-to-backlog correlation labels.
- CodeQL, dependency review, and Dependabot configuration.

## Solver Catalog

| Algorithm | Complete | Optimal | Weighted | Time | Space |
| --- | --- | --- | --- | --- | --- |
| Breadth-First Search | Yes | Yes | No | `O(V + E)` | `O(V)` |
| Lee Algorithm | Yes | Yes | No | `O(V + E)` | `O(V)` |
| Depth-First Search | Yes | No | No | `O(V + E)` | `O(V)` |
| Flood Fill Solver | Yes | Yes | No | `O(V + E)` | `O(V)` |
| A* Search | Yes | Yes | Yes | `O(E log V)` | `O(V)` |
| Iterative Deepening A* | Yes | Yes | No | `O(b^d)` worst case | `O(d)` |
| Hadlock's Algorithm | Yes | Yes | No | `O(V + E)` | `O(V)` |
| Dijkstra's Algorithm | Yes | Yes | Yes | `O((V + E) log V)` | `O(V)` |
| Uniform-Cost Search | Yes | Yes | Yes | `O((V + E) log V)` | `O(V)` |
| SPFA | Yes | Yes | Yes | `O(VE)` worst case | `O(V)` |
| Bidirectional BFS | Yes | Yes | No | `O(b^(d/2))` idealized | `O(b^(d/2))` |
| Greedy Best-First Search | Yes | No | No | `O(E log V)` | `O(V)` |
| Left-Hand Wall Follower | Topology-dependent | No | No | `O(k)` | `O(k)` |
| Right-Hand Wall Follower | Topology-dependent | No | No | `O(k)` | `O(k)` |
| Tremaux's Algorithm | Yes | No | No | `O(V + E)` | `O(V + E)` |
| Pledge Algorithm | Topology-dependent | No | No | `O(k)` | `O(k)` |
| Iterative Deepening Depth-First Search | Yes | Yes | No | `O(b^d)` | `O(d)` |
| Bellman-Ford | Yes | Yes | Yes | `O(VE)` | `O(V)` |
| Dead-End Filling | Yes | No | No | `O(V + E)` | `O(V)` |
| Random Mouse | No | No | No | Unbounded | `O(k)` |

## Generator Catalog

Recursive Backtracker, Randomized Prim, Randomized Kruskal, Wilson, Aldous-Broder, Hunt and Kill, Binary Tree, Sidewinder, Growing Tree, Eller, and Recursive Division are available in the Python core and the WebUI. The browser view explains each generator's graph model, perfect-maze claim, asymptotic cost, texture bias, invariant, and carving procedure while reporting wall ratio, dead ends, junctions, and corridor bias for the current maze.

Every generated maze keeps all open cells reachable from the start. In perfect topology mode, spanning-tree generators produce a connected acyclic passage graph with exactly one route between any two open cells. Braided topology adds connector loops without randomly closing passages or creating accidental 2x2 open blocks.

See [docs/ALGORITHMS.md](docs/ALGORITHMS.md) for the full catalog, complexity notes, and references.
The machine-readable implementation catalog is tracked in [src/maze_solver/algorithm_catalog.json](src/maze_solver/algorithm_catalog.json). The coverage counter combines those 85 implemented maze, grid, routing, robotics, sampling, optimization, and constraint-solving renditions with the researched backlog in [src/maze_solver/known_2d_backlog.json](src/maze_solver/known_2d_backlog.json), currently 85 of 128 known-applicable 2D algorithms covered.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
make dev
maze_solver gui
```

Run a terminal solve:

```bash
maze_solver tui --rows 21 --cols 41 --seed 2026 --algorithm Dijkstra
```

Add `--color always --legend` for a colorized terminal render with the state legend.

Run the WebUI locally:

```bash
make web-build
maze_solver web
```

Then open the URL printed by the command. It starts at port `4173`, falls forward when the port is busy, and stops cleanly on Ctrl-C.

## Development

Run Python checks:

```bash
source .venv/bin/activate
make test-python
make lint
```

Run WebUI checks:

```bash
make test-web
make web-build
```

Preview open GitHub issue correlation against the implemented catalog and researched backlog:

```bash
make backlog-correlate
```

Create a release:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The `Release` workflow verifies Python and WebUI checks before publishing the GitHub release.

## Repository Layout

```text
src/maze_solver/          Python package, GUI, TUI, server, and algorithm core
src/maze_solver/web/      Static Canvas WebUI
src/tests/                Python tests for solvers and generators
docs/ALGORITHMS.md        Algorithm catalog and references
docs/wiki/                GitHub Wiki source
.github/workflows/        CI, Pages, release, and security workflows
```

## License

MIT. See [LICENSE](LICENSE).
