#!/usr/bin/env python3
"""
Demo script showing the help center functionality
"""

import asyncio
import httpx
import json

API_BASE = "http://localhost:8000"
HEADERS = {"x-dev-editor-key": "dev-editor-key", "Content-Type": "application/json"}

async def demo():
    async with httpx.AsyncClient() as client:
        print("Help Center Backend Demo")
        print("=" * 50)
        
        # 1. Test GraphQL - Get all guides with media
        print("\n1. GraphQL Query - Guides with Media:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": "{ guides { id title slug media { id url alt } } }"
        })
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"GraphQL failed: {response.text}")
        
        # 2. Test REST API - List categories
        print("\n2. REST API - Categories:")
        response = await client.get(f"{API_BASE}/dev-editor/categories", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            for cat in data:
                print(f"  • {cat['name']} ({cat['slug']})")
        else:
            print(f"Categories failed: {response.text}")
        
        # 3. Test REST API - List media
        print("\n3. REST API - Media:")
        response = await client.get(f"{API_BASE}/dev-editor/media", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            for media in data:
                print(f"  • {media.get('alt', 'No alt')} - {media['url']}")
        else:
            print(f"Media failed: {response.text}")
        
        # 4. Test specific guide with media
        print("\n4. Specific Guide with Media:")
        response = await client.post(f"{API_BASE}/graphql", json={
            "query": '{ guide(slug: "upload-screenshots") { id title slug media { id url alt } } }'
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("guide"):
                guide = data["data"]["guide"]
                print(f"  Guide: {guide['title']}")
                print(f"  Slug: {guide['slug']}")
                print(f"  Media ({len(guide['media'])} items):")
                for media in guide['media']:
                    print(f"    • {media['alt']} - {media['url']}")
            else:
                print("  No guide found")
        else:
            print(f"Guide query failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(demo())
