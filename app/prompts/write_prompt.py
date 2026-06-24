# app/prompts/write_prompt.py

from app.prompts.prompt_contracts import PROSE_ONLY_CONTRACT


TTS_CONTROL_RULES = """
NON-VERBAL & PRONUNCIATION CONTROL:
You may use supported TTS control tags sparingly to make narration sound more natural and human.

Supported tags:
[laughter], [sigh], [confirmation-en], [question-en], [question-ah], [question-oh], [question-ei], [question-yi], [surprise-ah], [surprise-oh], [surprise-wa], [surprise-yo], [dissatisfaction-hnn].

Rules:
- Use only the supported tags listed above.
- Do not invent new tags.
- Use tags sparingly, only where they improve human-like delivery.
- Do not place tags in chapter headings.
- Do not use tags in every paragraph.
- Target 0 to 3 tags per 1,000 words.
- Prefer tags in dialogue, emotional hesitation, surprise, dissatisfaction, short confirmation, or rhetorical questions.
- Do not overperform.
- Do not make the narration sound like a cartoon.
- Keep the prose clean and readable for TTS.
"""


def build_hook_prompt(
    title: str = "",
    selected_premise: dict | None = None,
    story_bible: dict | None = None,
    outline: dict | None = None,
    target_audience: str = "American adults aged 45+",
    tone: str = "grounded emotional drama",
    niche: str = "Family Betrayal",
    narration_pov: str = "first person",
) -> str:
    if selected_premise is None:
        selected_premise = {}

    if story_bible is None:
        story_bible = {}

    if outline is None:
        outline = {}

    if not title:
        title = story_bible.get("original_user_title", "") or story_bible.get("story_title", "")

    return f"""
ROLE:
You are a professional American viral story hook writer for long-form YouTube text-to-speech drama.

TASK:
Write the opening Hook only.

The Hook does not need to be long.
A short strong Hook is better than a long weak Hook.
The goal is viewer retention.

ORIGINAL USER TITLE:
{title}

SELECTED PREMISE:
{selected_premise}

STORY BIBLE:
{story_bible}

OUTLINE:
{outline}

NARRATION POV:
{narration_pov}

TARGET AUDIENCE:
{target_audience}

TONE:
{tone}

NICHE:
{niche}

{PROSE_ONLY_CONTRACT}

ORIGINAL TITLE LOCK:
The final script title remains exactly:
{title}

Do not replace it with the selected premise title.
Do not invent a new title.

HOOK LAW:
- Do not write "Hook:".
- Do not add a title.
- Do not use markdown.
- Do not write chapter text.
- Do not write Chapter 1.
- Start with immediate tension, betrayal, humiliation, money loss, danger, mystery, or a shocking contradiction.
- The first sentence must make the viewer want to keep listening.
- Create one major unanswered question.
- Do not resolve the situation.
- Keep it grounded and realistic.
- Keep it emotionally sharp.
- Make it suitable for American adults aged 45+.
- Do not claim the story is true.
- Do not use sound effects, music cues, or stage directions.
- Target length: 120 to 220 words.

RETENTION STYLE:
- Begin close to the most emotionally charged moment.
- Make the listener wonder how the narrator will respond.
- Suggest betrayal, disrespect, hidden truth, or public humiliation quickly.
- End with a clean unresolved turn that leads naturally into Chapter 1.

{TTS_CONTROL_RULES}

HOOK VOICE RULE:
- The Hook may include 1 or 2 supported TTS control tags if they make the opening more human.
- Do not force tags if the Hook is stronger without them.

FINAL ANSWER:
Return only the Hook prose.
"""


