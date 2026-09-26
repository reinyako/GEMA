"""Pencapaian: dicatat di data simpanan, dilihat dari layar judul, diumumkan di layar hasil."""

from dataclasses import dataclass

from . import lang

FAST_TIME = 12 * 60.0      # "Tidak Menoleh": tamat lebih cepat dari ini (detik)
DARK_LIGHT_TIME = 60.0     # "Tanpa Cahaya": senter menyala kurang dari ini (detik)


@dataclass(frozen=True)
class Achievement:
    key: str
    counter: str = ""   # untuk pencapaian yang dikumpulkan: nama angka di data simpanan
    target: int = 0

    @property
    def name(self):
        return lang.data("achievements")[self.key][0]

    @property
    def desc(self):
        return lang.data("achievements")[self.key][1]


ALL = (
    Achievement("tamat_redup"),
    Achievement("tamat_gelap"),
    Achievement("tamat_pekat"),
    Achievement("tak_tersentuh"),
    Achievement("tak_lari"),
    Achievement("tanpa_cahaya"),
    Achievement("tangan_kosong"),
    Achievement("tidak_menoleh"),
    Achievement("pengalih"),
    Achievement("lagi", "ending", 2),
    Achievement("jalan_pintas", "total_dinding", 10),
    Achievement("menatap_balik", "pengamat_diusir", 10),
    Achievement("seribu_gema", "total_ping", 1000),
    Achievement("kembali_lagi", "percobaan", 10),
)
BY_KEY = {a.key: a for a in ALL}


def progress(save, achievement):
    """(sekarang, target) untuk pencapaian yang dikumpulkan, atau None."""
    if not achievement.counter:
        return None
    return min(getattr(save, achievement.counter), achievement.target), achievement.target


def record(save, run, finished):
    """Mencatat satu percobaan ke data simpanan. Mengembalikan pencapaian yang baru terbuka.

    Percobaan yang dibantu (mode dev, atau mulai dari lantai selain 1) tidak dicatat.
    """
    if run.recorded or run.assisted:
        return []
    run.recorded = True
    save.total_ping += run.pings
    save.total_dinding += run.walls_broken
    save.pengamat_diusir += run.banished
    key = run.difficulty.key
    if finished:
        save.tamat[key] = save.tamat.get(key, 0) + 1

    got = {a.key for a in ALL if a.counter and getattr(save, a.counter) >= a.target}
    if run.distractions > 0:
        got.add("pengalih")
    if finished:
        got.add(f"tamat_{key}")
        if run.deaths == 0:
            got.add("tak_tersentuh")
        if run.run_time == 0:
            got.add("tak_lari")
        if run.light_time < DARK_LIGHT_TIME:
            got.add("tanpa_cahaya")
        if run.stones_thrown == 0 and run.walls_broken == 0:
            got.add("tangan_kosong")
        if run.play_time < FAST_TIME:
            got.add("tidak_menoleh")

    new = [a for a in ALL if a.key in got and a.key not in save.pencapaian]
    save.pencapaian.extend(a.key for a in new)
    save.write()
    return new
