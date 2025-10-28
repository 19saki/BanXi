from PySide6 import QtWidgets, QtCore

import db
from db import get_user  # 导入获取用户信息的函数

from PySide6 import QtWidgets, QtCore, QtGui

import db
from db import get_user


from PySide6 import QtWidgets, QtCore, QtGui
class TopHUD(QtWidgets.QWidget):
    def __init__(self, user_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.last_level = None
        self.last_xp = None
        self._anim = None

        # 金币动画相关变量
        self.current_coins = 0
        self.target_coins = 0
        self.pending_change = 0
        self.animation_start_coins = 0
        self.animation_total_change = 0

        # 铂金币动画相关变量
        self.current_platinum = 0
        self.target_platinum = 0
        self.pending_platinum_change = 0
        self.animation_start_platinum = 0
        self.animation_total_platinum_change = 0

        # 金币动画时间参数
        self.change_delay = 1500
        self.animation_duration = 2000

        self.change_timer = QtCore.QTimer()
        self.change_timer.setSingleShot(True)
        self.change_timer.timeout.connect(self.start_coin_animation)

        # 铂金币动画计时器
        self.platinum_change_timer = QtCore.QTimer()
        self.platinum_change_timer.setSingleShot(True)
        self.platinum_change_timer.timeout.connect(self.start_platinum_animation)

        # 动画相关
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout.connect(self.update_coin_animation)
        self.animation_duration = 1500
        self.animation_start_time = 0
        self.is_animating = False

        # 铂金币动画相关
        self.platinum_animation_timer = QtCore.QTimer()
        self.platinum_animation_timer.timeout.connect(self.update_platinum_animation)
        self.platinum_animation_start_time = 0
        self.is_platinum_animating = False

        self.setFixedHeight(60)
        self.setStyleSheet("background: #0f1720; color: #e6eef8;")

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)

        # 等级标签
        self.level_label = QtWidgets.QLabel("Lv -")
        self.level_label.setStyleSheet("font-weight:700; font-size:14pt; color: #FFD166;")
        layout.addWidget(self.level_label)

        # 经验值进度条
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

        # 铂金币标签
        self.platinum_container = QtWidgets.QWidget()
        platinum_layout = QtWidgets.QHBoxLayout(self.platinum_container)
        platinum_layout.setContentsMargins(0, 0, 0, 0)
        platinum_layout.setSpacing(4)

        self.platinum_icon = QtWidgets.QLabel("P")
        self.platinum_icon.setStyleSheet("font-size:12pt; color: #B0C4DE;")

        self.platinum_label = QtWidgets.QLabel("0")
        self.platinum_label.setStyleSheet("font-size:12pt; color: #B0C4DE;")

        self.platinum_change_label = QtWidgets.QLabel("")
        self.platinum_change_label.setStyleSheet("font-size:10pt; color: #888;")

        platinum_layout.addWidget(self.platinum_icon)
        platinum_layout.addWidget(self.platinum_label)
        platinum_layout.addWidget(self.platinum_change_label)

        layout.addWidget(self.platinum_container)

        # 金币标签
        self.coin_container = QtWidgets.QWidget()
        coin_layout = QtWidgets.QHBoxLayout(self.coin_container)
        coin_layout.setContentsMargins(0, 0, 0, 0)
        coin_layout.setSpacing(4)

        self.coin_icon = QtWidgets.QLabel("G")
        self.coin_icon.setStyleSheet("font-size:12pt; color: #FFD166;")

        self.coin_label = QtWidgets.QLabel("0")
        self.coin_label.setStyleSheet("font-size:12pt; color: #FFD166;")

        self.change_label = QtWidgets.QLabel("")
        self.change_label.setStyleSheet("font-size:10pt; color: #888;")

        coin_layout.addWidget(self.coin_icon)
        coin_layout.addWidget(self.coin_label)
        coin_layout.addWidget(self.change_label)

        layout.addWidget(self.coin_container)
        layout.addStretch()

    def set_user(self, user_id):
        """设置用户，重置动画状态"""
        self.user_id = user_id
        self.reset_coin_animation()
        self.reset_platinum_animation()
        # 立即更新显示，但不要重置金币数值
        u = self._fetch_user()
        if u:
            uid, name, xp, level, coins, platinum_coins = u
            # 只更新显示，不触发动画
            self.current_coins = coins
            self.target_coins = coins
            self.coin_label.setText(str(coins))
            self.change_label.setText("")

            self.current_platinum = platinum_coins
            self.target_platinum = platinum_coins
            self.platinum_label.setText(str(platinum_coins))
            self.platinum_change_label.setText("")

    def reset_coin_animation(self):
        """重置金币动画状态"""
        self.change_timer.stop()
        self.animation_timer.stop()
        self.is_animating = False
        self.pending_change = 0
        self.change_label.setText("")

    def reset_platinum_animation(self):
        """重置铂金币动画状态"""
        self.platinum_change_timer.stop()
        self.platinum_animation_timer.stop()
        self.is_platinum_animating = False
        self.pending_platinum_change = 0
        self.platinum_change_label.setText("")

    def update_display(self, user_id=None):
        """更新显示，保持原有的动画逻辑"""
        if user_id is not None:
            self.user_id = user_id

        u = self._fetch_user()
        if not u:
            return

        uid, name, xp, level, coins, platinum_coins = u
        xp_needed_new = db.get_xp_required_for_level(level)

        # 处理金币变化 - 总是触发动画逻辑
        self.handle_coin_change(coins)
        self.handle_platinum_change(platinum_coins)

        # 第一次显示时直接初始化显示
        if self.last_level is None:
            self.level_label.setText(f"Lv {level}")
            self.current_coins = coins
            self.target_coins = coins
            self.coin_label.setText(str(coins))
            self.current_platinum = platinum_coins
            self.target_platinum = platinum_coins
            self.platinum_label.setText(str(platinum_coins))
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setValue(xp)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            self.last_level = level
            self.last_xp = xp
            return

        # 经验值动画逻辑（保持不变）
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
            self._anim = anim
            anim.start()

        if level == self.last_level:
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            animate_value(self.last_xp, xp, duration=500, finished_cb=lambda: self._on_anim_finished(level, xp))

        elif level > self.last_level:
            old_needed = db.get_xp_required_for_level(self.last_level)
            new_needed = xp_needed_new

            def after_fill_old():
                self.level_label.setText(f"Lv {level}")
                self.xp_bar.setMaximum(new_needed)
                self.xp_bar.setValue(0)
                self.xp_bar.setFormat(f"XP: {xp}/{new_needed}")
                animate_value(0, xp, duration=600, finished_cb=lambda: self._on_anim_finished(level, xp))

            self.xp_bar.setMaximum(old_needed)
            self.xp_bar.setFormat(f"XP: {old_needed}/{old_needed}")
            animate_value(self.last_xp, old_needed, duration=450, finished_cb=after_fill_old)

        else:
            self.level_label.setText(f"Lv {level}")
            self.xp_bar.setMaximum(xp_needed_new)
            self.xp_bar.setValue(xp)
            self.xp_bar.setFormat(f"XP: {xp}/{xp_needed_new}")
            self._on_anim_finished(level, xp)

    def handle_coin_change(self, new_coins):
        """处理金币变化，触发动画"""
        # 如果是第一次设置或者切换用户后，直接设置数值
        if self.current_coins == 0 and not self.is_animating:
            self.current_coins = new_coins
            self.target_coins = new_coins
            self.coin_label.setText(str(new_coins))
            return

        # 如果没有变化，直接返回
        if new_coins == self.target_coins:
            return

        change = new_coins - self.target_coins

        if self.is_animating:
            # 如果正在动画中，累积变化
            self.pending_change += change
            self.target_coins = new_coins
            self.update_change_label_immediately()
            # 重新开始计时
            self.change_timer.start(self.change_delay)
        else:
            # 没有动画时，累积变化而不是重置
            self.pending_change += change  # 改为累积而不是重置
            self.target_coins = new_coins
            self.update_change_label_immediately()
            # 开始计时器，增加延迟时间让用户多看一会
            self.change_timer.start(self.change_delay + 500)  # 增加500ms延迟

    def start_coin_animation(self):
        """开始金币动画"""
        if self.pending_change == 0:
            self.change_label.setText("")
            return

        # 保存动画开始前的状态
        # 注意：这里使用 current_coins 作为起始值，而不是 target_coins - pending_change
        self.animation_start_coins = self.current_coins
        self.animation_total_change = self.pending_change

        # 开始动画
        self.animation_start_time = QtCore.QDateTime.currentDateTime().toMSecsSinceEpoch()
        self.is_animating = True
        self.animation_timer.start(16)

    def update_coin_animation(self):
        """更新金币动画"""
        current_time = QtCore.QDateTime.currentDateTime().toMSecsSinceEpoch()
        elapsed = current_time - self.animation_start_time
        progress = min(elapsed / self.animation_duration, 1.0)

        if progress >= 1.0:
            # 动画结束
            self.animation_timer.stop()
            self.current_coins = self.target_coins  # 直接设置为目标值
            self.coin_label.setText(str(self.current_coins))
            self.change_label.setText("")
            self.pending_change = 0
            self.is_animating = False
        else:
            # 使用缓动函数让动画更自然
            eased_progress = self.ease_out_cubic(progress)

            # 计算当前显示的金币数（从动画开始时的数值开始）
            animated_coins = self.animation_start_coins + int(self.animation_total_change * eased_progress)
            self.coin_label.setText(str(animated_coins))

            # 更新变化标签（逐渐减少并变淡）
            remaining_change = self.animation_total_change - int(self.animation_total_change * eased_progress)
            if remaining_change > 0:
                self.change_label.setText(f"+{remaining_change}")
            elif remaining_change < 0:
                self.change_label.setText(f"{remaining_change}")
            else:
                self.change_label.setText("")

            # 变化标签逐渐变淡
            alpha = int(255 * (1 - progress * 0.8))
            if self.animation_total_change > 0:
                self.change_label.setStyleSheet(f"""
                    font-size: 11pt; 
                    color: rgba(102, 187, 106, {alpha / 255}); 
                    font-weight: bold;
                """)
            else:
                self.change_label.setStyleSheet(f"""
                    font-size: 11pt; 
                    color: rgba(239, 83, 80, {alpha / 255}); 
                    font-weight: bold;
                """)

    def update_change_label_immediately(self):
        """立即更新变化标签显示"""
        if self.pending_change > 0:
            self.change_label.setText(f"+{self.pending_change}")
            self.change_label.setStyleSheet("color: #66BB6A; font-weight: bold; font-size: 12pt;")
        else:
            self.change_label.setText(f"{self.pending_change}")
            self.change_label.setStyleSheet("color: #EF5350; font-weight: bold; font-size: 12pt;")

    # 铂金币动画相关函数
    def handle_platinum_change(self, new_platinum):
        """处理铂金币变化，触发动画"""
        # 如果是第一次设置或者切换用户后，直接设置数值
        if self.current_platinum == 0 and not self.is_platinum_animating:
            self.current_platinum = new_platinum
            self.target_platinum = new_platinum
            self.platinum_label.setText(str(new_platinum))
            return

        # 如果没有变化，直接返回
        if new_platinum == self.target_platinum:
            return

        change = new_platinum - self.target_platinum

        if self.is_platinum_animating:
            # 如果正在动画中，累积变化
            self.pending_platinum_change += change
            self.target_platinum = new_platinum
            self.update_platinum_change_label_immediately()
            # 重新开始计时
            self.platinum_change_timer.start(self.change_delay)
        else:
            # 没有动画时，累积变化而不是重置
            self.pending_platinum_change += change
            self.target_platinum = new_platinum
            self.update_platinum_change_label_immediately()
            # 开始计时器，增加延迟时间让用户多看一会
            self.platinum_change_timer.start(self.change_delay + 500)

    def start_platinum_animation(self):
        """开始铂金币动画"""
        if self.pending_platinum_change == 0:
            self.platinum_change_label.setText("")
            return

        # 保存动画开始前的状态
        self.animation_start_platinum = self.current_platinum
        self.animation_total_platinum_change = self.pending_platinum_change

        # 开始动画
        self.platinum_animation_start_time = QtCore.QDateTime.currentDateTime().toMSecsSinceEpoch()
        self.is_platinum_animating = True
        self.platinum_animation_timer.start(16)

    def update_platinum_animation(self):
        """更新铂金币动画"""
        current_time = QtCore.QDateTime.currentDateTime().toMSecsSinceEpoch()
        elapsed = current_time - self.platinum_animation_start_time
        progress = min(elapsed / self.animation_duration, 1.0)

        if progress >= 1.0:
            # 动画结束
            self.platinum_animation_timer.stop()
            self.current_platinum = self.target_platinum
            self.platinum_label.setText(str(self.current_platinum))
            self.platinum_change_label.setText("")
            self.pending_platinum_change = 0
            self.is_platinum_animating = False
        else:
            # 使用缓动函数让动画更自然
            eased_progress = self.ease_out_cubic(progress)

            # 计算当前显示的铂金币数
            animated_platinum = self.animation_start_platinum + int(self.animation_total_platinum_change * eased_progress)
            self.platinum_label.setText(str(animated_platinum))

            # 更新变化标签（逐渐减少并变淡）
            remaining_change = self.animation_total_platinum_change - int(self.animation_total_platinum_change * eased_progress)
            if remaining_change > 0:
                self.platinum_change_label.setText(f"+{remaining_change}")
            elif remaining_change < 0:
                self.platinum_change_label.setText(f"{remaining_change}")
            else:
                self.platinum_change_label.setText("")

            # 变化标签逐渐变淡
            alpha = int(255 * (1 - progress * 0.8))
            if self.animation_total_platinum_change > 0:
                self.platinum_change_label.setStyleSheet(f"""
                    font-size: 11pt;
                    color: rgba(176, 196, 222, {alpha / 255});
                    font-weight: bold;
                """)
            else:
                self.platinum_change_label.setStyleSheet(f"""
                    font-size: 11pt;
                    color: rgba(239, 83, 80, {alpha / 255});
                    font-weight: bold;
                """)

    def update_platinum_change_label_immediately(self):
        """立即更新铂金币变化标签显示"""
        if self.pending_platinum_change > 0:
            self.platinum_change_label.setText(f"+{self.pending_platinum_change}")
            self.platinum_change_label.setStyleSheet("color: #B0C4DE; font-weight: bold; font-size: 12pt;")
        else:
            self.platinum_change_label.setText(f"{self.pending_platinum_change}")
            self.platinum_change_label.setStyleSheet("color: #EF5350; font-weight: bold; font-size: 12pt;")







    def ease_out_cubic(self, x):
        """缓动函数：缓出立方"""
        return 1 - pow(1 - x, 3)

    def _fetch_user(self):
        if self.user_id is None:
            return None
        return get_user(self.user_id)

    def _on_anim_finished(self, level, xp):
        self.last_level = level
        self.last_xp = xp
        self.level_label.setText(f"Lv {level}")