from PySide6 import QtWidgets, QtCore, QtGui
from db import *
from hud import TopHUD
from dialogs import AddTaskDialog, AddShopDialog
from widgets import LeftUserCard

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("双人养成 v0.1.2")
        self.resize(920, 620)
        main = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()
        main.setLayout(main_layout)
        self.setCentralWidget(main)

        # Left sidebar
        self.left = QtWidgets.QFrame()
        self.left.setFixedWidth(180)
        self.left.setObjectName("leftPanel")
        self.left_layout_inner = QtWidgets.QVBoxLayout()
        self.left_layout_inner.setContentsMargins(12, 12, 12, 12)
        self.left_layout_inner.setSpacing(12)
        self.left.setLayout(self.left_layout_inner)

        # placeholders for dynamic user cards
        self.user_cards = {}
        main_layout.addWidget(self.left)

        # right main area
        right_frame = QtWidgets.QFrame()
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_frame.setLayout(right_layout)
        main_layout.addWidget(right_frame)

        # Top HUD (新增) - 在 tabs 之上
        self.top_hud = TopHUD(None)
        right_layout.addWidget(self.top_hud)

        # top: header with tabs
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setObjectName("mainTabs")
        self.task_tab = QtWidgets.QWidget()
        self.shop_tab = QtWidgets.QWidget()
        self.me_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.task_tab, "任务")
        self.tab_widget.addTab(self.shop_tab, "奖励")
        self.tab_widget.addTab(self.me_tab, "我的")
        right_layout.addWidget(self.tab_widget)

        # Task tab layout
        t_layout = QtWidgets.QVBoxLayout()
        t_layout.setContentsMargins(8, 8, 8, 8)
        self.task_list = QtWidgets.QListWidget()
        self.task_list.setObjectName("taskList")
        t_layout.addWidget(self.task_list)
        self.task_tab.setLayout(t_layout)

        # Shop tab
        s_layout = QtWidgets.QVBoxLayout()
        s_layout.setContentsMargins(8, 8, 8, 8)
        self.shop_list = QtWidgets.QListWidget()
        self.shop_list.setObjectName("shopList")
        s_layout.addWidget(self.shop_list)
        self.shop_tab.setLayout(s_layout)

        # Me tab
        m_layout = QtWidgets.QVBoxLayout()
        m_layout.setContentsMargins(8, 8, 8, 8)
        self.lbl_level = QtWidgets.QLabel("等级：")
        self.lbl_xp = QtWidgets.QLabel("经验：")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setFixedHeight(18)
        self.lbl_coins = QtWidgets.QLabel("金币：")
        m_layout.addWidget(self.lbl_level)
        m_layout.addWidget(self.lbl_xp)
        m_layout.addWidget(self.progress)
        m_layout.addWidget(self.lbl_coins)

        # Developer mode button (在我的页)
        self.dev_btn = QtWidgets.QPushButton("开发者模式")
        self.dev_btn.setToolTip("开发者工具：清空数据 / 添加账户 / 删除账户")
        self.dev_btn.clicked.connect(self.open_dev_dialog)
        m_layout.addWidget(self.dev_btn)

        m_layout.addStretch()
        self.me_tab.setLayout(m_layout)

        # Floating add buttons
        self.add_task_btn = QtWidgets.QPushButton("+")
        self.add_task_btn.setFixedSize(56, 56)
        self.add_task_btn.setObjectName("fab")
        self.add_task_btn.clicked.connect(self.on_add_task)
        self.add_shop_btn = QtWidgets.QPushButton("+")
        self.add_shop_btn.setFixedSize(56, 56)
        self.add_shop_btn.setObjectName("fab")
        self.add_shop_btn.clicked.connect(self.on_add_shop)

        # bottom area to hold floating btns
        bottom_holder = QtWidgets.QFrame()
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.add_task_btn)
        bottom_layout.addWidget(self.add_shop_btn)
        bottom_holder.setLayout(bottom_layout)
        right_layout.addWidget(bottom_holder)

        # connections
        self.task_list.itemDoubleClicked.connect(self.on_task_double_click)
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

        self.highlight_selected_user()
        self.refresh_all()

    def reload_user_cards(self):
        # clear existing in layout
        for i in reversed(range(self.left_layout_inner.count())):
            w = self.left_layout_inner.itemAt(i).widget()
            if w:
                w.setParent(None)
        # load users again
        users = get_users()
        self.user_cards = {}
        for uid, name, xp, level, coins in users:
            card = LeftUserCard(uid, name)
            card.clicked.connect(self.on_user_selected)
            self.left_layout_inner.addWidget(card)
            self.user_cards[uid] = card
        self.left_layout_inner.addStretch()

        # if current user deleted or None, pick a fallback
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

    def on_user_selected(self, user_id):
        self.current_user_id = user_id
        # tell hud to switch user and animate to new values
        self.top_hud.update_display(user_id)
        self.highlight_selected_user()
        self.refresh_all()

    def on_tab_changed(self, idx):
        # show/hide floating buttons depending on tab
        if idx == 0:
            self.add_task_btn.show()
            self.add_shop_btn.hide()
        elif idx == 1:
            self.add_task_btn.hide()
            self.add_shop_btn.show()
        else:
            self.add_task_btn.hide()
            self.add_shop_btn.hide()

    def refresh_all(self):
        # update HUD first (reads DB)
        if self.current_user_id is not None:
            self.top_hud.update_display(self.current_user_id)
        self.refresh_tasks()
        self.refresh_shop()
        self.refresh_me()
        # set tab button visibility
        self.on_tab_changed(self.tab_widget.currentIndex())

    def refresh_tasks(self):
        self.task_list.clear()
        if self.current_user_id is None:
            return
        tasks = get_tasks(self.current_user_id)
        for tid, name, xp_reward, completed in tasks:
            # 创建自定义的列表项控件
            item_widget = QtWidgets.QWidget()
            item_widget.setFixedHeight(60)
            item_widget.setObjectName("taskItem")  # 设置对象名用于样式
            item_layout = QtWidgets.QHBoxLayout()
            item_layout.setContentsMargins(12, 8, 12, 8)

            # 任务信息标签
            task_label = QtWidgets.QLabel()
            status = "（已完成）" if completed else ""
            task_label.setText(f"<b>{name}</b> {status}<br>奖励: {xp_reward} XP")
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

    def refresh_shop(self):
        self.shop_list.clear()
        items = get_shop_items()
        for iid, name, price in items:
            w = QtWidgets.QListWidgetItem()
            w.setText(f"{name}\n价格: {price} coins")
            w.setData(QtCore.Qt.ItemDataRole.UserRole, iid)
            self.shop_list.addItem(w)

    def refresh_me(self):
        if self.current_user_id is None:
            self.lbl_level.setText("等级：-")
            self.lbl_xp.setText("经验：-")
            self.progress.setValue(0)
            self.lbl_coins.setText("金币：-")
            return
        u = get_user(self.current_user_id)
        if u is None:
            return
        uid, name, xp, level, coins = u
        self.lbl_level.setText(f"等级：{level}")
        xp_need = 100 * level
        self.lbl_xp.setText(f"经验：{xp} / {xp_need}")
        # progress in percent
        pct = int((xp / xp_need) * 100) if xp_need > 0 else 0
        self.progress.setValue(pct)
        self.lbl_coins.setText(f"金币：{coins}")

    def on_add_task(self):
        if self.current_user_id is None:
            return
        dialog = AddTaskDialog(self)
        if dialog.exec():
            name, xp = dialog.get_data()
            if name:
                add_task(self.current_user_id, name, xp)
                self.refresh_tasks()
                # no need to update HUD here (no XP change)

    def on_add_shop(self):
        dialog = AddShopDialog(self)
        if dialog.exec():
            name, price = dialog.get_data()
            if name:
                add_shop_item(name, price)
                self.refresh_shop()

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

    def on_shop_double_click(self, item):
        iid = item.data(QtCore.Qt.ItemDataRole.UserRole)
        reply = QtWidgets.QMessageBox.question(self, "购买", "确认购买此商品？",
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            res = purchase_item(self.current_user_id, iid)
            if not res["success"]:
                if res["reason"] == "not_enough_coins":
                    QtWidgets.QMessageBox.warning(self, "失败", "金币不足。")
                else:
                    QtWidgets.QMessageBox.warning(self, "失败", "购买失败。")
            else:
                QtWidgets.QMessageBox.information(self, "成功", f"购买成功，剩余金币：{res['remaining']}")
                # update HUD + me tab
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

    def on_delete_task(self, task_id):
        """删除任务"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "删除任务",
            "确定要删除这个任务吗？此操作不可撤销。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # 需要在 db.py 中添加 delete_task 函数
            success = delete_task(task_id)
            if success:
                self.refresh_tasks()
                QtWidgets.QMessageBox.information(self, "成功", "任务已删除")
            else:
                QtWidgets.QMessageBox.warning(self, "失败", "删除任务失败")

    def on_complete_task(self, task_id):
        """完成任务的逻辑（原删除按钮的功能）"""
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
                msg = f"获得 {gained} XP"
                if leveled:
                    msg += f"\n升级了 {leveled} 次，额外获得 {coins_g} coins"
                QtWidgets.QMessageBox.information(self, "奖励", msg)
                self.refresh_all()

