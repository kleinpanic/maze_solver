from __future__ import annotations

import argparse
import functools
import http.server
import socket
import socketserver
from pathlib import Path


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def find_available_port(host: str, preferred_port: int, max_attempts: int = 100) -> int:
    for port in range(preferred_port, preferred_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((host, port))
            except OSError:
                continue
            return port
    raise OSError(f"No available port found from {preferred_port} to {preferred_port + max_attempts - 1}.")


def default_dist_dir() -> Path:
    package_candidate = Path(__file__).resolve().parent / "web" / "dist"
    repo_candidate = Path(__file__).resolve().parents[2] / "src" / "maze_solver" / "web" / "dist"
    cwd_candidate = Path.cwd() / "src" / "maze_solver" / "web" / "dist"
    direct_candidate = Path.cwd() / "dist"
    for candidate in (cwd_candidate, direct_candidate, repo_candidate, package_candidate):
        if (candidate / "index.html").exists():
            return candidate
    return cwd_candidate


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the Maze Solver WebUI with automatic port fallback.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--dist", type=Path, default=default_dist_dir())
    parser.add_argument(
        "--no-open", action="store_true", help="Reserved for scripts that manage the browser themselves."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    dist = args.dist.resolve()
    if not (dist / "index.html").exists():
        raise SystemExit(f"WebUI build not found at {dist}. Run `make web-build` first.")

    port = find_available_port(args.host, args.port)
    handler = functools.partial(QuietHandler, directory=str(dist))
    with ReusableTCPServer((args.host, port), handler) as httpd:
        print(f"Serving Maze Solver WebUI at http://{args.host}:{port}/")
        if port != args.port:
            print(f"Port {args.port} was busy; using {port}.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping Maze Solver WebUI server.")
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    main()
