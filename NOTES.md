# Lab 3 Notes

## Task 2: Vulnerabilities and Bare Except Analysis

### Bare Except Lines (from ruff check)
`ruff check .` detected 3 bare `except:` statements (`E722`):
- **Line 19**: Inside `load()` - Catches all errors silently and initializes an empty state, hiding bugs and file permission issues.
- **Line 28**: Inside `save()` - Silently swallows disk/permission write errors with `pass`.
- **Line 84**: Inside request parsing in `do_POST()` - Catches all errors and returns an incorrect `200 OK` status with `{"error": "bad json"}` instead of `400 Bad Request`.

### Test Cases and Observations

#### (a) GET /students/NOPE
- **Command**: `curl -i http://localhost:8000/students/NOPE`
- **Status Code**: `200 OK` (or crash/empty response)
- **Behavior**: The service fails to return a `404 Not Found` and instead sends null data or unhandled exceptions.

#### (b) POST /students with body 5
- **Command**: `curl -i -X POST http://localhost:8000/students -d "5"`
- **Status Code**: Crashes with `TypeError` in server log (`int object is not subscriptable`).
- **Behavior**: The server assumes the JSON root is always a `dict` without boundary type-checking.

#### (c) Invalid score string "abc"
- **Commands**:
  - `curl -i -X POST http://localhost:8000/students -d '{"id":"S1","name":"Ayesha"}'`
  - `curl -i -X POST http://localhost:8000/assessments -d '{"id":"A1","title":"Quiz","weight":"10","total":"10"}'`
  - `curl -i -X POST http://localhost:8000/marks -d '{"student":"S1","assessment":"A1","score":"abc"}'`
  - `curl -i http://localhost:8000/students/S1`
- **Status Code**: POST succeeds with `200 OK`, saving the string `"abc"` to `gradebook.json`. The subsequent GET fails or crashes when computing percentages.
- **Behavior**: Non-numeric score strings are accepted without validation at the boundary.

#### (d) Zero total / Division by zero
- **Commands**:
  - `curl -i -X POST http://localhost:8000/students -d '{"id":"S1","name":"Ayesha"}'`
  - `curl -i -X POST http://localhost:8000/assessments -d '{"id":"A1","title":"Quiz","weight":"10","total":"0"}'`
  - `curl -i -X POST http://localhost:8000/marks -d '{"student":"S1","assessment":"A1","score":"0"}'`
  - `curl -i http://localhost:8000/report`
- **Status Code / Error**: Crashes with `ZeroDivisionError` on `/report`.
- **Behavior**: An assessment total of `0` is accepted, leading to runtime arithmetic crashes.

#### (e) Dangling reference
- **Command**: `curl -i -X POST http://localhost:8000/marks -d '{"student":"S1","assessment":"DOES_NOT_EXIST","score":"10"}'`
- **Status Code**: Returns `200 OK` and saves mark.
- **Behavior**: Referential integrity is ignored; marks can reference non-existent assessments or students.

### Why `gradebook.json` had to be deleted
The original code lacked boundary validation and directly dumped invalid or corrupt state (such as `score: "abc"` or `total: 0`) into `gradebook.json`. Once bad data was written to disk, every subsequent startup or calculation reloaded this corrupted state and crashed repeatedly. Deleting `gradebook.json` was the only way to reset the database to a clean slate[cite: 1].
