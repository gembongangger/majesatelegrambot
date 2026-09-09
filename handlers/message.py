from telegram import Update
from telegram.ext import ContextTypes

from utils.formatter import detect_intent
from utils.menu import build_menu

from handlers.berita import berita_command
from handlers.ppdb import ppdb_command
from handlers.profil import profil_command
from handlers.prestasi import prestasi_command
from handlers.fasilitas import fasilitas_command
from handlers.kontak import kontak_command

HANDLER_BY_INTENT = {
    "berita": berita_command,
    "ppdb": ppdb_command,
    "profil": profil_command,
    "prestasi": prestasi_command,
    "fasilitas": fasilitas_command,
    "kontak": kontak_command,
}

FALLBACK_TEXT = (
    "Maaf, saya belum bisa menjawab pertanyaan seperti itu. 😅\n"
    "Saya adalah bot informasi <b>MAN 1 Jember</b>.\n\n"
    "Silakan gunakan salah satu menu di bawah ini, atau ketik /help:"
)


async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    intent = detect_intent(text)
    if intent and intent in HANDLER_BY_INTENT:
        await HANDLER_BY_INTENT[intent](update, context)
        return
    await update.message.reply_text(FALLBACK_TEXT, reply_markup=build_menu())