# app/prompts/premise_prompt.py

from app.prompts.prompt_contracts import (
    JSON_OUTPUT_CONTRACT,
    FINAL_JSON_ONLY_INSTRUCTION,
)


def build_premise_prompt(
    title: str,
    input_analysis: dict,
    target_words: int = 10000,
    narration_pov: str = "first person",
    target_audience: str = "American adults aged 45+",
    tone: str = "grounded emotional drama",
    revenge_intensity: str = "medium",
    ending_type: str = "satisfying moral ending",
    niche: str = "Family Betrayal",
    forbidden_names_text: str = "",
) -> str:
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
You are a professional American long-form viral story premise engine for YouTube-style text-to-speech narration.

TASK:
Generate exactly 10 fresh story premises based on the user's ORIGINAL TITLE, selected niche, and input analysis.

You are NOT writing the full story.
You are NOT writing the hook.
You are NOT writing chapters.
You are NOT writing markdown analysis.
You must return structured JSON only.

ORIGINAL USER TITLE:
{title}

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
The user's original title is the primary creative anchor:
{title}

All 10 premises must clearly fit this original title.
Do not generate premises that feel unrelated to the title.
Do not replace the story direction with a random viral template.
Each premise may have a different internal angle, but the final story must still be able to use the original title.

NICHE LOCK:
The selected niche is:
{niche}

Every premise must fit this selected niche.
Do not drift into another niche unless the original title and selected niche clearly support it.
If the selected niche is Military Female, every premise must include a believable military or veteran-related female-centered angle.
If the selected niche is Family Betrayal, every premise must center on family betrayal.
If the selected niche is Courtroom Revenge, every premise must involve a realistic legal/courtroom conflict.
If the selected niche is Inheritance, every premise must involve inheritance, wills, estate conflict, property, or family money.
If the selected niche is Rich Woman Hidden Identity, every premise must involve a woman whose status, wealth, or power is underestimated.
If the selected niche is Judge Stories, every premise must involve a judge, legal authority, or courtroom power dynamic.

NAME ORIGINALITY LAW:
- Use fresh, diverse, realistic American names.
- Do not use any first name, last name, or full name from the forbidden list.
- Do not use David, Evelyn, Julian, Richard, Elena, Arthur, Miller, Sterling, Vance, or Thorne.
- Do not repeat the same first name or last name across the 10 premises.
- Names must feel ordinary and realistic for American adults.
- Do not use melodramatic thriller names.

FORBIDDEN NAMES:
{forbidden_names_text}

{JSON_OUTPUT_CONTRACT}

JSON SCHEMA:
{{
  "premises": [
    {{
      "premise_id": "P01",
      "title": "",
      "original_user_title": "{title}",
      "niche": "{niche}",
      "original_title_fit": "",
      "niche_fit": "",
      "main_character": {{
        "name": "",
        "age": 0,
        "gender": "",
        "occupation": "",
        "family_role": "",
        "emotional_wound": "",
        "hidden_strength": ""
      }},
      "antagonist": {{
        "name": "",
        "age": 0,
        "gender": "",
        "relationship_to_main_character": "",
        "public_mask": "",
        "private_truth": ""
      }},
      "core_betrayal": "",
      "opening_hook": "",
      "hidden_truth": "",
      "revenge_or_boundary_mechanism": "",
      "midpoint_reversal": "",
      "public_payoff": "",
      "ending_promise": "",
      "why_it_will_retain_viewers": "",
      "youtube_safety_notes": "",
      "scores": {{
        "hook_strength": 0,
        "originality": 0,
        "emotional_realism": 0,
        "audience_fit": 0,
        "youtube_risk": "low"
      }}
    }}
  ]
}}

OUTPUT COUNT RULES:
- The top-level JSON object must contain exactly one key: "premises".
- "premises" must contain exactly 10 items.
- Do not return fewer than 10 premises.
- Do not return more than 10 premises.
- premise_id must be exactly: P01, P02, P03, P04, P05, P06, P07, P08, P09, P10.
- Each premise must contain exactly the fields shown in the schema.
- Do not add extra fields.
- Do not omit fields.
- Do not rename fields.

FIELD RULES:
1. title:
- Must be a viral American English title.
- It may differ from the original user title as a development title, but the final script must keep the original user title.
- Must not claim the story is true.

2. original_user_title:
- Must exactly equal:
{title}

3. niche:
- Must exactly equal:
{niche}

4. original_title_fit:
- Must explain why this premise fits the original user title.

5. niche_fit:
- Must explain why this premise fits the selected niche.

6. main_character:
- Must have a fresh name not found in the forbidden list.
- age must be a JSON number, not a string.
- Must feel suitable for American adults aged 45+ as listeners.
- Must have a clear emotional wound and hidden strength.

7. antagonist:
- Must have a fresh name not found in the forbidden list.
- age must be a JSON number, not a string.
- Must have a clear relationship to the main character.
- Must have a public mask and private truth.

8. core_betrayal:
- Must be clear, personal, and emotionally painful.
- Must be grounded and realistic.
- Must not rely on illegal revenge fantasy.

9. opening_hook:
- Must create immediate tension from the first sentence.
- Must strongly retain the audience.
- Must create a major unanswered question.

10. revenge_or_boundary_mechanism:
- Must be realistic.
- Must fit the selected revenge intensity:
{revenge_intensity}

11. public_payoff:
- Must give emotional satisfaction.
- Must not require unrealistic court/legal shortcuts unless the selected niche naturally requires it.

12. ending_promise:
- Must fit the selected ending type:
{ending_type}

13. scores:
- hook_strength must be a number from 1 to 10.
- originality must be a number from 1 to 10.
- emotional_realism must be a number from 1 to 10.
- audience_fit must be a number from 1 to 10.
- youtube_risk must be exactly one of: "low", "medium", "high".

CONTENT RULES:
- Use English for every field value.
- Stay grounded, adult, emotional, and realistic.
- Preserve the viral emotional mechanism from the input analysis.
- Do not copy the source transcript directly.
- Do not use the same premise structure 10 times.
- Do not use repeated character names.
- Do not use repeated occupations across all 10 premises.
- Do not make every story courtroom-based unless the selected niche requires it.
- Do not make every story military-based unless the selected niche requires it.
- Do not make every protagonist secretly rich unless the selected niche requires it.
- Do not include sound effects, music cues, production notes, camera directions, or stage directions.
- This is story planning for text-to-speech narration, not an audio production script.

FINAL CHECK BEFORE ANSWERING:
- Is the response one valid JSON object?
- Does the response start with {{ and end with }}?
- Does the top-level object contain only "premises"?
- Are there exactly 10 premises?
- Are premise_id values exactly P01 through P10?
- Is original_user_title exactly the original user title?
- Is niche exactly the selected niche?
- Does every premise explain original_title_fit and niche_fit?
- Are forbidden names avoided?
- Is there no markdown?
- Is there no explanation outside JSON?

{FINAL_JSON_ONLY_INSTRUCTION}
"""