from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class StoryProject:
    project_name: str = ""
    output_folder: str = "outputs"
    profile_name: str = ""

    title: str = ""
    transcript: str = ""

    target_words: int = 10000
    genre: str = "revenge family drama"
    narration_pov: str = "Ngôi thứ nhất - Tôi / của tôi"
    target_audience: str = "Người Mỹ từ 45 tuổi trở lên"
    tone: str = "Cảm xúc chân thực"
    revenge_intensity: str = "Trung bình - sự thật được phơi bày"
    ending_type: str = "Kết thúc có bài học đạo đức"
    niche: str = "Family Betrayal"

    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    ai_chat_url: str = ""

    input_signature: str = ""
    settings_signature: str = ""
    script_evaluation_signature: str = ""
    segment_signature: str = ""
    thumbnail_signature: str = ""

    input_analysis: dict[str, Any] = field(default_factory=dict)
    premises: list[dict[str, Any]] = field(default_factory=list)
    selected_premise: dict[str, Any] = field(default_factory=dict)
    story_bible: dict[str, Any] = field(default_factory=dict)
    outline: dict[str, Any] = field(default_factory=dict)
    chapters: list[dict[str, Any]] = field(default_factory=list)

    raw_responses: dict[str, str] = field(default_factory=dict)
    step_status: dict[str, str] = field(default_factory=dict)
    script_evaluation: str = ""
    final_repair: str = ""
    segment_script: str = ""
    thumbnail_prompt: str = ""
    seo_meta: str = ""

    version: str = "1.1"

    def touch(self):
        self.updated_at = now_iso()

    def to_dict(self) -> dict[str, Any]:
        self.touch()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoryProject":
        project = cls()

        project.project_name = data.get("project_name", "")
        project.output_folder = data.get("output_folder", "outputs")
        project.profile_name = data.get("profile_name", "")

        project.title = data.get("title", "")
        project.transcript = data.get("transcript", "")

        project.target_words = int(data.get("target_words", 10000) or 10000)
        project.narration_pov = data.get(
            "narration_pov",
            "Ngôi thứ nhất - Tôi / của tôi"
        )
        project.target_audience = data.get(
            "target_audience",
            "Người Mỹ từ 45 tuổi trở lên",
        )
        project.genre = data.get("genre", "revenge family drama")
        project.tone = data.get("tone", "Cảm xúc chân thực")
        project.revenge_intensity = data.get(
            "revenge_intensity",
            "Trung bình - sự thật được phơi bày",
        )
        project.ending_type = data.get("ending_type", "Kết thúc có bài học đạo đức")
        project.niche = data.get("niche", "Family Betrayal")

        project.created_at = data.get("created_at", now_iso())
        project.updated_at = data.get("updated_at", now_iso())

        project.ai_chat_url = data.get("ai_chat_url", "")
        project.input_signature = data.get("input_signature", "")
        project.settings_signature = data.get("settings_signature", "")
        project.script_evaluation_signature = data.get("script_evaluation_signature", "")
        project.segment_signature = data.get("segment_signature", "")
        project.thumbnail_signature = data.get("thumbnail_signature", "")

        project.input_analysis = data.get("input_analysis", {})
        project.premises = data.get("premises", [])
        project.selected_premise = data.get("selected_premise", {})
        project.story_bible = data.get("story_bible", {})
        project.outline = data.get("outline", {})
        project.chapters = data.get("chapters", [])

        project.raw_responses = data.get("raw_responses", {})
        project.step_status = data.get("step_status", {})
        project.script_evaluation = data.get("script_evaluation", "")
        project.final_repair = data.get("final_repair", "")
        project.segment_script = data.get("segment_script", "")
        project.thumbnail_prompt = data.get("thumbnail_prompt", "")
        project.seo_meta = data.get("seo_meta", "")

        project.version = data.get("version", "1.1")

        return project
