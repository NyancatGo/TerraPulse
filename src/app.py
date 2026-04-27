import sys
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
