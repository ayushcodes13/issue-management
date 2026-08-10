"""Read-only Granola API client for scheduled work-memory runs."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_GRANOLA_API_URL = "https://public-api.granola.ai/v1"


class GranolaApiError(RuntimeError):
    pass


def granola_api_key():
    api_key = os.environ.get("GRANOLA_API_KEY")
    if not api_key:
        raise GranolaApiError("GRANOLA_API_KEY is required for the API work-memory runner")
    return api_key


def granola_base_url():
    return os.environ.get("GRANOLA_API_URL", DEFAULT_GRANOLA_API_URL).rstrip("/")


def granola_get(path, params=None):
    params = {key: value for key, value in (params or {}).items() if value not in (None, "")}
    query = urllib.parse.urlencode(params)
    url = f"{granola_base_url()}{path}"
    if query:
        url = f"{url}?{query}"

    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {granola_api_key()}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GranolaApiError(f"Granola API failed with HTTP {exc.code}: {detail[:500]}") from exc


def list_notes(created_after=None, page_size=30, max_pages=10, folder_id=None):
    """List accessible notes, paginated.

    The API response shape is expected to include notes, hasMore, and cursor.
    """
    notes = []
    cursor = None
    for _ in range(max_pages):
        payload = list_notes_page(created_after, page_size, folder_id, cursor)
        notes.extend(notes_from_payload(payload))
        if not has_more(payload):
            break
        cursor = next_cursor(payload)
        if not cursor:
            break
    return notes


def list_notes_page(created_after, page_size, folder_id, cursor):
    variants = [
        {"page_size": page_size, "created_after": created_after, "folder_id": folder_id, "cursor": cursor},
        {"limit": page_size, "created_after": created_after, "folder_id": folder_id, "cursor": cursor},
        {"page_size": page_size, "createdAfter": created_after, "folder_id": folder_id, "cursor": cursor},
        {"limit": page_size, "createdAfter": created_after, "folderId": folder_id, "cursor": cursor},
    ]
    last_error = None
    for params in variants:
        try:
            return granola_get("/notes", params)
        except GranolaApiError as exc:
            last_error = exc
            if "HTTP 400" not in str(exc):
                raise
    raise last_error


def notes_from_payload(payload):
    if isinstance(payload.get("notes"), list):
        return payload["notes"]
    if isinstance(payload.get("data"), list):
        return payload["data"]
    if isinstance(payload.get("items"), list):
        return payload["items"]
    return []


def has_more(payload):
    return bool(payload.get("hasMore") or payload.get("has_more"))


def next_cursor(payload):
    return (
        payload.get("cursor")
        or payload.get("next_cursor")
        or payload.get("nextCursor")
        or (payload.get("pagination") or {}).get("next_cursor")
        or (payload.get("pagination") or {}).get("nextCursor")
    )


def get_note(note_id, include_transcript=False):
    params = {"include": "transcript"} if include_transcript else None
    return granola_get(f"/notes/{urllib.parse.quote(str(note_id), safe='')}", params)


def safe_note_metadata(note):
    return {
        "id": note.get("id") or "",
        "title": note.get("title") or "",
        "created_at": note.get("created_at") or "",
        "updated_at": note.get("updated_at") or "",
        "web_url": note.get("web_url") or "",
        "owner": safe_person(note.get("owner")),
        "attendees_count": len(note.get("attendees") or []),
        "calendar_event": safe_calendar_event(note.get("calendar_event") or {}),
    }


def note_payload_for_ai(note, max_text_chars=3500, include_transcript=False, max_transcript_chars=12000):
    """Return note data for AI, optionally including a capped transcript."""
    text = extract_note_text(note)
    if len(text) > max_text_chars:
        text = text[:max_text_chars] + "\n...[truncated]"
    payload = safe_note_metadata(note)
    payload["summary_text"] = text
    payload["has_transcript_field"] = any("transcript" in key.lower() for key in note.keys())
    if include_transcript:
        transcript = render_transcript(note.get("transcript") or [])
        if len(transcript) > max_transcript_chars:
            transcript = transcript[:max_transcript_chars] + "\n...[transcript truncated]"
        payload["transcript_text"] = transcript
    return payload


def render_transcript(transcript):
    if not isinstance(transcript, list):
        return ""
    lines = []
    for entry in transcript:
        if not isinstance(entry, dict):
            continue
        speaker = speaker_name(entry.get("speaker"))
        text = entry.get("text") or entry.get("content") or entry.get("utterance") or ""
        if not text:
            continue
        start = entry.get("start_time") or entry.get("startTime") or ""
        prefix = speaker or "Unknown"
        if start:
            prefix = f"{prefix} [{start}]"
        lines.append(f"{prefix}: {text}")
    return "\n".join(lines)


def speaker_name(speaker):
    if isinstance(speaker, str):
        return speaker
    if isinstance(speaker, dict):
        return (
            speaker.get("name")
            or speaker.get("email")
            or speaker.get("attribution")
            or speaker.get("source")
            or "Unknown"
        )
    return ""


def extract_note_text(note):
    """Extract summary/notes text while deliberately ignoring transcripts."""
    candidates = []
    for key in ("summary", "notes", "note", "content", "document"):
        if key in note:
            candidates.append(render_value(note.get(key)))
    for key, value in note.items():
        lowered = key.lower()
        if "transcript" in lowered:
            continue
        if lowered in {"id", "object", "title", "owner", "created_at", "updated_at", "web_url", "attendees"}:
            continue
        if lowered in {"summary", "notes", "note", "content", "document"}:
            continue
        if lowered.endswith("_summary") or "summary" in lowered:
            candidates.append(render_value(value))
    text = "\n\n".join(item.strip() for item in candidates if item and item.strip())
    return text.strip()


def render_value(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(render_value(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=True, indent=2)
    return str(value)


def safe_person(person):
    if not isinstance(person, dict):
        return {}
    return {
        "name": person.get("name") or "",
        "email": person.get("email") or "",
    }


def safe_calendar_event(event):
    if not isinstance(event, dict):
        return {}
    return {
        "event_title": event.get("event_title") or "",
        "organiser": event.get("organiser") or "",
        "scheduled_start_time": event.get("scheduled_start_time") or "",
        "scheduled_end_time": event.get("scheduled_end_time") or "",
        "invitees_count": len(event.get("invitees") or []),
    }
