import json

from pathlib import Path

STORAGE_FILE = Path(__file__).resolve().parent.parent / "vouchers.json"


def _load() -> dict:
    if not STORAGE_FILE.exists():
        return {"vouchers": []}
    try:
        return json.loads(STORAGE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"vouchers": []}


def _save(data: dict) -> None:
    STORAGE_FILE.write_text(json.dumps(data, indent=2))


def known_vouchers() -> list[str]:
    return list(_load()["vouchers"])


def record_voucher(username: str) -> None:
    data = _load()
    uname = username.lower()
    if uname not in [v.lower() for v in data["vouchers"]]:
        data["vouchers"].append(username)
        _save(data)


def forget_voucher(username: str) -> None:
    data = _load()
    uname = username.lower()
    remaining = [v for v in data["vouchers"] if v.lower() != uname]
    if len(remaining) != len(data["vouchers"]):
        data["vouchers"] = remaining
        _save(data)