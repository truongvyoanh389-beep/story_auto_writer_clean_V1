def build_script_evaluation_prompt(
    title: str,
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

FINAL EDITOR NOTES:
- concrete notes for revision

TITLE:
{title}

ORIGINAL SCRIPT:
{original_script}

NEW SCRIPT:
{new_script}
""".strip()
