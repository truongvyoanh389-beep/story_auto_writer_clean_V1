from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QMessageBox

from app.core.project_io import ProjectIO
from app.core.project_model import StoryProject
from app.core.export_builder import ExportBuilder
from app.controllers.chrome_controller import ChromeController
from app.controllers.gemini_client import GeminiClient
from app.controllers.auto_worker import AutoWorker


class AutoController:
    def __init__(self, main_window, project_controller):
        self.main_window = main_window
        self.project_controller = project_controller

        self.chrome = None
        self.gemini = None

        self.thread = None
        self.worker = None
        self.jobs = []
        self.job_counter = 0
        self.queue_stop_requested = False

        self.current_step_responses = {}

        self._connect()
        self.refresh_available_profiles()
        self.sync_write_jobs()

    def _connect(self):
        auto_page = self.main_window.auto_page
        setup_page = self.main_window.job_setup_page

        setup_page.add_job_btn.clicked.connect(self.add_current_job)
        setup_page.clear_jobs_btn.clicked.connect(self.clear_jobs)

        auto_page.assign_profile_btn.clicked.connect(self.assign_profile_to_selected_job)
        auto_page.start_queue_btn.clicked.connect(self.start_selected_job)
        auto_page.stop_queue_btn.clicked.connect(self.stop_selected_job)
        auto_page.job_table.itemSelectionChanged.connect(self.on_auto_job_selected)
        auto_page.job_combo.currentIndexChanged.connect(self.on_auto_job_combo_changed)
        setup_page.job_table.itemSelectionChanged.connect(self.on_setup_job_selected)
        self.main_window.write_page.job_combo.currentIndexChanged.connect(self.on_write_job_selected)

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def log(self, message: str):
        self.main_window.auto_page.log(message)

    def status(self, message: str, progress: int | None = None):
        self.main_window.auto_page.set_status(message, progress)
        self.log(message)

    # ------------------------------------------------------------------
    # Browser
    # ------------------------------------------------------------------

    def connect_chrome(self):
        try:
            port = self.main_window.auto_page.get_port()
            profile = self.main_window.auto_page.get_selected_profile()
            if profile and self.main_window.auto_page.should_auto_launch_chrome():
                self.ensure_selected_profile_running(profile)

            self.chrome = ChromeController(port=port)
            self.chrome.connect()

            self.gemini = GeminiClient(
                chrome_controller=self.chrome,
                log_func=self.log,
            )

            profile_text = f" ({profile.get('name')})" if profile else ""
            self.status(f"Đã kết nối Chrome port {port}{profile_text}.", 0)

            QMessageBox.information(
                self.main_window,
                "Đã kết nối",
                f"Đã kết nối Chrome port {port}{profile_text}.",
            )

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi Chrome",
                str(e),
            )
            self.log(f"Lỗi Chrome: {e}")

    def open_gemini(self):
        try:
            if not self.gemini:
                self.connect_chrome()

            self.gemini.open()
            self.status("Đã mở Gemini.", 0)

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Lỗi mở Gemini",
                str(e),
            )
            self.log(f"Lỗi mở Gemini: {e}")

    # ------------------------------------------------------------------
    # Auto thread
    # ------------------------------------------------------------------

    def auto_full(self):
        ok, error = self.main_window.input_page.validate()

        if not ok:
            QMessageBox.warning(
                self.main_window,
                "Thiếu input",
                error,
            )
            return

        project = self.project_controller.collect()

        if not project.project_name:
            from app.core.project_io import ProjectIO
            project.project_name = ProjectIO.safe_name(project.title or "untitled_project")

        self.project_controller.project = project
        self.project_controller.autosave()

        self.current_step_responses = {}
        self.main_window.auto_page.reset_steps()
        self.main_window.auto_page.set_running_state(True)
        self.main_window.auto_page.set_response("")

        wait_seconds = self.main_window.auto_page.get_wait_seconds()
        chrome_port = self.main_window.auto_page.get_port()
        profile = self.main_window.auto_page.get_selected_profile()
        if profile:
            if self.main_window.auto_page.should_auto_launch_chrome():
                try:
                    self.ensure_selected_profile_running(profile)
                except Exception as e:
                    self.main_window.auto_page.set_running_state(False)
                    QMessageBox.critical(
                        self.main_window,
                        "Lỗi mở Chrome",
                        str(e),
                    )
                    return

            self.log(f"Auto dùng Chrome profile {profile.get('name')} trên port {chrome_port}.")

        self.thread = QThread()
        self.worker = AutoWorker(
            project=project,
            chrome_port=chrome_port,
            wait_seconds=wait_seconds,
            hook_segment_words=self.main_window.auto_page.get_hook_segment_words(),
            chapter_segment_words=self.main_window.auto_page.get_chapter_segment_words(),
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.log_signal.connect(self.on_worker_log)
        self.worker.status_signal.connect(self.on_worker_status)
        self.worker.step_signal.connect(self.on_worker_step)
        self.worker.response_signal.connect(self.on_worker_response)
        self.worker.project_signal.connect(self.on_worker_project)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.finished_signal.connect(self.on_worker_finished)

        self.worker.finished_signal.connect(self.thread.quit)
        self.worker.error_signal.connect(lambda *_: self.thread.quit())

        self.thread.finished.connect(self.cleanup_thread)

        self.thread.start()

    def ensure_selected_profile_running(self, profile: dict):
        profile_controller = getattr(self.main_window, "profile_controller", None)
        if not profile_controller:
            return

        profile_controller.ensure_profile_running(profile)
        profile_controller.refresh_statuses()

    # ------------------------------------------------------------------
    # Multi job queue
    # ------------------------------------------------------------------

    def add_current_job(self):
        ok, error = self.main_window.input_page.validate()

        if not ok:
            QMessageBox.warning(
                self.main_window,
                "Thiếu input",
                error,
            )
            return

        project = self.clone_current_project()
        self.job_counter += 1
        job_id = f"job_{self.job_counter:03d}"

        if not project.project_name:
            project.project_name = ProjectIO.safe_name(project.title or job_id)

        project.project_name = self.unique_queue_project_name(project.project_name)

        job = {
            "id": job_id,
            "project": project,
            "profile": None,
            "profile_name": "",
            "port": "",
            "status": "pending",
            "steps": {},
            "thread": None,
            "worker": None,
        }

        self.jobs.append(job)
        self.add_job_to_views(job)
        self.refresh_available_profiles()
        self.sync_write_jobs()
        self.log(f"Đã thêm {job_id}: {project.project_name}")

    def add_job_to_views(self, job: dict):
        for page in (self.main_window.job_setup_page, self.main_window.auto_page):
            page.add_job_row(
                job_id=job["id"],
                project_name=job["project"].project_name,
                profile_name=job.get("profile_name", ""),
                port=job.get("port", ""),
            )

    def update_job_in_views(
        self,
        job_id: str,
        profile_name: str | None = None,
        port: int | str | None = None,
        status: str | None = None,
        progress: int | None = None,
        step: str | None = None,
    ):
        self.main_window.auto_page.update_job_row(
            job_id,
            profile_name=profile_name,
            port=port,
            status=status,
            progress=progress,
            step=step,
        )
        self.main_window.job_setup_page.update_job_row(
            job_id,
            profile_name=profile_name,
            port=port,
            status=status,
            progress=progress,
            step=step,
        )

    def clone_current_project(self) -> StoryProject:
        project = self.project_controller.collect()
        return StoryProject.from_dict(project.to_dict())

    def unique_queue_project_name(self, base_name: str) -> str:
        existing = {
            job["project"].project_name
            for job in self.jobs
        }

        if base_name not in existing:
            return base_name

        index = 2
        while f"{base_name}_{index}" in existing:
            index += 1

        return f"{base_name}_{index}"

    def clear_jobs(self):
        if any(job["status"] == "running" for job in self.jobs):
            QMessageBox.warning(
                self.main_window,
                "Queue đang chạy",
                "Không thể xóa job khi queue đang chạy.",
            )
            return

        self.jobs = []
        self.job_counter = 0
        self.main_window.auto_page.reset_jobs()
        self.main_window.job_setup_page.reset_jobs()
        self.main_window.write_page.set_jobs([])
        self.main_window.write_page.set_chapters([])
        self.refresh_available_profiles()

    def assign_profile_to_selected_job(self):
        job_id = self.main_window.auto_page.get_selected_job_id()
        job = self.find_job(job_id)
        profile = self.main_window.auto_page.get_selected_profile()

        if not job:
            QMessageBox.warning(self.main_window, "Chưa chọn job", "Bạn cần chọn job trong bảng queue.")
            return

        if not profile:
            QMessageBox.warning(self.main_window, "Chưa chọn profile", "Không có profile rảnh để gán.")
            return

        if job["status"] == "running":
            QMessageBox.warning(self.main_window, "Job đang chạy", "Không thể đổi profile khi job đang chạy.")
            return

        busy_ports = {
            item.get("port")
            for item in self.jobs
            if item["id"] != job["id"] and item.get("profile") and item["status"] in {"pending", "running"}
        }

        if profile.get("port") in busy_ports:
            QMessageBox.warning(self.main_window, "Profile đang bận", "Profile này đã được gán cho job khác.")
            self.refresh_available_profiles()
            return

        job["profile"] = dict(profile)
        job["profile_name"] = profile.get("name", "")
        job["port"] = int(profile.get("port", 0) or 0)
        job["project"].profile_name = job["profile_name"]
        self.update_job_in_views(
            job["id"],
            profile_name=job["profile_name"],
            port=job["port"],
            status="Pending",
            step="Đã gán profile",
        )
        self.refresh_available_profiles()
        self.log(f"Đã gán {job['profile_name']}:{job['port']} cho {job['id']}.")

    def start_selected_job(self):
        job_id = self.main_window.auto_page.get_selected_job_id()
        job = self.find_job(job_id)

        if not job:
            QMessageBox.warning(
                self.main_window,
                "Chưa chọn job",
                "Bạn cần chọn một job trong bảng Job queue.",
            )
            return

        if job["status"] == "running":
            QMessageBox.warning(
                self.main_window,
                "Job đang chạy",
                f"{job_id} đang chạy rồi.",
            )
            return

        if not job.get("profile"):
            QMessageBox.warning(
                self.main_window,
                "Job chưa gán profile",
                "Bạn cần chọn job, chọn profile rảnh, rồi bấm Gán profile cho job trước khi chạy.",
            )
            return

        running_ports = {
            item.get("port")
            for item in self.jobs
            if item["id"] != job["id"] and item["status"] == "running"
        }

        if job["port"] in running_ports:
            QMessageBox.warning(
                self.main_window,
                "Profile đang chạy",
                f"Port {job['port']} đang được job khác sử dụng.",
            )
            return

        self.main_window.auto_page.set_queue_running_state(True)
        self.main_window.auto_page.set_current_job(job["id"])
        self.render_job_process(job["id"])
        self.update_selected_job_buttons()
        self.log(f"Bắt đầu chạy {job['id']} trên profile {job['profile_name']}:{job['port']}.")

        if not self.prepare_job_chrome(job):
            self.main_window.auto_page.set_queue_running_state(False)
            self.refresh_available_profiles()
            return

        self.start_job(job)

    def stop_selected_job(self):
        job_id = self.main_window.auto_page.get_selected_job_id()
        job = self.find_job(job_id)

        if not job or job["status"] != "running" or not job.get("worker"):
            QMessageBox.warning(
                self.main_window,
                "Job chưa chạy",
                "Job đang chọn không ở trạng thái running.",
            )
            return

        job["worker"].request_stop()
        self.update_job_in_views(
            job["id"],
            status="Stopping",
            step="Đang yêu cầu dừng sau step hiện tại",
        )
        self.log(f"Đang yêu cầu dừng {job['id']} sau step hiện tại...")

    def start_next_jobs(self):
        return

        # Kept only as a compatibility stub. The UI now runs exactly one
        # selected job at a time via start_selected_job().
        running_jobs = [job for job in self.jobs if job["status"] == "running"]
        running_ports = {job["port"] for job in running_jobs}
        max_parallel = self.main_window.auto_page.get_max_parallel_jobs()

        for job in self.jobs:
            if len(running_jobs) >= max_parallel:
                break

            if job["status"] != "pending":
                continue

            if not job.get("profile"):
                profile = self.next_free_profile(running_ports)
                if profile:
                    job["profile"] = dict(profile)
                    job["profile_name"] = profile.get("name", "")
                    job["port"] = int(profile.get("port", 0) or 0)
                    job["project"].profile_name = job["profile_name"]
                    self.update_job_in_views(
                        job["id"],
                        profile_name=job["profile_name"],
                        port=job["port"],
                        status="Pending",
                        step="Auto gán profile rảnh",
                    )

            if not job.get("profile"):
                self.update_job_in_views(
                    job["id"],
                    status="Waiting profile",
                    step="Chưa có profile rảnh",
                )
                continue

            if job["port"] in running_ports:
                self.update_job_in_views(
                    job["id"],
                    status="Waiting port",
                    step=f"Port {job['port']} đang bận",
                )
                continue

            if not self.prepare_job_chrome(job):
                continue

            self.start_job(job)
            running_jobs.append(job)
            running_ports.add(job["port"])

        self.finish_queue_if_idle()

    def prepare_job_chrome(self, job: dict) -> bool:
        if not self.main_window.auto_page.should_auto_launch_chrome():
            return True

        profile_controller = getattr(self.main_window, "profile_controller", None)
        if not profile_controller:
            return True

        self.update_job_in_views(
            job["id"],
            status="Opening Chrome",
            step=f"{job['profile_name']}:{job['port']}",
        )

        try:
            profile_controller.ensure_profile_running(job["profile"])
            profile_controller.refresh_statuses()
            return True
        except Exception as e:
            job["status"] = "error"
            self.update_job_in_views(
                job["id"],
                status="Chrome error",
                step=str(e),
            )
            self.log(f"[{job['id']}] Không mở được Chrome profile {job['profile_name']}: {e}")
            return False

    def start_job(self, job: dict):
        thread = QThread()
        worker = AutoWorker(
            project=job["project"],
            chrome_port=job["port"],
            wait_seconds=self.main_window.auto_page.get_wait_seconds(),
            hook_segment_words=self.main_window.auto_page.get_hook_segment_words(),
            chapter_segment_words=self.main_window.auto_page.get_chapter_segment_words(),
        )

        job["thread"] = thread
        job["worker"] = worker
        job["status"] = "running"

        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        worker.log_signal.connect(lambda message, job_id=job["id"]: self.on_job_log(job_id, message))
        worker.status_signal.connect(lambda message, progress, job_id=job["id"]: self.on_job_status(job_id, message, progress))
        worker.step_signal.connect(lambda key, status, message, response_preview, job_id=job["id"]: self.on_job_step(job_id, key, status, message, response_preview))
        worker.response_signal.connect(lambda key, response, job_id=job["id"]: self.on_job_response(job_id, key, response))
        worker.project_signal.connect(lambda project, job_id=job["id"]: self.on_job_project(job_id, project))
        worker.error_signal.connect(lambda error, detail, job_id=job["id"]: self.on_job_error(job_id, error, detail))
        worker.finished_signal.connect(lambda job_id=job["id"]: self.on_job_finished(job_id))

        worker.finished_signal.connect(thread.quit)
        worker.error_signal.connect(lambda *_: thread.quit())
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda job_id=job["id"]: self.cleanup_job(job_id))

        self.update_job_in_views(
            job["id"],
            status="Running",
            progress=0,
            step="Khởi động",
        )
        self.log(f"{job['id']} bắt đầu chạy trên port {job['port']}.")
        thread.start()

    def find_job(self, job_id: str) -> dict | None:
        for job in self.jobs:
            if job["id"] == job_id:
                return job
        return None

    def on_job_log(self, job_id: str, message: str):
        self.log(f"[{job_id}] {message}")

    def on_job_status(self, job_id: str, message: str, progress: int):
        self.update_job_in_views(
            job_id,
            status="Running",
            progress=progress,
            step=message,
        )

    def on_job_step(self, job_id: str, key: str, status: str, message: str, response_preview: str):
        job = self.find_job(job_id)
        if job:
            job.setdefault("steps", {})[key] = {
                "status": status,
                "message": message,
                "response_preview": response_preview,
            }

        self.update_job_in_views(
            job_id,
            status=status,
            step=f"{key}: {message}",
        )

        if self.main_window.auto_page.get_selected_job_id() == job_id:
            self.render_job_process(job_id)

    def on_job_response(self, job_id: str, key: str, response: str):
        self.current_step_responses[f"{job_id}:{key}"] = response
        if self.main_window.auto_page.get_selected_job_id() == job_id:
            self.main_window.auto_page.set_response(response)

    def on_job_project(self, job_id: str, project):
        job = self.find_job(job_id)
        if not job:
            return

        job["project"] = project
        self.sync_write_jobs()
        if self.main_window.write_page.get_selected_job_id() == job_id:
            self.main_window.write_page.set_chapters(project.chapters)
            self.main_window.write_page.set_script_evaluation(getattr(project, "script_evaluation", ""))
            self.main_window.write_page.set_final_repair(getattr(project, "final_repair", ""))
            self.main_window.write_page.set_segment_script(getattr(project, "segment_script", ""))
            self.main_window.write_page.set_thumbnail_prompt(
                getattr(project, "seo_meta", "") or getattr(project, "thumbnail_prompt", "")
            )

    def on_job_error(self, job_id: str, error: str, detail: str):
        job = self.find_job(job_id)
        if job:
            job["status"] = "error"

        self.update_job_in_views(
            job_id,
            status="Error",
            step=error,
        )
        self.log(f"[{job_id}] Lỗi: {error}")
        self.log(detail)
        self.refresh_available_profiles()

    def on_job_finished(self, job_id: str):
        job = self.find_job(job_id)
        if job:
            job["status"] = "done"
            try:
                result = ExportBuilder.export(job["project"])
                self.log(f"[{job_id}] Export tự động: {result.get('export_dir')}")
            except Exception as e:
                self.log(f"[{job_id}] Export tự động lỗi: {e}")

        self.update_job_in_views(
            job_id,
            status="Done",
            progress=100,
            step="Hoàn tất",
        )
        self.log(f"[{job_id}] Hoàn tất.")
        self.refresh_available_profiles()
        self.sync_write_jobs()

    def cleanup_job(self, job_id: str):
        job = self.find_job(job_id)
        if job:
            job["thread"] = None
            job["worker"] = None

        self.update_selected_job_buttons()
        self.refresh_available_profiles()

    def finish_queue_if_idle(self):
        if any(job["status"] == "running" for job in self.jobs):
            return

        has_pending = any(job["status"] == "pending" for job in self.jobs)
        has_waiting = any(job["status"] == "Waiting port" for job in self.jobs)

        if has_pending or has_waiting:
            if not self.queue_stop_requested:
                return

        self.main_window.auto_page.set_queue_running_state(False)
        if self.queue_stop_requested:
            self.log("Queue đã dừng.")
        else:
            self.log("Queue đã chạy xong.")

    def next_free_profile(self, running_ports: set[int]) -> dict | None:
        busy_ports = {
            job.get("port")
            for job in self.jobs
            if job.get("profile") and job["status"] in {"pending", "running"}
        } | set(running_ports)

        for profile in getattr(self.main_window.auto_page, "profiles", []):
            port = int(profile.get("port", 0) or 0)
            if port not in busy_ports:
                return profile

        profile_controller = getattr(self.main_window, "profile_controller", None)
        if profile_controller:
            for profile in profile_controller.profiles:
                port = int(profile.get("port", 0) or 0)
                if port not in busy_ports:
                    return profile

        return None

    def refresh_available_profiles(self):
        profile_controller = getattr(self.main_window, "profile_controller", None)
        profiles = list(getattr(profile_controller, "profiles", [])) if profile_controller else []
        busy_ports = {
            job.get("port")
            for job in self.jobs
            if job.get("profile") and job["status"] in {"pending", "running"}
        }
        free_profiles = [
            profile for profile in profiles
            if int(profile.get("port", 0) or 0) not in busy_ports
        ]
        self.main_window.auto_page.set_profiles(free_profiles)

    def sync_write_jobs(self):
        self.main_window.write_page.set_jobs(self.jobs)

    def on_auto_job_selected(self):
        rows = self.main_window.auto_page.job_table.selectionModel().selectedRows()
        if not rows:
            return

        item = self.main_window.auto_page.job_table.item(rows[0].row(), 0)
        if not item:
            return

        job_id = item.text()
        self.main_window.auto_page.set_current_job(job_id)
        self.render_job_process(job_id)
        self.update_selected_job_buttons()

    def on_setup_job_selected(self):
        rows = self.main_window.job_setup_page.job_table.selectionModel().selectedRows()
        if not rows:
            return

        item = self.main_window.job_setup_page.job_table.item(rows[0].row(), 0)
        if not item:
            return

        self.main_window.auto_page.set_current_job(item.text())
        self.render_job_process(item.text())
        self.update_selected_job_buttons()

    def on_auto_job_combo_changed(self):
        job_id = self.main_window.auto_page.get_selected_job_id()
        if job_id:
            self.render_job_process(job_id)
            self.update_selected_job_buttons()

    def render_job_process(self, job_id: str):
        job = self.find_job(job_id)
        self.main_window.auto_page.reset_steps()
        if not job:
            return

        for key, data in job.get("steps", {}).items():
            self.main_window.auto_page.update_step(
                key,
                data.get("status", ""),
                data.get("message", ""),
                data.get("response_preview", ""),
            )

        self.main_window.write_page.set_current_job(job_id)
        self.main_window.write_page.set_chapters(job["project"].chapters)
        self.main_window.write_page.set_script_evaluation(getattr(job["project"], "script_evaluation", ""))
        self.main_window.write_page.set_final_repair(getattr(job["project"], "final_repair", ""))
        self.main_window.write_page.set_segment_script(getattr(job["project"], "segment_script", ""))
        self.main_window.write_page.set_thumbnail_prompt(
            getattr(job["project"], "seo_meta", "") or getattr(job["project"], "thumbnail_prompt", "")
        )

    def on_write_job_selected(self):
        job_id = self.main_window.write_page.get_selected_job_id()
        job = self.find_job(job_id)
        if job:
            self.main_window.write_page.set_chapters(job["project"].chapters)
            self.main_window.write_page.set_script_evaluation(getattr(job["project"], "script_evaluation", ""))
            self.main_window.write_page.set_final_repair(getattr(job["project"], "final_repair", ""))
            self.main_window.write_page.set_segment_script(getattr(job["project"], "segment_script", ""))
            self.main_window.write_page.set_thumbnail_prompt(
                getattr(job["project"], "seo_meta", "") or getattr(job["project"], "thumbnail_prompt", "")
            )

    def update_selected_job_buttons(self):
        job_id = self.main_window.auto_page.get_selected_job_id()
        job = self.find_job(job_id)
        selected_running = bool(job and job.get("status") == "running")
        self.main_window.auto_page.set_queue_running_state(selected_running)

    def stop_auto(self):
        if self.worker:
            self.worker.request_stop()
            self.status("Đang yêu cầu dừng Auto sau step hiện tại...", None)

    def cleanup_thread(self):
        self.main_window.auto_page.set_running_state(False)

        if self.worker:
            self.worker.deleteLater()

        if self.thread:
            self.thread.deleteLater()

        self.worker = None
        self.thread = None

    # ------------------------------------------------------------------
    # Worker slots
    # ------------------------------------------------------------------

    def on_worker_log(self, message: str):
        self.log(message)

    def on_worker_status(self, message: str, progress: int):
        self.main_window.auto_page.set_status(message, progress)

    def on_worker_step(self, key: str, status: str, message: str, response_preview: str):
        self.main_window.auto_page.update_step(
            key=key,
            status=status,
            message=message,
            response_preview=response_preview,
        )

    def on_worker_response(self, key: str, response: str):
        self.current_step_responses[key] = response
        self.main_window.auto_page.set_response(response)

    def on_worker_project(self, project):
        self.project_controller.project = project
        self.main_window.write_page.set_chapters(project.chapters)
        self.main_window.write_page.set_script_evaluation(getattr(project, "script_evaluation", ""))
        self.main_window.write_page.set_final_repair(getattr(project, "final_repair", ""))
        self.main_window.write_page.set_segment_script(getattr(project, "segment_script", ""))
        self.main_window.write_page.set_thumbnail_prompt(
            getattr(project, "seo_meta", "") or getattr(project, "thumbnail_prompt", "")
        )

    def on_worker_error(self, error: str, detail: str):
        self.main_window.auto_page.set_running_state(False)
        self.main_window.auto_page.set_status("Auto đã dừng do lỗi.", 0)

        QMessageBox.critical(
            self.main_window,
            "Lỗi Auto - đã dừng tại step lỗi",
            f"{error}\n\nTool đã dừng để bạn kiểm tra response và sửa lỗi.",
        )

        self.log(detail)

    def on_worker_finished(self):
        self.main_window.auto_page.set_running_state(False)
        self.main_window.auto_page.set_status("Hoàn tất Auto Full Pipeline.", 100)

        QMessageBox.information(
            self.main_window,
            "Hoàn tất",
            "Đã chạy xong Auto Full Pipeline.",
        )
