from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_categories():
    query = """
    query {
      categories {
        id
        name
        slug
      }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "categories" in data["data"]