# Python Maze Solver

[![CI](https://img.shields.io/github/actions/workflow/status/kleinpanic/maze_solver/ci.yml?branch=main&label=CI)](https://github.com/kleinpanic/maze_solver/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/github/actions/workflow/status/kleinpanic/maze_solver/pages.yml?branch=main&label=Pages)](https://github.com/kleinpanic/maze_solver/actions/workflows/pages.yml)
[![Security](https://img.shields.io/github/actions/workflow/status/kleinpanic/maze_solver/security.yml?branch=main&label=Security)](https://github.com/kleinpanic/maze_solver/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](pyproject.toml)

Maze Solver is an interactive maze generation and pathfinding lab. It ships three interfaces over the same algorithm core:

- a Tkinter GUI for step-by-step desktop visualization,
- a terminal UI for reproducible command-line runs,
- a static Canvas WebUI designed for GitHub Pages: <https://kleinpanic.github.io/maze_solver/>.

The project treats mazes as grid graphs, where open cells are vertices and north/south/east/west moves are edges. Solver and generator metadata live beside the implementations, so the GUI, TUI, WebUI, tests, and documentation stay aligned as the catalog grows.

## Features

- Real-time visualization of visited cells, frontier cells, and final paths.
- Deterministic maze generation with seeds and a connected-open-component guarantee after noise/loop shaping.
- Shared Python package under `src/maze_solver`.
- Browser-side educational WebUI with Canvas animation, researched complexity notes, calculated per-maze graph bounds, runtime metrics, per-solver math breakdowns, generator theory, maze-structure statistics, and an algorithm roadmap.
- Desktop GUI with algorithm metadata, restart-on-selection solving, runtime controls, graph telemetry, calculated bound estimates, and high-contrast visualization states.
- Terminal UI with reproducible runs, optional ANSI color, calculated graph/work statistics, and a `--catalog` view for the full roadmap.
- CI for Python 3.11, 3.12, and 3.13.
- GitHub Pages deployment from `web/dist`.
- Automated tagged releases for `v*` tags, including Python distributions and a zipped WebUI build.
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

Every generated maze keeps all open cells reachable from the start after the optional loop/noise pass. That means a seed can produce braided routes and extra rooms, but it should not leave disconnected islands that look playable while being unreachable.

See [docs/ALGORITHMS.md](docs/ALGORITHMS.md) for the full catalog, complexity notes, and references.
The machine-readable roadmap is tracked in [src/maze_solver/algorithm_catalog.json](src/maze_solver/algorithm_catalog.json) and currently covers 85 maze, grid, routing, robotics, sampling, optimization, and constraint-solving approaches.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python3 main.py
```

Run a terminal solve:

```bash
maze-solver-tui --rows 21 --cols 41 --seed 2026 --algorithm Dijkstra
```

Add `--color always --legend` for a colorized terminal render with the state legend.

Run the WebUI locally:

```bash
cd web
npm ci
npm run build
cd ..
maze-solver-web
```

Then open the URL printed by the command. It starts at port `4173`, falls forward when the port is busy, and stops cleanly on Ctrl-C.

## Development

Run Python checks:

```bash
source .venv/bin/activate
pytest
ruff check .
ruff format --check .
```

Run WebUI checks:

```bash
cd web
npm test
npm run build
```

Create a release:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The `Release` workflow verifies Python and WebUI checks before publishing the GitHub release.

## Repository Layout

```text
src/maze_solver/        Python package and algorithm core
tests/                  Python tests for solvers and generators
web/                    Static Canvas WebUI
docs/ALGORITHMS.md      Algorithm catalog and references
.github/workflows/      CI, Pages, and security workflows
```

## License

MIT. See [LICENSE](LICENSE).
