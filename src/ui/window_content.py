import traceback
from enum import Enum
from urllib import request

from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLayout, QPushButton, QHBoxLayout

from src.data import general_info
from src.data.general_settings import DEBUG_MODE
from src.libs.icons import Icon
from src.libs.threading import Worker
from src.libs.updates_info import UpdatesInfo
from src.ui.notifications import error_notification
from src.ui.status_text_widget import StatusTextWidget

INITIAL_STATUS = 'Ready to update'
CHECKING_FOR_UPDATE = 'Checking for update...'
UP_TO_DATE = 'Your application is already up to date.'
UPDATE_IS_AVAILABLE_TEMPLATE = 'Newer version "{}" has been found and can be downloaded'

UPDATESCRIPT_FILENAME = 'updatescript.ini'


class ContentState(Enum):
    CHECK_FOR_UPDATE = 0
    UPDATE_AVAILABLE = 1
    UP_TO_DATE = 2
    DOWNLOAD_UPDATE = 3
    INSTALL_UPDATE = 4
    UPDATE_COMPLETE = 5
    UPDATE_FAILED = 6


class WindowContent(QWidget):
    current_state: ContentState
    update_failed_text: str = ''
    updates_info: UpdatesInfo

    layout: QVBoxLayout = None
    threadpool: QThreadPool

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 10, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(self.layout)

        self.threadpool = QThreadPool()

        self._load_content_by_state(ContentState.CHECK_FOR_UPDATE)

    def _load_content_by_state(self, state: ContentState):
        current_state = state

        self._clear_layout(self.layout)
        status_text = StatusTextWidget()
        self.layout.addWidget(status_text)

        match current_state:
            case ContentState.CHECK_FOR_UPDATE:
                status_text.set_status(CHECKING_FOR_UPDATE, True)
                self._start_update_check()

            case ContentState.UPDATE_FAILED:
                status_text.set_status(self.update_failed_text, icon=Icon.CROSS_CIRCLE)

            case ContentState.UP_TO_DATE:
                status_text.set_status(UP_TO_DATE, icon=Icon.CHECKMARK_CIRCLE)

            case ContentState.UPDATE_AVAILABLE:
                update_text = UPDATE_IS_AVAILABLE_TEMPLATE.format(
                    self.updates_info.latest_version)
                status_text.set_status(update_text, icon=Icon.CHECKMARK_CIRCLE)
                self.layout.addStretch()
                button_bar = QWidget()
                bar_layout = QHBoxLayout()
                cancel_button = QPushButton('Cancel')
                download_button = QPushButton('Download')
                bar_layout.addStretch()
                bar_layout.addWidget(cancel_button)
                bar_layout.addWidget(download_button)
                button_bar.setLayout(bar_layout)
                self.layout.addWidget(button_bar)

    def _clear_layout(self, layout):
        if isinstance(layout, QLayout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())

    def _start_update_check(self):
        checker = Worker(self._fetch_updatescript, general_info.info.update_base_url)
        checker.signals.successResult.connect(self._process_updatescript)
        checker.signals.error.connect(self._process_error)
        self.threadpool.start(checker)

    def _fetch_updatescript(self, url: str):
        fetch_url = url + UPDATESCRIPT_FILENAME
        with request.urlopen(fetch_url) as response:
            return response.read().decode("utf-8")

    def _process_updatescript(self, updatescript: str):
        try:
            self.updates_info = UpdatesInfo(updatescript)
        except Exception as ex:
            self._process_error(ex)
            self.update_failed_text = 'Failed to parse update info from the update script.'
            self._load_content_by_state(ContentState.UPDATE_FAILED)
            return

        current_version = general_info.info.current_update_version
        if not current_version in self.updates_info.release_versions:
            self.update_failed_text = 'Current version not supported by the update script.'
            self._load_content_by_state(ContentState.UPDATE_FAILED)
            return

        if current_version != self.updates_info.latest_version:
            self._load_content_by_state(ContentState.UPDATE_AVAILABLE)
        else:
            self._load_content_by_state(ContentState.UP_TO_DATE)

    def _process_error(self, ex: Exception) -> None:
        # Enable below line for debugging
        if DEBUG_MODE:
            error_notification(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)), self)
        else:
            error_notification(str(ex), self)
