# GEMA — Rencana Pengembangan

> Versi 1.0 · 24 September 2026 · Pasangan dari [`GDD.md`](GDD.md)

## 1. Target

| Milestone | Isi | Target |
|---|---|---|
| **M0** Fondasi | Kerangka proyek, loop game, test harness | Hari ini |
| **M1** Inti | Game lengkap yang bisa dimainkan dari Lantai 1 sampai 5 | Hari ini / besok |
| **M2** Lapisan horor | Stres, gema palsu, Pengamat, labirin bergeser, ping peniru | Besok |
| **M3** Cerita & polish | Catatan, simpanan, ending, audio lengkap, README | Besok |
| **M4** Tuning | Penyetelan angka dari hasil playtest kamu | Setelah playtest |

Setiap milestone langsung di-push begitu lulus kriteria selesainya. Jadi kalau waktunya mepet, versi yang bisa dimainkan sudah ada sejak M1.

---

## 2. Teknologi

| | Pilihan | Alasan |
|---|---|---|
| Bahasa | Python 3.10+ | |
| Engine | **pygame-ce** 2.5 | Fork pygame yang aktif dikembangkan dan punya wheel untuk Python versi baru. API-nya sama dengan pygame (`import pygame`). |
| Audio | **numpy** | Semua suara dibuat dari gelombang, tanpa file aset |
| Test | pytest | Unit test + bot headless |

> Kalau di komputermu sudah terpasang `pygame` biasa, uninstall dulu (`pip uninstall pygame`) sebelum memasang `pygame-ce`, karena keduanya memakai nama modul yang sama.

### Hasil uji kelayakan (sudah dicoba di server)

| Uji | Hasil | Batas |
|---|---|---|
| Satu frame pencahayaan: kerucut senter 65 sinar + gradasi + blend penuh layar 960×540 | **3,4 ms** | 16,7 ms (60 FPS) |
| Satu ping sonar (360 sinar DDA) | **0,65 ms** | Sekali per ping |
| Membuat suara dengan numpy dan memutarnya di mode tanpa layar/audio | Berjalan | – |

Kesimpulannya, pendekatan pencahayaan dan sonar yang direncanakan aman dari sisi performa.

---

## 3. Arsitektur

### 3.1 Struktur folder

```
simple_pygame/
├── main.py                  # titik masuk: python main.py [--seed N --floor N --difficulty X --dev --mute]
├── requirements.txt         # pygame-ce, numpy
├── README.md
├── docs/
│   ├── GDD.md
│   └── PLAN.md
├── gema/
│   ├── config.py            # SEMUA angka tuning + preset kesulitan (satu-satunya tempat angka)
│   ├── app.py               # jendela, loop 60 FPS, pergantian scene
│   ├── save.py              # simpanan: percobaan, kematian, ending, lantai terbaik
│   ├── notes.py             # teks catatan + varian dinamis
│   ├── world/
│   │   ├── maze.py          # generator labirin, BFS, braiding, pergeseran dinding
│   │   ├── raycast.py       # DDA raycasting + line-of-sight
│   │   ├── noise.py         # bus kejadian suara
│   │   ├── player.py
│   │   ├── listener.py      # Pendengar: state machine + pathfinding
│   │   ├── watcher.py       # Pengamat
│   │   ├── items.py         # fragmen, baterai, pintu keluar
│   │   ├── sonar.py         # gelombang, titik gema, jejak ingatan, tanda objek
│   │   ├── flashlight.py    # kerucut cahaya, baterai, kedipan, uji "terkena cahaya"
│   │   ├── stress.py        # meter stres tersembunyi
│   │   ├── director.py      # penjadwal kejadian horor + pacing
│   │   └── floor.py         # merakit satu lantai dari seed + nomor lantai + kesulitan
│   ├── render/
│   │   ├── lighting.py      # peta cahaya (kerucut, aura, celah pintu)
│   │   ├── draw.py          # dunia, entitas, gema
│   │   ├── effects.py       # vignette, grain, goyangan kamera, fade
│   │   └── text.py          # font, efek mesin ketik
│   ├── audio/
│   │   ├── synth.py         # pembuatan semua suara dengan numpy
│   │   └── manager.py       # channel, panning stereo, loop, fallback tanpa suara
│   └── scenes/
│       ├── title.py
│       ├── difficulty.py
│       ├── play.py
│       ├── pause.py
│       ├── interlude.py     # intro lantai, layar mati, akhir percobaan
│       └── ending.py
├── tests/
│   ├── test_maze.py
│   ├── test_raycast.py
│   ├── test_notes_save.py
│   └── test_smoke.py        # bot headless memainkan beberapa lantai
└── tools/
    └── snap.py              # ambil screenshot headless untuk review visual
```

