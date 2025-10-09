from PySide6 import QtWidgets

class AddTaskDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新任务")
        self.setFixedSize(320, 160)
        layout = QtWidgets.QVBoxLayout()
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("任务名称")
        self.xp_spin = QtWidgets.QSpinBox()
        self.xp_spin.setRange(1, 10000)
        self.xp_spin.setValue(10)
        self.xp_spin.setSuffix(" XP")
        layout.addWidget(QtWidgets.QLabel("任务名称"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QtWidgets.QLabel("经验奖励"))
        layout.addWidget(self.xp_spin)
        btns = QtWidgets.QHBoxLayout()
        ok = QtWidgets.QPushButton("添加")
        cancel = QtWidgets.QPushButton("取消")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def get_data(self):
        return self.name_edit.text().strip(), self.xp_spin.value()

class AddShopDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新商品")
        self.setFixedSize(320, 160)
        layout = QtWidgets.QVBoxLayout()
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("商品名称")
        self.price_spin = QtWidgets.QSpinBox()
        self.price_spin.setRange(1, 100000)
        self.price_spin.setValue(100)
        self.price_spin.setSuffix(" coins")
        layout.addWidget(QtWidgets.QLabel("商品名称"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QtWidgets.QLabel("价格"))
        layout.addWidget(self.price_spin)
        btns = QtWidgets.QHBoxLayout()
        ok = QtWidgets.QPushButton("添加")
        cancel = QtWidgets.QPushButton("取消")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def get_data(self):
        return self.name_edit.text().strip(), self.price_spin.value()
