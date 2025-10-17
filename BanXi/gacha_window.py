from PySide6 import QtWidgets, QtCore, QtGui


class GachaTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # 抽卡信息区域 - 简化版，只保留查看奖池按钮
        info_frame = QtWidgets.QFrame()
        info_frame.setObjectName("gachaInfoFrame")
        info_layout = QtWidgets.QHBoxLayout()

        # 移除金币和保底显示，只保留查看奖池按钮
        info_layout.addStretch()

        # 查看奖池按钮
        self.view_pool_btn = QtWidgets.QPushButton("查看奖池")
        self.view_pool_btn.clicked.connect(self.show_pool_dialog)
        info_layout.addWidget(self.view_pool_btn)

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # 抽卡结果显示区域 - 移到按钮上面
        result_frame = QtWidgets.QFrame()
        result_layout = QtWidgets.QVBoxLayout()

        result_layout.addWidget(QtWidgets.QLabel("抽卡记录:"))
        self.result_list = QtWidgets.QListWidget()
        self.result_list.setObjectName("gachaResultList")
        result_layout.addWidget(self.result_list)

        result_frame.setLayout(result_layout)
        layout.addWidget(result_frame)

        # 抽卡按钮区域 - 使用水平布局固定在右下角
        button_container = QtWidgets.QWidget()
        button_container.setFixedHeight(100)  # 给按钮区域固定高度
        button_layout = QtWidgets.QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # 在左侧添加弹性空间，把按钮推到右边
        button_layout.addStretch()

        # 单抽按钮
        self.single_draw_btn = QtWidgets.QPushButton("单次抽卡\n(600金币)")
        self.single_draw_btn.setFixedSize(120, 80)
        self.single_draw_btn.setObjectName("gachaButton")
        self.single_draw_btn.clicked.connect(self.on_single_draw)
        button_layout.addWidget(self.single_draw_btn)

        # 十连抽按钮
        self.ten_draw_btn = QtWidgets.QPushButton("十连抽卡\n(6000金币)")
        self.ten_draw_btn.setFixedSize(120, 80)
        self.ten_draw_btn.setObjectName("gachaButton")
        self.ten_draw_btn.clicked.connect(self.on_ten_draw)
        button_layout.addWidget(self.ten_draw_btn)

        layout.addWidget(button_container)

        self.setLayout(layout)

        # 应用样式
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            #gachaInfoFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
            }
            #gachaButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6c63ff, stop:1 #1f6feb);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            #gachaButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #7c73ff, stop:1 #2f7ffb);
            }
            #gachaButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #5c53ee, stop:1 #0f5fdb);
            }
            #gachaResultList {
                background: rgba(255, 255, 255, 0.02);
                border-radius: 8px;
                padding: 4px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

    def set_user(self, user_id):
        self.user_id = user_id
        # 重置动画状态，避免切换用户时触发动画

        self.refresh_display()

    def refresh_display(self):
        if not hasattr(self, 'user_id') or self.user_id is None:
            return

        from gacha_fixed import get_user_gacha_records

        # 更新抽卡记录
        self.result_list.clear()
        records = get_user_gacha_records(self.user_id, 20)

        for draw_time, item_name, star, description in records:
            # 根据星级设置颜色
            color_map = {
                3: "#4FC3F7",  # 蓝色
                4: "#BA68C8",  # 紫色
                5: "#FFB74D",  # 橙色
                6: "#FF6B6B"  # 红色 - 六星改为红色
            }

            color = color_map.get(star, "#FFFFFF")
            star_text = "★" * star

            item = QtWidgets.QListWidgetItem()
            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout()

            # 星级显示 - 所有星级统一宽度为80，保持对齐
            star_label = QtWidgets.QLabel(star_text)
            star_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
            star_label.setFixedWidth(80)  # 统一宽度为80
            star_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # 居中对齐
            item_layout.addWidget(star_label)

            # 物品信息
            info_label = QtWidgets.QLabel(f"{item_name}")
            info_label.setStyleSheet("color: #e6eef8;")
            item_layout.addWidget(info_label)

            item_layout.addStretch()

            # 时间
            time_label = QtWidgets.QLabel(draw_time.split()[0])  # 只显示日期
            time_label.setStyleSheet("color: #888; font-size: 10px;")
            item_layout.addWidget(time_label)

            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())

            self.result_list.addItem(item)
            self.result_list.setItemWidget(item, item_widget)

    # 在 gacha_window.py 中
    def on_single_draw(self):
        if not hasattr(self, 'user_id') or self.user_id is None:
            QtWidgets.QMessageBox.warning(self, "错误", "请先选择用户")
            return

        try:
            from gacha_fixed import draw_gacha
            result = draw_gacha(self.user_id)
            self.handle_draw_result(result, is_single=True)

            # 立即刷新显示，让用户看到金币变化
            self.refresh_display()
            if self.parent:
                self.parent.refresh_all()  # 正常刷新，触发动画

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "抽卡失败", f"抽卡过程中出现错误: {str(e)}")

    def on_ten_draw(self):
        if not hasattr(self, 'user_id') or self.user_id is None:
            QtWidgets.QMessageBox.warning(self, "错误", "请先选择用户")
            return

        try:
            from gacha_fixed import draw_gacha_10
            result = draw_gacha_10(self.user_id)

            if not result["success"]:
                if result.get("reason") == "not_enough_coins":
                    QtWidgets.QMessageBox.warning(self, "金币不足", "金币不足，无法进行十连抽！需要6000金币。")
                    return
                else:
                    QtWidgets.QMessageBox.warning(self, "抽卡失败", f"十连抽失败: {result.get('reason', '未知错误')}")
                    return

            self.handle_draw_result(result, is_single=False)

            # 立即刷新显示，让用户看到金币变化
            self.refresh_display()
            if self.parent:
                self.parent.refresh_all()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "抽卡失败", f"十连抽过程中出现错误: {str(e)}")

    def handle_draw_result(self, result, is_single=True):
        if not result["success"]:
            reason = result.get("reason", "未知错误")
            if reason == "not_enough_coins":
                QtWidgets.QMessageBox.warning(self, "金币不足", "金币不足，无法抽卡！")
            else:
                QtWidgets.QMessageBox.warning(self, "抽卡失败", f"抽卡失败: {reason}")
            return

        if is_single:
            self.show_draw_result_dialog([result])
        else:
            self.show_draw_result_dialog(result["draws"])

    def show_draw_result_dialog(self, results):
        dialog = GachaResultDialog(results, self)
        dialog.exec()

    def show_pool_dialog(self):
        dialog = GachaPoolDialog(self)
        dialog.exec()




