import os
import sys
from PySide6 import QtWidgets, QtGui


from repeat_tasks import init_repeat_tasks
from window import MainWindow
from db import init_db
from style import STYLE


def main():
    init_db()
    init_repeat_tasks()

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setWindowIcon(QtGui.QIcon("icon.ico"))

    win = MainWindow()
    win.show()
    win.on_tab_changed(win.tab_widget.currentIndex())
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
