"""Bahasa tampilan: Bahasa Indonesia atau English.

Semua teks yang dilihat pemain ada di text_id.py dan text_en.py. Modul lain memakai t() untuk
teks tunggal dan data() untuk daftar atau tabel (catatan, kontrol, kredit, dan sebagainya).
"""

import locale
import os
import sys

from . import text_en, text_id

TEXTS = {"id": text_id.TEXT, "en": text_en.TEXT}
NAMES = {"id": "Bahasa Indonesia", "en": "English"}
CODES = tuple(TEXTS)  # urutan saat berganti bahasa di Pengaturan

current = "id"


def set_lang(code):
    global current
    if code in TEXTS:
        current = code


def t(key, **values):
    text = TEXTS[current][key]
    return text.format(**values) if values else text


def data(key):
    return TEXTS[current][key]


def _is_indonesian(name):
    name = name.lower()
    return name == "id" or name.startswith(("id_", "id-", "indonesian"))


def detect():
    """Bahasa sistem: Indonesia kalau Windows (atau OS lain) memakai bahasa Indonesia, selain itu English."""
    if sys.platform == "win32":
        try:
            import ctypes

            primary = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF
            return "id" if primary == 0x21 else "en"  # 0x21 = LANG_INDONESIAN
        except (AttributeError, OSError):
            pass
    names = [os.environ.get(k, "") for k in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")]
    try:
        names.append(locale.getlocale()[0] or "")
    except ValueError:
        pass
    return "id" if any(_is_indonesian(n) for n in names if n) else "en"
