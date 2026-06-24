from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QGroupBox,
)


class WritePage(QWidget):
    def __init__(self):
        super().__init__()

        self.chapters = []
        self.script_evaluation = ""
        self.final_repair = ""
        self.segment_script = ""
        self.thumbnail_prompt = ""

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Nội dung truyện")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Job"))
        self.job_combo = QComboBox()
        selector_row.addWidget(self.job_combo, 1)
        selector_row.addStretch()
        layout.addLayout(selector_row)

        body = QHBoxLayout()

        left_box = QGroupBox("Danh sách")
        left_layout = QVBoxLayout(left_box)

        self.chapter_list = QListWidget()
        self.chapter_list.addItem(QListWidgetItem("SEO Meta + Thumbnail Prompt"))
        self.chapter_list.addItem(QListWidgetItem("Script Evaluation"))
        self.chapter_list.addItem(QListWidgetItem("Final Repair"))
        self.chapter_list.addItem(QListWidgetItem("Segment Script"))
        self.chapter_list.addItem(QListWidgetItem("Hook"))

        for i in range(1, 11):
            self.chapter_list.addItem(QListWidgetItem(f"Chapter {i}"))

        self.chapter_list.currentRowChanged.connect(self.on_selected)

        left_layout.addWidget(self.chapter_list)

        right_box = QGroupBox("Text")
        right_layout = QVBoxLayout(right_box)

        self.editor = QTextEdit()
        self.editor.setReadOnly(False)
        right_layout.addWidget(self.editor)

        self.info_label = QLabel("Số từ: 0")
        self.info_label.setStyleSheet("color: #94a3b8;")
        right_layout.addWidget(self.info_label)

        body.addWidget(left_box, 1)
        body.addWidget(right_box, 3)

        layout.addLayout(body, 1)

        self.chapter_list.setCurrentRow(0)

    def set_jobs(self, jobs: list[dict]):
        current = self.job_combo.currentData()
        self.job_combo.blockSignals(True)
        self.job_combo.clear()

        for job in jobs:
            project = job.get("project")
            project_name = getattr(project, "project_name", "") if project else ""
            self.job_combo.addItem(
                f"{job.get('id', '')} - {project_name}",
                job.get("id", ""),
            )

        if current:
            for index in range(self.job_combo.count()):
                if self.job_combo.itemData(index) == current:
                    self.job_combo.setCurrentIndex(index)
                    break

        self.job_combo.blockSignals(False)

    def get_selected_job_id(self) -> str:
        value = self.job_combo.currentData()
        return str(value or "")

    def set_current_job(self, job_id: str):
        for index in range(self.job_combo.count()):
            if self.job_combo.itemData(index) == job_id:
                self.job_combo.setCurrentIndex(index)
                return

    def set_chapters(self, chapters: list[dict]):
        self.chapters = chapters or []
        self.refresh_list()
        self.on_selected(self.chapter_list.currentRow())

    def set_script_evaluation(self, text: str):
        self.script_evaluation = text or ""
        self.refresh_list()
        self.on_selected(self.chapter_list.currentRow())

    def set_final_repair(self, text: str):
        self.final_repair = text or ""
        self.refresh_list()
        self.on_selected(self.chapter_list.currentRow())

    def set_segment_script(self, text: str):
        self.segment_script = text or ""
        self.refresh_list()
        self.on_selected(self.chapter_list.currentRow())

    def set_thumbnail_prompt(self, text: str):
        self.thumbnail_prompt = text or ""
        self.refresh_list()
        self.on_selected(self.chapter_list.currentRow())

    def get_chapters(self) -> list[dict]:
        return self.chapters

    def upsert_chapter(self, chapter_data: dict):
        key = chapter_data.get("chapter_number")

        for index, chapter in enumerate(self.chapters):
            if chapter.get("chapter_number") == key:
                self.chapters[index] = chapter_data
                self.refresh_list()
                return

            try:
                if key != "hook" and int(chapter.get("chapter_number")) == int(key):
                    self.chapters[index] = chapter_data
                    self.refresh_list()
                    return
            except Exception:
                pass

        self.chapters.append(chapter_data)
        self.refresh_list()

    def on_selected(self, row: int):
        if row == 0:
            text = getattr(self, "thumbnail_prompt", "")
            self.editor.setPlainText(text)
            self.info_label.setText(f"Số từ: {len(text.split())}")
            return

        if row == 1:
            text = getattr(self, "script_evaluation", "")
            self.editor.setPlainText(text)
            self.info_label.setText(f"Số từ: {len(text.split())}")
            return

        if row == 2:
            text = getattr(self, "final_repair", "")
            self.editor.setPlainText(text)
            self.info_label.setText(f"Số từ: {len(text.split())}")
            return

        if row == 3:
            text = getattr(self, "segment_script", "")
            self.editor.setPlainText(text)
            self.info_label.setText(f"Số từ: {len(text.split())}")
            return

        key = "hook" if row == 4 else row - 4
        chapter = self.find_chapter(key)

        if chapter:
            text = chapter.get("text", "")
        else:
            text = ""

        self.editor.setPlainText(text)
        self.info_label.setText(f"Số từ: {len(text.split())}")

    def find_chapter(self, key):
        for chapter in self.chapters:
            if chapter.get("chapter_number") == key:
                return chapter

            try:
                if key != "hook" and int(chapter.get("chapter_number")) == int(key):
                    return chapter
            except Exception:
                pass

        return None

    def refresh_list(self):
        thumbnail = getattr(self, "thumbnail_prompt", "")
        thumbnail_item = self.chapter_list.item(0)
        if thumbnail_item:
            thumbnail_item.setText("SEO Meta + Thumbnail Prompt - OK" if thumbnail else "SEO Meta + Thumbnail Prompt - Chưa có")

        evaluation = getattr(self, "script_evaluation", "")
        evaluation_item = self.chapter_list.item(1)
        if evaluation_item:
            evaluation_item.setText("Script Evaluation - OK" if evaluation else "Script Evaluation - Chưa có")

        repair = getattr(self, "final_repair", "")
        repair_item = self.chapter_list.item(2)
        if repair_item:
            repair_item.setText("Final Repair - OK" if repair else "Final Repair - Chưa có")

        segment = getattr(self, "segment_script", "")
        segment_item = self.chapter_list.item(3)
        if segment_item:
            segment_item.setText("Segment Script - OK" if segment else "Segment Script - Chưa có")

        for row in range(self.chapter_list.count()):
            if row in {0, 1, 2, 3}:
                continue
            item = self.chapter_list.item(row)
            key = "hook" if row == 4 else row - 4
            chapter = self.find_chapter(key)

            if row == 4:
                base = "Hook"
            else:
                base = f"Chapter {row - 4}"

            if not chapter:
                item.setText(f"{base} - Chưa viết")
                continue

            word_count = chapter.get("word_count", 0)
            status = chapter.get("status", "done")

            if status == "done":
                item.setText(f"{base} - OK ({word_count} từ)")
            else:
                item.setText(f"{base} - {status} ({word_count} từ)")
