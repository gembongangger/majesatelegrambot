from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_menu(current: str | None = None) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📰 Berita", callback_data="menu:berita"),
            InlineKeyboardButton("🌱 PPDB/PMBM", callback_data="menu:ppdb"),
        ],
        [
            InlineKeyboardButton("🏫 Profil", callback_data="menu:profil"),
            InlineKeyboardButton("🏆 Prestasi", callback_data="menu:prestasi"),
        ],
        [
            InlineKeyboardButton("💻 Fasilitas", callback_data="menu:fasilitas"),
            InlineKeyboardButton("📞 Kontak", callback_data="menu:kontak"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_berita_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="menu:menu"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_ppdb_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("BIC", callback_data="ppdb:bic"),
            InlineKeyboardButton("Reguler", callback_data="ppdb:reguler"),
        ],
        [
            InlineKeyboardButton("Pengumuman BIC", callback_data="ppdb:peng_bic"),
            InlineKeyboardButton("Pengumuman Reguler", callback_data="ppdb:peng_reg"),
        ],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu:menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_profil_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Visi & Misi", callback_data="profil:visi_misi"),
            InlineKeyboardButton("Sejarah", callback_data="profil:sejarah"),
        ],
        [
            InlineKeyboardButton("Struktur Organisasi", callback_data="profil:struktur"),
            InlineKeyboardButton("Guru & Karyawan", callback_data="profil:gukar"),
        ],
        [
            InlineKeyboardButton("Ekstrakurikuler", callback_data="profil:eka"),
        ],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu:menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_gukar_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🧑‍🏫 Guru MIPA", callback_data="gukar:mipa"),
            InlineKeyboardButton("🧑‍🏫 Guru IPS", callback_data="gukar:ips"),
        ],
        [
            InlineKeyboardButton("🧑‍🏫 Guru Bahasa", callback_data="gukar:bahasa"),
            InlineKeyboardButton("🧑‍🏫 Guru Agama", callback_data="gukar:agama"),
        ],
        [
            InlineKeyboardButton("🧑‍🏫 Guru Keterampilan", callback_data="gukar:keterampilan"),
            InlineKeyboardButton("🧑‍🏫 Guru Olah Raga", callback_data="gukar:olahraga"),
        ],
        [
            InlineKeyboardButton("🧑‍🏫 Guru Matematika", callback_data="gukar:matematika"),
            InlineKeyboardButton("🧑‍🏫 Guru BK", callback_data="gukar:bk"),
        ],
        [
            InlineKeyboardButton("🧑‍💼 Karyawan", callback_data="gukar:karyawan"),
        ],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu:profil")],
    ]
    return InlineKeyboardMarkup(keyboard)