
# GEMA
<img width="1916" height="1007" alt="Screenshot 2026-09-25 123525" src="https://github.com/user-attachments/assets/991ddb80-b1fb-4df3-8eeb-8d9a3081f1bf" />
*oleh v.obscura*

Game horor psikologis top-down yang dibuat dengan pygame. Di labirin yang gelap total, melihat berarti terdengar.

Kamu terbangun di labirin gelap dengan senter tua dan alat sonar. Sonar memperlihatkan jalan, tapi makhluk di sana berburu dengan telinga. Kumpulkan tiga fragmen di setiap lantai, lalu temukan pintu keluar.

## Unduh (Windows)

Ambil file `GEMA-v<versi>-windows.zip` terbaru dari halaman [Releases](https://github.com/reinyako/GEMA/releases), ekstrak, lalu jalankan `GEMA.exe`. Tidak perlu memasang Python.

> `GEMA.exe` tidak ditandatangani secara digital, jadi Windows SmartScreen bisa menampilkan "Windows protected your PC". Klik **More info**, lalu **Run anyway**.

## Cara pasang (dari kode)

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

### Opsi lain

| Opsi | Kegunaan |
|---|---|
| `python main.py --floor 4` | Langsung mulai dari Lantai 4 |
| `python main.py --seed 123` | Labirin yang sama setiap kali (sertakan seed saat melaporkan bug) |
| `python main.py --difficulty pekat` | Pilihan awal di layar kesulitan |
| `python main.py --mute` | Tanpa suara |
| `python main.py --dev` | Mode dev untuk testing: menu kebal, sonar tanpa jeda, dan senter tanpa batas. Saat bermain: `F3` overlay debug (peta, status monster, stres, baterai, FPS), `F5` ambil semua fragmen, `F6` pindah ke pintu keluar |

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

## Membuat GEMA.exe

Di Windows:

```bash
pip install -r requirements-build.txt
python tools/build_exe.py
```

Script ini membuat ikon, membungkus game dengan PyInstaller, menjalankan `GEMA.exe --selftest`, lalu membuat `dist/GEMA-v<versi>-windows.zip` yang siap diunggah ke Releases. Versinya diambil dari `gema/__init__.py`.

Ikonnya juga digambar dengan kode ([`gema/render/icon.py`](gema/render/icon.py)), sama seperti visual lain di game ini.

## Dokumen

- [Game Design Document](docs/GDD.md): konsep, mekanik, sistem horor, cerita, visual, dan audio
- [Rencana Pengembangan](docs/PLAN.md): arsitektur, milestone, strategi pengujian, dan checklist playtest

Semua angka tuning (kecepatan, baterai, stres, dan lain-lain) ada di satu file: [`gema/config.py`](gema/config.py).
