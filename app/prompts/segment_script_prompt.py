def build_segment_script_prompt(
    title: str,
    story_bible: dict,
    outline: dict,
    full_script: str,
    narrator_name: str = "",
    hook_segment_words: int = 45,
    chapter_segment_words: int = 85,
) -> str:
    return f"""
ROLE:
You are a production script editor for long-form YouTube storytelling.

TASK:
Convert the full repaired script into a segment script in plain .txt format.

IMPORTANT:
- Do not change the story.
- Do not rewrite the prose unless a tiny wording fix is needed to keep the segment natural.
- Preserve existing supported TTS emotion tags from the script when they are already useful.
- Do not remove supported TTS emotion tags such as [sigh], [surprise-oh], [dissatisfaction-hnn], [question-en], [confirmation-en], or [laughter].
- Do not invent new emotion tags.
- Do not add extra emotion tags unless the original line clearly lost an existing emotional cue during segmentation.
- Do not add SFX, music, or image prompts.
- Do not output JSON.
- Keep the original story order exactly.
- Split by scene and emotional beat.
- Each segment must be ready for TTS and later visual production.
- Dialogue must be labeled with the speaker name when possible using bracket labels, for example [Hazel] "Dialogue..."
- The narrator is the main character of the story, so first-person narration should stay logically consistent with that character.
- If narration is first person, keep that voice aligned with the narrator name above.

ORIGINAL TITLE:
{title}

STORY BIBLE:
{story_bible}

OUTLINE:
{outline}

FULL SCRIPT:
{full_script}

NARRATOR NAME:
{narrator_name}

SEGMENT LENGTH RULES:
- Hook segments: aim for {hook_segment_words} words.
- Chapter segments: aim for {chapter_segment_words} words.
- Hook segments should move faster and cut more often.
- Chapters can breathe a little more, but still should not be too long.
- Do not make any segment longer than about 130 words.
- Do not make any segment shorter than about 25 words unless the beat is a very short reveal or a sharp line.
- Cut at a strong beat, dialogue shift, reveal, location shift, or emotional turn.

OUTPUT FORMAT:
Use this exact style:

# Hook

[SEG_001]
Text...

[SEG_002]
Text...

# Chapter 1: Chapter title

[SEG_003]
Chapter 1: Chapter title

[SEG_004]
Text...

[SEG_005]
[Morgan] "I didn't move."

FORMAT RULES:
- Keep headings exactly as chapter sections.
- Keep segment IDs sequential across the whole script.
- Segment IDs must be zero-padded like SEG_001, SEG_002, SEG_003.
- Use the actual chapter titles from the script if available.
- Every chapter title line such as "Chapter 1: The Fallout of Recognition" must become its own separate segment immediately after that chapter heading.
- Chapter title segments should contain only the chapter title text, with no narration and no dialogue.
- Keep supported TTS emotion tags inside the segment text exactly where they help the spoken performance.
- Supported TTS emotion tags are:
  [laughter], [sigh], [confirmation-en], [question-en], [question-ah], [question-oh], [question-ei], [question-yi], [surprise-ah], [surprise-oh], [surprise-wa], [surprise-yo], [dissatisfaction-hnn].
- Remove only unsupported bracket notes, production notes, SFX, music cues, camera cues, and image directions.
- For dialogue, prefix the speaker name inside square brackets, for example:
  [Morgan] "I didn't move."
  [Lawrence] "You think this changes anything?"
- Never use colon speaker labels like Morgan: or Hazel:.
- If the source line is `Hazel: "I found something else..."`, convert it to `[Hazel] "I found something else..."`.
- For narration, keep plain prose.
- Do not use bullet points.
- Do not use markdown outside the required headings and segment ids.
- Do not add commentary.

FINAL ANSWER:
Return only the segment script text.
"""
