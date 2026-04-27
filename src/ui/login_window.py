import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DBManager


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DBManager()
        self.authenticated_user = None
        self._login_in_progress = False
        self._password_visible = False

        icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        self.eye_icon = QIcon(os.path.join(icons_dir, "eye.svg"))
        self.eye_off_icon = QIcon(os.path.join(icons_dir, "eye_off.svg"))

        self.setWindowTitle("TerraPulse Kurumsal Giriş")
        self.setModal(True)
        self.setMinimumSize(480, 560)
        self.resize(500, 580)

        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 28, 28, 28)

        card = QFrame()
        card.setObjectName("LoginCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 28)
        card_layout.setSpacing(18)

        brand_badge = QLabel("TP")
        brand_badge.setObjectName("BrandBadge")
        brand_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_badge.setFixedSize(64, 64)

        badge_row = QHBoxLayout()
        badge_row.addStretch()
        badge_row.addWidget(brand_badge)
        badge_row.addStretch()

        title_label = QLabel("TerraPulse Kurumsal Giriş")
        title_label.setObjectName("LoginTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel(
            "Sismik analiz paneline erişmek için kullanıcı bilgilerinizle oturum açın."
        )
        subtitle_label.setObjectName("LoginSubtitle")
        subtitle_label.setWordWrap(True)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFixedHeight(52)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setVisible(False)
        self.status_label.setWordWrap(True)
        self.status_label.setFixedHeight(0)

        form_wrap = QWidget()
        form_layout = QVBoxLayout(form_wrap)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(14)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı adı")
        self.username_input.setClearButtonEnabled(True)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_toggle_action = self.password_input.addAction(
            self.eye_icon,
            QLineEdit.ActionPosition.TrailingPosition,
        )
        self.password_toggle_action.triggered.connect(self._toggle_password_visibility)

        form_layout.addWidget(self._build_field("Kullanıcı Adı", self.username_input))
        form_layout.addWidget(self._build_field("Şifre", self.password_input))

        self.btn_login = QPushButton("Giriş Yap")
        self.btn_login.setObjectName("PrimaryButton")
        self.btn_login.setDefault(True)
        self.btn_login.setAutoDefault(True)
        self.btn_login.clicked.connect(self._attempt_login)

        self.btn_cancel = QPushButton("Vazgeç")
        self.btn_cancel.setObjectName("GhostButton")
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.clicked.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addWidget(self.btn_cancel)
        button_row.addWidget(self.btn_login)

        helper_label = QLabel(
            "Rol tabanlı erişim aktiftir. Admin kullanıcıları veri yönetimi aracını görebilir."
        )
        helper_label.setObjectName("HelperText")
        helper_label.setWordWrap(True)
        helper_label.setFixedHeight(42)

        card_layout.addLayout(badge_row)
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(form_wrap)
        card_layout.addSpacing(4)
        card_layout.addLayout(button_row)
        card_layout.addWidget(helper_label)

        root_layout.addWidget(card)

        self.username_input.setFocus()

    def _build_field(self, label_text: str, field: QWidget):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(label_text)
        label.setObjectName("FieldLabel")

        layout.addWidget(label)
        layout.addWidget(field)
        return wrapper

    def _apply_styles(self):
        self.setStyleSheet(
            """
            QDialog {
                background: #07111f;
            }
            #LoginCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #0d1b2a, stop:1 #13263b);
                border: 1px solid rgba(125, 211, 252, 0.22);
                border-radius: 18px;
            }
            #BrandBadge {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #38bdf8, stop:1 #0ea5e9);
                color: #e0f2fe;
                font-size: 24px;
                font-weight: 700;
                border-radius: 32px;
            }
            #LoginTitle {
                color: #f8fafc;
                font-size: 24px;
                font-weight: 700;
            }
            #LoginSubtitle {
                color: #9fb6cf;
                font-size: 13px;
                line-height: 1.4;
            }
            #FieldLabel {
                color: #d5e6f8;
                font-size: 12px;
                font-weight: 600;
            }
            QLineEdit {
                min-height: 44px;
                padding: 0 14px;
                border-radius: 12px;
                border: 1px solid #27415d;
                background: #081522;
                color: #f8fafc;
                selection-background-color: #0ea5e9;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #38bdf8;
                background: #0a1827;
            }
            #PrimaryButton, #GhostButton {
                min-height: 44px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 18px;
            }
            #PrimaryButton {
                border: none;
                background: #0ea5e9;
                color: #f8fafc;
            }
            #PrimaryButton:hover {
                background: #38bdf8;
            }
            #GhostButton {
                border: 1px solid #30465f;
                background: transparent;
                color: #dbeafe;
            }
            #GhostButton:hover {
                background: rgba(148, 163, 184, 0.10);
            }
            #StatusLabel {
                border-radius: 10px;
                padding: 10px 12px;
                background: rgba(248, 113, 113, 0.12);
                border: 1px solid rgba(248, 113, 113, 0.28);
                color: #fecaca;
                font-size: 12px;
                font-weight: 600;
            }
            #HelperText {
                color: #7f98b6;
                font-size: 12px;
            }
            """
        )

    def _attempt_login(self):
        if self._login_in_progress:
            return

        self._login_in_progress = True
        username = self.username_input.text().strip()
        password = self.password_input.text()

        try:
            if not username or not password:
                QMessageBox.warning(self, "Eksik Bilgi", "Lutfen kullanici adi ve sifre alanlarini doldurun.")
                return

            if self.db.get_user_count() == 0:
                QMessageBox.warning(
                    self,
                    "Kullanici Bulunamadi",
                    "users tablosunda kayit bulunamadi. Once varsayilan kullanici SQL scriptini calistirin.",
                )
                return

            user = self.db.authenticate_user(username, password)
            if not user:
                QMessageBox.warning(self, "Giris Hatasi", "Gecersiz kullanici adi veya sifre!")
                self.password_input.clear()
                self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
                self._password_visible = False
                self.password_toggle_action.setIcon(self.eye_icon)
                self.password_input.setFocus()
                return

            self.authenticated_user = user
            self.accept()
        finally:
            self._login_in_progress = False

    def _set_status(self, message: str):
        self.status_label.setText(message)
        self.status_label.setVisible(True)

    def _toggle_password_visibility(self):
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.password_toggle_action.setIcon(self.eye_off_icon)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_toggle_action.setIcon(self.eye_icon)

    def done(self, result: int):
        if hasattr(self, "db") and self.db:
            self.db.close()
        super().done(result)
