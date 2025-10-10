import sys
from PySide6 import QtWidgets
from window import MainWindow
from db import init_db
from style import STYLE

def main():
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    win = MainWindow()
    win.show()
    win.on_tab_changed(win.tab_widget.currentIndex())
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
