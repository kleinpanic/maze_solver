# Backlog

## Issue Correlation

Open GitHub issues are correlated against the implemented algorithm catalog and the researched 2D backlog. The automation adds area labels for interface or operations scope, then adds one of the backlog labels:

- `backlog:implemented` when an issue names an implemented catalog item.
- `backlog:known-2d` when an issue names a researched backlog candidate.
- `backlog:uncorrelated` when the issue does not name a known catalog or backlog entry.

## Running Locally

```bash
make backlog-correlate
```

That target uses the GitHub CLI and prints a Markdown summary. The Actions workflow runs the same package module on issue changes and writes the report to the workflow summary.

Maintainers with a write-capable token can apply labels locally:

```bash
make backlog-correlate-apply
```

## Label Areas

- `area:algorithm`
- `area:webui`
- `area:gui`
- `area:tui`
- `area:docs`
- `area:ci`

The label set is intentionally small so issues stay scannable as the algorithm museum grows.
