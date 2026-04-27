"""TerraPulse icin paylasilan UI bilesenleri ve tema yardimcilari."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def _apply_shadow(widget: QWidget, blur: int = 24, y_offset: int = 10, alpha: int = 60):
    """Kartlara yumusak koyu golge uygula."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(2, 6, 23, alpha))
    widget.setGraphicsEffect(shadow)
    return shadow


def build_app_stylesheet() -> str:
    """Tum uygulama icin dark mode tema."""
    return """
    QMainWindow {
        background: #08111f;
    }

    QWidget {
        background: transparent;
        color: #e5edf7;
        font-size: 13px;
    }

    QWidget#AppShell,
    QWidget#TabPage {
        background: #08111f;
    }

    QWidget#AppHeader {
        background: #0d1729;
        border: 1px solid #1b2a40;
        border-radius: 14px;
    }

    QLabel#HeaderTitle {
        font-size: 24px;
        font-weight: 800;
        color: #f8fbff;
    }

    QLabel#HeaderSubtitle {
        font-size: 12px;
        color: #8ea2bd;
    }

    QLabel#SectionTitle {
        font-size: 18px;
        font-weight: 800;
        color: #f8fbff;
    }

    QLabel#SectionSubtitle {
        font-size: 12px;
        color: #8ea2bd;
    }

    QLabel#CardTitle {
        font-size: 14px;
        font-weight: 700;
        color: #f8fbff;
    }

    QLabel#CardSubtitle {
        font-size: 11px;
        color: #8195b0;
    }

    QLabel#FieldLabel {
        font-size: 11px;
        font-weight: 700;
        color: #91a4bc;
    }

    QLabel#MetricValue {
        font-size: 24px;
        font-weight: 800;
        color: #f8fbff;
    }

    QLabel#MetricCaption {
        font-size: 11px;
        color: #8195b0;
        font-weight: 700;
    }

    QLabel#TagChip {
        border-radius: 13px;
        padding: 5px 11px;
        font-size: 11px;
        font-weight: 700;
    }

    QLabel#TagChip[chipTone="neutral"] {
        background: #132239;
        color: #b5c7dd;
        border: 1px solid #253653;
    }

    QLabel#TagChip[chipTone="accent"] {
        background: #0f2b2d;
        color: #5ce1d1;
        border: 1px solid #1e5755;
    }

    QLabel#TagChip[chipTone="info"] {
        background: #102340;
        color: #74a7ff;
        border: 1px solid #27467a;
    }

    QLabel#TagChip[chipTone="success"] {
        background: #10291d;
        color: #74d99f;
        border: 1px solid #1d5a37;
    }

    QLabel#TagChip[chipTone="warning"] {
        background: #32220d;
        color: #ffce73;
        border: 1px solid #73511b;
    }

    QLabel#TagChip[chipTone="danger"] {
        background: #321217;
        color: #ff8c97;
        border: 1px solid #6a2430;
    }

    QFrame[cardRole="surface"],
    QFrame[cardRole="hero"] {
        background: #0d1729;
        border: 1px solid #1b2a40;
        border-radius: 16px;
    }

    QFrame[cardRole="muted"] {
        background: #101c31;
        border: 1px solid #20314c;
        border-radius: 16px;
    }

    QTabWidget::pane {
        border: none;
        top: -1px;
    }

    QTabBar::tab {
        background: #0d1729;
        color: #8ea2bd;
        border: 1px solid #1b2a40;
        border-bottom: none;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        padding: 10px 16px;
        margin-right: 8px;
        min-width: 156px;
        font-weight: 700;
    }

    QTabBar::tab:selected {
        background: #13213a;
        color: #f8fbff;
        border-color: #2a446d;
    }

    QTabBar::tab:hover:!selected {
        background: #10203a;
        color: #c2d1e4;
    }

    QPushButton {
        background: #0f766e;
        color: #f8fbff;
        border: 1px solid #15968b;
        border-radius: 10px;
        padding: 8px 14px;
        min-height: 16px;
        font-weight: 700;
    }

    QPushButton:hover {
        background: #129084;
    }

    QPushButton:pressed {
        background: #0b5f57;
    }

    QPushButton[variant="secondary"] {
        background: #132239;
        color: #d9e6f5;
        border: 1px solid #243755;
    }

    QPushButton[variant="secondary"]:hover {
        background: #182a46;
        border-color: #32517a;
    }

    QPushButton[variant="secondary"]:pressed {
        background: #10203a;
    }

    QPushButton:disabled {
        background: #101a2c;
        color: #61738b;
        border-color: #1d2c43;
    }

    QComboBox,
    QSpinBox {
        background: #08111f;
        color: #e5edf7;
        border: 1px solid #243755;
        border-radius: 10px;
        padding: 7px 11px;
        min-height: 18px;
    }

    QComboBox:hover,
    QSpinBox:hover {
        border-color: #32517a;
    }

    QComboBox:focus,
    QSpinBox:focus {
        border: 1px solid #1ba8a0;
    }

    QComboBox::drop-down {
        border: none;
        width: 24px;
    }

    QSpinBox::up-button,
    QSpinBox::down-button {
        border: none;
        width: 20px;
    }

    QComboBox QAbstractItemView {
        background: #0d1729;
        color: #e5edf7;
        border: 1px solid #243755;
        selection-background-color: #123a52;
        selection-color: #f8fbff;
        outline: 0;
    }

    QSlider::groove:horizontal {
        height: 8px;
        border-radius: 4px;
        background: #16243c;
    }

    QSlider::sub-page:horizontal {
        border-radius: 4px;
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #14b8a6,
            stop:1 #2563eb
        );
    }

    QSlider::handle:horizontal {
        width: 16px;
        margin: -5px 0;
        border-radius: 8px;
        background: #f8fbff;
        border: 2px solid #14b8a6;
    }

    QSlider::handle:horizontal:hover {
        border-color: #60a5fa;
    }

    QTableWidget {
        background: #0a1324;
        color: #e5edf7;
        border: 1px solid #1b2a40;
        border-radius: 16px;
        gridline-color: #18263d;
        alternate-background-color: #0d1729;
        selection-background-color: #123a52;
        selection-color: #f8fbff;
    }

    QHeaderView::section {
        background: #101c31;
        color: #b5c7dd;
        border: none;
        border-bottom: 1px solid #1f314e;
        padding: 10px 8px;
        font-size: 11px;
        font-weight: 800;
    }

    QTableCornerButton::section {
        background: #101c31;
        border: none;
        border-bottom: 1px solid #1f314e;
        border-right: 1px solid #1f314e;
    }

    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #18263d;
    }

    QSplitter::handle {
        background: transparent;
    }

    QSplitter::handle:horizontal {
        width: 10px;
    }

    QSplitter::handle:vertical {
        height: 10px;
    }

    QScrollBar:vertical {
        background: transparent;
        width: 10px;
        margin: 3px 0 3px 0;
    }

    QScrollBar::handle:vertical {
        background: #2a3c59;
        min-height: 36px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background: #385279;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: transparent;
        height: 0px;
    }

    QToolTip {
        background: #0d1729;
        color: #f8fbff;
        border: 1px solid #243755;
        padding: 6px 8px;
    }
    """


