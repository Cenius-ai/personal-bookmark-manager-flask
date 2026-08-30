# Installation

## 1. Prerequisites

- **Python 3.11** or later
- **pip** (included with Python)

## 2. Get the code

Obtain the project source files. You can clone the repository or download the source archive.

## 3. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure environment

Copy the example environment file and modify it if needed:

```bash
cp .env.example .env
```

The following variables are available (see `.env.example` for details):
- `SECRET_KEY` — Flask secret key.
- `FLASK_DEBUG` — Set to `1` to enable debug mode.
- `PORT` — Override the default port (note: Flask’s built‑in server uses `FLASK_RUN_PORT`, so use that if needed).

## 6. Initialize the database

No manual step is required. The application automatically creates the SQLite database (`bookmarks.db`) and seeds it with sample data on the first request.

## 7. Run the development server

```bash
flask --app app run --debug
```

The server starts on `http://localhost:5000`.

## 8. Verify

Open a browser and visit `http://localhost:5000/` — you should see the bookmarks list.

## 9. Troubleshooting

- **ImportError: No module named 'flask'**  
  Make sure you have activated the virtual environment and installed dependencies with `pip install -r requirements.txt`.

- **Port 5000 is already in use**  
  Use `flask --app app run --debug --port 8000` (or set the `FLASK_RUN_PORT` environment variable).

- **Database issues**  
  Delete `bookmarks.db` and restart the app; it will be recreated automatically.