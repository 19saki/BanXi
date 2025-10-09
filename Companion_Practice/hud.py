from PySide6 import QtWidgets, QtCore
from db import get_user  # 导入获取用户信息的函数

class TopHUD(QtWidgets.QWidget):
    def __init__(self, user_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id  # 当前显示的用户ID
        self.last_level = None  # 上一次显示的等级
        self.last_xp = None     # 上一次显示的经验值
        self._anim = None       # 用于保存进度条动画对象，避免重复创建

        # 设置顶部 HUD 高度固定
        self.setFixedHeight(60)

        # 设置 TopHUD 背景和文字颜色（这里取消了渐变，使用纯色）
        self.setStyleSheet("""
             background: #0f1720;
             color: #e6eef8;
        """)

        # 水平布局，容纳等级标签、经验条和金币标签
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)  # 内边距
        layout.setSpacing(16)  # 子控件之间的间距

        # 等级标签
        self.level_label = QtWidgets.QLabel("Lv -")
        self.level_label.setStyleSheet("font-weight:700; font-size:14pt; color: #FFD166;")
        layout.addWidget(self.level_label)

        # 经验值进度条
        self.xp_bar = QtWidgets.QProgressBar()
        self.xp_bar.setTextVisible(True)  # 显示文本
        self.xp_bar.setFixedHeight(20)
        self.xp_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 10px;
                background: rgba(255,255,255,0.03);  # 背景半透明
                text-align: center;                  # 文本居中
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6c63ff, stop:1 #1f6feb);
                # 如果想取消渐变，可以改成单色，例如 background: #6c63ff;
            }
        """)
        layout.addWidget(self.xp_bar, stretch=1)  # stretch=1 使进度条拉伸占满剩余空间

        # 金币标签
        self.coin_label = QtWidgets.QLabel("G 0")
        self.coin_label.setStyleSheet("font-size:12pt; color: #FFD166;")
        layout.addWidget(self.coin_label)

        # 占位填充，保持左侧控件靠左显示
        layout.addStretch()

    # -------------------------
    # 获取用户信息
    # -------------------------
    def _fetch_user(self):
        if self.user_id is None:
            return None
        return get_user(self.user_id)

    # -------------------------
    # 设置显示的用户ID
    # -------------------------
    def set_user(self, user_id):
        self.user_id = user_id

    # -------------------------
    # 更新 HUD 显示
    # -------------------------
    def update_display(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id

        u = self._fetch_user()  # 获取用户数据
        if not u:
            return

        # 拆包用户信息
        uid, name, xp, level, coins = u
        xp_needed_new = 100 * level  # 升级所需经验值

        # 第一次显示时直接初始化显示
        if self.last_level is None:
            self.level_label.setText(f"Lv {level}")
            self.coin_label.setText(f"G {coins}")
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setValue(xp)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            self.last_level = level
            self.last_xp = xp
            return

        # -------------------------
        # 内部函数：动画过渡经验值
        # -------------------------
        def animate_value(start, end, duration=500, finished_cb=None):
            if self._anim is not None:  # 停止之前的动画
                try:
                    self._anim.stop()
                except Exception:
                    pass
            anim = QtCore.QPropertyAnimation(self.xp_bar, b"value")  # 动画作用于 QProgressBar.value 属性
            anim.setDuration(duration)
            anim.setStartValue(start)
            anim.setEndValue(end)
            if finished_cb:
                anim.finished.connect(finished_cb)  # 动画结束回调
            self._anim = anim
            anim.start()

        # -------------------------
        # 升级逻辑
        # -------------------------
        if level == self.last_level:
            # 等级未变，只更新经验值
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            animate_value(self.last_xp, xp, duration=500, finished_cb=lambda: self._on_anim_finished(level, xp))

        elif level > self.last_level:
            # 等级升高，需要先动画填满旧等级进度条
            old_needed = 100 * self.last_level
            new_needed = xp_needed_new

            def after_fill_old():
                # 更新为新等级
                self.level_label.setText(f"Lv {level}")
                self.coin_label.setText(f"G {coins}")
                self.xp_bar.setMaximum(new_needed)
                self.xp_bar.setValue(0)
                self.xp_bar.setFormat(f"XP: {xp}/{new_needed}")
                animate_value(0, xp, duration=600, finished_cb=lambda: self._on_anim_finished(level, xp))

            # 动画填满旧等级
            self.xp_bar.setMaximum(old_needed)
            self.xp_bar.setFormat(f"XP: {old_needed}/{old_needed}")
            animate_value(self.last_xp, old_needed, duration=450, finished_cb=after_fill_old)

        else:
            # 等级下降（理论上不常见）
            self.level_label.setText(f"Lv {level}")
            self.coin_label.setText(f"G {coins}")
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setValue(xp)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            self._on_anim_finished(level, xp)

    # -------------------------
    # 动画完成后更新最后显示值
    # -------------------------
    def _on_anim_finished(self, level, xp):
        self.last_level = level
        self.last_xp = xp
        self.level_label.setText(f"Lv {level}")
        self.coin_label.setText(
            f"🪙 {get_user(self.user_id)[4] if get_user(self.user_id) else 0}"
        )
