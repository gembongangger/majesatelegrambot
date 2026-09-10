import random
import string
import secrets
from contextlib import contextmanager

import routeros_api

from config import (
    MIKROTIK_API_PORT,
    MIKROTIK_IP,
    MIKROTIK_PASS,
    MIKROTIK_USER,
    VOUCHER_LIMIT_UPTIME_MIN,
    VOUCHER_PREFIX,
)

_HOTSPOT_USER = "/ip/hotspot/user"

# hindari karakter ganda yang membingungkan
_NAME_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_PASS_ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class MikroTikError(Exception):
    pass


@contextmanager
def _api():
    pool = routeros_api.RouterOsApiPool(
        host=MIKROTIK_IP,
        username=MIKROTIK_USER,
        password=MIKROTIK_PASS,
        port=MIKROTIK_API_PORT,
        plaintext_login=True,
    )
    try:
        api = pool.get_api()
    except Exception as exc:
        try:
            pool.disconnect()
        except Exception:
            pass
        raise MikroTikError(f"Tidak dapat terhubung ke MikroTik: {exc}")
    try:
        yield api
    finally:
        pool.disconnect()


def _generate_name() -> str:
    return f"{VOUCHER_PREFIX}-{''.join(random.choices(_NAME_ALPHABET, k=5))}"


def _generate_password(length: int = 8) -> str:
    return "".join(secrets.choice(_PASS_ALPHABET) for _ in range(length))


def create_voucher(uptime_min: int | None = None, name: str | None = None) -> dict:
    uptime_min = uptime_min or VOUCHER_LIMIT_UPTIME_MIN
    name = name or _generate_name()
    password = _generate_password()

    with _api() as api:
        try:
            res = api.get_resource(_HOTSPOT_USER)
            res.add(name=name, password=password, limit_uptime=f"{uptime_min}m", comment=password)
        except Exception as exc:
            raise MikroTikError(f"Gagal membuat voucher: {exc}")

    return {"name": name, "password": password, "limit_uptime_min": uptime_min}


def list_vouchers() -> list[dict]:
    with _api() as api:
        try:
            users = api.get_resource(_HOTSPOT_USER).get()
        except Exception as exc:
            raise MikroTikError(f"Gagal membaca voucher: {exc}")

    items = []
    for u in users:
        items.append(
            {
                "id": u.get("id"),
                "name": u.get("name"),
                "limit_uptime": u.get("limit-uptime"),
                "uptime": u.get("uptime"),
                "bytes_in": u.get("bytes-in"),
                "bytes_out": u.get("bytes-out"),
                "disabled": u.get("disabled") == "true",
                "comment": u.get("comment"),
            }
        )
    return items


def _find_by_name(users: list[dict], name: str):
    return next((u for u in users if u["name"] == name or u["name"].lower() == name.lower()), None)


def set_disabled(name: str, disabled: bool = True) -> bool:
    with _api() as api:
        try:
            res = api.get_resource(_HOTSPOT_USER)
            users = res.get()
            target = _find_by_name(users, name)
            if not target:
                return False
            res.set(**{"id": target["id"], "disabled": "yes" if disabled else "no"})
            return True
        except Exception as exc:
            raise MikroTikError(f"Gagal mengubah voucher: {exc}")


def remove_voucher(name: str) -> bool:
    with _api() as api:
        try:
            res = api.get_resource(_HOTSPOT_USER)
            users = res.get()
            target = _find_by_name(users, name)
            if not target:
                return False
            res.remove(id=target["id"])
            return True
        except Exception as exc:
            raise MikroTikError(f"Gagal menghapus voucher: {exc}")


def router_name() -> str:
    with _api() as api:
        try:
            data = api.get_resource("/system/identity").get()
            return data[0]["name"] if data else "?"
        except Exception:
            return "?"