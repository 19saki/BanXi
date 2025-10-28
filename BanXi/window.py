
from PySide6 import QtWidgets, QtCore, QtGui

import db
from db import *
from gacha_fixed import init_gacha_system
from gacha_window import GachaTab
from hud import TopHUD
from dialogs import AddTaskDialog, AddRewardDialog
from widgets import LeftUserCard
from repeat_tasks import init_repeat_tasks, add_repeat_task, get_repeat_tasks, complete_repeat_task, delete_repeat_task
from repeat_task_dialog import AddRepeatTaskDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("伴习 v1.1.0 新增铂金币")  # 更新版本号
        self.resize(1000, 680)
        main = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()
        main.setLayout(main_layout)
        self.setCentralWidget(main)

        # 初始化重复任务表和抽卡系统
        init_repeat_tasks()
        init_gacha_system()

        # Left sidebar (保持不变)
        self.left = QtWidgets.QFrame()
        self.left.setFixedWidth(180)
        self.left.setObjectName("leftPanel")
        self.left_layout_inner = QtWidgets.QVBoxLayout()
        self.left_layout_inner.setContentsMargins(12, 12, 12, 12)
        self.left_layout_inner.setSpacing(12)
        self.left.setLayout(self.left_layout_inner)

        # 在初始化时添加一个弹性空间在底部，这样卡片就会靠上
        self.left_layout_inner.addStretch()

        # placeholders for dynamic user cards
        self.user_cards = {}
        main_layout.addWidget(self.left)

        # right main area
        right_frame = QtWidgets.QFrame()
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_frame.setLayout(right_layout)
        main_layout.addWidget(right_frame)

        # Top HUD (保持不变)
        self.top_hud = TopHUD(None)
        right_layout.addWidget(self.top_hud)

        # top: header with tabs - 添加抽卡标签页
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setObjectName("mainTabs")

        # 创建各个标签页
        self.task_tab = QtWidgets.QWidget()
        self.repeat_task_tab = QtWidgets.QWidget()
        self.gacha_tab = GachaTab(self)  # 新增抽卡标签页
        self.shop_tab = QtWidgets.QWidget()
        self.me_tab = QtWidgets.QWidget()

        # 添加标签页
        self.tab_widget.addTab(self.task_tab, "单次任务")
        self.tab_widget.addTab(self.repeat_task_tab, "重复任务")
        self.tab_widget.addTab(self.gacha_tab, "抽卡")  # 新增标签
        self.tab_widget.addTab(self.shop_tab, "奖励")
        self.tab_widget.addTab(self.me_tab, "我的")
        right_layout.addWidget(self.tab_widget)

        # 单次任务标签页布局
        t_layout = QtWidgets.QVBoxLayout()
        t_layout.setContentsMargins(8, 8, 8, 8)
        self.task_list = QtWidgets.QListWidget()
        self.task_list.setObjectName("taskList")
        t_layout.addWidget(self.task_list)
        self.task_tab.setLayout(t_layout)

        # 重复任务标签页布局
        rt_layout = QtWidgets.QVBoxLayout()
        rt_layout.setContentsMargins(8, 8, 8, 8)
        self.repeat_task_list = QtWidgets.QListWidget()
        self.repeat_task_list.setObjectName("repeatTaskList")
        rt_layout.addWidget(self.repeat_task_list)
        self.repeat_task_tab.setLayout(rt_layout)

        # Shop tab (保持不变)
        s_layout = QtWidgets.QVBoxLayout()
        s_layout.setContentsMargins(8, 8, 8, 8)
        self.shop_list = QtWidgets.QListWidget()
        self.shop_list.setObjectName("shopList")
        s_layout.addWidget(self.shop_list)
        self.shop_tab.setLayout(s_layout)

        # Me tab (保持不变)
        m_layout = QtWidgets.QVBoxLayout()
        m_layout.setContentsMargins(8, 8, 8, 8)
        self.lbl_level = QtWidgets.QLabel("等级：")
        self.lbl_xp = QtWidgets.QLabel("经验：")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setFixedHeight(18)
        self.lbl_platinum = QtWidgets.QLabel("铂金币：")
        self.lbl_coins = QtWidgets.QLabel("金币：")

        # 添加兑换按钮
        exchange_btn_layout = QtWidgets.QHBoxLayout()
        self.btn_exchange = QtWidgets.QPushButton("货币兑换")
        self.btn_exchange.clicked.connect(self.open_exchange_dialog)
        exchange_btn_layout.addWidget(self.btn_exchange)
        exchange_btn_layout.addStretch()

        m_layout.addWidget(self.lbl_level)
        m_layout.addWidget(self.lbl_xp)
        m_layout.addWidget(self.progress)
        m_layout.addWidget(self.lbl_platinum)
        m_layout.addWidget(self.lbl_coins)
        m_layout.addLayout(exchange_btn_layout)

        # Developer mode button (在我的页)
        self.dev_btn = QtWidgets.QPushButton("开发者模式")
        self.dev_btn.setToolTip("开发者工具：清空数据 / 添加账户 / 删除账户")
        self.dev_btn.clicked.connect(self.open_dev_dialog)
        m_layout.addWidget(self.dev_btn)

        m_layout.addStretch()
        self.me_tab.setLayout(m_layout)

        # Floating add buttons - 添加抽卡按钮管理
        self.add_task_btn = QtWidgets.QPushButton("+")
        self.add_task_btn.setFixedSize(56, 56)
        self.add_task_btn.setObjectName("fab")
        self.add_task_btn.clicked.connect(self.on_add_task)

        self.add_repeat_task_btn = QtWidgets.QPushButton("+")
        self.add_repeat_task_btn.setFixedSize(56, 56)
        self.add_repeat_task_btn.setObjectName("fab")
        self.add_repeat_task_btn.clicked.connect(self.on_add_repeat_task)

        self.add_shop_btn = QtWidgets.QPushButton("+")
        self.add_shop_btn.setFixedSize(56, 56)
        self.add_shop_btn.setObjectName("fab")
        self.add_shop_btn.clicked.connect(self.on_add_shop)

        # bottom area to hold floating btns
        bottom_holder = QtWidgets.QFrame()
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.add_task_btn)
        bottom_layout.addWidget(self.add_repeat_task_btn)
        bottom_layout.addWidget(self.add_shop_btn)
        bottom_holder.setLayout(bottom_layout)
        right_layout.addWidget(bottom_holder)

        # connections
        self.task_list.itemDoubleClicked.connect(self.on_task_double_click)
        self.repeat_task_list.itemDoubleClicked.connect(self.on_repeat_task_double_click)
        self.shop_list.itemDoubleClicked.connect(self.on_shop_double_click)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # initialize DB and UI content
        users = get_users()
        first_user = users[0][0] if users else None
        self.current_user_id = first_user
        # populate left user cards
        self.reload_user_cards()
        # tell HUD about the user and initialize display
        self.top_hud.set_user(self.current_user_id)

        # 设置抽卡标签页的用户
        if hasattr(self, 'gacha_tab'):
            self.gacha_tab.set_user(self.current_user_id)

        self.highlight_selected_user()
        self.refresh_all()

    def reload_user_cards(self):
        # 清除现有卡片（但保留底部的弹性空间）
        for i in reversed(range(self.left_layout_inner.count())):
            item = self.left_layout_inner.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        # 重新加载用户
        users = get_users()
        self.user_cards = {}
        for uid, name, xp, level, coins, platinum_coins in users:
            card = LeftUserCard(uid, name)
            card.clicked.connect(self.on_user_selected)
            # 在弹性空间之前插入卡片
            self.left_layout_inner.insertWidget(self.left_layout_inner.count() - 1, card)
            self.user_cards[uid] = card

        # 如果当前用户被删除或为None，选择备用用户
        if self.current_user_id not in self.user_cards:
            all_uids = list(self.user_cards.keys())
            self.current_user_id = all_uids[0] if all_uids else None
            self.top_hud.set_user(self.current_user_id)

    def highlight_selected_user(self):
        for uid, card in self.user_cards.items():
            if uid == self.current_user_id:
                card.setProperty("active", True)
            else:
                card.setProperty("active", False)
            card.style().unpolish(card)
            card.style().polish(card)
            card.update()

    def on_tab_changed(self, idx):
        # show/hide floating buttons depending on tab
        if idx == 0:  # 单次任务
            self.add_task_btn.show()
            self.add_repeat_task_btn.hide()
            self.add_shop_btn.hide()
        elif idx == 1:  # 重复任务
            self.add_task_btn.hide()
            self.add_repeat_task_btn.show()
            self.add_shop_btn.hide()
        elif idx == 2:  # 抽卡 - 不显示浮动按钮
            self.add_task_btn.hide()
            self.add_repeat_task_btn.hide()
            self.add_shop_btn.hide()
        elif idx == 3:  # 奖励
            self.add_task_btn.hide()
            self.add_repeat_task_btn.hide()
            self.add_shop_btn.show()
        else:  # 我的
            self.add_task_btn.hide()
            self.add_repeat_task_btn.hide()
            self.add_shop_btn.hide()



    # 新增：刷新抽卡标签页
    def refresh_gacha_tab(self):
        if hasattr(self, 'gacha_tab') and self.current_user_id is not None:
            self.gacha_tab.set_user(self.current_user_id)
            self.gacha_tab.refresh_display()

    def on_user_selected(self, user_id):
        # 在切换用户前，停止当前用户的动画
        if hasattr(self.top_hud, 'reset_coin_animation'):
            self.top_hud.reset_coin_animation()

        self.current_user_id = user_id

        # 更新HUD显示
        self.top_hud.set_user(user_id)

        # 设置抽卡标签页的用户
        if hasattr(self, 'gacha_tab'):
            self.gacha_tab.set_user(self.current_user_id)

        self.highlight_selected_user()
        self.refresh_all()

    def refresh_all(self):
        # 正常刷新，触发所有动画
        if self.current_user_id is not None:
            self.top_hud.update_display(self.current_user_id)

        self.refresh_tasks()
        self.refresh_repeat_tasks()
        self.refresh_gacha_tab()
        self.refresh_rewards()
        self.refresh_me()
        self.on_tab_changed(self.tab_widget.currentIndex())

    def refresh_tasks(self):
        self.task_list.clear()
        if self.current_user_id is None:
            return
        tasks = get_tasks(self.current_user_id)
        for tid, name, xp_reward, platinum_reward, completed in tasks:
            # 创建自定义的列表项控件
            item_widget = QtWidgets.QWidget()
            item_widget.setFixedHeight(60)
            item_widget.setObjectName("taskItem")  # 设置对象名用于样式
            item_layout = QtWidgets.QHBoxLayout()
            item_layout.setContentsMargins(12, 8, 12, 8)

            # 任务信息标签
            task_label = QtWidgets.QLabel()
            status = "（已完成）" if completed else ""
            reward_text = f"{xp_reward} XP"
            if platinum_reward > 0:
                reward_text += f" + {platinum_reward} 铂金币"
            task_label.setText(f"<b>{name}</b> {status}<br>奖励: {reward_text}")
            task_label.setWordWrap(True)
            task_label.setStyleSheet("color: #e6eef8; background: transparent;")

            # 完成按钮
            complete_btn = QtWidgets.QPushButton("完成")
            complete_btn.setFixedSize(50, 32)
            complete_btn.setObjectName("completeBtn")
            complete_btn.clicked.connect(lambda checked, task_id=tid: self.on_complete_task(task_id))

            # 如果任务已完成，禁用完成按钮
            if completed:
                complete_btn.setEnabled(False)
                complete_btn.setToolTip("任务已完成")
                task_label.setStyleSheet("color: #888; background: transparent;")  # 已完成的任务文字变灰

            item_layout.addWidget(task_label)
            item_layout.addStretch()
            item_layout.addWidget(complete_btn)
            item_widget.setLayout(item_layout)

            # 创建列表项
            list_item = QtWidgets.QListWidgetItem()
            list_item.setSizeHint(QtCore.QSize(0, 60))
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, tid)

            # 如果任务已完成，设置不同的背景
            if completed:
                list_item.setBackground(QtGui.QColor(255, 255, 255, 10))  # 轻微的背景色

            self.task_list.addItem(list_item)
            self.task_list.setItemWidget(list_item, item_widget)

    # 新增：刷新重复任务列表
    def refresh_repeat_tasks(self):
        self.repeat_task_list.clear()
        if self.current_user_id is None:
            return

        tasks = get_repeat_tasks(self.current_user_id)
        for tid, name, xp_reward, platinum_reward, max_completions, current_completions, completed in tasks:
            # 创建自定义的列表项控件
            item_widget = QtWidgets.QWidget()
            item_widget.setFixedHeight(70)
            item_widget.setObjectName("repeatTaskItem")
            item_layout = QtWidgets.QHBoxLayout()
            item_layout.setContentsMargins(12, 8, 12, 8)

            # 任务信息标签
            task_label = QtWidgets.QLabel()

            # 构建显示文本
            status = "（已完成）" if completed else ""
            completion_text = f"{current_completions}"
            if max_completions > 0:
                completion_text += f"/{max_completions}"
            else:
                completion_text += "次"

            # 构建奖励文本，包含铂金币信息
            reward_text = f"{xp_reward} XP/次"
            if platinum_reward > 0:
                reward_text += f" + {platinum_reward} 铂金币/次"

            task_label.setText(f"<b>{name}</b> {status}<br>奖励: {reward_text}<br>完成: {completion_text}")
            task_label.setWordWrap(True)
            task_label.setStyleSheet("color: #e6eef8; background: transparent;")

            # 完成按钮
            complete_btn = QtWidgets.QPushButton("完成")
            complete_btn.setFixedSize(50, 32)
            complete_btn.setObjectName("completeBtn")
            complete_btn.clicked.connect(lambda checked, task_id=tid: self.on_complete_repeat_task(task_id))

            # 如果任务已完成，禁用完成按钮
            if completed:
                complete_btn.setEnabled(False)
                complete_btn.setToolTip("任务已达到最大完成次数")
                task_label.setStyleSheet("color: #888; background: transparent;")

            item_layout.addWidget(task_label)
            item_layout.addStretch()
            item_layout.addWidget(complete_btn)
            item_widget.setLayout(item_layout)

            # 创建列表项
            list_item = QtWidgets.QListWidgetItem()
            list_item.setSizeHint(QtCore.QSize(0, 70))
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, tid)

            # 如果任务已完成，设置不同的背景
            if completed:
                list_item.setBackground(QtGui.QColor(255, 255, 255, 10))

            self.repeat_task_list.addItem(list_item)
            self.repeat_task_list.setItemWidget(list_item, item_widget)

    def refresh_rewards(self):
        self.shop_list.clear()
        if self.current_user_id is None:
            return

        rewards = get_rewards(self.current_user_id)
        for rid, name, price, currency_type, completed in rewards:
            # 创建自定义的列表项控件
            item_widget = QtWidgets.QWidget()
            item_widget.setFixedHeight(60)
            item_widget.setObjectName("rewardItem")
            item_layout = QtWidgets.QHBoxLayout()
            item_layout.setContentsMargins(12, 8, 12, 8)

            # 奖励信息标签
            reward_label = QtWidgets.QLabel()
            status = "（已兑换）" if completed else ""

            # 根据货币类型显示不同的信息
            if currency_type == 'platinum':
                currency_display = f"{price} 铂金币"
                currency_icon = "💎"
            else:
                currency_display = f"{price} coins"
                currency_icon = "🪙"

            reward_label.setText(f"<b>{name}</b> {status}<br>{currency_icon} 所需: {currency_display}")
            reward_label.setWordWrap(True)
            reward_label.setStyleSheet("color: #e6eef8; background: transparent;")

            # 兑换按钮
            redeem_btn = QtWidgets.QPushButton("兑换")
            redeem_btn.setFixedSize(50, 32)
            redeem_btn.setObjectName("completeBtn")
            redeem_btn.clicked.connect(lambda checked, reward_id=rid: self.on_redeem_reward(reward_id))

            # 如果奖励已兑换，禁用兑换按钮
            if completed:
                redeem_btn.setEnabled(False)
                redeem_btn.setToolTip("奖励已兑换")
                reward_label.setStyleSheet("color: #888; background: transparent;")

            item_layout.addWidget(reward_label)
            item_layout.addStretch()
            item_layout.addWidget(redeem_btn)
            item_widget.setLayout(item_layout)

            # 创建列表项
            list_item = QtWidgets.QListWidgetItem()
            list_item.setSizeHint(QtCore.QSize(0, 60))
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, rid)

            # 如果奖励已兑换，设置不同的背景
            if completed:
                list_item.setBackground(QtGui.QColor(255, 255, 255, 10))

            self.shop_list.addItem(list_item)
            self.shop_list.setItemWidget(list_item, item_widget)

    def refresh_me(self):
        if self.current_user_id is None:
            self.lbl_level.setText("等级：-")
            self.lbl_xp.setText("经验：-")
            self.progress.setValue(0)
            self.lbl_platinum.setText("铂金币：-")
            self.lbl_coins.setText("金币：-")
            return
        u = get_user(self.current_user_id)
        if u is None:
            return
        uid, name, xp, level, coins, platinum_coins = u
        self.lbl_level.setText(f"等级：{level}")

        xp_need = db.get_xp_required_for_level(level)
        self.lbl_xp.setText(f"经验：{xp} / {xp_need}")
        # progress in percent
        pct = int((xp / xp_need) * 100) if xp_need > 0 else 0
        self.progress.setValue(pct)
        self.lbl_platinum.setText(f"铂金币：{platinum_coins}")
        self.lbl_coins.setText(f"金币：{coins}")

    def on_add_task(self):
        if self.current_user_id is None:
            return
        dialog = AddTaskDialog(self)
        if dialog.exec():
            name, xp, platinum = dialog.get_data()
            if name:
                add_task(self.current_user_id, name, xp, platinum)
                self.refresh_tasks()
                # no need to update HUD here (no XP change)

    # 新增：添加重复任务
    def on_add_repeat_task(self):
        if self.current_user_id is None:
            return
        dialog = AddRepeatTaskDialog(self)
        if dialog.exec():
            name, xp, max_completions, platinum = dialog.get_data()
            if name:
                add_repeat_task(self.current_user_id, name, xp, max_completions, platinum)
                self.refresh_repeat_tasks()

    def on_add_shop(self):
        if self.current_user_id is None:
            return
        dialog = AddRewardDialog(self)  # 使用奖励对话框
        if dialog.exec():
            name, price, currency_type = dialog.get_data()
            if name:
                add_reward(self.current_user_id, name, price, currency_type)  # 添加个人奖励
                self.refresh_rewards()

    # 修改 on_shop_double_click 函数为删除奖励
    def on_shop_double_click(self, item):
        """双击奖励项执行删除逻辑"""
        reward_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self,
            "删除奖励",
            "确定要删除这个奖励吗？此操作不可撤销。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            success = delete_reward(reward_id)
            if success:
                self.refresh_rewards()
                QtWidgets.QMessageBox.information(self, "成功", "奖励已删除")
            else:
                QtWidgets.QMessageBox.warning(self, "失败", "删除奖励失败")

    # 新增：删除重复任务
    def on_repeat_task_double_click(self, item):
        """双击重复任务项执行删除逻辑"""
        task_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self,
            "删除重复任务",
            "确定要删除这个重复任务吗？此操作不可撤销。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            success = delete_repeat_task(task_id)
            if success:
                self.refresh_repeat_tasks()
                QtWidgets.QMessageBox.information(self, "成功", "重复任务已删除")
            else:
                QtWidgets.QMessageBox.warning(self, "失败", "删除重复任务失败")



    def on_task_double_click(self, item):
        """双击任务项执行删除逻辑"""
        task_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self,
            "删除任务",
            "确定要删除这个任务吗？此操作不可撤销。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            success = delete_task(task_id)
            if success:
                self.refresh_tasks()
                QtWidgets.QMessageBox.information(self, "成功", "任务已删除")
            else:
                QtWidgets.QMessageBox.warning(self, "失败", "删除任务失败")

    def on_complete_task(self, task_id):
        """完成任务的逻辑"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "完成任务",
            "确认标记此任务为完成并领取奖励？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            res = complete_task(task_id)
            if res is None:
                QtWidgets.QMessageBox.information(self, "提示", "无法完成此任务（可能已完成或不存在）。")
            else:
                gained = res["xp"]
                leveled = res["leveled"]
                coins_g = res["coins_gained"]
                platinum_g = res.get("platinum_gained", 0)
                level_up_details = res.get("level_up_details", [])

                msg = f"获得 {gained} XP"
                if platinum_g > 0 and not leveled:
                    msg += f" 和 {platinum_g} 铂金币"
                if leveled:
                    msg += f"\n升级了 {leveled} 次，总共获得 {coins_g} coins"
                    if platinum_g > 0:
                        msg += f" 和 {platinum_g} 铂金币"

                    if len(level_up_details) > 0:
                        msg += "\n\n升级详情："
                        for detail in level_up_details:
                            from_lv = detail["from_level"]
                            to_lv = detail["to_level"]
                            base = detail["base_reward"]
                            multiplier = detail["random_multiplier"]
                            actual = detail["actual_reward"]
                            platinum_reward = detail.get("platinum_reward", 0)
                            msg += f"\nLv{from_lv}→Lv{to_lv}: {base} × {multiplier} = {actual} coins"
                            if platinum_reward > 0:
                                msg += f" + {platinum_reward} 铂金币"

                QtWidgets.QMessageBox.information(self, "奖励", msg)
                # 正常刷新，触发动画
                self.refresh_all()

    def on_complete_repeat_task(self, task_id):
        """完成重复任务的逻辑"""
        # 先获取任务信息（包含铂金币奖励）
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT name, xp_reward, platinum_reward, max_completions, current_completions, completed
            FROM repeat_tasks WHERE id=?
        """, (task_id,))
        task_info = c.fetchone()
        conn.close()

        if not task_info:
            QtWidgets.QMessageBox.information(self, "提示", "任务不存在。")
            return

        name, xp_reward, platinum_reward, max_completions, current_completions, completed = task_info

        if completed:
            QtWidgets.QMessageBox.information(self, "提示", "此任务已达到最大完成次数。")
            return

        # 弹出选择完成次数的对话框
        from repeat_task_dialog import CompleteMultipleTimesDialog
        dialog = CompleteMultipleTimesDialog(name, task_id, current_completions, max_completions, self)
        if dialog.exec():
            times = dialog.get_completion_count()

            # 构建确认消息，包含铂金币信息
            total_xp = xp_reward * times
            total_platinum = platinum_reward * times
            reward_msg = f"{total_xp} XP"
            if total_platinum > 0:
                reward_msg += f" + {total_platinum} 铂金币"

            reply = QtWidgets.QMessageBox.question(
                self,
                "确认完成",
                f"确认要完成 '{name}' {times} 次吗？\n总共将获得 {reward_msg}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )

            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                from repeat_tasks import complete_repeat_task_multiple_times
                res = complete_repeat_task_multiple_times(task_id, times)

                if res is None:
                    QtWidgets.QMessageBox.information(self, "提示", "无法完成任务（可能已完成或不存在）。")
                else:
                    times_completed = res["times_completed"]
                    total_xp = res["total_xp"]
                    leveled = res["leveled"]
                    coins_g = res["coins_gained"]
                    platinum_g = res.get("platinum_gained", 0)
                    completion_count = res["completion_count"]
                    is_fully_completed = res["is_fully_completed"]

                    # 使用优化的批量任务完成通知函数
                    msg = self._format_batch_completion_message(res, name, max_completions, is_fully_completed)

                    QtWidgets.QMessageBox.information(self, "完成结果", msg)
                    # 刷新显示
                    self.refresh_all()

    def on_redeem_reward(self, reward_id):
        """兑换奖励"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "兑换奖励",
            "确认兑换此奖励？将扣除相应货币。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            res = redeem_reward(reward_id)
            if not res["success"]:
                if res["reason"] == "not_enough_coins":
                    QtWidgets.QMessageBox.warning(self, "失败", "金币不足。")
                elif res["reason"] == "not_enough_platinum":
                    QtWidgets.QMessageBox.warning(self, "失败", "铂金币不足。")
                elif res["reason"] == "already_redeemed":
                    QtWidgets.QMessageBox.warning(self, "失败", "奖励已兑换。")
                else:
                    QtWidgets.QMessageBox.warning(self, "失败", "兑换失败。")
            else:
                # 根据货币类型显示不同的成功消息
                if res["currency_type"] == "platinum":
                    message = f"兑换成功！\n剩余铂金币：{res['remaining_platinum']}\n剩余金币：{res['remaining_coins']}"
                else:
                    message = f"兑换成功！\n剩余金币：{res['remaining_coins']}\n剩余铂金币：{res['remaining_platinum']}"

                QtWidgets.QMessageBox.information(self, "成功", message)
                # 使用带动画的刷新
                self.refresh_all()


    # -------------------------
    # Developer dialog & actions
    # -------------------------
    def open_dev_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("开发者模式")
        dlg.setFixedSize(360, 200)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        info = QtWidgets.QLabel("选择操作：")
        layout.addWidget(info)

        btn_clear = QtWidgets.QPushButton("清空当前数据")
        btn_add = QtWidgets.QPushButton("添加账户")
        btn_del = QtWidgets.QPushButton("删除账户")
        layout.addWidget(btn_clear)
        layout.addWidget(btn_add)
        layout.addWidget(btn_del)

        btn_close = QtWidgets.QPushButton("关闭")
        layout.addStretch()
        layout.addWidget(btn_close)

        dlg.setLayout(layout)

        btn_clear.clicked.connect(lambda: self.handle_clear_data(dlg))
        btn_add.clicked.connect(lambda: self.handle_add_account(dlg))
        btn_del.clicked.connect(lambda: self.handle_delete_account(dlg))
        btn_close.clicked.connect(dlg.accept)

        dlg.exec()

    def handle_clear_data(self, parent_dialog=None):
        reply = QtWidgets.QMessageBox.question(self, "清空数据确认",
                                               "此操作将删除整个数据库并重建（会重置为初始用户 玖/未）。确定继续？",
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            ok = clear_data_file_and_reinit()
            if ok:
                QtWidgets.QMessageBox.information(self, "完成", "数据已清空并重建。")
                # reload UI
                self.reload_user_cards()
                self.highlight_selected_user()
                self.refresh_all()
                if parent_dialog:
                    parent_dialog.accept()
            else:
                QtWidgets.QMessageBox.warning(self, "失败", "清空数据失败。")

    def handle_add_account(self, parent_dialog=None):
        text, ok = QtWidgets.QInputDialog.getText(self, "添加账户", "输入新账户名称：")
        if ok:
            name = text.strip()
            if not name:
                QtWidgets.QMessageBox.warning(self, "错误", "名称不能为空。")
                return
            res = add_user(name)
            if res.get("success"):
                QtWidgets.QMessageBox.information(self, "完成", f"已添加账户：{name}")
                # reload UI & keep current user unchanged
                self.reload_user_cards()
                self.highlight_selected_user()
                self.refresh_all()
                if parent_dialog:
                    parent_dialog.accept()
            else:
                if res.get("reason") == "user_exists":
                    QtWidgets.QMessageBox.warning(self, "失败", "该用户名已存在。")
                else:
                    QtWidgets.QMessageBox.warning(self, "失败", "添加失败。")

    def handle_delete_account(self, parent_dialog=None):
        users = get_users()
        if not users:
            QtWidgets.QMessageBox.warning(self, "提示", "当前没有用户可删除。")
            return
        # present list of usernames with ids
        items = [f"{u[1]} (id:{u[0]})" for u in users]
        names = [u[1] for u in users]
        idx, ok = QtWidgets.QInputDialog.getItem(self, "删除账户", "选择要删除的账户：", items, 0, False)
        if ok and idx:
            # parse selected id
            # item string format: "name (id:123)"
            try:
                selected_id = int(idx.split("id:")[-1].strip(")"))
            except Exception:
                QtWidgets.QMessageBox.warning(self, "错误", "无法解析所选项。")
                return
            # safety: confirm
            reply = QtWidgets.QMessageBox.question(self, "删除确认",
                                                   f"确定删除账户 id={selected_id}？该用户的任务也会被删除。",
                                                   QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                ok_del = delete_user(selected_id)
                if ok_del:
                    QtWidgets.QMessageBox.information(self, "完成", "删除成功。")
                    # if deleted current user, pick fallback
                    if self.current_user_id == selected_id:
                        users_after = get_users()
                        self.current_user_id = users_after[0][0] if users_after else None
                        self.top_hud.set_user(self.current_user_id)
                    self.reload_user_cards()
                    self.highlight_selected_user()
                    self.refresh_all()
                    if parent_dialog:
                        parent_dialog.accept()
                else:
                    QtWidgets.QMessageBox.warning(self, "失败", "删除失败或用户不存在.")

    def open_exchange_dialog(self):
        """打开货币兑换对话框"""
        if self.current_user_id is None:
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择用户")
            return

        from db import exchange_platinum_to_gold, PLATINUM_TO_GOLD_RATE

        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("货币兑换")
        dlg.setFixedSize(400, 250)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # 显示当前余额
        u = get_user(self.current_user_id)
        if u is None:
            return
        uid, name, xp, level, coins, platinum_coins = u

        info_label = QtWidgets.QLabel(f"当前余额：\n铂金币: {platinum_coins}\n金币: {coins}\n\n兑换比例: 1 铂金币 = {PLATINUM_TO_GOLD_RATE} 金币\n\n注意：只能将铂金币兑换为金币（单向兑换）")
        info_label.setStyleSheet("font-size: 11pt; padding: 10px;")
        layout.addWidget(info_label)

        # 铂金币换金币
        platinum_to_gold_group = QtWidgets.QGroupBox("铂金币 → 金币")
        ptg_layout = QtWidgets.QHBoxLayout()
        self.platinum_input = QtWidgets.QSpinBox()
        self.platinum_input.setMinimum(0)
        self.platinum_input.setMaximum(platinum_coins)
        self.platinum_input.setValue(0)
        ptg_layout.addWidget(QtWidgets.QLabel("铂金币数量:"))
        ptg_layout.addWidget(self.platinum_input)
        btn_ptg = QtWidgets.QPushButton("兑换")
        btn_ptg.clicked.connect(lambda: self.do_platinum_to_gold_exchange(dlg))
        ptg_layout.addWidget(btn_ptg)
        platinum_to_gold_group.setLayout(ptg_layout)
        layout.addWidget(platinum_to_gold_group)

        # 关闭按钮
        btn_close = QtWidgets.QPushButton("关闭")
        btn_close.clicked.connect(dlg.accept)
        layout.addStretch()
        layout.addWidget(btn_close)

        dlg.setLayout(layout)
        dlg.exec()

    def do_platinum_to_gold_exchange(self, dialog):
        """执行铂金币换金币"""
        from db import exchange_platinum_to_gold

        amount = self.platinum_input.value()
        if amount <= 0:
            QtWidgets.QMessageBox.warning(self, "错误", "请输入有效的铂金币数量")
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "确认兑换",
            f"确认将 {amount} 铂金币兑换为 {amount * 100} 金币？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            res = exchange_platinum_to_gold(self.current_user_id, amount)
            if res["success"]:
                QtWidgets.QMessageBox.information(
                    self,
                    "兑换成功",
                    f"成功兑换 {res['platinum_spent']} 铂金币为 {res['gold_gained']} 金币\n"
                    f"剩余铂金币: {res['remaining_platinum']}\n"
                    f"当前金币: {res['new_gold']}"
                )
                self.refresh_all()
                dialog.accept()
            else:
                reason = res.get("reason", "unknown")
                if reason == "not_enough_platinum":
                    QtWidgets.QMessageBox.warning(self, "失败", "铂金币不足")
                else:
                    QtWidgets.QMessageBox.warning(self, "失败", f"兑换失败: {reason}")

    def _format_batch_completion_message(self, res, task_name, max_completions, is_fully_completed):
        """
        优化的批量任务完成通知格式化函数
        遵循单任务完成通知的模式，确保铂金币显示的一致性

        参数:
            res: 任务完成结果字典
            task_name: 任务名称
            max_completions: 最大完成次数
            is_fully_completed: 是否已完全完成

        返回:
            str: 格式化的通知消息
        """
        times_completed = res["times_completed"]
        total_xp = res["total_xp"]
        leveled = res["leveled"]
        coins_g = res["coins_gained"]
        platinum_g = res.get("platinum_gained", 0)
        completion_count = res["completion_count"]

        # 基础信息：任务完成情况
        msg = f"成功完成 {times_completed} 次 '{task_name}'\n"
        msg += f"获得 {total_xp} XP ({res['xp_per_completion']} XP/次)\n"
        msg += f"完成次数: {completion_count}"
        if max_completions > 0:
            msg += f"/{max_completions}"
        else:
            msg += "次"

        # 任务完成状态提示
        if is_fully_completed:
            msg += "\n\n⚠️ 此任务已达到最大完成次数"

        # 铂金币奖励显示（修复：遵循单任务模式）
        if platinum_g > 0 and not leveled:
            msg += f"\n获得 {platinum_g} 铂金币"

        # 升级奖励显示
        if leveled:
            msg += f"\n升级了 {leveled} 次，总共获得 {coins_g} coins"
            if platinum_g > 0:
                msg += f" 和 {platinum_g} 铂金币"

            # 升级详情
            level_up_details = res.get("level_up_details", [])
            if len(level_up_details) > 0:
                msg += "\n\n升级详情："
                for detail in level_up_details:
                    from_lv = detail["from_level"]
                    to_lv = detail["to_level"]
                    base = detail["base_reward"]
                    multiplier = detail["random_multiplier"]
                    actual = detail["actual_reward"]
                    platinum_reward = detail.get("platinum_reward", 0)
                    msg += f"\nLv{from_lv}→Lv{to_lv}: {base} × {multiplier} = {actual} coins"
                    if platinum_reward > 0:
                        msg += f" + {platinum_reward} 铂金币"

        return msg


