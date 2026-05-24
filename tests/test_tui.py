import numpy as np

from maze_solver import tui
from maze_solver.tui import render_maze


def test_render_maze_supports_plain_and_color_output():
    maze = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
    )
    start = (1, 1)
    goal = (1, 3)
    path = [(1, 1), (1, 2), (1, 3)]
    visited = [(1, 1), (1, 2)]
    frontier = [(1, 3)]

    plain = render_maze(maze, start, goal, path, visited, frontier, color=False)
    color = render_maze(maze, start, goal, path, visited, frontier, color=True)

    assert "\033[" not in plain
    assert "\033[" in color
    assert "S*G" in plain


def test_tui_main_prints_metadata_legend_and_stats(capsys):
    tui.main(
        [
            "--rows",
            "11",
            "--cols",
            "21",
            "--seed",
            "2026",
            "--generator",
            "Eller",
            "--algorithm",
            "A*",
            "--color",
            "never",
            "--legend",
        ]
    )

    output = capsys.readouterr().out
    assert "Maze Solver TUI | Eller | A* | seed 2026" in output
    assert "A* Search | Heuristic shortest path | time=O(E log V) with a binary heap" in output
    assert "Legend: S=start G=goal *=path +=frontier .=visited" in output
    assert "path=27 visited=34 frontier=40 steps=34" in output
    assert "wall_ratio=56.3%" in output
    assert "\033[" not in output
