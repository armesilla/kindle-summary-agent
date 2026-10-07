import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


COMPACT_WIDTH = 440
COMPACT_HEIGHT = 560

BACKGROUND = "#F7F6F3"
PRIMARY_INK = "#1A1A18"
ACCENT = "#E2D44C"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = (
    PROJECT_ROOT
    / "src"
    / "kindle_summary_agent"
    / "resources"
    / "fonts"
)


def load_font(filename: str) -> str:
    font_path = FONTS_DIR / filename

    font_id = QFontDatabase.addApplicationFont(
        str(font_path)
    )

    if font_id == -1:
        raise RuntimeError(
            f"Could not load font: {font_path}"
        )

    families = QFontDatabase.applicationFontFamilies(
        font_id
    )

    if not families:
        raise RuntimeError(
            f"No font family found for: {font_path}"
        )

    return families[0]


class ShellWindow(QMainWindow):
    def __init__(
        self,
        newsreader_family: str,
        geist_family: str,
    ) -> None:
        super().__init__()

        self.newsreader_family = newsreader_family
        self.geist_family = geist_family

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

        layout = QVBoxLayout(surface)
        layout.setContentsMargins(
            28,
            28,
            28,
            28,
        )
        layout.setSpacing(12)

        title = QLabel(
            "Kindle Summary Agent"
        )
        title.setFont(
            QFont(
                self.newsreader_family,
                28,
            )
        )
        title.setStyleSheet(
            f"color: {PRIMARY_INK};"
        )

        body = QLabel(
            "Your Kindle highlights, "
            "turned into useful knowledge."
        )
        body.setWordWrap(True)
        body.setFont(
            QFont(
                self.geist_family,
                13,
            )
        )
        body.setStyleSheet(
            f"color: {PRIMARY_INK};"
        )

        accent = QWidget()
        accent.setFixedHeight(6)
        accent.setStyleSheet(
            f"""
            background: {ACCENT};
            border-radius: 3px;
            """
        )

        layout.addWidget(title)
        layout.addWidget(body)
        layout.addWidget(accent)
        layout.addStretch()

        self.setCentralWidget(surface)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(
        "Kindle Summary Agent"
    )

    newsreader_family = load_font(
        "Newsreader16pt-Regular.ttf"
    )

    geist_family = load_font(
        "Geist-Regular.ttf"
    )

    window = ShellWindow(
        newsreader_family=newsreader_family,
        geist_family=geist_family,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()