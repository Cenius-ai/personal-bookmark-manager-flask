"""Database operations for the bookmarks app."""

import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookmarks.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS bookmark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS bookmark_tag (
    bookmark_id INTEGER NOT NULL REFERENCES bookmark(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (bookmark_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_bookmark_tag_bookmark_id ON bookmark_tag(bookmark_id);
CREATE INDEX IF NOT EXISTS idx_bookmark_tag_tag_id ON bookmark_tag(tag_id);
CREATE INDEX IF NOT EXISTS idx_bookmark_created_at ON bookmark(created_at);
"""


def get_db() -> sqlite3.Connection:
    """Return a new database connection with foreign keys enabled and row factory set."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist. Idempotent."""
    conn = get_db()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def get_all_bookmarks(tag_filter: str | None = None) -> list[dict]:
    """Return all bookmarks, optionally filtered by tag name.

    Each bookmark dict includes a 'tags' key with a list of tag names.
    """
    conn = get_db()
    try:
        if tag_filter:
            rows = conn.execute(
                """
                SELECT DISTINCT b.*
                FROM bookmark b
                JOIN bookmark_tag bt ON b.id = bt.bookmark_id
                JOIN tag t ON bt.tag_id = t.id
                WHERE t.name = ?
                ORDER BY b.created_at DESC
                """,
                (tag_filter,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM bookmark ORDER BY created_at DESC"
            ).fetchall()

        bookmarks = []
        for row in rows:
            bm = dict(row)
            tag_rows = conn.execute(
                """
                SELECT t.name FROM tag t
                JOIN bookmark_tag bt ON t.id = bt.tag_id
                WHERE bt.bookmark_id = ?
                ORDER BY t.name
                """,
                (bm["id"],),
            ).fetchall()
            bm["tags"] = [t["name"] for t in tag_rows]
            bookmarks.append(bm)
        return bookmarks
    finally:
        conn.close()


def get_bookmark(bookmark_id: int) -> dict | None:
    """Return a single bookmark with its tags, or None if not found."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM bookmark WHERE id = ?", (bookmark_id,)
        ).fetchone()
        if row is None:
            return None
        bm = dict(row)
        tag_rows = conn.execute(
            """
            SELECT t.name FROM tag t
            JOIN bookmark_tag bt ON t.id = bt.tag_id
            WHERE bt.bookmark_id = ?
            ORDER BY t.name
            """,
            (bm["id"],),
        ).fetchall()
        bm["tags"] = [t["name"] for t in tag_rows]
        return bm
    finally:
        conn.close()


def create_bookmark(title: str, url: str, tag_names: list[str]) -> dict:
    """Insert a bookmark and its tags. Returns the created bookmark dict."""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO bookmark (title, url) VALUES (?, ?)",
            (title, url),
        )
        bookmark_id = cur.lastrowid

        tag_ids = _ensure_tags(conn, tag_names)
        for tid in tag_ids:
            conn.execute(
                "INSERT INTO bookmark_tag (bookmark_id, tag_id) VALUES (?, ?)",
                (bookmark_id, tid),
            )

        conn.commit()
        return get_bookmark(bookmark_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_bookmark(bookmark_id: int, title: str, url: str, tag_names: list[str]) -> dict | None:
    """Update a bookmark and its tags. Returns the updated bookmark or None if not found."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id FROM bookmark WHERE id = ?", (bookmark_id,)
        ).fetchone()
        if row is None:
            conn.close()
            return None

        conn.execute(
            "UPDATE bookmark SET title = ?, url = ? WHERE id = ?",
            (title, url, bookmark_id),
        )

        # Replace tags: remove old, insert new
        conn.execute(
            "DELETE FROM bookmark_tag WHERE bookmark_id = ?", (bookmark_id,)
        )
        tag_ids = _ensure_tags(conn, tag_names)
        for tid in tag_ids:
            conn.execute(
                "INSERT INTO bookmark_tag (bookmark_id, tag_id) VALUES (?, ?)",
                (bookmark_id, tid),
            )

        conn.commit()
        return get_bookmark(bookmark_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_bookmark(bookmark_id: int) -> bool:
    """Delete a bookmark. Returns True if deleted, False if not found."""
    conn = get_db()
    try:
        cur = conn.execute("DELETE FROM bookmark WHERE id = ?", (bookmark_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_all_tags() -> list[dict]:
    """Return all tags with bookmark counts, ordered by count descending."""
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT t.id, t.name, COUNT(bt.bookmark_id) AS bookmark_count
            FROM tag t
            LEFT JOIN bookmark_tag bt ON t.id = bt.tag_id
            GROUP BY t.id
            ORDER BY bookmark_count DESC, t.name ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _ensure_tags(conn: sqlite3.Connection, tag_names: list[str]) -> list[int]:
    """Given a list of tag name strings, ensure each exists and return their IDs."""
    ids = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        row = conn.execute(
            "SELECT id FROM tag WHERE name = ?", (name,)
        ).fetchone()
        if row:
            ids.append(row["id"])
        else:
            cur = conn.execute("INSERT INTO tag (name) VALUES (?)", (name,))
            ids.append(cur.lastrowid)
    return ids
