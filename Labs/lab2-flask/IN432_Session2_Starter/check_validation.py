"""Small, read-only checkpoints for the lab validator.

Run: python check_validation.py. This sends no HTTP requests and changes no store.
"""
from task_api.errors import ApiError
from task_api.validation import validate_task


def main():
    # name, payload, partial mode, expected clean dictionary, expected error
    cases = [
        ("trim the title", {"title": "  Prepare project proposal  "}, False,
         {"title": "Prepare project proposal"}, False),
        ("retain False", {"done": False}, True, {"done": False}, False),
        ("reject numeric title", {"title": 42}, False, None, True),
        ("reject a short title", {"title": "ab"}, False, None, True),
        ("reject string boolean", {"title": "Example", "done": "false"}, False,
         None, True),
        ("reject integer boolean", {"done": 0}, True, None, True),
        ("require title on creation", {}, False, None, True),
        ("reject empty partial update", {}, True, None, True),
        ("reject client id", {"title": "Example", "id": 99}, False, None, True),
        ("reject nonobject body", [], False, None, True),
    ]
    failed = 0
    for name, payload, partial, expected, expect_error in cases:
        try:
            actual = validate_task(payload, partial=partial)
        except ApiError as error:
            passed = expect_error and error.status_code == 400
            detail = str(error.status_code) + " " + error.code
        else:
            passed = not expect_error and actual == expected
            detail = repr(actual)
        if passed:
            print("PASS", name)
        else:
            failed += 1
            print("FAIL", name, "received", detail)
    print("Validation checks passed:", len(cases) - failed, "/", len(cases))
    if failed:
        print("Read TODO 1a and TODO 1b and run this command again.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
