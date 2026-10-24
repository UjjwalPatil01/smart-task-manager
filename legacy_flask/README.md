# Smart Task Manager — Legacy Flask Edition (v1.0 Milestone)

This directory preserves the original single-file Flask web application for historical reference and portfolio continuity.

## Architecture Overview
- **Framework:** Flask 3.x
- **Frontend:** Jinja2 server-rendered templates (`templates/`) and vanilla CSS (`static/`)
- **Persistence:** JSON file storage (`tasks.json`)
- **AI Integration:** Google Gemini SDK (`google.genai`)

## Known Architectural Limitations (Resolved in Modern v2.0)
The legacy Flask implementation contains several architectural limitations that were solved in the modern FastAPI + Streamlit rewrite:
1. **Array Index Mutation Race:** `/done/<int:index>`, `/undo/<int:index>`, and `/delete/<int:index>` manipulate raw array indices. If tasks are filtered or searched in the UI, modifying an index alters the wrong task record.
2. **Missing Database Persistence:** Relies directly on un-journaled JSON file writes, creating race conditions during concurrent requests.
3. **Boot Crash on Missing Secrets:** `app.py` raises an unhandled `ValueError` at import time if `GOOGLE_API_KEY` is not configured in `.env`.
4. **Monolithic Layout:** Web routes, AI logic, and data functions are coupled into a single script.

## Running the Legacy App Standalone
To test or inspect the legacy application independently:
```bash
# 1. Install legacy dependencies:
pip install -r legacy_flask/requirements.txt

# 2. Run Flask server:
python legacy_flask/app.py
```
*Note: Make sure `GOOGLE_API_KEY` is set in your `.env` before starting.*
