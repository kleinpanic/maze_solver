# Architecture

## Package Layout

```text
src/maze_solver/          Python package, CLI, GUI, TUI, server, algorithms
src/maze_solver/web/      Static Canvas WebUI and browser tests
src/tests/                Python tests for the package
docs/                     Long-form documentation and wiki source
docs/wiki/                GitHub Wiki source synced by Actions
.github/workflows/        CI, Pages, release, security, backlog, wiki
```

## Interfaces

- `maze_solver gui` launches the Tkinter visualizer.
- `maze_solver tui` runs terminal solves with optional color and catalog views.
- `maze_solver web` serves the built static WebUI and chooses the next available port when the default is busy.
- `maze_solver catalog` prints the tracked solver and backlog coverage.

## Shared Data Flow

The Python package owns the solver registry, generator registry, catalog JSON, and topology validation. GUI, TUI, WebUI, tests, and documentation read from those sources instead of carrying separate algorithm lists.

That keeps the project honest: adding an algorithm means adding metadata, implementation coverage, interface exposure, and tests in the same release path.
