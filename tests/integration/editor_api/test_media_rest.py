import pytest
import io


@pytest.mark.asyncio
async def test_upload_media(editor_client, editor_headers):
    # Create a mock file
    file_content = b"fake image content"
    file = io.BytesIO(file_content)

    files = {"file": ("test_image.jpg", file, "image/jpeg")}
    data = {"alt": "Test image description"}

    resp = await editor_client.post("/dev-editor/media/upload", files=files, data=data, headers=editor_headers)
    assert resp.status_code == 200
    response_data = resp.json()
    assert "id" in response_data
    assert "url" in response_data
    assert "alt" in response_data
    assert response_data["alt"] == "Test image description"
    return response_data["id"]


@pytest.mark.asyncio
async def test_upload_media_with_guide_id(editor_client, editor_headers):
    import uuid
    # First create a guide
    unique_slug = f"media-test-guide-{uuid.uuid4().hex[:8]}"
    guide_payload = {
        "title": "Media Test Guide",
        "slug": unique_slug,
        "body": {"blocks": [{"type": "paragraph", "text": "Test content"}]},
        "estimated_read_time": 3,
        "category_ids": []
    }
    guide_resp = await editor_client.post("/dev-editor/guides", json=guide_payload, headers=editor_headers)
    assert guide_resp.status_code == 200
    guide_id = guide_resp.json()["id"]

    # Upload media with guide_id
    file_content = b"fake image content"
    file = io.BytesIO(file_content)

    files = {"file": ("test_image2.jpg", file, "image/jpeg")}
    data = {"alt": "Test image for guide", "guide_id": guide_id}

    resp = await editor_client.post("/dev-editor/media/upload", files=files, data=data, headers=editor_headers)
    assert resp.status_code == 200
    response_data = resp.json()
    assert "id" in response_data
    assert "url" in response_data
    return response_data["id"]


@pytest.mark.asyncio
async def test_list_media(editor_client, editor_headers):
    resp = await editor_client.get("/dev-editor/media", headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    for media in data:
        assert "id" in media
        assert "url" in media
        assert "alt" in media
        assert "createdAt" in media


@pytest.mark.asyncio
async def test_get_media_by_id(editor_client, editor_headers):
    # First upload a media
    media_id = await test_upload_media(editor_client, editor_headers)

    # Get media by ID
    resp = await editor_client.get(f"/dev-editor/media/{media_id}", headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == media_id
    assert "url" in data
    assert "alt" in data


@pytest.mark.asyncio
async def test_attach_media_to_guide(editor_client, editor_headers):
    # Create a guide
    guide_payload = {
        "title": "Attachment Test Guide",
        "slug": "attachment-test-guide",
        "body": {"blocks": [{"type": "paragraph", "text": "Test content"}]},
        "estimated_read_time": 2,
        "category_ids": []
    }
    guide_resp = await editor_client.post("/dev-editor/guides", json=guide_payload, headers=editor_headers)
    assert guide_resp.status_code == 200
    guide_id = guide_resp.json()["id"]

    # Upload media
    media_id = await test_upload_media(editor_client, editor_headers)

    # Attach media to guide
    resp = await editor_client.post(f"/dev-editor/guides/{guide_id}/media/{media_id}", headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_get_guide_media(editor_client, editor_headers):
    import uuid
    # Create a guide
    unique_slug = f"guide-media-test-{uuid.uuid4().hex[:8]}"
    guide_payload = {
        "title": "Guide Media Test",
        "slug": unique_slug,
        "body": {"blocks": [{"type": "paragraph", "text": "Test content"}]},
        "estimated_read_time": 2,
        "category_ids": []
    }
    guide_resp = await editor_client.post("/dev-editor/guides", json=guide_payload, headers=editor_headers)
    assert guide_resp.status_code == 200
    guide_id = guide_resp.json()["id"]

    # Upload media directly to this guide
    file_content = b"fake image content for guide media test"
    file = io.BytesIO(file_content)

    files = {"file": ("guide_media_test.jpg", file, "image/jpeg")}
    data = {"alt": "Guide media test image", "guide_id": guide_id}

    media_resp = await editor_client.post("/dev-editor/media/upload", files=files, data=data, headers=editor_headers)
    assert media_resp.status_code == 200
    media_id = media_resp.json()["id"]

    # Get media for guide
    resp = await editor_client.get(f"/dev-editor/guides/{guide_id}/media", headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Should have at least the attached media


@pytest.mark.asyncio
async def test_detach_media_from_guide(editor_client, editor_headers):
    # Create a guide
    guide_payload = {
        "title": "Detach Test Guide",
        "slug": "detach-test-guide",
        "body": {"blocks": [{"type": "paragraph", "text": "Test content"}]},
        "estimated_read_time": 2,
        "category_ids": []
    }
    guide_resp = await editor_client.post("/dev-editor/guides", json=guide_payload, headers=editor_headers)
    assert guide_resp.status_code == 200
    guide_id = guide_resp.json()["id"]

    # Upload and attach media
    media_id = await test_upload_media_with_guide_id(editor_client, editor_headers)

    # Detach media from guide
    resp = await editor_client.delete(f"/dev-editor/guides/{guide_id}/media/{media_id}", headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_delete_media(editor_client, editor_headers):
    # Upload media
    media_id = await test_upload_media(editor_client, editor_headers)

    # Delete media
    resp = await editor_client.delete(f"/dev-editor/media/{media_id}", headers=editor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data

    # Verify it's deleted
    resp2 = await editor_client.get(f"/dev-editor/media/{media_id}", headers=editor_headers)
    assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_upload_invalid_file_type(editor_client, editor_headers):
    # Try to upload a non-image file
    file_content = b"not an image"
    file = io.BytesIO(file_content)

    files = {"file": ("test.txt", file, "text/plain")}
    data = {"alt": "Invalid file"}

    resp = await editor_client.post("/dev-editor/media/upload", files=files, data=data, headers=editor_headers)
    assert resp.status_code == 400
    assert "Only image and video files are allowed" in resp.json()["detail"]
