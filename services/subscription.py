import json
import os

from pathlib import Path

STORAGE_FILE = Path(__file__).resolve().parent.parent / "data.json"


def _load() -> dict:
    if not STORAGE_FILE.exists():
        return {"subscribers": [], "last_post_id": 0}
    try:
        return json.loads(STORAGE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"subscribers": [], "last_post_id": 0}


def _save(data: dict) -> None:
    STORAGE_FILE.write_text(json.dumps(data, indent=2))


def get_subscribers() -> list[int]:
    return _load()["subscribers"]


def add_subscriber(chat_id: int) -> bool:
    data = _load()
    if chat_id in data["subscribers"]:
        return False
    data["subscribers"].append(chat_id)
    _save(data)
    return True


def remove_subscriber(chat_id: int) -> bool:
    data = _load()
    if chat_id not in data["subscribers"]:
        return False
    data["subscribers"] = [c for c in data["subscribers"] if c != chat_id]
    _save(data)
    return True


def get_last_post_id() -> int:
    return _load()["last_post_id"]


def set_last_post_id(post_id: int) -> None:
    data = _load()
    data["last_post_id"] = post_id
    _save(data)