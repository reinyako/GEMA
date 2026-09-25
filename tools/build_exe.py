"""Membungkus GEMA menjadi satu file GEMA.exe untuk rilis Windows.

    pip install -r requirements-build.txt
    python tools/build_exe.py

Langkahnya: membuat ikon, menjalankan PyInstaller, menjalankan `GEMA.exe --selftest`,
lalu membuat zip rilis. Hasil ada di dist/: GEMA.exe dan GEMA-v<versi>-windows.zip.
"""

import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
DIST = ROOT / "dist"
sys.path.insert(0, str(ROOT))

from gema import __version__  # noqa: E402

VERSION_INFO = """\
VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}, mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'v.obscura'),
      StringStruct('FileDescription', 'GEMA'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', 'GEMA'),
      StringStruct('OriginalFilename', 'GEMA.exe'),
      StringStruct('ProductName', 'GEMA'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""

README = """\
GEMA {version}
oleh v.obscura

Game horor psikologis top-down. Di labirin yang gelap total, melihat berarti terdengar.


CARA MAIN
Jalankan GEMA.exe. Tidak perlu memasang Python.

PAKAI EARPHONE. Setengah dari game ini ada di suaranya, dan arah suara (kiri/kanan)
adalah informasi penting.

  W A S D              bergerak (jalan pelan)
  Shift (tahan)        lari: cepat tapi berisik
  Mouse                mengarahkan senter
  Klik kiri (tahan)    senter
  Klik kanan / Spasi   sonar
  Esc                  jeda (ada daftar catatan yang sudah ditemukan)
  F11                  layar penuh


KALAU WINDOWS MEMBLOKIR
GEMA.exe tidak ditandatangani secara digital, jadi Windows SmartScreen bisa menampilkan
"Windows protected your PC". Klik "More info" lalu "Run anyway".

Saat dibuka, GEMA.exe perlu beberapa detik sebelum jendelanya muncul. Itu normal.


DATA SIMPANAN
Jumlah percobaan, kematian, dan ending disimpan di %USERPROFILE%\\.gema\\save.json.
Hapus file itu untuk mulai dari nol.
"""


def step(title):
    print(f"\n== {title}", flush=True)


def run(cmd, **kw):
    print("  $ " + " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def main():
    if sys.platform != "win32":
        sys.exit("Script ini untuk membuat GEMA.exe dan harus dijalankan di Windows.")
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.exit("PyInstaller belum terpasang: pip install -r requirements-build.txt")

    nums = tuple(int(n) for n in __version__.split(".")) + (0,)
    ico = BUILD / "gema.ico"
    version_file = BUILD / "version_info.txt"
    exe = DIST / "GEMA.exe"

    step("Ikon")
    run([sys.executable, ROOT / "tools" / "make_icon.py", "--out", ico, "--png", BUILD / "gema.png"])
    version_file.write_text(VERSION_INFO.format(nums=nums, version=__version__), encoding="utf-8")

    step("PyInstaller")
    run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
        "--name", "GEMA", "--icon", ico, "--version-file", version_file,
        "--distpath", DIST, "--workpath", BUILD / "pyinstaller", "--specpath", BUILD,
        "--exclude-module", "tkinter", "--exclude-module", "PIL", "--exclude-module", "pytest",
        ROOT / "main.py",
    ], cwd=ROOT)

    step("Selftest")
    log = Path(tempfile.mkdtemp(prefix="gema-build-")) / "selftest.txt"
    env = dict(os.environ, GEMA_SELFTEST_LOG=str(log))
    result = subprocess.run([str(exe), "--selftest"], env=env, timeout=180)
    report = log.read_text(encoding="utf-8").strip() if log.exists() else "(tidak ada laporan)"
    print("  " + report.replace("\n", "\n  "))
    if result.returncode != 0:
        sys.exit(f"Selftest gagal (kode {result.returncode}). GEMA.exe jangan dirilis dulu.")

    step("Zip")
    zip_path = DIST / f"GEMA-v{__version__}-windows.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(exe, "GEMA/GEMA.exe")
        z.writestr("GEMA/BACA-DULU.txt", README.format(version=__version__).replace("\n", "\r\n"))

    mb = 1024 * 1024
    print(f"\nSelesai.\n  {exe}  ({exe.stat().st_size / mb:.1f} MB)")
    print(f"  {zip_path}  ({zip_path.stat().st_size / mb:.1f} MB)")


if __name__ == "__main__":
    main()
