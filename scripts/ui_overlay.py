import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer

app = QApplication(sys.argv)

window = QWidget()
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
window.setAttribute(Qt.WA_TranslucentBackground)
window.setGeometry(100, 100, 400, 200)

label = QLabel('Live Overlay Text', window)
label.setStyleSheet("color: white; font-size: 24px;")
label.move(10, 10)

window.show()

def make_click_through():
    from AppKit import NSApp
    ns_window = NSApp.mainWindow()
    if ns_window is not None:
        ns_window.setIgnoresMouseEvents_(True)
    else:
        print("Warning: NSApp.mainWindow() is None")

# Run after 500ms (half second)
QTimer.singleShot(500, make_click_through)

sys.exit(app.exec_())

