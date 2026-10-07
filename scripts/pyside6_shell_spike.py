import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
)


COMPACT_WIDTH = 440
COMPACT_HEIGHT = 560

BACKGROUND = "#F7F6F3"


class ShellWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Kindle Summary Agent")
        self.setFixedSize(
            COMPACT_WIDTH,
            COMPACT_HEIGHT,
        )

        surface = QWidget()
        surface.setObjectName("productSurface")
        surface.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )
        surface.setStyleSheet(
            f"""
            QWidget#productSurface {{
                background: {BACKGROUND};
            }}
            """
        )

        self.setCentralWidget(surface)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Kindle Summary Agent")

    window = ShellWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()