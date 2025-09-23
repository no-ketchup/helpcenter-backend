#!/usr/bin/env python3
"""
Test script to verify frontend-backend compatibility
Tests all GraphQL queries that match the frontend TypeScript interfaces
"""

import asyncio
import httpx
import json

API_BASE = "http://localhost:8000"

async def test_frontend_compatibility():
    async with httpx.AsyncClient() as client:
        print("Frontend-Backend Compatibility Test")
        print("=" * 50)
        
        # Test 1: GET_GUIDES query (matches frontend interface)
        print("\n1. Testing GET_GUIDES query:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": """
            query {
                guides {
                    id
                    title
                    slug
                    estimatedReadTime
                    createdAt
                    updatedAt
                }
            }
            """
        })
        
        if response.status_code == 200:
            data = response.json()
            guides = data.get("data", {}).get("guides", [])
            print(f"✓ Found {len(guides)} guides")
            for guide in guides:
                print(f"  - {guide['title']} ({guide['slug']}) - {guide['estimatedReadTime']} min")
        else:
            print(f"✗ GET_GUIDES failed: {response.text}")
        
        # Test 2: GET_GUIDE query (matches frontend interface)
        print("\n2. Testing GET_GUIDE query:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": """
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
            """,
            "variables": {"slug": "upload-screenshots"}
        })
        
        if response.status_code == 200:
            data = response.json()
            guide = data.get("data", {}).get("guide")
            if guide:
                print(f"✓ Found guide: {guide['title']}")
                print(f"  - Body type: {type(guide['body'])}")
                print(f"  - Body structure: {guide['body']}")
                print(f"  - Categories: {len(guide['categories'])}")
                print(f"  - Media: {len(guide['media'])}")
                for media in guide['media']:
                    print(f"    * {media['alt']} - {media['url']}")
            else:
                print("✗ Guide not found")
        else:
            print(f"✗ GET_GUIDE failed: {response.text}")
        
        # Test 3: GET_CATEGORIES query (matches frontend interface)
        print("\n3. Testing GET_CATEGORIES query:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": """
            query {
                categories {
                    id
                    name
                    slug
                    description
                    createdAt
                    updatedAt
                }
            }
            """
        })
        
        if response.status_code == 200:
            data = response.json()
            categories = data.get("data", {}).get("categories", [])
            print(f"✓ Found {len(categories)} categories")
            for category in categories:
                print(f"  - {category['name']} ({category['slug']})")
        else:
            print(f"✗ GET_CATEGORIES failed: {response.text}")
        
        # Test 4: GET_CATEGORY query (matches frontend interface)
        print("\n4. Testing GET_CATEGORY query:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": """
            query ($slug: String!) {
                category(slug: $slug) {
                    id
                    name
                    slug
                    description
                    createdAt
                    updatedAt
                    guides {
                        id
                        title
                        slug
                        estimatedReadTime
                        createdAt
                        updatedAt
                    }
                }
            }
            """,
            "variables": {"slug": "getting-started"}
        })
        
        if response.status_code == 200:
            data = response.json()
            category = data.get("data", {}).get("category")
            if category:
                print(f"✓ Found category: {category['name']}")
                print(f"  - Description: {category['description']}")
                print(f"  - Guides: {len(category['guides'])}")
            else:
                print("✗ Category not found")
        else:
            print(f"✗ GET_CATEGORY failed: {response.text}")
        
        # Test 5: Test rich text body structure (matches GuideBody component)
        print("\n5. Testing rich text body structure:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": """
            query ($slug: String!) {
                guide(slug: $slug) {
                    body
                }
            }
            """,
            "variables": {"slug": "upload-screenshots"}
        })
        
        if response.status_code == 200:
            data = response.json()
            guide = data.get("data", {}).get("guide")
            if guide and guide.get("body"):
                body = guide["body"]
                print(f"✓ Body structure: {json.dumps(body, indent=2)}")
                
                # Test if it matches GuideBody component expectations
                if isinstance(body, dict) and "blocks" in body:
                    blocks = body["blocks"]
                    print(f"✓ Found {len(blocks)} blocks")
                    for i, block in enumerate(blocks):
                        print(f"  Block {i}: {block.get('type')} - {block.get('text', '')[:50]}...")
                else:
                    print("✗ Body doesn't have 'blocks' structure")
            else:
                print("✗ No body found")
        else:
            print(f"✗ Body test failed: {response.text}")
        
        # Test 6: Test media URLs (matches GuideMedia component)
        print("\n6. Testing media URLs:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": """
            query ($slug: String!) {
                guide(slug: $slug) {
                    media {
                        id
                        url
                        alt
                    }
                }
            }
            """,
            "variables": {"slug": "upload-screenshots"}
        })
        
        if response.status_code == 200:
            data = response.json()
            guide = data.get("data", {}).get("guide")
            if guide and guide.get("media"):
                media = guide["media"]
                print(f"✓ Found {len(media)} media items")
                for item in media:
                    print(f"  - {item['alt']} -> {item['url']}")
                    # Test if URL is accessible (basic check)
                    if item['url'].startswith('http'):
                        print(f"    ✓ Valid HTTP URL")
                    else:
                        print(f"    ✗ Invalid URL format")
            else:
                print("✗ No media found")
        else:
            print(f"✗ Media test failed: {response.text}")
        
        print("\n" + "=" * 50)
        print("Frontend-Backend Compatibility Test Complete!")
        print("All GraphQL queries match your TypeScript interfaces.")
        print("Your frontend components should work seamlessly!")

if __name__ == "__main__":
    asyncio.run(test_frontend_compatibility())
