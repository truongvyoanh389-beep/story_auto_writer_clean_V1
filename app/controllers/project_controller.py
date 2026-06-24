from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from app.core.project_model import StoryProject
from app.core.project_io import ProjectIO


class ProjectController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.project = StoryProject()
        self.project_path = None

        self._connect()

    def _connect(self):
        page = self.main_window.project_page

        page.new_project_btn.clicked.connect(self.new_project)
        page.import_project_btn.clicked.connect(self.import_project)
        page.save_project_btn.clicked.connect(self.save_project)

    def collect(self) -> StoryProject:
        project_data = self.main_window.project_page.get_data()
        input_data = self.main_window.input_page.get_data()

        self.project.project_name = project_data["project_name"]
        self.project.output_folder = project_data["output_folder"]

        self.project.title = input_data["title"]
        self.project.transcript = input_data["transcript"]

        self.project.target_words = input_data["target_words"]
        self.project.narration_pov = input_data["narration_pov"]
        self.project.target_audience = input_data["target_audience"]
        self.project.tone = input_data["tone"]
        self.project.revenge_intensity = input_data["revenge_intensity"]
        self.project.ending_type = input_data["ending_type"]
        self.project.niche = input_data["niche"]

        self.project.chapters = self.main_window.write_page.get_chapters()

        return self.project

    def apply(self, project: StoryProject):
        self.project = project

        self.main_window.project_page.set_data({
            "project_name": project.project_name,
            "output_folder": project.output_folder,
        })

        self.main_window.input_page.set_data({
            "title": project.title,
            "transcript": project.transcript,
            "target_words": project.target_words,
            "narration_pov": project.narration_pov,
            "target_audience": project.target_audience,
            "tone": project.tone,
            "revenge_intensity": project.revenge_intensity,
            "ending_type": project.ending_type,
            "niche": project.niche
        })

        self.main_window.write_page.set_chapters(project.chapters)

    def new_project(self):
        self.project = StoryProject()
        self.project_path = None

        self.main_window.project_page.clear()
        self.main_window.input_page.clear()
        self.main_window.write_page.set_chapters([])

        self.main_window.auto_page.log("Đã tạo dự án mới.")

    def import_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Mở project.json",
            "",
            "Project JSON (*.json)",
        )

        if not file_path:
            return

        try:
            project = ProjectIO.load(file_path)
            self.project_path = Path(file_path)
            self.apply(project)

            self.main_window.auto_page.log(f"Đã mở project: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi mở project",
                str(e),
            )

    def save_project(self):
        try:
            project = self.collect()
            path = ProjectIO.save(project)
            self.project_path = path

            self.main_window.auto_page.log(f"Đã lưu project: {path}")

            QMessageBox.information(
                self.main_window,
                "Đã lưu",
                f"Đã lưu project:\n{path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi lưu project",
                str(e),
            )

    def autosave(self):
        project = self.collect()

        if not project.project_name:
            project.project_name = ProjectIO.safe_name(project.title or "untitled_project")

        path = ProjectIO.save(project)
        self.project_path = path

        self.main_window.auto_page.log(f"Autosave: {path}")

        return path
