import pytest

from maze_solver import web_server


class BusySocket:
    attempted: list[int] = []

    def __init__(self, *args: object) -> None:
        pass

    def __enter__(self) -> "BusySocket":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def setsockopt(self, *args: object) -> None:
        return None

    def bind(self, address: tuple[str, int]) -> None:
        self.attempted.append(address[1])
        raise OSError("busy")


def test_find_available_port_stops_at_highest_valid_port(monkeypatch):
    BusySocket.attempted = []
    monkeypatch.setattr(web_server.socket, "socket", BusySocket)

    with pytest.raises(OSError, match="from 65530 to 65535"):
        web_server.find_available_port("127.0.0.1", 65530)

    assert BusySocket.attempted == list(range(65530, 65536))


@pytest.mark.parametrize("port", ["0", "-1", "65536", "70000"])
def test_parse_args_rejects_out_of_range_ports(port, capsys):
    with pytest.raises(SystemExit) as exit_error:
        web_server.parse_args(["--port", port])

    assert exit_error.value.code == 2
    assert "port must be between 1 and 65535" in capsys.readouterr().err
