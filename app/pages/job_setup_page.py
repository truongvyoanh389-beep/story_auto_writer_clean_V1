from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.pages.input_page import InputPage
from app.pages.project_page import ProjectPage


class JobSetupPage(QWidget):
    def __init__(self):
        super().__init__()
        self.project_page = ProjectPage()
        self.input_page = InputPage()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Dự án & Đầu vào")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        form_row = QHBoxLayout()
        form_row.addWidget(self.project_page, 1)
        form_row.addWidget(self.input_page, 2)
        layout.addLayout(form_row, 3)

        job_box = QGroupBox("Danh sách job")
        job_layout = QVBoxLayout(job_box)

        actions = QHBoxLayout()
        self.add_job_btn = QPushButton("Thêm job từ form")
        self.add_job_btn.setObjectName("PrimaryButton")
        self.clear_jobs_btn = QPushButton("Xóa toàn bộ job")
        actions.addWidget(self.add_job_btn)
        actions.addWidget(self.clear_jobs_btn)
        actions.addStretch()
        job_layout.addLayout(actions)

        self.job_table = QTableWidget(0, 7)
        self.job_table.setHorizontalHeaderLabels([
            "Job",
            "Project",
            "Profile",
            "Port",
            "Status",
            "Progress",
            "Step",
        ])
        self.job_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.job_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.job_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.job_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.job_table.verticalHeader().setDefaultSectionSize(36)
        self.job_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        job_layout.addWidget(self.job_table)
        layout.addWidget(job_box, 2)

    def reset_jobs(self):
        self.job_table.setRowCount(0)

    def add_job_row(self, job_id: str, project_name: str, profile_name: str, port: int | str):
        row = self.job_table.rowCount()
        self.job_table.insertRow(row)
        self.job_table.setItem(row, 0, QTableWidgetItem(job_id))
        self.job_table.setItem(row, 1, QTableWidgetItem(project_name))
        self.job_table.setItem(row, 2, QTableWidgetItem(profile_name or "Chưa gán"))
        self.job_table.setItem(row, 3, QTableWidgetItem(str(port or "")))
        self.job_table.setItem(row, 4, QTableWidgetItem("Pending"))
        self.job_table.setItem(row, 5, QTableWidgetItem("0"))
        self.job_table.setItem(row, 6, QTableWidgetItem(""))

    def update_job_row(
        self,
        job_id: str,
        profile_name: str | None = None,
        port: int | str | None = None,
        status: str | None = None,
        progress: int | None = None,
        step: str | None = None,
    ):
        for row in range(self.job_table.rowCount()):
            item = self.job_table.item(row, 0)
            if not item or item.text() != job_id:
                continue

            if profile_name is not None:
                self.job_table.setItem(row, 2, QTableWidgetItem(profile_name or "Chưa gán"))
            if port is not None:
                self.job_table.setItem(row, 3, QTableWidgetItem(str(port or "")))
            if status is not None:
                self.job_table.setItem(row, 4, QTableWidgetItem(status))
            if progress is not None:
                self.job_table.setItem(row, 5, QTableWidgetItem(str(progress)))
            if step is not None:
                self.job_table.setItem(row, 6, QTableWidgetItem(step))
            return
