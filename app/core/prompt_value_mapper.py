class PromptValueMapper:
    POV_VI_TO_EN = {
        "Ngôi thứ nhất - Tôi / của tôi": "First person, using I / me / my / mine",
        "Ngôi thứ hai - Bạn / của bạn": "Second person, using you / your",
        "Ngôi thứ ba giới hạn": "Third person limited",
        "Ngôi thứ ba toàn tri": "Third person omniscient",
    }

    AUDIENCE_VI_TO_EN = {
        "Người Mỹ từ 45 tuổi trở lên": "American adults aged 45 and above",
        "Phụ nữ Mỹ từ 45 tuổi trở lên": "American women aged 45 and above",
        "Đàn ông Mỹ từ 45 tuổi trở lên": "American men aged 45 and above",
        "Người Mỹ cao tuổi từ 60 tuổi trở lên": "American seniors aged 60 and above",
        "Khán giả Mỹ trưởng thành nói chung": "General American adult audience",
    }

    TONE_VI_TO_EN = {
        "Cảm xúc chân thực": "emotionally realistic",
        "Cảm xúc chậm, thấm sâu": "slow-burn emotional",
        "Căng thẳng, kịch tính nhưng đời thường": "tense and dramatic but grounded",
        "Lặng, đau, nhiều suy ngẫm": "quiet, painful, and reflective",
        "Tối ưu giữ chân người nghe audio": "high-retention text-to-speech narration",
    }

    REVENGE_VI_TO_EN = {
        "Trung bình - sự thật được phơi bày": "medium revenge intensity, truth exposed",
        "Nhẹ - đặt ranh giới cảm xúc": "low revenge intensity, emotional boundary",
        "Cao - phơi bày công khai": "high revenge intensity, public exposure",
        "Hậu quả pháp lý / tài chính nhưng thực tế": "legal / financial consequence but realistic",
        "Đảo ngược danh tiếng trong gia đình": "family reputation reversal",
    }

    ENDING_VI_TO_EN = {
        "Kết thúc có bài học đạo đức": "moral lesson ending",
        "Công lý được thực thi": "justice served ending",
        "Kết thúc bằng ranh giới lặng lẽ": "quiet boundary ending",
        "Hoà giải buồn vui lẫn lộn": "bittersweet reconciliation ending",
        "Không liên lạc, giữ lòng tự trọng": "no-contact self-respect ending",
    }

    @staticmethod
    def _reverse(mapping: dict) -> dict:
        return {v: k for k, v in mapping.items()}

    @staticmethod
    def narration_pov(value: str) -> str:
        return PromptValueMapper.POV_VI_TO_EN.get(value, value)

    @staticmethod
    def audience(value: str) -> str:
        return PromptValueMapper.AUDIENCE_VI_TO_EN.get(value, value)

    @staticmethod
    def tone(value: str) -> str:
        return PromptValueMapper.TONE_VI_TO_EN.get(value, value)

    @staticmethod
    def revenge_intensity(value: str) -> str:
        return PromptValueMapper.REVENGE_VI_TO_EN.get(value, value)

    @staticmethod
    def ending_type(value: str) -> str:
        return PromptValueMapper.ENDING_VI_TO_EN.get(value, value)

    @staticmethod
    def pov_to_vi(value: str) -> str:
        return PromptValueMapper._reverse(PromptValueMapper.POV_VI_TO_EN).get(value, value)

    @staticmethod
    def audience_to_vi(value: str) -> str:
        return PromptValueMapper._reverse(PromptValueMapper.AUDIENCE_VI_TO_EN).get(value, value)

    @staticmethod
    def tone_to_vi(value: str) -> str:
        return PromptValueMapper._reverse(PromptValueMapper.TONE_VI_TO_EN).get(value, value)

    @staticmethod
    def revenge_to_vi(value: str) -> str:
        return PromptValueMapper._reverse(PromptValueMapper.REVENGE_VI_TO_EN).get(value, value)

    @staticmethod
    def ending_to_vi(value: str) -> str:
        return PromptValueMapper._reverse(PromptValueMapper.ENDING_VI_TO_EN).get(value, value)