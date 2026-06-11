class Guardrails:

    banned_keywords = [
        "guaranteed profit",
        "risk-free",
        "100% return",
        "no risk"
    ]

    @staticmethod
    def validate(text: str):

        lower = text.lower()

        violations = []

        for word in Guardrails.banned_keywords:

            if word in lower:

                violations.append(
                    f"Banned phrase detected: {word}"
                )

        return violations