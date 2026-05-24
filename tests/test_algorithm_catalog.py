from __future__ import annotations

from maze_solver.algorithms import ALGORITHM_REGISTRY
from maze_solver.catalog import algorithm_catalog, catalog_summary


def test_algorithm_catalog_tracks_broad_2d_solver_roadmap():
    catalog = algorithm_catalog()
    names = [entry["name"] for entry in catalog]
    families = {entry["family"] for entry in catalog}

    assert len(catalog) >= 80
    assert len(names) == len(set(names))
    assert {"Grid pruning", "Any-angle search", "Incremental replanning", "Sampling-based planning"} <= families

    for entry in catalog:
        assert entry["status"] in {"implemented", "planned"}
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
