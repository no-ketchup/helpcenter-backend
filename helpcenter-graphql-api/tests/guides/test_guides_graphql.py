import pytest


@pytest.mark.asyncio
async def test_graphql_guides_query(client):
    query = """
    query {
      guides {
        id
        title
        slug
        estimatedReadTime
        createdAt
        updatedAt
        body
        categories {
          id
          name
          slug
        }
        media {
          id
          url
          alt
        }
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "guides" in data["data"]
    assert isinstance(data["data"]["guides"], list)


@pytest.mark.asyncio
async def test_graphql_guide_by_slug_query(client):
    query = """
    query ($slug: String!) {
      guide(slug: $slug) {
        id
        title
        slug
        body
        estimatedReadTime
        createdAt
        updatedAt
        categories {
          id
          name
          slug
          description
        }
        media {
          id
          url
          alt
          createdAt
          updatedAt
        }
      }
    }
    """
    variables = {"slug": "getting-started-guide"}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "guide" in data["data"]
    if data["data"]["guide"]:  # If guide exists
        guide = data["data"]["guide"]
        assert "id" in guide
        assert "title" in guide
        assert "slug" in guide
        assert "body" in guide
        assert "estimatedReadTime" in guide
        assert "categories" in guide
        assert "media" in guide


@pytest.mark.asyncio
async def test_graphql_guide_body_structure(client):
    query = """
    query ($slug: String!) {
      guide(slug: $slug) {
        body
      }
    }
    """
    variables = {"slug": "getting-started-guide"}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    
    if data["data"]["guide"]:
        body = data["data"]["guide"]["body"]
        assert isinstance(body, dict)
        assert "blocks" in body
        assert isinstance(body["blocks"], list)
        if body["blocks"]:
            block = body["blocks"][0]
            assert "type" in block
            assert "text" in block


@pytest.mark.asyncio
async def test_graphql_guide_with_media(client):
    query = """
    query ($slug: String!) {
      guide(slug: $slug) {
        id
        title
        media {
          id
          url
          alt
          createdAt
        }
      }
    }
    """
    variables = {"slug": "upload-screenshots"}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    
    if data["data"]["guide"]:
        guide = data["data"]["guide"]
        assert "media" in guide
        assert isinstance(guide["media"], list)
        for media in guide["media"]:
            assert "id" in media
            assert "url" in media
            assert "alt" in media
            assert "createdAt" in media
