import pytest


@pytest.mark.asyncio
async def test_create_guide_and_fetch_by_id(client, editor_headers):
    import uuid
    unique_slug = f"getting-started-guide-{uuid.uuid4().hex[:8]}"
    payload = {
        "title": "Getting Started Guide",
        "slug": unique_slug,
        "body": {
            "blocks": [
                {"type": "heading", "level": 1, "text": "Welcome"},
                {"type": "paragraph", "text": "This is a test guide."}
            ]
        },
        "estimated_read_time": 5,
        "category_ids": []
    }
    # Create
    resp = await client.post("/dev-editor/guides", json=payload, headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Getting Started Guide"
    assert data["slug"] == unique_slug
    assert data["estimated_read_time"] == 5
    assert data["body"]["blocks"][0]["type"] == "heading"
    guide_id = data["id"]

    # Fetch by ID
    resp2 = await client.get(f"/dev-editor/guides/{guide_id}", headers=editor_headers)
    assert resp2.status_code == 200
    fetched = resp2.json()
    assert fetched["id"] == guide_id
    assert fetched["title"] == "Getting Started Guide"


@pytest.mark.asyncio
async def test_create_duplicate_slug_conflict(client, editor_headers):
    import uuid
    unique_slug = f"test-guide-{uuid.uuid4().hex[:8]}"
    payload = {
        "title": "Test Guide",
        "slug": unique_slug,
        "body": {"blocks": [{"type": "paragraph", "text": "Test content"}]},
        "estimated_read_time": 3,
        "category_ids": []
    }
    # First create succeeds
    resp1 = await client.post("/dev-editor/guides", json=payload, headers=editor_headers)
    assert resp1.status_code == 200

    # Second create should conflict
    resp2 = await client.post("/dev-editor/guides", json=payload, headers=editor_headers)
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == "Slug already exists"


@pytest.mark.asyncio
async def test_list_and_fetch_by_slug(client, editor_headers):
    import uuid
    # Create a guide with unique slug
    unique_slug = f"list-test-guide-{uuid.uuid4().hex[:8]}"
    create_payload = {
        "title": "List Test Guide",
        "slug": unique_slug,
        "body": {"blocks": [{"type": "paragraph", "text": "Test content"}]},
        "estimated_read_time": 3,
        "category_ids": []
    }
    resp = await client.post("/dev-editor/guides", json=create_payload, headers=editor_headers)
    assert resp.status_code == 200
    
    # Should list the created guide
    resp = await client.get("/dev-editor/guides", headers=editor_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert any(g["slug"] == unique_slug for g in items)

    # Fetch by slug
    resp2 = await client.get(f"/dev-editor/guides/slug/{unique_slug}", headers=editor_headers)
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["slug"] == unique_slug


@pytest.mark.asyncio
async def test_update_guide(client, editor_headers):
    import uuid
    # First create a guide
    unique_slug = f"update-test-guide-{uuid.uuid4().hex[:8]}"
    create_payload = {
        "title": "Original Title",
        "slug": unique_slug,
        "body": {"blocks": [{"type": "paragraph", "text": "Original content"}]},
        "estimated_read_time": 2,
        "category_ids": []
    }
    resp = await client.post("/dev-editor/guides", json=create_payload, headers=editor_headers)
    assert resp.status_code == 200
    guide_id = resp.json()["id"]

    # Update the guide
    update_payload = {
        "title": "Updated Title",
        "body": {"blocks": [{"type": "paragraph", "text": "Updated content"}]},
        "estimated_read_time": 4
    }
    resp2 = await client.put(f"/dev-editor/guides/{guide_id}", json=update_payload, headers=editor_headers)
    assert resp2.status_code == 200
    updated = resp2.json()
    assert updated["title"] == "Updated Title"
    assert updated["estimated_read_time"] == 4
    assert updated["body"]["blocks"][0]["text"] == "Updated content"


@pytest.mark.asyncio
async def test_delete_guide(client, editor_headers):
    import uuid
    # Create a guide to delete with unique slug
    unique_slug = f"delete-test-guide-{uuid.uuid4().hex[:8]}"
    payload = {
        "title": "Guide to Delete",
        "slug": unique_slug,
        "body": {"blocks": [{"type": "paragraph", "text": "This will be deleted"}]},
        "estimated_read_time": 1,
        "category_ids": []
    }
    resp = await client.post("/dev-editor/guides", json=payload, headers=editor_headers)
    assert resp.status_code == 200
    guide_id = resp.json()["id"]

    # Delete the guide
    resp2 = await client.delete(f"/dev-editor/guides/{guide_id}", headers=editor_headers)
    assert resp2.status_code == 200

    # Verify it's deleted
    resp3 = await client.get(f"/dev-editor/guides/{guide_id}", headers=editor_headers)
    assert resp3.status_code == 404
