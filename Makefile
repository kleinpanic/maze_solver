PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
WEB_DIR := src/maze_solver/web

.PHONY: install dev format lint test test-python test-web web-build web-smoke run gui tui web catalog backlog-correlate backlog-correlate-apply clean

install:
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install -e ".[dev]"
	npm --prefix $(WEB_DIR) ci

format:
	$(PYTHON) -m ruff format .

lint:
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m ruff check .

test: lint test-python test-web

test-python:
	$(PYTHON) -m pytest

test-web:
	npm --prefix $(WEB_DIR) test

web-build:
	npm --prefix $(WEB_DIR) run build

web-smoke:
	npm --prefix $(WEB_DIR) run test:e2e

run gui:
	$(PYTHON) -m maze_solver.cli gui

tui:
	$(PYTHON) -m maze_solver.cli tui

web:
	$(PYTHON) -m maze_solver.cli web

catalog:
	$(PYTHON) -m maze_solver.cli catalog

backlog-correlate:
	$(PYTHON) -m maze_solver.automation.correlate_issues --summary

backlog-correlate-apply:
	$(PYTHON) -m maze_solver.automation.correlate_issues --apply --summary

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .ruff_cache
	rm -rf $(WEB_DIR)/dist
