"""Seed the database with sample bookmarks. Idempotent — safe to re-run."""

import os
import sys

# Ensure the project root is on the path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import init_db, get_db

SEED_BOOKMARKS = [
    {
        "title": "Python Documentation",
        "url": "https://docs.python.org/3/",
        "tags": ["python", "documentation", "reference"],
    },
    {
        "title": "Flask Web Framework",
        "url": "https://flask.palletsprojects.com/",
        "tags": ["python", "flask", "web", "framework"],
    },
    {
        "title": "CSS-Tricks",
        "url": "https://css-tricks.com/",
        "tags": ["css", "web", "tutorials"],
    },
    {
        "title": "Mozilla Developer Network",
        "url": "https://developer.mozilla.org/",
        "tags": ["reference", "web", "javascript", "css"],
    },
    {
        "title": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "tags": ["news", "tech", "community"],
    },
    {
        "title": "SQLite Official Site",
        "url": "https://www.sqlite.org/",
        "tags": ["database", "sqlite", "reference"],
    },
    {
        "title": "Real Python Tutorials",
        "url": "https://realpython.com/",
        "tags": ["python", "tutorials", "learning"],
    },
    {
        "title": "A List Apart",
        "url": "https://alistapart.com/",
        "tags": ["web", "design", "articles"],
    },
    {
        "title": "The Architecture of Open Source Applications",
        "url": "https://aosabook.org/",
        "tags": ["architecture", "books", "reference"],
    },
    {
        "title": "GitHub",
        "url": "https://github.com/",
        "tags": ["tools", "development", "git"],
    },
]


def seed_if_empty() -> None:
    """Insert seed bookmarks only if the database is empty."""
    init_db()
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM bookmark").fetchone()[0]
        if count > 0:
            print(f"Database already has {count} bookmarks — skipping seed.")
            return

        for item in SEED_BOOKMARKS:
            cur = conn.execute(
                "INSERT INTO bookmark (title, url) VALUES (?, ?)",
                (item["title"], item["url"]),
            )
            bookmark_id = cur.lastrowid
            for tag_name in item["tags"]:
                tag_row = conn.execute(
                    "SELECT id FROM tag WHERE name = ?", (tag_name,)
                ).fetchone()
                if tag_row:
                    tag_id = tag_row["id"]
                else:
                    tag_cur = conn.execute(
                        "INSERT INTO tag (name) VALUES (?)", (tag_name,)
                    )
                    tag_id = tag_cur.lastrowid
                conn.execute(
                    "INSERT INTO bookmark_tag (bookmark_id, tag_id) VALUES (?, ?)",
                    (bookmark_id, tag_id),
                )

        conn.commit()
        print(f"Seeded {len(SEED_BOOKMARKS)} bookmarks.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_if_empty()
