import joblib
import numpy as np


class Ranker:

    def __init__(self):
        self.model = joblib.load("ranker.pkl")

    def rank(self, features, candidate_ids):

        scores = self.model.predict(features)

        ranked = sorted(
            zip(candidate_ids, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [x[0] for x in ranked]