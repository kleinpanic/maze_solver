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

## Algorithm Changes

Add solver metadata to `ALGORITHM_REGISTRY`, wire the generator into `SOLVER_REGISTRY`, and add tests for path validity, optimality claims, and edge cases. Add maze generators to `GENERATION_REGISTRY`, verify deterministic seeds, and keep generated mazes solvable through the shared BFS check.
