# -*- mode: python ; coding: utf-8 -*-
"""
TerraPulse PyInstaller Spec Dosyasi
====================================
Bu dosya, TerraPulse uygulamasini bagimsiz bir Windows exe'ye
donusturmek icin PyInstaller yapilandirmasini icerir.

Kullanim:
    pyinstaller terrapulse.spec

veya:
    python build_exe.py
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

# Proje kok dizini (spec dosyasinin bulundugu yer)
PROJECT_ROOT = os.path.abspath(SPECPATH)

# ---------------------------------------------------------------
# Folium ve branca kutuphaneleri kendi sablonlarini (JS/CSS/HTML)
# paket icerisinde tasir. Bunlar --collect-data ile dahil edilmezse
# harita uretimi sirasinda Jinja2 TemplateNotFound hatasi olusur.
# ---------------------------------------------------------------
folium_datas = collect_data_files('folium')
branca_datas = collect_data_files('branca')

# ---------------------------------------------------------------
# Uygulama kaynaklari: ikonlar, GeoJSON, CSV ve varsayilan DB
# ---------------------------------------------------------------
app_datas = [
    # SVG ikonlar
    (os.path.join(PROJECT_ROOT, 'src', 'ui', 'icons', 'eye.svg'),
     os.path.join('src', 'ui', 'icons')),
    (os.path.join(PROJECT_ROOT, 'src', 'ui', 'icons', 'eye_off.svg'),
     os.path.join('src', 'ui', 'icons')),
    # GeoJSON fay hatlari
    (os.path.join(PROJECT_ROOT, 'data', 'geo', 'turkey_fault_lines.geojson'),
     os.path.join('data', 'geo')),
    # Ham deprem verisi (veritabani yeniden olusturma icin yedek)
    (os.path.join(PROJECT_ROOT, 'data', 'raw', 'earthquakes.csv'),
     os.path.join('data', 'raw')),
    # Varsayilan SQLite veritabani (ilk calistirmada kopyalanir)
    (os.path.join(PROJECT_ROOT, 'data', 'processed', 'terrapulse.db'),
     os.path.join('data', 'processed')),
    # SQL dosyalari
    (os.path.join(PROJECT_ROOT, 'sql', 'default_users.sql'),
     'sql'),
]

all_datas = app_datas + folium_datas + branca_datas

# ---------------------------------------------------------------
# Hidden imports: PyInstaller'in otomatik bulamadigi moduller
# ---------------------------------------------------------------
hidden_imports = [
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebChannel',
    'PyQt6.sip',
    'fpdf',
    # Matplotlib backend
    'matplotlib.backends.backend_qtagg',
    # Proje modulleri
    'database.db_manager',
    'data_processing.data_cleaner',
    'visualization.map_engine',
    'reporting.report_manager',
    'ui.main_window',
    'ui.login_window',
    'ui.analysis_tab',
    'ui.components',
    'ui.map_view',
    'utils.paths',
]

# ---------------------------------------------------------------
# Analysis, PYZ, EXE ve COLLECT yapilandirmasi
# ---------------------------------------------------------------
a = Analysis(
    [os.path.join(PROJECT_ROOT, 'src', 'app.py')],
    pathex=[os.path.join(PROJECT_ROOT, 'src')],
    binaries=[],
    datas=all_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        '_tkinter',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TerraPulse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Konsol penceresi acilmasin
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TerraPulse',
)
