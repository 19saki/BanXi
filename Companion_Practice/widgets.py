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
        self.name_label = QtWidgets.QLabel(name)
        self.name_label.setObjectName("userName")
        v.addWidget(self.name_label)
        v.addStretch()
        h.addLayout(v)
        self.setLayout(h)

    def mousePressEvent(self, e):
        self.clicked.emit(self.user_id)
