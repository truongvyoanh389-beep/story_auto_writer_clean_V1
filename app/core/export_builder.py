from pathlib import Path

from app.core.project_io import ProjectIO
from app.core.project_model import StoryProject


class ExportBuilder:
    @staticmethod
    def export(project: StoryProject) -> dict:
        export_dir = ProjectIO.project_dir(project) / "export"
        export_dir.mkdir(parents=True, exist_ok=True)

        full_story = ExportBuilder.build_full_story(project)
        title = project.story_bible.get("story_title") or project.title or project.project_name
        file_name = ProjectIO.safe_name(title or "story") + ".txt"

        full_path = export_dir / file_name

        full_path.write_text(full_story, encoding="utf-8")

        seo_meta = getattr(project, "seo_meta", "") or getattr(project, "thumbnail_prompt", "")
        seo_meta_path = export_dir / "seo_meta.txt"
        seo_meta_path.write_text(seo_meta or "", encoding="utf-8")

        segment_script = getattr(project, "segment_script", "")
        segment_script_path = export_dir / "segment_script.txt"
        segment_script_path.write_text(segment_script or "", encoding="utf-8")

        chapters_dir = export_dir / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        for chapter in ExportBuilder.sorted_chapters(project.chapters):
            number = chapter.get("chapter_number")
            text = chapter.get("text", "").strip()

            if not text:
                continue

            if number == "hook":
                file_name = "00_hook.txt"
            else:
                file_name = f"{int(number):02d}_chapter_{int(number)}.txt"

            (chapters_dir / file_name).write_text(text + "\n", encoding="utf-8")

        return {
            "export_dir": str(export_dir),
            "story": str(full_path),
            "seo_meta": str(seo_meta_path),
            "segment_script": str(segment_script_path),
            "chapters_dir": str(chapters_dir),
        }

    @staticmethod
    def build_full_story(project: StoryProject) -> str:
        parts = []

        for chapter in ExportBuilder.sorted_chapters(project.chapters):
            text = chapter.get("text", "").strip()

            if text:
                parts.append(text)
                parts.append("")

        return "\n".join(parts).strip() + "\n"

    @staticmethod
    def build_timeline(project: StoryProject) -> str:
        lines = [
            "VIDEO STRUCTURE / TIMELINE",
            "==========================",
            "",
        ]

        for chapter in ExportBuilder.sorted_chapters(project.chapters):
            number = chapter.get("chapter_number")
            word_count = chapter.get("word_count", 0)

            if number == "hook":
                title = "Hook"
            else:
                title = chapter.get("heading") or chapter.get("title") or f"Chapter {number}"

                if not str(title).lower().startswith("chapter"):
                    title = f"Chapter {number}: {title}"

            lines.append(f"- {title} ({word_count} words)")

        lines.append("")
        lines.append("Note: Add exact timestamps after TTS/render because voice speed changes duration.")

        return "\n".join(lines).strip() + "\n"

    @staticmethod
    def sorted_chapters(chapters: list[dict]) -> list[dict]:
        def key_func(chapter: dict):
            number = chapter.get("chapter_number")

            if number == "hook":
                return 0

            try:
                return int(number)
            except Exception:
                return 999

        return sorted(chapters or [], key=key_func)
