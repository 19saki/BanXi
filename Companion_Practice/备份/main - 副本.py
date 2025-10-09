# main.py
# 双人养成 v0.1 (PySide6 + SQLite)
# 运行: python main.py
# 依赖: PySide6
# pip install PySide6

import sys
import sqlite3
import os
from PySide6 import QtCore, QtGui, QtWidgets

DB_FILE = "../data.db"

# -------------------------
# Database helper functions
# -------------------------
def init_db():
    created = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        coins INTEGER DEFAULT 0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        xp_reward INTEGER,
        completed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS shop(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER
    )
    """)
    conn.commit()

    # Insert two users if missing
    for uname in ["玖", "未"]:
        c.execute("SELECT id FROM users WHERE name=?", (uname,))
        if c.fetchone() is None:
            c.execute("INSERT INTO users(name, xp, level, coins) VALUES(?,?,?,?)",
                      (uname, 0, 1, 0))
    conn.commit()
    conn.close()
    return created

def get_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, xp, level, coins FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, xp, level, coins FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_user(user_id, xp=None, level=None, coins=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if xp is not None:
        c.execute("UPDATE users SET xp=? WHERE id=?", (xp, user_id))
    if level is not None:
        c.execute("UPDATE users SET level=? WHERE id=?", (level, user_id))
    if coins is not None:
        c.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))
    conn.commit()
    conn.close()

def add_task(user_id, name, xp_reward):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tasks(user_id, name, xp_reward) VALUES(?,?,?)", (user_id, name, xp_reward))
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, xp_reward, completed FROM tasks WHERE user_id=? ORDER BY completed, id", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def complete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, xp_reward, completed FROM tasks WHERE id=?", (task_id,))
    t = c.fetchone()
    if t is None:
        conn.close()
        return None
    user_id, xp_reward, completed = t
    if completed:
        conn.close()
        return None
    # mark completed
    c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    # add xp/coins
    c.execute("SELECT xp, level, coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.commit()
        conn.close()
        return None
    cur_xp, level, coins = u
    new_xp = cur_xp + xp_reward
    # level up loop
    xp_needed = 100 * level
    gained_coins = 0
    leveled = 0
    while new_xp >= xp_needed:
        new_xp -= xp_needed
        level += 1
        leveled += 1
        reward = 10 * level
        coins += reward
        gained_coins += reward
        xp_needed = 100 * level
    c.execute("UPDATE users SET xp=?, level=?, coins=? WHERE id=?", (new_xp, level, coins, user_id))
    conn.commit()
    conn.close()
    return {"user_id": user_id, "xp": xp_reward, "leveled": leveled, "coins_gained": gained_coins}

def add_shop_item(name, price):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO shop(name, price) VALUES(?,?)", (name, price))
    conn.commit()
    conn.close()

def get_shop_items():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, price FROM shop ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def purchase_item(user_id, item_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT price FROM shop WHERE id=?", (item_id,))
    s = c.fetchone()
    if s is None:
        conn.close()
        return {"success": False, "reason": "item_not_found"}
    price = s[0]
    c.execute("SELECT coins FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    if u is None:
        conn.close()
        return {"success": False, "reason": "user_not_found"}
    coins = u[0]
    if coins < price:
        conn.close()
        return {"success": False, "reason": "not_enough_coins"}
    coins -= price
    c.execute("UPDATE users SET coins=? WHERE id=?", (coins, user_id))
    # Could add purchase history table later
    conn.commit()
    conn.close()
    return {"success": True, "remaining": coins}

# Developer DB helpers
def add_user(name):
    if not name:
        return {"success": False, "reason": "empty_name"}
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(name, xp, level, coins) VALUES(?,?,?,?)", (name, 0, 1, 0))
        conn.commit()
        uid = c.lastrowid
        conn.close()
        return {"success": True, "id": uid}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "reason": "user_exists"}

def delete_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # remove tasks belonging to user too
    c.execute("DELETE FROM tasks WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def clear_data_file_and_reinit():
    # remove DB file and recreate with default users
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_db()
        return True
    except Exception:
        return False

# ==========================
# Top HUD：显示等级 / XP / 金币（带动画）
# ==========================
class TopHUD(QtWidgets.QWidget):
    def __init__(self, user_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.last_level = None
        self.last_xp = None
        self._anim = None

        self.setFixedHeight(60)
        self.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0f1720, stop:1 #16202a);
            color: #e6eef8;
        """)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)

        # Level display
        self.level_label = QtWidgets.QLabel("Lv -")
        self.level_label.setStyleSheet("font-weight:700; font-size:14pt; color: #FFD166;")
        layout.addWidget(self.level_label)

        # XP bar (we will set max dynamically)
        self.xp_bar = QtWidgets.QProgressBar()
        self.xp_bar.setTextVisible(True)
        self.xp_bar.setFixedHeight(20)
        self.xp_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 10px;
                background: rgba(255,255,255,0.03);
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6c63ff, stop:1 #1f6feb);
            }
        """)
        layout.addWidget(self.xp_bar, stretch=1)

        # Coins
        self.coin_label = QtWidgets.QLabel("🪙 0")
        self.coin_label.setStyleSheet("font-size:12pt; color: #FFD166;")
        layout.addWidget(self.coin_label)

        layout.addStretch()

    def _fetch_user(self):
        if self.user_id is None:
            return None
        return get_user(self.user_id)

    def set_user(self, user_id):
        self.user_id = user_id

    def update_display(self, user_id=None):
        """读取 DB，然后以动画方式更新显示"""
        if user_id is not None:
            self.user_id = user_id
        u = self._fetch_user()
        if not u:
            return
        uid, name, xp, level, coins = u
        xp_needed_new = 100 * level

        # first time initialization — set directly
        if self.last_level is None:
            self.level_label.setText(f"Lv {level}")
            self.coin_label.setText(f"🪙 {coins}")
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setValue(xp)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            self.last_level = level
            self.last_xp = xp
            return

        # Helper to animate value
        def animate_value(start, end, duration=500, finished_cb=None):
            if self._anim is not None:
                try:
                    self._anim.stop()
                except Exception:
                    pass
            anim = QtCore.QPropertyAnimation(self.xp_bar, b"value")
            anim.setDuration(duration)
            anim.setStartValue(start)
            anim.setEndValue(end)
            if finished_cb:
                anim.finished.connect(finished_cb)
            # keep reference so GC 不回收
            self._anim = anim
            anim.start()

        # same level: just animate start->end
        if level == self.last_level:
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            animate_value(self.last_xp, xp, duration=500, finished_cb=lambda: self._on_anim_finished(level, xp))
        elif level > self.last_level:
            # leveled up: 先把进度条补到旧等级满（动画），再切为新等级并从0动画到新xp
            old_needed = 100 * self.last_level
            new_needed = xp_needed_new

            def after_fill_old():
                # update level & coins display to new values
                self.level_label.setText(f"Lv {level}")
                self.coin_label.setText(f"🪙 {coins}")
                # switch progress bar maximum to new_needed
                self.xp_bar.setMaximum(new_needed)
                # set visual to 0 then animate 0 -> xp
                self.xp_bar.setValue(0)
                self.xp_bar.setFormat(f"XP: {xp}/{new_needed}")
                # animate 0->xp
                animate_value(0, xp, duration=600, finished_cb=lambda: self._on_anim_finished(level, xp))

            # animate last_xp -> old_needed (quick)
            self.xp_bar.setMaximum(old_needed)
            self.xp_bar.setFormat(f"XP: {old_needed}/{old_needed}")
            animate_value(self.last_xp, old_needed, duration=450, finished_cb=after_fill_old)
        else:
            # level decreased? unlikely, but set directly
            self.level_label.setText(f"Lv {level}")
            self.coin_label.setText(f"🪙 {coins}")
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setValue(xp)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            self._on_anim_finished(level, xp)

    def _on_anim_finished(self, level, xp):
        # update internal state after animations
        self.last_level = level
        self.last_xp = xp
        # ensure labels reflect final
        self.level_label.setText(f"Lv {level}")
        self.coin_label.setText(f"🪙 {get_user(self.user_id)[4] if get_user(self.user_id) else 0}")


# -------------------------
# UI Classes (Dialogs / Left card / MainWindow)
# -------------------------
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
        self.name_edit.setPlaceholderText("商品名称（例如：小裙子）")
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

class LeftUserCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(int)  # user_id

    def __init__(self, user_id, name, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setFixedHeight(80)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setObjectName("userCard")
        h = QtWidgets.QHBoxLayout()
        h.setContentsMargins(10, 10, 10, 10)
        h.setSpacing(10)
        # avatar circle
        self.avatar = QtWidgets.QLabel()
        self.avatar.setFixedSize(48, 48)
        self.avatar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.avatar.setObjectName("avatarCircle")
        self.avatar.setText(name[0] if name else "?")
        font = self.avatar.font()
        font.setBold(True)
        font.setPointSize(14)
        self.avatar.setFont(font)
        h.addWidget(self.avatar)
        # name
        v = QtWidgets.QVBoxLayout()
        self.name_label = QtWidgets.QLabel(name)
        self.name_label.setObjectName("userName")
        v.addWidget(self.name_label)
        v.addStretch()
        h.addLayout(v)
        self.setLayout(h)

    def mousePressEvent(self, e):
        self.clicked.emit(self.user_id)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("双人养成 v0.1")
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
        self.tab_widget.addTab(self.shop_tab, "商店")
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
            w = QtWidgets.QListWidgetItem()
            status = "（已完成）" if completed else ""
            w.setText(f"{name} {status}\n商店: {xp_reward} XP")
            w.setData(QtCore.Qt.ItemDataRole.UserRole, tid)
            # subtle formatting
            if completed:
                w.setFlags(w.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.task_list.addItem(w)

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
        tid = item.data(QtCore.Qt.ItemDataRole.UserRole)
        # confirm completion
        reply = QtWidgets.QMessageBox.question(self, "完成任务", "确认标记此任务为完成并领取奖励？",
                                               QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            res = complete_task(tid)
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
                # refresh everything, HUD will animate based on DB diff
                self.refresh_all()

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

# -------------------------
# Styles (QSS)
# -------------------------
STYLE = """
/* 全局 */
QWidget {
    background: #0f1720;
    color: #e6eef8;
    font-family: "Segoe UI", "Microsoft YaHei", Arial;
    font-size: 12px;
}

