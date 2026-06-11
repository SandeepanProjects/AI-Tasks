class RAGASAdapter:

    @staticmethod
    def context_relevance(question, context):

        q_words = set(question.lower().split())

        c_words = set(context.lower().split())

        overlap = len(q_words & c_words)

        return overlap / (len(q_words) + 1)


    @staticmethod
    def faithfulness(answer, context):

        a_words = set(answer.lower().split())

        c_words = set(context.lower().split())

        overlap = len(a_words & c_words)

        return overlap / (len(a_words) + 1)