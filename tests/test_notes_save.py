from gema import notes
from gema.save import SaveData


def test_all_notes_exist_and_are_short():
    for i in range(15):
        text = notes.note_text(i, attempt=1)
        assert text and len(text.split()) <= 16


def test_dynamic_notes():
    assert "pertama" in notes.note_text(5, attempt=1)
    assert "ke-7" in notes.note_text(5, attempt=7)
    assert notes.note_text(11, attempt=2) == notes.NOTES[11]
    assert "Sudah berapa kali" in notes.note_text(11, attempt=3)


def test_ending_closes_the_loop():
    first = notes.note_text(0, attempt=1)
    assert first.startswith(notes.ENDING_LINES[1].rstrip("."))


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


def test_corrupt_save_is_ignored(tmp_path):
    path = tmp_path / "save.json"
    for junk in ["{not json", "[]", '{"percobaan": "banyak", "kematian": -3}', ""]:
        path.write_text(junk)
        data = SaveData.load(path)
        assert data.percobaan == 0 and data.kematian == 0
