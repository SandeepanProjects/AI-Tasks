import re

PATTERNS = [

    r"ignore previous instructions",

    r"reveal system prompt",

    r"act as system",

    r"bypass"
]


def detect_prompt_injection(
    text: str
):

    text = text.lower()

    for pattern in PATTERNS:

        if re.search(pattern, text):

            return True

    return False