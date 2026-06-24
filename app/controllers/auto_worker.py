import traceback
import hashlib
import json
import re
from difflib import SequenceMatcher
import time
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from app.core.json_parser import JsonParser
from app.core.project_io import ProjectIO
from app.core.premise_selector import PremiseSelector
from app.core.content_normalizer import ContentNormalizer

from app.prompts.input_analysis_prompt import build_input_analysis_prompt
from app.prompts.premise_prompt import build_premise_prompt
from app.prompts.story_bible_prompt import build_story_bible_prompt
from app.prompts.outline_prompt import build_outline_prompt
from app.prompts.write_prompt import build_hook_prompt, build_chapter_prompt
from app.prompts.script_evaluation_prompt import build_script_evaluation_prompt
from app.prompts.final_repair_prompt import build_final_repair_prompt
from app.prompts.segment_script_prompt import build_segment_script_prompt
from app.prompts.thumbnail_prompt import build_thumbnail_prompt_prompt
from app.core.prompt_value_mapper import PromptValueMapper
from app.core.name_registry import NameRegistry
from app.controllers.chrome_controller import ChromeController
from app.controllers.gemini_client import GeminiClient


class AutoWorker(QObject):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str, int)
    step_signal = pyqtSignal(str, str, str, str)
    response_signal = pyqtSignal(str, str)
    project_signal = pyqtSignal(object)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str, str)

    def __init__(
        self,
        project,
        chrome_port: int = 9222,
        wait_seconds: int = 300,
        hook_segment_words: int = 45,
        chapter_segment_words: int = 85,
    ):
        super().__init__()
        self.project = project
        self.chrome_port = chrome_port
        self.wait_seconds = wait_seconds
        self.hook_segment_words = hook_segment_words
        self.chapter_segment_words = chapter_segment_words
        self.should_stop = False

        self.chrome = None
        self.gemini = None

    def request_stop(self):
        self.should_stop = True

    def log(self, message: str):
        self.log_signal.emit(message)

    def status(self, message: str, progress: int):
        self.status_signal.emit(message, progress)
        self.log(message)

    def mark_step(self, key: str, status: str, message: str = "", response: str = ""):
        preview = response[:500] if response else ""
        self.step_signal.emit(key, status, message, preview)

    def emit_project(self):
        self.project_signal.emit(self.project)

    def check_stop(self):
        if self.should_stop:
            raise RuntimeError("Người dùng đã dừng Auto.")

    @pyqtSlot()
    def run(self):
        try:
            self.status("Bắt đầu Auto Full Pipeline realtime...", 1)

            self.setup_browser()

            self.ensure_project_name()
            self.sync_input_cache_state()
            self.autosave()

            self.ensure_input_analysis()
            self.ensure_premises()
            self.ensure_selected_premise()
            self.ensure_story_bible()
            self.ensure_outline()
            self.ensure_hook()
            self.ensure_chapters()
            self.ensure_script_evaluation()
            self.ensure_final_repair()
            self.ensure_segment_script()
            self.ensure_thumbnail_prompt()

            self.autosave()
            self.status("Hoàn tất Auto Full Pipeline.", 100)
            self.finished_signal.emit()

        except Exception as e:
            err = str(e)
            detail = traceback.format_exc()
            self.log(f"LỖI AUTO: {err}")
            self.log(detail)
            self.autosave()
            self.error_signal.emit(err, detail)

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------

    def ensure_project_name(self):
        if not self.project.project_name:
            self.project.project_name = ProjectIO.safe_name(self.project.title or "untitled_project")

    def autosave(self):
        path = ProjectIO.save(self.project)
        self.log(f"Autosave: {path}")
        self.emit_project()

    def send_prompt(
        self,
        step_key: str,
        task_name: str,
        prompt: str,
        expect_json: bool = False,
    ) -> str:
        """
        Gửi prompt sang Gemini.

        Fix lỗi Gemini đôi khi:
        - đã trả output trên UI nhưng tool không bắt được
        - copy lại prompt cũ
        - response rỗng
        - response gần giống prompt
        - đợi tới timeout

        Nếu gặp các trường hợp đó:
        -> mở chat Gemini mới
        -> gửi lại đúng step hiện tại
        -> không tự nhảy sang step khác
        """

        max_attempts = 2
        last_error = None
        last_response = ""

        for attempt in range(1, max_attempts + 1):
            self.check_stop()

            if attempt == 1:
                self.mark_step(step_key, "Đang chạy", f"Đang gửi prompt: {task_name}")
                self.log(f"Đang gửi prompt: {task_name}")
            else:
                self.mark_step(
                    step_key,
                    "Đang chạy lại",
                    f"Đang chạy lại {task_name} trên chat mới. Lần {attempt}/{max_attempts}",
                )
                self.log(f"Đang chạy lại {task_name} trên chat mới. Lần {attempt}/{max_attempts}")

            try:
                response = self.gemini.send_prompt(
                    prompt=prompt,
                    wait_seconds=self.wait_seconds,
                    expect_json=expect_json,
                )

                last_response = response or ""

                if self.is_bad_gemini_response(
                    response=last_response,
                    prompt=prompt,
                    expect_json=expect_json,
                ):
                    raise RuntimeError(
                        f"Gemini response không hợp lệ hoặc bị echo prompt ở step {task_name}."
                    )

                ProjectIO.save_raw_response(self.project, task_name, last_response)

                self.response_signal.emit(step_key, last_response)
                self.mark_step(
                    step_key,
                    "Đã nhận response",
                    f"Đã nhận response: {task_name}",
                    last_response,
                )

                self.log(f"Đã nhận response: {task_name}")

                return last_response

            except Exception as e:
                last_error = e
                self.log(f"{task_name}: Lỗi nhận response lần {attempt}: {e}")

                if attempt < max_attempts:
                    self.reopen_gemini_chat_for_retry(step_key, task_name)
                    time.sleep(2)
                    continue

                break

        self.mark_step(
            step_key,
            "Lỗi",
            f"Không nhận được response hợp lệ sau {max_attempts} lần chạy lại: {last_error}",
            last_response,
        )

        raise RuntimeError(
            f"{task_name}: Không nhận được response hợp lệ sau {max_attempts} lần. "
            f"Lỗi cuối: {last_error}"
        )

    def parse_json_response(
        self,
        response: str,
        step_key: str,
        task_name: str = "",
    ):
        """
        Parser JSON tương thích cho V1.

        Cho phép gọi kiểu cũ:
            self.parse_json_response(response, step)

        Và kiểu mới:
            self.parse_json_response(response, step, task_name="03_story_bible")

        Không làm crash vì thiếu task_name.
        """
        import json
        import re

        if not task_name:
            task_name = step_key

        text = response or ""
        text = text.strip()

        # Bỏ markdown code fence nếu Gemini bọc JSON trong ```json
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        # Nếu Gemini thêm chữ trước/sau JSON, bóc object JSON đầu tiên
        if not text.startswith("{"):
            start = text.find("{")
            end = text.rfind("}")

            if start != -1 and end != -1 and end > start:
                text = text[start:end + 1].strip()

        try:
            return json.loads(text)
        except Exception as first_error:
            # Thử json_repair nếu có
            try:
                from json_repair import repair_json

                repaired = repair_json(text)
                return json.loads(repaired)
            except Exception as second_error:
                self.mark_step(
                    step_key,
                    "Lỗi",
                    f"Không parse được JSON: {second_error}",
                    response,
                )

                raise ValueError(
                    f"{task_name}: Không parse được JSON. "
                    f"Lỗi json.loads: {first_error}. "
                    f"Lỗi json_repair: {second_error}"
                )

    def chapter_done(self, key, min_words: int) -> bool:
        chapter = self.find_chapter(key)

        if not chapter:
            return False

        text = chapter.get("text", "").strip()
        word_count = int(chapter.get("word_count", 0) or 0)
        status = chapter.get("status", "")

        return bool(text) and word_count >= min_words and status == "done"

    def find_chapter(self, key):
        for chapter in self.project.chapters or []:
            if chapter.get("chapter_number") == key:
                return chapter

            try:
                if key != "hook" and int(chapter.get("chapter_number")) == int(key):
                    return chapter
            except Exception:
                pass

        return None

    def upsert_chapter(self, new_chapter: dict):
        chapters = self.project.chapters or []
        key = new_chapter.get("chapter_number")

        for index, chapter in enumerate(chapters):
            if chapter.get("chapter_number") == key:
                chapters[index] = new_chapter
                self.project.chapters = chapters
                return

            try:
                if key != "hook" and int(chapter.get("chapter_number")) == int(key):
                    chapters[index] = new_chapter
                    self.project.chapters = chapters
                    return
            except Exception:
                pass

        chapters.append(new_chapter)
        self.project.chapters = chapters

    def get_chapter_min_words(self) -> int:
        return int(self.get_chapter_target_words(1) * 0.65)

    def get_target_words(self) -> int:
        try:
            target_words = int(self.project.target_words or 10000)
        except Exception:
            target_words = 10000

        return max(3000, target_words)

    def get_chapter_count(self) -> int:
        target_words = self.get_target_words()

        if target_words <= 5000:
            return 5
        if target_words <= 7000:
            return 6
        if target_words <= 9000:
            return 8

        return 10

    def get_outline_chapter(self, chapter_number: int) -> dict:
        chapters = self.project.outline.get("chapters", []) if isinstance(self.project.outline, dict) else []

        for chapter in chapters:
            try:
                if int(chapter.get("chapter_number")) == chapter_number:
                    return chapter
            except Exception:
                pass

        return {}

    def get_chapter_target_words(self, chapter_number: int) -> int:
        outline_chapter = self.get_outline_chapter(chapter_number)

        try:
            outline_target = int(outline_chapter.get("target_words", 0) or 0)
        except Exception:
            outline_target = 0

        if outline_target > 0:
            return outline_target

        hook_budget = 180
        chapter_count = self.get_chapter_count()
        total_words = self.get_target_words()
        return max(450, int((total_words - hook_budget) / chapter_count))

    def outline_matches_current_length(self) -> bool:
        outline = self.project.outline if isinstance(self.project.outline, dict) else {}
        if not outline:
            return False

        chapters = outline.get("chapters", [])
        if not isinstance(chapters, list):
            return False

        try:
            outline_count = int(outline.get("total_chapters", 0) or len(chapters))
        except Exception:
            outline_count = len(chapters)

        try:
            outline_target = int(outline.get("target_total_words", 0) or 0)
        except Exception:
            outline_target = 0

        current_target = self.get_target_words()
        current_count = self.get_chapter_count()

        if outline_count != current_count:
            return False

        if outline_target and abs(outline_target - current_target) > 100:
            return False

        return True

    def clear_length_dependent_outputs(self):
        self.project.outline = {}
        self.project.chapters = []
        self.project.script_evaluation = ""
        self.project.final_repair = ""
        self.project.segment_script = ""
        self.project.segment_signature = ""
        self.project.thumbnail_prompt = ""
        self.project.seo_meta = ""

        for key in list(self.project.step_status.keys()):
            if (
                key == "outline"
                or key == "hook"
                or key.startswith("chapter_")
                or key in {"script_evaluation", "final_repair", "segment_script", "thumbnail_prompt", "seo_meta"}
            ):
                self.project.step_status.pop(key, None)

    def _signature(self, payload: dict) -> str:
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def current_input_signature(self) -> str:
        return self._signature({
            "title": (self.project.title or "").strip(),
            "transcript": (self.project.transcript or "").strip(),
        })

    def current_settings_signature(self) -> str:
        return self._signature({
            "target_words": self.get_target_words(),
            "narration_pov": self.project.narration_pov,
            "target_audience": self.project.target_audience,
            "tone": self.project.tone,
            "revenge_intensity": self.project.revenge_intensity,
            "ending_type": self.project.ending_type,
            "niche": getattr(self.project, "niche", "Family Betrayal"),
        })

    def clear_all_generated_outputs(self):
        self.project.input_analysis = {}
        self.project.premises = []
        self.project.selected_premise = {}
        self.project.story_bible = {}
        self.project.outline = {}
        self.project.chapters = []
        self.project.raw_responses = {}
        self.project.step_status = {}
        self.project.script_evaluation = ""
        self.project.final_repair = ""
        self.project.segment_script = ""
        self.project.segment_signature = ""
        self.project.thumbnail_prompt = ""
        self.project.seo_meta = ""

    def clear_settings_dependent_outputs(self):
        self.project.premises = []
        self.project.selected_premise = {}
        self.project.story_bible = {}
        self.project.outline = {}
        self.project.chapters = []
        self.project.script_evaluation = ""
        self.project.final_repair = ""
        self.project.segment_script = ""
        self.project.segment_signature = ""
        self.project.thumbnail_prompt = ""
        self.project.seo_meta = ""

        for key in list(self.project.raw_responses.keys()):
            if key != "01_input_analysis":
                self.project.raw_responses.pop(key, None)

        for key in list(self.project.step_status.keys()):
            if key != "input_analysis":
                self.project.step_status.pop(key, None)

    def generated_outputs_match_current_inputs(self) -> bool:
        if not self.project.input_analysis:
            return True

        original_title = str(self.project.input_analysis.get("original_user_title", "") or "").strip()
        return not original_title or original_title == (self.project.title or "").strip()

    def generated_outputs_match_current_settings(self) -> bool:
        niche = getattr(self.project, "niche", "Family Betrayal")

        for data in (self.project.selected_premise, self.project.story_bible, self.project.outline):
            if isinstance(data, dict) and data:
                data_niche = str(data.get("niche", "") or "").strip()
                if data_niche and data_niche != niche:
                    return False

        return self.outline_matches_current_length() if self.project.outline else True

    def sync_input_cache_state(self):
        input_signature = self.current_input_signature()
        settings_signature = self.current_settings_signature()

        input_changed = bool(getattr(self.project, "input_signature", "")) and self.project.input_signature != input_signature
        settings_changed = bool(getattr(self.project, "settings_signature", "")) and self.project.settings_signature != settings_signature
        legacy_settings_unknown = (
            not getattr(self.project, "settings_signature", "")
            and bool(
                self.project.premises
                or self.project.selected_premise
                or self.project.story_bible
                or self.project.outline
                or self.project.chapters
            )
        )

        legacy_input_mismatch = not self.generated_outputs_match_current_inputs()
        legacy_settings_mismatch = not self.generated_outputs_match_current_settings()

        if input_changed or legacy_input_mismatch:
            self.log("Input title/transcript đã thay đổi. Xóa toàn bộ output AI cũ để chạy lại đúng input mới.")
            self.clear_all_generated_outputs()
        elif settings_changed or legacy_settings_mismatch or legacy_settings_unknown:
            self.log("Cài đặt truyện đã thay đổi. Xóa premise/story bible/outline/chapters cũ để chạy lại đúng settings mới.")
            self.clear_settings_dependent_outputs()

        self.project.input_signature = input_signature
        self.project.settings_signature = settings_signature

    def get_outline_title(self, chapter_number: int) -> str:
        chapter = self.get_outline_chapter(chapter_number)
        if chapter:
            return chapter.get("chapter_title", "") or f"Chapter {chapter_number}"

        return f"Chapter {chapter_number}"

    def get_previous_text(self, chapter_number: int) -> str:
        if chapter_number <= 1:
            hook_text = self.get_hook_text()

            if not hook_text:
                return ""

            # Chỉ đưa phần rất ngắn để AI biết hook đã xảy ra,
            # không đưa nguyên hook để tránh nó copy lại.
            clean = hook_text.strip()
            words = clean.split()

            short_hook = " ".join(words[-80:]) if len(words) > 80 else clean

            return (
                "The hook has already been narrated. "
                "Do not repeat it. Continue after this final hook beat:\n\n"
                + short_hook
            )

        previous = self.find_chapter(chapter_number - 1)

        if not previous:
            return ""

        text = previous.get("text", "").strip()
        words = text.split()

        if len(words) > 250:
            text = " ".join(words[-250:])

        return text

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------

    def ensure_input_analysis(self):
        step = "01_input_analysis"

        if self.project.input_analysis:
            self.mark_step(step, "Bỏ qua", "Đã có input analysis")
            self.status("Đã có input analysis. Bỏ qua.", 10)
            return

        self.status("Đang phân tích đầu vào...", 5)

        prompt = build_input_analysis_prompt(
            title=self.project.title,
            transcript=self.project.transcript,
        )

        response = self.send_prompt(step, "01_input_analysis", prompt, expect_json=True)
        data = self.parse_json_response(
            response=response,
            step_key=step,
            task_name="01_input_analysis",
        )

        self.project.input_analysis = data
        self.project.step_status["input_analysis"] = "done"

        self.autosave()

        self.mark_step(step, "Hoàn tất", "Hoàn tất phân tích đầu vào", response)
        self.status("Hoàn tất phân tích đầu vào.", 10)

    def ensure_premises(self):
        step = "02_premises"
    
        if self.project.premises:
            self.mark_step(step, "Bỏ qua", "Đã có 10 ý tưởng")
            self.status("Đã có 10 ý tưởng. Bỏ qua.", 20)
            return
    
        self.status("Đang tạo 10 ý tưởng...", 15)
    
        forbidden_names_text = NameRegistry.get_forbidden_names_text()
    
        selected_niche = getattr(self.project, "niche", "").strip()
    
        if not selected_niche:
            selected_niche = "Family Betrayal"
    
        self.log(f"NICHE ĐANG DÙNG CHO 02_PREMISES: {selected_niche}")
    
        prompt = build_premise_prompt(
            title=self.project.title,
            input_analysis=self.project.input_analysis,
            target_words=self.project.target_words,
            narration_pov=PromptValueMapper.narration_pov(self.project.narration_pov),
            target_audience=PromptValueMapper.audience(self.project.target_audience),
            tone=PromptValueMapper.tone(self.project.tone),
            revenge_intensity=PromptValueMapper.revenge_intensity(self.project.revenge_intensity),
            ending_type=PromptValueMapper.ending_type(self.project.ending_type),
            niche=selected_niche,
            forbidden_names_text=forbidden_names_text,
        )
    
        response = self.send_prompt(step, "02_premises", prompt, expect_json=True)
    
        data = self.parse_json_response(
            response=response,
            step_key=step,
            task_name="02_premises",
        )
    
        premises = data.get("premises", [])
    
        if not isinstance(premises, list) or len(premises) < 10:
            self.mark_step(step, "Lỗi", "JSON không có đủ 10 premises", response)
            raise ValueError("JSON premises cần có key 'premises' với đủ 10 ý tưởng.")
    
        normalized = []
    
        for index, premise in enumerate(premises[:10], start=1):
            if isinstance(premise, dict):
                premise.setdefault("id", index)
                premise.setdefault("premise_id", f"P{index:02d}")
    
                # Ép lại niche local, không để Gemini đổi.
                premise["niche"] = selected_niche
    
                normalized.append(premise)
    
        normalized = NameRegistry.normalize_premises(normalized)
    
        self.project.premises = normalized
        self.project.step_status["premises"] = "done"
    
        self.autosave()
    
        self.mark_step(step, "Hoàn tất", f"Hoàn tất tạo {len(normalized)} ý tưởng với niche: {selected_niche}", response)
        self.status(f"Hoàn tất tạo {len(normalized)} ý tưởng.", 25)
    def ensure_selected_premise(self):
        step = "03_select_premise"

        if self.project.selected_premise:
            self.mark_step(step, "Bỏ qua", "Đã có selected premise")
            self.status("Đã có selected premise. Bỏ qua.", 30)
            return

        self.status("Đang chọn ý tưởng điểm cao nhất...", 28)

        if not self.project.premises:
            self.mark_step(step, "Lỗi", "Không có premises để chọn")
            raise ValueError("Không có premises để chọn.")

        best = PremiseSelector.select_best(self.project.premises)

        if not best:
            self.mark_step(step, "Lỗi", "Không chọn được premise điểm cao nhất")
            raise ValueError("Không chọn được premise điểm cao nhất.")

        self.project.selected_premise = best
        self.project.step_status["selected_premise"] = "done"

        self.autosave()

        msg = f"Đã chọn: {best.get('title', '')}"
        self.mark_step(step, "Hoàn tất", msg)
        self.status(msg, 30)

    def ensure_story_bible(self):
        step = "03_story_bible"

        if self.project.story_bible:
            # Không dừng nếu tên cũ bị lặp/cấm.
            # Tự chuẩn hóa tên rồi chạy tiếp.
            mapping = NameRegistry.normalize_project_names(self.project)

            if mapping:
                self.autosave()
                self.mark_step(
                    step,
                    "Đã sửa",
                    "Đã tự thay tên bị cấm/lặp trong Story Bible: "
                    + ", ".join([f"{old} -> {new}" for old, new in mapping.items()]),
                )

            self.mark_step(step, "Bỏ qua", "Đã có Story Bible")
            self.status("Đã có Story Bible. Bỏ qua.", 40)
            return

        self.status("Đang tạo Story Bible...", 35)

        forbidden_names_text = NameRegistry.get_forbidden_names_text()

        prompt = build_story_bible_prompt(
            title=self.project.title,
            selected_premise=self.project.selected_premise,
            input_analysis=self.project.input_analysis,
            target_words=self.project.target_words,
            narration_pov=PromptValueMapper.narration_pov(self.project.narration_pov),
            target_audience=PromptValueMapper.audience(self.project.target_audience),
            tone=PromptValueMapper.tone(self.project.tone),
            revenge_intensity=PromptValueMapper.revenge_intensity(self.project.revenge_intensity),
            ending_type=PromptValueMapper.ending_type(self.project.ending_type),
            niche=getattr(self.project, "niche", "Family Betrayal"),
            forbidden_names_text=forbidden_names_text,
        )

        response = self.send_prompt(step, "03_story_bible", prompt, expect_json=True)

        data = self.parse_json_response(
            response=response,
            step_key=step,
            task_name="03_story_bible",
        )

        self.project.story_bible = data

        # Quan trọng:
        # Không raise ValueError nếu tên bị lặp/cấm.
        # Tự thay local bằng bank tên.
        mapping = NameRegistry.normalize_project_names(self.project)

        if mapping:
            self.mark_step(
                step,
                "Đã sửa",
                "Đã tự thay tên bị cấm/lặp trong Story Bible: "
                + ", ".join([f"{old} -> {new}" for old, new in mapping.items()]),
                response,
            )

        self.project.step_status["story_bible"] = "done"

        NameRegistry.update_from_project(self.project)

        self.autosave()

        self.mark_step(step, "Hoàn tất", "Hoàn tất Story Bible", response)
        self.status("Hoàn tất Story Bible.", 45)

    def ensure_outline(self):
        step = "04_outline"

        if self.project.outline and not self.outline_matches_current_length():
            self.mark_step(
                step,
                "Đang sửa",
                "Target words/chapter count đã thay đổi. Xóa outline và chapters cũ để chạy lại đúng input.",
            )
            self.clear_length_dependent_outputs()
            self.autosave()

        if self.project.outline:
            mapping = NameRegistry.normalize_project_names(self.project)

            if mapping:
                self.autosave()
                self.mark_step(
                    step,
                    "Đã sửa",
                    "Đã tự thay tên bị cấm/lặp trong Outline: "
                    + ", ".join([f"{old} -> {new}" for old, new in mapping.items()]),
                )

            self.mark_step(step, "Bỏ qua", "Đã có Outline")
            self.status("Đã có Outline. Bỏ qua.", 50)
            return

        self.status("Đang tạo Outline...", 48)

        if self.project.chapters:
            self.project.chapters = []
            self.project.script_evaluation = ""
            self.project.final_repair = ""
            self.project.segment_script = ""
            self.project.segment_signature = ""
            self.project.thumbnail_prompt = ""
            self.project.seo_meta = ""
            self.autosave()

        chapter_count = self.get_chapter_count()

        prompt = build_outline_prompt(
            title=self.project.title,
            story_bible=self.project.story_bible,
            target_words=self.project.target_words,
            chapter_count=chapter_count,
            narration_pov=PromptValueMapper.narration_pov(self.project.narration_pov),
            target_audience=PromptValueMapper.audience(self.project.target_audience),
            tone=PromptValueMapper.tone(self.project.tone),
            revenge_intensity=PromptValueMapper.revenge_intensity(self.project.revenge_intensity),
            ending_type=PromptValueMapper.ending_type(self.project.ending_type),
            niche=getattr(self.project, "niche", "Family Betrayal"),
        )

        response = self.send_prompt(step, "04_outline", prompt, expect_json=True)

        data = self.parse_json_response(
            response=response,
            step_key=step,
            task_name="04_outline",
        )

        chapters = data.get("chapters", [])

        if not isinstance(chapters, list) or len(chapters) < chapter_count:
            self.mark_step(step, "Lỗi", "Outline JSON không đủ 10 chương", response)
            raise ValueError("Outline JSON cần có key chapters với đủ 10 chương.")

        data["chapters"] = chapters[:chapter_count]
        data["total_chapters"] = chapter_count
        data["target_total_words"] = self.get_target_words()

        self.project.outline = data

        mapping = NameRegistry.normalize_project_names(self.project)

        if mapping:
            self.mark_step(
                step,
                "Đã sửa",
                "Đã tự thay tên bị cấm/lặp trong Outline: "
                + ", ".join([f"{old} -> {new}" for old, new in mapping.items()]),
                response,
            )

        self.project.step_status["outline"] = "done"

        self.autosave()

        self.mark_step(step, "Hoàn tất", "Hoàn tất Outline", response)
        self.status("Hoàn tất Outline.", 55)

    def rewrite_weak_hook(self, original_hook: str) -> str:
        premise_title = ""

        try:
            premise_title = self.project.selected_premise.get("title", "")
        except Exception:
            premise_title = self.project.title

        rewrite_prompt = f"""
    ROLE:
    You are a professional American viral story hook editor for long-form YouTube text-to-speech drama.

    TASK:
    Rewrite the Hook below so it immediately retains the viewer.

    The Hook does NOT need to be long.
    It should be short, sharp, emotionally loaded, and impossible to ignore.

    CURRENT WEAK HOOK:
    {original_hook}

    ORIGINAL USER TITLE:
    {self.project.title}

    SELECTED PREMISE TITLE:
    {premise_title}

    SELECTED PREMISE:
    {self.project.selected_premise}

    STORY BIBLE:
    {self.project.story_bible}

    OUTLINE:
    {self.project.outline}

    HOOK RULES:
    - Write prose only.
    - Do not return JSON.
    - Do not use markdown.
    - Do not add a title.
    - Do not write "Hook:".
    - Do not explain anything.
    - Do not include sound effects.
    - Do not include music cues.
    - Do not include stage directions.
    - Start with immediate tension, betrayal, humiliation, money loss, danger, mystery, or a shocking contradiction.
    - Create one strong unanswered question.
    - Do not resolve the situation.
    - Do not repeat Chapter 1.
    - Keep it suitable for American adults aged 45+.
    - Keep it grounded and realistic.
    - Length target: 120 to 220 words.
    - First sentence must be strong enough to make the viewer keep listening.

    NON-VERBAL & PRONUNCIATION CONTROL:
    You may use these supported TTS tags sparingly:
    [laughter], [sigh], [confirmation-en], [question-en], [question-ah], [question-oh], [question-ei], [question-yi], [surprise-ah], [surprise-oh], [surprise-wa], [surprise-yo], [dissatisfaction-hnn].

    Rules:
    - Use only the supported tags listed above.
    - Use at most 1 or 2 tags in the Hook.
    - Do not force tags if the Hook is stronger without them.
    - Do not place tags in headings.
    - Do not invent new tags.

    Return only the rewritten Hook prose.
    """

        self.log("Hook chưa đủ mạnh. Đang yêu cầu Gemini tự viết lại Hook...")

        rewritten_hook = self.gemini.send_prompt(
            prompt=rewrite_prompt,
            wait_seconds=self.wait_seconds,
            expect_json=False,
        )

        rewritten_hook = ContentNormalizer.normalize_hook(rewritten_hook)

        if not rewritten_hook.strip():
            return original_hook

        return rewritten_hook

    def ensure_hook(self):
        step = "05_hook"

        existing_hook = self.find_chapter("hook")

        if existing_hook and existing_hook.get("text", "").strip() and existing_hook.get("status") == "done":
            self.mark_step(step, "Bỏ qua", "Hook đã có")
            self.status("Hook đã có. Bỏ qua.", 58)
            return

        self.status("Đang viết Hook...", 56)

        prompt = build_hook_prompt(
            title=self.project.title,
            selected_premise=self.project.selected_premise,
            story_bible=self.project.story_bible,
            outline=self.project.outline,
            target_audience=PromptValueMapper.audience(self.project.target_audience),
            tone=PromptValueMapper.tone(self.project.tone),
            niche=getattr(self.project, "niche", "Family Betrayal"),
            narration_pov=PromptValueMapper.narration_pov(self.project.narration_pov),
        )

        response = self.send_prompt(
            step,
            "05_hook",
            prompt,
            expect_json=False,
        )

        if ContentNormalizer.looks_like_outline_json(response):
            self.mark_step(
                step,
                "Lỗi",
                "Hook nhận nhầm Outline JSON. Dừng để kiểm tra.",
                response,
            )
            raise ValueError("Hook nhận nhầm Outline JSON, không phải prose.")

        hook_text = ContentNormalizer.normalize_hook(response)

        if not hook_text:
            self.mark_step(step, "Lỗi", "Không lấy được hook text", response)
            raise ValueError("Không lấy được hook text.")

        if not ContentNormalizer.hook_has_strong_opening(hook_text):
            self.mark_step(
                step,
                "Đang sửa",
                "Hook chưa đủ mạnh. Tool đang tự viết lại Hook lần 1.",
                hook_text,
            )

            rewritten_hook = self.rewrite_weak_hook(hook_text)

            if not ContentNormalizer.hook_has_strong_opening(rewritten_hook):
                self.mark_step(
                    step,
                    "Đang sửa",
                    "Hook rewrite lần 1 vẫn yếu. Tool đang rewrite lần 2.",
                    rewritten_hook,
                )

                rewritten_hook = self.rewrite_weak_hook(rewritten_hook)

            if rewritten_hook and rewritten_hook.strip():
                hook_text = rewritten_hook

            if ContentNormalizer.hook_has_strong_opening(hook_text):
                self.mark_step(
                    step,
                    "Đã sửa",
                    "Hook đã được tự viết lại đủ mạnh.",
                    hook_text,
                )
            else:
                self.mark_step(
                    step,
                    "Cảnh báo",
                    "Hook vẫn chưa thật mạnh sau 2 lần rewrite, nhưng tool sẽ tiếp tục chạy.",
                    hook_text,
                )

        word_count = ContentNormalizer.count_words(hook_text)

        self.upsert_chapter({
            "chapter_number": "hook",
            "type": "hook",
            "title": "Hook",
            "heading": "Hook",
            "text": hook_text,
            "word_count": word_count,
            "status": "done",
        })

        self.project.step_status["hook"] = "done"
        self.autosave()

        self.mark_step(step, "Hoàn tất", f"Hook: {word_count} từ", hook_text)
        self.status(f"Hoàn tất Hook: {word_count} từ.", 60)

    def ensure_chapters(self):
        chapter_count = self.get_chapter_count()

        for chapter_number in range(1, chapter_count + 1):
            self.check_stop()
            min_words = int(self.get_chapter_target_words(chapter_number) * 0.65)

            step = f"{chapter_number + 5:02d}_chapter_{chapter_number:02d}"

            if self.chapter_done(chapter_number, min_words=min_words):
                self.mark_step(step, "Bỏ qua", f"Chapter {chapter_number} đã có")
                self.status(f"Chapter {chapter_number} đã có. Bỏ qua.", 60 + chapter_number * 3)
                continue

            self.write_chapter(chapter_number, step)

        for chapter_number in range(chapter_count + 1, 11):
            step = f"{chapter_number + 5:02d}_chapter_{chapter_number:02d}"
            self.mark_step(step, "Bỏ qua", f"Target words chỉ cần {chapter_count} chương")

    def ensure_script_evaluation(self):
        step = "17_script_evaluation"

        if getattr(self.project, "script_evaluation", ""):
            self.mark_step(step, "Bỏ qua", "Đã có đánh giá script")
            self.status("Đã có đánh giá script. Bỏ qua.", 96)
            return

        self.status("Đang so sánh script gốc và script mới...", 94)

        new_script = self.build_new_script_text()
        if not new_script.strip():
            self.mark_step(step, "Lỗi", "Không có script mới để đánh giá")
            raise ValueError("Không có script mới để đánh giá.")

        prompt = build_script_evaluation_prompt(
            title=self.project.title,
            original_script=self.project.transcript,
            new_script=new_script,
        )

        response = self.send_prompt(
            step,
            "07_script_evaluation",
            prompt,
            expect_json=False,
        )

        self.project.script_evaluation = response or ""
        self.project.step_status["script_evaluation"] = "done"
        self.autosave()

        self.mark_step(step, "Hoàn tất", "Hoàn tất đánh giá script", response)
        self.status("Hoàn tất đánh giá script.", 98)

    def evaluation_needs_final_repair(self) -> bool:
        report = (getattr(self.project, "script_evaluation", "") or "").lower()

        if not report:
            return False

        triggers = [
            "continuity / logic issues",
            "continuity",
            "logic issues",
            "name slip",
            "name continuity",
            "name mixing",
            "fix name",
            "fix immediately",
            "retention risks",
            "technical jargon",
            "pacing",
            "final editor notes",
        ]

        return any(trigger in report for trigger in triggers)

    def ensure_final_repair(self):
        step = "18_final_repair"

        if getattr(self.project, "final_repair", ""):
            self.mark_step(step, "Bỏ qua", "Đã có final repair")
            self.status("Đã có final repair. Bỏ qua.", 98)
            return

        if not self.evaluation_needs_final_repair():
            self.project.final_repair = "SKIPPED: Script evaluation did not flag repair-critical issues."
            self.project.step_status["final_repair"] = "skipped"
            self.autosave()
            self.mark_step(step, "Bỏ qua", "Evaluation không có lỗi cần repair")
            self.status("Không cần final repair.", 98)
            return

        self.status("Đang sửa final script theo report đánh giá...", 98)

        current_script = self.build_new_script_text()
        if not current_script.strip():
            self.mark_step(step, "Lỗi", "Không có script để final repair")
            raise ValueError("Không có script để final repair.")

        prompt = build_final_repair_prompt(
            title=self.project.title,
            story_bible=self.project.story_bible,
            outline=self.project.outline,
            evaluation_report=self.project.script_evaluation,
            script_text=current_script,
            target_words=self.get_target_words(),
            chapter_count=self.get_chapter_count(),
        )

        response = self.send_prompt(
            step,
            "08_final_repair",
            prompt,
            expect_json=False,
        )

        repaired_script = ContentNormalizer.clean_text(response)
        repaired_chapters = self.parse_repaired_script(repaired_script)

        if not repaired_chapters:
            self.mark_step(step, "Lỗi", "Không tách được repaired script thành Hook/Chapters", response)
            raise ValueError("Không tách được repaired script thành Hook/Chapters.")

        self.project.chapters = repaired_chapters
        self.project.final_repair = repaired_script
        self.project.thumbnail_prompt = ""
        self.project.seo_meta = ""
        self.project.step_status["final_repair"] = "done"
        self.project.step_status.pop("thumbnail_prompt", None)
        self.project.step_status.pop("seo_meta", None)
        self.autosave()

        self.mark_step(step, "Hoàn tất", "Đã sửa final script theo evaluation report", repaired_script)
        self.status("Hoàn tất final repair.", 98)

    def get_narrator_name(self) -> str:
        try:
            main_character = self.project.story_bible.get("main_character", {})
            name = (main_character.get("name") or "").strip()
            if name:
                return name
        except Exception:
            pass

        try:
            main_character = self.project.selected_premise.get("main_character", {})
            name = (main_character.get("name") or "").strip()
            if name:
                return name
        except Exception:
            pass

        return "Main character"

    def current_segment_signature(self, script_text: str) -> str:
        return self._signature({
            "script_text": script_text,
            "hook_segment_words": self.hook_segment_words,
            "chapter_segment_words": self.chapter_segment_words,
            "narrator_name": self.get_narrator_name(),
        })

    def ensure_segment_script(self):
        step = "19_segment_script"

        full_script = self.build_new_script_text()
        if not full_script.strip():
            self.mark_step(step, "Lỗi", "Không có script để chia segment")
            raise ValueError("Không có script để chia segment.")

        signature = self.current_segment_signature(full_script)

        if getattr(self.project, "segment_script", "") and getattr(self.project, "segment_signature", "") == signature:
            self.mark_step(step, "Bỏ qua", "Đã có Segment Script")
            self.status("Đã có Segment Script. Bỏ qua.", 99)
            return

        self.status("Đang chia Segment + phân vai...", 99)

        prompt = build_segment_script_prompt(
            title=self.project.title,
            story_bible=self.project.story_bible,
            outline=self.project.outline,
            full_script=full_script,
            narrator_name=self.get_narrator_name(),
            hook_segment_words=self.hook_segment_words,
            chapter_segment_words=self.chapter_segment_words,
        )

        response = self.send_prompt(
            step,
            "09_segment_script",
            prompt,
            expect_json=False,
        )

        segment_script = ContentNormalizer.clean_text(response)

        if "[SEG_" not in segment_script:
            self.mark_step(step, "Lỗi", "Segment Script không có SEG id", response)
            raise ValueError("Segment Script không có SEG id.")

        self.project.segment_script = segment_script
        self.project.segment_signature = signature
        self.project.step_status["segment_script"] = "done"
        self.autosave()

        self.mark_step(step, "Hoàn tất", "Hoàn tất Segment + phân vai", segment_script)
        self.status("Hoàn tất Segment + phân vai.", 99)

    def parse_repaired_script(self, script: str) -> list[dict]:
        text = ContentNormalizer.clean_text(script)
        if not text:
            return []

        pattern = re.compile(r"(?im)^\s*(?:#+\s*)?(hook|opening hook|chapter\s+\d+\s*(?::[^\n]*)?)\s*$")
        matches = list(pattern.finditer(text))

        if not matches:
            return []

        parsed = []

        for index, match in enumerate(matches):
            heading = match.group(1).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()

            if not body:
                continue

            if heading.lower() in {"hook", "opening hook"}:
                hook_text = ContentNormalizer.normalize_hook(body)
                if hook_text:
                    parsed.append({
                        "chapter_number": "hook",
                        "type": "hook",
                        "title": "Hook",
                        "heading": "Hook",
                        "text": hook_text,
                        "word_count": ContentNormalizer.count_words(hook_text),
                        "status": "done",
                    })
                continue

            number_match = re.match(r"chapter\s+(\d+)\s*:?\s*(.*)$", heading, flags=re.IGNORECASE)
            if not number_match:
                continue

            chapter_number = int(number_match.group(1))
            parsed_title = number_match.group(2).strip()
            chapter_title = parsed_title or self.get_outline_title(chapter_number)
            chapter_text = ContentNormalizer.normalize_chapter(
                response=f"Chapter {chapter_number}: {chapter_title}\n\n{body}",
                chapter_number=chapter_number,
                chapter_title=chapter_title,
            )
            word_count = ContentNormalizer.count_words(chapter_text)

            parsed.append({
                "chapter_number": chapter_number,
                "title": chapter_title or f"Chapter {chapter_number}",
                "heading": ContentNormalizer.build_chapter_heading(chapter_number, chapter_title),
                "text": chapter_text,
                "word_count": word_count,
                "status": "done",
            })

        chapter_count = self.get_chapter_count()
        found_numbers = {
            item.get("chapter_number")
            for item in parsed
            if item.get("chapter_number") != "hook"
        }

        if len(found_numbers) < chapter_count:
            return []

        return parsed

    def ensure_thumbnail_prompt(self):
        step = "20_thumbnail_prompt"

        if getattr(self.project, "seo_meta", ""):
            self.mark_step(step, "Bỏ qua", "Đã có SEO meta và thumbnail prompt")
            self.status("Đã có SEO meta và thumbnail prompt. Bỏ qua.", 99)
            return

        self.status("Đang tạo SEO meta và prompt thumbnail...", 98)

        new_script = self.build_new_script_text()
        if not new_script.strip():
            self.mark_step(step, "Lỗi", "Không có script mới để tạo SEO meta")
            raise ValueError("Không có script mới để tạo SEO meta.")

        prompt = build_thumbnail_prompt_prompt(
            title=self.project.title,
            niche=getattr(self.project, "niche", "Family Betrayal"),
            story_bible=self.project.story_bible,
            outline=self.project.outline,
            script_text=new_script,
        )

        response = self.send_prompt(
            step,
            "08_thumbnail_prompt",
            prompt,
            expect_json=False,
        )

        self.project.thumbnail_prompt = response or ""
        self.project.seo_meta = response or ""
        self.project.step_status["thumbnail_prompt"] = "done"
        self.project.step_status["seo_meta"] = "done"
        self.autosave()

        self.mark_step(step, "Hoàn tất", "Hoàn tất SEO meta và thumbnail prompt", response)
        self.status("Hoàn tất SEO meta và thumbnail prompt.", 99)

    def build_new_script_text(self) -> str:
        parts = []

        def chapter_key(item):
            number = item.get("chapter_number")
            if number == "hook":
                return 0
            try:
                return int(number)
            except Exception:
                return 999

        for chapter in sorted(self.project.chapters or [], key=chapter_key):
            text = (chapter.get("text") or "").strip()
            if text:
                parts.append(text)

        return "\n\n".join(parts).strip()

    def write_chapter(self, chapter_number: int, step_key: str):
        self.status(f"Đang viết Chapter {chapter_number}...", 60 + chapter_number * 3)

        previous_text = self.get_previous_text(chapter_number)
        chapter_title = self.get_outline_title(chapter_number)

        try:
            total_words = self.get_target_words()
        except Exception:
            total_words = 10000

        chapter_count = self.get_chapter_count()
        target_words = self.get_chapter_target_words(chapter_number)

        prompt = build_chapter_prompt(
            title=self.project.title,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            story_bible=self.project.story_bible,
            outline=self.project.outline,
            previous_text=previous_text,
            target_words=target_words,
            total_target_words=total_words,
            chapter_count=chapter_count,
            narration_pov=PromptValueMapper.narration_pov(self.project.narration_pov),
            target_audience=PromptValueMapper.audience(self.project.target_audience),
            tone=PromptValueMapper.tone(self.project.tone),
            niche=getattr(self.project, "niche", "Family Betrayal"),
        )

        response = self.send_prompt(
            step_key,
            f"06_chapter_{chapter_number:02d}",
            prompt,
            expect_json=False,
        )

        if ContentNormalizer.looks_like_outline_json(response):
            self.mark_step(
                step_key,
                "Lỗi",
                f"Chapter {chapter_number} nhận nhầm Outline JSON.",
                response,
            )
            raise ValueError(
                f"Chapter {chapter_number} nhận nhầm Outline JSON, không phải prose."
            )

        chapter_text = ContentNormalizer.normalize_chapter(
            response=response,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
        )

        if chapter_number == 1:
            hook_text = self.get_hook_text()

            if hook_text and ContentNormalizer.has_large_overlap(
                hook_text,
                chapter_text,
                threshold=0.28,
            ):
                ratio = ContentNormalizer.similarity_ratio(hook_text, chapter_text)

                self.mark_step(
                    step_key,
                    "Đang sửa",
                    f"Chapter 1 bị lặp Hook quá nhiều. Similarity: {ratio:.2f}. Đang viết lại.",
                    chapter_text,
                )

                rewrite_prompt = build_chapter_prompt(
                    title=self.project.title,
                    chapter_number=chapter_number,
                    chapter_title=chapter_title,
                    story_bible=self.project.story_bible,
                    outline=self.project.outline,
                    previous_text=(
                        "The Hook has already been narrated. Do not repeat it. "
                        "Write Chapter 1 as a continuation with new action, new context, "
                        "or a new consequence immediately.\n\n"
                        f"HOOK TO AVOID REPEATING:\n{hook_text[:1200]}"
                    ),
                    target_words=target_words,
                    total_target_words=total_words,
                    chapter_count=chapter_count,
                    narration_pov=PromptValueMapper.narration_pov(self.project.narration_pov),
                    target_audience=PromptValueMapper.audience(self.project.target_audience),
                    tone=PromptValueMapper.tone(self.project.tone),
                    niche=getattr(self.project, "niche", "Family Betrayal"),
                )

                response = self.send_prompt(
                    step_key,
                    f"06_chapter_{chapter_number:02d}_rewrite",
                    rewrite_prompt,
                    expect_json=False,
                )

                chapter_text = ContentNormalizer.normalize_chapter(
                    response=response,
                    chapter_number=chapter_number,
                    chapter_title=chapter_title,
                )

        if not chapter_text:
            self.mark_step(step_key, "Lỗi", f"Không lấy được text Chapter {chapter_number}", response)
            raise ValueError(f"Không lấy được text Chapter {chapter_number}.")

        word_count = ContentNormalizer.count_words(chapter_text)
        min_words = self.get_chapter_min_words()

        status = "done" if word_count >= min_words else "too_short"

        heading = ContentNormalizer.build_chapter_heading(
            chapter_number,
            chapter_title,
        )

        self.upsert_chapter({
            "chapter_number": chapter_number,
            "title": chapter_title or f"Chapter {chapter_number}",
            "heading": heading,
            "text": chapter_text,
            "word_count": word_count,
            "status": status,
        })

        self.project.step_status[f"chapter_{chapter_number}"] = status
        self.autosave()

        self.mark_step(step_key, "Hoàn tất", f"Chapter {chapter_number}: {word_count} từ", response)
        self.status(f"Hoàn tất Chapter {chapter_number}: {word_count} từ.", 60 + chapter_number * 3)
    
    def setup_browser(self):
        self.log(f"Worker đang kết nối Chrome port {self.chrome_port}...")

        self.chrome = ChromeController(port=self.chrome_port)
        self.chrome.connect()

        self.gemini = GeminiClient(
            chrome_controller=self.chrome,
            log_func=self.log,
        )

        self.gemini.open()

        self.log("Worker đã mở Gemini.")

    def get_hook_text(self) -> str:
        for item in self.project.chapters or []:
            if item.get("type") == "hook":
                return item.get("text", "")

            if item.get("chapter_number") == "hook":
                return item.get("text", "")

        return ""
    
    def replace_forbidden_names_locally(self, duplicated_names: list[str]):
        """
        Fallback local: nếu Gemini vẫn dùng tên bị cấm,
        tự thay trực tiếp trong selected_premise và story_bible.
        """

        unique_bad_names = []

        for name in duplicated_names or []:
            if name and name not in unique_bad_names:
                unique_bad_names.append(name)

        fallback_pool = [
            "Nora Caldwell",
            "Marvin Brooks",
            "Lydia Harper",
            "Samuel Pierce",
            "Clara Bennett",
            "Elaine Mercer",
            "Warren Hayes",
            "Rachel Monroe",
            "Graham Ellis",
            "Audrey Fletcher",
            "Vivian Brooks",
            "Harold Camden",
            "Miriam Lawson",
            "Thomas Bell",
            "Janet Reeves",
            "Patrick Sloan",
            "Laura Whitman",
            "Dennis Carver",
            "Helen Porter",
            "Robert Hale",
        ]

        mapping = {}

        used_replacements = set()

        for index, bad_name in enumerate(unique_bad_names):
            replacement = ""

            for candidate in fallback_pool:
                if candidate not in used_replacements:
                    replacement = candidate
                    used_replacements.add(candidate)
                    break

            if not replacement:
                replacement = f"Character {index + 1}"

            mapping[bad_name] = replacement

        def replace_value(value):
            if isinstance(value, str):
                new_value = value

                for old_name, new_name in mapping.items():
                    new_value = new_value.replace(old_name, new_name)

                    # Thay thêm first / last name nếu Gemini rải lẻ
                    old_parts = old_name.split()
                    new_parts = new_name.split()

                    if len(old_parts) >= 2 and len(new_parts) >= 2:
                        new_value = new_value.replace(old_parts[0], new_parts[0])
                        new_value = new_value.replace(old_parts[-1], new_parts[-1])

                return new_value

            if isinstance(value, dict):
                return {
                    key: replace_value(item)
                    for key, item in value.items()
                }

            if isinstance(value, list):
                return [
                    replace_value(item)
                    for item in value
                ]

            return value

        self.project.selected_premise = replace_value(self.project.selected_premise)
        self.project.story_bible = replace_value(self.project.story_bible)

        self.log(
            "Đã tự thay tên bị cấm bằng fallback local: "
            + ", ".join([f"{old} -> {new}" for old, new in mapping.items()])
        )

        return mapping
    
    def rewrite_story_bible_names(self, duplicated_names: list[str], original_response: str = ""):
        """
        Yêu cầu Gemini đổi toàn bộ tên bị cấm trong selected_premise + story_bible.
        Chỉ đổi tên, không đổi cốt truyện.
        """

        unique_bad_names = []

        for name in duplicated_names or []:
            if name and name not in unique_bad_names:
                unique_bad_names.append(name)

        forbidden_names_text = NameRegistry.get_forbidden_names_text()

        repair_prompt = f"""
    ROLE:
    You are a professional story continuity editor.

    TASK:
    The selected premise and story bible below contain forbidden or previously used character names.

    You must replace all forbidden names with fresh, realistic American names.

    CRITICAL:
    - Do not change the plot.
    - Do not change relationships.
    - Do not change emotional arcs.
    - Do not change the selected niche.
    - Do not change the revenge mechanism.
    - Only replace forbidden names.
    - Replace first names, last names, and full names consistently everywhere.
    - Do not use any name from the forbidden list.
    - Do not use David, Evelyn, Julian, Richard, Elena, Arthur, Miller, Sterling, Vance, or Thorne.
    - Do not use Thorne as a last name.
    - Do not repeat the same first name or last name.
    - Names must feel ordinary and realistic for American adults.

    FORBIDDEN NAMES FOUND:
    {unique_bad_names}

    FULL FORBIDDEN NAME LIST:
    {forbidden_names_text}

    CURRENT SELECTED PREMISE:
    {self.project.selected_premise}

    CURRENT STORY BIBLE:
    {self.project.story_bible}

    Return ONLY valid JSON using this exact shape:
    {{
    "selected_premise": {{}},
    "story_bible": {{}}
    }}

    Rules:
    - Return valid JSON only.
    - Do not wrap JSON in markdown.
    - Do not add explanation.
    - Do not add notes.
    - The first character must be {{
    - The last character must be }}
    """

        self.log(
            "Story Bible có tên bị cấm. Đang yêu cầu Gemini đổi tên: "
            + ", ".join(unique_bad_names)
        )

        response = self.send_prompt(
            "03_story_bible",
            "03_story_bible_name_repair",
            repair_prompt,
            expect_json=True,
        )

        data = self.parse_json_response(
            response=response,
            step_key="03_story_bible",
            task_name="03_story_bible_name_repair",
        )

        new_selected_premise = data.get("selected_premise")
        new_story_bible = data.get("story_bible")

        if isinstance(new_selected_premise, dict):
            self.project.selected_premise = new_selected_premise

        if isinstance(new_story_bible, dict):
            self.project.story_bible = new_story_bible

        return response
    
    def is_bad_gemini_response(
        self,
        response: str,
        prompt: str,
        expect_json: bool = False,
    ) -> bool:
        """
        Kiểm tra response có lỗi phổ biến không:
        - rỗng
        - quá ngắn
        - copy lại prompt
        - step JSON nhưng không có dấu JSON
        """

        text = (response or "").strip()

        if not text:
            return True

        if len(text) < 30:
            return True

        prompt_head = (prompt or "").strip()[:2000]
        text_head = text[:2000]

        try:
            ratio = SequenceMatcher(None, prompt_head, text_head).ratio()
            if ratio >= 0.82:
                self.log(f"Response giống prompt quá cao. Similarity: {ratio:.2f}")
                return True
        except Exception:
            pass

        # Với step JSON, chỉ bắt lỗi rất thô.
        # Không parse ở đây, vì parse_json_response sẽ xử lý repair sau.
        if expect_json:
            has_json_signal = "{" in text and "}" in text
            if not has_json_signal:
                return True

        # Một số lỗi Gemini hay trả
        bad_phrases = [
            "i can't help with that",
            "i cannot assist",
            "something went wrong",
            "try again",
            "there was an error",
        ]

        lower_text = text.lower()

        if any(phrase in lower_text for phrase in bad_phrases):
            return True

        return False


    def reopen_gemini_chat_for_retry(self, step_key: str, task_name: str):
        """
        Mở lại khung chat Gemini mới để chạy lại step hiện tại.
        Ưu tiên gọi method nếu GeminiClient có sẵn.
        Nếu không có thì gọi lại self.gemini.open().
        """

        self.mark_step(
            step_key,
            "Đang mở chat mới",
            f"Gemini bị kẹt ở {task_name}. Đang mở chat mới và chạy lại.",
        )

        self.log(f"Gemini bị kẹt ở {task_name}. Đang mở chat mới...")

        try:
            if hasattr(self.gemini, "open_new_chat"):
                self.gemini.open_new_chat()
                return

            if hasattr(self.gemini, "new_chat"):
                self.gemini.new_chat()
                return

            # fallback: mở lại Gemini hiện tại
            self.gemini.open()

        except Exception as e:
            self.log(f"Không mở được chat mới bằng GeminiClient: {e}")

            try:
                self.setup_browser()
            except Exception as e2:
                self.log(f"Reconnect browser cũng lỗi: {e2}")
