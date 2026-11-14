# Student checkpoints — IN432 JavaScript and Flask

Follow the numbered presentation checkpoints. **These are requirements, not solutions.** Implement each stage in `app.js`; save your own working snapshot in the identically named `checkpoints/*.js` file after verification.

## Checkpoint 1 — Hello World

- [ ] Run a short JavaScript expression in the browser Console.
- [ ] Make `app.js` produce a visible log in the Console when the page loads.
- [ ] Explain the difference between the Console and the terminal.

Expected: a JavaScript log appears; no Flask server is needed.

## Checkpoint 2 — Variables, functions and arrays

- [ ] Declare task-related values and use `let` and `const` correctly.
- [ ] Write a function that returns a calculated value.
- [ ] Create task objects, put them in an array, and inspect entries.
- [ ] Count active tasks with a loop, then use an arrow function and `map`.

Expected: Console values match predictions made in class.

## Checkpoint 3 — DOM and events

- [ ] Change the page heading.
- [ ] Read a typed task title when the form is submitted.
- [ ] Avoid a normal page reload during this JavaScript-controlled submission.
- [ ] Display a useful message if the title is empty.
- [ ] React to the Load button click.

Expected: clicking the button or submitting the form changes visible text on the page.

## Checkpoint 4 — Local Task Manager

- [ ] Create an in-memory task array.
- [ ] Render its tasks into `#task-list` and maintain `#task-count`.
- [ ] Add new tasks through the form.
- [ ] Observe what happens after refreshing the browser page.

Expected: tasks appear, but any local changes disappear after a full page reload.

## Checkpoint 5 — GET data from the Flask API

- [ ] Run the Session 5 Flask backend separately on port 5000.
- [ ] Read the API address from `config.js`.
- [ ] Fetch `GET /api/tasks`, check the HTTP result, parse JSON and render tasks.
- [ ] Handle a failed request without crashing the page.

Expected: tasks stored in SQLite appear in the page on port 5500.

## Checkpoint 6 — GET + POST

- [ ] Validate user input.
- [ ] Send `POST /api/tasks` using a JSON request body.
- [ ] Display the refreshed task list after successful creation.
- [ ] Reload the page to show that the backend retained the new task.

Expected: creation returns HTTP 201; a later GET includes the same task.

## Checkpoint 7 — Full CRUD

- [ ] Complete/reopen a task using PATCH `{ "done": true/false }`.
- [ ] Rename a task using PATCH `{ "title": "..." }`.
- [ ] Delete a task using DELETE, and handle the 204 response (no JSON body).
- [ ] Display errors for failed validation, missing task IDs and lost connections.
- [ ] Demonstrate persistence after a browser refresh and backend restart.

Expected: GET, POST, PATCH and DELETE work against the same Flask API. The Session 5 API does **not** use PUT for ordinary task field updates; it uses PATCH.

## Existing Session 5 API contract (for reference)

| Method | Endpoint | Purpose | Expected successful status |
|---|---|---|---|
| GET | `/api/health` | Verify API is running | 200 |
| GET | `/api/tasks` | List task objects | 200 |
| GET | `/api/tasks/{id}` | Read one task | 200 |
| POST | `/api/tasks` | Create task | 201 |
| PATCH | `/api/tasks/{id}` | Change title or done | 200 |
| DELETE | `/api/tasks/{id}` | Delete task | 204 |

Task objects include `id`, `title`, `done`; a Session 5 backend with relationships may also expose `project_id` and `tag_ids`. The frontend should ignore fields it does not need.

## Notes for troubleshooting

- A browser request to Flask on port 5000 is cross-origin when the page is served on port 5500. Flask must permit `http://127.0.0.1:5500` through CORS.
- A browser `fetch()` request is different from using Flask's Python `api_client.py`, which is not subject to browser CORS rules.
- HTTP 400 means the request data may have failed validation; HTTP 404 means the requested route or task was not found; a connection failure may mean Flask is not running.
- The `frontend` folder contains **no backend or persistence code**.
