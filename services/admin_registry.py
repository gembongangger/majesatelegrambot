import json
from datetime import datetime

from pathlib import Path

from config import ADMIN_IDS

STORAGE_FILE = Path(__file__).resolve().parent.parent / "admins.json"


def _load() -> dict:
    if not STORAGE_FILE.exists():
        return {"admins": []}
    try:
        return json.loads(STORAGE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"admins": []}


def _save(data: dict) -> None:
    STORAGE_FILE.write_text(json.dumps(data, indent=2))


def is_master(uid: int) -> bool:
    return uid in ADMIN_IDS


def is_admin(uid: int) -> bool:
    if not uid:
        return False
    if is_master(uid):
        return True
    return any(a["id"] == uid for a in _load()["admins"])


def list_admins() -> list[dict]:
    out = [{"id": uid, "name": "Master (ADMIN_IDS)", "source": "master"} for uid in ADMIN_IDS]
    for a in _load()["admins"]:
        out.append({"id": a["id"], "name": a.get("name") or str(a["id"]), "source": "file"})
    return out


def add_admin(uid: int, name: str = "") -> bool:
    if not uid or is_admin(uid):
        return False
    data = _load()
    data["admins"].append(
        {"id": uid, "name": name or str(uid), "added_at": datetime.now().isoformat(timespec="seconds")}
    )
    _save(data)
    return True


def remove_admin(uid: int) -> bool:
    if not uid or is_master(uid):
        return False
    data = _load()
    remaining = [a for a in data["admins"] if a["id"] != uid]
    if len(remaining) == len(data["admins"]):
        return False
    data["admins"] = remaining
    _save(data)
    return True