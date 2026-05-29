"""
TerraPulse - Merkezi Yol Yonetim Modulu
========================================
Uygulamanin hem gelistirici modunda (python src/app.py) hem de
PyInstaller ile paketlenmis frozen modda (.exe) dogru dosya
yollarini bulmasi icin tek bir referans noktasi saglar.

Temel mantik:
  - Statik kaynaklar (SVG ikonlar, GeoJSON, varsayilan DB, CSV)
    frozen modda sys._MEIPASS icerisinden okunur.
  - Yazilabilir veriler (aktif SQLite DB, harita HTML ciktilari)
    exe'nin yanindaki TerraPulse_Data/ klasorune yazilir.
"""

import os
import sys
import shutil


def is_frozen() -> bool:
    """Uygulama PyInstaller ile paketlenmis mi?"""
    return getattr(sys, "frozen", False)


def _get_bundle_dir() -> str:
    """
    Paket icerisindeki kaynaklarin bulundugu kok dizini dondurur.
    - Frozen modda: sys._MEIPASS (gecici acma dizini)
    - Gelistirici modda: proje kok dizini (TerraPulse/)
    """
    if is_frozen():
        return sys._MEIPASS
    # src/utils/paths.py -> src/utils -> src -> TerraPulse/
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_app_dir() -> str:
    """
    Uygulamanin calistigi dizini dondurur.
    - Frozen modda: exe dosyasinin bulundugu klasor
    - Gelistirici modda: proje kok dizini (TerraPulse/)
    """
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_resource_path(relative_path: str) -> str:
    """
    Paket icerisindeki SALT OKUNUR bir kaynaga erisim saglar.

    Ornekler:
        get_resource_path("data/geo/turkey_fault_lines.geojson")
        get_resource_path("src/ui/icons/eye.svg")
        get_resource_path("data/raw/earthquakes.csv")
    """
    return os.path.join(_get_bundle_dir(), relative_path)


def get_data_dir() -> str:
    """
    Yazilabilir veri dizinini dondurur ve yoksa olusturur.
    - Frozen: <exe_dizini>/TerraPulse_Data/
    - Gelistirici: <proje_koku>/  (proje koku direkt kullanilir)
    """
    if is_frozen():
        data_dir = os.path.join(_get_app_dir(), "TerraPulse_Data")
    else:
        data_dir = _get_app_dir()
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_db_path() -> str:
    """
    Yazilabilir SQLite veritabani yolunu dondurur.
    Ilk calistirmada veritabani yoksa paket icerisindeki
    varsayilan kopyayi hedef dizine kopyalar.
    """
    data_dir = get_data_dir()
    db_dir = os.path.join(data_dir, "data", "processed")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "terrapulse.db")

    # Veritabani yoksa ve paket icerisinde varsayilan varsa kopyala
    if not os.path.exists(db_path):
        bundled_db = get_resource_path(os.path.join("data", "processed", "terrapulse.db"))
        if os.path.exists(bundled_db):
            print(f"📦 Varsayilan veritabani kopyalaniyor: {bundled_db} -> {db_path}")
            shutil.copy2(bundled_db, db_path)

    return db_path


def get_maps_dir() -> str:
    """
    Yazilabilir harita cikti dizinini dondurur ve yoksa olusturur.
    """
    data_dir = get_data_dir()
    maps_dir = os.path.join(data_dir, "maps")
    os.makedirs(maps_dir, exist_ok=True)
    return maps_dir
