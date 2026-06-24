from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ProfilePage(QWidget):
    open_profile_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.profiles = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Chrome Profiles")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        form_box = QGroupBox("Profile")
        form_layout = QVBoxLayout(form_box)

        row1 = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("pro1")

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1000, 99999)
        self.port_spin.setValue(9222)
        self.port_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.profile_dir_edit = QLineEdit("default")

        row1.addWidget(QLabel("Tên"))
        row1.addWidget(self.name_edit, 2)
        row1.addWidget(QLabel("Port"))
        row1.addWidget(self.port_spin)
        row1.addWidget(QLabel("Profile directory"))
        row1.addWidget(self.profile_dir_edit, 2)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.user_data_dir_edit = QLineEdit()
        self.user_data_dir_edit.setPlaceholderText(r"D:\ChromeProfile\pro1")
        self.browse_user_dir_btn = QPushButton("Chọn thư mục")
        self.browse_user_dir_btn.clicked.connect(self.choose_user_data_dir)

        row2.addWidget(QLabel("User data dir"))
        row2.addWidget(self.user_data_dir_edit, 1)
        row2.addWidget(self.browse_user_dir_btn)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.chrome_path_edit = QLineEdit()
        self.chrome_path_edit.setPlaceholderText(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        self.browse_chrome_btn = QPushButton("Chọn chrome.exe")
        self.browse_chrome_btn.clicked.connect(self.choose_chrome_path)

        row3.addWidget(QLabel("Chrome path"))
        row3.addWidget(self.chrome_path_edit, 1)
        row3.addWidget(self.browse_chrome_btn)
        form_layout.addLayout(row3)

        actions = QHBoxLayout()
        self.new_btn = QPushButton("Tạo mới")
        self.save_btn = QPushButton("Lưu profile")
        self.open_chrome_btn = QPushButton("Mở Chrome")
        self.open_chrome_btn.setObjectName("SuccessButton")
        self.refresh_status_btn = QPushButton("Refresh status")
        self.delete_btn = QPushButton("Xóa profile")
        self.delete_btn.setObjectName("DangerButton")

        actions.addWidget(self.new_btn)
        actions.addWidget(self.save_btn)
        actions.addWidget(self.open_chrome_btn)
        actions.addWidget(self.refresh_status_btn)
        actions.addWidget(self.delete_btn)
        actions.addStretch()
        form_layout.addLayout(actions)

        batch = QHBoxLayout()
        self.batch_count_spin = QSpinBox()
        self.batch_count_spin.setRange(1, 20)
        self.batch_count_spin.setValue(3)
        self.batch_count_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.batch_base_port_spin = QSpinBox()
        self.batch_base_port_spin.setRange(1000, 99999)
        self.batch_base_port_spin.setValue(9222)
        self.batch_base_port_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.create_batch_btn = QPushButton("Tạo profile tự động")
        self.open_all_btn = QPushButton("Mở tất cả OFF")
        self.open_all_btn.setObjectName("SuccessButton")

        batch.addWidget(QLabel("Số profile"))
        batch.addWidget(self.batch_count_spin)
        batch.addWidget(QLabel("Base port"))
        batch.addWidget(self.batch_base_port_spin)
        batch.addWidget(self.create_batch_btn)
        batch.addWidget(self.open_all_btn)
        batch.addStretch()
        form_layout.addLayout(batch)

        layout.addWidget(form_box)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Status",
            "Tên",
            "Port",
            "User data dir",
            "Profile directory",
            "Chrome path",
            "Action",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 112)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, 1)

    def choose_user_data_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn user data dir")
        if folder:
            self.user_data_dir_edit.setText(folder)

    def choose_chrome_path(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn chrome.exe",
            r"C:\Program Files\Google\Chrome\Application",
            "Chrome (chrome.exe);;Executable (*.exe);;All files (*.*)",
        )
        if path:
            self.chrome_path_edit.setText(path)

    def get_form_data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "port": self.port_spin.value(),
            "user_data_dir": self.user_data_dir_edit.text().strip(),
            "profile_directory": self.profile_dir_edit.text().strip() or "default",
            "chrome_path": self.chrome_path_edit.text().strip(),
        }

    def set_form_data(self, profile: dict):
        self.name_edit.setText(str(profile.get("name", "")))
        self.port_spin.setValue(int(profile.get("port", 9222)))
        self.user_data_dir_edit.setText(str(profile.get("user_data_dir", "")))
        self.profile_dir_edit.setText(str(profile.get("profile_directory", "default")))
        self.chrome_path_edit.setText(str(profile.get("chrome_path", "")))

    def clear_form(self):
        next_index = len(self.profiles) + 1
        self.set_form_data({
            "name": f"pro{next_index}",
            "port": 9221 + next_index,
            "user_data_dir": rf"D:\ChromeProfile\pro{next_index}",
            "profile_directory": "default",
            "chrome_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        })

    def get_batch_count(self) -> int:
        return self.batch_count_spin.value()

    def get_batch_base_port(self) -> int:
        return self.batch_base_port_spin.value()

    def set_profiles(self, profiles: list[dict], statuses: dict[str, str] | None = None):
        self.profiles = profiles
        statuses = statuses or {}
        self.table.setRowCount(0)

        for profile in profiles:
            name = str(profile.get("name", ""))
            row = self.table.rowCount()
            self.table.insertRow(row)
            status = statuses.get(name, "OFF")
            status_item = QTableWidgetItem(status)
            if status == "RUN":
                status_item.setForeground(QColor("#22c55e"))
            else:
                status_item.setForeground(QColor("#ef4444"))
            self.table.setItem(row, 0, status_item)
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(str(profile.get("port", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(str(profile.get("user_data_dir", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(str(profile.get("profile_directory", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(str(profile.get("chrome_path", ""))))

            open_btn = QPushButton("Mở")
            open_btn.setObjectName("ProfileTableOpenButton")
            open_btn.setFixedSize(72, 30)
            open_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            open_btn.setProperty("profile_name", name)
            open_btn.clicked.connect(self.emit_open_profile)

            button_cell = QWidget()
            button_layout = QHBoxLayout(button_cell)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.addWidget(open_btn)
            self.table.setCellWidget(row, 6, button_cell)

        if profiles and self.table.currentRow() < 0:
            self.table.selectRow(0)

    def selected_profile_name(self) -> str:
        row = self.table.currentRow()
        if row < 0:
            return ""
        item = self.table.item(row, 1)
        return item.text() if item else ""

    def emit_open_profile(self):
        button = self.sender()
        if not button:
            return

        name = button.property("profile_name")
        if name:
            self.open_profile_requested.emit(str(name))
