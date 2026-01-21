from PyQt6.QtCore import QThreadPool, Qt, QSize
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from semver import Version

from src.data import general_info
from src.data.general_info import GeneralInfo
from src.data.general_settings import VERSION, WINDOW_WIDTH, WINDOW_HEIGHT
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
            current_update_version=Version.parse(current_update_version),
            target_directory_path=target_directory_path
        )

        # WINDOW
        self.setWindowTitle('Updater ' + VERSION_PREFIX + VERSION)
        self.setFixedSize(QSize(WINDOW_WIDTH, WINDOW_HEIGHT))

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # CENTER CONTENT
        self.window_content = WindowContent()
        layout.addWidget(self.window_content)

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
