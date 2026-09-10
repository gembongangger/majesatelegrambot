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
    VOUCHER_CUSTOMER,
    VOUCHER_LIMIT_UPTIME_MIN,
    VOUCHER_PREFIX,
    VOUCHER_TEMPLATE,
)

_UM_USER = "/tool/user-manager/user"

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


def _find_by_username(users: list[dict], username: str):
    return next(
        (u for u in users if (u.get("username") or "").lower() == username.lower()),
        None,
    )


def create_voucher(uptime_min: int | None = None, name: str | None = None) -> dict:
    uptime_min = uptime_min or VOUCHER_LIMIT_UPTIME_MIN
    name = name or _generate_name()
    password = _generate_password()

    with _api() as api:
        try:
            res = api.get_resource(_UM_USER)
            try:
                res.add(
                    customer=VOUCHER_CUSTOMER,
                    username=name,
                    password=password,
                    copy_from=VOUCHER_TEMPLATE,
                )
            except Exception:
                res.add(customer=VOUCHER_CUSTOMER, username=name, password=password)
            row = _find_by_username(api.get_resource(_UM_USER).get(), name)
            if row:
                try:
                    res.set(**{"id": row["id"], "disabled": "no", "shared_users": "1"})
                except Exception:
                    pass
        except Exception as exc:
            raise MikroTikError(f"Gagal membuat voucher: {exc}")

    return {"name": name, "password": password, "limit_uptime_min": uptime_min}


def list_vouchers() -> list[dict]:
    with _api() as api:
        try:
            users = api.get_resource(_UM_USER).get()
        except Exception as exc:
            raise MikroTikError(f"Gagal membaca voucher: {exc}")

    items = []
    prefix = VOUCHER_PREFIX.upper()
    for u in users:
        uname = u.get("username") or ""
        if not uname.upper().startswith(prefix):
            continue
        items.append(
            {
                "id": u.get("id"),
                "name": uname,
                "customer": u.get("customer"),
                "password": u.get("password") or "",
                "profile": u.get("actual-profile"),
                "shared_users": u.get("shared-users"),
                "disabled": u.get("disabled") == "true",
                "uptime": u.get("uptime-used"),
                "download_used": u.get("download-used"),
                "last_seen": u.get("last-seen"),
            }
        )
    return items


def set_disabled(name: str, disabled: bool = True) -> bool:
    with _api() as api:
        try:
            res = api.get_resource(_UM_USER)
            users = res.get()
            target = _find_by_username(users, name)
            if not target:
                return False
            res.set(**{"id": target["id"], "disabled": "yes" if disabled else "no"})
            return True
        except Exception as exc:
            raise MikroTikError(f"Gagal mengubah voucher: {exc}")


def remove_voucher(name: str) -> bool:
    with _api() as api:
        try:
            res = api.get_resource(_UM_USER)
            users = res.get()
            target = _find_by_username(users, name)
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