import http.client
import http.server
import threading
from collections.abc import Iterator
from typing import Any
import pytest
import gradebook

@pytest.fixture
def port(state: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> Iterator[int]:
    monkeypatch.setattr(gradebook, "STATE", state)
    server = http.server.HTTPServer(("127.0.0.1", 0), gradebook.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield server.server_port
    server.shutdown()
    server.server_close()

def send(port: int, method: str, path: str, body: bytes | None = None) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port)
    connection.request(method, path, body=body)
    response = connection.getresponse()
    return response.status, response.read()

@pytest.mark.parametrize(
    "path",
    ["/students/S1", "/students/S1/", "/students/S1?format=json"],
)
def test_get_student_handles_trailing_slashes_and_queries(
    port: int,
    state: dict[str, Any],
    path: str,
) -> None:
    state["students"]["S1"] = {"id": "S1", "name": "Ayesha", "joined": "2026-01-01"}
    status, _ = send(port, "GET", path)
    assert status == 200