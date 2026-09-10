import html

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_IDS, VOUCHER_LIMIT_UPTIME_MIN
from services.mikrotik import MikroTikError, create_voucher, list_vouchers, remove_voucher, set_disabled, router_name

from utils.menu import build_menu


def _is_admin(update: Update) -> bool:
    uid = update.effective_user.id
    return uid in ADMIN_IDS


def _denied() -> str:
    return "⛔ Akses ditolak. Perintah voucher hanya untuk admin."


async def voucher_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await update.message.reply_text(_denied())
        return

    args = (update.message.text or "").strip().split()
    sub = args[1].lower() if len(args) > 1 else "buat"
    name = args[2] if len(args) > 2 else None

    try:
        if sub == "list":
            users = list_vouchers()
            if not users:
                await update.message.reply_text("📭 Belum ada voucher (prefix MAJ).")
                return
            lines = [f"📡 <b>VOUCHER WIFI</b> ({len(users)})", ""]
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

        # default: buat voucher
        v = create_voucher()
        uptime_display = v["limit_uptime_min"] / 60 if v["limit_uptime_min"] >= 60 else v["limit_uptime_min"]
        unit = "jam" if v["limit_uptime_min"] >= 60 else "menit"
        await update.message.reply_text(
            "🎫 <b>VOUCHER BARU</b>\n\n"
            f"Username: <code>{html.escape(v['name'])}</code>\n"
            f"Password: <code>{html.escape(v['password'])}</code>\n\n"
            f"⏱️ Masa aktif: {uptime_display:.0f} {unit} sejak login pertama\n\n"
            "Cara pakai: hubungkan ke WiFi, buka browser, login di halaman hotspot dgn kredensial di atas.",
            parse_mode="HTML",
            reply_markup=build_menu(),
        )
    except MikroTikError as exc:
        await update.message.reply_text(f"⚠️ {exc}")