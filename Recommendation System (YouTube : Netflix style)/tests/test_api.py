from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api():
    res = client.get("/recommend/user_1")
    assert res.status_code == 200