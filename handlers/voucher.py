import html
import re

from telegram import Update
from telegram.ext import ContextTypes

from config import (
    VOUCHER_LIMIT_UPTIME_MIN,
    VOUCHER_NAME_MAX_LEN,
    VOUCHER_NAME_MIN_LEN,
    VOUCHER_NAME_PATTERN,
    VOUCHER_PASS_MAX_LEN,
    VOUCHER_PASS_MIN_LEN,
    VOUCHER_PASS_PATTERN,
)
from services.mikrotik import (
    MikroTikError,
    create_voucher,
    list_vouchers,
    remove_voucher,
    set_disabled,
    router_name,
    template_ready,
)
from services.admin_registry import is_admin

from utils.menu import build_menu


def _is_admin(update: Update) -> bool:
    return is_admin(update.effective_user.id)


def _denied() -> str:
    return "⛔ Akses ditolak. Perintah voucher hanya untuk admin."


def _voucher_msg(v: dict) -> str:
    uptime_display = v["limit_uptime_min"] / 60 if v["limit_uptime_min"] >= 60 else v["limit_uptime_min"]
    unit = "jam" if v["limit_uptime_min"] >= 60 else "menit"
    return (
        "🎫 <b>VOUCHER BARU</b>\n\n"
        f"Username: <code>{html.escape(v['name'])}</code>\n"
        f"Password: <code>{html.escape(v['password'])}</code>\n\n"
        f"⏱️ Masa aktif: {uptime_display:.0f} {unit} sejak login pertama\n\n"
        "Cara pakai: hubungkan ke WiFi, buka browser, login di halaman hotspot dgn kredensial di atas."
    )


async def voucher_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await update.message.reply_text(_denied())
        return

    args = (update.message.text or "").strip().split()
    sub = args[1].lower() if len(args) > 1 else "buat"
    name = args[2] if len(args) > 2 else None

    try:
        if sub == "cek":
            ok, msg = template_ready()
            await update.message.reply_text(
                ("✅ " + msg if ok else "⚠️ " + msg),
                parse_mode="HTML",
            )
            return

        if sub == "list":
            tpl_ok, tpl_msg = template_ready()
            users = list_vouchers()
            if not users and tpl_ok:
                await update.message.reply_text("📭 Belum ada voucher (prefix MAJ).")
                return
            lines = []
            if not tpl_ok:
                lines.append(f"⚠️ <b>CEK TEMPLATE DULU:</b>\n{tpl_msg}\n\n---")
            if tpl_ok and not users:
                await update.message.reply_text("📭 Belum ada voucher (prefix MAJ).")
                return
            lines.append(f"📡 <b>VOUCHER WIFI</b> ({len(users)})")
            lines.append("")
            for u in users:
                status = "🔴 nonaktif" if u["disabled"] else "🟢 aktif"
                prof = u["profile"] or "-"
                seen = u["last_seen"] or "belum dipakai"
                lines.append(
                    f"• <b>{html.escape(u['name'])}</b> — {status}\n"
                    f"   profil: {html.escape(prof)} | pakai: {html.escape(seen)}\n"
                    f"   pass: <code>{html.escape(u['password'])}</code>"
                )
            await update.message.reply_text("\n\n".join(lines), parse_mode="HTML", reply_markup=build_menu())
            return

        if sub in ("kustom", "custom", "minta"):
            if len(args) < 4:
                await update.message.reply_text("Gunakan: /voucher kustom <username> <password>")
                return
            username = args[2]
            password = args[3]
            if not re.fullmatch(VOUCHER_NAME_PATTERN, username) or not (
                VOUCHER_NAME_MIN_LEN <= len(username) <= VOUCHER_NAME_MAX_LEN
            ):
                await update.message.reply_text(
                    f"⚠️ Username harus {VOUCHER_NAME_MIN_LEN}-{VOUCHER_NAME_MAX_LEN} karakter, "
                    "hanya huruf/angka dan ` . _ -` (tanpa spasi)."
                )
                return
            if not re.fullmatch(VOUCHER_PASS_PATTERN, password) or not (
                VOUCHER_PASS_MIN_LEN <= len(password) <= VOUCHER_PASS_MAX_LEN
            ):
                await update.message.reply_text(
                    f"⚠️ Password harus {VOUCHER_PASS_MIN_LEN}-{VOUCHER_PASS_MAX_LEN} karakter, tanpa spasi."
                )
                return
            v = create_voucher(name=username, password=password)
            await update.message.reply_text(_voucher_msg(v), parse_mode="HTML", reply_markup=build_menu())
            return

        if sub in ("hapus", "remove", "del"):
            if not name:
                await update.message.reply_text("Gunakan: /voucher hapus <username>")
                return
            ok = remove_voucher(name)
            await update.message.reply_text(
                f"🗑️ Voucher <b>{html.escape(name)}</b> dihapus." if ok else f"❌ Voucher <b>{html.escape(name)}</b> tidak ditemukan.",
                parse_mode="HTML",
            )
            return

        if sub in ("off", "disable", "nonaktif"):
            if not name:
                await update.message.reply_text("Gunakan: /voucher off <username>")
                return
            ok = set_disabled(name, True)
            await update.message.reply_text(
                f"⛔ Voucher <b>{html.escape(name)}</b> dinonaktifkan." if ok else f"❌ Voucher <b>{html.escape(name)}</b> tidak ditemukan.",
                parse_mode="HTML",
            )
            return

        if sub in ("on", "enable", "aktif"):
            if not name:
                await update.message.reply_text("Gunakan: /voucher on <username>")
                return
            ok = set_disabled(name, False)
            await update.message.reply_text(
                f"✅ Voucher <b>{html.escape(name)}</b> diaktifkan kembali." if ok else f"❌ Voucher <b>{html.escape(name)}</b> tidak ditemukan.",
                parse_mode="HTML",
            )
            return

        # default: buat voucher (random)
        v = create_voucher()
        await update.message.reply_text(_voucher_msg(v), parse_mode="HTML", reply_markup=build_menu())
    except MikroTikError as exc:
        await update.message.reply_text(f"⚠️ {exc}")