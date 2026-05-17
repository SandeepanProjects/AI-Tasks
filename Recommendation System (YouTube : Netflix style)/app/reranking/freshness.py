import random


class FreshnessReranker:

    def rerank(self, items):

        random.shuffle(items)

        return items