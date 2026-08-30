"""Personal Bookmarks Manager — Flask application."""

import os
import sys

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)

from models import (
    create_bookmark,
    delete_bookmark,
    get_all_bookmarks,
    get_all_tags,
    get_bookmark,
    init_db,
    update_bookmark,
)
from validators import parse_tags, validate_title, validate_url

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cenius-dev-bookmarks-a1b2c3d4e5f6")

_db_ready = False


@app.before_request
def _ensure_db() -> None:
    """Create tables and seed on first request if the database is empty."""
    global _db_ready
    if _db_ready:
        return

    init_db()

    from models import get_db

    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM bookmark").fetchone()[0]
    finally:
        conn.close()

    if count == 0:
        import seed

        seed.seed_if_empty()

    _db_ready = True


@app.route("/")
def index():
    """Redirect root to the bookmarks page."""
    return redirect(url_for("list_bookmarks"))


@app.route("/bookmarks", methods=["GET", "POST"])
def list_bookmarks():
    """Main page: split-pane with bookmark list and add/edit form."""
    if request.method == "POST":
        return _handle_add()

    tag_filter = request.args.get("tag", "").strip() or None
    edit_id_raw = request.args.get("edit", "").strip()

    bookmarks = get_all_bookmarks(tag_filter)
    all_tags = get_all_tags()

    edit_bookmark = None
    if edit_id_raw:
        try:
            edit_bookmark = get_bookmark(int(edit_id_raw))
        except (ValueError, TypeError):
            pass

    return render_template(
        "bookmarks.html",
        bookmarks=bookmarks,
        all_tags=all_tags,
        tag_filter=tag_filter,
        edit_bookmark=edit_bookmark,
    )


def _handle_add():
    """Process the add-bookmark form submission."""
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    tags_raw = request.form.get("tags", "")

    title_error = validate_title(title)
    url_error = validate_url(url)

    if title_error or url_error:
        bookmarks = get_all_bookmarks()
        all_tags = get_all_tags()
        return render_template(
            "bookmarks.html",
            bookmarks=bookmarks,
            all_tags=all_tags,
            tag_filter=None,
            edit_bookmark=None,
            form_data={"title": title, "url": url, "tags": tags_raw or ""},
            title_error=title_error,
            url_error=url_error,
        ), 422

    tag_names = parse_tags(tags_raw)
    create_bookmark(title, url, tag_names)
    return redirect(url_for("list_bookmarks"))


@app.route("/bookmarks/<int:bookmark_id>/edit", methods=["POST"])
def edit_bookmark(bookmark_id: int):
    """Handle edit-bookmark form submission."""
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    tags_raw = request.form.get("tags", "")

    title_error = validate_title(title)
    url_error = validate_url(url)

    if title_error or url_error:
        bookmarks = get_all_bookmarks()
        all_tags = get_all_tags()
        bm = get_bookmark(bookmark_id)
        return render_template(
            "bookmarks.html",
            bookmarks=bookmarks,
            all_tags=all_tags,
            tag_filter=None,
            edit_bookmark=bm,
            form_data={"title": title, "url": url, "tags": tags_raw or ""},
            title_error=title_error,
            url_error=url_error,
        ), 422

    tag_names = parse_tags(tags_raw)
    updated = update_bookmark(bookmark_id, title, url, tag_names)
    if updated is None:
        return "Bookmark not found.", 404

    return redirect(url_for("list_bookmarks"))


@app.route("/bookmarks/<int:bookmark_id>/delete", methods=["POST"])
def delete_bookmark_route(bookmark_id: int):
    """Delete a bookmark."""
    deleted = delete_bookmark(bookmark_id)
    if not deleted:
        return "Bookmark not found.", 404
    return redirect(url_for("list_bookmarks"))


@app.route("/stats")
def stats():
    """Tag statistics page."""
    all_tags = get_all_tags()
    return render_template("stats.html", all_tags=all_tags)


# ---------------------------------------------------------------------------
# Security headers on every response
# ---------------------------------------------------------------------------
@app.after_request
def _set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
