from telegram import Update
from telegram.ext import ContextTypes

from services.subscription import add_subscriber, get_subscribers, remove_subscriber


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if add_subscriber(chat_id):
        await update.message.reply_text(
            "✅ Anda berhasil berlangganan notifikasi berita.\n"
            "Setiap ada berita baru, saya akan kirim ke chat ini."
        )
    else:
        await update.message.reply_text("ℹ️ Anda sudah berlangganan notifikasi.")


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if remove_subscriber(chat_id):
        await update.message.reply_text("🚫 Anda sudah berhenti berlangganan notifikasi.")
    else:
        await update.message.reply_text("ℹ️ Anda belum berlangganan. Ketik /subscribe untuk mulai.")


async def notify_all(context: ContextTypes.DEFAULT_TYPE, title: str, post_id: int, link: str) -> None:
    for chat_id in get_subscribers():
        try:
            await context.bot.send_message(
                chat_id,
                f"🆕 <b>BERITA BARU</b>\n\n{title}\n🔗 {link}",
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception:
            continue