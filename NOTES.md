Failed test summary line:
3 failed, 25 passed in 0.12s

1. Test Doubles Used:
- Stub: Used in test_add_mark.py as stub_clock, returning a hardcoded timestamp ("2026-10-12 09:00:00").
- Fake: Used in test_add_mark.py as the state dictionary fixture, providing a simplified in-memory working gradebook.
- Mock: Used in test_add_mark.py as save_mock (Mock()), recording whether save() was invoked and with what arguments.

2. Reasons for Not Mocking:
- pct(): Pure logic functions do not produce side effects or interact with external services. Calling pct directly is simpler and tests actual behavior.
- Storage Files in Task 5: Testing directly against temporary files using tmp_path verifies real filesystem reads and writes rather than checking mocked file call expectations.
