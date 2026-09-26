"""Teks cerita yang bergantung pada keadaan: catatan di fragmen, ending, kematian, dan label layar judul.

Teksnya sendiri ada di text_id.py dan text_en.py, sesuai bahasa yang dipilih (lang.py).
"""

from . import lang

NOTE_COUNT = 15


def notes_list():
    return lang.data("notes_list")


def ending_lines():
    return lang.data("ending_lines")


def death_words():
    return lang.data("death_words")


def credits():
    return lang.data("credits")


def controls():
    return lang.data("controls")


def note_text(index, attempt, own_note=""):
    """Teks catatan ke-index (0..14) untuk percobaan ke-attempt.

    own_note: catatan yang ditulis pemain sendiri di ending. Kalau ada, ia menjadi catatan pertama.
    """
    if index == 0 and own_note:
        return own_note
    if index == 5:
        if attempt <= 1:
            return lang.t("note_first_attempt")
        return lang.t("note_attempt", n=attempt)
    if index == 11 and attempt >= 3:
        return lang.t("note_again")
    if 0 <= index < NOTE_COUNT:
        return notes_list()[index]
    return "..."


def retry_text(count):
    """Tulisan untuk pengulangan lantai ke-count (mulai dari 1) di lantai yang sama."""
    words, late = lang.data("retry_words"), lang.data("retry_words_late")
    if count <= len(words):
        return words[max(1, count) - 1]
    return late[(count - len(words) - 1) % len(late)]


def start_label(save):
    if save.ending > 0:
        return lang.t("start_ended")
    if save.kematian > 0:
        return lang.t("start_died")
    return lang.t("start")
