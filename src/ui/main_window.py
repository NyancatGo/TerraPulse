from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QPushButton, QLabel, QSlider, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt
from ui.map_view import MapView
from ui.analysis_tab import AnalysisTab
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
        self.combo_region1.addItems(["Tüm Türkiye", "Marmara", "Ege", "Akdeniz", "İç Anadolu", "Karadeniz", "Doğu Anadolu", "Güneydoğu Anadolu"])
        self.combo_region2 = QComboBox()
        self.combo_region2.addItems(["Tüm Türkiye", "Marmara", "Ege", "Akdeniz", "İç Anadolu", "Karadeniz", "Doğu Anadolu", "Güneydoğu Anadolu"])
        
        # Sinyal Bağlantıları (Seçim değiştiğinde filtrelemeyi tetikler)
        self.combo_region1.currentIndexChanged.connect(self._apply_filter)
        self.combo_region2.currentIndexChanged.connect(self._apply_filter)
        # Eğer bir Karşılaştır butonu isterseniz (opsiyonel), o da tetikleyebilir:
        
        controls.addWidget(QLabel("Bölge 1:"))
        controls.addWidget(self.combo_region1)
        controls.addWidget(QLabel("Bölge 2:"))
        controls.addWidget(self.combo_region2)
        
        self.btn_compare = QPushButton("Karşılaştır")
        self.btn_compare.clicked.connect(self._apply_filter)
        controls.addWidget(self.btn_compare)
                # Matplotlib grafik alanı (AnalysisTab) için güvenli container
        self.analysis_container = QWidget()
        container_layout = QVBoxLayout(self.analysis_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # İçine AnalysisTab'ı yerleştir
        self.analysis_widget = AnalysisTab()
        container_layout.addWidget(self.analysis_widget)

        layout.addLayout(controls)
        layout.addWidget(self.analysis_container, stretch=1)
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
        
        # Seçili bölgeleri al (.currentText() ile)
        # Sınıf başlatılırken combo_region1 vb henüz yoksa (hata almamak için) try-except bloğu kullanılabilir veya hasattr sorgusu
        region1 = getattr(self, "combo_region1", None)
        region2 = getattr(self, "combo_region2", None)
        
        region1_text = region1.currentText() if region1 else "Tüm Türkiye"
        region2_text = region2.currentText() if region2 else "Tüm Türkiye"
        
        # Debug Çıktısı (Kullanıcının Tıklamalarını doğrulamak için)
        print(f"\n[DEBUG] Seçilen Bölge 1: {region1_text}, Bölge 2: {region2_text}")
        print(f"[DEBUG] 🔍 Diğer Filtreler: Mag>={min_mag:.1f}, Yıl: {start_year}-{end_year}")
        
        # SQLite'tan filtrelenmiş veriyi çek (db_manager modifiye edilerek WHERE bölgesine parametre eklendi)
        filtered_df = self.db.fetch_earthquakes(
            min_mag=min_mag,
            max_mag=10.0,
            start_year=start_year,
            end_year=end_year,
            region1=region1_text,
            region2=region2_text
        )
        
        # Filtre sonucunun kontrolü
        print(f"[DEBUG] 📊 filtrelenmiş DF uzunluğu: {len(filtered_df)}")
        if not filtered_df.empty:
            print(f"[DEBUG] 📊 Gelen sütunlar: {filtered_df.columns.tolist()}")
        
        # Deprem sayısını güncelle
        self.lbl_count.setText(f"📊 Deprem: {len(filtered_df)}")
        
        # Grafikleri güncelle
        self.analysis_widget.update_charts(filtered_df)
        
        # Haritayı güncelle
        if not filtered_df.empty:
            self._update_map(filtered_df)
        else:
            print("⚠️ Filtre sonucu veri bulunamadı")
            self.lbl_count.setText("📊 Deprem: 0")
            
        # --- VERİ DOĞRULAMA ÇAĞRISI ---
        self._validate_data(filtered_df)
        
    def _validate_data(self, df):
        """Çizilen grafik verisinin ham DB verisiyle uyumunu test eder"""
        print("\n" + "="*50)
        print("🔍 ÇAPRAZ VERİ KONTROLÜ (DATA VALIDATION)")
        if df is None or df.empty:
            print("   ⚠️ Doğrulanacak veri yok (DataFrame Empty).")
            print("="*50 + "\n")
            return
            
        # Toplam satır sayısını yazdır
        print(f"   📊 Grafiklere ve Haritaya İletilen Toplam Deprem: {len(df)}")
        
        # En yüksek büyüklüğe sahip ilk 3 depremi bul
        print("   📈 Büyüklüğü (Magnitude) En Yüksek İlk 3 Deprem:")
        try:
            # Sütun isimleri farklıysa uyuşmazlığı engelle:
            date_col = 'date' if 'date' in df.columns else 'time' 
            top_3 = df.nlargest(3, 'magnitude')
            
            for index, row in top_3.iterrows():
                print(f"      - Tarih: {row[date_col]} | Mag: {row['magnitude']} | Konum: {row['place']}")
        except Exception as e:
            print(f"   ❌ Doğrulama sırasında hata oluştu: {e}")
            
        print("="*50 + "\n")
    
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
        
        # İlk yükleme veri durumu kontrolü
        print(f"[DEBUG] İlk yüklenen DF uzunluğu: {len(filtered_df)}")
        if not filtered_df.empty:
             print(f"[DEBUG] 📊 İlk yüklenen sütunlar: {filtered_df.columns.tolist()}")
        
        # Sayacı güncelle
        self.lbl_count.setText(f"📊 Deprem: {len(filtered_df)}")
        
        # Grafikleri başlat
        self.analysis_widget.update_charts(filtered_df)
        
        # Haritayı oluştur
        if not filtered_df.empty:
            self._update_map(filtered_df)
    
    def closeEvent(self, event):
        """Pencere kapatılırken veritabanı bağlantısını kapat"""
        if hasattr(self, 'db'):
            self.db.close()
            print("✅ Veritabanı bağlantısı kapatıldı")
        event.accept()
