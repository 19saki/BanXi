STYLE = """
QWidget {
    background: #0f1720;
    color: #e6eef8;
    font-family: "Segoe UI", "Microsoft YaHei", Arial;
    font-size: 12px;
}
#leftPanel {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0b1220, stop:1 #0f1720);
    border-right: 1px solid rgba(255,255,255,0.03);
}
#userCard {
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
}
#userCard[active="true"] {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #6c63ff);
    color: white;
}
#avatarCircle {
    border-radius: 24px;
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #253046, stop:1 #1b2a3a);
    color: #a8d0ff;
}
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
QListWidget {
    background: rgba(255,255,255,0.02);
    border-radius: 8px;
    padding: 4px;
    outline: none;
    border: none;
}
QListWidget::item {
    background: rgba(255,255,255,0.02);
    margin: 2px;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.05);
}
QListWidget::item:hover {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
}
QListWidget::item:selected {
    background: rgba(255,255,255,0.03);
}
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
QProgressBar {
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #6c63ff, stop:1 #1f6feb);
    border-radius: 8px;
}
#completeBtn {
    background: rgba(34, 197, 94, 0.7);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 11px;
    padding: 6px 8px;
    font-weight: 500;
    min-width: 50px;
    min-height: 32px;
}
#completeBtn:hover {
    background: rgba(34, 197, 94, 0.9);
}
#completeBtn:disabled {
    background: rgba(100, 100, 100, 0.2);
    color: rgba(255, 255, 255, 0.4);
}

/* 自定义任务项样式 */
.task-item {
    background: transparent;
    border: none;
    border-radius: 6px;
}
.task-item:hover {
    background: rgba(255,255,255,0.05);
}
"""