class GachaResultDialog(QtWidgets.QDialog):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.results = results
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("抽卡结果")

        # 根据结果数量调整对话框大小
        if len(self.results) == 1:
            self.setFixedSize(400, 200)  # 单抽结果对话框较小
        else:
            self.setFixedSize(500, 400)  # 十连结果对话框较大

        layout = QtWidgets.QVBoxLayout()

        # 结果显示区域
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(8)  # 增加项间距

        for result in self.results:
            item = result["item"]
            item_widget = self.create_item_widget(item, result.get("is_duplicate", False))
            content_layout.addWidget(item_widget)

        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # 统计信息（仅十连显示）
        if len(self.results) > 1:
            total_refund = sum(r.get("refund_coins", 0) for r in self.results)
            six_star_count = sum(1 for r in self.results if r["item"]["star"] == 6)
            five_star_count = sum(1 for r in self.results if r["item"]["star"] == 5)

            stats_text = f"十连统计: {six_star_count}个六星, {five_star_count}个五星"
            if total_refund > 0:
                stats_text += f", 重复返还: {total_refund}金币"

            stats_label = QtWidgets.QLabel(stats_text)
            stats_label.setStyleSheet("color: #FFD166; font-weight: bold; padding: 10px;")
            layout.addWidget(stats_label)

        # 确定按钮
        btn = QtWidgets.QPushButton("确定")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self.setLayout(layout)

    def create_item_widget(self, item, is_duplicate):
        widget = QtWidgets.QFrame()
        widget.setFrameStyle(QtWidgets.QFrame.Shape.Box)
        widget.setLineWidth(1)
        widget.setFixedHeight(70)  # 固定高度，保持统一

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)

        # 星级颜色 - 六星改为红色
        color_map = {
            3: ("#4FC3F7", "三星"),  # 蓝色
            4: ("#BA68C8", "四星"),  # 紫色
            5: ("#FFB74D", "五星"),  # 橙色
            6: ("#FF6B6B", "六星")  # 红色
        }

        color, star_text = color_map.get(item["star"], ("#FFFFFF", "未知"))

        # 星级显示 - 所有星级统一宽度
        star_label = QtWidgets.QLabel("★" * item["star"])
        star_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 16px;
            padding: 5px;
            border: 1px solid {color};
            border-radius: 5px;
            min-width: 80px;
            max-width: 80px;
        """)
        star_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(star_label)

        # 物品信息
        info_layout = QtWidgets.QVBoxLayout()
        name_label = QtWidgets.QLabel(item["name"])
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #e6eef8;")
        info_layout.addWidget(name_label)

        if item["description"]:
            desc_label = QtWidgets.QLabel(item["description"])
            desc_label.setStyleSheet("color: #888; font-size: 11px;")
            info_layout.addWidget(desc_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # 重复标记
        if is_duplicate:
            dup_label = QtWidgets.QLabel("重复")
            dup_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
            layout.addWidget(dup_label)

        widget.setLayout(layout)
        return widget


class GachaPoolDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_pool_items()

    def setup_ui(self):
        self.setWindowTitle("奖池内容")
        self.setFixedSize(600, 500)
        layout = QtWidgets.QVBoxLayout()

        # 概率说明
        rate_label = QtWidgets.QLabel("概率: 六星2% 五星8% 四星50% 三星40% (有保底机制)")
        rate_label.setStyleSheet("color: #FFD166; padding: 10px;")
        layout.addWidget(rate_label)

        # 奖品列表
        self.pool_list = QtWidgets.QListWidget()
        layout.addWidget(self.pool_list)

        # 按钮
        btn_layout = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("添加奖品")
        add_btn.clicked.connect(self.on_add_item)
        btn_layout.addWidget(add_btn)

        del_btn = QtWidgets.QPushButton("删除选中")
        del_btn.clicked.connect(self.on_delete_item)
        btn_layout.addWidget(del_btn)

        btn_layout.addStretch()
        close_btn = QtWidgets.QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_pool_items(self):
        from gacha_fixed import get_gacha_items
        items = get_gacha_items()

        self.pool_list.clear()
        for item_id, name, star, description in items:
            item_widget = self.create_item_widget(name, star, description, item_id)
            list_item = QtWidgets.QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, item_id)
            self.pool_list.addItem(list_item)
            self.pool_list.setItemWidget(list_item, item_widget)

    def create_item_widget(self, name, star, description, item_id):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        # 星级颜色 - 六星改为红色
        color_map = {
            3: "#4FC3F7",  # 蓝色
            4: "#BA68C8",  # 紫色
            5: "#FFB74D",  # 橙色
            6: "#FF6B6B"  # 红色
        }

        color = color_map.get(star, "#FFFFFF")

        # 星级显示 - 统一宽度
        star_label = QtWidgets.QLabel("★" * star)
        star_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 14px;
            padding: 5px;
            border: 1px solid {color};
            border-radius: 5px;
            min-width: 80px;
            max-width: 80px;
        """)
        star_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(star_label)

        # 物品信息
        info_layout = QtWidgets.QVBoxLayout()
        name_label = QtWidgets.QLabel(name)
        name_label.setStyleSheet("font-weight: bold; color: #e6eef8;")
        info_layout.addWidget(name_label)

        if description:
            desc_label = QtWidgets.QLabel(description)
            desc_label.setStyleSheet("color: #888; font-size: 11px;")
            info_layout.addWidget(desc_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # ID显示
        id_label = QtWidgets.QLabel(f"ID: {item_id}")
        id_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(id_label)

        widget.setLayout(layout)
        return widget

    def on_add_item(self):
        from gacha_dialog import AddGachaItemDialog
        dialog = AddGachaItemDialog(self)
        if dialog.exec():
            name, star, description = dialog.get_data()
            if name:
                from gacha_fixed import add_gacha_item
                add_gacha_item(name, star, description)
                self.load_pool_items()

    def on_delete_item(self):
        current_item = self.pool_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "错误", "请先选择一个奖品")
            return

        item_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个奖品吗？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            from gacha_fixed import (delete_gacha_item)
            success = delete_gacha_item(item_id)
            if success:
                self.load_pool_items()
                QtWidgets.QMessageBox.information(self, "成功", "奖品已删除")
            else:
                QtWidgets.QMessageBox.warning(self, "失败", "删除奖品失败")
