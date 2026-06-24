# app/prompts/story_bible_prompt.py

from app.prompts.prompt_contracts import (
    JSON_OUTPUT_CONTRACT,
    FINAL_JSON_ONLY_INSTRUCTION,
)


def build_story_bible_prompt(
    title: str = "",
    selected_premise: dict | None = None,
    input_analysis: dict | None = None,
    target_words: int = 10000,
    narration_pov: str = "first person",
    target_audience: str = "American adults aged 45+",
    tone: str = "grounded emotional drama",
    revenge_intensity: str = "medium",
    ending_type: str = "satisfying moral ending",
    niche: str = "Family Betrayal",
    forbidden_names_text: str = "",
) -> str:
    if selected_premise is None:
        selected_premise = {}

    if input_analysis is None:
        input_analysis = {}

    if not title:
        title = selected_premise.get("original_user_title", "") or selected_premise.get("title", "")

    if not forbidden_names_text:
        forbidden_names_text = """
- david
- evelyn
- julian
- richard
- elena
- arthur
- miller
- sterling
- vance
- thorne
"""

    return f"""
ROLE:
You are a professional American long-form story bible architect for viral YouTube-style text-to-speech drama.

TASK:
Create a complete Story Bible from the selected premise.

You are NOT writing the full story yet.
You are NOT writing the hook.
You are NOT writing chapters.
You are NOT writing markdown.
You must return structured JSON only.

ORIGINAL USER TITLE:
{title}

SELECTED PREMISE:
{selected_premise}

INPUT ANALYSIS:
{input_analysis}

TARGET SETTINGS:
- Target words: {target_words}
- Narration POV: {narration_pov}
- Target audience: {target_audience}
- Tone: {tone}
- Revenge intensity: {revenge_intensity}
- Ending type: {ending_type}
- Selected niche: {niche}

ORIGINAL TITLE LOCK:
The final story title must remain exactly the user's original title:
{title}

Do not replace it with the selected premise title.
The selected premise title is only a development aid.
The final script, story bible, outline, hook, and chapters must use the original title as the story title.

NICHE LOCK:
The Story Bible must stay inside the selected niche:
{niche}

Do not drift into another niche unless it directly supports the original title and selected premise.
Do not turn the story into a courtroom, military, inheritance, secret billionaire, judge, hospital, or workplace story unless that is the selected niche or the selected premise clearly requires it.

NAME CONTINUITY LAW:
- Use the character names from the selected premise if they are valid and not forbidden.
- Do not replace names randomly.
- Do not use names from the forbidden list.
- Do not use David, Evelyn, Julian, Richard, Elena, Arthur, Miller, Sterling, Vance, or Thorne.
- Do not use Thorne as a last name.
- Keep all character names realistic for American adults.
- Do not create unnecessary supporting characters.

FORBIDDEN NAMES:
{forbidden_names_text}

{JSON_OUTPUT_CONTRACT}

JSON SCHEMA:
{{
  "story_title": "{title}",
  "original_user_title": "{title}",
  "niche": "{niche}",
  "logline": "",
  "narration": {{
    "pov": "",
    "voice": "",
    "tense": "",
    "audience_feel": ""
  }},
  "setting": {{
    "primary_location": "",
    "social_world": "",
    "time_period": "",
    "realism_level": ""
  }},
  "main_character": {{
    "name": "",
    "age": 0,
    "gender": "",
    "occupation": "",
    "family_role": "",
    "emotional_wound": "",
    "hidden_strength": "",
    "external_goal": "",
    "internal_need": "",
    "moral_boundary": ""
  }},
  "antagonist": {{
    "name": "",
    "age": 0,
    "gender": "",
    "relationship_to_main_character": "",
    "public_mask": "",
    "private_truth": "",
    "main_pressure_tactic": "",
    "emotional_weapon": ""
  }},
  "supporting_characters": [
    {{
      "name": "",
      "age": 0,
      "gender": "",
      "relationship_to_main_character": "",
      "story_function": "",
      "loyalty_position": ""
    }}
  ],
  "core_conflict": "",
  "core_betrayal": "",
  "hidden_truth": "",
  "revenge_or_boundary_mechanism": "",
  "emotional_arc": [],
  "retention_plan": [],
  "chapter_engine": {{
    "opening_question": "",
    "mid_story_escalation": "",
    "late_story_reversal": "",
    "final_payoff": ""
  }},
  "continuity_locks": [],
  "must_avoid": [],
  "youtube_safety_notes": []
}}

FIELD RULES:
- story_title must exactly equal the original user title:
{title}
- original_user_title must exactly equal:
{title}
- niche must exactly equal:
{niche}
- logline must be one concise sentence.
- narration.pov must match or logically adapt the requested narration POV.
- main_character.age and antagonist.age must be JSON numbers, not strings.
- supporting_characters may be an empty array if not needed.
- Do not create more than 4 supporting characters.
- retention_plan must include concrete retention devices.
- continuity_locks must define facts that later chapters must not contradict.
- must_avoid must include repetition risks, realism risks, and credibility risks.
- youtube_safety_notes must avoid true-story claims and unrealistic illegal revenge.

CONTENT RULES:
- Use English for every field value.
- Keep the story grounded and emotionally realistic.
- Preserve the selected premise.
- Preserve the original user title as the final script title.
- Stay inside the selected niche.
- Do not copy the source transcript directly.
- Do not write prose scenes.
- Do not write the Hook.
- Do not write chapters.
- Do not use sound effects, stage directions, music cues, or production notes.
- Do not output markdown.
- Do not output text outside JSON.

FINAL CHECK BEFORE ANSWERING:
- Is the response one valid JSON object?
- Does the response start with {{ and end with }}?
- Is story_title exactly the original user title?
- Is original_user_title exactly the original user title?
- Is niche exactly the selected niche?
- Are all required fields present?
- Are there no extra fields?
- Are forbidden names avoided?
- Is there no markdown?
- Is there no explanation outside JSON?

{FINAL_JSON_ONLY_INSTRUCTION}
"""