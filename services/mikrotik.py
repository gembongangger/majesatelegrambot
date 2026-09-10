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
    VOUCHER_NAME_MAX_LEN,
    VOUCHER_NAME_MIN_LEN,
    VOUCHER_NAME_PATTERN,
    VOUCHER_PASS_MAX_LEN,
    VOUCHER_PASS_MIN_LEN,
    VOUCHER_PASS_PATTERN,
    VOUCHER_PREFIX,
    VOUCHER_TEMPLATE,
)
from services.voucher_registry import (
    forget_voucher,
    known_vouchers,
    record_voucher,
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


def template_ready() -> tuple[bool, str]:
    with _api() as api:
        try:
            t = _find_by_username(api.get_resource(_UM_USER).get(), VOUCHER_TEMPLATE)
        except Exception as exc:
            raise MikroTikError(f"Gagal memeriksa template: {exc}")
    if not t:
        return False, f"User template <b>{VOUCHER_TEMPLATE}</b> tidak ditemukan di User Manager."
    prof = t.get("actual-profile")
    if not prof:
        return False, (
            f"User template <b>{VOUCHER_TEMPLATE}</b> <ins>belum punya profil</ins>. "
            f"Buka Web UM <code>http://{MIKROTIK_IP}/userman/</code> → Users → pilih <b>{VOUCHER_TEMPLATE}</b> "
            f"→ assign profil <b>Voucher_90m</b> → Save. Tanpa itu, voucher yang dibuat tidak bisa login."
        )
    return True, f"Template <b>{VOUCHER_TEMPLATE}</b> siap (profil <b>{prof}</b>)."


def create_voucher(
    uptime_min: int | None = None,
    name: str | None = None,
    password: str | None = None,
) -> dict:
    uptime_min = uptime_min or VOUCHER_LIMIT_UPTIME_MIN
    name = name or _generate_name()
    password = password or _generate_password()

    ok, _ = template_ready()
    if not ok:
        raise MikroTikError(
            f"Voucher tidak dibuat: user template <b>{VOUCHER_TEMPLATE}</b> belum punya profil. "
            f"Assign profil <b>Voucher_90m</b> ke {VOUCHER_TEMPLATE} via Web UM "
            f"(<code>http://{MIKROTIK_IP}/userman/</code>)."
        )

    import time

    expires_at = time.time() + uptime_min * 60

    with _api() as api:
        try:
            res = api.get_resource(_UM_USER)
            if _find_by_username(res.get(), name):
                raise MikroTikError(f"Usernama <b>{name}</b> sudah dipakai. Coba yang lain.")
            res.add(
                customer=VOUCHER_CUSTOMER,
                username=name,
                password=password,
                copy_from=VOUCHER_TEMPLATE,
            )
            row = _find_by_username(res.get(), name)
            if not row or not row.get("actual-profile"):
                raise MikroTikError(
                    f"Klon <b>{name}</b> tidak membawa profil (template {VOUCHER_TEMPLATE} tanpa profil). "
                    f"Assign profil dulu, lalu ulangi."
                )
            try:
                res.set(**{"id": row["id"], "disabled": "no"})
            except Exception:
                pass
            record_voucher(name, expires_at=expires_at)
        except MikroTikError:
            raise
        except Exception as exc:
            raise MikroTikError(f"Gagal membuat voucher: {exc}")

    return {"name": name, "password": password, "limit_uptime_min": uptime_min, "expires_at": expires_at}


def list_vouchers() -> list[dict]:
    with _api() as api:
        try:
            users = api.get_resource(_UM_USER).get()
        except Exception as exc:
            raise MikroTikError(f"Gagal membaca voucher: {exc}")

    items = []
    known = known_vouchers()
    known_lower = {k.lower() for k in known}
    prefix = VOUCHER_PREFIX.upper()
    for u in users:
        uname = u.get("username") or ""
        if known:
            if uname.lower() not in known_lower:
                continue
        elif not uname.upper().startswith(prefix):
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
            forget_voucher(name)
            return True
        except Exception as exc:
            raise MikroTikError(f"Gagal menghapus voucher: {exc}")


def is_voucher_known(name: str) -> bool:
    uname = name.lower()
    return any(v.lower() == uname for v in known_vouchers())


def router_name() -> str:
    with _api() as api:
        try:
            data = api.get_resource("/system/identity").get()
            return data[0]["name"] if data else "?"
        except Exception:
            return "?"