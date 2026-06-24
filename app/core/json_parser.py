import json
import re


class JsonParser:
    @staticmethod
    def extract_json_object(text: str) -> dict:
        if not text or not text.strip():
            raise ValueError("Nội dung rỗng, không có JSON để parse.")

        cleaned = JsonParser._remove_code_fence(text.strip())

        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return data
            raise ValueError("JSON hợp lệ nhưng không phải object.")
        except Exception:
            pass

        json_text = JsonParser._find_first_json_object(cleaned)

        if not json_text:
            raise ValueError(
                "Không tìm thấy JSON object trong response.\n\n"
                f"Preview:\n{cleaned[:1200]}"
            )

        try:
            return json.loads(json_text)
        except Exception:
            repaired = JsonParser._repair_json(json_text)

            if isinstance(repaired, dict):
                return repaired

            raise ValueError(
                "Có JSON object nhưng parse thất bại.\n\n"
                f"Preview:\n{json_text[:1200]}"
            )

    @staticmethod
    def _remove_code_fence(text: str) -> str:
        text = text.strip()

        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r"```$", "", text).strip()

        return text

    @staticmethod
    def _find_first_json_object(text: str) -> str:
        start = text.find("{")

        if start < 0:
            return ""

        depth = 0
        in_string = False
        escape = False

        for i in range(start, len(text)):
            ch = text[i]

            if escape:
                escape = False
                continue

            if ch == "\\":
                escape = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1

                if depth == 0:
                    return text[start:i + 1]

        return ""

    @staticmethod
    def _repair_json(text: str):
        try:
            from json_repair import repair_json
            return repair_json(text, return_objects=True)
        except Exception:
            return None