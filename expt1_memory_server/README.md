# Expt 1: Personal Assistant Memory Server (MCP)

An MCP server that stores notes in `notes.json`, and a Python client where an LLM decides which tool to call.

## Tools
| Tool | CRUD | Description |
| --- | --- | --- |
| `save_note(content, tags)` | Create | Save a note |
| `search_notes(query)` | Read | Keyword search over text and tags |
| `list_notes()` | Read | Show all notes |
| `update_note(note_id, content)` | Update | Edit a note |
| `delete_note(note_id)` | Delete | Remove a note |

## Setup
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env       # macOS/Linux: cp .env.example .env  (then add your Groq API key)
```

## Run
```bash
python client.py
```
Try:
- `Remember that the project deadline is Nov 15` -> calls `save_note`
- `What did I say about the project deadline?` -> calls `search_notes`

The client starts `server.py` automatically over stdio.
