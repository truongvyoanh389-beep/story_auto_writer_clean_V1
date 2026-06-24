APP_STYLE = """
/* =========================
   Base
   ========================= */

QMainWindow {
    background: #0f172a;
}

QWidget {
    font-family: Segoe UI, Arial;
    font-size: 13px;
    color: #e5e7eb;
    background-color: #0f172a;
}

QLabel {
    color: #e5e7eb;
    background: transparent;
}

/* =========================
   Input fields
   ========================= */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QComboBox {
    background-color: #111827;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 8px;
    color: #f9fafb;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QSpinBox:focus,
QComboBox:focus {
    border: 1px solid #60a5fa;
    background-color: #0b1220;
    color: #ffffff;
}

QLineEdit:disabled,
QTextEdit:disabled,
QPlainTextEdit:disabled,
QSpinBox:disabled,
QComboBox:disabled {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #94a3b8;
}

/* =========================
   QSpinBox
   ========================= */

QSpinBox {
    min-height: 20px;
}

QSpinBox::up-button,
QSpinBox::down-button {
    width: 0px;
    border: none;
}

/* =========================
   QComboBox
   ========================= */

QComboBox {
    min-height: 20px;
    padding-left: 8px;
    padding-right: 28px;
    color: #ffffff;
    background-color: #111827;
}

QComboBox:hover {
    border: 1px solid #60a5fa;
    background-color: #0b1220;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #334155;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    background-color: #1e293b;
}

QComboBox::down-arrow {
    width: 0px;
    height: 0px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #f9fafb;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #111827;
    color: #f9fafb;
    border: 1px solid #475569;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    outline: 0;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 6px 8px;
    color: #f9fafb;
    background-color: #111827;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #1e40af;
    color: #ffffff;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

/* =========================
   Buttons
   ========================= */

QPushButton {
    background-color: #1f2937;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 9px 14px;
    color: #f9fafb;
}

QPushButton:hover {
    background-color: #334155;
    border: 1px solid #64748b;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #64748b;
}

QPushButton#PrimaryButton {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#SuccessButton {
    background-color: #16a34a;
    border: 1px solid #22c55e;
    color: #ffffff;
}

QPushButton#SuccessButton:hover {
    background-color: #15803d;
}

QPushButton#ProfileTableOpenButton {
    background-color: #2563eb;
    border: 1px solid #60a5fa;
    border-radius: 6px;
    padding: 0px;
    color: #ffffff;
    font-weight: 600;
    min-width: 72px;
    max-width: 72px;
    min-height: 30px;
    max-height: 30px;
}

QPushButton#ProfileTableOpenButton:hover {
    background-color: #1d4ed8;
    border: 1px solid #93c5fd;
}

QPushButton#ProfileTableOpenButton:pressed {
    background-color: #1e40af;
    border: 1px solid #60a5fa;
}

QPushButton#DangerButton {
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
}

QPushButton#DangerButton:hover {
    background-color: #b91c1c;
}

/* =========================
   GroupBox
   ========================= */

QGroupBox {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    margin-top: 12px;
    padding: 14px;
    color: #f9fafb;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #ffffff;
    background-color: #0f172a;
}

/* =========================
   Tabs
   ========================= */

QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #0f172a;
}

QTabBar::tab {
    background-color: #1e293b;
    color: #cbd5e1;
    padding: 10px 16px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QTabBar::tab:hover {
    background-color: #334155;
    color: #ffffff;
}

/* =========================
   Progress
   ========================= */

QProgressBar {
    border: 1px solid #334155;
    border-radius: 8px;
    text-align: center;
    background-color: #111827;
    color: #f9fafb;
    min-height: 20px;
}

QProgressBar::chunk {
    background-color: #22c55e;
    border-radius: 8px;
}

/* =========================
   Lists / Tables
   ========================= */

QListWidget,
QTableWidget {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #f9fafb;
    gridline-color: #334155;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QListWidget::item,
QTableWidget::item {
    padding: 8px;
    color: #f9fafb;
    background-color: #111827;
}

QListWidget::item:selected,
QTableWidget::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QListWidget::item:hover,
QTableWidget::item:hover {
    background-color: #1e40af;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #ffffff;
    padding: 7px;
    border: 1px solid #334155;
    font-weight: 600;
}

/* =========================
   Scrollbar
   ========================= */

QScrollBar:vertical {
    background-color: #0f172a;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #475569;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64748b;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0f172a;
    height: 12px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #475569;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #64748b;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* =========================
   QMessageBox / Dialog
   ========================= */

QMessageBox {
    background-color: #111827;
    color: #f9fafb;
}

QMessageBox QLabel {
    color: #f9fafb;
    background-color: transparent;
    font-size: 13px;
    line-height: 1.4;
}

QMessageBox QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    padding: 8px 18px;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #1d4ed8;
}

QDialog {
    background-color: #111827;
    color: #f9fafb;
}

QDialog QLabel {
    color: #f9fafb;
    background-color: transparent;
}

QFileDialog {
    background-color: #111827;
    color: #f9fafb;
}

QFileDialog QLabel,
QFileDialog QTreeView,
QFileDialog QListView,
QFileDialog QLineEdit,
QFileDialog QComboBox {
    color: #f9fafb;
    background-color: #111827;
}

QFileDialog QTreeView::item:selected,
QFileDialog QListView::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}
"""
