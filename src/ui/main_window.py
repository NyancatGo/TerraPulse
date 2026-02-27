from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QPushButton, QLabel, QSlider, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TerraPulse - Sismik Veri Analizi")
        self.setGeometry(100, 100, 1024, 768)

        # Tab widget kurulumu
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._init_tabs()

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
        
        # Büyüklük filtresi (Slider)
        self.slider_mag = QSlider(Qt.Orientation.Horizontal)
        self.slider_mag.setRange(0, 100) # 0.0 - 10.0 (x10)
        self.slider_mag.setValue(40) # Default 4.0
        
        # Filtreleme butonu
        self.btn_filter = QPushButton("Filtrele")

        # Layout'a ekle
        filter_layout.addWidget(QLabel("Min Büyüklük:"))
        filter_layout.addWidget(self.slider_mag)
        filter_layout.addWidget(self.btn_filter)

        # Harita görünüm alanı (Placeholder)
        self.map_placeholder = QLabel("Burada Folium haritası PyQtWebEngine ile görüntülenecektir (Hafta 4)")
        self.map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_placeholder.setStyleSheet("background-color: lightgray; border: 1px solid black;")

        # Ana layout'a yerleştirme
        layout.addLayout(filter_layout)
        layout.addWidget(self.map_placeholder, stretch=1)
        
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
