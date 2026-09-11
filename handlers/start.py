from telegram import Update
from telegram.ext import ContextTypes

from utils.menu import build_menu

HELP_TEXT = (
    "🤖 <b>BOT INFO MAN 1 JEMBER</b>\n"
    "<i>Madrasah Aliyah Negeri 1 Jember - MAPK - BIC - REGULER</i>\n\n"
    "Perintah yang tersedia:\n"
    "• /start - Menu utama\n"
    "• /berita - Berita terbaru\n"
    "• /ppdb - Info PPDB/PMBM\n"
    "• /profil - Profil madrasah\n"
    "• /prestasi - Prestasi siswa\n"
    "• /fasilitas - Fasilitas\n"
    "• /kontak - Kontak & alamat\n"
    "• /subscribe - Aktifkan notifikasi berita baru\n"
    "• /unsubscribe - Nonaktifkan notifikasi\n"
    "• /voucher - Buat voucher WiFi hotspot (khusus admin)\n"
    "• /id - Lihat ID Telegram Anda (untuk ditambahkan sebagai admin)\n"
    "• /help - Bantuan ini\n\n"
    "Silakan pilih menu di bawah ini 👇"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    first = user.first_name or "Saudara/i"
    await update.message.reply_text(
        f"Assalamu'alaikum, <b>{first}</b>! 👋\n"
        "Selamat datang di <b>BOT INFO MAN 1 JEMBER</b>.\n"
        "Di sini Anda bisa mendapatkan informasi seputar madrasah: berita, PPDB, profil, prestasi, fasilitas, dan kontak.\n\n"
        "Pilih salah satu menu di bawah ini:",
        reply_markup=build_menu(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, reply_markup=build_menu())