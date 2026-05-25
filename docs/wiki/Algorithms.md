# Algorithms

## Catalog Policy

The implemented catalog tracks runnable maze, grid-routing, robotics, sampling, optimization, and constraint-solving renditions that can be demonstrated on a 2D maze plane. The researched backlog tracks known-applicable candidates that should be implemented or explained next.

Each catalog entry should carry:

- family and status,
- completeness and optimality claims where applicable,
- weighted or unweighted cost model,
- time and space bounds,
- a concise reference note.

## Maze Generation Policy

Generators should preserve solvability. Perfect topology mode should produce a connected acyclic passage graph with one simple path between any two open cells. Braided topology can add loops, but it should not create accidental disconnected rooms or noisy 2x2 artifacts.

## Solver Policy

Solvers should report visited cells, frontier states where meaningful, final paths, and measured runtime statistics. Big-O text belongs in metadata, while per-maze work estimates should be calculated from the current graph size.

## Reference Sources

Long-form references and algorithm notes live in `docs/ALGORITHMS.md`. Machine-readable coverage lives in `src/maze_solver/algorithm_catalog.json` and `src/maze_solver/known_2d_backlog.json`.
