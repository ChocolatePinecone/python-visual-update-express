from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout

from src.data import general_info
from src.data.general_info import GeneralInfo
from src.data.general_settings import VERSION, WINDOW_WIDTH
from src.ui.window_content import WindowContent

VERSION_PREFIX = 'v. '


class UpdaterWindow(QMainWindow):
    window_content: WindowContent

    threadpool: QThreadPool
    centered_on_init: bool = False

    def __init__(self, update_base_url: str, current_update_version: str, target_directory_path: str) -> None:
        super().__init__()

        # GENERAL INFO
        general_info.info = GeneralInfo(
            update_base_url=update_base_url,
            current_update_version=current_update_version,
            target_directory_path=target_directory_path
        )

        # WINDOW
        self.setWindowTitle('Updater')
        self.setMinimumWidth(WINDOW_WIDTH)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 10, 10, 0)

        # CENTER CONTENT
        layout.addSpacing(10)
        self.window_content = WindowContent()
        layout.addWidget(self.window_content)

        # BOTTOM LINE
        layout.addSpacing(10)
        bottom_line = QWidget()
        bottom_line_layout = QHBoxLayout()
        bottom_line_layout.setContentsMargins(0, 0, 0, 0)
        bottom_line_layout.addStretch()

        version_label = QLabel(VERSION_PREFIX + VERSION)
        font = QFont()
        font.setPointSize(10)
        version_label.setFont(font)
        bottom_line_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignRight)

        bottom_line.setLayout(bottom_line_layout)
        layout.addWidget(bottom_line)

        # INITIALIZATION
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.threadpool = QThreadPool()

    # Adjust screen position on resize to center it after resizing in initialization
    def resizeEvent(self, event) -> None:
        if self.centered_on_init:
            return

        center = QGuiApplication.primaryScreen().geometry().center()
        self.move(center - self.rect().center())

        self.centered_on_init = True
        return super().resizeEvent(event)
