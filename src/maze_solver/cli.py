from __future__ import annotations

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="maze_solver", description="Maze Solver command line entrypoint.")
    parser.add_argument("command", nargs="?", choices=("gui", "tui", "web", "catalog"), default="gui")
    args, remainder = parser.parse_known_args(argv)
    args.args = remainder
    return args


def _clean_remainder(args: list[str]) -> list[str]:
    return args[1:] if args[:1] == ["--"] else args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    command = args.command or "gui"

    # Import interfaces lazily so the TUI and web commands work without Tkinter installed.
    if command == "gui":
        from maze_solver import gui

        gui.main()
    elif command == "tui":
        from maze_solver import tui

        tui.main(_clean_remainder(args.args))
    elif command == "web":
        from maze_solver import web_server

        web_server.main(_clean_remainder(args.args))
    elif command == "catalog":
        from maze_solver import tui

        tui.main(["--catalog", *_clean_remainder(args.args)])
    else:
        raise SystemExit(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
