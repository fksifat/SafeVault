"""Shared UI styling for SafeVault."""


from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication


DARK_STYLESHEET = """
QMainWindow, QWidget {
    background: #202326;
    color: #f3f5f7;
    font-family: "Inter", "Segoe UI", "Ubuntu", "Arial";
    font-size: 14px;
}

QMenuBar {
    background: #202326;
    color: #dce3ea;
    padding: 2px 6px;
}

QMenuBar::item {
    padding: 6px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected, QMenu {
    background: #2b3035;
}

QTabWidget::pane {
    border: 1px solid #3a4148;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background: #272b30;
    border: 1px solid #3a4148;
    border-bottom: 0;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #dce3ea;
}

QTabBar::tab:selected {
    background: #30363c;
    color: #ffffff;
}

QTabBar::tab:hover {
    background: #363d44;
}

QLabel#PageTitle {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
}

QLabel, QCheckBox {
    background: transparent;
}

QLabel#SectionTitle {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#MutedText {
    color: #aab4bf;
}

QFrame#Panel, QFrame#StatCard {
    background: #282d32;
    border: 1px solid #3b424a;
    border-radius: 8px;
}

QFrame#StatCard QLabel {
    background: transparent;
}

QLabel#StatValue {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
}

QLineEdit, QComboBox, QSpinBox {
    background: #1f2327;
    border: 1px solid #48515a;
    border-radius: 6px;
    padding: 7px 9px;
    min-height: 20px;
    color: #f3f5f7;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #7da2ce;
}

QPushButton {
    background: #30363c;
    border: 1px solid #515b66;
    border-radius: 6px;
    color: #f3f5f7;
    padding: 7px 13px;
    min-height: 20px;
}

QPushButton:hover {
    background: #3a424a;
}

QPushButton:pressed {
    background: #252a30;
}

QPushButton#PrimaryButton {
    background: #2f6fab;
    border-color: #3e83c3;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#PrimaryButton:hover {
    background: #367dbc;
}

QPushButton#QuietButton {
    background: transparent;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #56616c;
    border-radius: 3px;
    background: #1f2327;
}

QCheckBox::indicator:hover {
    border-color: #7da2ce;
}

QCheckBox::indicator:checked {
    background: #2f6fab;
    border-color: #3e83c3;
}

QTreeWidget, QTableWidget {
    background: #1f2327;
    alternate-background-color: #242a2f;
    border: 1px solid #3b424a;
    border-radius: 6px;
    gridline-color: #343b42;
    selection-background-color: #34516d;
    selection-color: #ffffff;
}

QHeaderView::section {
    background: #30363c;
    border: 0;
    border-right: 1px solid #424a53;
    border-bottom: 1px solid #424a53;
    color: #e9eef3;
    font-weight: 600;
    padding: 7px 9px;
}

QTableWidget::item, QTreeWidget::item {
    padding: 6px 8px;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background: #34516d;
    color: #ffffff;
}

QScrollBar:vertical {
    background: #1f2327;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: #4a535d;
    border-radius: 6px;
    min-height: 28px;
}
"""


LIGHT_STYLESHEET = """
QMainWindow, QWidget {
    background: #f4f6f8;
    color: #1f2933;
    font-family: "Inter", "Segoe UI", "Ubuntu", "Arial";
    font-size: 14px;
}

QMenuBar {
    background: #f4f6f8;
    color: #1f2933;
    padding: 2px 6px;
}

QMenuBar::item {
    padding: 6px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected, QMenu {
    background: #e5eaf0;
}

QTabWidget::pane {
    border: 1px solid #c9d2dc;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background: #e8edf3;
    border: 1px solid #c9d2dc;
    border-bottom: 0;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #314151;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #111827;
}

QTabBar::tab:hover {
    background: #f8fafc;
}

QLabel, QCheckBox {
    background: transparent;
}

QLabel#PageTitle {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
}

QLabel#SectionTitle {
    font-size: 16px;
    font-weight: 700;
    color: #111827;
}

QLabel#MutedText {
    color: #5f6f80;
}

QFrame#Panel, QFrame#StatCard {
    background: #ffffff;
    border: 1px solid #cbd5df;
    border-radius: 8px;
}

QFrame#StatCard QLabel {
    background: transparent;
}

QLabel#StatValue {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
}

QLineEdit, QComboBox, QSpinBox {
    background: #ffffff;
    border: 1px solid #b8c4cf;
    border-radius: 6px;
    padding: 7px 9px;
    min-height: 20px;
    color: #1f2933;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #256fb3;
}

QPushButton {
    background: #ffffff;
    border: 1px solid #b8c4cf;
    border-radius: 6px;
    color: #1f2933;
    padding: 7px 13px;
    min-height: 20px;
}

QPushButton:hover {
    background: #eef3f8;
}

QPushButton:pressed {
    background: #dde6ef;
}

QPushButton#PrimaryButton {
    background: #256fb3;
    border-color: #1f5f9b;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#PrimaryButton:hover {
    background: #2f7fc9;
}

QPushButton#QuietButton {
    background: transparent;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #9eacba;
    border-radius: 3px;
    background: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #256fb3;
}

QCheckBox::indicator:checked {
    background: #256fb3;
    border-color: #1f5f9b;
}

QTreeWidget, QTableWidget {
    background: #ffffff;
    alternate-background-color: #f5f7fa;
    border: 1px solid #cbd5df;
    border-radius: 6px;
    gridline-color: #d8e0e8;
    selection-background-color: #cfe2f6;
    selection-color: #111827;
}

QHeaderView::section {
    background: #e9eef4;
    border: 0;
    border-right: 1px solid #cbd5df;
    border-bottom: 1px solid #cbd5df;
    color: #1f2933;
    font-weight: 600;
    padding: 7px 9px;
}

QTableWidget::item, QTreeWidget::item {
    padding: 6px 8px;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background: #cfe2f6;
    color: #111827;
}

QScrollBar:vertical {
    background: #f4f6f8;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: #b8c4cf;
    border-radius: 6px;
    min-height: 28px;
}
"""


APP_STYLESHEET = DARK_STYLESHEET


def get_app_stylesheet(theme: str) -> str:
    """Return the stylesheet for a saved theme option."""
    theme = (theme or "Dark").lower()
    if theme == "light":
        return LIGHT_STYLESHEET
    if theme == "system":
        app = QApplication.instance()
        if app and app.palette().color(QPalette.ColorRole.Window).lightness() > 128:
            return LIGHT_STYLESHEET
    return DARK_STYLESHEET