### 3.2 Urutan update per frame (scene `play`)

```
1. Input           → arah gerak, lari, sudut bidik, senter ditahan, sonar ditekan
2. Player          → gerak + tabrakan dinding → kirim suara langkah ke NoiseBus
3. Flashlight      → kurangi baterai, kedipan, hitung poligon kerucut (raycast)
4. Sonar           → ping baru (cek jeda) → kirim suara; gelombang melebar → titik gema & tanda
5. Monsters        → Pendengar (baca NoiseBus, cek beku) dan Pengamat (cek diamati)
6. Items           → ambil fragmen/baterai, cek pintu keluar
7. Stress          → hitung naik/turun dari konteks frame ini
8. Director        → jadwalkan gema palsu, geser dinding, ping peniru, bisikan, bayangan
9. Audio           → volume & panning semua loop posisional, jadwal detak jantung
10. NoiseBus       → dikosongkan
11. Render         → lihat 3.4
```

`dt` diambil dari `clock.tick(60)` dan dibatasi maksimal 0,05 detik, supaya lag sesaat tidak membuat monster "melompat".

### 3.3 Model data inti

- **Maze:** grid petak (`0` = lantai, `1` = dinding) berukuran `(2W+1) × (2H+1)`. Sel ada di koordinat ganjil, dan dinding antar-sel ada di petak "sambungan". Pergeseran labirin cukup membalik nilai petak sambungan, lalu cek keterhubungan dengan BFS.
- **Koordinat:** dunia dalam piksel, petak 32 px. Kamera mengikuti pemain.
- **NoiseBus:** daftar `Noise(pos, radius, source)` untuk frame ini.
- **Config:** `dataclass` untuk konstanta umum ditambah `Difficulty` preset (`REDUP`, `GELAP`, `PEKAT`) dan `FloorRules` per lantai (tabel §8.2 GDD).

### 3.4 Lapisan render

```
1. Layar dikosongkan hitam
2. Potongan "dunia asli" (lantai + dinding, sudah dirender sekali per lantai) + entitas yang terkena cahaya
   × peta cahaya (kerucut senter + aura + celah pintu)          ← BLEND_MULT
3. Jejak ingatan sonar (surface persisten per lantai)            ← additive
4. Titik gema aktif + tanda objek                                ← additive
5. Penanda pemain
6. Efek layar: vignette (ikut stres), grain, goyangan kamera, fade
7. UI teks: catatan, petunjuk, intro lantai
```

- **Jejak ingatan** adalah surface seukuran dunia. Titik yang memudar "dicetak" ke surface ini sekali saja, jadi ribuan titik lama tidak digambar ulang tiap frame.
- **Pemindaian ulang menghapus jejak lama.** Setiap sinar sonar menghapus jejak di sepanjang jalurnya, karena ruang itu sekarang terbukti kosong.
- **Pergeseran labirin** mengubah surface dunia asli di satu petak itu, tapi tidak menyentuh jejak ingatan. Dengan begitu ingatan pemain bisa salah.

### 3.5 Pipeline audio

- `synth.py` membuat semua suara (array int16 stereo) sekali saat start dalam waktu kurang dari 1 detik.
- `manager.py` mengatur channel sebagai berikut:
  - Channel khusus untuk loop: dengung latar A dan B (crossfade saat stres), detak jantung, dengung fragmen, dengung pintu, seretan tiap Pendengar, napas Pengamat.
  - Sisa channel untuk suara sekali putar.
- Panning memakai `Channel.set_volume(kiri, kanan)` dengan rumus *equal-power*. Volume turun mengikuti jarak.
- Kalau `mixer.init()` gagal, semua fungsi audio berjalan tanpa suara dan game tetap jalan.

### 3.6 AI Pendengar

- State machine sesuai tabel §7.1 GDD.
- Pathfinding memakai BFS di grid petak (paling besar ±41×27 petak, jadi murah). Jalur dihitung ulang saat ada target baru atau paling lambat setiap 0,5 detik.
- Pengecekan "terkena cahaya" dilakukan dua langkah: sudut ke pemain harus masuk kerucut, lalu line-of-sight dicek dengan raycast.

