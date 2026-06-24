# app/prompts/outline_prompt.py

from app.prompts.prompt_contracts import (
    JSON_OUTPUT_CONTRACT,
    FINAL_JSON_ONLY_INSTRUCTION,
)


def build_outline_prompt(
    title: str = "",
    story_bible: dict | None = None,
    target_words: int = 10000,
    chapter_count: int = 10,
    narration_pov: str = "first person",
    target_audience: str = "American adults aged 45+",
    tone: str = "grounded emotional drama",
    revenge_intensity: str = "medium",
    ending_type: str = "satisfying moral ending",
    niche: str = "Family Betrayal",
) -> str:
    if story_bible is None:
        story_bible = {}

    if not title:
        title = story_bible.get("original_user_title", "") or story_bible.get("story_title", "")

    return f"""
ROLE:
You are a professional American long-form story outline architect for viral YouTube-style text-to-speech drama.

TASK:
Create a complete chapter outline from the Story Bible.

You are NOT writing the full story.
You are NOT writing the Hook.
You are NOT writing chapter prose.
You are only creating the chapter plan.

ORIGINAL USER TITLE:
{title}

STORY BIBLE:
{story_bible}

TARGET SETTINGS:
- Target words: {target_words}
- Chapter count: {chapter_count}
- Narration POV: {narration_pov}
- Target audience: {target_audience}
- Tone: {tone}
- Revenge intensity: {revenge_intensity}
- Ending type: {ending_type}
- Selected niche: {niche}

ORIGINAL TITLE LOCK:
The final script title must remain exactly:
{title}

Do not replace it with a new title.
Do not use the selected premise title as the final title.

NICHE LOCK:
The outline must stay inside the selected niche:
{niche}

{JSON_OUTPUT_CONTRACT}

JSON SCHEMA:
{{
  "outline_title": "{title}",
  "original_user_title": "{title}",
  "niche": "{niche}",
  "total_chapters": {chapter_count},
  "target_total_words": {target_words},
  "overall_arc": "",
  "hook_strategy": "",
  "chapters": [
    {{
      "chapter_number": 1,
      "chapter_title": "",
      "chapter_function": "",
      "target_words": 0,
      "opening_state": "",
      "main_events": [],
      "emotional_beats": [],
      "conflict": "",
      "reveal_or_twist": "",
      "retention_hook": "",
      "must_include_details": [],
      "must_avoid": [],
      "continuity_notes": ""
    }}
  ],
  "continuity_plan": [],
  "realism_guardrails": [],
  "chapter_1_anti_repeat_instruction": ""
}}

OUTPUT COUNT RULES:
- total_chapters must exactly equal {chapter_count}.
- chapters must contain exactly {chapter_count} items.
- chapter_number must start at 1 and increase sequentially.
- Do not return fewer chapters.
- Do not return more chapters.
- Do not add extra fields.
- Do not omit fields.

FIELD RULES:
1. outline_title:
- Must exactly equal the original user title:
{title}

2. original_user_title:
- Must exactly equal:
{title}

3. niche:
- Must exactly equal:
{niche}

4. overall_arc:
- Must describe the full emotional journey from betrayal to final payoff.

5. hook_strategy:
- Must describe how the separate Hook should retain viewers.
- Do not write the Hook text here.

6. chapters:
- Each chapter must have a distinct narrative function.
- Each chapter must move the story forward.
- Do not repeat the same function in neighboring chapters.
- Chapter 1 must begin after the Hook, not repeat the Hook.
- Chapter 1 must introduce new action, new consequence, or new context immediately.
- Each retention_hook must create a reason to continue to the next chapter.

7. target_words:
- Each chapter target_words must be a JSON number.
- Total chapter target_words should roughly match {target_words}.
- The sum of all chapter target_words should leave about 120 to 220 words for the Hook.
- Do not plan oversized chapters. Each chapter target must fit the total budget.

CONTENT RULES:
- Use English for every field value.
- Stay inside the selected niche: {niche}.
- Keep the story grounded and realistic.
- Preserve continuity from the Story Bible.
- Preserve the original user title.
- Do not write prose.
- Do not write dialogue.
- Do not write sound effects, music cues, or stage directions.
- Do not output markdown.
- Do not output text outside JSON.

CHAPTER 1 ANTI-REPETITION LAW:
- Chapter 1 must not repeat the Hook.
- Assume the listener already heard the Hook.
- Chapter 1 must continue after the Hook's final emotional beat.
- Chapter 1 must not reuse the same opening image, same first paragraph, or same reveal structure as the Hook.
- Chapter 1 must add new information or consequence immediately.

FINAL CHECK BEFORE ANSWERING:
- Is the response one valid JSON object?
- Does the response start with {{ and end with }}?
- Is outline_title exactly the original user title?
- Is original_user_title exactly the original user title?
- Is niche exactly the selected niche?
- Are there exactly {chapter_count} chapters?
- Are chapter_number values sequential?
- Is there no markdown?
- Is there no explanation outside JSON?

{FINAL_JSON_ONLY_INSTRUCTION}
"""
