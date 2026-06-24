from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)


class ExportPage(QWidget):
    def __init__(self):
        super().__init__()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Export")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        row = QHBoxLayout()

        self.export_btn = QPushButton("Export full_story + timeline")
        self.export_btn.setObjectName("SuccessButton")

        row.addWidget(self.export_btn)
        row.addStretch()

        layout.addLayout(row)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Kết quả export sẽ hiển thị tại đây...")

        layout.addWidget(self.result_text, 1)

    def set_result(self, result: dict):
        lines = ["Export thành công:", ""]

        for key, value in result.items():
            lines.append(f"{key}: {value}")

        self.result_text.setPlainText("\n".join(lines))