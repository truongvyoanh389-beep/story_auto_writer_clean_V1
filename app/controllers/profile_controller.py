from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from app.core.chrome_launcher import ChromeLauncher
from app.core.chrome_profile_store import ChromeProfileStore


class ProfileController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.page = main_window.profile_page
        self.profiles = []
        self._connect()
        self.reload()

    def _connect(self):
        self.page.new_btn.clicked.connect(self.new_profile)
        self.page.save_btn.clicked.connect(self.save_profile)
        self.page.delete_btn.clicked.connect(self.delete_profile)
        self.page.open_chrome_btn.clicked.connect(self.open_chrome)
        self.page.refresh_status_btn.clicked.connect(self.refresh_statuses)
        self.page.create_batch_btn.clicked.connect(self.create_batch_profiles)
        self.page.open_all_btn.clicked.connect(self.open_all_off_profiles)
        self.page.open_profile_requested.connect(self.open_chrome_by_name)
        self.page.table.itemSelectionChanged.connect(self.on_selected)

    def reload(self):
        self.profiles = ChromeProfileStore.load()
        self.page.set_profiles(self.profiles, self.profile_statuses())
        self.sync_auto_profiles()

        if self.profiles:
            self.page.set_form_data(self.profiles[0])

    def sync_auto_profiles(self):
        auto_controller = getattr(self.main_window, "auto_controller", None)
        if auto_controller:
            auto_controller.refresh_available_profiles()
        elif hasattr(self.main_window, "auto_page"):
            self.main_window.auto_page.set_profiles(self.profiles)

    def new_profile(self):
        self.page.clear_form()

    def create_batch_profiles(self):
        count = self.page.get_batch_count()
        base_port = self.page.get_batch_base_port()
        used_ports = {int(profile.get("port", 0) or 0) for profile in self.profiles}
        existing_names = {profile.get("name", "") for profile in self.profiles}
        chrome_path = self.page.chrome_path_edit.text().strip() or ChromeProfileStore.DEFAULT_CHROME_PATH
        created = []

        for _ in range(count):
            index = 1
            while f"pro{index}" in existing_names:
                index += 1

            name = f"pro{index}"
            existing_names.add(name)
            port = ChromeLauncher.find_free_port(base_port, used_ports)
            used_ports.add(port)

            created.append(ChromeProfileStore.normalize({
                "name": name,
                "port": port,
                "user_data_dir": str(Path(ChromeProfileStore.DEFAULT_BASE_DIR) / name),
                "profile_directory": "default",
                "chrome_path": chrome_path,
            }))

        self.profiles.extend(created)
        ChromeProfileStore.save(self.profiles)
        self.page.set_profiles(self.profiles, self.profile_statuses())
        self.sync_auto_profiles()

        if created:
            self.select_profile(created[0]["name"])
            self.page.set_form_data(created[0])

    def save_profile(self):
        profile = ChromeProfileStore.normalize(self.page.get_form_data())

        if not profile["name"]:
            QMessageBox.warning(self.main_window, "Thiếu tên", "Bạn cần nhập tên profile.")
            return

        if not profile["chrome_path"]:
            QMessageBox.warning(self.main_window, "Thiếu chrome.exe", "Bạn cần nhập đường dẫn chrome.exe.")
            return

        existing_ports = {
            item["port"]
            for item in self.profiles
            if item.get("name") != profile["name"]
        }
        if profile["port"] in existing_ports:
            QMessageBox.warning(
                self.main_window,
                "Trùng port",
                f"Port {profile['port']} đã được profile khác sử dụng.",
            )
            return

        updated = False
        for index, item in enumerate(self.profiles):
            if item.get("name") == profile["name"]:
                self.profiles[index] = profile
                updated = True
                break

        if not updated:
            self.profiles.append(profile)

        ChromeProfileStore.save(self.profiles)
        self.page.set_profiles(self.profiles, self.profile_statuses())
        self.select_profile(profile["name"])
        self.sync_auto_profiles()

    def delete_profile(self):
        name = self.page.selected_profile_name() or self.page.get_form_data().get("name", "")
        if not name:
            return

        self.profiles = [profile for profile in self.profiles if profile.get("name") != name]
        ChromeProfileStore.save(self.profiles)
        self.page.set_profiles(self.profiles, self.profile_statuses())
        self.sync_auto_profiles()

        if self.profiles:
            self.page.set_form_data(self.profiles[0])
        else:
            self.page.clear_form()

    def on_selected(self):
        name = self.page.selected_profile_name()
        if not name:
            return

        profile = self.find_profile(name)
        if profile:
            self.page.set_form_data(profile)

    def find_profile(self, name: str) -> dict | None:
        for profile in self.profiles:
            if profile.get("name") == name:
                return profile
        return None

    def select_profile(self, name: str):
        for row in range(self.page.table.rowCount()):
            item = self.page.table.item(row, 1)
            if item and item.text() == name:
                self.page.table.selectRow(row)
                return

    def open_chrome_by_name(self, name: str):
        profile = self.find_profile(name)
        if not profile:
            return

        self.page.set_form_data(profile)
        self.open_chrome(profile)

    def open_chrome(self, profile: dict | None = None):
        if profile is None or isinstance(profile, bool):
            profile = self.page.get_form_data()

        profile = ChromeProfileStore.normalize(profile)
        try:
            args = self.ensure_profile_running(profile)
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi mở Chrome",
                str(e),
            )
            return

        QMessageBox.information(
            self.main_window,
            "Đã mở Chrome",
            "Chrome đã sẵn sàng:\n"
            + " ".join([
                f'"{args[0]}"',
                args[1],
                f'--user-data-dir="{profile["user_data_dir"]}"',
                f'--profile-directory="{profile["profile_directory"]}"',
            ]),
        )

        QTimer.singleShot(1200, self.refresh_statuses)

    def open_all_off_profiles(self):
        opened = 0
        errors = []

        for profile in self.profiles:
            if ChromeLauncher.is_port_open(int(profile.get("port", 0) or 0)):
                continue

            try:
                self.ensure_profile_running(profile)
                opened += 1
            except Exception as e:
                errors.append(f"{profile.get('name')}: {e}")

        self.refresh_statuses()

        if errors:
            QMessageBox.warning(
                self.main_window,
                "Một số profile lỗi",
                "\n".join(errors),
            )
            return

        QMessageBox.information(
            self.main_window,
            "Đã mở Chrome",
            f"Đã mở {opened} profile đang OFF.",
        )

    def ensure_profile_running(self, profile: dict) -> list[str]:
        profile = ChromeProfileStore.normalize(profile)
        port = int(profile.get("port", 0) or 0)

        if ChromeLauncher.is_port_open(port):
            return [
                str(Path(profile["chrome_path"])),
                f"--remote-debugging-port={port}",
            ]

        args = ChromeLauncher.launch(profile)
        if not ChromeLauncher.wait_until_ready(port, timeout_seconds=12):
            raise TimeoutError(f"Chrome port {port} chưa sẵn sàng sau 12 giây.")

        return args

    def refresh_statuses(self):
        current = self.page.selected_profile_name()
        self.page.set_profiles(self.profiles, self.profile_statuses())
        if current:
            self.select_profile(current)

    def profile_statuses(self) -> dict[str, str]:
        statuses = {}
        for profile in self.profiles:
            name = str(profile.get("name", ""))
            port = int(profile.get("port", 0) or 0)
            statuses[name] = "RUN" if ChromeLauncher.is_port_open(port) else "OFF"
        return statuses
