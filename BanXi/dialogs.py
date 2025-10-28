from PySide6 import QtWidgets, QtCore, QtGui


class ValidatedLineEdit(QtWidgets.QLineEdit):
    """
    带验证功能的输入框
    """

    def __init__(self, placeholder="", validator=None, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)

        if validator:
            self.setValidator(validator)

        self.textChanged.connect(self.clear_error_style)

    def set_error_style(self, has_error):
        if has_error:
            self.setStyleSheet("border: 1px solid #ff6b6b; background: rgba(255,107,107,0.1);")
        else:
            self.setStyleSheet("")

    def clear_error_style(self):
        self.set_error_style(False)

    def validate(self):
        text = self.text().strip()
        if not text:
            return False, "此项不能为空"
        return True, ""


class BaseDialog(QtWidgets.QDialog):
    """
    基础对话框类
    """

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.setStyleSheet("""
            QDialog {
                background: #0f1720;
                color: #e6eef8;
                font-family: "Segoe UI", "Microsoft YaHei", Arial;
                font-size: 12px;
            }
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: #e6eef8;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.3);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.05);
            }
        """)

        self.setup_enter_key()

    def setup_enter_key(self):
        self.enter_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Return"), self)
        self.enter_shortcut.activated.connect(self.on_enter_pressed)
        self.escape_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self.reject)

    def on_enter_pressed(self):
        if self.validate_inputs():
            self.accept()

    def validate_inputs(self):
        return True

    def show_error(self, message, widget=None):
        if widget and hasattr(widget, 'set_error_style'):
            widget.set_error_style(True)
        QtWidgets.QMessageBox.warning(self, "输入错误", message)

    def set_initial_focus(self, widget):
        QtCore.QTimer.singleShot(100, lambda: widget.setFocus())


class NoArrowSpinBox(QtWidgets.QSpinBox):
    """无上下箭头的 SpinBox"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)


class AddTaskDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新任务")
        self.setFixedSize(400, 300)
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

        # 经验奖励
        xp_label = QtWidgets.QLabel("经验奖励")
        self.xp_spin = NoArrowSpinBox()
        self.xp_spin.setRange(1, 10000)
        self.xp_spin.setValue(10)
        self.xp_spin.setSuffix(" XP")

        layout.addWidget(xp_label)
        layout.addWidget(self.xp_spin)

        # 铂金币奖励
        platinum_label = QtWidgets.QLabel("铂金币奖励（可选）")
        self.platinum_spin = NoArrowSpinBox()
        self.platinum_spin.setRange(0, 100)
        self.platinum_spin.setValue(0)
        self.platinum_spin.setSuffix(" 铂金币")
        self.platinum_spin.setSpecialValueText("无")

        layout.addWidget(platinum_label)
        layout.addWidget(self.platinum_spin)

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
            self.platinum_spin.value()
        )

class AddRewardDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新奖励")
        self.setFixedSize(400, 320)
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
            QComboBox {
                background: rgba(255,255,255,0.06);
                color: #e6eef8;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 1px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.1);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
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

        # 奖励名称
        name_label = QtWidgets.QLabel("奖励名称")
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("请输入奖励名称")

        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # 货币类型选择
        currency_label = QtWidgets.QLabel("货币类型")
        self.currency_combo = QtWidgets.QComboBox()
        self.currency_combo.addItem("金币", "coins")
        self.currency_combo.addItem("铂金币", "platinum")
        self.currency_combo.currentTextChanged.connect(self.on_currency_changed)

        layout.addWidget(currency_label)
        layout.addWidget(self.currency_combo)

        # 所需货币数量
        self.price_label = QtWidgets.QLabel("所需金币")
        self.price_spin = NoArrowSpinBox()
        self.price_spin.setRange(1, 100000)
        self.price_spin.setValue(100)
        self.price_spin.setSuffix(" coins")

        layout.addWidget(self.price_label)
        layout.addWidget(self.price_spin)

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

    def on_currency_changed(self, text):
        """当货币类型改变时更新标签和后缀"""
        if text == "铂金币":
            self.price_label.setText("所需铂金币")
            self.price_spin.setSuffix(" 铂金币")
            self.price_spin.setRange(1, 1000)  # 铂金币范围较小
            self.price_spin.setValue(1)
        else:
            self.price_label.setText("所需金币")
            self.price_spin.setSuffix(" coins")
            self.price_spin.setRange(1, 100000)
            self.price_spin.setValue(100)

    def get_data(self):
        currency_type = self.currency_combo.currentData()
        return (
            self.name_edit.text().strip(),
            self.price_spin.value(),
            currency_type
        )

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # 测试任务对话框
    task_dialog = AddTaskDialog()
    if task_dialog.exec():
        name, xp = task_dialog.get_data()
        print(f"添加任务: {name}, XP: {xp}")

    # 测试奖励对话框
    reward_dialog = AddRewardDialog()
    if reward_dialog.exec():
        name, price, currency_type = reward_dialog.get_data()
        print(f"添加奖励: {name}, 价格: {price}, 货币类型: {currency_type}")

    sys.exit()
