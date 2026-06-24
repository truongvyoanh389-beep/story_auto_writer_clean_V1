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

CANON LOCK:
The Story Bible and Outline are the highest authority.
The evaluation report is advisory only and must never override canon.
If the evaluation report asks for or implies a change that would alter the core story, reject that suggestion and restore the Story Bible instead.

CORE STORY ELEMENTS THAT MUST NOT CHANGE:
- Main character name, gender, role, authority, hidden leverage, and emotional wound.
- Antagonist name, gender, role, relationship to the main character, and betrayal function.
- Core conflict, public humiliation, secret reveal, revenge/payoff mechanism, and ending.
- Chapter order and major plot beats from the Outline.

REPAIR MODE SAFETY:
- If the report says CANON_RESTORE, only restore wrong canon details. Do not rewrite scenes that already match canon.
- If the report says CHAPTER_REPAIR, repair only the affected chapters or paragraphs named in the report.
- If a repair would require changing the whole premise, do not do that. Preserve canon and make the smallest local correction.
- Example: if the Story Bible says the antagonist is the father, never change him into the mother. If the current script does that, change those lines back to the father while preserving the scene.

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
- Do not change the protagonist.
- Do not change the antagonist.
- Do not change family relationships, military/career identity, secret leverage, core betrayal, or final payoff.
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


def build_section_repair_prompt(
    title: str,
    story_bible: dict,
    outline: dict,
    evaluation_report: str,
    repair_mode: str,
    section_heading: str,
    section_text: str,
    previous_context: str = "",
    next_context: str = "",
    target_words: int = 0,
) -> str:
    length_rule = ""
    if target_words:
        length_rule = f"- Keep this section close to about {target_words} words unless a small fix requires otherwise."

    return f"""
ROLE:
You are a senior continuity editor repairing ONE section of a long YouTube revenge story.

TASK:
Repair only the section below using the evaluation report and Story Bible.
Do not rewrite the whole script.
Do not change sections outside this one.

REPAIR MODE:
{repair_mode}

CANON LOCK:
The Story Bible and Outline are the highest authority.
The evaluation report is advisory only and must never override canon.
If the current section violates canon, restore the canon with the smallest possible local edit.

CORE STORY ELEMENTS THAT MUST NOT CHANGE:
- Main character name, gender, role, authority, hidden leverage, and emotional wound.
- Antagonist name, gender, role, relationship to the main character, and betrayal function.
- Core conflict, public humiliation, secret reveal, revenge/payoff mechanism, and ending.
- Chapter order and major plot beats from the Outline.

STRICT LIMITS:
- Repair only this section.
- Preserve the existing heading.
- Preserve the section's approximate length and narrative function.
- Do not invent a new story.
- Do not change protagonist, antagonist, family relationships, career identity, secret leverage, core betrayal, or payoff.
- Do not summarize.
- Do not return analysis.
- Do not output JSON.

TARGET LENGTH:
{length_rule}

ORIGINAL USER TITLE:
{title}

STORY BIBLE / CANONICAL FACTS:
{story_bible}

OUTLINE:
{outline}

SCRIPT EVALUATION REPORT:
{evaluation_report}

PREVIOUS CONTEXT FOR CONTINUITY ONLY:
{previous_context}

SECTION TO REPAIR:
{section_heading}

{section_text}

NEXT CONTEXT FOR CONTINUITY ONLY:
{next_context}

OUTPUT FORMAT:
Return only the corrected section, including the same heading.
Do not include notes, bullets, markdown commentary, or explanations.
""".strip()
