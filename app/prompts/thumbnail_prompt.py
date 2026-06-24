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
Follow the fixed high-CTR revenge-story template below.
The template controls the layout and emotional logic only. The thumbnail copy must be freshly written from the actual story.
Do not force generic wording like "THEY CALLED ME POOR" unless the story truly contains that insult.

FIXED THUMBNAIL TEMPLATE:
A high-contrast, cinematic YouTube thumbnail designed to generate extremely high CTR, featuring a dramatic mini-story layout.
The left two-thirds of the image contains bold, easy-to-read sans-serif typography in a mix of white and striking red text.
Across the bottom, a prominent highlight text in large, bold yellow with a black stroke exclaims the story payoff.
The right third of the thumbnail features a powerful, close-up portrait of the main character, captured from the head and shoulders only.
The main character must look elegant, calm, composed, and emotionally tense: slightly hurt yet undeniably confident.
The setting should be a blurred story-relevant background, such as a high-luxury family dinner, wedding, ceremony, courtroom, Pentagon, Navy, military office, or other authority setting when the story supports it.
Use warm cinematic lighting, deep soft bokeh, strong contrast, clean viral storytelling composition, and a clear focus on the main character's expression.

TEXT FORMULA:
Use this structure as a copywriting framework, not as fixed words.
Write short, punchy, story-specific lines that tightly connect to the actual humiliation, setting, secret leverage, and payoff.
Line 1: social setting or trigger event from the story.
Line 2: the most painful insult, accusation, dismissal, or betrayal from the story.
Line 3: the visible humiliation, exclusion, mockery, or threat.
Line 4: the protagonist's restraint, silence, or controlled response.
Bottom highlight: the strongest authority / secret / evidence / payoff reveal from the story.

COPY QUALITY RULES:
- Every line must be specific to THIS story, not generic revenge-story filler.
- Use concrete nouns from the script: relationship, rank, place, object, document, money amount, code phrase, military unit, courtroom, dinner, wedding, office, etc.
- The bottom highlight must connect directly to the final reveal/payoff.
- Keep each line short enough to fit a thumbnail, but make it emotionally explosive.
- Prefer 3 to 7 words per line when possible.
- Do not invent a jet, Navy rank, Pentagon, wedding, courtroom, or money amount unless present or clearly supported by the story.
- Do not copy the example text unless it genuinely matches the story.

EXAMPLE ONLY - DO NOT COPY UNLESS IT MATCHES THE STORY:
"AT FAMILY DINNER"
"THEY CALLED ME POOR"
"LAUGHED AT ME"
"I STAYED SILENT"
Bottom highlight:
"UNTIL HE ASKED ABOUT THE JET"

DESIGN RULES:
1. Canvas: 16:9 YouTube thumbnail.
2. Layout:
   - Left two-thirds: dramatic multi-line text block.
   - Right one-third: named main character portrait, head and shoulders only.
   - Bottom: large yellow payoff highlight text with black stroke.
3. Typography:
   - Bold sans-serif, all caps, extremely readable at mobile size.
   - Mix white and striking red text in the left block.
   - Bottom highlight must be bold yellow with black stroke.
4. Character:
   - The portrait subject MUST be the main character by name from the story.
   - If the story bible has a protagonist/main character name, use that exact name in VISUAL_PROMPT.
   - If multiple names appear, choose the protagonist or narrator.
   - Expression: calm, composed, wounded but confident.
5. SEO:
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
Line 1: [story-specific setting/trigger]
Line 2: [story-specific insult or accusation]
Line 3: [story-specific public humiliation]
Line 4: [story-specific silent/control beat]
Bottom highlight: [story-specific reveal/payoff]

VISUAL_PROMPT:
[A single detailed prompt for image generation / designer execution. Must follow the fixed thumbnail template and name the main character explicitly as the portrait subject.]

LAYOUT_NOTES:
- left two-thirds text placement note
- right one-third portrait note
- bottom highlight note

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
