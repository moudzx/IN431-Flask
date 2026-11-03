"""Each comparison starts from a fresh task. No live server is required."""
import json
from .put_patch_demo import create_app

CASES = [
    ("A", "PATCH", {"done": True}),
    ("B", "PUT", {"done": True}),
    ("C", "PUT", {"title": "Revised project proposal", "done": True}),
    ("D", "PATCH", {"title": "Revised project proposal"}),
]


def observe_case(label, method, payload):
    client = create_app().test_client()
    before = client.get("/demo/tasks/4").get_json()
    response = client.open("/demo/tasks/4", method=method, json=payload)
    after = client.get("/demo/tasks/4").get_json()
    print("\nCase", label, "starts from a fresh task")
    print("Before:", json.dumps(before))
    print("Request:", method, "/demo/tasks/4", json.dumps(payload))
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.get_json()))
    print("After:", json.dumps(after))


if __name__ == "__main__":
    for case in CASES:
        observe_case(*case)
    print("\nRetry comparison on one fresh instance per method")
    for method, payload in [
        ("PUT", {"title": "Revised project proposal", "done": True}),
        ("PATCH", {"done": True}),
    ]:
        client = create_app().test_client()
        first = client.open("/demo/tasks/4", method=method, json=payload)
        second = client.open("/demo/tasks/4", method=method, json=payload)
        print(method, "statuses", first.status_code, second.status_code,
              "same final representation", first.get_json() == second.get_json())
