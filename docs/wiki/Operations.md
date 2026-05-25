# Operations

## Continuous Integration

The CI workflow runs formatting, linting, and Python tests on supported Python versions. WebUI checks run through package scripts and Pages deployment builds from `src/maze_solver/web`.

## GitHub Pages

The Pages workflow publishes the static WebUI. The live site is:

https://kleinpanic.github.io/maze_solver/

## Releases

Version tags drive release automation. Pushing a `v*` tag verifies the project and publishes release assets, including Python distributions and the WebUI build.

## Wiki Publishing

The GitHub Wiki is sourced from `docs/wiki`. Pushing changes under that directory triggers the wiki workflow, which mirrors the Markdown pages into the repository wiki.

## Backlog Correlation

Issue changes trigger the backlog workflow. It applies area and backlog labels through the GitHub CLI, then writes a correlation table to the workflow summary.
