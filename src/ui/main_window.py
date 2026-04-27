import os
import math
import shutil

import pandas as pd

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DBManager, ensure_database_exists
from reporting.report_manager import ReportManager
from ui.analysis_tab import AnalysisTab
from ui.components import PageHeader, RiskIndicatorWidget, SurfaceCard, TagChip, build_app_stylesheet
from ui.map_view import MapView
from visualization.map_engine import create_earthquake_map


def get_risk_color(risk_level):
    """Risk seviyesine gore tablo vurgu rengini don."""
    color_map = {
        "Çok Yüksek": QColor(220, 38, 38),
        "Yüksek": QColor(234, 88, 12),
        "Orta": QColor(202, 138, 4),
        "Düşük": QColor(101, 163, 13),
        "Çok Düşük": QColor(21, 128, 61),
    }
    return color_map.get(risk_level, QColor(100, 116, 139))


class DataManagementDialog(QDialog):
    def __init__(self, db_manager: DBManager, parent=None):
        super().__init__(parent)
        self.db = db_manager

        self.setWindowTitle("Veri Yonetimi Paneli")
        self.setModal(True)
        self.resize(980, 620)

        self._build_ui()
        self._load_preview_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Sismik Veri Yonetimi")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #e2e8f0;")

        subtitle = QLabel("Veritabanindaki son 50 deprem kaydi onizlenir, yeni CSV verileri eklenir ve yedek alinabilir.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(6)
        self.preview_table.setHorizontalHeaderLabels([
            "Tarih",
            "Bolge / Konum",
            "Buyukluk",
            "Derinlik",
            "Enlem",
            "Boylam",
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setShowGrid(False)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_upload_csv = QPushButton("📂 Yeni Sismik Veri Ekle (CSV)")
        self.btn_upload_csv.clicked.connect(self._append_csv_data)

        self.btn_backup_db = QPushButton("💾 Veritabanini Yedekle")
        self.btn_backup_db.setProperty("variant", "secondary")
        self.btn_backup_db.clicked.connect(self._backup_database)

        action_row.addWidget(self.btn_upload_csv)
        action_row.addWidget(self.btn_backup_db)
        action_row.addStretch()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.preview_table, stretch=1)
        layout.addLayout(action_row)

    def _load_preview_data(self):
        query = (
            "SELECT time, place, magnitude, depth, latitude, longitude "
            "FROM earthquakes ORDER BY datetime(time) DESC LIMIT 50"
        )

        try:
            df = pd.read_sql_query(query, self.db.conn)
        except Exception as exc:
            QMessageBox.critical(self, "Veri Onizleme Hatasi", f"Kayitlar okunurken hata olustu:\n{exc}")
            self.preview_table.setRowCount(0)
            return

        self.preview_table.setRowCount(len(df))
        for row_index, row in df.iterrows():
            values = [
                str(row.get("time", "")),
                str(row.get("place", "")),
                f"{float(row.get('magnitude')):.1f}" if pd.notna(row.get("magnitude")) else "",
                f"{float(row.get('depth')):.1f}" if pd.notna(row.get("depth")) else "",
                f"{float(row.get('latitude')):.4f}" if pd.notna(row.get("latitude")) else "",
                f"{float(row.get('longitude')):.4f}" if pd.notna(row.get("longitude")) else "",
            ]
            for col_index, value in enumerate(values):
                self.preview_table.setItem(row_index, col_index, QTableWidgetItem(value))

    def _append_csv_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "CSV Dosyasi Sec",
            "",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
            required_columns = {"time", "magnitude", "place", "latitude", "longitude", "depth"}
            missing_columns = required_columns.difference(df.columns)
            if missing_columns:
                missing_str = ", ".join(sorted(missing_columns))
                QMessageBox.warning(
                    self,
                    "CSV Formati Uyumsuz",
                    f"CSV dosyasinda eksik alanlar var: {missing_str}",
                )
                return

            df[list(required_columns)].to_sql("earthquakes", self.db.conn, if_exists="append", index=False)
            QMessageBox.information(
                self,
                "Veri Yukleme Basarili",
                f"CSV verisi basariyla veritabanina eklendi.\nEklenen kayit sayisi: {len(df)}",
            )
            self._load_preview_data()
        except Exception as exc:
            QMessageBox.critical(self, "CSV Yukleme Hatasi", f"CSV verisi eklenirken hata olustu:\n{exc}")

    def _backup_database(self):
        source_path = self.db.db_path
        backup_dir = os.path.dirname(source_path)
        backup_path = os.path.join(backup_dir, "backup_terrapulse.db")

        try:
            shutil.copy(source_path, backup_path)
            QMessageBox.information(
                self,
                "Yedekleme Basarili",
                f"Veritabani yedegi olusturuldu:\n{backup_path}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Yedekleme Hatasi", f"Veritabani yedeklenirken hata olustu:\n{exc}")


class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.setWindowTitle("TerraPulse - Sismik Veri Analizi")
        self.setGeometry(100, 100, 1320, 860)
        self.setMinimumSize(1180, 760)
        self.current_user = current_user or {"username": "Standart Kullanici", "role": "user"}

        ensure_database_exists()
        self.db = DBManager()

        self.min_year, self.max_year = self.db.get_date_range()
        print(f"📅 Tarih aralığı: {self.min_year} - {self.max_year}")

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        maps_dir = os.path.join(project_root, "maps")
        os.makedirs(maps_dir, exist_ok=True)
        self.map_path = os.path.join(maps_dir, "earthquake_map.html")

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.report_manager = ReportManager()
        self.current_filtered_df = None
        self.latest_risk_scores = []

        self._build_shell()
        self.setStyleSheet(build_app_stylesheet())
        self._init_tabs()
        self._load_initial_map()

    def _build_shell(self):
        root = QWidget()
        root.setObjectName("AppShell")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 12, 16, 14)
        root_layout.setSpacing(12)

        root_layout.addWidget(self._create_app_header())
        root_layout.addWidget(self.tabs, stretch=1)

        self.setCentralWidget(root)

    def _create_app_header(self):
        header = QWidget()
        header.setObjectName("AppHeader")
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)

        title_label = QLabel("TerraPulse")
        title_label.setObjectName("HeaderTitle")

        subtitle_label = QLabel(
            "Sismik veriyi harita, karsilastirmali analiz ve risk skorlama yuzeylerinde okuyun."
        )
        subtitle_label.setObjectName("HeaderSubtitle")
        subtitle_label.setWordWrap(True)
        subtitle_label.setMaximumHeight(34)

        text_column.addWidget(title_label)
        text_column.addWidget(subtitle_label)

        chip_row = QHBoxLayout()
        chip_row.setContentsMargins(0, 0, 0, 0)
        chip_row.setSpacing(8)
        chip_row.addStretch()
        self.btn_data_admin = QPushButton("🛠️ Veri Yönetimi")
        self.btn_data_admin.setProperty("variant", "secondary")
        self.btn_data_admin.setVisible(self.current_user.get("role") == "admin")
        self.btn_data_admin.setToolTip("Bu alan admin kullanicilar icin ayrilmistir.")
        self.btn_data_admin.clicked.connect(self._open_data_management)

        chip_row.addWidget(TagChip("Dark mode", "info"))
        chip_row.addWidget(TagChip(f"{self.min_year}-{self.max_year}", "neutral"))
        chip_row.addWidget(TagChip("SQLite onbellek", "accent"))
        chip_row.addWidget(TagChip(self.current_user.get("username", "Kullanici"), "neutral"))
        chip_row.addWidget(self.btn_data_admin)

        layout.addLayout(text_column, 1)
        layout.addLayout(chip_row, 0)
        return header

    def _init_tabs(self):
        self.tab_map = QWidget()
        self.tab_map.setObjectName("TabPage")
        self.tab_analysis = QWidget()
        self.tab_analysis.setObjectName("TabPage")
        self.tab_risk = QWidget()
        self.tab_risk.setObjectName("TabPage")

        self.tabs.addTab(self.tab_map, "Harita & Filtreleme")
        self.tabs.addTab(self.tab_analysis, "Karşılaştırmalı Analiz")
        self.tabs.addTab(self.tab_risk, "Risk Skorlama")

        self._setup_map_tab()
        self._setup_analysis_tab()
        self._setup_risk_tab()

    def _setup_map_tab(self):
        layout = QVBoxLayout(self.tab_map)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(
            PageHeader(
                "Harita ve Filtreleme",
                "Kontroller ustte kompakt tutulur; harita alani sekme icinde tam gorunur.",
                chips=[("Canli filtreleme", "accent"), ("Folium harita", "info")],
            )
        )

        control_card = SurfaceCard(padding=16, spacing=12)
        controls_grid = QGridLayout()
        controls_grid.setContentsMargins(0, 0, 0, 0)
        controls_grid.setHorizontalSpacing(18)
        controls_grid.setVerticalSpacing(10)

        controls_grid.addWidget(self._create_field_label("Min Buyukluk (Mw)"), 0, 0)
        controls_grid.addWidget(self._create_field_label("Baslangic Yili"), 0, 1)
        controls_grid.addWidget(self._create_field_label("Bitis Yili"), 0, 2)

        self.slider_mag = QSlider(Qt.Orientation.Horizontal)
        self.slider_mag.setRange(30, 80)
        self.slider_mag.setValue(40)
        self.slider_mag.valueChanged.connect(self._update_magnitude_label)

        self.lbl_mag_value = TagChip("4.0", "accent")
        self.lbl_mag_value.setMinimumWidth(52)
        mag_wrap = self._wrap_slider(self.slider_mag, self.lbl_mag_value)

        self.slider_start_year = QSlider(Qt.Orientation.Horizontal)
        self.slider_start_year.setRange(self.min_year, self.max_year)
        self.slider_start_year.setValue(self.min_year)
        self.slider_start_year.valueChanged.connect(self._update_year_labels)

        self.slider_end_year = QSlider(Qt.Orientation.Horizontal)
        self.slider_end_year.setRange(self.min_year, self.max_year)
        self.slider_end_year.setValue(self.max_year)
        self.slider_end_year.valueChanged.connect(self._update_year_labels)

        self.lbl_start_year = TagChip(str(self.min_year), "neutral")
        self.lbl_end_year = TagChip(str(self.max_year), "neutral")
        self.lbl_start_year.setMinimumWidth(64)
        self.lbl_end_year.setMinimumWidth(64)

        start_wrap = self._wrap_slider(self.slider_start_year, self.lbl_start_year)
        end_wrap = self._wrap_slider(self.slider_end_year, self.lbl_end_year)

        controls_grid.addWidget(mag_wrap, 1, 0)
        controls_grid.addWidget(start_wrap, 1, 1)
        controls_grid.addWidget(end_wrap, 1, 2)
        controls_grid.setColumnStretch(0, 1)
        controls_grid.setColumnStretch(1, 1)
        controls_grid.setColumnStretch(2, 1)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_filter = QPushButton("Filtrele")
        self.btn_filter.clicked.connect(self._apply_filter)

        self.btn_reset = QPushButton("Sifirla")
        self.btn_reset.setProperty("variant", "secondary")
        self.btn_reset.clicked.connect(self._reset_filter)

        self.lbl_count = QLabel("0")
        self.lbl_count.setObjectName("MetricValue")
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.lbl_count_caption = QLabel("Filtrelenmis deprem")
        self.lbl_count_caption.setObjectName("MetricCaption")
        self.lbl_count_caption.setAlignment(Qt.AlignmentFlag.AlignRight)

        count_box = QWidget()
        count_layout = QVBoxLayout(count_box)
        count_layout.setContentsMargins(0, 0, 0, 0)
        count_layout.setSpacing(0)
        count_layout.addWidget(self.lbl_count)
        count_layout.addWidget(self.lbl_count_caption)

        action_row.addWidget(self.btn_filter)
        action_row.addWidget(self.btn_reset)
        action_row.addStretch()
        action_row.addWidget(count_box, 0, Qt.AlignmentFlag.AlignVCenter)

        control_card.content_layout.addLayout(controls_grid)
        control_card.content_layout.addLayout(action_row)
        layout.addWidget(control_card)

        map_card = SurfaceCard(padding=0, spacing=0)
        map_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        map_header = QWidget()
        map_header_layout = QHBoxLayout(map_header)
        map_header_layout.setContentsMargins(18, 14, 18, 10)
        map_header_layout.setSpacing(12)
        map_header_layout.addWidget(
            self._create_card_header("Turkiye Deprem Haritasi", "Harita alani ekranda tam gorunsun diye ust panel kompakt tutuldu."),
            1,
        )
        map_header_layout.addWidget(TagChip("Yerel HTML gorunumu", "neutral"), 0, Qt.AlignmentFlag.AlignTop)

        self.map_widget = MapView()
        map_card.content_layout.addWidget(map_header)
        map_card.content_layout.addWidget(self.map_widget, stretch=1)
        layout.addWidget(map_card, stretch=1)

    def _setup_analysis_tab(self):
        layout = QVBoxLayout(self.tab_analysis)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(
            PageHeader(
                "Karsilastirmali Analiz",
                "Secim paneli kisaldi; grafik alani sekmede daha genis gorunur.",
                chips=[("Matplotlib grafikler", "info"), ("Bolgesel kiyas", "accent")],
            )
        )

        control_card = SurfaceCard(padding=16, spacing=10)
        control_card.content_layout.addWidget(
            self._create_card_header("Bolge Secimi", "Grafikler mevcut filtrelerle birlikte secili bolgelere gore yenilenir.")
        )

        controls = QHBoxLayout()
        controls.setSpacing(12)

        self.combo_region1 = QComboBox()
        self.combo_region1.addItems(
            ["Tüm Türkiye", "Marmara", "Ege", "Akdeniz", "İç Anadolu", "Karadeniz", "Doğu Anadolu", "Güneydoğu Anadolu"]
        )
        self.combo_region1.currentIndexChanged.connect(self._apply_filter)

        self.combo_region2 = QComboBox()
        self.combo_region2.addItems(
            ["Tüm Türkiye", "Marmara", "Ege", "Akdeniz", "İç Anadolu", "Karadeniz", "Doğu Anadolu", "Güneydoğu Anadolu"]
        )
        self.combo_region2.currentIndexChanged.connect(self._apply_filter)

        self.btn_compare = QPushButton("Karsilastir")
        self.btn_compare.setProperty("variant", "secondary")
        self.btn_compare.clicked.connect(self._apply_filter)

        controls.addWidget(self._create_labeled_control("Bolge 1", self.combo_region1), 1)
        controls.addWidget(self._create_labeled_control("Bolge 2", self.combo_region2), 1)
        controls.addWidget(self.btn_compare, 0, Qt.AlignmentFlag.AlignBottom)

        control_card.content_layout.addLayout(controls)

        self.analysis_widget = AnalysisTab()
        layout.addWidget(control_card)
        layout.addWidget(self.analysis_widget, stretch=1)

    def _setup_risk_tab(self):
        layout = QVBoxLayout(self.tab_risk)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(
            PageHeader(
                "Risk Skorlama",
                "Risk paneli ve parametreler tek satirda tutulur; tabloya daha fazla alan birakilir.",
                chips=[("Poisson modeli", "warning"), ("Bolgesel siralama", "accent")],
            )
        )

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.risk_indicator = RiskIndicatorWidget()
        top_row.addWidget(self.risk_indicator, 3)

        control_card = SurfaceCard(padding=16, spacing=10)
        control_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        control_card.content_layout.addWidget(
            self._create_card_header("Parametreler", "Esik buyuklugunu ve tahmin ufkunu secerek risk skorlarini yeniden uretin.")
        )

        controls = QHBoxLayout()
        controls.setSpacing(12)

        self.combo_risk_mag = QComboBox()
        self.combo_risk_mag.addItems(["4.0", "4.5", "5.0", "5.5", "6.0"])
        self.combo_risk_mag.setCurrentText("5.0")

        self.spin_forecast_years = QSpinBox()
        self.spin_forecast_years.setRange(1, 50)
        self.spin_forecast_years.setValue(1)

        self.btn_calculate = QPushButton("Hesapla")
        self.btn_calculate.clicked.connect(self._calculate_risk_scores)

        self.btn_export = QPushButton("📄 Raporu Indir (PDF)")
        self.btn_export.setProperty("variant", "secondary")
        self.btn_export.setEnabled(True)
        self.btn_export.setToolTip("Mevcut analiz ve risk sonuclarini PDF olarak kaydet.")
        self.btn_export.clicked.connect(self._export_pdf_report)

        controls.addWidget(self._create_labeled_control("Min Buyukluk (Mw)", self.combo_risk_mag), 1)
        controls.addWidget(self._create_labeled_control("Tahmin Ufku (Yil)", self.spin_forecast_years), 1)
        controls.addWidget(self.btn_calculate, 0, Qt.AlignmentFlag.AlignBottom)
        controls.addWidget(self.btn_export, 0, Qt.AlignmentFlag.AlignBottom)

        self.lbl_risk_summary = QLabel("Hesaplama icin esik degerini secip butona tiklayin.")
        self.lbl_risk_summary.setWordWrap(True)
        self.lbl_risk_summary.setMaximumHeight(36)
        self.lbl_risk_summary.setStyleSheet("font-size: 12px; color: #b5c7dd; font-weight: 600;")

        control_card.content_layout.addLayout(controls)
        control_card.content_layout.addWidget(self.lbl_risk_summary)
        top_row.addWidget(control_card, 4)

        layout.addLayout(top_row)

        table_card = SurfaceCard(padding=0, spacing=0)
        table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_header = QWidget()
        table_header_layout = QHBoxLayout(table_header)
        table_header_layout.setContentsMargins(18, 14, 18, 10)
        table_header_layout.setSpacing(12)
        table_header_layout.addWidget(
            self._create_card_header("Risk Tablosu", "Her bolge icin yillik oran, olasilik ve tekrarlanma suresi birlikte sunulur."),
            1,
        )
        table_header_layout.addWidget(TagChip("Canli siralama", "neutral"), 0, Qt.AlignmentFlag.AlignTop)

        self.risk_table = QTableWidget()
        self.risk_table.setColumnCount(6)
        self.risk_table.setHorizontalHeaderLabels(
            ["Bolge", "Deprem Sayisi", "λ (Yillik)", "P(N≥1)", "Tekrarlanma (Yil)", "Risk Seviyesi"]
        )
        self.risk_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.risk_table.verticalHeader().setVisible(False)
        self.risk_table.setAlternatingRowColors(True)
        self.risk_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.risk_table.setShowGrid(False)
        self.risk_table.setMinimumHeight(280)
        self.risk_table.verticalHeader().setDefaultSectionSize(36)

        table_card.content_layout.addWidget(table_header)
        table_card.content_layout.addWidget(self.risk_table, stretch=1)
        layout.addWidget(table_card, stretch=1)

    def _create_card_header(self, title: str, subtitle: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("CardSubtitle")
        subtitle_label.setWordWrap(True)
        subtitle_label.setMaximumHeight(34)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        return widget

    def _create_field_label(self, text: str):
        label = QLabel(text)
        label.setObjectName("FieldLabel")
        return label

    def _create_labeled_control(self, title: str, control: QWidget):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._create_field_label(title))
        layout.addWidget(control)
        return widget

    def _wrap_slider(self, slider: QSlider, badge: TagChip):
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        row.addWidget(slider, 1)
        row.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)
        return wrapper

    def _set_quake_count(self, count: int):
        self.lbl_count.setText(str(count))

    def _update_magnitude_label(self):
        value = self.slider_mag.value() / 10.0
        self.lbl_mag_value.setText(f"{value:.1f}")

    def _update_year_labels(self):
        start_year = self.slider_start_year.value()
        end_year = self.slider_end_year.value()

        if start_year > end_year:
            self.slider_start_year.setValue(end_year)
            start_year = end_year

        self.lbl_start_year.setText(str(start_year))
        self.lbl_end_year.setText(str(end_year))

    def _apply_filter(self):
        min_mag = self.slider_mag.value() / 10.0
        start_year = self.slider_start_year.value()
        end_year = self.slider_end_year.value()

        region1 = getattr(self, "combo_region1", None)
        region2 = getattr(self, "combo_region2", None)

        region1_text = region1.currentText() if region1 else "Tüm Türkiye"
        region2_text = region2.currentText() if region2 else "Tüm Türkiye"

        print(f"\n[DEBUG] Seçilen Bölge 1: {region1_text}, Bölge 2: {region2_text}")
        print(f"[DEBUG] 🔍 Diğer Filtreler: Mag>={min_mag:.1f}, Yıl: {start_year}-{end_year}")

        filtered_df = self.db.fetch_earthquakes(
            min_mag=min_mag,
            max_mag=10.0,
            start_year=start_year,
            end_year=end_year,
            region1=region1_text,
            region2=region2_text,
        )

        print(f"[DEBUG] 📊 filtrelenmiş DF uzunluğu: {len(filtered_df)}")
        if not filtered_df.empty:
            print(f"[DEBUG] 📊 Gelen sütunlar: {filtered_df.columns.tolist()}")

        self.current_filtered_df = filtered_df.copy()
        self._set_quake_count(len(filtered_df))
        self.analysis_widget.update_charts(filtered_df)

        if not filtered_df.empty:
            self._update_map(filtered_df)
        else:
            print("⚠️ Filtre sonucu veri bulunamadı")
            self._set_quake_count(0)

        self._validate_data(filtered_df)

    def _validate_data(self, df):
        print("\n" + "=" * 50)
        print("🔍 ÇAPRAZ VERİ KONTROLÜ (DATA VALIDATION)")
        if df is None or df.empty:
            print("   ⚠️ Doğrulanacak veri yok (DataFrame Empty).")
            print("=" * 50 + "\n")
            return

        print(f"   📊 Grafiklere ve Haritaya İletilen Toplam Deprem: {len(df)}")
        print("   📈 Büyüklüğü (Magnitude) En Yüksek İlk 3 Deprem:")
        try:
            date_col = "date" if "date" in df.columns else "time"
            top_3 = df.nlargest(3, "magnitude")

            for index, row in top_3.iterrows():
                print(f"      - Tarih: {row[date_col]} | Mag: {row['magnitude']} | Konum: {row['place']}")
        except Exception as e:
            print(f"   ❌ Doğrulama sırasında hata oluştu: {e}")

        print("=" * 50 + "\n")

    def _calculate_risk_scores(self):
        min_mag = float(self.combo_risk_mag.currentText())
        forecast_years = int(self.spin_forecast_years.value())
        start_year = self.slider_start_year.value()
        end_year = self.slider_end_year.value()

        scores = self.db.calculate_poisson_risk_scores(
            min_mag=min_mag,
            start_year=start_year,
            end_year=end_year,
            forecast_years=forecast_years,
        )
        self.latest_risk_scores = scores

        self.risk_table.setRowCount(len(scores))

        for row_index, score in enumerate(scores):
            recurrence_text = "∞" if score["recurrence_years"] is None else f"{score['recurrence_years']:.1f}"
            row_values = [
                score["region"],
                str(score["event_count"]),
                f"{score['annual_rate']:.3f}",
                f"%{score['probability'] * 100:.1f}",
                recurrence_text,
                score["risk_level"],
            ]

            for column_index, value in enumerate(row_values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if column_index == 5:
                    risk_color = get_risk_color(score["risk_level"])
                    item.setBackground(QBrush(risk_color))
                    item.setForeground(QBrush(QColor(255, 255, 255)))

                self.risk_table.setItem(row_index, column_index, item)

        if scores:
            highest = scores[0]
            self.risk_indicator.set_risk_data(highest)
            summary = (
                f"Analiz Donemi: {start_year}-{end_year} | "
                f"Esik: Mw≥{min_mag:.1f} | "
                f"Tahmin Ufku: {forecast_years} yil | "
                f"En Yuksek Risk: {highest['region']} (%{highest['risk_score']:.1f})"
            )
        else:
            self.risk_indicator.set_no_data_state()
            summary = "Risk skoru hesaplanamadi. Secilen filtreler icin veri bulunamadi."

        self.lbl_risk_summary.setText(summary)
        print(f"✅ Risk skorları hesaplandı: {len(scores)} bölge")

    def _reset_filter(self):
        self.slider_mag.setValue(30)
        self.slider_start_year.setValue(self.min_year)
        self.slider_end_year.setValue(self.max_year)

        print("🔄 Filtreler sıfırlandı")
        self._apply_filter()

    def _update_map(self, df):
        if df.empty:
            print("⚠️ Gösterilecek deprem verisi yok")
            return

        try:
            map_path = create_earthquake_map(df, self.map_path)
            self.map_widget.load_map(map_path)
            print(f"✅ Harita güncellendi: {len(df)} deprem gösteriliyor")
        except Exception as e:
            print(f"❌ Harita yükleme hatası: {e}")
            import traceback

            traceback.print_exc()

    def _load_initial_map(self):
        print("🗺️ İlk harita yükleniyor (Büyüklük >= 4.0)...")

        filtered_df = self.db.fetch_earthquakes(
            min_mag=4.0,
            max_mag=10.0,
            start_year=self.min_year,
            end_year=self.max_year,
        )

        print(f"[DEBUG] İlk yüklenen DF uzunluğu: {len(filtered_df)}")
        if not filtered_df.empty:
            print(f"[DEBUG] 📊 İlk yüklenen sütunlar: {filtered_df.columns.tolist()}")

        self.current_filtered_df = filtered_df.copy()
        self._set_quake_count(len(filtered_df))
        self.analysis_widget.update_charts(filtered_df)

        if not filtered_df.empty:
            self._update_map(filtered_df)

    def _export_pdf_report(self):
        if not self.latest_risk_scores:
            self._calculate_risk_scores()

        if self.current_filtered_df is None or self.current_filtered_df.empty:
            QMessageBox.warning(self, "Rapor Olusturulamadi", "Rapor icin kullanilabilecek filtrelenmis deprem verisi bulunamadi.")
            return

        default_name = f"terrapulse_analiz_raporu_{self.slider_start_year.value()}_{self.slider_end_year.value()}.pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF Raporunu Kaydet",
            default_name,
            "PDF Files (*.pdf)",
        )

        if not output_path:
            return

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        summary_stats = self._build_report_summary_stats()
        risk_results = self._build_report_risk_results()
        figures = [
            ("Zamana Gore Sismik Aktivite", self.analysis_widget.fig_time),
            ("Buyukluk Frekansi", self.analysis_widget.fig_hist),
            ("Derinlik - Buyukluk Iliskisi", self.analysis_widget.fig_scatter),
        ]

        try:
            saved_path = self.report_manager.generate_report(
                output_path=output_path,
                summary_stats=summary_stats,
                risk_results=risk_results,
                figures=figures,
            )
            QMessageBox.information(self, "Rapor Hazir", f"PDF raporu basariyla kaydedildi.\n\n{saved_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Rapor Hatasi", f"PDF raporu olusturulurken hata olustu:\n{exc}")

    def _open_data_management(self):
        if self.current_user.get("role") != "admin":
            QMessageBox.warning(self, "Yetkisiz Islem", "Bu alana sadece admin kullanicilar erisebilir.")
            return

        dialog = DataManagementDialog(self.db, self)
        dialog.exec()

    def _build_report_summary_stats(self):
        df = self.current_filtered_df.copy()
        selected_regions = []
        if hasattr(self, "combo_region1"):
            region1 = self.combo_region1.currentText()
            if region1 and region1 != "Tüm Türkiye":
                selected_regions.append(region1)
        if hasattr(self, "combo_region2"):
            region2 = self.combo_region2.currentText()
            if region2 and region2 != "Tüm Türkiye" and region2 not in selected_regions:
                selected_regions.append(region2)

        selected_region_label = " / ".join(selected_regions) if selected_regions else "Tum Turkiye"
        start_year = self.slider_start_year.value()
        end_year = self.slider_end_year.value()
        min_magnitude = self.slider_mag.value() / 10.0

        if "time" in df.columns and "date" not in df.columns:
            df = df.rename(columns={"time": "date"})

        largest_earthquake = "-"
        average_depth = "-"
        if not df.empty:
            max_row = df.loc[df["magnitude"].idxmax()]
            place = max_row.get("place", "Bilinmiyor")
            date_value = str(max_row.get("date", max_row.get("time", "N/A")))[:19]
            largest_earthquake = f"M{max_row['magnitude']:.1f} - {place} ({date_value})"

            if "depth" in df.columns and not df["depth"].empty:
                average_depth = f"{df['depth'].mean():.1f} km"

        return {
            "report_scope": f"{selected_region_label} | {start_year}-{end_year}",
            "created_at": self._current_timestamp(),
            "selected_region": selected_region_label,
            "date_range": f"{start_year} - {end_year}",
            "min_magnitude": f"Mw >= {min_magnitude:.1f}",
            "total_earthquakes": len(df),
            "largest_earthquake": largest_earthquake,
            "average_depth": average_depth,
        }

    def _build_report_risk_results(self):
        scores = self.latest_risk_scores or []
        if not scores:
            return {
                "top_risk": {},
                "probability_50y": "-",
                "ranked_regions": [],
            }

        top = scores[0]
        annual_rate = float(top.get("annual_rate", 0.0))
        probability_50y = 1 - math.exp(-annual_rate * 50)

        def _format_recurrence(value):
            if value is None:
                return "Sinirli veri"
            return f"{value:.1f} yil"

        ranked_regions = []
        for row in scores[:5]:
            ranked_regions.append(
                {
                    "region": row.get("region", "-"),
                    "risk_score": f"%{row.get('risk_score', 0.0):.1f}",
                    "risk_level": row.get("risk_level", "-"),
                    "probability": f"%{row.get('probability', 0.0) * 100:.1f}",
                    "recurrence_years": _format_recurrence(row.get("recurrence_years")),
                }
            )

        top_risk = {
            "region": top.get("region", "-"),
            "annual_rate": f"{annual_rate:.3f}",
            "recurrence_years": _format_recurrence(top.get("recurrence_years")),
            "risk_level": top.get("risk_level", "-"),
            "risk_score": f"%{top.get('risk_score', 0.0):.1f}",
        }

        return {
            "top_risk": top_risk,
            "probability_50y": f"%{probability_50y * 100:.1f}",
            "ranked_regions": ranked_regions,
        }

    def _current_timestamp(self):
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def closeEvent(self, event):
        if hasattr(self, "db"):
            self.db.close()
            print("✅ Veritabanı bağlantısı kapatıldı")
        event.accept()
