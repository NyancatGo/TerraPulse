"""
TerraPulse Map View
PyQt6 WebEngine tabanli harita goruntuleme widget'i
"""
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QColor
import os


class MapView(QWebEngineView):
    """
    Folium HTML haritalarını görüntülemek için özel WebEngine view
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 360)
        self.setObjectName("MapViewport")
        self.setStyleSheet("border: none; background: #0a1324;")

        # WebEngine ayarları - local file access ve JavaScript
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        self.page().setBackgroundColor(QColor("#0a1324"))
        
    def load_map(self, path):
        """
        HTML harita dosyasını yükler
        
        Args:
            path: HTML dosya yolu (göreceli veya mutlak)
        """
        # Mutlak yolu al
        file_path = os.path.abspath(path)
        
        print(f"🗺️ Harita yükleniyor: {file_path}")
        
        # Dosya var mı kontrol et
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
        
        # Haritayı yükle
        url = QUrl.fromLocalFile(file_path)
        print(f"🔗 URL: {url.toString()}")
        
        self.load(url)
        print(f"✅ QWebEngineView.load() çağrıldı")
    
    def load_html_string(self, html_content):
        """
        Doğrudan HTML içeriğini yükler
        
        Args:
            html_content: HTML string
        """
        self.setHtml(html_content)
    
    def reload_map(self):
        """
        Mevcut haritayı yeniden yükler
        """
        self.reload()
