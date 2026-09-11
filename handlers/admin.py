import html

from telegram import Update
from telegram.ext import ContextTypes

from services.admin_registry import add_admin, is_admin, is_master, list_admins, remove_admin


def _denied() -> str:
    return "⛔ Akses ditolak. Perintah ini hanya untuk admin."


def _name(user) -> str:
    return html.escape(user.full_name or user.username or str(user.id))


def _target(update: Update, cmd_arg: str | None):
    reply = update.message.reply_to_message
    if reply and reply.from_user:
        return reply.from_user
    if cmd_arg:
        try:
            return int(cmd_arg)
        except ValueError:
            return None
    return None


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    name = html.escape(user.full_name or user.username or str(user.id))
    await update.message.reply_text(
        f"ℹ️ <b>{name}</b>\n\n"
        f"ID Telegram Anda: <code>{user.id}</code>\n\n"
        "Gunakan ID ini untuk keperluan administrasi (mis. ditambahkan sebagai admin).",
        parse_mode="HTML",
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    caller = update.effective_user
    if not caller or not is_admin(caller.id):
        await update.message.reply_text(_denied())
        return

    args = (update.message.text or "").strip().split()
    sub = args[1].lower() if len(args) > 1 else "list"
    cmd_arg = args[2] if len(args) > 2 else None

    if sub in ("list", "lihat"):
        lines = [f"👮 <b>DAFTAR ADMIN</b> ({len(list_admins())})", ""]
        for a in list_admins():
            role = "<b>Master (dari ADMIN_IDS)</b>" if a["source"] == "master" else "Tambahan (admins.json)"
            alias = html.escape(a["name"])
            lines.append(f"• <code>{a['id']}</code> — {alias}\n   {role}")
        await update.message.reply_text("\n\n".join(lines), parse_mode="HTML")
        return

    if sub not in ("add", "tambah", "remove", "hapus"):
        await update.message.reply_text(
            "Gunakan:\n"
            "/admin — daftar admin\n"
            "/admin add (reply pesan) — tambah admin\n"
            "/admin remove (reply pesan) — hapus admin"
        )
        return

    if not is_master(caller.id):
        await update.message.reply_text("⛔ Hanya admin master (ADMIN_IDS) yang bisa menambah/menghapus admin.")
        return

    target = _target(update, cmd_arg)
    if target is None:
        await update.message.reply_text(
            f"Balas pesan dari pengguna yang dituju, lalu kirim <code>/admin {sub}</code>."
        )
        return

    target_id = target if isinstance(target, int) else target.id

    if sub in ("add", "tambah"):
        if target_id == caller.id:
            await update.message.reply_text("ℹ️ Anda sudah admin master.")
            return
        if is_admin(target_id):
            await update.message.reply_text(f"ℹ️ <code>{target_id}</code> sudah terdaftar sebagai admin.")
            return
        name = "" if isinstance(target, int) else (target.full_name or target.username or "")
        add_admin(target_id, name)
        label = _name(target) if not isinstance(target, int) else str(target_id)
        await update.message.reply_text(
            f"✅ <b>{label}</b> ditambahkan sebagai admin.\n\nKini mereka bisa pakai <code>/voucher</code>.",
            parse_mode="HTML",
        )
        return

    if sub in ("remove", "hapus"):
        if is_master(target_id):
            await update.message.reply_text("⛔ Admin master tidak bisa dihapus via bot. Edit <code>ADMIN_IDS</code> di .env.")
            return
        if remove_admin(target_id):
            await update.message.reply_text(f"🗑️ Admin <code>{target_id}</code> dihapus.", parse_mode="HTML")
        else:
            await update.message.reply_text(f"❌ <code>{target_id}</code> bukan admin tambahan.", parse_mode="HTML")
        return