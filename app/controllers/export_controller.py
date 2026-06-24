from PyQt6.QtWidgets import QMessageBox

from app.core.export_builder import ExportBuilder


class ExportController:
    def __init__(self, main_window, project_controller):
        self.main_window = main_window
        self.project_controller = project_controller

        self._connect()

    def _connect(self):
        self.main_window.export_page.export_btn.clicked.connect(self.export)

    def export(self):
        try:
            project = self.project_controller.collect()

            result = ExportBuilder.export(project)

            self.main_window.export_page.set_result(result)
            self.main_window.auto_page.log("Export thành công.")

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi export",
                str(e),
            )