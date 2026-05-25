# Contributing

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make dev
```

## Checks

Run the Python suite:

```bash
make lint
make test-python
```

Run the WebUI checks:

```bash
make test-web
make web-build
```

Preview issue correlation against the algorithm catalog and researched backlog:

```bash
make backlog-correlate
```

## Algorithm Changes

Add solver metadata to `ALGORITHM_REGISTRY`, wire the generator into `SOLVER_REGISTRY`, and add tests for path validity, optimality claims, and edge cases. Add maze generators to `GENERATION_REGISTRY`, verify deterministic seeds, and keep generated mazes solvable through the shared BFS check.

## Wiki Changes

Edit GitHub Wiki source in `docs/wiki`. The wiki workflow mirrors those Markdown files into the repository wiki after changes land on `main`.
