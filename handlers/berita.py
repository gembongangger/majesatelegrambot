from telegram import Update
from telegram.ext import ContextTypes

from services.wordpress_api import get_latest_posts
from utils.formatter import format_berita_list
from utils.menu import build_berita_keyboard


async def berita_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    posts = await get_latest_posts()
    await update.message.reply_text(
        format_berita_list(posts),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=build_berita_keyboard(),
    )