---

## 4. Milestone & tugas

### M0 — Fondasi
- [x] Struktur folder, `requirements.txt`, `.gitignore`, `main.py`
- [x] `config.py` dengan konstanta, preset kesulitan, dan aturan per lantai
- [x] `app.py`: jendela 960×540 `SCALED`, loop 60 FPS, pergantian scene, `F11`
- [x] Argumen CLI: `--seed`, `--floor`, `--difficulty`, `--dev`, `--mute`
- [x] Test harness headless (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`) + pytest

**Selesai kalau:** `python main.py` membuka layar judul sementara, dan `pytest` hijau.

### M1 — Inti (bisa dimainkan)
- [x] `maze.py`: recursive backtracker, braiding, ruangan, penempatan semua objek, BFS
- [x] `raycast.py`: cast DDA + line-of-sight
- [x] Player: gerak, tabrakan, lari, bidik, suara langkah
- [x] NoiseBus
- [x] Sonar: gelombang, 360 sinar, titik gema, jejak ingatan, tanda objek (tajam atau buram), jeda
- [x] Senter: kerucut, gradasi, baterai, jangkauan menyusut, kedipan, efek beku
- [x] Pendengar: state machine lengkap, BFS, mematikan saat menyentuh
- [x] Fragmen, baterai, dan pintu keluar (terkunci lalu terbuka, masih versi dasar)
- [x] Alur lantai: intro lantai, pindah lantai, nyawa, muncul lagi, akhir percobaan
- [x] Layar pilih kesulitan + penerapan preset
- [x] Render: komposisi peta cahaya, siluet Pendengar, vignette dasar
- [x] Audio v1: ping, langkah, dengung fragmen (posisional), detak jantung (kedekatan), dengung latar
- [x] Overlay debug `F3`: seluruh peta, state monster, stres, baterai, FPS
- [x] Test: labirin (terhubung, ukuran, penempatan), raycast, pathfinding, smoke bot

**Selesai kalau:** game bisa dimainkan dari judul sampai Lantai 5 selesai atau sampai nyawa habis, bot headless 3 menit per lantai tidak crash, dan screenshot sudah aku review.

### M2 — Lapisan horor
- [x] Meter stres beserta semua aturan naik/turun dan batas bawah
- [x] Efek stres: vignette dinamis, detak jantung, jejak ingatan berkedip, bisikan, crossfade dengung sumbang, goyangan kamera
- [x] Director dengan jarak minimal antar kejadian besar dan jeda setelah momen puncak
- [x] Gema palsu dan gema hilang, termasuk semua aturan keadilan
- [x] Pengamat: muncul di belakang, jarak nyaman, berhenti saat diamati, pergi setelah disorot 2 detik, napas peringatan, bentuk sama seperti pemain
- [x] Labirin bergeser: tanpa pengamatan, keterhubungan terjaga, bunyi gesekan, update dunia asli tanpa mengubah ingatan
- [x] Ping peniru: ping sumbang, lingkaran samar, masuk NoiseBus
- [x] Bayangan palsu di tepi kerucut senter
- [x] Pintu terbuka: hening 6 detik, Pendengar gelisah, dengung pintu, celah cahaya
- [x] Pengenalan elemen per lantai sesuai tabel §8.2 GDD
- [x] Test: keterhubungan setelah 1000 kali geser acak, batasan gema palsu, transisi state Pengamat

**Selesai kalau:** setiap elemen muncul di lantai yang benar, bot test hijau, dan screenshot di stres 0, 50, dan 90 sudah aku review.

### M3 — Cerita & polish
- [x] `notes.py`: 15 catatan, varian dinamis, pengisian `{n}`
- [x] Tampilan catatan dengan efek mesin ketik, plus daftar catatan di menu jeda
- [x] `save.py`: tahan terhadap file rusak
- [x] Layar judul: tombol dinamis, judul bergaya titik sonar, saran memakai earphone
- [x] Urutan kematian (hening, bunyi tumpul, teks acak) dan akhir percobaan
- [x] Lantai terakhir + ending + kredit
- [x] Audio lengkap sesuai tabel §12 GDD + cek batas kekerasan suara
- [x] Polish: grain, transisi fade
- [x] README final: cara pasang, cara main, kontrol, tombol debug

**Selesai kalau:** satu run penuh sampai ending bisa diselesaikan (dicek pakai lompatan lantai debug), semua teks berbahasa Indonesia, dan tidak ada crash.

### M4 — Tuning
- [x] Mode dev (`--dev`): kebal, sonar tanpa jeda, senter tanpa batas, bisa diubah dari judul dan menu jeda
- [x] Umpan balik saat tertangkap: waktu berhenti, getar layar, makhluk yang menangkap terlihat, denyut merah
- [ ] Kamu memainkan game dan mengisi checklist playtest (§7)
- [ ] Angka-angka di `config.py` disetel dari masukanmu
- [ ] Bug yang ditemukan diperbaiki

---

## 5. Strategi pengujian

| Jenis | Apa yang dicek |
|---|---|
| **Unit test** | Labirin selalu terhubung dan ukurannya benar. Braiding mengurangi jalan buntu. Jarak penempatan fragmen dan pintu keluar sesuai aturan. Keterhubungan tetap terjaga setelah 1000 pergeseran acak. Hasil raycast sama dengan sampling brute-force. BFS menemukan jalur terpendek. Varian catatan dan pengisian `{n}` benar. File simpanan rusak tidak membuat crash. |
| **Bot headless** | Bot bergerak acak, memakai sonar dan senter selama ±3 menit waktu game per lantai dengan `dt` tetap. Dengan kait debug, ia mengambil semua fragmen dan pindah lantai sampai ending. Target: tanpa exception, dan waktu per frame tercatat. |
| **Review visual** | `tools/snap.py` merender frame tertentu (lantai, stres, posisi) ke PNG, lalu aku periksa gambarnya. |
| **Playtest manusia** | Kamu. Hanya lewat cara ini "rasa" game bisa dinilai (§7). |

**Alat bantu untuk kamu saat playtest:**
- `--dev`: menu mode dev (kebal, sonar tanpa jeda, senter tanpa batas, kerikil & dinding tanpa batas) plus `F3` (overlay debug) dan `F5`/`F6`
- `python main.py --floor 4`: langsung ke Lantai 4
- `--seed 123`: labirin yang sama setiap kali main, berguna untuk melaporkan bug
- `--mute`: main tanpa suara

---

## 6. Risiko & mitigasi

| Risiko | Mitigasi |
|---|---|
| Pencahayaan terlalu berat di laptop lemah | Sudah diuji 3,4 ms/frame. Cadangannya, peta cahaya dirender di setengah resolusi lalu diperbesar. |
| Tidak ada perangkat audio, atau perilaku audio beda antar-OS | Fallback tanpa suara. Hanya memakai fitur mixer dasar. |
| Labirin bergeser mengurung pemain | Invarian BFS "semua lantai terhubung" ditambah property test 1000 pergeseran |
| Kematian terasa tidak adil karena gema palsu | Aturan keadilan §6.3 GDD dikodekan dan dites |
| "Rasa takut" tidak bisa aku uji sendiri | Semua angka ada di satu file `config.py`, ada overlay debug, dan ada checklist playtest |
| Scope membengkak | Daftar "tidak masuk" di §15 GDD. Fitur baru masuk backlog, tidak langsung dikerjakan. |
| Bentrok `pygame` dan `pygame-ce` di komputermu | Instruksi uninstall di README |

---

## 7. Checklist playtest (untuk M4)

Setelah main minimal satu run, jawab singkat saja:

1. Kapan pertama kali kamu merasa tegang? Kapan merasa aman?
2. Pernah mati dan merasa itu tidak adil? Ceritakan kejadiannya.
3. Sonar: terlalu sering dipakai, terlalu jarang, atau pas?
4. Baterai: sering habis, berlebih, atau pas?
5. Pengamat terasa mengganggu dalam arti bagus (bikin tidak nyaman), atau menyebalkan dalam arti buruk?
6. Kamu sadar labirinnya bergeser? Kapan pertama kali sadar?
7. Kamu membaca catatan-catatannya? Mana yang paling mengena?
8. Berapa lama satu lantai? Terlalu panjang atau terlalu pendek?
9. Ada suara yang terlalu keras atau mengagetkan? Seharusnya tidak ada.
10. Game lag atau patah-patah?

---

## 8. Alur kerja git

- Semua pekerjaan dilakukan di branch `claude/simple-pygame-game-m8hhm7`.
- Commit dibuat per fitur, dengan pesan yang jelas.
- Push dilakukan setiap kali satu milestone lulus kriteria selesainya, dan test harus hijau sebelum push.
