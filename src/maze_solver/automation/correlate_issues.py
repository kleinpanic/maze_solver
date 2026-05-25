from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

from maze_solver.catalog import algorithm_catalog, known_2d_algorithm_backlog


@dataclass(frozen=True)
class LabelSpec:
    name: str
    color: str
    description: str


LABELS = (
    LabelSpec("area:algorithm", "5319e7", "Algorithm, solver, generator, or maze topology work."),
    LabelSpec("area:webui", "1d76db", "Browser interface or GitHub Pages work."),
    LabelSpec("area:gui", "0e8a16", "Tkinter desktop interface work."),
    LabelSpec("area:tui", "c2e0c6", "Terminal interface work."),
    LabelSpec("area:docs", "0075ca", "Documentation, wiki, examples, or references."),
    LabelSpec("area:ci", "fbca04", "GitHub Actions, releases, packaging, or automation."),
    LabelSpec("backlog:implemented", "0e8a16", "Issue matches an implemented catalog algorithm."),
    LabelSpec("backlog:known-2d", "d4c5f9", "Issue matches the researched 2D algorithm backlog."),
    LabelSpec("backlog:uncorrelated", "ededed", "Issue did not match a known catalog or backlog entry."),
)

AREA_KEYWORDS = {
    "area:algorithm": (
        "algorithm",
        "astar",
        "a star",
        "backlog",
        "dijkstra",
        "generator",
        "maze",
        "pathfinding",
        "solver",
        "topology",
    ),
    "area:webui": ("browser", "canvas", "github pages", "html", "javascript", "pages", "tailwind", "web", "webui"),
    "area:gui": ("desktop", "gui", "tkinter"),
    "area:tui": ("ansi", "cli", "terminal", "tui"),
    "area:docs": ("changelog", "docs", "documentation", "readme", "reference", "wiki"),
    "area:ci": ("action", "actions", "ci", "release", "workflow"),
}


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def searchable_terms(entry: dict[str, Any]) -> set[str]:
    name = entry["name"]
    terms = {name}
    notes = str(entry.get("notes", ""))
    aliases = entry.get("aliases", [])
    if isinstance(aliases, list):
        terms.update(str(alias) for alias in aliases)
    parenthetical = re.findall(r"\(([^)]+)\)", name)
    terms.update(parenthetical)
    without_parenthetical = re.sub(r"\s*\([^)]*\)", "", name).strip()
    if without_parenthetical != name:
        terms.add(without_parenthetical)
    short = re.sub(r"\b(algorithm|search|solver)\b", "", name, flags=re.IGNORECASE).strip()
    if len(short) >= 3:
        terms.add(short)
    lowered = name.lower()
    normalized_name = normalize_text(name)
    if "a*" in lowered:
        terms.update({"a*", "astar", "a star"})
    if normalized_name in {"breadth first search", "breadth first"}:
        terms.update({"bfs", "breadth first"})
    if normalized_name in {"depth first search", "depth first"}:
        terms.update({"dfs", "depth first"})
    if normalized_name == "dijkstra":
        terms.add("dijkstra")
    if normalized_name == "lee algorithm":
        terms.add("lee")
    if normalized_name == "hadlock s algorithm":
        terms.add("hadlock")
    if notes:
        first_clause = re.split(r"[.;]", notes, maxsplit=1)[0]
        if 4 <= len(first_clause) <= 60:
            terms.add(first_clause)
    return {normalize_text(term) for term in terms if normalize_text(term)}


def matched_entries(text: str, entries: list[dict[str, Any]]) -> list[str]:
    normalized = f" {normalize_text(text)} "
    matches: list[str] = []
    for entry in entries:
        for term in searchable_terms(entry):
            if len(term) < 3:
                continue
            if f" {term} " in normalized:
                matches.append(entry["name"])
                break
    return matches


def issue_labels(issue: dict[str, Any]) -> tuple[set[str], list[str], list[str]]:
    text = f"{issue.get('title', '')}\n{issue.get('body') or ''}"
    normalized = f" {normalize_text(text)} "
    labels: set[str] = set()

    implemented = matched_entries(text, algorithm_catalog())
    backlog = matched_entries(text, known_2d_algorithm_backlog())

    for label, keywords in AREA_KEYWORDS.items():
        if any(f" {normalize_text(keyword)} " in normalized for keyword in keywords):
            labels.add(label)

    if implemented:
        labels.add("area:algorithm")
        labels.add("backlog:implemented")
    if backlog:
        labels.add("area:algorithm")
        labels.add("backlog:known-2d")
    if not implemented and not backlog:
        labels.add("backlog:uncorrelated")

    return labels, implemented, backlog


def run_gh(args: list[str]) -> str:
    completed = subprocess.run(["gh", *args], check=True, text=True, capture_output=True)
    return completed.stdout


def ensure_labels(apply: bool) -> None:
    if not apply:
        return
    existing_payload = run_gh(["label", "list", "--limit", "200", "--json", "name"])
    existing = {entry["name"] for entry in json.loads(existing_payload)}
    for spec in LABELS:
        if spec.name in existing:
            run_gh(["label", "edit", spec.name, "--color", spec.color, "--description", spec.description])
        else:
            run_gh(["label", "create", spec.name, "--color", spec.color, "--description", spec.description])


def open_issues(limit: int) -> list[dict[str, Any]]:
    payload = run_gh(
        ["issue", "list", "--state", "open", "--limit", str(limit), "--json", "number,title,body,labels,url"]
    )
    issues = json.loads(payload)
    if not isinstance(issues, list):
        raise ValueError("gh issue list returned an unexpected payload.")
    return issues


def apply_labels(issue_number: int, labels: set[str]) -> None:
    if labels:
        args = ["issue", "edit", str(issue_number)]
        for label in sorted(labels):
            args.extend(["--add-label", label])
        run_gh(args)


def build_report(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Backlog Correlation",
        "",
        f"Open issues scanned: {len(rows)}",
        "",
        "| Issue | Labels | Implemented matches | Backlog matches |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        issue = f"[#{row['number']}]({row['url']})"
        labels = ", ".join(row["labels"]) or "-"
        implemented = ", ".join(row["implemented"]) or "-"
        backlog = ", ".join(row["backlog"]) or "-"
        lines.append(f"| {issue} | {labels} | {implemented} | {backlog} |")
    return "\n".join(lines)


def correlate(limit: int, apply: bool) -> str:
    ensure_labels(apply)
    rows: list[dict[str, Any]] = []
    for issue in open_issues(limit):
        labels, implemented, backlog = issue_labels(issue)
        if apply:
            apply_labels(issue["number"], labels)
        rows.append(
            {
                "number": issue["number"],
                "url": issue["url"],
                "labels": sorted(labels),
                "implemented": implemented,
                "backlog": backlog,
            }
        )
    return build_report(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Correlate GitHub issues with the Maze Solver algorithm backlog.")
    parser.add_argument("--limit", type=int, default=200, help="Maximum number of open issues to scan.")
    parser.add_argument("--apply", action="store_true", help="Create labels and apply correlations through gh.")
    parser.add_argument("--summary", action="store_true", help="Print a Markdown summary.")
    args = parser.parse_args(argv)

    report = correlate(limit=args.limit, apply=args.apply)
    if args.summary:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
