"""Expt 1 - Personal Assistant Memory Server (MCP).

Tools: save_note, search_notes (+ list_notes, update_note, delete_note for full CRUD).
Notes are stored in a local notes.json file next to this script.
"""
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

NOTES_FILE = Path(__file__).parent / "notes.json"
mcp = FastMCP("personal-assistant-memory")

STOPWORDS = {
    "a", "an", "the", "i", "me", "my", "we", "you", "is", "are", "was", "were", "do", "did",
    "does", "what", "when", "where", "which", "who", "how", "about", "say", "said", "tell",
    "of", "to", "in", "on", "for", "and", "or", "that", "this", "it", "with", "have", "had",
}


def _load() -> list[dict]:
    if not NOTES_FILE.exists():
        return []
    try:
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save(notes: list[dict]) -> None:
    NOTES_FILE.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")


def _keywords(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _format(note: dict) -> str:
    tags = ", ".join(note["tags"]) if note["tags"] else "none"
    return f"[{note['id']}] {note['content']} (tags: {tags}; saved: {note['created_at']})"


@mcp.tool()
def save_note(content: str, tags: list[str] | None = None) -> str:
    """Save a new note to memory (CREATE).

    Args:
        content: The text of the note to remember.
        tags: Optional short labels, e.g. ["project", "deadline"].
    """
    notes = _load()
    note = {
        "id": uuid.uuid4().hex[:8],
        "content": content.strip(),
        "tags": [t.strip().lower() for t in (tags or []) if t.strip()],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    notes.append(note)
    _save(notes)
    return f"Saved note {note['id']}: {note['content']}"


@mcp.tool()
def search_notes(query: str) -> str:
    """Search saved notes by keywords (READ). Matches note text and tags.

    Args:
        query: What to look for, e.g. "project deadline".
    """
    words = _keywords(query)
    if not words:
        return "Please give at least one meaningful keyword to search for."
    scored = []
    for note in _load():
        haystack = note["content"].lower()
        score = sum(2 if w in note["tags"] else 0 for w in words) + sum(w in haystack for w in words)
        if score:
            scored.append((score, note))
    if not scored:
        return f"No notes found for: {query}"
    scored.sort(key=lambda s: s[0], reverse=True)
    return "\n".join(_format(n) for _, n in scored[:5])


@mcp.tool()
def list_notes() -> str:
    """List every saved note (READ)."""
    notes = _load()
    return "\n".join(_format(n) for n in notes) if notes else "No notes saved yet."


@mcp.tool()
def update_note(note_id: str, content: str) -> str:
    """Replace the text of an existing note (UPDATE).

    Args:
        note_id: The id shown in brackets when the note was saved or listed.
        content: The new text.
    """
    notes = _load()
    for note in notes:
        if note["id"] == note_id:
            note["content"] = content.strip()
            _save(notes)
            return f"Updated note {note_id}."
    return f"No note with id {note_id}."


@mcp.tool()
def delete_note(note_id: str) -> str:
    """Delete a note by id (DELETE).

    Args:
        note_id: The id of the note to remove.
    """
    notes = _load()
    kept = [n for n in notes if n["id"] != note_id]
    if len(kept) == len(notes):
        return f"No note with id {note_id}."
    _save(kept)
    return f"Deleted note {note_id}."


if __name__ == "__main__":
    mcp.run(transport="stdio")
