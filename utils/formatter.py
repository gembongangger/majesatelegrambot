from datetime import datetime


def format_date(iso_date: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso_date


def truncate(text: str, limit: int = 220) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def format_berita_list(posts: list[dict], title: str = "📰 BERITA TERBARU") -> str:
    if not posts:
        return "❌ Tidak ada berita ditemukan."
    lines = [f"<b>{title}</b>", ""]
    for i, post in enumerate(posts, 1):
        plain_title = post["title"]
        date = format_date(post["date"])
        lines.append(f"{i}. <b>{plain_title}</b>")
        lines.append(f"   📅 {date}")
        lines.append(f"   🔗 {post['link']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_plain_posts(posts: list[dict], title: str) -> str:
    if not posts:
        return f"❌ Tidak ada data {title.lower()} ditemukan."
    lines = [f"<b>{title}</b>", ""]
    for i, post in enumerate(posts, 1):
        lines.append(f"{i}. {post['title']}")
        if post.get("date"):
            lines.append(f"   📅 {format_date(post['date'])}")
        lines.append(f"   🔗 {post['link']}")
        lines.append("")
    return "\n".join(lines).rstrip()


KEYWORDS: dict[str, list[str]] = {
    "berita": ["berita", "news", "kabar", "terbaru"],
    "ppdb": ["ppdb", "pmbm", "pendaftaran", "murid baru", "murid-baru", "bic", "reguler", "daftar"],
    "profil": ["profil", "visi", "misi", "sejarah", "struktur", "guru", "karyawan", "ekstrakurikuler"],
    "prestasi": ["prestasi", "juara", "lomba", "medali", "piala"],
    "fasilitas": ["fasilitas", "lms", "perpustakaan", "rdm", "rumah belajar", "mosaic"],
    "kontak": ["kontak", "alamat", "telepon", "email", "hubungi", "nomor", "lokasi"],
}

INTENT_LABELS = {
    "berita": "📰 Berita",
    "ppdb": "🌱 PPDB/PMBM",
    "profil": "🏫 Profil",
    "prestasi": "🏆 Prestasi",
    "fasilitas": "💻 Fasilitas",
    "kontak": "📞 Kontak",
}


def detect_intent(text: str) -> str | None:
    lower = text.lower()
    for intent, words in KEYWORDS.items():
        for word in words:
            if word in lower:
                return intent
    return None