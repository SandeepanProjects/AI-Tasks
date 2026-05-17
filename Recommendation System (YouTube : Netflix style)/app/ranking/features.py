import numpy as np


def build_features(user_id, candidate_ids):

    features = []

    for item_id in candidate_ids:

        feature_vector = np.random.rand(20)

        features.append(feature_vector)

    return np.array(features)