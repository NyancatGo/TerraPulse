"""
TerraPulse - Exe Paketleme Betigi
==================================
Bu script, PyInstaller kullanarak TerraPulse uygulamasini
bagimsiz bir Windows exe'ye donusturur.

Kullanim:
    py build_exe.py

Gereksinimler:
    py -m pip install pyinstaller
"""

import subprocess
import sys
import os
import shutil

# Windows konsol encoding sorunlarini onle
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    spec_file = os.path.join(project_root, "terrapulse.spec")
    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")

    # Spec dosyasi kontrol
    if not os.path.exists(spec_file):
        print("[HATA] terrapulse.spec dosyasi bulunamadi!")
        print(f"   Beklenen konum: {spec_file}")
        sys.exit(1)

    # PyInstaller kurulu mu?
    try:
        import PyInstaller
        print(f"[OK] PyInstaller surumu: {PyInstaller.__version__}")
    except ImportError:
        print("[HATA] PyInstaller kurulu degil!")
        print("   Kurmak icin: py -m pip install pyinstaller")
        sys.exit(1)

    # Onceki build temizligi
    for cleanup_dir in [build_dir]:
        if os.path.exists(cleanup_dir):
            print(f"[TEMIZLIK] Onceki build temizleniyor: {cleanup_dir}")
            shutil.rmtree(cleanup_dir, ignore_errors=True)

    print("")
    print("=" * 60)
    print("  TerraPulse exe paketleme baslatiliyor...")
    print("=" * 60)
    print("")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        spec_file,
        "--noconfirm",
        "--clean",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
    ]

    print(f"[KOMUT] {' '.join(cmd)}")
    print("")

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        exe_path = os.path.join(dist_dir, "TerraPulse", "TerraPulse.exe")
        print("")
        print("=" * 60)
        print("[BASARILI] Paketleme tamamlandi!")
        print(f"[CIKTI]    {os.path.join(dist_dir, 'TerraPulse')}")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"[BOYUT]    Exe: {size_mb:.1f} MB")
        print("=" * 60)
        print("")
        print("Uygulamayi calistirmak icin:")
        print(f"  {exe_path}")
    else:
        print("")
        print("=" * 60)
        print("[BASARISIZ] Paketleme hatasi!")
        print("   Hata ciktisini yukari kaydirarak inceleyin.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
