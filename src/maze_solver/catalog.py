from __future__ import annotations

import json
from functools import cache
from importlib import resources
from typing import Any


@cache
def algorithm_catalog() -> list[dict[str, Any]]:
    with resources.files("maze_solver").joinpath("algorithm_catalog.json").open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    if not isinstance(catalog, list):
        raise ValueError("Algorithm catalog must be a list.")
    return catalog


@cache
def known_2d_algorithm_backlog() -> list[dict[str, Any]]:
    with resources.files("maze_solver").joinpath("known_2d_backlog.json").open(encoding="utf-8") as handle:
        backlog = json.load(handle)
    if not isinstance(backlog, list):
        raise ValueError("Known 2D backlog must be a list.")
    implemented = {entry["name"] for entry in algorithm_catalog()}
    duplicates = implemented & {entry["name"] for entry in backlog}
    if duplicates:
        raise ValueError(f"Known 2D backlog duplicates implemented algorithms: {sorted(duplicates)}")
    return backlog


def catalog_summary() -> tuple[int, int]:
    catalog = algorithm_catalog()
    implemented = sum(1 for entry in catalog if entry.get("status") == "implemented")
    return implemented, len(catalog)


def known_2d_coverage_summary() -> tuple[int, int, int]:
    implemented, tracked = catalog_summary()
    backlog = len(known_2d_algorithm_backlog())
    return implemented, tracked + backlog, backlog
