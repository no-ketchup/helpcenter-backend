import pytest


@pytest.mark.asyncio
async def test_create_category_and_fetch_by_id(client, editor_headers):
    payload = {
        "name": "Docs",
        "description": "Developer docs",
        "slug": "docs"
    }
    # Create
    resp = await client.post("/dev-editor/categories", json=payload, headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Docs"
    assert data["slug"] == "docs"
    category_id = data["id"]

    # Fetch by ID
    resp2 = await client.get(f"/dev-editor/categories/{category_id}", headers=editor_headers)
    assert resp2.status_code == 200
    fetched = resp2.json()
    assert fetched["id"] == category_id
    assert fetched["name"] == "Docs"


@pytest.mark.asyncio
async def test_create_duplicate_slug_conflict(client, editor_headers):
    payload = {
        "name": "Tutorials",
        "description": "Step by step guides",
        "slug": "tutorials"
    }
    # First create succeeds
    resp1 = await client.post("/dev-editor/categories", json=payload, headers=editor_headers)
    assert resp1.status_code == 200

    # Second create should conflict
    resp2 = await client.post("/dev-editor/categories", json=payload, headers=editor_headers)
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == "Slug already exists"


@pytest.mark.asyncio
async def test_list_and_fetch_by_slug(client, editor_headers):
    # Should list at least the two inserted ones
    resp = await client.get("/dev-editor/categories", headers=editor_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert any(c["slug"] == "docs" for c in items)
    assert any(c["slug"] == "tutorials" for c in items)

    # Fetch by slug
    resp2 = await client.get("/dev-editor/categories/slug/docs", headers=editor_headers)
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["slug"] == "docs"