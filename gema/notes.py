"""Semua teks cerita: catatan di fragmen, ending, teks kematian, dan label layar judul."""

NOTES = [
    # Lantai 1
    "Kalau kamu baca ini, berarti alatnya masih nyala. Bagus.",
    "Sonar memperlihatkan jalan. Tapi mereka juga dengar. Pakai seperlunya.",
    "Cahaya membuat mereka diam. Bukan pergi. Diam.",
    # Lantai 2
    "Mereka tidak bisa melihat. Mereka mendengar. Jangan lari kalau tidak perlu.",
    "Ada yang berdiri di ujung cahaya. Selama kamu lihat, dia tidak bergerak.",
    None,  # dinamis, lihat note_text()
    # Lantai 3
    "Jangan percaya ingatanmu soal jalan. Dindingnya pindah waktu tidak dilihat.",
    "Yang berdiri di pinggir cahaya itu tidak berbahaya.",
    "Jangan percaya catatan yang bilang dia tidak berbahaya.",
    # Lantai 4
    "Kalau ada bunyi sonar padahal kamu tidak menekannya, itu bukan kamu.",
    "Tidak semua yang muncul di sonar itu nyata. Tidak semua yang nyata muncul di sonar.",
    "Tulisan ini mirip tulisanku. Tapi aku tidak ingat pernah menulisnya.",
    # Lantai 5
    "Sudah sadar belum? Bentuknya sama persis kayak kamu.",
    "Mereka yang di sini semuanya pernah memegang senter ini.",
    "Pintu terakhir tidak mengarah keluar. Aku tetap akan membukanya. Kamu juga.",
]

ENDING_LINES = [
    "Catatan pertama.",
    "Kalau kamu baca ini, berarti alatnya masih nyala.",
    "Bagus.",
]

DEATH_WORDS = ["Belum.", "Lagi.", "Bangun."]

# (teks, ukuran font, terang?)
CREDITS = [
    ("GEMA", 30, True),
    ("", 10, False),
    ("oleh v.obscura", 18, True),
    ("", 10, False),
    ("dibuat dengan pygame-ce dan numpy", 15, False),
    ("tanpa satu pun file gambar atau suara", 15, False),
]

CONTROLS = [
    ("WASD", "bergerak"),
    ("Shift", "lari (berisik)"),
    ("Mouse", "arahkan senter"),
    ("Tahan klik kiri", "senter"),
    ("Klik kanan / Spasi", "sonar"),
    ("Esc", "jeda"),
    ("F11", "layar penuh"),
]


def note_text(index, attempt):
    """Teks catatan ke-index (0..14) untuk percobaan ke-attempt."""
    if index == 5:
        if attempt <= 1:
            return "Ini percobaan pertama. Setidaknya itu yang tertulis."
        return f"Ini percobaan ke-{attempt}. Kali ini jangan lari."
    if index == 11 and attempt >= 3:
        return "Sudah berapa kali kamu membaca kalimat ini?"
    if 0 <= index < len(NOTES):
        return NOTES[index]
    return "..."


def start_label(save):
    if save.ending > 0:
        return "Kamu kembali. Lagi."
    if save.kematian > 0:
        return "Kamu kembali."
    return "Mulai"
