from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QPushButton, QLabel, QSlider, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt
from ui.map_view import MapView
from visualization.map_engine import create_earthquake_map, filter_earthquakes
from data_processing.data_cleaner import DataCleaner
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TerraPulse - Sismik Veri Analizi")
        self.setGeometry(100, 100, 1024, 768)

        # Veri yükleme
        self.data_cleaner = DataCleaner()
        self.earthquake_data = self.data_cleaner.process_data()
        self.filtered_data = self.earthquake_data.copy()
        
        # Harita dosya yolu - maps/ dizinine kaydet
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        maps_dir = os.path.join(project_root, "maps")
        os.makedirs(maps_dir, exist_ok=True)
        self.map_path = os.path.join(maps_dir, "earthquake_map.html")

        # Tab widget kurulumu
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._init_tabs()
        
        # İlk haritayı oluştur ve yükle
        if not self.earthquake_data.empty:
            # İlk yüklemede performans için sadece büyük depremleri göster
            print("🗺️ İlk harita yükleniyor (Büyüklük >= 4.0 - optimize)...")
            self.filtered_data = filter_earthquakes(self.earthquake_data, min_magnitude=4.0)
            self.slider_mag.setValue(40)  # 4.0
            self._update_map()
            # Count label'ı güncelle
            if hasattr(self, 'lbl_count'):
                self.lbl_count.setText(f"📊 {len(self.filtered_data)} deprem")

    def _init_tabs(self):
        """Sekmeleri (Tab) oluştur ve ekle."""
        self.tab_map = QWidget()
        self.tab_analysis = QWidget()
        self.tab_risk = QWidget()

        self.tabs.addTab(self.tab_map, "Harita & Filtreleme")
        self.tabs.addTab(self.tab_analysis, "Karşılaştırmalı Analiz")
        self.tabs.addTab(self.tab_risk, "Risk Skorlama")

        self._setup_map_tab()
        self._setup_analysis_tab()
        self._setup_risk_tab()

    def _setup_map_tab(self):
        """1. Sekme: Harita & Filtreleme arayüz bileşenleri"""
        layout = QVBoxLayout()
        
        # Filtreleme Kontrolleri Layout'u
        filter_layout = QHBoxLayout()
        
        # Büyüklük filtresi (Slider) - 3.0'dan başlasın performans için
        self.slider_mag = QSlider(Qt.Orientation.Horizontal)
        self.slider_mag.setRange(30, 80)  # 3.0 - 8.0 (x10)
        self.slider_mag.setValue(40)  # Default 4.0
        
        # Slider değer etiketi
        self.lbl_mag_value = QLabel("4.0")
        self.slider_mag.valueChanged.connect(self._update_magnitude_label)
        
        # Filtreleme butonu
        self.btn_filter = QPushButton("Filtrele")
        self.btn_filter.clicked.connect(self._apply_filter)
        
        # Sıfırlama butonu
        self.btn_reset = QPushButton("Sıfırla")
        self.btn_reset.clicked.connect(self._reset_filter)

        # Layout'a ekle
        filter_layout.addWidget(QLabel("Min Büyüklük:"))
        filter_layout.addWidget(self.slider_mag)
        filter_layout.addWidget(self.lbl_mag_value)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addWidget(self.btn_reset)
        
        # Performans bilgi etiketi
        self.lbl_count = QLabel("")
        filter_layout.addWidget(self.lbl_count)
        filter_layout.addStretch()

        # Harita widget'ı (MapView)
        self.map_widget = MapView()

        # Ana layout'a yerleştirme
        layout.addLayout(filter_layout)
        layout.addWidget(self.map_widget, stretch=1)
        
        self.tab_map.setLayout(layout)

    def _setup_analysis_tab(self):
        """2. Sekme: Karşılaştırmalı Analiz bileşenleri"""
        layout = QVBoxLayout()
        
        controls = QHBoxLayout()
        self.combo_region1 = QComboBox()
        self.combo_region1.addItems(["Marmara", "Ege", "İç Anadolu", "Doğu Anadolu"])
        self.combo_region2 = QComboBox()
        self.combo_region2.addItems(["Marmara", "Ege", "İç Anadolu", "Doğu Anadolu"])
        
        controls.addWidget(QLabel("Bölge 1:"))
        controls.addWidget(self.combo_region1)
        controls.addWidget(QLabel("Bölge 2:"))
        controls.addWidget(self.combo_region2)
        
        self.btn_compare = QPushButton("Karşılaştır")
        controls.addWidget(self.btn_compare)

        # Matplotlib grafik alanı
        self.graph_placeholder = QLabel("Burada Matplotlib grafikleri yer alacak (Hafta 7)")
        self.graph_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_placeholder.setStyleSheet("background-color: #e0e0e0; border: 1px dashed gray;")

        layout.addLayout(controls)
        layout.addWidget(self.graph_placeholder, stretch=1)
        self.tab_analysis.setLayout(layout)

    def _setup_risk_tab(self):
        """3. Sekme: Risk Skorlama bileşenleri"""
        layout = QVBoxLayout()
        
        lbl_info = QLabel("Poisson dağılımı kullanılarak Risk Skorlama Modülü (Hafta 9)")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_calculate = QPushButton("Risk Skorlarını Hesapla")
        self.btn_export = QPushButton("PDF Raporu Oluştur")

        layout.addWidget(lbl_info)
        layout.addWidget(self.btn_calculate)
        layout.addWidget(self.btn_export)
        layout.addStretch()

        self.tab_risk.setLayout(layout)
    
    def _update_magnitude_label(self):
        """Slider değerini etikette göster"""
        value = self.slider_mag.value() / 10.0
        self.lbl_mag_value.setText(f"{value:.1f}")
    
    def _apply_filter(self):
        """Filtreleme uygula ve haritayı güncelle"""
        # Minimum büyüklük değerini al
        min_mag = self.slider_mag.value() / 10.0
        
        # Veriyi filtrele
        self.filtered_data = filter_earthquakes(
            self.earthquake_data, 
            min_magnitude=min_mag
        )
        
        print(f"🔍 Filtre uygulandı: Min Büyüklük {min_mag:.1f}")
        print(f"📊 Toplam {len(self.filtered_data)} deprem gösteriliyor")
        
        # Bilgi etiketini güncelle
        self.lbl_count.setText(f"📊 {len(self.filtered_data)} deprem")
        
        # Haritayı güncelle
        self._update_map()
    
    def _reset_filter(self):
        """Filtreyi sıfırla"""
        self.slider_mag.setValue(30)  # 3.0'a dön
        self.filtered_data = filter_earthquakes(self.earthquake_data, min_magnitude=3.0)
        print("🔄 Filtre sıfırlandı (3.0+)")
        self.lbl_count.setText(f"📊 {len(self.filtered_data)} deprem")
        self._update_map()
    
    def _update_map(self):
        """Haritayı oluştur ve görüntüle"""
        if self.filtered_data.empty:
            print("⚠️ Gösterilecek deprem verisi yok")
            return
        
        try:
            # Harita oluştur
            map_path = create_earthquake_map(self.filtered_data, self.map_path)
            
            # MapView'e yükle
            self.map_widget.load_map(map_path)
            print(f"✅ Harita güncellendi: {len(self.filtered_data)} deprem gösteriliyor")
        except Exception as e:
            print(f"❌ Harita yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
