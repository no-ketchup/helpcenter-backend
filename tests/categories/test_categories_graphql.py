import pytest


@pytest.mark.asyncio
async def test_graphql_empty_categories(client):
    query = """
    query {
      categories {
        id
        name
        slug
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]
    print(response.json())
    assert "categories" in data
    assert data["categories"] == []