"""
TerraPulse Map View
PyQt6 WebEngine tabanlı harita görüntüleme widget'ı
"""
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl
import os


class MapView(QWebEngineView):
    """
    Folium HTML haritalarını görüntülemek için özel WebEngine view
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        
        # WebEngine ayarları - local file access ve JavaScript
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        
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
            self.setHtml("<h1 style='text-align:center; margin-top:50px;'>Harita dosyası bulunamadı</h1>")
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
