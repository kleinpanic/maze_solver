from __future__ import annotations

import numpy as np

from maze_solver.algorithms import ALGORITHM_REGISTRY, SOLVER_REGISTRY
from maze_solver.catalog import (
    algorithm_catalog,
    catalog_summary,
    known_2d_algorithm_backlog,
    known_2d_coverage_summary,
)


def test_algorithm_catalog_tracks_broad_2d_solver_roadmap():
    catalog = algorithm_catalog()
    names = [entry["name"] for entry in catalog]
    families = {entry["family"] for entry in catalog}

    assert len(catalog) >= 80
    assert len(names) == len(set(names))
    assert {"Grid pruning", "Any-angle search", "Incremental replanning", "Sampling-based planning"} <= families

    for entry in catalog:
        assert entry["status"] == "implemented"
        assert entry["time"]
        assert entry["space"]
        assert entry["notes"]
        assert entry["reference"]


def test_implemented_catalog_matches_solver_registry():
    implemented = {entry["name"] for entry in algorithm_catalog() if entry["status"] == "implemented"}
    aliases = {"UCS": "Uniform-Cost Search"}
    registry_names = {aliases.get(name, name) for name in ALGORITHM_REGISTRY}

    assert registry_names <= implemented
    assert catalog_summary() == (len(implemented), len(algorithm_catalog()))


def test_known_2d_coverage_counter_extends_beyond_current_catalog():
    catalog_names = {entry["name"] for entry in algorithm_catalog()}
    backlog = known_2d_algorithm_backlog()
    backlog_names = {entry["name"] for entry in backlog}
    implemented, known_total, backlog_count = known_2d_coverage_summary()

    assert len(backlog) >= 40
    assert len(backlog_names) == len(backlog)
    assert catalog_names.isdisjoint(backlog_names)
    assert implemented == len(algorithm_catalog())
    assert known_total == len(algorithm_catalog()) + len(backlog)
    assert backlog_count == len(backlog)
    assert known_total >= 120
    assert {"RRT-Connect", "Conflict-Based Search", "SMT Path Encoding"} <= backlog_names


def test_every_catalog_algorithm_has_a_runnable_grid_rendition():
    aliases = {"Uniform-Cost Search": "UCS"}
    maze = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
    )
    start = (1, 1)
    end = (3, 1)

    for entry in algorithm_catalog():
        key = aliases.get(entry["name"], entry["name"])
        assert key in SOLVER_REGISTRY
        events = list(SOLVER_REGISTRY[key](maze, start, end))
        path = [cell for action, cell, _steps in events if action == "path" and cell is not None]
        assert path[0] == start, key
        assert path[-1] == end, key
        assert all(maze[cell] == 0 for cell in path), key
