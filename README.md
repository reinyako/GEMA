# GEMA

*oleh v.obscura*

Game horor psikologis top-down yang dibuat dengan pygame. Di labirin yang gelap total, melihat berarti terdengar.

Kamu terbangun di labirin gelap dengan senter tua dan alat sonar. Sonar memperlihatkan jalan, tapi makhluk di sana berburu dengan telinga. Kumpulkan tiga fragmen di setiap lantai, lalu temukan pintu keluar.

Tidak ada file gambar atau suara sama sekali. Semua visual digambar dengan kode, dan semua suara dibuat dengan numpy.

## Cara pasang

Butuh **Python 3.10 atau lebih baru**.

```bash
pip install -r requirements.txt
```

> Kalau di komputermu sudah ada `pygame` biasa, uninstall dulu dengan `pip uninstall pygame`. Game ini memakai `pygame-ce`, dan keduanya memakai nama modul yang sama.

## Cara main

```bash
python main.py
```

**Pakai earphone.** Setengah dari game ini ada di suaranya, dan arah suara (kiri/kanan) adalah informasi penting.

| Tombol | Aksi |
|---|---|
| `W` `A` `S` `D` | Bergerak (jalan pelan) |
| `Shift` (tahan) | Lari: cepat tapi berisik |
| Mouse | Mengarahkan senter |
| Klik kiri (tahan) | Senter |
| Klik kanan / `Spasi` | Sonar |
| `Esc` | Jeda (ada daftar catatan yang sudah ditemukan) |
| `F11` | Layar penuh |

### Beberapa hal yang perlu kamu tahu

- Diam itu sunyi. Jalan itu pelan. Lari itu terdengar dari jauh.
- Sonar bisa dipakai untuk melihat, tapi setiap ping terdengar.
- Cahaya senter membuat mereka diam. Bukan pergi.
- Baterai tidak terisi ulang saat pindah lantai.

## Untuk playtest dan debug

### Mode dev

```bash
python main.py --dev
```

Muncul menu **Mode dev** di layar judul dan di menu jeda (`Esc`). Pilihannya bisa dinyalakan atau dimatikan kapan saja, termasuk di tengah permainan:

| Pilihan | Efek |
|---|---|
| Kebal | Tidak bisa mati. Kalau tersentuh monster, efek tertangkap (getar, merah, makhluknya terlihat) tetap muncul supaya bisa dites. |
| Sonar tanpa jeda | Sonar bisa dipakai terus-menerus |
| Senter tanpa batas | Baterai selalu penuh |

Selama ada pilihan yang menyala, pojok kanan atas layar menampilkan tulisan kecil `DEV`, supaya kamu tidak lupa sedang main dalam mode dev. Di mode dev juga ada tombol `F5` (ambil semua fragmen lantai ini) dan `F6` (lompat ke pintu keluar).

### Opsi lain

| Opsi | Kegunaan |
|---|---|
| `python main.py --floor 4` | Langsung mulai dari Lantai 4 |
| `python main.py --seed 123` | Labirin yang sama setiap kali (sertakan seed saat melaporkan bug) |
| `python main.py --difficulty pekat` | Pilihan awal di layar kesulitan |
| `python main.py --mute` | Tanpa suara |
| `F3` saat bermain | Overlay debug: peta, status monster, stres, baterai, FPS |

Opsi-opsi ini bisa digabung, misalnya `python main.py --dev --floor 5`.

Data simpanan (jumlah percobaan, kematian, ending) ada di `~/.gema/save.json`. Hapus file itu untuk mulai dari nol.

## Menjalankan test

```bash
pip install -r requirements-dev.txt
pytest
```

Test berjalan tanpa layar dan tanpa suara. Salah satu test menjalankan bot yang memainkan game dari Lantai 1 sampai ending.

Untuk screenshot tanpa layar (berguna saat menyetel visual):

```bash
python tools/snap.py --floor 3 --light --ping --near --stress 90 --out shots/contoh.png
```

## Dokumen

- [Game Design Document](docs/GDD.md): konsep, mekanik, sistem horor, cerita, visual, dan audio
- [Rencana Pengembangan](docs/PLAN.md): arsitektur, milestone, strategi pengujian, dan checklist playtest

Semua angka tuning (kecepatan, baterai, stres, dan lain-lain) ada di satu file: [`gema/config.py`](gema/config.py).
