from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QPushButton, QLabel, QSlider, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt
from ui.map_view import MapView
from visualization.map_engine import create_earthquake_map
from database.db_manager import DBManager, ensure_database_exists
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TerraPulse - Sismik Veri Analizi")
        self.setGeometry(100, 100, 1024, 768)

        # Veritabanı bağlantısını kur
        ensure_database_exists()  # Veritabanı yoksa oluştur
        self.db = DBManager()
        
        # Tarih aralığını al
        self.min_year, self.max_year = self.db.get_date_range()
        print(f"📅 Tarih aralığı: {self.min_year} - {self.max_year}")
        
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
        self._load_initial_map()

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
        
        # === İLK SATIR: Büyüklük Filtresi ===
        mag_filter_layout = QHBoxLayout()
        
        # Büyüklük filtresi (Slider)
        mag_filter_layout.addWidget(QLabel("📈 Min Büyüklük:"))
        self.slider_mag = QSlider(Qt.Orientation.Horizontal)
        self.slider_mag.setRange(30, 80)  # 3.0 - 8.0 (x10)
        self.slider_mag.setValue(40)  # Default 4.0
        mag_filter_layout.addWidget(self.slider_mag)
        
        self.lbl_mag_value = QLabel("4.0")
        self.lbl_mag_value.setMinimumWidth(40)
        self.slider_mag.valueChanged.connect(self._update_magnitude_label)
        mag_filter_layout.addWidget(self.lbl_mag_value)
        
        mag_filter_layout.addStretch()
        layout.addLayout(mag_filter_layout)
        
        # === İKİNCİ SATIR: Tarih Aralığı Filtresi ===
        year_filter_layout = QHBoxLayout()
        
        year_filter_layout.addWidget(QLabel("📅 Yıl Aralığı:"))
        
        # Başlangıç yılı
        self.slider_start_year = QSlider(Qt.Orientation.Horizontal)
        self.slider_start_year.setRange(self.min_year, self.max_year)
        self.slider_start_year.setValue(self.min_year)
        year_filter_layout.addWidget(self.slider_start_year)
        
        self.lbl_start_year = QLabel(str(self.min_year))
        self.lbl_start_year.setMinimumWidth(50)
        self.slider_start_year.valueChanged.connect(self._update_year_labels)
        year_filter_layout.addWidget(self.lbl_start_year)
        
        year_filter_layout.addWidget(QLabel("-"))
        
        # Bitiş yılı
        self.slider_end_year = QSlider(Qt.Orientation.Horizontal)
        self.slider_end_year.setRange(self.min_year, self.max_year)
        self.slider_end_year.setValue(self.max_year)
        year_filter_layout.addWidget(self.slider_end_year)
        
        self.lbl_end_year = QLabel(str(self.max_year))
        self.lbl_end_year.setMinimumWidth(50)
        self.slider_end_year.valueChanged.connect(self._update_year_labels)
        year_filter_layout.addWidget(self.lbl_end_year)
        
        year_filter_layout.addStretch()
        layout.addLayout(year_filter_layout)
        
        # === ÜÇÜNCÜ SATIR: Butonlar ve Sayaç ===
        button_layout = QHBoxLayout()
        
        # Filtreleme butonu
        self.btn_filter = QPushButton("🔍 Filtrele")
        self.btn_filter.clicked.connect(self._apply_filter)
        self.btn_filter.setStyleSheet("font-weight: bold; padding: 8px;")
        button_layout.addWidget(self.btn_filter)
        
        # Sıfırlama butonu
        self.btn_reset = QPushButton("🔄 Sıfırla")
        self.btn_reset.clicked.connect(self._reset_filter)
        button_layout.addWidget(self.btn_reset)
        
        button_layout.addStretch()
        
        # Deprem sayacı
        self.lbl_count = QLabel("📊 Deprem: 0")
        self.lbl_count.setStyleSheet("font-weight: bold; font-size: 14px;")
        button_layout.addWidget(self.lbl_count)
        
        layout.addLayout(button_layout)
        
        # === Harita widget'ı ===
        self.map_widget = MapView()
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
        """Büyüklük slider değerini etikette göster"""
        value = self.slider_mag.value() / 10.0
        self.lbl_mag_value.setText(f"{value:.1f}")
    
    def _update_year_labels(self):
        """Yıl slider değerlerini etiketlerde göster"""
        start_year = self.slider_start_year.value()
        end_year = self.slider_end_year.value()
        
        # Başlangıç yılı bitiş yılından büyük olamaz
        if start_year > end_year:
            self.slider_start_year.setValue(end_year)
            start_year = end_year
        
        self.lbl_start_year.setText(str(start_year))
        self.lbl_end_year.setText(str(end_year))
    
    def _apply_filter(self):
        """Filtreleme uygula - SQLite'tan veri çek ve haritayı güncelle"""
        # Filtre değerlerini al
        min_mag = self.slider_mag.value() / 10.0
        start_year = self.slider_start_year.value()
        end_year = self.slider_end_year.value()
        
        # SQLite'tan filtrelenmiş veriyi çek
        print(f"🔍 Filtre: Mag>={min_mag:.1f}, Yıl: {start_year}-{end_year}")
        filtered_df = self.db.fetch_earthquakes(
            min_mag=min_mag,
            max_mag=10.0,
            start_year=start_year,
            end_year=end_year
        )
        
        # Deprem sayısını güncelle
        self.lbl_count.setText(f"📊 Deprem: {len(filtered_df)}")
        
        # Haritayı güncelle
        if not filtered_df.empty:
            self._update_map(filtered_df)
        else:
            print("⚠️ Filtre sonucu veri bulunamadı")
            self.lbl_count.setText("📊 Deprem: 0")
    
    def _reset_filter(self):
        """Filtreleri sıfırla"""
        self.slider_mag.setValue(30)  # 3.0
        self.slider_start_year.setValue(self.min_year)
        self.slider_end_year.setValue(self.max_year)
        
        print("🔄 Filtreler sıfırlandı")
        
        # Varsayılan filtreyi uygula
        self._apply_filter()
    
    def _update_map(self, df):
        """Haritayı oluştur ve görüntüle"""
        if df.empty:
            print("⚠️ Gösterilecek deprem verisi yok")
            return
        
        try:
            # Harita oluştur
            map_path = create_earthquake_map(df, self.map_path)
            
            # MapView'e yükle
            self.map_widget.load_map(map_path)
            print(f"✅ Harita güncellendi: {len(df)} deprem gösteriliyor")
        except Exception as e:
            print(f"❌ Harita yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_initial_map(self):
        """İlk açılışta haritayı yükle"""
        print("🗺️ İlk harita yükleniyor (Büyüklük >= 4.0)...")
        
        # Varsayılan filtre: 4.0+ magnitude, tüm yıllar
        filtered_df = self.db.fetch_earthquakes(
            min_mag=4.0,
            max_mag=10.0,
            start_year=self.min_year,
            end_year=self.max_year
        )
        
        # Sayacı güncelle
        self.lbl_count.setText(f"📊 Deprem: {len(filtered_df)}")
        
        # Haritayı oluştur
        if not filtered_df.empty:
            self._update_map(filtered_df)
    
    def closeEvent(self, event):
        """Pencere kapatılırken veritabanı bağlantısını kapat"""
        if hasattr(self, 'db'):
            self.db.close()
            print("✅ Veritabanı bağlantısı kapatıldı")
        event.accept()
