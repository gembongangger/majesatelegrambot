from telegram import Update
from telegram.ext import ContextTypes

from services.gukar_scraper import get_gukar_category, get_gukar_sections
from services.wordpress_api import get_page
from utils.formatter import truncate
from utils.menu import build_gukar_keyboard, build_menu, build_profil_keyboard


async def profil_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🏫 <b>PROFIL MADRASAH</b>\n\nPilih informasi yang ingin Anda lihat:",
        reply_markup=build_profil_keyboard(),
    )


async def _show_profil(update: Update, context: ContextTypes.DEFAULT_TYPE, slug: str, label: str, back: bool = True) -> None:
    page = await get_page(slug)
    text = f"🏫 <b>{label}</b>\n\n{truncate(page['content'], 3800)}" if page else "❌ Data tidak ditemukan."
    markup = build_profil_keyboard() if back else build_menu()
    query = update.callback_query
    if query:
        await query.answer()
        try:
            await query.message.edit_text(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)
            return
        except Exception:
            pass
    await context.bot.send_message(update.effective_chat.id, text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)


async def profil_visi_misi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _show_profil(update, context, "mis", "VISI DAN MISI")


async def profil_sejarah(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _show_profil(update, context, "sejarah", "SEJARAH")


async def profil_struktur(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _show_profil(update, context, "struktur", "STRUKTUR ORGANISASI")


async def profil_gukar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _show_profil(update, context, "gukar", "GURU DAN KARYAWAN")


async def profil_eka(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _show_profil(update, context, "eka", "EKSTRAKURIKULER")


async def gukar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sections = await get_gukar_sections()
    intro = "🧑‍🏫 <b>GURU & KARYAWAN</b>\n\nPilih kategori berikut:"
    if sections:
        total = sum(len(names) for names in sections.values())
        intro = f"🧑‍🏫 <b>GURU & KARYAWAN</b> - {total} pendidik\n\nPilih kategori berikut:"
    query = update.callback_query
    if query:
        await query.answer()
        try:
            await query.message.edit_text(intro, parse_mode="HTML", reply_markup=build_gukar_keyboard())
            return
        except Exception:
            pass
    await context.bot.send_message(update.effective_chat.id, intro, parse_mode="HTML", reply_markup=build_gukar_keyboard())


async def gukar_category(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> None:
    result = await get_gukar_category(key)
    query = update.callback_query
    if query:
        await query.answer()
    if not result:
        text = "❌ Data tidak ditemukan."
    else:
        label, names = result
        lines = [f"🧑‍🏫 <b>{label}</b>", ""]
        lines += [f"• {n}" for n in names]
        text = "\n".join(lines)
    if query:
        try:
            await query.message.edit_text(text, parse_mode="HTML", reply_markup=build_gukar_keyboard())
            return
        except Exception:
            pass
    await context.bot.send_message(update.effective_chat.id, text, parse_mode="HTML", reply_markup=build_gukar_keyboard())