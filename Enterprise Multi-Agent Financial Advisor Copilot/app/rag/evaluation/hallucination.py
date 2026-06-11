class HallucinationDetector:

    @staticmethod
    def detect(answer: str, context: str):

        answer_sentences = set(
            answer.lower().split(".")
        )

        context_sentences = set(
            context.lower().split(".")
        )

        hallucinated = []

        for sentence in answer_sentences:

            if not any(
                sentence.strip() in c
                for c in context_sentences
            ):

                if len(sentence.strip()) > 20:

                    hallucinated.append(sentence)

        return {
            "hallucinated_statements": hallucinated,
            "risk": "HIGH" if hallucinated else "LOW"
        }