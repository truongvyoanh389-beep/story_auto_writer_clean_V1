def build_script_evaluation_prompt(
    title: str,
    story_bible: dict | None,
    outline: dict | None,
    original_script: str,
    new_script: str,
) -> str:
    return f"""
ROLE:
You are a senior YouTube script analyst and story editor.

TASK:
Compare the ORIGINAL SCRIPT with the NEW SCRIPT written by the tool.
Evaluate whether the new script keeps the strongest emotional promise of the original while improving retention, clarity, drama, and audience satisfaction.

Return a practical editor report, not a rewrite.

CANON RULE:
The Story Bible and Outline are the canonical source of truth for the new story.
Do not recommend changes that alter the locked core story unless the current new script already violates the Story Bible.
Examples of STRUCTURAL / CANON conflicts:
- Antagonist changed from father to mother, spouse to sibling, commander to civilian, etc.
- Main character identity, gender, job, authority, secret leverage, or relationship changed.
- Core betrayal, hidden truth, reveal, or final payoff changed into a different story.
- Timeline or relationship logic breaks the Story Bible.

Repair mode rules:
- SKIP: New script is better/equal or score new >= score original, and there are no canon conflicts.
- CANON_RESTORE: The script violates Story Bible / Outline canon. Restore canon only; do not rewrite the whole story creatively.
- CHAPTER_REPAIR: The script is worse and only selected chapters need safe fixes such as pacing, jargon, name consistency, or weak dialogue.
- FULL_REPAIR: Use only if the whole script is incoherent and cannot be fixed chapter-by-chapter.

EVALUATION CRITERIA:
1. Hook strength
2. Emotional stakes
3. Character clarity
4. Conflict escalation
5. Payoff and ending satisfaction
6. Retention risk
7. Repetition or filler
8. Continuity issues
9. Whether the new script is better, equal, or worse than the original
10. Whether the new script violates Story Bible / Outline canon

OUTPUT FORMAT:
Use this exact structure:

OVERALL VERDICT:
- Better / Equal / Worse:
- Score original: 0-10
- Score new: 0-10
- One paragraph verdict:

WHAT THE NEW SCRIPT IMPROVES:
- bullet points

WHAT THE NEW SCRIPT LOSES FROM THE ORIGINAL:
- bullet points

RETENTION RISKS:
- bullet points

CONTINUITY / LOGIC ISSUES:
- bullet points

CANON / STRUCTURAL CONFLICTS:
- None, or concrete conflicts against Story Bible / Outline

REPAIR_DECISION:
- Mode: SKIP / CANON_RESTORE / CHAPTER_REPAIR / FULL_REPAIR
- Reason:
- Affected chapters:
- Canon restore instructions:
- Safe chapter repair instructions:

FINAL EDITOR NOTES:
- concrete notes for revision

TITLE:
{title}

STORY BIBLE / CANON:
{story_bible or {}}

OUTLINE:
{outline or {}}

ORIGINAL SCRIPT:
{original_script}

NEW SCRIPT:
{new_script}
""".strip()
