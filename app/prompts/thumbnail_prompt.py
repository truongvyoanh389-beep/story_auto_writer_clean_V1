def build_thumbnail_prompt_prompt(
    title: str,
    niche: str,
    story_bible: dict,
    outline: dict,
    script_text: str,
) -> str:
    return f"""
ROLE:
You are a YouTube thumbnail strategist for long-form revenge stories.

TASK:
Create a production-ready SEO metadata package and thumbnail prompt for a revenge-story YouTube video.

IMPORTANT:
This niche intentionally uses MANY WORDS on the thumbnail. Do NOT simplify into a minimalist thumbnail.
Follow the fixed competitor-style formula below.

FIXED THUMBNAIL FORMULA:
1. Canvas: 16:9 YouTube thumbnail.
2. Background: dark/black high-contrast background.
3. Layout:
   - Left 60-70%: dense dramatic text block.
   - Right 30-40%: main character portrait, preferably military/navy/authority-coded when relevant.
   - Bottom strip: large red or yellow payoff/punchline bar.
4. Text structure:
   - Top quote: public insult / mockery.
   - Middle: social setting + hidden identity / rank / authority / secret leverage.
   - Bottom punchline: consequence or shock reaction.
5. Color rules:
   - White: narration/context.
   - Neon green: insult quote or humiliating line.
   - Yellow: secret identity, rank, amount, evidence, authority detail.
   - Red: final revenge payoff / face went pale / silence / calls / stood up.
6. Typography:
   - All caps or near all caps.
   - Heavy bold sans-serif.
   - Thick stroke/shadow for readability.
   - Text should fill the left side aggressively.
7. Image:
   - One dominant character on the right.
   - The character image subject MUST be the main character by name from the story.
   - If the story bible has a protagonist/main character name, use that exact name in VISUAL_PROMPT.
   - If multiple names appear, choose the protagonist or narrator.
   - Serious, calm, controlled expression.
   - Military uniform, formal suit, courtroom, Pentagon, Navy, ceremony, or elite authority cues if story supports it.
8. Output must include exact thumbnail text lines.
9. SEO:
   - Write an emotional YouTube SEO description for revenge stories.
   - Include the fixed hashtags exactly:
     #revengestories #familydrama #familybetrayal
   - Create comma-separated video tags.

RETURN FORMAT:
Return ONLY this structure:

SEO_DESCRIPTION:
[SEO optimized Vietnamese or English description matching the story language and YouTube audience]

HASHTAGS:
#revengestories #familydrama #familybetrayal

VIDEO_TAGS:
[comma-separated video tags]

THUMBNAIL_TEXT:
Top quote:
Middle text:
Bottom punchline:

VISUAL_PROMPT:
[A single detailed prompt for image generation / designer execution. Must name the main character explicitly as the portrait subject.]

LAYOUT_NOTES:
- note 1
- note 2
- note 3

NEGATIVE_PROMPT:
[What to avoid]

TITLE:
{title}

NICHE:
{niche}

STORY_BIBLE:
{story_bible}

OUTLINE:
{outline}

SCRIPT:
{script_text}
""".strip()