class TagChip(QLabel):
    """Kucuk, okunakli bilgi etiketi."""

    def __init__(self, text: str, tone: str = "neutral", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName("TagChip")
        self.setProperty("chipTone", tone)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


class PageHeader(QWidget):
    """Sayfa basligi ve yardimci etiketleri."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        chips: list[tuple[str, str]] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("PageHeader")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("SectionTitle")

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("SectionSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setMaximumHeight(36)

        text_column.addWidget(self.title_label)
        text_column.addWidget(self.subtitle_label)

        layout.addLayout(text_column, 1)

        if chips:
            chip_row = QHBoxLayout()
            chip_row.setContentsMargins(0, 0, 0, 0)
            chip_row.setSpacing(8)
            chip_row.addStretch()

            for chip_text, tone in chips:
                chip_row.addWidget(TagChip(chip_text, tone))

            layout.addLayout(chip_row, 0)


class SurfaceCard(QFrame):
    """Ortak yuzey paneli."""

    def __init__(
        self,
        role: str = "surface",
        padding: int = 18,
        spacing: int = 12,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setProperty("cardRole", role)
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(padding, padding, padding, padding)
        self.content_layout.setSpacing(spacing)
        _apply_shadow(self)


def _risk_palette(score: float) -> tuple[str, str, str]:
    """Skora gore vurgu, yumusak arka plan ve koyu metin rengi."""
    if score <= 33:
        return ("#22c55e", "#10291d", "#74d99f")
    if score <= 66:
        return ("#f59e0b", "#32220d", "#ffce73")
    return ("#ef4444", "#321217", "#ff8c97")


def _risk_label(score: float) -> str:
    """Sayisal skoru kolay okunur risk etiketine cevir."""
    if score <= 33:
        return "Dusuk Risk"
    if score <= 66:
        return "Orta Risk"
    return "Yuksek Risk"


class RiskIndicatorWidget(SurfaceCard):
    """Poisson tabanli deprem riskini one cikaran ozet panel."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(role="hero", padding=18, spacing=14, parent=parent)
        self.setMinimumHeight(168)
        self.setMaximumHeight(210)
        self._build_ui()
        self.set_no_data_state()

    def _build_ui(self):
        header = QHBoxLayout()
        header.setSpacing(12)

        self.icon_badge = QLabel("λ")
        self.icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_badge.setFixedSize(46, 46)
        self.icon_badge.setStyleSheet(
            """
            QLabel {
                border-radius: 23px;
                background: #132239;
                color: #f8fbff;
                font-size: 22px;
                font-weight: 800;
                border: 1px solid #243755;
            }
            """
        )

        title_column = QVBoxLayout()
        title_column.setSpacing(2)

        self.title_label = QLabel("Risk Skorlama Paneli")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 800; color: #f8fbff;")

        self.subtitle_label = QLabel("Poisson dagilimi ile bolgesel risk ozetini hizli okuyun.")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setMaximumHeight(32)
        self.subtitle_label.setStyleSheet("font-size: 11px; color: #8ea2bd;")

        title_column.addWidget(self.title_label)
        title_column.addWidget(self.subtitle_label)

        self.status_badge = TagChip("Hazir", "neutral")
        self.status_badge.setMinimumWidth(104)

        header.addWidget(self.icon_badge, 0, Qt.AlignmentFlag.AlignTop)
        header.addLayout(title_column, 1)
        header.addWidget(self.status_badge, 0, Qt.AlignmentFlag.AlignTop)
        self.content_layout.addLayout(header)

        score_row = QHBoxLayout()
        score_row.setSpacing(16)

        score_column = QVBoxLayout()
        score_column.setSpacing(2)

        self.score_label = QLabel("--")
        score_font = QFont()
        score_font.setPointSize(28)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        self.score_label.setStyleSheet("color: #f8fbff;")

        self.score_caption = QLabel("Genel Risk Skoru")
        self.score_caption.setStyleSheet("font-size: 11px; color: #8ea2bd; font-weight: 700;")

        score_column.addWidget(self.score_label)
        score_column.addWidget(self.score_caption)
        score_column.addStretch()

        detail_column = QVBoxLayout()
        detail_column.setSpacing(8)

        self.risk_description = QLabel("Risk skoru hesaplandiginda burada donem ve bolge ozeti gorunur.")
        self.risk_description.setWordWrap(True)
        self.risk_description.setStyleSheet("font-size: 12px; color: #b5c7dd; font-weight: 600;")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(14)
        self.progress.setStyleSheet(
            """
            QProgressBar {
                border: none;
                border-radius: 7px;
                background: #16243c;
            }
            QProgressBar::chunk {
                border-radius: 7px;
                background: #22c55e;
            }
            """
        )

        detail_column.addWidget(self.risk_description)
        detail_column.addWidget(self.progress)
        score_row.addLayout(score_column, 2)
        score_row.addLayout(detail_column, 3)
        self.content_layout.addLayout(score_row)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(14)

        self.info_probability = self._create_metric_column("Poisson Olasiligi")
        self.info_recurrence = self._create_metric_column("Tekrarlanma Periyodu")
        self.info_region = self._create_metric_column("En Riskli Bolge")

        metrics_row.addWidget(self.info_probability, 1)
        metrics_row.addWidget(self._create_divider())
        metrics_row.addWidget(self.info_recurrence, 1)
        metrics_row.addWidget(self._create_divider())
        metrics_row.addWidget(self.info_region, 1)

        self.content_layout.addLayout(metrics_row)

    def _create_divider(self) -> QFrame:
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("color: #1f314e;")
        return divider

    def _create_metric_column(self, title: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10px; color: #8195b0; font-weight: 700;")

        value_label = QLabel("--")
        value_label.setWordWrap(True)
        value_label.setStyleSheet("font-size: 14px; color: #f8fbff; font-weight: 800;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        widget.title_label = title_label
        widget.value_label = value_label
        return widget

    def set_no_data_state(self):
        """Paneli notr baslangic gorunumune al."""
        self._apply_theme(0)
        self.score_label.setText("--")
        self.status_badge.setText("Hazir")
        self.risk_description.setText("Risk skoru hesaplandiginda burada donem ve bolge ozeti gorunur.")
        self.progress.setValue(0)
        self.info_probability.value_label.setText("--")
        self.info_recurrence.value_label.setText("--")
        self.info_region.value_label.setText("--")

    def set_risk_data(self, score_data: dict):
        """Hesaplanan risk verisini gorsel ozet paneline yansit."""
        score = float(score_data.get("risk_score", 0.0))
        region = score_data.get("region", "Bilinmiyor")
        probability = float(score_data.get("probability", 0.0))
        recurrence_years = score_data.get("recurrence_years")
        event_count = score_data.get("event_count", 0)
        analysis_years = score_data.get("analysis_years", 0)
        forecast_years = score_data.get("forecast_years", 1)

        self._apply_theme(score)
        self.score_label.setText(f"{score:.1f}")
        self.status_badge.setText(_risk_label(score))
        self.progress.setValue(int(round(score)))

        if recurrence_years is None:
            recurrence_text = "Sinirli veri"
        else:
            recurrence_text = f"{recurrence_years:.1f} yil"

        self.risk_description.setText(
            f"{region} icin {analysis_years} yillik gecmise gore {forecast_years} yillik risk ongorusu olusturuldu."
        )
        self.info_probability.value_label.setText(f"%{probability * 100:.1f}")
        self.info_recurrence.value_label.setText(recurrence_text)
        self.info_region.value_label.setText(f"{region} · {event_count} kayit")

    def _apply_theme(self, score: float):
        main_color, soft_color, dark_color = _risk_palette(score)
        tone = "success" if score <= 33 else "warning" if score <= 66 else "danger"

        self.status_badge.setProperty("chipTone", tone)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

        self.icon_badge.setStyleSheet(
            f"""
            QLabel {{
                border-radius: 23px;
                background: {soft_color};
                color: {dark_color};
                font-size: 22px;
                font-weight: 800;
                border: 1px solid {soft_color};
            }}
            """
        )

        self.score_label.setStyleSheet(f"color: {main_color};")
        self.progress.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                border-radius: 7px;
                background: #16243c;
            }}
            QProgressBar::chunk {{
                border-radius: 7px;
                background: {main_color};
            }}
            """
        )
