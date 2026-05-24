# Contributing

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

For the WebUI:

```bash
cd web
npm ci
```

## Checks

Run the Python suite:

```bash
pytest
ruff check .
ruff format --check .
```

Run the WebUI checks:

```bash
cd web
npm test
npm run build
```

## Algorithm Changes

Add solver metadata to `ALGORITHM_REGISTRY`, wire the generator into `SOLVER_REGISTRY`, and add tests for path validity, optimality claims, and edge cases. Add maze generators to `GENERATION_REGISTRY`, verify deterministic seeds, and keep generated mazes solvable through the shared BFS check.
