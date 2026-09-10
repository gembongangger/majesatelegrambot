import logging

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from config import NEWS_POLL_INTERVAL_MINUTES, TELEGRAM_BOT_TOKEN
from handlers.start import help_command, start_command
from handlers.berita import berita_command
from handlers.ppdb import ppdb_command
from handlers.profil import profil_command
from handlers.prestasi import prestasi_command
from handlers.fasilitas import fasilitas_command
from handlers.kontak import kontak_command
from handlers.subscribe import subscribe_command, unsubscribe_command
from handlers.voucher import voucher_command
from handlers.callback import handle_callback
from handlers.message import fallback_handler
from scheduler.news_checker import check_new_news

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_bot_token_here":
        raise SystemExit("⚠️ TELEGRAM_BOT_TOKEN belum diisi. Edit file .env terlebih dahulu.")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(CommandHandler("voucher", voucher_command))
    app.add_handler(CommandHandler("berita", berita_command))
    app.add_handler(CommandHandler("ppdb", ppdb_command))
    app.add_handler(CommandHandler("profil", profil_command))
    app.add_handler(CommandHandler("prestasi", prestasi_command))
    app.add_handler(CommandHandler("fasilitas", fasilitas_command))
    app.add_handler(CommandHandler("kontak", kontak_command))

    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler))

    job_queue = app.job_queue
    if job_queue is not None:
        job_queue.run_repeating(check_new_news, interval=NEWS_POLL_INTERVAL_MINUTES * 60, first=60)

    logging.info("Bot MAN 1 Jember berjalan... (tekan Ctrl+C untuk berhenti)")
    app.run_polling()


if __name__ == "__main__":
    main()