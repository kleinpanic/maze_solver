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


def catalog_summary() -> tuple[int, int]:
    catalog = algorithm_catalog()
    implemented = sum(1 for entry in catalog if entry.get("status") == "implemented")
    return implemented, len(catalog)
