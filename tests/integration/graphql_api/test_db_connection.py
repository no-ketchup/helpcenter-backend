#!/usr/bin/env python3
"""
Simple script to test database connection with Neon DB
"""
import asyncio
import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

@pytest.mark.asyncio
async def test_connection():
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL_ASYNC')
    if not db_url:
        print("DATABASE_URL_ASYNC not set")
        return False

    print(f"Testing connection to: {db_url[:50]}...")

    try:
        # Create engine with SSL context
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Remove SSL parameters from URL for asyncpg
        if "sslmode=require" in db_url or "channel_binding=require" in db_url:
            url_str = db_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
            url_str = url_str.replace("?channel_binding=require", "").replace("&channel_binding=require", "")
            url_str = url_str.replace("?&", "?").replace("&&", "&")
            if url_str.endswith("?") or url_str.endswith("&"):
                url_str = url_str[:-1]
            db_url = url_str

        engine = create_async_engine(db_url, connect_args={"ssl": ssl_context})

        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"Connection successful! Test query result: {row[0]}")
            return True

    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    finally:
        if 'engine' in locals():
            try:
                await engine.dispose()
            except:
                pass  # Ignore dispose errors

if __name__ == "__main__":
    asyncio.run(test_connection())
