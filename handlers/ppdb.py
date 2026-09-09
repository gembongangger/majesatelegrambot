from telegram import Update
from telegram.ext import ContextTypes

from services.wordpress_api import get_page, get_posts_search_by_title
from utils.formatter import format_plain_posts, truncate
from utils.menu import build_ppdb_keyboard

_INTRO = "🌱 <b>INFORMASI MURID BARU (PPDB/PMBM)</b>\n\nPilih program yang ingin Anda ketahui:"


def _format_page(page: dict, label: str) -> str:
    text = f"🌱 <b>{label}</b>\n\n{truncate(page['content'], 3400)}"
    downloads = page.get("downloads") or []
    for name, url in downloads:
        text += f"\n📥 <b>{name}</b>\n🔗 {url}"
    return text


async def ppdb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_INTRO, reply_markup=build_ppdb_keyboard())


async def ppdb_bic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    page = await get_page("program-unggulan-dan-bic")
    text = _format_page(page, "PROGRAM BIC DAN REGULER") if page else "❌ Data tidak ditemukan."
    await _edit(update, context, text)


async def ppdb_reguler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Halaman program BIC juga mencakup informasi reguler; jika ada slug khusus, sesuaikan.
    page = await get_page("program-unggulan-dan-bic")
    text = _format_page(page, "PROGRAM REGULER") if page else "❌ Data tidak ditemukan."
    await _edit(update, context, text)


async def ppdb_pengumuman_bic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    posts = await get_posts_search_by_title("BIC", "BIC")
    text = format_plain_posts(posts, "📢 PENGUMUMAN BIC")
    await _edit(update, context, text)


async def ppdb_pengumuman_reguler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    posts = await get_posts_search_by_title("REGULER", "REGULER")
    text = format_plain_posts(posts, "📢 PENGUMUMAN REGULER")
    await _edit(update, context, text)


async def _edit(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    query = update.callback_query
    if query:
        await query.answer()
        try:
            await query.message.edit_text(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_ppdb_keyboard())
            return
        except Exception:
            pass
    await context.bot.send_message(update.effective_chat.id, text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_ppdb_keyboard())