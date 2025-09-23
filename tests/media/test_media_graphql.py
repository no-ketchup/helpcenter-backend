import pytest


@pytest.mark.asyncio
async def test_graphql_media_query(client):
    query = """
    query {
      media {
        id
        url
        alt
        createdAt
        updatedAt
        guides {
          id
          title
          slug
        }
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "media" in data["data"]
    assert isinstance(data["data"]["media"], list)
    
    # Check structure of media items
    for media in data["data"]["media"]:
        assert "id" in media
        assert "url" in media
        assert "alt" in media
        assert "createdAt" in media
        assert "updatedAt" in media
        assert "guides" in media
        assert isinstance(media["guides"], list)


@pytest.mark.asyncio
async def test_graphql_media_urls_are_valid(client):
    query = """
    query {
      media {
        id
        url
        alt
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    
    for media in data["data"]["media"]:
        url = media["url"]
        assert url.startswith("http")
        # Should be either placeholder URL or GCS URL
        assert "placeholder.com" in url or "storage.googleapis.com" in url


@pytest.mark.asyncio
async def test_graphql_media_with_guides(client):
    query = """
    query {
      media {
        id
        url
        alt
        guides {
          id
          title
          slug
          estimatedReadTime
        }
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    
    for media in data["data"]["media"]:
        assert "guides" in media
        assert isinstance(media["guides"], list)
        for guide in media["guides"]:
            assert "id" in guide
            assert "title" in guide
            assert "slug" in guide
            assert "estimatedReadTime" in guide
