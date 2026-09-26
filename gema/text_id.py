"""Semua teks yang dilihat pemain, dalam Bahasa Indonesia. Kunci-kuncinya harus sama dengan text_en.py."""

TEXT = {
    # --- layar judul & menu ---------------------------------------------
    "start": "Mulai",
    "start_died": "Kamu kembali.",
    "start_ended": "Kamu kembali. Lagi.",
    "menu_dev": "Mode dev",
    "menu_achievements": "Pencapaian",
    "menu_settings": "Pengaturan",
    "menu_quit": "Keluar",
    "earphones": "Gunakan earphone.",
    "back": "Kembali",
    "back_hint": "Esc: kembali",

    # --- pilih kesulitan -------------------------------------------------
    "how_dark": "Seberapa gelap?",
    "deepest": "   (terdalam: Lantai {n})",
    "finished_mark": "   (tamat)",
    "difficulty": {
        "redup": ("Redup", "3 nyawa, lantai diulang kalau habis. Tidak segelap itu, mereka lebih lambat."),
        "gelap": ("Gelap", "2 nyawa. Seperti yang dimaksudkan."),
        "pekat": ("Pekat", "1 nyawa. Jangan berharap banyak."),
    },

    # --- pengaturan ------------------------------------------------------
    "settings_title": "Pengaturan",
    "setting_language": "Bahasa",

    # --- bermain ---------------------------------------------------------
    "floor": "Lantai {n}",
    "floor_final": "Lantai",
    "attempt_over": "Percobaan ke-{n} berakhir.",
    "new_achievement": "Pencapaian baru: {name}",
    "pause": "Jeda",
    "resume": "Lanjut",
    "notes": "Catatan",
    "to_title": "Kembali ke judul",
    "notes_none": "Belum ada.",
    "tool_stones": "kerikil",
    "tool_walls": "dinding",
    "controls": [
        ("WASD", "bergerak"),
        ("Shift", "lari (berisik)"),
        ("Mouse", "arahkan senter"),
        ("Tahan klik kiri", "senter"),
        ("Klik kanan / Spasi", "sonar"),
        ("Q", "lempar kerikil"),
        ("Tahan E", "hancurkan dinding (berisik)"),
        ("Esc", "jeda"),
        ("F11", "layar penuh"),
    ],

    # --- cerita ----------------------------------------------------------
    "notes_list": [
        # Lantai 1
        "Kalau kamu baca ini, berarti alatnya masih nyala. Bagus.",
        "Sonar memperlihatkan jalan. Tapi mereka juga dengar. Pakai seperlunya.",
        "Cahaya membuat mereka diam. Bukan pergi. Diam.",
        # Lantai 2
        "Mereka tidak bisa melihat. Mereka mendengar. Jangan lari kalau tidak perlu.",
        "Ada yang berdiri di ujung cahaya. Selama kamu lihat, dia tidak bergerak.",
        None,  # dinamis: note_first_attempt / note_attempt
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
    ],
    "note_first_attempt": "Ini percobaan pertama. Setidaknya itu yang tertulis.",
    "note_attempt": "Ini percobaan ke-{n}. Kali ini jangan lari.",
    "note_again": "Sudah berapa kali kamu membaca kalimat ini?",
    "ending_lines": [
        "Catatan pertama.",
        "Kalau kamu baca ini, berarti alatnya masih nyala.",
        "Bagus.",
    ],
    "death_words": ["Belum.", "Lagi.", "Bangun."],
    # Redup: saat lantai diulang karena nyawa habis. Makin sering di lantai yang sama, makin menusuk.
    "retry_words": [
        "Kamu bangun lagi.",
        "Lagi.",
        "Kamu lelah?",
        "Tempat ini mulai hafal langkahmu.",
        "Mereka sudah tidak perlu mencarimu lagi.",
        "Senternya masih nyala. Kamu?",
    ],
    "retry_words_late": [
        "Sudah berapa kali?",
        "Istirahat saja. Tidak ada yang menunggu.",
        "Kamu masih di sini.",
    ],
    # (teks, ukuran font, terang?)
    "credits": [
        ("GEMA", 30, True),
        ("", 10, False),
        ("oleh v.obscura", 18, True),
        ("", 10, False),
        ("dibuat dengan pygame-ce dan numpy", 15, False),
        ("tanpa satu pun file gambar atau suara", 15, False),
    ],

    # --- ending ----------------------------------------------------------
    "note_prompt": "Tulis sesuatu untuk yang berikutnya.",
    "note_keys": "Enter: simpan     Esc: lewati",
    "result_title": "Keluar dari {name}",
    "result_line1": "Waktu {time}    Mati {deaths} kali{retried}    Catatan {notes}/{total}",
    "result_retried": "    Ulang lantai {n} kali",
    "result_line2": "Sonar {pings} kali    Kerikil {stones}    Dinding {walls}    Pengamat diusir {banished}",
    "assisted": "Percobaan ini dibantu (mode dev, atau tidak mulai dari Lantai 1). Tidak ada pencapaian.",
    "new_achievements": "Pencapaian baru",
    "no_new": "Tidak ada pencapaian baru kali ini.",
    "achievements_total": "Pencapaian: {got} dari {total}",
    "note_saved": "Catatanmu tersimpan.",
    "continue_hint": "Enter: lanjut",
    "next_attempt": "Percobaan ke-{n}.",

    # --- pencapaian ------------------------------------------------------
    "achievements_title": "Pencapaian",
    "achievements_count": "{got} dari {total}",
    "achievements": {
        "tamat_redup": ("Keluar dari Redup", "Tamat di Redup."),
        "tamat_gelap": ("Keluar dari Gelap", "Tamat di Gelap."),
        "tamat_pekat": ("Keluar dari Pekat", "Tamat di Pekat."),
        "tak_tersentuh": ("Tak Tersentuh", "Tamat tanpa mati sekali pun."),
        "tak_lari": ("Tidak Pernah Lari", "Tamat tanpa pernah lari."),
        "tanpa_cahaya": ("Tanpa Cahaya", "Tamat dengan senter menyala kurang dari satu menit."),
        "tangan_kosong": ("Tangan Kosong", "Tamat tanpa kerikil dan tanpa menghancurkan dinding."),
        "tidak_menoleh": ("Tidak Menoleh", "Tamat dalam waktu kurang dari 12 menit."),
        "pengalih": ("Pengalih", "Alihkan Pendengar yang sedang memburumu dengan kerikil."),
        "lagi": ("Lagi.", "Tamat dua kali."),
        "jalan_pintas": ("Jalan Pintas", "Hancurkan 10 dinding."),
        "menatap_balik": ("Menatap Balik", "Usir Pengamat 10 kali."),
        "seribu_gema": ("Seribu Gema", "Pakai sonar 1000 kali."),
        "kembali_lagi": ("Kembali Lagi", "Mulai 10 percobaan."),
    },

    # --- mode dev --------------------------------------------------------
    "dev_title": "Mode dev",
    "dev_options": {
        "god": ("Kebal (tidak bisa mati)", "kebal"),
        "no_cooldown": ("Sonar tanpa jeda", "sonar tanpa jeda"),
        "infinite_light": ("Senter tanpa batas", "senter tanpa batas"),
        "infinite_tools": ("Kerikil & dinding tanpa batas", "alat tanpa batas"),
    },
    "dev_keys": [
        "F5: ambil semua fragmen lantai ini",
        "F6: lompat ke pintu keluar",
        "F3: overlay debug",
    ],
}
