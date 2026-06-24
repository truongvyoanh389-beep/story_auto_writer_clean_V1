# app/prompts/prompt_contracts.py

JSON_OUTPUT_CONTRACT = """
OUTPUT REQUIREMENT:
Return ONLY one valid JSON object.
Do not return markdown.
Do not wrap the answer in code fences.
Do not write explanation before or after the JSON.
Do not add notes.
Do not add commentary.
Do not add comments.
Do not use trailing commas.

The first character of your response must be {
The last character of your response must be }

VALIDATION RULES:
- The output must be parseable by Python json.loads().
- Return exactly one top-level JSON object.
- Every required field in the schema must be present.
- Do not rename fields.
- Do not omit fields.
- Do not add extra fields not listed in the schema.
- Strings must be plain JSON strings.
- Arrays must be real JSON arrays.
- Numbers must be JSON numbers, not strings.
"""


FINAL_JSON_ONLY_INSTRUCTION = """
FINAL ANSWER:
Return the JSON object now.
No markdown.
No explanation.
No text before JSON.
No text after JSON.
"""


PROSE_ONLY_CONTRACT = """
OUTPUT REQUIREMENT:
Return prose only.
Do not return JSON.
Do not return markdown.
Do not wrap the answer in code fences.
Do not add notes.
Do not add commentary.
Do not explain what you are doing.
Do not include sound effects.
Do not include music cues.
Do not include stage directions.
Do not include production notes.
"""