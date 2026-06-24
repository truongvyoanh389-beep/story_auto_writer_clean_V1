from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from app.pages.job_setup_page import JobSetupPage
from app.pages.profile_page import ProfilePage
from app.pages.auto_page import AutoPage
from app.pages.write_page import WritePage

from app.controllers.project_controller import ProjectController
from app.controllers.profile_controller import ProfileController
from app.controllers.auto_controller import AutoController
from app.core.app_version import APP_NAME, APP_VERSION, APP_VERSION_LABEL


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} {APP_VERSION_LABEL} - {APP_VERSION}")
        self.resize(1800, 1100)
        self.setMinimumSize(1400, 900)

        self._build_ui()
        self._build_controllers()

    def _build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()

        self.profile_page = ProfilePage()
        self.job_setup_page = JobSetupPage()
        self.project_page = self.job_setup_page.project_page
        self.input_page = self.job_setup_page.input_page
        self.auto_page = AutoPage()
        self.write_page = WritePage()

        self.tabs.addTab(self.profile_page, "Profile Chrome")
        self.tabs.addTab(self.job_setup_page, "Dự án & Đầu vào")
        self.tabs.addTab(self.auto_page, "Auto Gemini")
        self.tabs.addTab(self.write_page, "Nội dung")

        layout.addWidget(self.tabs)

        self.setCentralWidget(root)

    def _build_controllers(self):
        self.project_controller = ProjectController(self)
        self.profile_controller = ProfileController(self)
        self.auto_controller = AutoController(
            main_window=self,
            project_controller=self.project_controller,
        )
