import numpy as np


class DriftDetector:
    """
    Detects embedding + distribution drift in production.
    """

    def __init__(self, threshold: float = 0.12):
        self.threshold = threshold

    def embedding_drift(self, old: np.ndarray, new: np.ndarray) -> float:
        return float(np.linalg.norm(old.mean(axis=0) - new.mean(axis=0)))

    def distribution_drift(self, old: np.ndarray, new: np.ndarray) -> float:
        old_hist = np.histogram(old, bins=50, density=True)[0]
        new_hist = np.histogram(new, bins=50, density=True)[0]

        return float(np.sum(np.abs(old_hist - new_hist)))

    def is_drift_detected(self, old: np.ndarray, new: np.ndarray) -> bool:
        return self.embedding_drift(old, new) > self.threshold