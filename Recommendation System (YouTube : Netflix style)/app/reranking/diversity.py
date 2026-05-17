class DiversityReranker:

    def rerank(self, items):

        seen = set()
        results = []

        for item in items:

            category = item % 5

            if category not in seen:
                results.append(item)
                seen.add(category)

        return results