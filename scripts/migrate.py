#!/usr/bin/env python3
"""
Unified database migration script for all environments.
Handles migrations consistently across development, testing, and production.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_migration(environment: str = "development", database_url: str = None):
    """Run database migrations for the specified environment."""
    
    # Set environment variables
    os.environ["ENVIRONMENT"] = environment
    if database_url:
        os.environ["DATABASE_URL"] = database_url
    
    # Ensure PYTHONPATH is set
    project_root = Path(__file__).parent.parent
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Run alembic migration
    try:
        result = subprocess.run([
            "alembic", 
            "-c", "alembic.ini", 
            "upgrade", "head"
        ], cwd=project_root, check=True, capture_output=True, text=True)
        
        print(f"✅ Migrations completed successfully for {environment}")
        if result.stdout:
            print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed for {environment}")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed.")
        return False

def main():
    """Main entry point for migration script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "--env", 
        choices=["development", "test", "staging", "production"],
        default="development",
        help="Environment to run migrations for"
    )
    parser.add_argument(
        "--database-url",
        help="Database URL (overrides environment variable)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check migration status without running"
    )
    
    args = parser.parse_args()
    
    if args.check:
        # Check migration status
        try:
            result = subprocess.run([
                "alembic", 
                "-c", "alembic.ini", 
                "current"
            ], cwd=Path(__file__).parent.parent, check=True, capture_output=True, text=True)
            print("Current migration status:")
            print(result.stdout)
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Failed to check migration status: {e.stderr}")
            return 1
    
    # Run migrations
    success = run_migration(args.env, args.database_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
