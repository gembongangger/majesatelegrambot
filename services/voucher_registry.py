import json
import time

from pathlib import Path

STORAGE_FILE = Path(__file__).resolve().parent.parent / "vouchers.json"


def _load() -> dict:
    if not STORAGE_FILE.exists():
        return {"vouchers": []}
    try:
        raw = json.loads(STORAGE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"vouchers": []}

    migrated = []
    changed = False
    for v in raw.get("vouchers", []):
        if isinstance(v, str):
            migrated.append({"name": v, "expires_at": None})
            changed = True
        elif isinstance(v, dict):
            migrated.append(v)
    if changed:
        raw["vouchers"] = migrated
        _save(raw)
    return raw


def _save(data: dict) -> None:
    STORAGE_FILE.write_text(json.dumps(data, indent=2))


def _entries() -> list[dict]:
    return _load().get("vouchers", [])


def known_vouchers() -> list[str]:
    return [e["name"] for e in _entries()]


def record_voucher(username: str, expires_at: float | None = None) -> None:
    data = _load()
    uname = username.lower()
    if uname not in [e["name"].lower() for e in data["vouchers"]]:
        data["vouchers"].append({"name": username, "expires_at": expires_at})
        _save(data)


def forget_voucher(username: str) -> None:
    data = _load()
    uname = username.lower()
    remaining = [e for e in data["vouchers"] if e["name"].lower() != uname]
    if len(remaining) != len(data["vouchers"]):
        data["vouchers"] = remaining
        _save(data)


def get_voucher_expiry(username: str) -> float | None:
    uname = username.lower()
    for e in _entries():
        if e["name"].lower() == uname:
            return e.get("expires_at")
    return None


def pop_expired_vouchers() -> list[str]:
    now = time.time()
    data = _load()
    expired = []
    remaining = []
    for e in data["vouchers"]:
        exp = e.get("expires_at")
        if exp is not None and now >= exp:
            expired.append(e["name"])
        else:
            remaining.append(e)
    if expired:
        data["vouchers"] = remaining
        _save(data)
    return expired