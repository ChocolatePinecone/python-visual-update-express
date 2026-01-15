from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from pyqtwaitingspinner import WaitingSpinner, SpinnerParameters, SpinDirection

SPINNER_PARAMS = SpinnerParameters(  # These can be generated in the spinner editor `spinner-conf`
    roundness=100.0,
    trail_fade_percentage=50.0,
    number_of_lines=13,
    line_length=5,
    line_width=2,
    inner_radius=3,
    revolutions_per_second=1.57,
    color=QColor(80, 80, 80),
    minimum_trail_opacity=3.14,
    spin_direction=SpinDirection.CLOCKWISE,
    center_on_parent=True,
    disable_parent_when_spinning=False,
)
SPINNER_WIDGET_WIDTH = 20
SPINNER_WIDGET_HEIGHT = 20


class StatusTextWidget(QWidget):
    status_text: QLabel
    spinner_widget: QWidget
    spinner: WaitingSpinner

    initial_status: str

    def __init__(self, initial_status_text: str):
        super().__init__()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.initial_status = initial_status_text
        self.status_text = QLabel(initial_status_text)
        self.status_text.setFixedHeight(
            SPINNER_WIDGET_HEIGHT)  # Prevents vertical repositioning when spinner is activated
        font = QFont()
        font.setPointSize(10)
        self.status_text.setFont(font)
        layout.addWidget(self.status_text)

        self.spinner_widget = QWidget()
        self.spinner = WaitingSpinner(self.spinner_widget, SPINNER_PARAMS)
        self.set_spinner_active(False)
        layout.addWidget(self.spinner_widget)

        self.setLayout(layout)

    def set_spinner_active(self, active: bool):
        if active:
            self.spinner.start()
            self.spinner_widget.setFixedSize(SPINNER_WIDGET_WIDTH, SPINNER_WIDGET_HEIGHT)
        else:
            self.spinner.stop()
            self.spinner_widget.setFixedSize(0, 0)

    def set_status(self, status: str, spinner: bool = False):
        self.status_text.setText(status)
        self.status_text.setStyleSheet('')
        self.set_spinner_active(spinner)

    def set_warning_status(self, status: str):
        self.status_text.setText(status)
        self.status_text.setStyleSheet('color: red;')

    def reset_status(self):
        self.status_text.setText(self.initial_status)
        self.status_text.setStyleSheet('')
        self.set_spinner_active(False)
