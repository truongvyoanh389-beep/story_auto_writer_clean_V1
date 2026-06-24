import json
from pathlib import Path


class ChromeProfileStore:
    STORE_PATH = Path("config") / "chrome_profiles.json"
    DEFAULT_CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    DEFAULT_BASE_DIR = r"D:\ChromeProfile"

    @classmethod
    def load(cls) -> list[dict]:
        if not cls.STORE_PATH.exists():
            return [cls.default_profile()]

        try:
            data = json.loads(cls.STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return [cls.default_profile()]

        profiles = data.get("profiles", [])
        if not isinstance(profiles, list) or not profiles:
            return [cls.default_profile()]

        return [cls.normalize(profile) for profile in profiles]

    @classmethod
    def save(cls, profiles: list[dict]):
        cls.STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        normalized = [cls.normalize(profile) for profile in profiles]
        cls.STORE_PATH.write_text(
            json.dumps({"profiles": normalized}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def default_profile(cls) -> dict:
        return {
            "name": "pro1",
            "port": 9222,
            "user_data_dir": str(Path(cls.DEFAULT_BASE_DIR) / "pro1"),
            "profile_directory": "default",
            "chrome_path": cls.DEFAULT_CHROME_PATH,
        }

    @classmethod
    def normalize(cls, profile: dict) -> dict:
        name = str(profile.get("name") or "pro1").strip()
        try:
            port = int(profile.get("port") or 9222)
        except Exception:
            port = 9222

        return {
            "name": name,
            "port": port,
            "user_data_dir": str(profile.get("user_data_dir") or Path(cls.DEFAULT_BASE_DIR) / name),
            "profile_directory": str(profile.get("profile_directory") or "default"),
            "chrome_path": str(profile.get("chrome_path") or cls.DEFAULT_CHROME_PATH),
        }
