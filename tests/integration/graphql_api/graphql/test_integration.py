import pytest


@pytest.mark.asyncio
async def test_complete_guide_workflow(client, editor_headers):
    """Test the complete workflow: create category, create guide, upload media, attach media"""
    
    # 1. Create a category
    category_payload = {
        "name": "Integration Test Category",
        "description": "Category for integration testing",
        "slug": "integration-test-category"
    }
    category_resp = await client.post("/dev-editor/categories", json=category_payload, headers=editor_headers)
    assert category_resp.status_code == 200
    category_id = category_resp.json()["id"]
    
    # 2. Create a guide in that category
    guide_payload = {
        "title": "Integration Test Guide",
        "slug": "integration-test-guide",
        "body": {
            "blocks": [
                {"type": "heading", "level": 1, "text": "Integration Test"},
                {"type": "paragraph", "text": "This is a comprehensive integration test."},
                {"type": "list", "items": ["Step 1", "Step 2", "Step 3"]}
            ]
        },
        "estimated_read_time": 10,
        "category_ids": [category_id]
    }
    guide_resp = await client.post("/dev-editor/guides", json=guide_payload, headers=editor_headers)
    assert guide_resp.status_code == 200
    guide_id = guide_resp.json()["id"]
    
    # 3. Upload media
    import io
    file_content = b"fake image content for integration test"
    file = io.BytesIO(file_content)
    
    files = {"file": ("integration_test.jpg", file, "image/jpeg")}
    data = {"alt": "Integration test image", "guide_id": guide_id}
    
    media_resp = await client.post("/dev-editor/media/upload", files=files, data=data, headers=editor_headers)
    assert media_resp.status_code == 200
    media_id = media_resp.json()["id"]
    
    # 4. Test GraphQL queries
    # Test categories query
    categories_query = """
    query {
      categories {
        id
        name
        slug
        description
        guides {
          id
          title
          slug
        }
      }
    }
    """
    categories_resp = await client.post("/graphql", json={"query": categories_query})
    assert categories_resp.status_code == 200
    categories_data = categories_resp.json()
    assert "data" in categories_data
    assert "categories" in categories_data["data"]
    
    # Find our test category
    test_category = None
    for cat in categories_data["data"]["categories"]:
        if cat["slug"] == "integration-test-category":
            test_category = cat
            break
    assert test_category is not None
    assert test_category["name"] == "Integration Test Category"
    assert len(test_category["guides"]) >= 1
    
    # Test guides query
    guides_query = """
    query {
      guides {
        id
        title
        slug
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
    guides_resp = await client.post("/graphql", json={"query": guides_query})
    assert guides_resp.status_code == 200
    guides_data = guides_resp.json()
    assert "data" in guides_data
    assert "guides" in guides_data["data"]
    
    # Find our test guide
    test_guide = None
    for guide in guides_data["data"]["guides"]:
        if guide["slug"] == "integration-test-guide":
            test_guide = guide
            break
    assert test_guide is not None
    assert test_guide["title"] == "Integration Test Guide"
    assert test_guide["body"]["blocks"][0]["type"] == "heading"
    assert len(test_guide["categories"]) >= 1
    assert len(test_guide["media"]) >= 1
    
    # Test specific guide query
    guide_query = """
    query ($slug: String!) {
      guide(slug: $slug) {
        id
        title
        slug
        body
        categories {
          id
          name
        }
        media {
          id
          url
          alt
        }
      }
    }
    """
    guide_resp = await client.post("/graphql", json={
        "query": guide_query,
        "variables": {"slug": "integration-test-guide"}
    })
    assert guide_resp.status_code == 200
    guide_data = guide_resp.json()
    assert "data" in guide_data
    assert "guide" in guide_data["data"]
    assert guide_data["data"]["guide"]["title"] == "Integration Test Guide"
    
    # Test media query
    media_query = """
    query {
      media {
        id
        url
        alt
        guides {
          id
          title
        }
      }
    }
    """
    media_resp = await client.post("/graphql", json={"query": media_query})
    assert media_resp.status_code == 200
    media_data = media_resp.json()
    assert "data" in media_data
    assert "media" in media_data["data"]
    
    # Find our test media
    test_media = None
    for media in media_data["data"]["media"]:
        if media["alt"] == "Integration test image":
            test_media = media
            break
    assert test_media is not None
    assert len(test_media["guides"]) >= 1


@pytest.mark.asyncio
async def test_graphql_error_handling(client):
    """Test GraphQL error handling for invalid queries"""
    
    # Test invalid query
    invalid_query = """
    query {
      nonExistentField {
        id
      }
    }
    """
    response = await client.post("/graphql", json={"query": invalid_query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data
    assert len(data["errors"]) > 0


@pytest.mark.asyncio
async def test_graphql_variables(client):
    """Test GraphQL queries with variables"""
    
    query = """
    query ($slug: String!) {
      guide(slug: $slug) {
        id
        title
        slug
      }
    }
    """
    variables = {"slug": "non-existent-guide"}
    
    response = await client.post("/graphql", json={
        "query": query,
        "variables": variables
    })
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["guide"] is None  # Should return null for non-existent guide


@pytest.mark.asyncio
async def test_graphql_mutation_feedback(client):
    """Test GraphQL feedback mutation"""
    
    mutation = """
    mutation ($name: String!, $email: String!, $message: String!, $expectReply: Boolean!) {
      submitFeedback(name: $name, email: $email, message: $message, expectReply: $expectReply) {
        id
        name
        email
        message
        expectReply
        createdAt
      }
    }
    """
    variables = {
        "name": "Test User",
        "email": "test@example.com",
        "message": "This is a test feedback message",
        "expectReply": True
    }
    
    response = await client.post("/graphql", json={
        "query": mutation,
        "variables": variables
    })
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "submitFeedback" in data["data"]
    feedback = data["data"]["submitFeedback"]
    assert feedback["name"] == "Test User"
    assert feedback["email"] == "test@example.com"
    assert feedback["message"] == "This is a test feedback message"
    assert feedback["expectReply"] == True
