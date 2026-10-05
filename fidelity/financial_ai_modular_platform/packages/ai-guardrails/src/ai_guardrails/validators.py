def reject_prompt_injection(text: str) -> list[str]:
    terms = ("ignore previous instructions", "system prompt", "jailbreak")
    return ["possible prompt injection"] if any(t in text.lower() for t in terms) else []

def reject_empty(text: str) -> list[str]:
    return ["empty input"] if not text.strip() else []
