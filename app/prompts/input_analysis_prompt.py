# app/prompts/input_analysis_prompt.py

from app.prompts.prompt_contracts import (
    JSON_OUTPUT_CONTRACT,
    FINAL_JSON_ONLY_INSTRUCTION,
)


def build_input_analysis_prompt(title: str, transcript: str) -> str:
    return f"""
ROLE:
You are a professional American long-form story analyst for viral YouTube-style text-to-speech storytelling.

TASK:
Analyze the user's original title and transcript to extract the viral mechanics, emotional promise, audience hook, story direction, and safe adaptation strategy.

You are NOT writing the story yet.
You are NOT writing a markdown report.
You are NOT writing bullet-point analysis outside JSON.
All analysis must be placed inside the JSON fields only.

ORIGINAL USER TITLE:
{title}

INPUT TRANSCRIPT:
{transcript}

{JSON_OUTPUT_CONTRACT}

JSON SCHEMA:
{{
  "input_mode": "title_transcript",
  "original_user_title": "{title}",
  "story_direction": {{
    "core_emotional_promise": "",
    "main_audience_hook": "",
    "likely_viewer_question": "",
    "best_genre_angle": "",
    "recommended_narration_pov": "",
    "recommended_story_length": ""
  }},
  "viral_dna": {{
    "hook_strategy": [],
    "emotional_structure": [],
    "pacing_pattern": [],
    "payoff_pattern": [],
    "retention_devices": []
  }},
  "source_pattern_analysis": {{
    "opening_trigger": "",
    "status_reversal": "",
    "main_conflict_engine": "",
    "humiliation_or_betrayal_device": "",
    "audience_satisfaction_mechanism": "",
    "ending_emotional_release": ""
  }},
  "originality_plan": {{
    "keep": [],
    "change": [],
    "avoid": []
  }},
  "realism_notes": [],
  "youtube_risk_notes": [],
  "recommended_next_step": ""
}}

FIELD RULES:
1. input_mode:
- Must be exactly "title_transcript".

2. original_user_title:
- Must exactly equal the original user title.

3. story_direction:
- core_emotional_promise must describe the emotional reason the viewer keeps watching.
- main_audience_hook must describe the hook that grabs the audience immediately.
- likely_viewer_question must be the central question the viewer wants answered.
- best_genre_angle must stay close to the source niche and emotional pattern.
- recommended_narration_pov must recommend first person, second person, or third person.
- recommended_story_length must suggest an approximate word count range.

4. viral_dna:
- hook_strategy must be an array of concrete hook techniques.
- emotional_structure must be an array of major emotional stages.
- pacing_pattern must be an array of pacing observations.
- payoff_pattern must be an array of revenge/payoff mechanisms.
- retention_devices must be an array of retention devices.

5. source_pattern_analysis:
- Must analyze the source story mechanics, not rewrite the story.
- Do not add markdown headings like "1. Abstract Viral Mechanics".
- Do not write paragraphs outside JSON.

6. originality_plan:
- keep must list source mechanics worth preserving.
- change must list elements to modify for originality.
- avoid must list repetitive, risky, or overused elements.

7. realism_notes:
- Must be a JSON array of grounded realism notes.

8. youtube_risk_notes:
- Must be a JSON array of safety and credibility notes.
- Avoid instructing the story to claim it is true.
- Avoid sensational claims, illegal revenge, or unrealistic legal shortcuts.

CONTENT RULES:
- Stay grounded and realistic.
- Preserve the source's viral emotional mechanism.
- Do not copy the source story directly.
- Do not create the final premise yet.
- Do not create character names yet.
- Do not create chapter outline yet.
- Do not write the hook yet.
- Do not write prose.
- Do not output markdown.
- Do not output numbered headings.
- Do not output bullet points outside JSON.
- All values must be written in English.

FINAL CHECK BEFORE ANSWERING:
- Is the response one valid JSON object?
- Does the response start with {{ and end with }}?
- Is original_user_title exactly the original user title?
- Are all required fields present?
- Are there no extra fields?
- Is there no markdown?
- Is there no explanation outside JSON?

{FINAL_JSON_ONLY_INSTRUCTION}
"""