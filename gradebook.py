"""gradebook.py -- Department gradebook service."""

import http.server
import json
import logging
import sys
from typing import Any, Callable, Dict, List, Tuple

from errors import ConflictError, GradebookError, NotFoundError, ValidationError
import models

# Configure standard logging (replaces print)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DATA = "gradebook.json"
STATE: Dict[str, Any] = {
    "students": {},
    "assessments": {},
    "marks": [],
}


def load() -> None:
    """Load gradebook state from disk, catching only FileNotFoundError."""
    global STATE
    try:
        with open(DATA, "r", encoding="utf-8") as f:
            STATE = json.load(f)
    except FileNotFoundError:
        # Expected on first run; initialize fresh state
        STATE = {"students": {}, "assessments": {}, "marks": []}


def save() -> None:
    """Persist current state to disk without swallowing I/O errors."""
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(STATE, f)


class GradebookHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler with a centralized error boundary."""

    def _send(self, code: int, body: Any) -> None:
        """Serialize and send JSON response."""
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> object:
        """Parse raw request body into a JSON object fail-fast."""
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
        except Exception:
            raise ValidationError("Body is not valid JSON") from None

    def _dispatch(self, action: Callable[[], Tuple[int, Any]]) -> None:
        """Central Error Boundary: maps exceptions to status codes."""
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
            logging.exception("Unexpected server failure")
            self._send(500, {"error": "internal error"})

    # --- GET Handlers ---

    def do_GET(self) -> None:
        self._dispatch(self._route_get)

    def _route_get(self) -> Tuple[int, Any]:
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

    def _build_report(self) -> List[Dict[str, Any]]:
        """Calculate weighted percentage for all students."""
        report = []
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

    # --- POST Handlers ---

    def do_POST(self) -> None:
        self._dispatch(self._route_post)

    def _route_post(self) -> Tuple[int, Any]:
        path = self.path.rstrip("/")
        raw_body = self._read_body()

        if path == "/students":
            student = models.parse_student(raw_body)
            if student.id in STATE["students"]:
                raise ConflictError(f"Student '{student.id}' already exists")
            record = {"id": student.id, "name": student.name}
            STATE["students"][student.id] = record
            save()
            return 200, record

        if path == "/assessments":
            assessment = models.parse_assessment(raw_body)
            if assessment.id in STATE["assessments"]:
                raise ConflictError(f"Assessment '{assessment.id}' already exists")
            record = {
                "id": assessment.id,
                "title": assessment.title,
                "weight": assessment.weight,
                "total": assessment.total,
            }
            STATE["assessments"][assessment.id] = record
            save()
            return 200, record

        if path == "/marks":
            mark = models.parse_mark(raw_body)
            # Enforce referential integrity
            if mark.student not in STATE["students"]:
                raise NotFoundError(f"Student '{mark.student}' does not exist")
            if mark.assessment not in STATE["assessments"]:
                raise NotFoundError(f"Assessment '{mark.assessment}' does not exist")

            # Enforce invariant: score cannot exceed assessment total
            target_assessment = STATE["assessments"][mark.assessment]
            if mark.score > target_assessment["total"]:
                raise ValidationError("score cannot exceed assessment total")

            record = {
                "student": mark.student,
                "assessment": mark.assessment,
                "score": mark.score,
            }
            STATE["marks"].append(record)
            save()
            return 200, record

        raise NotFoundError("Unknown route")


def main() -> None:
    load()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.HTTPServer(("localhost", port), GradebookHandler)
    logging.info("Listening on http://localhost:%d", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()