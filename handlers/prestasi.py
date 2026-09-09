from telegram import Update
from telegram.ext import ContextTypes

from services.wordpress_api import get_latest_posts_by_category
from utils.formatter import format_plain_posts
from utils.menu import build_menu


async def prestasi_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    posts = await get_latest_posts_by_category("prestasi")
    text = format_plain_posts(posts, "🏆 PRESTASI SISWA")
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_menu())