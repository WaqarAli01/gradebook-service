# gradebook.py -- the department gradebook service
# started by someone who left. it works. don't touch it.
import datetime
import http.server
import json
import logging
import sys
from collections.abc import Callable
from typing import Any

from errors import ConflictError, NotFoundError, ValidationError
from models import parse_assessment, parse_mark, parse_student
from rules import ensure_weight_fits

logger = logging.getLogger(__name__)

DATA = "gradebook.json"
STATE: dict[str, Any] = {}

def add_assessment(
    state: dict[str, Any],
    assessment: dict[str, Any],
    save: Callable[[], None],
) -> None:
    parsed = parse_assessment(assessment)
    assessment_dict = {
        "id": parsed.id,
        "title": parsed.title,
        "weight": parsed.weight,
        "total": parsed.total,
    }

    if "assessments" not in state:
        state["assessments"] = {}

    assessment_id = assessment_dict["id"]
    if assessment_id in state["assessments"]:
        raise ConflictError(f"Assessment {assessment_id} already exists")

    existing_weights = [
        float(str(a["weight"])) for a in state.get("assessments", {}).values()
    ]
    ensure_weight_fits(existing_weights, float(str(assessment_dict["weight"])))

    state["assessments"][assessment_id] = assessment_dict
    save()

def add_mark(
    state: dict[str, Any],
    mark: dict[str, Any],
    now: Callable[[], str],
    save: Callable[[], None],
) -> None:
    student_id = mark.get("student")
    assessment_id = mark.get("assessment")
    score = mark.get("score")

    if student_id not in state.get("students", {}):
        raise NotFoundError(f"Student {student_id} not found")

    if assessment_id not in state.get("assessments", {}):
        raise NotFoundError(f"Assessment {assessment_id} not found")

    if score is None or float(str(score)) < 0.0:
        raise ValidationError(f"Score {score} cannot be negative")

    assessment_total = float(str(state["assessments"][assessment_id]["total"]))
    if float(str(score)) > assessment_total:
        raise ValidationError(f"Score {score} exceeds assessment total {assessment_total}")

    if "marks" not in state:
        state["marks"] = []

    # Remove pre-existing mark for this student + assessment pair
    state["marks"] = [
        m for m in state["marks"]
        if not (m["student"] == student_id and m["assessment"] == assessment_id)
    ]

    state["marks"].append({
        "student": student_id,
        "assessment": assessment_id,
        "score": score,
        "at": now(),
    })
    save()

def load() -> None:
    global STATE
    try:
        with open(DATA) as f:
            STATE = json.load(f)
    except FileNotFoundError:
        STATE = {"students": {}, "assessments": {}, "marks": []}


def save() -> None:
    with open(DATA, "w") as f:
        json.dump(STATE, f)


def pct(sid: str) -> str:
    total = 0.0
    got = 0.0
    for m in STATE["marks"]:
        if m["student"] == sid:
            a = STATE["assessments"].get(m["assessment"])
            if a:
                got = got + float(m["score"]) * float(a["weight"]) / float(a["total"])
                total = total + float(a["weight"])
    if total == 0:
        return "0"
    return str(round(got, 2))


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass

    def _send(self, code: int, obj: object) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_error(self, error: Exception) -> None:
        if isinstance(error, ValidationError):
            self._send(400, {"error": str(error)})
        elif isinstance(error, NotFoundError):
            self._send(404, {"error": str(error)})
        elif isinstance(error, ConflictError):
            self._send(409, {"error": str(error)})
        else:
            logger.exception("Unexpected error")
            self._send(500, {"error": "internal error"})

    def _get(self) -> tuple[int, object]:
        if self.path == "/students":
            return 200, list(STATE["students"].values())

        if self.path.startswith("/students/"):
            sid = self.path.split("/")[2]

            if sid not in STATE["students"]:
                raise NotFoundError("student not found")

            student = dict(STATE["students"][sid])
            student["percentage"] = pct(sid)
            return 200, student

        if self.path == "/assessments":
            return 200, list(STATE["assessments"].values())

        if self.path == "/report":
            out = []

            for sid in STATE["students"]:
                out.append(
                    {
                        "id": sid,
                        "name": STATE["students"][sid]["name"],
                        "pct": pct(sid),
                    }
                )

            return 200, out

        raise NotFoundError("unknown endpoint")

    def _post(self) -> tuple[int, object]:
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)

        try:
            d = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValidationError("bad json") from error

        if self.path == "/students":
            student = parse_student(d)

            if student.id in STATE["students"]:
                raise ConflictError("student already exists")

            STATE["students"][student.id] = {
                "id": student.id,
                "name": student.name,
                "joined": str(datetime.datetime.now(datetime.UTC)),
            }

            save()
            return 201, STATE["students"][student.id]

        if self.path == "/assessments":
            assessment = parse_assessment(d)

            assessment_dict = {
                "id": assessment.id,
                "title": assessment.title,
                "weight": assessment.weight,
                "total": assessment.total,
            }

            # Delegate to add_assessment so ensure_weight_fits is executed
            add_assessment(STATE, assessment_dict, save)

            return 201, STATE["assessments"][assessment.id]

        if self.path == "/marks":
            mark = parse_mark(d)

            mark_dict = {
                "student": mark.student,
                "assessment": mark.assessment,
                "score": mark.score,
            }

            def clock_now() -> str:
                return str(datetime.datetime.now(datetime.UTC))

            add_mark(STATE, mark_dict, clock_now, save)

            return 201, {"ok": True}

        raise NotFoundError("unknown endpoint")

    def do_GET(self) -> None:
        try:
            code, body = self._get()
            self._send(code, body)
        except Exception as error:  # noqa: BLE001
            self._handle_error(error)

    def do_POST(self) -> None:
        try:
            code, body = self._post()
            self._send(code, body)
        except Exception as error:  # noqa: BLE001
            self._handle_error(error)

def main(argv: list[str]) -> None:
    load()
    port = 8000
    if len(argv) > 1:
        if not argv[1].isdigit() or not 1 <= int(argv[1]) <= 65535:
            raise SystemExit("port must be a whole number from 1 to 65535")
        port = int(argv[1])
    logger.info("gradebook on %s", port)
    http.server.HTTPServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main(sys.argv)