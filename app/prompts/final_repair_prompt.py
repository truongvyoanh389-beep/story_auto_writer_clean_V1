def build_final_repair_prompt(
    title: str,
    story_bible: dict,
    outline: dict,
    evaluation_report: str,
    script_text: str,
    target_words: int,
    chapter_count: int,
) -> str:
    return f"""
ROLE:
You are a senior continuity editor and final-pass YouTube script doctor.

TASK:
Repair the completed script using the evaluation report.

This is NOT a rewrite from scratch.
Make only the necessary fixes.
Preserve the plot, chapter order, emotional arc, and approximate length.

ORIGINAL USER TITLE:
{title}

STORY BIBLE / CANONICAL FACTS:
{story_bible}

OUTLINE:
{outline}

SCRIPT EVALUATION REPORT:
{evaluation_report}

CURRENT FULL SCRIPT:
{script_text}

TARGET LENGTH:
- Total script target: about {target_words} words.
- Total chapter count: {chapter_count}.
- Keep the repaired script close to the current length unless a small adjustment is required.

REPAIR PRIORITIES:
1. Fix all name continuity issues immediately.
2. Preserve canonical protagonist, antagonist, and supporting character names from the Story Bible.
3. Fix antagonist / protagonist name mixing.
4. Fix continuity or logic issues listed in the evaluation report.
5. Lightly improve pacing issues listed in the report.
6. Simplify dense technical or legal jargon only where the report says it may hurt retention.
7. Keep emotional impact stronger than technical explanation.

STRICT LIMITS:
- Do not invent a new story.
- Do not change the ending.
- Do not remove major plot beats.
- Do not add new characters unless required to fix continuity.
- Do not summarize.
- Do not return analysis.
- Do not return markdown notes.
- Do not output JSON.

OUTPUT FORMAT:
Return the full corrected script only.

Use this exact structure:

Hook

[corrected hook prose]

Chapter 1: [existing chapter title]

[corrected chapter 1 prose]

Chapter 2: [existing chapter title]

[corrected chapter 2 prose]

Continue through the final chapter.
"""
