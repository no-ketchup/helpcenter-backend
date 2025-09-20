from fastapi.testclient import TestClient
from app.core.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/graphql")
    assert response.status_code in (200, 405)  # GET may not be allowed, just a basic check