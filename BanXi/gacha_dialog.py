from PySide6 import QtWidgets, QtCore


class AddGachaItemDialog(QtWidgets.QDialog):
    """
    添加抽卡奖品对话框

    用于管理抽卡系统的奖品配置
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加抽卡奖品")
        self.setFixedSize(400, 300)
        layout = QtWidgets.QVBoxLayout()

        # 奖品名称输入
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("奖品名称")
        layout.addWidget(QtWidgets.QLabel("奖品名称"))
        layout.addWidget(self.name_edit)

        # 星级选择下拉框
        layout.addWidget(QtWidgets.QLabel("星级"))
        self.star_combo = QtWidgets.QComboBox()
        self.star_combo.addItems(["三星", "四星", "五星", "六星"])
        layout.addWidget(self.star_combo)

        # 描述输入框
        self.desc_edit = QtWidgets.QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setPlaceholderText("奖品描述（可选）")
        layout.addWidget(QtWidgets.QLabel("奖品描述"))
        layout.addWidget(self.desc_edit)

        # 星级颜色预览
        preview_layout = QtWidgets.QHBoxLayout()
        preview_layout.addWidget(QtWidgets.QLabel("星级颜色预览:"))
        self.star_preview = QtWidgets.QLabel()
        self.star_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.star_preview.setFixedSize(100, 30)
        self.update_star_preview()  # 初始化预览
        preview_layout.addWidget(self.star_preview)
        preview_layout.addStretch()
        layout.addLayout(preview_layout)

        # 星级改变时更新预览
        self.star_combo.currentIndexChanged.connect(self.update_star_preview)

        # 按钮区域
        btns = QtWidgets.QHBoxLayout()
        ok = QtWidgets.QPushButton("添加")
        cancel = QtWidgets.QPushButton("取消")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)

        self.setLayout(layout)

    def update_star_preview(self):
        """
        根据选择的星级更新颜色预览

        不同星级对应不同颜色主题：
        - 三星：蓝色
        - 四星：紫色
        - 五星：橙色
        - 六星：红色
        """
        star_colors = {
            0: ("蓝色", "color: #4FC3F7; background: rgba(79, 195, 247, 0.2); border: 1px solid #4FC3F7;"),
            1: ("紫色", "color: #BA68C8; background: rgba(186, 104, 200, 0.2); border: 1px solid #BA68C8;"),
            2: ("橙色", "color: #FFB74D; background: rgba(255, 183, 77, 0.2); border: 1px solid #FFB74D;"),
            3: ("红色", "color: #FF6B6B; background: rgba(255, 107, 107, 0.2); border: 1px solid #FF6B6B;")
        }

        current_index = self.star_combo.currentIndex()
        text, style = star_colors[current_index]
        self.star_preview.setText(f"{self.star_combo.currentText()} - {text}")
        self.star_preview.setStyleSheet(f"border-radius: 5px; padding: 5px; {style}")

    def get_data(self):
        """
        获取用户输入的奖品数据

        返回:
            tuple: (奖品名称, 星级数值, 描述)
        """
        star_mapping = {"三星": 3, "四星": 4, "五星": 5, "六星": 6}
        star = star_mapping[self.star_combo.currentText()]
        return (
            self.name_edit.text().strip(),
            star,
            self.desc_edit.toPlainText().strip()
        )