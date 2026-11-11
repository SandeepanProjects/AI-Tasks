"""Synthetic load test. Configure BASE_URL, BEARER_TOKEN and REVIEW_PATH for staging."""
import os
import uuid
from locust import HttpUser, task, between

class ComplianceReviewUser(HttpUser):
    wait_time = between(1, 3)
    def on_start(self):
        self.token = os.getenv("BEARER_TOKEN", "")
        self.review_path = os.getenv("REVIEW_PATH", "/reviews")
    @task(4)
    def health(self):
        self.client.get("/health", name="GET /health")
    @task(1)
    def create_review(self):
        if not self.token:
            return
        self.client.post(self.review_path,
            json={"statement": "Synthetic test: the investment product has fees and market risk."},
            headers={"Authorization": f"Bearer {self.token}", "Idempotency-Key": str(uuid.uuid4())},
            name="POST /reviews")
