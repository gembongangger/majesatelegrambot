from telegram import Update
from telegram.ext import ContextTypes

from config import FASILITAS_INFO, KONTAK_INFO
from services.wordpress_api import get_latest_posts, get_latest_posts_by_category
from utils.formatter import format_berita_list, format_plain_posts
from utils.menu import build_berita_keyboard, build_menu, build_ppdb_keyboard, build_profil_keyboard

from handlers.ppdb import ppdb_bic, ppdb_pengumuman_bic, ppdb_pengumuman_reguler, ppdb_reguler
from handlers.profil import gukar_category, gukar_command, profil_eka, profil_sejarah, profil_struktur, profil_visi_misi

SENDERS = {
    "ppdb:bic": ppdb_bic,
    "ppdb:reguler": ppdb_reguler,
    "ppdb:peng_bic": ppdb_pengumuman_bic,
    "ppdb:peng_reg": ppdb_pengumuman_reguler,
    "profil:visi_misi": profil_visi_misi,
    "profil:sejarah": profil_sejarah,
    "profil:struktur": profil_struktur,
    "profil:gukar": gukar_command,
    "profil:eka": profil_eka,
}

INTRO = {
    "menu:ppdb": ("🌱 INFORMASI MURID BARU (PPDB/PMBM)\n\nPilih program:", build_ppdb_keyboard),
    "menu:profil": ("🏫 PROFIL MADRASAH\n\nPilih informasi:", build_profil_keyboard),
}


async def _edit_or_send(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, markup) -> None:
    query = update.callback_query
    try:
        await query.message.edit_text(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)
    except Exception:
        await context.bot.send_message(update.effective_chat.id, text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in SENDERS:
        await SENDERS[data](update, context)
        return

    if data.startswith("gukar:"):
        key = data.split(":", 1)[1]
        await gukar_category(update, context, key)
        return

    if data in INTRO:
        text, builder = INTRO[data]
        await _edit_or_send(update, context, text, builder())
        return

    if data == "menu:berita":
        posts = await get_latest_posts()
        await _edit_or_send(update, context, format_berita_list(posts), build_berita_keyboard())
        return

    if data == "menu:prestasi":
        posts = await get_latest_posts_by_category("prestasi")
        await _edit_or_send(update, context, format_plain_posts(posts, "🏆 PRESTASI SISWA"), build_menu())
        return

    if data == "menu:fasilitas":
        await _edit_or_send(update, context, FASILITAS_INFO, build_menu())
        return

    if data == "menu:kontak":
        await _edit_or_send(update, context, KONTAK_INFO, build_menu())
        return

    if data in ("menu:menu",):
        await _edit_or_send(update, context, "Pilih menu:", build_menu())
        return

    await query.message.reply_text("Pilih menu:", reply_markup=build_menu())