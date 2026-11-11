from hashlib import sha256
from app.domain.schemas import ReviewRequest

def test_request_hash_is_stable_for_same_payload():
    first = sha256(ReviewRequest(statement="A financial claim").model_dump_json().encode()).hexdigest()
    second = sha256(ReviewRequest(statement="A financial claim").model_dump_json().encode()).hexdigest()
    assert first == second
