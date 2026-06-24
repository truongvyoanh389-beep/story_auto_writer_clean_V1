# app/core/name_registry.py

import json
import random
import re
from pathlib import Path
from typing import Any


class NameRegistry:
    """
    Quản lý tên nhân vật cho story generator.

    Chức năng:
    - Tự tạo app/data/american_names_1000.json nếu chưa có.
    - Random tên Mỹ không trùng.
    - Lưu tên đã dùng vào outputs/_name_registry.json.
    - Tự thay tên bị cấm / tên cũ / tên lặp.
    - Nhân vật gia đình dùng cùng họ với main character.
    """

    DATA_DIR = Path("app") / "data"
    NAME_BANK_PATH = DATA_DIR / "american_names_1000.json"
    REGISTRY_PATH = Path("outputs") / "_name_registry.json"

    DEFAULT_FORBIDDEN_NAMES = {
        "david", "david miller", "miller",
        "evelyn", "evelyn thorne", "thorne",
        "julian", "julian thorne", "julian vance",
        "richard", "richard sterling", "sterling",
        "elena", "elena vance", "vance",
        "arthur", "arthur vance",
        "marcus", "marcus vance",
        "gerald", "gerald hendricks",
    }

    FAMILY_RELATION_KEYWORDS = [
        "husband",
        "wife",
        "son",
        "daughter",
        "mother",
        "father",
        "mother-in-law",
        "father-in-law",
        "sister",
        "brother",
        "sister-in-law",
        "brother-in-law",
        "cousin",
        "aunt",
        "uncle",
        "grandmother",
        "grandfather",
        "stepmother",
        "stepfather",
        "family",
        "in-law",
        "parent",
        "child",
        "spouse",
    ]

    MALE_FIRST_NAMES = [
        "Aaron", "Adam", "Alan", "Albert", "Andrew", "Anthony", "Arthur", "Barry",
        "Benjamin", "Blake", "Bradley", "Brandon", "Brian", "Bruce", "Caleb",
        "Carl", "Charles", "Christopher", "Clarence", "Craig", "Daniel", "Darren",
        "Dean", "Dennis", "Derek", "Donald", "Douglas", "Edward", "Elliot",
        "Eric", "Ethan", "Eugene", "Frank", "Frederick", "Gary", "George",
        "Graham", "Gregory", "Harold", "Henry", "Howard", "Isaac", "Jack",
        "Jacob", "James", "Jason", "Jeffrey", "Jeremy", "Joel", "John",
        "Jonathan", "Joseph", "Joshua", "Kenneth", "Kevin", "Lawrence", "Leonard",
        "Louis", "Malcolm", "Martin", "Matthew", "Michael", "Nathan", "Nicholas",
        "Patrick", "Paul", "Peter", "Philip", "Raymond", "Robert", "Roger",
        "Ronald", "Russell", "Samuel", "Scott", "Stephen", "Steven", "Terrence",
        "Thomas", "Timothy", "Victor", "Vincent", "Walter", "Wayne", "William",
        "Warren", "Neil", "Grant", "Cole", "Wesley", "Norman", "Clifford",
    ]

    FEMALE_FIRST_NAMES = [
        "Abigail", "Alice", "Amanda", "Amy", "Angela", "Ann", "Audrey", "Barbara",
        "Beth", "Beverly", "Brenda", "Caroline", "Catherine", "Charlotte", "Cheryl",
        "Christine", "Claire", "Clara", "Cynthia", "Diane", "Donna", "Dorothy",
        "Elaine", "Elizabeth", "Emily", "Erica", "Frances", "Gloria", "Grace",
        "Hannah", "Harriet", "Helen", "Irene", "Jacqueline", "Janet", "Janice",
        "Jean", "Jennifer", "Joan", "Joyce", "Judith", "Julia", "Karen",
        "Kathleen", "Katherine", "Laura", "Lauren", "Linda", "Lisa", "Louise",
        "Margaret", "Maria", "Marilyn", "Martha", "Mary", "Melissa", "Michelle",
        "Nancy", "Natalie", "Nora", "Olivia", "Pamela", "Patricia", "Paula",
        "Rachel", "Rebecca", "Rose", "Ruth", "Sandra", "Sharon", "Sheila",
        "Stephanie", "Susan", "Teresa", "Theresa", "Valerie", "Victoria",
        "Virginia", "Vivian", "Wendy", "Yvonne", "Diana", "Monica", "Carol",
    ]

    LAST_NAMES = [
        "Abbott", "Adler", "Alden", "Baker", "Baldwin", "Barrett", "Baxter",
        "Beckett", "Bell", "Bennett", "Benson", "Bishop", "Blackwell", "Blair",
        "Boone", "Bowman", "Bradford", "Bradley", "Brennan", "Brooks", "Bryant",
        "Burke", "Caldwell", "Camden", "Carlson", "Carver", "Chandler", "Chapman",
        "Clayton", "Collins", "Connelly", "Cooper", "Crawford", "Daniels",
        "Dawson", "Delaney", "Donovan", "Douglas", "Doyle", "Duncan", "Ellis",
        "Emerson", "Fletcher", "Foster", "Franklin", "Gallagher", "Garrett",
        "Gibson", "Goodwin", "Granger", "Grant", "Grayson", "Greene", "Griffin",
        "Hale", "Hamilton", "Harper", "Harris", "Harrison", "Hart", "Hawkins",
        "Hayes", "Henderson", "Holland", "Hudson", "Hunter", "Ingram", "Jennings",
        "Keller", "Kennedy", "Kingston", "Lambert", "Lawson", "Lennox", "Lewis",
        "Logan", "Maddox", "Marshall", "Mason", "Maxwell", "Mercer", "Mitchell",
        "Monroe", "Morgan", "Morrison", "Newton", "Nolan", "Norris", "Palmer",
        "Parker", "Pearson", "Pierce", "Porter", "Preston", "Quinn", "Reed",
        "Reeves", "Reynolds", "Rhodes", "Roberts", "Rowan", "Russell", "Sanders",
        "Sawyer", "Sloan", "Spencer", "Sullivan", "Taylor", "Turner", "Wallace",
        "Walsh", "Warner", "Watkins", "Weaver", "Wells", "West", "Whitaker",
        "Whitman", "Wilcox", "Winslow", "Wright", "Young",
    ]

    @staticmethod
    def normalize_name(name: str) -> str:
        name = name or ""
        name = name.strip().lower()
        name = re.sub(r"\s+", " ", name)
        name = re.sub(r"[^a-z\s'-]", "", name)
        return name.strip()

    @staticmethod
    def split_name(name: str) -> tuple[str, str]:
        normalized = NameRegistry.normalize_name(name)
        parts = normalized.split()

        if not parts:
            return "", ""

        first = parts[0]
        last = parts[-1] if len(parts) >= 2 else ""

        return first, last

    @staticmethod
    def make_full_name(first: str, last: str) -> str:
        return f"{first.strip()} {last.strip()}".strip()

    @staticmethod
    def ensure_name_bank() -> list[dict]:
        """
        Đảm bảo có file app/data/american_names_1000.json.
        Nếu chưa có thì tự tạo 1000 tên.
        """

        NameRegistry.DATA_DIR.mkdir(parents=True, exist_ok=True)

        if NameRegistry.NAME_BANK_PATH.exists():
            try:
                data = json.loads(NameRegistry.NAME_BANK_PATH.read_text(encoding="utf-8"))

                if isinstance(data, list) and len(data) >= 1000:
                    return data
            except Exception:
                pass

        records = []
        seen = set()

        rng = random.Random(20260701)

        first_pool = []

        for first in NameRegistry.MALE_FIRST_NAMES:
            first_pool.append((first, "male"))

        for first in NameRegistry.FEMALE_FIRST_NAMES:
            first_pool.append((first, "female"))

        candidates = []

        for first, gender in first_pool:
            for last in NameRegistry.LAST_NAMES:
                full_name = NameRegistry.make_full_name(first, last)
                normalized = NameRegistry.normalize_name(full_name)

                if normalized in NameRegistry.DEFAULT_FORBIDDEN_NAMES:
                    continue

                first_norm, last_norm = NameRegistry.split_name(full_name)

                if first_norm in NameRegistry.DEFAULT_FORBIDDEN_NAMES:
                    continue

                if last_norm in NameRegistry.DEFAULT_FORBIDDEN_NAMES:
                    continue

                candidates.append({
                    "full_name": full_name,
                    "first_name": first,
                    "last_name": last,
                    "gender": gender,
                })

        rng.shuffle(candidates)

        for item in candidates:
            normalized = NameRegistry.normalize_name(item["full_name"])

            if normalized in seen:
                continue

            seen.add(normalized)
            records.append(item)

            if len(records) >= 1000:
                break

        NameRegistry.NAME_BANK_PATH.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return records

    @staticmethod
    def load_registry() -> dict:
        if not NameRegistry.REGISTRY_PATH.exists():
            return {
                "used_full_names": [],
                "used_first_names": [],
                "used_last_names": [],
            }

        try:
            data = json.loads(NameRegistry.REGISTRY_PATH.read_text(encoding="utf-8"))

            if not isinstance(data, dict):
                raise ValueError("registry invalid")

            data.setdefault("used_full_names", [])
            data.setdefault("used_first_names", [])
            data.setdefault("used_last_names", [])

            return data

        except Exception:
            return {
                "used_full_names": [],
                "used_first_names": [],
                "used_last_names": [],
            }

    @staticmethod
    def save_registry(data: dict):
        NameRegistry.REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        NameRegistry.REGISTRY_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def get_all_forbidden_names() -> set[str]:
        data = NameRegistry.load_registry()

        names = set(NameRegistry.DEFAULT_FORBIDDEN_NAMES)
        names.update(data.get("used_full_names", []))
        names.update(data.get("used_first_names", []))
        names.update(data.get("used_last_names", []))

        return {
            NameRegistry.normalize_name(name)
            for name in names
            if NameRegistry.normalize_name(name)
        }

    @staticmethod
    def get_forbidden_names_text(limit: int = 250) -> str:
        names = sorted(NameRegistry.get_all_forbidden_names())

        if len(names) > limit:
            names = names[-limit:]

        if not names:
            return "- none"

        return "\n".join(f"- {name}" for name in names)

    @staticmethod
    def mark_name_used(full_name: str):
        full_name_norm = NameRegistry.normalize_name(full_name)

        if not full_name_norm:
            return

        first, last = NameRegistry.split_name(full_name_norm)

        data = NameRegistry.load_registry()

        used_full = set(data.get("used_full_names", []))
        used_first = set(data.get("used_first_names", []))
        used_last = set(data.get("used_last_names", []))

        used_full.add(full_name_norm)

        if first:
            used_first.add(first)

        if last:
            used_last.add(last)

        data["used_full_names"] = sorted(used_full)
        data["used_first_names"] = sorted(used_first)
        data["used_last_names"] = sorted(used_last)

        NameRegistry.save_registry(data)

    @staticmethod
    def is_name_forbidden(name: str) -> bool:
        normalized = NameRegistry.normalize_name(name)

        if not normalized:
            return True

        first, last = NameRegistry.split_name(normalized)
        forbidden = NameRegistry.get_all_forbidden_names()

        if normalized in forbidden:
            return True

        if first and first in forbidden:
            return True

        if last and last in forbidden:
            return True

        return False

    @staticmethod
    def allocate_name(gender: str = "", last_name: str = "", mark_used: bool = False) -> str:
        """
        Lấy 1 tên từ bank.
        Nếu truyền last_name thì giữ họ đó.
        """

        bank = NameRegistry.ensure_name_bank()
        forbidden = NameRegistry.get_all_forbidden_names()

        gender_norm = (gender or "").strip().lower()
        last_name = (last_name or "").strip()

        candidates = []

        for item in bank:
            item_gender = item.get("gender", "")
            first = item.get("first_name", "")
            last = last_name or item.get("last_name", "")
            full_name = NameRegistry.make_full_name(first, last)

            normalized = NameRegistry.normalize_name(full_name)
            first_norm, last_norm = NameRegistry.split_name(full_name)

            if normalized in forbidden:
                continue

            if first_norm in forbidden:
                continue

            if last_norm in forbidden:
                continue

            if gender_norm in ["male", "m", "man"] and item_gender != "male":
                continue

            if gender_norm in ["female", "f", "woman"] and item_gender != "female":
                continue

            candidates.append(full_name)

        if not candidates:
            # fallback rất hiếm
            full_name = NameRegistry.make_full_name("Morgan", last_name or "Reed")
        else:
            full_name = random.choice(candidates)

        if mark_used:
            NameRegistry.mark_name_used(full_name)

        return full_name

    @staticmethod
    def is_family_relationship(relationship_text: str) -> bool:
        text = (relationship_text or "").lower()

        return any(keyword in text for keyword in NameRegistry.FAMILY_RELATION_KEYWORDS)

    @staticmethod
    def replace_text_value(value: Any, mapping: dict[str, str]) -> Any:
        if isinstance(value, str):
            new_value = value

            for old_name, new_name in mapping.items():
                if not old_name or not new_name:
                    continue

                new_value = new_value.replace(old_name, new_name)

                old_parts = old_name.split()
                new_parts = new_name.split()

                if len(old_parts) >= 2 and len(new_parts) >= 2:
                    new_value = re.sub(
                        rf"\b{re.escape(old_parts[0])}\b",
                        new_parts[0],
                        new_value,
                    )
                    new_value = re.sub(
                        rf"\b{re.escape(old_parts[-1])}\b",
                        new_parts[-1],
                        new_value,
                    )

            return new_value

        if isinstance(value, list):
            return [
                NameRegistry.replace_text_value(item, mapping)
                for item in value
            ]

        if isinstance(value, dict):
            return {
                key: NameRegistry.replace_text_value(item, mapping)
                for key, item in value.items()
            }

        return value

    @staticmethod
    def normalize_premises(premises: list[dict]) -> list[dict]:
        """
        Chuẩn hóa tên trong 10 premises.
        - Main character: random tên riêng từ bank.
        - Antagonist nếu là gia đình: cùng họ main.
        - Antagonist không phải gia đình: tên random khác.
        """

        normalized = []

        for premise in premises or []:
            if not isinstance(premise, dict):
                continue

            main = premise.get("main_character", {})
            antagonist = premise.get("antagonist", {})

            if not isinstance(main, dict):
                main = {}

            if not isinstance(antagonist, dict):
                antagonist = {}

            main_gender = main.get("gender", "")
            new_main_name = NameRegistry.allocate_name(
                gender=main_gender,
                mark_used=True,
            )

            _, main_last = NameRegistry.split_name(new_main_name)

            old_main_name = main.get("name", "")
            main["name"] = new_main_name

            antagonist_relation = antagonist.get("relationship_to_main_character", "")
            antagonist_gender = antagonist.get("gender", "")

            old_antagonist_name = antagonist.get("name", "")

            if NameRegistry.is_family_relationship(antagonist_relation):
                new_antagonist_name = NameRegistry.allocate_name(
                    gender=antagonist_gender,
                    last_name=main_last.title(),
                    mark_used=True,
                )
            else:
                new_antagonist_name = NameRegistry.allocate_name(
                    gender=antagonist_gender,
                    mark_used=True,
                )

            antagonist["name"] = new_antagonist_name

            mapping = {}

            if old_main_name and old_main_name != new_main_name:
                mapping[old_main_name] = new_main_name

            if old_antagonist_name and old_antagonist_name != new_antagonist_name:
                mapping[old_antagonist_name] = new_antagonist_name

            premise["main_character"] = main
            premise["antagonist"] = antagonist

            if mapping:
                premise = NameRegistry.replace_text_value(premise, mapping)

                # replace_text_value sẽ giữ dict mới, cần set lại tên chắc chắn
                premise["main_character"]["name"] = new_main_name
                premise["antagonist"]["name"] = new_antagonist_name

            normalized.append(premise)

        return normalized

    @staticmethod
    def normalize_project_names(project) -> dict[str, str]:
        """
        Chuẩn hóa tên trong selected_premise, story_bible, outline, chapters.
        Không raise lỗi. Luôn cố sửa local.
        """

        mapping = {}

        selected = getattr(project, "selected_premise", {}) or {}
        bible = getattr(project, "story_bible", {}) or {}

        main = {}
        antagonist = {}

        if isinstance(bible, dict):
            main = bible.get("main_character", {}) or {}
            antagonist = bible.get("antagonist", {}) or {}

        if not isinstance(main, dict):
            main = {}

        if not isinstance(antagonist, dict):
            antagonist = {}

        old_main_name = main.get("name", "")

        # Nếu main bị cấm hoặc thiếu tên thì thay
        if not old_main_name or NameRegistry.is_name_forbidden(old_main_name):
            new_main_name = NameRegistry.allocate_name(
                gender=main.get("gender", ""),
                mark_used=True,
            )

            if old_main_name:
                mapping[old_main_name] = new_main_name

            main["name"] = new_main_name
        else:
            new_main_name = old_main_name
            NameRegistry.mark_name_used(new_main_name)

        _, main_last = NameRegistry.split_name(new_main_name)
        main_last_title = main_last.title() if main_last else ""

        old_antagonist_name = antagonist.get("name", "")
        relation = antagonist.get("relationship_to_main_character", "")

        if not old_antagonist_name or NameRegistry.is_name_forbidden(old_antagonist_name):
            if NameRegistry.is_family_relationship(relation) and main_last_title:
                new_antagonist_name = NameRegistry.allocate_name(
                    gender=antagonist.get("gender", ""),
                    last_name=main_last_title,
                    mark_used=True,
                )
            else:
                new_antagonist_name = NameRegistry.allocate_name(
                    gender=antagonist.get("gender", ""),
                    mark_used=True,
                )

            if old_antagonist_name:
                mapping[old_antagonist_name] = new_antagonist_name

            antagonist["name"] = new_antagonist_name
        else:
            new_antagonist_name = old_antagonist_name
            NameRegistry.mark_name_used(new_antagonist_name)

        # Supporting characters
        supporting = bible.get("supporting_characters", []) if isinstance(bible, dict) else []

        if isinstance(supporting, list):
            for item in supporting:
                if not isinstance(item, dict):
                    continue

                old_name = item.get("name", "")
                relationship = item.get("relationship_to_main_character", "")
                gender = item.get("gender", "")

                must_replace = not old_name or NameRegistry.is_name_forbidden(old_name)

                if must_replace:
                    if NameRegistry.is_family_relationship(relationship) and main_last_title:
                        new_name = NameRegistry.allocate_name(
                            gender=gender,
                            last_name=main_last_title,
                            mark_used=True,
                        )
                    else:
                        new_name = NameRegistry.allocate_name(
                            gender=gender,
                            mark_used=True,
                        )

                    if old_name:
                        mapping[old_name] = new_name

                    item["name"] = new_name
                else:
                    NameRegistry.mark_name_used(old_name)

        if isinstance(bible, dict):
            bible["main_character"] = main
            bible["antagonist"] = antagonist
            bible["supporting_characters"] = supporting

        if mapping:
            project.selected_premise = NameRegistry.replace_text_value(
                getattr(project, "selected_premise", {}),
                mapping,
            )

            project.story_bible = NameRegistry.replace_text_value(
                getattr(project, "story_bible", {}),
                mapping,
            )

            project.outline = NameRegistry.replace_text_value(
                getattr(project, "outline", {}),
                mapping,
            )

            project.chapters = NameRegistry.replace_text_value(
                getattr(project, "chapters", []),
                mapping,
            )

            # Gán lại chắc chắn sau replace
            if isinstance(project.story_bible, dict):
                project.story_bible.setdefault("main_character", {})
                project.story_bible.setdefault("antagonist", {})
                project.story_bible["main_character"]["name"] = main["name"]
                project.story_bible["antagonist"]["name"] = antagonist["name"]

        return mapping

    @staticmethod
    def extract_names_from_project(project) -> list[str]:
        names = []

        def add(value):
            if isinstance(value, str) and value.strip():
                names.append(value.strip())

        selected = getattr(project, "selected_premise", {}) or {}
        bible = getattr(project, "story_bible", {}) or {}

        for source in [selected, bible]:
            if not isinstance(source, dict):
                continue

            for key in ["main_character", "protagonist", "antagonist"]:
                value = source.get(key)

                if isinstance(value, dict):
                    add(value.get("name", ""))
                elif isinstance(value, str):
                    add(value)

        supporting = bible.get("supporting_characters", []) if isinstance(bible, dict) else []

        if isinstance(supporting, list):
            for item in supporting:
                if isinstance(item, dict):
                    add(item.get("name", ""))
                elif isinstance(item, str):
                    add(item)

        return names

    @staticmethod
    def find_forbidden_names_in_project(project) -> list[str]:
        found = []

        for name in NameRegistry.extract_names_from_project(project):
            if NameRegistry.is_name_forbidden(name):
                found.append(name)

        return found

    @staticmethod
    def update_from_project(project):
        for name in NameRegistry.extract_names_from_project(project):
            NameRegistry.mark_name_used(name)