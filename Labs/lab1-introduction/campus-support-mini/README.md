# Campus Support Mini

Small Flask app that serves a static page and a JSON API of fictional campus support tickets (IN432 Lab 1).

## Setup

```
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS or Linux
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the application

```
python -m flask --app app run --debug
```

Open http://127.0.0.1:5000/

If port 5000 is busy, use `--port 5001` and open http://127.0.0.1:5001/

## Routes and expected responses

| Request | Status | Content-Type | Body observation |
|---|---|---|---|
| GET / | 200 | text/html | HTML interface |
| GET /api/health | 200 | application/json | `{"status":"ok"}` |
| GET /api/tickets | 200 | application/json | count 3 |
| GET /api/tickets?status=OPEN | 200 | application/json | count 2 |
| GET /api/tickets?status=RESOLVED | 200 | application/json | count 1 |
| GET /api/tickets?status=UNKNOWN | 400 | application/json | `{"error":"Unsupported status"}` |
| GET /api/tickets?status= | 400 | application/json | `{"error":"Unsupported status"}` |
| GET /api/missing | 404 | text/html | Flask "Not Found" page |
| POST /api/tickets | 405 | text/html | Flask "Method Not Allowed" page |

## Interaction trace for Open

1. Browser: the user selects Open and submits the form. The submit handler calls `preventDefault()` and runs `loadTickets()`.
2. Browser: the button is disabled, the list is cleared and feedback shows "Loading...".
3. Network: `GET /api/tickets?status=OPEN` with `Accept: application/json`.
4. Flask: `list_tickets` reads `request.args.get("status")`, validates it, filters `TICKETS`.
5. Network: `200 application/json` with `{"count":2,"items":[...]}`.
6. Browser: `response.ok` is checked, `response.json()` parses the body, `renderTickets(data.items)` rebuilds the DOM list, feedback shows the count.
7. Browser: `finally` re-enables the button.

Validation happens in Flask. JSON is parsed in the browser with `response.json()`.

## Failure observations

- HTTP errors (400, 404, 405) produce a Response, but Fetch does not throw. The code checks `response.ok` and throws manually.
- With the server stopped, Fetch rejects before any Response exists and the catch block shows the error message. The button is re-enabled by `finally`.

## Known limitation: records are in memory

Ticket records live in a Python list and reset when the server restarts. A database would add persistence, concurrent access, querying and the ability to create or update tickets.
