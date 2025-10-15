from PySide6 import QtWidgets, QtCore


class NoArrowSpinBox(QtWidgets.QSpinBox):
    """无上下箭头的 SpinBox"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)


class AddRepeatTaskDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加重复任务")
        self.setFixedSize(400, 280)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
                font-weight: 500;
                font-size: 13px;
                background: transparent;
            }
            QLineEdit {
                background: rgba(255,255,255,0.06);
                color: #e6eef8;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.1);
            }
            QSpinBox {
                background: rgba(255,255,255,0.06);
                color: #e6eef8;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
            }
            QSpinBox:focus {
                border: 1px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.1);
            }
            QPushButton {
                background-color: rgba(255,255,255,0.1);
                color: #e6eef8;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
            }
            QPushButton:pressed {
                background-color: rgba(255,255,255,0.25);
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(12)

        # 任务名称
        name_label = QtWidgets.QLabel("任务名称")
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("请输入任务名称")

        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # 每次完成经验奖励
        xp_label = QtWidgets.QLabel("每次完成经验奖励")
        self.xp_spin = NoArrowSpinBox()
        self.xp_spin.setRange(1, 10000)
        self.xp_spin.setValue(10)
        self.xp_spin.setSuffix(" XP")

        layout.addWidget(xp_label)
        layout.addWidget(self.xp_spin)

        # 最大完成次数
        max_layout = QtWidgets.QHBoxLayout()
        max_label = QtWidgets.QLabel("最大完成次数")
        self.max_completions_spin = NoArrowSpinBox()
        self.max_completions_spin.setRange(0, 1000)
        self.max_completions_spin.setValue(0)
        self.max_completions_spin.setSpecialValueText("无限")

        max_layout.addWidget(max_label)
        max_layout.addWidget(self.max_completions_spin)
        layout.addLayout(max_layout)

        # 提示信息
        info_label = QtWidgets.QLabel("提示：设置为 0 表示可以无限次完成")
        info_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        layout.addWidget(info_label)

        # 按钮
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)
        ok = QtWidgets.QPushButton("添加")
        cancel = QtWidgets.QPushButton("取消")
        ok.setMinimumWidth(100)
        cancel.setMinimumWidth(100)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(ok)
        btn_layout.addWidget(cancel)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        return (
            self.name_edit.text().strip(),
            self.xp_spin.value(),
            self.max_completions_spin.value()
        )


# 直接运行测试
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dlg = AddRepeatTaskDialog()
    if dlg.exec() == QtWidgets.QDialog.Accepted:
        print(dlg.get_data())
