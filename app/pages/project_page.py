from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFileDialog,
)


class ProjectPage(QWidget):
    def __init__(self):
        super().__init__()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Dự án")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        box = QGroupBox("Thông tin dự án")
        box_layout = QVBoxLayout(box)

        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Tên dự án, ví dụ: story_001")

        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText("outputs")

        browse_row = QHBoxLayout()
        self.browse_output_btn = QPushButton("Chọn thư mục xuất")
        self.browse_output_btn.clicked.connect(self.choose_output_folder)

        browse_row.addWidget(self.output_folder_input, 1)
        browse_row.addWidget(self.browse_output_btn)

        box_layout.addWidget(QLabel("Tên dự án"))
        box_layout.addWidget(self.project_name_input)
        box_layout.addWidget(QLabel("Thư mục xuất"))
        box_layout.addLayout(browse_row)

        layout.addWidget(box)

        action_row = QHBoxLayout()

        self.new_project_btn = QPushButton("Tạo dự án mới")
        self.import_project_btn = QPushButton("Mở project.json")
        self.save_project_btn = QPushButton("Lưu project.json")
        self.save_project_btn.setObjectName("SuccessButton")

        action_row.addWidget(self.new_project_btn)
        action_row.addWidget(self.import_project_btn)
        action_row.addWidget(self.save_project_btn)
        action_row.addStretch()

        layout.addLayout(action_row)
        layout.addStretch()

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục xuất",
            self.output_folder_input.text().strip() or ".",
        )

        if folder:
            self.output_folder_input.setText(folder)

    def get_data(self) -> dict:
        return {
            "project_name": self.project_name_input.text().strip(),
            "output_folder": self.output_folder_input.text().strip() or "outputs",
        }

    def set_data(self, data: dict):
        self.project_name_input.setText(data.get("project_name", ""))
        self.output_folder_input.setText(data.get("output_folder", "outputs"))

    def clear(self):
        self.project_name_input.clear()
        self.output_folder_input.setText("outputs")