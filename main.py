from PySide6.QtWidgets import QApplication

from ticker_sandbox_qt import Sandbox

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    sandbox = Sandbox()
    sandbox.show()
    sys.exit(app.exec())