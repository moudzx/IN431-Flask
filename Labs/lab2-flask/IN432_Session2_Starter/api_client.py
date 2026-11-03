"""Small HTTP client using only the Python standard library."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("method", choices=["GET", "POST", "PATCH", "DELETE", "PUT"])
    parser.add_argument("path")
    body_group = parser.add_mutually_exclusive_group()
    body_group.add_argument("--json", dest="json_file")
    body_group.add_argument("--raw", dest="raw_file")
    parser.add_argument("--content-type", default="application/json")
    parser.add_argument("--base", default="http://127.0.0.1:5000")
    args = parser.parse_args()
    headers = {"Accept": "application/json"}
    data = None
    file_name = args.json_file or args.raw_file
    if file_name:
        data = Path(file_name).read_bytes()
        if args.json_file:
            json.loads(data)  # Use --raw for deliberately malformed JSON.
        headers["Content-Type"] = args.content_type
    req = Request(args.base.rstrip("/") + "/" + args.path.lstrip("/"),
                  data=data, headers=headers, method=args.method)
    try:
        response = urlopen(req, timeout=5)
    except HTTPError as error:
        response = error
    except URLError as error:
        print("Connection failed:", error.reason)
        print("Start the Flask server and check the base URL and port.")
        raise SystemExit(2)
    with response:
        print("HTTP", response.status)
        for key in ("Content-Type", "Location", "Allow", "X-Request-ID"):
            if key in response.headers:
                print(key + ":", response.headers[key])
        body = response.read().decode("utf-8")
        if not body:
            print("<empty body>")
        else:
            try:
                print(json.dumps(json.loads(body), indent=2))
            except json.JSONDecodeError:
                print(body)


if __name__ == "__main__":
    main()
