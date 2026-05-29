import sys
import os

# ------------------------------------------------------------------
# PyInstaller frozen modu icin sys.path ayari
# Hem gelistirici modunda hem de .exe olarak calistiginda
# src/ altindaki modullerin import edilebilmesini saglar.
# ------------------------------------------------------------------
if getattr(sys, "frozen", False):
    # Frozen modda: sys._MEIPASS/src/ dizinini ekle
    _src_dir = os.path.join(sys._MEIPASS, "src")
else:
    # Gelistirici modda: bu dosyanin bulundugu dizini ekle (src/)
    _src_dir = os.path.dirname(os.path.abspath(__file__))

if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from PyQt6.QtWidgets import QApplication, QDialog
from ui.main_window import MainWindow
from ui.login_window import LoginDialog

def main():
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    window = MainWindow(current_user=login_dialog.authenticated_user)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
