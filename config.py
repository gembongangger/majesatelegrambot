import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
NEWS_POLL_INTERVAL_MINUTES = int(os.getenv("NEWS_POLL_INTERVAL_MINUTES", "30"))

API_BASE = "https://man1jember.sch.id/wp-json/wp/v2"
API_FIELDS_POST = "id,title,date,link,excerpt"
API_FIELDS_PAGE = "id,title,link,content"
API_FIELDS_CAT = "id,name,slug"

BERITA_LIMIT = 5
CACHE_TTL_SECONDS = 300

PAGES = {
    "ppdb_bic": "program-unggulan-dan-bic",
    "pengumuman_bic": "pengumuman-bic",
    "pengumuman_reguler": "pengumuman-reguler",
    "sejarah": "sejarah",
    "visi_misi": "mis",
    "struktur": "struktur",
    "gukar": "gukar",
    "ekstrakurikuler": "eka",
    "prestasi": "prestasi-siswa",
    "regulasi": "regulasi",
}

KONTAK_INFO = (
    "MAN 1 JEMBER\n"
    "JL. Imam Bonjol No. 50, Jember\n\n"
    "Telepon: 0331-485109\n"
    "Fax: 0331-484651\n"
    "Email: man1jember@yahoo.co.id\n\n"
    "Media Sosial:\n"
    "• YouTube: @MAN1Jember\n"
    "• Instagram: @man1jember_official\n"
    "• Twitter/X: @man1jember_ofc\n"
    "• TikTok: @man1jember_official"
)

FASILITAS_INFO = (
    "Fasilitas Online MAN 1 Jember:\n\n"
    "• LMS: https://lms.man1jember.sch.id\n"
    "• RDM: https://rdm.man1jember.sch.id\n"
    "• Rumah Belajar: https://belajar.kemdikbud.go.id\n"
    "• Perpustakaan Digital: https://perpus.man1jember.sch.id\n"
    "• MOSAIC: https://mosaic.man1jember.sch.id\n"
    "• PTSP: https://ptsp.man1jember.sch.id\n"
    "• Ma'had (Asrama): tersedia\n"
    "• Program: MAPK - BIC - REGULER"
)