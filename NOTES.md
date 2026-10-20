# Lab 05 Notes

## Task 1 Baseline Coverage
- Total Coverage: 88%
- File with Lowest Coverage: gradebook.py (82%)

## Task 2 TDD Failures
- Cycle 1 Failure: None (First implementation).
- Cycle 2 Failure: `Failed: DID NOT RAISE <class 'errors.ValidationError'>`
- Cycle 3 Failure: Did not fail first (passed immediately as logic was already sufficient).
- Cycle 4 Failure: `errors.ValidationError: Total weight cannot exceed 100` (due to floating point sum `100.00000000000001`).