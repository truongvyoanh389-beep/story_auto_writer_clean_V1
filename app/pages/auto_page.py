from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QProgressBar,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class AutoPage(QWidget):
    STEPS = [
        ("01_input_analysis", "Phân tích đầu vào"),
        ("02_premises", "Tạo 10 ý tưởng"),
        ("03_select_premise", "Chọn ý tưởng tốt nhất"),
        ("04_story_bible", "Tạo Story Bible"),
        ("05_outline", "Tạo Outline"),
        ("06_hook", "Viết Hook"),
        ("07_chapter_01", "Viết Chapter 1"),
        ("08_chapter_02", "Viết Chapter 2"),
        ("09_chapter_03", "Viết Chapter 3"),
        ("10_chapter_04", "Viết Chapter 4"),
        ("11_chapter_05", "Viết Chapter 5"),
        ("12_chapter_06", "Viết Chapter 6"),
        ("13_chapter_07", "Viết Chapter 7"),
        ("14_chapter_08", "Viết Chapter 8"),
        ("15_chapter_09", "Viết Chapter 9"),
        ("16_chapter_10", "Viết Chapter 10"),
        ("17_script_evaluation", "So sánh script gốc / mới"),
        ("18_final_repair", "Final repair / editor pass"),
        ("19_segment_script", "Segment + role script"),
        ("20_thumbnail_prompt", "SEO meta + prompt thumbnail"),
    ]

    def __init__(self):
        super().__init__()
        self.step_row_map = {}
        self.profiles = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Auto Gemini")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        top = QHBoxLayout()

        self.job_combo = QComboBox()
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.on_profile_changed)

        self.assign_profile_btn = QPushButton("Gán profile cho job")
        self.assign_profile_btn.setObjectName("PrimaryButton")

        self.start_queue_btn = QPushButton("Chạy Job")
        self.start_queue_btn.setObjectName("SuccessButton")

        self.stop_queue_btn = QPushButton("Dừng Job")
        self.stop_queue_btn.setObjectName("DangerButton")
        self.stop_queue_btn.setEnabled(False)

        top.addWidget(QLabel("Job"))
        top.addWidget(self.job_combo, 2)
        top.addWidget(QLabel("Profile rảnh"))
        top.addWidget(self.profile_combo, 2)
        top.addWidget(self.assign_profile_btn)
        top.addWidget(self.start_queue_btn)
        top.addWidget(self.stop_queue_btn)
        top.addStretch()

        layout.addLayout(top)

        settings_box = QGroupBox("Cài đặt")
        settings_layout = QHBoxLayout(settings_box)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1000, 99999)
        self.port_spin.setValue(9222)
        self.port_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.wait_spin = QSpinBox()
        self.wait_spin.setRange(30, 1800)
        self.wait_spin.setValue(300)
        self.wait_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.hook_segment_spin = QSpinBox()
        self.hook_segment_spin.setRange(20, 120)
        self.hook_segment_spin.setValue(45)
        self.hook_segment_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.chapter_segment_spin = QSpinBox()
        self.chapter_segment_spin.setRange(40, 180)
        self.chapter_segment_spin.setValue(85)
        self.chapter_segment_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.auto_launch_chrome_check = QCheckBox("Tự mở Chrome khi chạy job")
        self.auto_launch_chrome_check.setChecked(True)

        settings_layout.addWidget(QLabel("Timeout tối đa mỗi bước, giây"))
        settings_layout.addWidget(self.wait_spin)
        settings_layout.addWidget(QLabel("Hook segment words"))
        settings_layout.addWidget(self.hook_segment_spin)
        settings_layout.addWidget(QLabel("Chapter segment words"))
        settings_layout.addWidget(self.chapter_segment_spin)
        settings_layout.addWidget(self.auto_launch_chrome_check)
        settings_layout.addStretch()

        layout.addWidget(settings_box)

        queue_box = QGroupBox("Job queue")
        queue_layout = QVBoxLayout(queue_box)

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
        queue_layout.addWidget(self.job_table)

        layout.addWidget(queue_box, 1)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Chưa chạy auto.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.status_label)

        step_box = QGroupBox("Process realtime")
        step_layout = QVBoxLayout(step_box)

        self.step_table = QTableWidget(0, 4)
        self.step_table.setHorizontalHeaderLabels([
            "Step",
            "Trạng thái",
            "Thông báo",
            "Response preview",
        ])
        self.step_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.step_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.step_table.itemSelectionChanged.connect(self.on_step_selected)

        step_layout.addWidget(self.step_table)

        layout.addWidget(step_box, 2)

        body = QHBoxLayout()

        log_box = QGroupBox("Log realtime")
        log_layout = QVBoxLayout(log_box)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        response_box = QGroupBox("Response của step đang chọn / response cuối")
        response_layout = QVBoxLayout(response_box)

        self.response_text = QTextEdit()
        response_layout.addWidget(self.response_text)

        body.addWidget(log_box, 1)
        body.addWidget(response_box, 1)

        layout.addLayout(body, 2)

        self.reset_steps()

    def get_port(self) -> int:
        profile = self.get_selected_profile()
        if profile:
            return int(profile.get("port", self.port_spin.value()))
        return self.port_spin.value()

    def set_profiles(self, profiles: list[dict]):
        current_name = ""
        current_profile = self.get_selected_profile()
        if current_profile:
            current_name = current_profile.get("name", "")

        self.profiles = profiles or []
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()

        for profile in self.profiles:
            self.profile_combo.addItem(
                f"{profile.get('name', '')} : {profile.get('port', '')}",
                profile.get("name", ""),
            )

        if current_name:
            for index, profile in enumerate(self.profiles):
                if profile.get("name") == current_name:
                    self.profile_combo.setCurrentIndex(index)
                    break

        self.profile_combo.blockSignals(False)
        self.on_profile_changed()

    def get_selected_profile(self) -> dict | None:
        index = self.profile_combo.currentIndex()
        if index < 0 or index >= len(self.profiles):
            return None
        return self.profiles[index]

    def on_profile_changed(self):
        profile = self.get_selected_profile()
        if profile:
            self.port_spin.setValue(int(profile.get("port", self.port_spin.value())))

    def get_wait_seconds(self) -> int:
        return self.wait_spin.value()

    def get_hook_segment_words(self) -> int:
        return self.hook_segment_spin.value()

    def get_chapter_segment_words(self) -> int:
        return self.chapter_segment_spin.value()

    def get_max_parallel_jobs(self) -> int:
        return 1

    def should_auto_launch_chrome(self) -> bool:
        return self.auto_launch_chrome_check.isChecked()

    def set_running_state(self, running: bool):
        pass

    def set_queue_running_state(self, running: bool):
        self.assign_profile_btn.setEnabled(True)
        self.start_queue_btn.setEnabled(True)
        self.stop_queue_btn.setEnabled(running)

    def set_status(self, text: str, progress: int | None = None):
        self.status_label.setText(text)
        if progress is not None:
            self.progress.setValue(progress)

    def log(self, text: str):
        self.log_text.append(text)

    def set_response(self, text: str):
        self.response_text.setPlainText(text or "")

    def reset_jobs(self):
        self.job_table.setRowCount(0)
        self.job_combo.clear()

    def add_job_row(self, job_id: str, project_name: str, profile_name: str, port: int):
        row = self.job_table.rowCount()
        self.job_table.insertRow(row)
        self.job_table.setItem(row, 0, QTableWidgetItem(job_id))
        self.job_table.setItem(row, 1, QTableWidgetItem(project_name))
        self.job_table.setItem(row, 2, QTableWidgetItem(profile_name))
        self.job_table.setItem(row, 3, QTableWidgetItem(str(port)))
        self.job_table.setItem(row, 4, QTableWidgetItem("Pending"))
        self.job_table.setItem(row, 5, QTableWidgetItem("0"))
        self.job_table.setItem(row, 6, QTableWidgetItem(""))
        self.job_combo.addItem(f"{job_id} - {project_name}", job_id)

        if self.job_combo.count() == 1:
            self.job_combo.setCurrentIndex(0)
            self.job_table.selectRow(0)

    def get_selected_job_id(self) -> str:
        index = self.job_combo.currentIndex()
        if index >= 0:
            value = self.job_combo.itemData(index)
            return str(value or "")

        rows = self.job_table.selectionModel().selectedRows()
        if rows:
            item = self.job_table.item(rows[0].row(), 0)
            return item.text() if item else ""

        return ""

    def set_current_job(self, job_id: str):
        for index in range(self.job_combo.count()):
            if self.job_combo.itemData(index) == job_id:
                self.job_combo.setCurrentIndex(index)
                break

        for row in range(self.job_table.rowCount()):
            item = self.job_table.item(row, 0)
            if item and item.text() == job_id:
                self.job_table.selectRow(row)
                break

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

    def reset_steps(self):
        self.step_table.setRowCount(0)
        self.step_row_map = {}

        for key, name in self.STEPS:
            row = self.step_table.rowCount()
            self.step_table.insertRow(row)
            self.step_row_map[key] = row

            self.step_table.setItem(row, 0, QTableWidgetItem(name))
            self.step_table.setItem(row, 1, QTableWidgetItem("Chờ chạy"))
            self.step_table.setItem(row, 2, QTableWidgetItem(""))
            self.step_table.setItem(row, 3, QTableWidgetItem(""))

    def update_step(self, key: str, status: str, message: str = "", response_preview: str = ""):
        if key not in self.step_row_map:
            row = self.step_table.rowCount()
            self.step_table.insertRow(row)
            self.step_row_map[key] = row
            self.step_table.setItem(row, 0, QTableWidgetItem(key))
            self.step_table.setItem(row, 1, QTableWidgetItem(""))
            self.step_table.setItem(row, 2, QTableWidgetItem(""))
            self.step_table.setItem(row, 3, QTableWidgetItem(""))

        row = self.step_row_map[key]

        self.step_table.setItem(row, 1, QTableWidgetItem(status))
        self.step_table.setItem(row, 2, QTableWidgetItem(message))
        self.step_table.setItem(row, 3, QTableWidgetItem(response_preview[:300] if response_preview else ""))

        self.step_table.selectRow(row)

    def on_step_selected(self):
        rows = self.step_table.selectionModel().selectedRows()

        if not rows:
            return

        row = rows[0].row()
        preview_item = self.step_table.item(row, 3)

        if preview_item:
            # Không set response full ở đây vì table chỉ có preview.
            pass
