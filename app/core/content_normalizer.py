import re
from difflib import SequenceMatcher

from app.core.json_parser import JsonParser


class ContentNormalizer:
    TEXT_KEYS = [
        "hook_text",
        "hook",
        "chapter_text",
        "chapter",
        "content",
        "text",
        "story_text",
        "prose",
        "final_text",
    ]

    @staticmethod
    def normalize_hook(response: str) -> str:
        text = ContentNormalizer.extract_text(response)
        text = ContentNormalizer.clean_text(text)
        text = ContentNormalizer.remove_hook_heading(text)
        return text.strip()

    @staticmethod
    def normalize_chapter(
        response: str,
        chapter_number: int,
        chapter_title: str = "",
    ) -> str:
        text = ContentNormalizer.extract_text(response)
        text = ContentNormalizer.clean_text(text)
        body = ContentNormalizer.remove_chapter_heading(text, chapter_number).strip()

        heading = ContentNormalizer.build_chapter_heading(
            chapter_number,
            chapter_title,
        )

        if not body:
            return heading

        return f"{heading}\n\n{body}".strip()

    @staticmethod
    def extract_text(response: str) -> str:
        raw = (response or "").strip()

        if not raw:
            return ""

        try:
            data = JsonParser.extract_json_object(raw)
            text = ContentNormalizer.extract_text_from_json(data)

            if text:
                return text
        except Exception:
            pass

        return raw

    @staticmethod
    def extract_text_from_json(data) -> str:
        if isinstance(data, str):
            return data

        if isinstance(data, dict):
            for key in ContentNormalizer.TEXT_KEYS:
                value = data.get(key)

                if isinstance(value, str) and value.strip():
                    return value.strip()

                if isinstance(value, dict):
                    nested = ContentNormalizer.extract_text_from_json(value)
                    if nested:
                        return nested

            long_values = []

            for value in data.values():
                if isinstance(value, str) and len(value.strip()) > 80:
                    long_values.append(value.strip())

            if long_values:
                return "\n\n".join(long_values)

        if isinstance(data, list):
            parts = []

            for item in data:
                text = ContentNormalizer.extract_text_from_json(item)
                if text:
                    parts.append(text)

            return "\n\n".join(parts)

        return ""

    @staticmethod
    def clean_text(text: str) -> str:
        text = (text or "").strip()

        if text.startswith("```"):
            text = re.sub(r"^```(?:json|text|markdown)?", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r"```$", "", text).strip()

        prefixes = [
            "Here is the hook:",
            "Here is the chapter:",
            "Sure, here is",
            "Below is",
            "As requested,",
        ]

        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = ContentNormalizer.remove_production_notes(text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @staticmethod
    def remove_hook_heading(text: str) -> str:
        lines = text.splitlines()

        while lines and not lines[0].strip():
            lines.pop(0)

        if not lines:
            return ""

        first = lines[0].strip()

        if re.match(r"^(#+\s*)?(hook|opening hook)\s*:?\s*$", first, re.IGNORECASE):
            return "\n".join(lines[1:]).strip()

        match = re.match(r"^(hook|opening hook)\s*:\s*(.+)$", first, re.IGNORECASE)

        if match:
            lines[0] = match.group(2).strip()

        return "\n".join(lines).strip()

    @staticmethod
    def remove_chapter_heading(text: str, chapter_number: int) -> str:
        lines = text.splitlines()

        while lines and not lines[0].strip():
            lines.pop(0)

        if not lines:
            return ""

        first = lines[0].strip()

        patterns = [
            rf"^#+\s*chapter\s*{chapter_number}\s*[:\-—–].*$",
            rf"^chapter\s*{chapter_number}\s*[:\-—–].*$",
            rf"^#+\s*chapter\s*{chapter_number}\s*$",
            rf"^chapter\s*{chapter_number}\s*$",
            rf"^#+\s*chương\s*{chapter_number}\s*[:\-—–].*$",
            rf"^chương\s*{chapter_number}\s*[:\-—–].*$",
        ]

        for pattern in patterns:
            if re.match(pattern, first, re.IGNORECASE):
                return "\n".join(lines[1:]).strip()

        return "\n".join(lines).strip()

    @staticmethod
    def build_chapter_heading(chapter_number: int, chapter_title: str = "") -> str:
        title = ContentNormalizer.clean_heading_title(chapter_title)

        if title:
            return f"Chapter {chapter_number}: {title}"

        return f"Chapter {chapter_number}"

    @staticmethod
    def clean_heading_title(title: str) -> str:
        title = (title or "").strip()
        title = re.sub(r"^chapter\s*\d+\s*[:\-—–]\s*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^chương\s*\d+\s*[:\-—–]\s*", "", title, flags=re.IGNORECASE)
        return title.strip()

    @staticmethod
    def count_words(text: str) -> int:
        return len((text or "").split())
    
    @staticmethod
    def remove_production_notes(text: str) -> str:
        text = text or ""

        # Xoá các dòng dạng:
        # [Sound effect: ...]
        # [Music: ...]
        # [SFX: ...]
        # [The sound of ...]
        patterns = [
            r"^\s*\[(?:sound effect|sfx|music|audio|ambience|ambient sound|voiceover|vo|cut to|fade in|fade out|camera|scene|stage direction)[^\]]*\]\s*$",
            r"^\s*\((?:sound effect|sfx|music|audio|ambience|ambient sound|voiceover|vo|cut to|fade in|fade out|camera|scene|stage direction)[^\)]*\)\s*$",
        ]

        lines = []

        for line in text.splitlines():
            stripped = line.strip()

            should_remove = False

            for pattern in patterns:
                if re.match(pattern, stripped, flags=re.IGNORECASE):
                    should_remove = True
                    break

            # Xoá cả dòng kiểu "Sound effect: ..."
            if re.match(
                r"^\s*(sound effect|sfx|music|audio cue|ambience|ambient sound|voiceover|vo|cut to|fade in|fade out|camera|stage direction)\s*:",
                stripped,
                flags=re.IGNORECASE,
            ):
                should_remove = True

            if not should_remove:
                lines.append(line)

        cleaned = "\n".join(lines)

        # Xoá production note nằm giữa paragraph nếu có
        cleaned = re.sub(
            r"\[(?:Sound effect|SFX|Music|Audio|Ambience|Ambient sound|Voiceover|VO|Cut to|Fade in|Fade out|Camera|Scene|Stage direction)[^\]]*\]",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\((?:Sound effect|SFX|Music|Audio|Ambience|Ambient sound|Voiceover|VO|Cut to|Fade in|Fade out|Camera|Scene|Stage direction)[^\)]*\)",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        return cleaned.strip()
    
    @staticmethod
    def looks_like_outline_json(text: str) -> bool:
        text = (text or "").strip()

        if not text.startswith("{"):
            return False

        markers = [
            '"outline_title"',
            '"total_chapters"',
            '"overall_arc"',
            '"chapters"',
            '"chapter_function"',
            '"continuity_plan"',
            '"realism_guardrails"',
        ]

        return sum(1 for marker in markers if marker in text) >= 3
    
    @staticmethod
    def normalize_for_similarity(text: str) -> str:
        text = text or ""
        text = text.lower()
        text = re.sub(r"chapter\s+\d+\s*:\s*.+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


    @staticmethod
    def similarity_ratio(a: str, b: str) -> float:
        a = ContentNormalizer.normalize_for_similarity(a)
        b = ContentNormalizer.normalize_for_similarity(b)

        if not a or not b:
            return 0.0

        # Chỉ so phần đầu vì lỗi thường là Chapter 1 lặp nguyên Hook ở đầu.
        a = a[:2500]
        b = b[:2500]

        return SequenceMatcher(None, a, b).ratio()


    @staticmethod
    def has_large_overlap(a: str, b: str, threshold: float = 0.28) -> bool:
        return ContentNormalizer.similarity_ratio(a, b) >= threshold
    
    @staticmethod
    def hook_has_strong_opening(text: str) -> bool:
        text = (text or "").strip()

        if not text:
            return False

        first_part = text[:500].lower()

        tension_words = [
            "empty",
            "gone",
            "stolen",
            "betray",
            "betrayed",
            "lie",
            "lied",
            "secret",
            "locked",
            "safe",
            "court",
            "judge",
            "police",
            "sheriff",
            "lawyer",
            "auction",
            "debt",
            "fraud",
            "signature",
            "inheritance",
            "will",
            "threat",
            "humiliated",
            "erased",
            "ruined",
        ]

        return any(word in first_part for word in tension_words)