from __future__ import annotations

from maze_solver.automation.correlate_issues import issue_labels, matched_entries


def test_issue_correlates_implemented_algorithm() -> None:
    issue = {"title": "Dijkstra solver should expose weighted costs", "body": "webui and docs need this"}

    labels, implemented, backlog = issue_labels(issue)

    assert "area:algorithm" in labels
    assert "area:webui" in labels
    assert "area:docs" in labels
    assert "backlog:implemented" in labels
    assert "Dijkstra" in implemented
    assert backlog == []


def test_issue_correlates_known_backlog_algorithm() -> None:
    issue = {"title": "Add Yen k shortest path comparison", "body": "The algorithm table should track this."}

    labels, implemented, backlog = issue_labels(issue)

    assert "area:algorithm" in labels
    assert "backlog:known-2d" in labels
    assert any("Yen" in name for name in backlog)
    assert not implemented


def test_issue_marks_uncorrelated_work() -> None:
    issue = {"title": "Refresh release badge color", "body": "No solver is mentioned here."}

    labels, implemented, backlog = issue_labels(issue)

    assert "area:ci" in labels
    assert "backlog:uncorrelated" in labels
    assert implemented == []
    assert backlog == []


def test_matching_uses_normalized_phrases() -> None:
    entries = [{"name": "Breadth-First Search", "notes": ""}]

    assert matched_entries("Need BFS parity", entries) == ["Breadth-First Search"]
