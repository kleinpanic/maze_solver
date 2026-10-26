import subprocess
import sys

# Simulate a Python build without Tkinter (python3-tk not installed, slim containers).
NO_TKINTER = "import sys; sys.modules['tkinter'] = None; from maze_solver import cli; cli.main({argv!r})"


def run_without_tkinter(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", NO_TKINTER.format(argv=argv)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_tui_command_works_without_tkinter():
    completed = run_without_tkinter(["tui", "--rows", "9", "--cols", "9", "--seed", "1", "--color", "never"])

    assert completed.returncode == 0, completed.stderr
    assert "Maze Solver TUI" in completed.stdout


def test_catalog_command_works_without_tkinter():
    completed = run_without_tkinter(["catalog", "--catalog-search", "dijkstra"])

    assert completed.returncode == 0, completed.stderr
    assert "Dijkstra" in completed.stdout