def build_chapter_prompt(
    title: str = "",
    chapter_number: int = 1,
    chapter_title: str = "",
    story_bible: dict | None = None,
    outline: dict | None = None,
    previous_text: str = "",
    target_words: int = 900,
    total_target_words: int = 10000,
    chapter_count: int = 10,
    narration_pov: str = "first person",
    target_audience: str = "American adults aged 45+",
    tone: str = "grounded emotional drama",
    niche: str = "Family Betrayal",
) -> str:
    if story_bible is None:
        story_bible = {}

    if outline is None:
        outline = {}

    if not title:
        title = story_bible.get("original_user_title", "") or story_bible.get("story_title", "")

    if not chapter_title:
        chapter_title = f"Chapter {chapter_number}"

    chapter_1_rule = ""

    if int(chapter_number) == 1:
        chapter_1_rule = """
CHAPTER 1 ANTI-REPETITION LAW:
- Chapter 1 must not repeat the Hook.
- Assume the listener already heard the Hook.
- Continue after the Hook's final emotional beat.
- Do not reuse the same opening paragraph, same first image, same reveal structure, or same emotional sentence pattern from the Hook.
- Add new action, new information, new consequence, or new context immediately.
- Do not summarize the Hook.
"""

    return f"""
ROLE:
You are a professional American long-form story chapter writer for YouTube text-to-speech narration.

TASK:
Write Chapter {chapter_number} only.

You are writing polished story prose, not an outline.
You must follow the Story Bible and Outline.
You must keep continuity with previous text.

ORIGINAL USER TITLE:
{title}

CHAPTER NUMBER:
{chapter_number}

CHAPTER TITLE:
{chapter_title}

STORY BIBLE:
{story_bible}

OUTLINE:
{outline}

PREVIOUS TEXT / CONTINUITY CONTEXT:
{previous_text}

TARGET WORDS FOR THIS CHAPTER:
{target_words}

TOTAL SCRIPT WORD BUDGET:
{total_target_words}

TOTAL CHAPTER COUNT:
{chapter_count}

NARRATION POV:
{narration_pov}

TARGET AUDIENCE:
{target_audience}

TONE:
{tone}

NICHE:
{niche}

{PROSE_ONLY_CONTRACT}

ORIGINAL TITLE LOCK:
The final script title remains exactly:
{title}

Do not replace it with the selected premise title.
Do not invent a new title.

OUTPUT FORMAT:
Start exactly with:
Chapter {chapter_number}: {chapter_title}

Then write one blank line.
Then write the chapter prose.

CHAPTER RULES:
- Write in English.
- Write only Chapter {chapter_number}.
- Do not write other chapters.
- Respect the chapter length target. Aim for {target_words} words.
- Acceptable range: about {int(target_words * 0.85)} to {int(target_words * 1.15)} words.
- Hard cap: do not exceed {int(target_words * 1.25)} words for this chapter.
- The full script budget is {total_target_words} words across Hook plus {chapter_count} chapters, so do not expand beyond this chapter's assigned size.
- Do not write JSON.
- Do not write markdown.
- Do not add notes.
- Do not add analysis.
- Do not add sound effects.
- Do not add music cues.
- Do not add stage directions.
- Do not use headings other than the required chapter heading.
- Keep the story grounded and realistic.
- Preserve character names and continuity from the Story Bible.
- Maintain the requested narration POV.
- Make the chapter emotionally clear and easy to follow for TTS.
- Use vivid but clean prose.
- Avoid purple prose.
- Avoid repeating the same sentence pattern.
- Avoid repeating the protagonist's name too often.
- Avoid moralizing too early.
- End with a retention beat that naturally leads to the next chapter.

{chapter_1_rule}

DIALOGUE RULES:
- Dialogue is allowed when it moves the scene forward.
- Keep dialogue natural for American adults.
- Do not overuse dialogue.
- Do not let dialogue become theatrical or unrealistic.
- Keep quoted dialogue intact inside a paragraph.
- Do not split one long spoken line into disconnected fragments.

{TTS_CONTROL_RULES}

DIALOGUE DELIVERY RULE:
- When a character sighs, reacts with surprise, asks a sharp question, or expresses dissatisfaction, you may add one supported TTS tag before the line.
- Example style only:
[sigh] I should have seen it coming.
[question-oh]? Did they really think I would stay silent?
[dissatisfaction-hnn], I was done pretending this was normal.
- Do not use tags in every dialogue line.
- Do not add more than 0 to 3 tags per 1,000 words.

RETENTION RULES:
- Every 250 to 400 words, add a new emotional turn, discovery, consequence, or escalation.
- Do not let the chapter stall.
- Do not repeat information the viewer already knows unless it gains new meaning.
- End with an unresolved emotional or practical consequence.

FINAL ANSWER:
Return only the required chapter heading and chapter prose.
"""
