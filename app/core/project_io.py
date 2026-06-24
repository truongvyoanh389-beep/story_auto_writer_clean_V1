import json
from pathlib import Path

from app.core.project_model import StoryProject


class ProjectIO:
    @staticmethod
    def safe_name(name: str) -> str:
        name = (name or "untitled_project").strip()
        invalid = '<>:"/\\|?*'

        for ch in invalid:
            name = name.replace(ch, "_")

        return name or "untitled_project"

    @staticmethod
    def project_dir(project: StoryProject) -> Path:
        safe = ProjectIO.safe_name(project.project_name or project.title)
        profile = ProjectIO.safe_name(getattr(project, "profile_name", "") or "no_profile")
        path = Path(project.output_folder or "outputs") / profile / safe
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def project_path(project: StoryProject) -> Path:
        return ProjectIO.project_dir(project) / "project.json"

    @staticmethod
    def save(project: StoryProject) -> Path:
        path = ProjectIO.project_path(project)
        path.write_text(
            json.dumps(project.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    @staticmethod
    def load(path: str | Path) -> StoryProject:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return StoryProject.from_dict(data)

    @staticmethod
    def save_raw_response(project: StoryProject, task_name: str, text: str) -> Path:
        raw_dir = ProjectIO.project_dir(project) / "raw_responses"
        raw_dir.mkdir(parents=True, exist_ok=True)

        path = raw_dir / f"{task_name}.txt"
        path.write_text(text or "", encoding="utf-8")

        project.raw_responses[task_name] = str(path)

        return path
