from PySide6 import QtWidgets, QtCore
from db import get_db_connection  # 添加导入


class NoArrowSpinBox(QtWidgets.QSpinBox):
    """无上下箭头的 SpinBox"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)


class AddRepeatTaskDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加重复任务")
        self.setFixedSize(400, 340)
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

        # 铂金币奖励
        platinum_label = QtWidgets.QLabel("每次完成铂金币奖励（可选）")
        self.platinum_spin = NoArrowSpinBox()
        self.platinum_spin.setRange(0, 100)
        self.platinum_spin.setValue(0)
        self.platinum_spin.setSuffix(" 铂金币")
        self.platinum_spin.setSpecialValueText("无")

        layout.addWidget(platinum_label)
        layout.addWidget(self.platinum_spin)

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
            self.max_completions_spin.value(),
            self.platinum_spin.value()
        )


class CompleteMultipleTimesDialog(QtWidgets.QDialog):
    def __init__(self, task_name, task_id, current_completions, max_completions, parent=None):
        super().__init__(parent)
        self.task_name = task_name
        self.task_id = task_id  # 保存任务ID
        self.current_completions = current_completions
        self.max_completions = max_completions
        self.xp_reward, self.platinum_reward = self.get_task_rewards()  # 从数据库获取奖励信息
        self.setWindowTitle("多次完成任务")
        self.setFixedSize(400, 200)
        self.setup_ui()

    def get_task_rewards(self):
        """从数据库获取任务的奖励信息（经验和铂金币）"""
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT xp_reward, platinum_reward FROM repeat_tasks WHERE id=?", (self.task_id,))
        result = c.fetchone()
        conn.close()

        if result:
            return result[0], result[1]  # 返回 (xp_reward, platinum_reward)
        else:
            return 10, 0  # 默认值，如果找不到任务

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(12)

        # 任务信息
        info_text = f"任务: {self.task_name}\n"
        info_text += f"当前完成: {self.current_completions}"
        if self.max_completions > 0:
            info_text += f" / {self.max_completions}"
        else:
            info_text += " 次"
        # 构建奖励信息，包含铂金币
        reward_text = f"{self.xp_reward} XP"
        if self.platinum_reward > 0:
            reward_text += f" + {self.platinum_reward} 铂金币"
        info_text += f"\n每次奖励: {reward_text}"

        info_label = QtWidgets.QLabel(info_text)
        info_label.setStyleSheet("color: #e6eef8; font-size: 13px;")
        layout.addWidget(info_label)

        # 输入完成次数
        count_label = QtWidgets.QLabel("完成次数:")
        self.count_spin = NoArrowSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(1)

        count_layout = QtWidgets.QHBoxLayout()
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_spin)
        layout.addLayout(count_layout)

        # 最大可完成次数提示
        if self.max_completions > 0:
            max_available = self.max_completions - self.current_completions
            if max_available > 0:
                hint_label = QtWidgets.QLabel(f"提示: 最多还可完成 {max_available} 次")
                hint_label.setStyleSheet("color: #FFD166; font-size: 11px;")
                layout.addWidget(hint_label)
                self.count_spin.setRange(1, max_available)
            else:
                hint_label = QtWidgets.QLabel("提示: 任务已达到最大完成次数")
                hint_label.setStyleSheet("color: #FF6B6B; font-size: 11px;")
                layout.addWidget(hint_label)
                self.count_spin.setEnabled(False)

        # 预计奖励信息
        self.reward_label = QtWidgets.QLabel("")
        self.reward_label.setStyleSheet("color: #66BB6A; font-size: 12px;")
        layout.addWidget(self.reward_label)

        # 按钮
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("确认完成")
        cancel_btn = QtWidgets.QPushButton("取消")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # 连接信号，实时更新预计奖励
        self.count_spin.valueChanged.connect(self.update_reward_info)
        # 初始化奖励显示
        self.update_reward_info(1)

    def update_reward_info(self, count):
        """更新预计奖励信息，包含经验和铂金币"""
        total_xp = self.xp_reward * count
        total_platinum = self.platinum_reward * count

        # 构建预计奖励文本
        reward_text = f"{total_xp} XP"
        if total_platinum > 0:
            reward_text += f" + {total_platinum} 铂金币"

        self.reward_label.setText(f"预计获得: {reward_text}")

    def get_completion_count(self):
        return self.count_spin.value()

# 直接运行测试
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dlg = AddRepeatTaskDialog()
    if dlg.exec() == QtWidgets.QDialog.Accepted:
        print(dlg.get_data())
