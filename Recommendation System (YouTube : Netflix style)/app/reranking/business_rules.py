from typing import List, Dict


class BusinessRulesEngine:
    """
    Production-safe rule filter for recommendations.
    """

    def __init__(self):
        self.banned_items = set()
        self.geo_blocklist = set()
        self.min_score = 0.0

    def update_banned_items(self, items: List[int]):
        self.banned_items.update(items)

    def apply(self, items: List[Dict], user_region: str = "global") -> List[Dict]:

        filtered = []

        for item in items:
            item_id = item.get("id")

            if item_id in self.banned_items:
                continue

            if user_region in self.geo_blocklist:
                continue

            if item.get("score", 0) < self.min_score:
                continue

            if item.get("is_expired", False):
                continue

            if item.get("nsfw", False):
                continue

            filtered.append(item)

        return filtered