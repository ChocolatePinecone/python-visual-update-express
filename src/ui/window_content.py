import traceback
from enum import Enum
from urllib import request

from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.data import general_info
from src.data.general_settings import DEBUG_MODE
from src.libs.threading import Worker
from src.libs.update_data import UpdateData
from src.ui.notifications import error_notification
from src.ui.status_text_widget import StatusTextWidget

INITIAL_STATUS = 'Ready to update'
CHECKING_FOR_UPDATE = 'Checking for update...'

UPDATESCRIPT_FILENAME = 'updatescript.ini'


class ContentState(Enum):
    CHECK_FOR_UPDATE = 0
    UPDATE_AVAILABLE = 1
    NO_UPDATE = 2
    DOWNLOAD_UPDATE = 3
    INSTALL_UPDATE = 4
    UPDATE_COMPLETE = 5
    UPDATE_FAILED = 6


class WindowContent(QWidget):
    current_state: ContentState

    layout: QVBoxLayout
    status_text: StatusTextWidget
    threadpool: QThreadPool

    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()

        self.status_text = StatusTextWidget(INITIAL_STATUS)
        self._load_content_by_state(ContentState.CHECK_FOR_UPDATE)

    def _clear_content(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(self.layout)

    def _load_content_by_state(self, state: ContentState):
        current_state = state

        self._clear_content()
        match current_state:
            case ContentState.CHECK_FOR_UPDATE:
                self.status_text.set_status(CHECKING_FOR_UPDATE, True)
                self.layout.addWidget(self.status_text)
                self._start_update_check()

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
            update_data = UpdateData(updatescript)
        except Exception as ex:
            self._process_error(ex)

        # Get all supported version numbers
        # Check if current version is in the list
        # Check if a newer version is present
        # IF current version is in list and new version is available
        # change to state: UPDATE_AVAILABLE
        # ELSE
        # change to state: NO_UPDATE

    def _process_error(self, ex: Exception) -> None:
        # Enable below line for debugging
        if DEBUG_MODE:
            error_notification(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)), self)
        else:
            error_notification(str(ex), self)
