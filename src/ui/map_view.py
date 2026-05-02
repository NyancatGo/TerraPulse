"""
TerraPulse Map View
PyQt6 WebEngine tabanli harita goruntuleme widget'i
"""

import os

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QColor
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MapView(QWebEngineView):
    """
    Folium HTML haritalarini goruntulemek icin ozel WebEngine view.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 360)
        self.setObjectName("MapViewport")
        self.setStyleSheet("border: none; background: #0a1324;")
        self._pending_url = None

        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        profile = self.page().profile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        profile.setHttpCacheMaximumSize(64 * 1024 * 1024)
        profile.clearHttpCache()

        self.page().setBackgroundColor(QColor("#0a1324"))
        self.loadFinished.connect(self._refresh_leaflet_after_load)

    def load_map(self, path):
        """
        HTML harita dosyasini yukler.
        """
        file_path = os.path.abspath(path)
        print(f"🗺️ Harita yükleniyor: {file_path}")

        if not os.path.exists(file_path):
            print(f"⚠️ Harita dosyası bulunamadı: {file_path}")
            self.setHtml(
                """
                <html>
                    <body style="margin:0; font-family:'Segoe UI', sans-serif; background:#0a1324; color:#e5edf7;">
                        <div style="height:100vh; display:flex; align-items:center; justify-content:center;">
                            <div style="text-align:center;">
                                <div style="font-size:18px; font-weight:700; margin-bottom:8px;">Harita dosyasi bulunamadi</div>
                                <div style="font-size:13px; color:#8ea2bd;">Harita uretildiginde bu alan otomatik olarak yenilenecek.</div>
                            </div>
                        </div>
                    </body>
                </html>
                """
            )
            return

        print(f"✅ Dosya mevcut, boyut: {os.path.getsize(file_path) / 1024 / 1024:.2f} MB")
        self._pending_url = QUrl.fromLocalFile(file_path)

        # Eski Folium dokumanini once temizle; ardindan benzersiz dosyayi yukle.
        self.stop()
        self.setHtml(
            """
            <html>
                <body style="margin:0; background:#0a1324;"></body>
            </html>
            """
        )
        QTimer.singleShot(30, self._load_pending_url)

    def _load_pending_url(self):
        if self._pending_url is None:
            return

        print(f"🔗 URL: {self._pending_url.toString()}")
        self.load(self._pending_url)
        print("✅ QWebEngineView.load() çağrıldı")

    def _refresh_leaflet_after_load(self, ok):
        if not ok:
            return

        QTimer.singleShot(120, self._run_leaflet_refresh)
        QTimer.singleShot(420, self._run_leaflet_refresh)

    def _run_leaflet_refresh(self):
        script = """
        (function () {
            Object.keys(window)
                .filter(function (key) {
                    return key.indexOf('map_') === 0 &&
                        window[key] &&
                        typeof window[key].invalidateSize === 'function';
                })
                .forEach(function (key) {
                    var map = window[key];
                    map.invalidateSize(true);
                    if (map.dragging) map.dragging.enable();
                    if (map.scrollWheelZoom) map.scrollWheelZoom.enable();
                    if (map.doubleClickZoom) map.doubleClickZoom.enable();
                    if (map.boxZoom) map.boxZoom.enable();
                    if (map.keyboard) map.keyboard.enable();
                });
        })();
        """
        self.page().runJavaScript(script)

    def load_html_string(self, html_content):
        self.setHtml(html_content)

    def reload_map(self):
        self.reload()
