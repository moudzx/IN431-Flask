# IN432 — JavaScript Frontend Starter (Student Edition)

**This download contains only the frontend. No completed JavaScript CRUD solution is included.**

Use this folder with the *separate* Session 5 Flask backend you already developed. Do **not** copy this frontend inside `backend/` or inside `task_api/static/`.

## 1. Start the frontend independently

Open a terminal in **this `frontend` folder**:

```bash
python -m http.server 5500 --bind 127.0.0.1
```

Open <http://127.0.0.1:5500/> in your browser. The HTML and CSS should appear, but the application features are **deliberately not implemented** until you complete the checkpoints.

Keep a second terminal for Flask, which typically runs at <http://127.0.0.1:5000/>. Start the Flask backend when you reach Checkpoint 5. It must be configured to allow the frontend's origin via CORS.

## 2. Your working files

| File | Purpose |
|---|---|
| `index.html` | Supplied HTML form, list, buttons and status elements |
| `styles.css` | Supplied styling; no CSS work is necessary to begin |
| `config.js` | API location, configured for the local Flask server |
| `app.js` | **Your JavaScript code — edit this file during every checkpoint** |
| `checkpoints/01_hello.js` … `07_full_crud.js` | **Empty milestone placeholders** for snapshots of your own work |
| `CHECKPOINTS.md` | Tasks, expected behavior and the HTTP contract |

**Workflow:** Follow the presentation → implement the current feature in `app.js` → test it → **copy your own `app.js` into the matching `checkpoints/XX_*.js`** → proceed to the next feature. The checkpoint files are not loaded by the webpage. Only `app.js` is loaded.

Use the browser Console and Network tab to observe results. The `Add task` and `Load tasks` buttons are initially unconnected on purpose.

## 3. Keep the frontend and backend separate

Typical folder layout:

```text
IN432/
  backend/                  # Existing Session 5 Flask task_api package
  frontend/                 # This starter folder
    index.html
    styles.css
    config.js
    app.js
    checkpoints/
```

The browser fetches the API with the URL in `config.js`. There is **no import of Python or database code** into the frontend, and the frontend uses its own HTTP server rather than Flask to serve its files.

## 4. What to submit

Submit your final `app.js`, all seven completed checkpoint snapshots, and a short demonstration of persisted tasks (reload the page, then restart Flask and reload again). Do not submit your `.venv` or database backup unless instructed by the instructor.
