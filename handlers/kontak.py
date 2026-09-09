from telegram import Update
from telegram.ext import ContextTypes

from config import KONTAK_INFO
from utils.menu import build_menu


async def kontak_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        KONTAK_INFO,
        disable_web_page_preview=True,
        reply_markup=build_menu(),
    )