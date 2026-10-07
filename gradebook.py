"""gradebook.py -- Department gradebook service."""

import http.server
import json
import logging
import sys
from collections.abc import Callable
from typing import Any

import models
from errors import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DATA: str = "gradebook.json"
STATE: dict[str, Any] = {
    "students": {},
    "assessments": {},
    "marks": [],
}


def read_port(raw: str) -> int:
    """Parse and validate port number; exits immediately on invalid input."""
    try:
        port = int(raw)
        if not (1 <= port <= 65535):
            raise ValueError
        return port
    except ValueError:
        raise SystemExit(f"Error: port must be an integer from 1 to 65535, got: {raw!r}") from None


def load() -> None:
    """Load gradebook state; exits if file is corrupt, catches only FileNotFoundError."""
    global STATE
    try:
        with open(DATA, "r", encoding="utf-8") as f:
            content = json.load(f)
            if not isinstance(content, dict):
                raise SystemExit("Error: gradebook.json root must be a JSON object")
            STATE = content
    except FileNotFoundError:
        STATE = {"students": {}, "assessments": {}, "marks": []}
    except json.JSONDecodeError:
        raise SystemExit("Error: gradebook.json exists but is not valid JSON") from None


def save() -> None:
    """Persist current state to disk without swallowing I/O errors."""
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(STATE, f)


class GradebookHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler with centralized error boundary."""

    def _send(self, code: int, body: Any) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> object:
        length_header = self.headers.get("Content-Length")
        if length_header is None:
            raise ValidationError("Missing Content-Length header")
        try:
            length = int(length_header)
        except ValueError:
            raise ValidationError("Content-Length is not a number") from None

        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValidationError("Body is not valid JSON") from None

    def _dispatch(self, action: Callable[[], tuple[int, Any]]) -> None:
        try:
            code, body = action()
            self._send(code, body)
        except ValidationError as e:
            self._send(400, {"error": str(e)})
        except NotFoundError as e:
            self._send(404, {"error": str(e)})
        except ConflictError as e:
            self._send(409, {"error": str(e)})
        except Exception:
            logger.exception("Unexpected server failure")
            self._send(500, {"error": "internal error"})

    def do_GET(self) -> None:
        self._dispatch(self._route_get)

    def _route_get(self) -> tuple[int, Any]:
        path = self.path.rstrip("/")
        if path == "/students":
            return 200, list(STATE["students"].values())
        if path.startswith("/students/"):
            sid = path.split("/students/")[1]
            if sid not in STATE["students"]:
                raise NotFoundError(f"Student '{sid}' does not exist")
            return 200, STATE["students"][sid]
        if path == "/assessments":
            return 200, list(STATE["assessments"].values())
        if path == "/report":
            return 200, self._build_report()
        raise NotFoundError("Unknown route")

    def _build_report(self) -> list[dict[str, Any]]:
        report: list[dict[str, Any]] = []
        for sid, s in STATE["students"].items():
            total_earned = 0.0
            total_weight = 0.0
            for mark in STATE["marks"]:
                if mark["student"] == sid:
                    aid = mark["assessment"]
                    if aid in STATE["assessments"]:
                        ass = STATE["assessments"][aid]
                        total_earned += (mark["score"] / ass["total"]) * ass["weight"]
                        total_weight += ass["weight"]
            pct = round((total_earned / total_weight) * 100, 2) if total_weight > 0 else 0.0
            report.append({"student": s["name"], "id": sid, "percentage": pct})
        return report

    def do_POST(self) -> None:
        self._dispatch(self._route_post)

    def _route_post(self) -> tuple[int, Any]:
        path = self.path.rstrip("/")
        raw_body = self._read_body()

        if path == "/students":
            student = models.parse_student(raw_body)
            if student.id in STATE["students"]:
                raise ConflictError(f"Student '{student.id}' already exists")
            student_record: dict[str, Any] = {"id": student.id, "name": student.name}
            STATE["students"][student.id] = student_record
            save()
            return 200, student_record

        if path == "/assessments":
            assessment = models.parse_assessment(raw_body)
            if assessment.id in STATE["assessments"]:
                raise ConflictError(f"Assessment '{assessment.id}' already exists")
            assessment_record: dict[str, Any] = {
                "id": assessment.id,
                "title": assessment.title,
                "weight": assessment.weight,
                "total": assessment.total,
            }
            STATE["assessments"][assessment.id] = assessment_record
            save()
            return 200, assessment_record

        if path == "/marks":
            mark = models.parse_mark(raw_body)
            if mark.student not in STATE["students"]:
                raise NotFoundError(f"Student '{mark.student}' does not exist")
            if mark.assessment not in STATE["assessments"]:
                raise NotFoundError(f"Assessment '{mark.assessment}' does not exist")

            target_assessment = STATE["assessments"][mark.assessment]
            if mark.score > target_assessment["total"]:
                raise ValidationError("score cannot exceed assessment total")

            mark_record: dict[str, Any] = {
                "student": mark.student,
                "assessment": mark.assessment,
                "score": mark.score,
            }
            STATE["marks"].append(mark_record)
            save()
            return 200, mark_record

        raise NotFoundError("Unknown route")


def main() -> None:
    port = read_port(sys.argv[1]) if len(sys.argv) > 1 else 8000
    load()
    server = http.server.HTTPServer(("localhost", port), GradebookHandler)
    logger.info("Listening on http://localhost:%d", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()