/* Left panel */
#leftPanel {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0b1220, stop:1 #0f1720);
    border-right: 1px solid rgba(255,255,255,0.03);
}

/* User card */
#userCard {
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
}
#userCard[active="true"] {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #6c63ff);
    color: white;
}

/* Avatar circle */
#avatarCircle {
    border-radius: 24px;
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #253046, stop:1 #1b2a3a);
    color: #a8d0ff;
}

/* Tabs */
QTabWidget::pane { border: none; }
QTabBar::tab {
    background: transparent;
    border: none;
    padding: 10px 18px;
    margin-right: 4px;
    color: #cfe6ff;
    border-radius: 8px;
}
QTabBar::tab:selected {
    background: rgba(255,255,255,0.04);
    color: white;
}

/* Lists */
QListWidget {
    background: rgba(255,255,255,0.02);
    border-radius: 8px;
    padding: 8px;
}
QListWidget::item {
    background: transparent;
    padding: 10px;
    margin: 6px;
    border-radius: 8px;
}
QListWidget::item:selected {
    background: rgba(255,255,255,0.03);
}

/* Floating fab */
#fab {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #6c63ff, stop:1 #1f6feb);
    color: white;
    border-radius: 28px;
    font-size: 22px;
    font-weight: bold;
    border: none;
}
#fab:hover {
    transform: scale(1.03);
}

/* Progress bar */
QProgressBar {
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #6c63ff, stop:1 #1f6feb);
    border-radius: 8px;
}
"""

# -------------------------
# Run
# -------------------------
def main():
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    win = MainWindow()
    win.show()
    # set initial visibility for floating buttons
    win.on_tab_changed(win.tab_widget.currentIndex())
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
