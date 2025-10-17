from PySide6 import QtWidgets, QtCore, QtGui

class LeftUserCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(int)

    def __init__(self, user_id, name, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setFixedHeight(80)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setObjectName("userCard")


        h = QtWidgets.QHBoxLayout()
        h.setContentsMargins(10, 10, 10, 10)
        h.setSpacing(10)
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

        v = QtWidgets.QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        v.setSpacing(0)  # 移除间距

        self.name_label = QtWidgets.QLabel(name)
        self.name_label.setObjectName("userName")
        self.name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # 文字水平居中

        v.addStretch()  # 在上方添加弹性空间
        v.addWidget(self.name_label)
        v.addStretch()  # 在下方添加弹性空间

        h.addLayout(v)
        h.addStretch()  # 在右侧添加弹性空间，让整体居中
        self.setLayout(h)

    def mousePressEvent(self, e):
        self.clicked.emit(self.user_id)
