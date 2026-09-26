import string

from gema import achievements, lang, notes
from gema import config as C
from gema.run import Run
from gema.save import NOTE_MAX, SaveData


def test_all_notes_exist_and_are_short():
    for i in range(15):
        text = notes.note_text(i, attempt=1)
        assert text and len(text.split()) <= 16


def test_dynamic_notes():
    assert "pertama" in notes.note_text(5, attempt=1)
    assert "ke-7" in notes.note_text(5, attempt=7)
    assert notes.note_text(11, attempt=2) == notes.notes_list()[11]
    assert "Sudah berapa kali" in notes.note_text(11, attempt=3)


def test_players_own_note_becomes_the_first_note():
    assert notes.note_text(0, attempt=4, own_note="Jangan lari di Lantai 2.") == "Jangan lari di Lantai 2."
    assert notes.note_text(1, attempt=4, own_note="Jangan lari di Lantai 2.") == notes.notes_list()[1]
    assert notes.note_text(0, attempt=4, own_note="") == notes.notes_list()[0]


def test_retry_words_grow_sharper_on_the_same_floor():
    assert notes.retry_text(1) == "Kamu bangun lagi."
    assert notes.retry_text(3) == "Kamu lelah?"
    late = {notes.retry_text(n) for n in range(7, 20)}
    assert late == set(lang.data("retry_words_late"))
    for code in lang.CODES:
        words = lang.TEXTS[code]["retry_words"] + lang.TEXTS[code]["retry_words_late"]
        assert all(len(t.split()) <= 8 for t in words)


def test_ending_closes_the_loop():
    first = notes.note_text(0, attempt=1)
    assert first.startswith(notes.ending_lines()[1].rstrip("."))


def _shape(value):
    """Bentuk sebuah teks: kunci, panjang daftar, dan {placeholder} yang dipakai."""
    if isinstance(value, dict):
        return {k: _shape(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_shape(v) for v in value]
    if isinstance(value, str):
        return sorted(name for _, name, _, _ in string.Formatter().parse(value) if name)
    return type(value).__name__


def test_both_languages_have_the_same_texts():
    assert _shape(lang.TEXTS["id"]) == _shape(lang.TEXTS["en"])


def test_english_notes_are_short_too():
    lang.set_lang("en")
    for i in range(notes.NOTE_COUNT):
        for attempt in (1, 3):
            text = notes.note_text(i, attempt=attempt)
            assert text and len(text.split()) <= 16
    assert notes.note_text(0, attempt=1).startswith(notes.ending_lines()[1].rstrip("."))
    assert notes.start_label(SaveData()) == "Begin"


def test_language_is_remembered_and_new_players_follow_the_system(tmp_path, monkeypatch):
    path = tmp_path / "save.json"
    monkeypatch.setattr(lang, "detect", lambda: "en")
    assert SaveData.load(path).bahasa == "en"          # pemain baru: ikut bahasa sistem
    path.write_text('{"percobaan": 3}')
    assert SaveData.load(path).bahasa == "id"          # pemain lama: tetap Bahasa Indonesia
    save = SaveData.load(path)
    save.bahasa = "en"
    save.write()
    assert SaveData.load(path).bahasa == "en"


def test_start_label_changes(tmp_path):
    save = SaveData(path=tmp_path / "s.json")
    assert notes.start_label(save) == "Mulai"
    save.kematian = 1
    assert notes.start_label(save) == "Kamu kembali."
    save.ending = 1
    assert notes.start_label(save) == "Kamu kembali. Lagi."


def test_save_roundtrip(tmp_path):
    path = tmp_path / "deep" / "save.json"
    save = SaveData.load(path)
    save.percobaan, save.kematian, save.ending = 3, 5, 1
    save.record_floor("gelap", 4)
    save.write()
    again = SaveData.load(path)
    assert (again.percobaan, again.kematian, again.ending) == (3, 5, 1)
    assert again.lantai_terbaik["gelap"] == 4


def test_save_roundtrip_new_fields(tmp_path):
    path = tmp_path / "save.json"
    save = SaveData.load(path)
    save.tamat["pekat"] = 2
    save.total_ping, save.total_dinding, save.pengamat_diusir = 120, 4, 7
    save.pencapaian = ["tak_lari", "pengalih"]
    save.catatan_pemain = "x" * (NOTE_MAX + 50)
    save.write()
    again = SaveData.load(path)
    assert again.tamat["pekat"] == 2
    assert (again.total_ping, again.total_dinding, again.pengamat_diusir) == (120, 4, 7)
    assert again.pencapaian == ["tak_lari", "pengalih"]
    assert len(again.catatan_pemain) == NOTE_MAX


def test_corrupt_save_is_ignored(tmp_path):
    path = tmp_path / "save.json"
    for junk in ["{not json", "[]", '{"percobaan": "banyak", "kematian": -3}', ""]:
        path.write_text(junk)
        data = SaveData.load(path)
        assert data.percobaan == 0 and data.kematian == 0
    path.write_text('{"pencapaian": "semua", "catatan_pemain": 5, "tamat": [1], "total_ping": -1}')
    data = SaveData.load(path)
    assert data.pencapaian == [] and data.catatan_pemain == ""
    assert data.tamat == {"redup": 0, "gelap": 0, "pekat": 0} and data.total_ping == 0


def _finished_run(**stats):
    run = Run(C.GELAP, seed=1, attempt=1)
    run.play_time, run.light_time = 1500.0, 300.0
    run.stones_thrown, run.walls_broken, run.run_time, run.deaths = 1, 1, 30.0, 1
    for key, value in stats.items():
        setattr(run, key, value)
    return run


def test_achievements_for_a_finished_run(tmp_path):
    save = SaveData(path=tmp_path / "s.json")
    save.percobaan = save.ending = 1
    new = achievements.record(save, _finished_run(deaths=0, run_time=0.0, distractions=2), finished=True)
    assert [a.key for a in new] == ["tamat_gelap", "tak_tersentuh", "tak_lari", "pengalih"]
    assert save.tamat["gelap"] == 1


def test_run_is_recorded_only_once_and_never_when_assisted(tmp_path):
    save = SaveData(path=tmp_path / "s.json")
    run = _finished_run(pings=10)
    achievements.record(save, run, finished=False)
    assert achievements.record(save, run, finished=True) == []
    assert save.total_ping == 10 and save.tamat["gelap"] == 0
    helped = _finished_run(pings=10, assisted=True)
    assert achievements.record(save, helped, finished=True) == []
    assert save.total_ping == 10
    assert Run(C.GELAP, seed=1, attempt=1, floor=3).assisted


def test_collected_achievements_count_across_runs(tmp_path):
    save = SaveData(path=tmp_path / "s.json")
    for _ in range(4):
        new = achievements.record(save, _finished_run(pings=300, banished=3), finished=False)
    assert "seribu_gema" in [a.key for a in new]
    assert "menatap_balik" in save.pencapaian
    assert achievements.progress(save, achievements.BY_KEY["jalan_pintas"]) == (4, 10)  # 1 dinding per percobaan
