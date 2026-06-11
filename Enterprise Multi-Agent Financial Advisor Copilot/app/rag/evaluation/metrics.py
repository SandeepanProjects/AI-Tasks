import re


class Metrics:

    @staticmethod
    def precision_at_k(retrieved, expected):

        retrieved_ids = [
            r["id"] for r in retrieved
        ]

        relevant = 0

        for doc in retrieved_ids:

            if doc in expected:
                relevant += 1

        return relevant / len(retrieved_ids)


    @staticmethod
    def recall_at_k(retrieved, expected):

        retrieved_ids = [
            r["id"] for r in retrieved
        ]

        relevant = 0

        for doc in expected:

            if doc in retrieved_ids:
                relevant += 1

        return relevant / len(expected)