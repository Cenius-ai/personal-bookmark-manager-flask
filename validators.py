"""Input validation for bookmark fields."""

from urllib.parse import urlparse


def validate_title(title: str | None) -> str | None:
    """Return error message if title is invalid, else None."""
    if not title or not title.strip():
        return "Title is required."
    if len(title.strip()) > 500:
        return "Title must be 500 characters or fewer."
    return None


def validate_url(url: str | None) -> str | None:
    """Return error message if URL is invalid, else None."""
    if not url or not url.strip():
        return "URL is required."

    stripped = url.strip()

    parsed = urlparse(stripped)
    if parsed.scheme not in ("http", "https"):
        return "Invalid URL"
    if not parsed.netloc:
        return "Invalid URL"
    if parsed.netloc not in ("localhost", "127.0.0.1") and "." not in parsed.netloc:
        return "Invalid URL"
    if len(stripped) > 2048:
        return "Invalid URL"

    return None


def parse_tags(tags_string: str | None) -> list[str]:
    """Parse a comma-separated tag string into a list of cleaned tag names.

    Returns a list of unique, non-empty, lowercased, stripped tag names.
    """
    if not tags_string or not tags_string.strip():
        return []

    names = []
    seen = set()
    for part in tags_string.split(","):
        cleaned = part.strip().lower()
        if cleaned and cleaned not in seen:
            names.append(cleaned)
            seen.add(cleaned)
    return names
