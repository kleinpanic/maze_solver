import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from maze_solver.render import algorithm_display_names


def test_algorithm_display_names_searches_catalog_metadata():
    results = algorithm_display_names("dijkstra")

    assert "Dijkstra" in results
    assert "Hierarchical Dijkstra" in results
    assert "BFS" not in results


def test_algorithm_display_names_filters_by_family():
    results = algorithm_display_names(family="Weighted shortest path")

    assert "Dijkstra" in results
    assert "UCS" in results
    assert "DFS" not in results
