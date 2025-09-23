#!/usr/bin/env python3
"""
Minimal Help Center Editor CLI
A simple terminal-based editor for managing guides, categories, and media.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint

# Configuration
API_BASE = "http://localhost:8000"
HEADERS = {"x-dev-editor-key": "dev-editor-key", "Content-Type": "application/json"}

console = Console()

class HelpCenterEditor:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE, headers=HEADERS)
    
    async def close(self):
        await self.client.aclose()
    
    def check_exit(self, input_text: str) -> bool:
        """Check if user wants to exit from any input."""
        return input_text.lower().strip() in ['q', 'quit', 'exit', 'bye']
    
    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make API request and handle errors."""
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error {e.response.status_code}: {e.response.text}[/red]")
            return {}
        except Exception as e:
            console.print(f"[red]Request failed: {e}[/red]")
            return {}
    
    async def list_categories(self):
        """List all categories."""
        data = await self.request("GET", "/dev-editor/categories")
        if not data:
            return
        
        table = Table(title="Categories")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Slug", style="yellow")
        table.add_column("Description", style="white")
        
        for cat in data:
            table.add_row(
                str(cat["id"])[:8] + "...",
                cat["name"],
                cat["slug"],
                cat.get("description", "")[:50] + "..." if len(cat.get("description", "")) > 50 else cat.get("description", "")
            )
        
        console.print(table)
    
    async def create_category(self):
        """Create a new category."""
        name = Prompt.ask("Category name (or 'q' to quit)")
        if self.check_exit(name):
            return
        
        slug = Prompt.ask("Slug", default=name.lower().replace(" ", "-"))
        if self.check_exit(slug):
            return
            
        description = Prompt.ask("Description", default="")
        if self.check_exit(description):
            return
        
        data = {
            "name": name,
            "slug": slug,
            "description": description
        }
        
        result = await self.request("POST", "/dev-editor/categories", json=data)
        if result:
            console.print(f"[green]Created category: {result['name']}[/green]")
    
    async def list_guides(self):
        """List all guides."""
        data = await self.request("GET", "/dev-editor/guides")
        if not data:
            return
        
        table = Table(title="Guides")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Slug", style="yellow")
        table.add_column("Read Time", style="blue")
        
        for guide in data:
            table.add_row(
                str(guide["id"])[:8] + "...",
                guide["title"],
                guide["slug"],
                f"{guide['estimated_read_time']} min"
            )
        
        console.print(table)
    
    async def create_guide(self):
        """Create a new guide."""
        title = Prompt.ask("Guide title (or 'q' to quit)")
        if self.check_exit(title):
            return None
            
        slug = Prompt.ask("Slug", default=title.lower().replace(" ", "-"))
        if self.check_exit(slug):
            return None
            
        read_time_input = Prompt.ask("Estimated read time (minutes)", default="5")
        if self.check_exit(read_time_input):
            return None
            
        try:
            read_time = int(read_time_input)
        except ValueError:
            read_time = 5
        
        # Simple body editor
        console.print("\n[bold]Guide Body (JSON format)[/bold]")
        console.print("Example: {\"blocks\": [{\"type\": \"heading\", \"level\": 1, \"text\": \"Title\"}, {\"type\": \"paragraph\", \"text\": \"Content\"}]}")
        
        body_input = Prompt.ask("Body JSON (or 'q' to quit)", default='{"blocks": [{"type": "heading", "level": 1, "text": "' + title + '"}, {"type": "paragraph", "text": "Content goes here..."}]}')
        if self.check_exit(body_input):
            return None
        
        try:
            body = json.loads(body_input)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON, using default body[/red]")
            body = {"blocks": [{"type": "heading", "level": 1, "text": title}, {"type": "paragraph", "text": "Content goes here..."}]}
        
        data = {
            "title": title,
            "slug": slug,
            "body": body,
            "estimated_read_time": read_time,
            "categoryIds": []
        }
        
        result = await self.request("POST", "/dev-editor/guides", json=data)
        if result:
            console.print(f"[green]Created guide: {result['title']}[/green]")
            return result["id"]
        return None
    
    async def upload_media(self, guide_id: Optional[str] = None):
        """Upload media file."""
        file_path = Prompt.ask("File path")
        
        if not Path(file_path).exists():
            console.print("[red]File not found[/red]")
            return
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"alt": Path(file_path).stem}
            if guide_id:
                data["guide_id"] = guide_id
            
            # Use different client for file upload
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE}/dev-editor/media/upload",
                    headers={"x-dev-editor-key": "dev-editor-key"},
                    files=files,
                    data=data
                )
        
        if response.status_code == 200:
            result = response.json()
            console.print(f"[green]Uploaded media: {result['url']}[/green]")
            return result["id"]
        else:
            console.print(f"[red]Upload failed: {response.text}[/red]")
            return None
    
    async def attach_media_to_guide(self):
        """Attach media to guide."""
        guide_id = Prompt.ask("Guide ID")
        media_id = Prompt.ask("Media ID")
        
        result = await self.request("POST", f"/dev-editor/guides/{guide_id}/media/{media_id}")
        if result:
            console.print("[green]Media attached to guide[/green]")
    
    async def list_media(self):
        """List all media."""
        data = await self.request("GET", "/dev-editor/media")
        if not data:
            return
        
        table = Table(title="Media")
        table.add_column("ID", style="cyan")
        table.add_column("Alt", style="green")
        table.add_column("URL", style="yellow")
        
        for media in data:
            table.add_row(
                str(media["id"])[:8] + "...",
                media.get("alt", ""),
                media["url"][:50] + "..." if len(media["url"]) > 50 else media["url"]
            )
        
        console.print(table)
    
    async def test_graphql(self):
        """Test GraphQL queries."""
        queries = {
            "1": "{ categories { id name slug guides { id title } } }",
            "2": "{ guides { id title slug media { id url alt } } }",
            "3": "{ media { id url alt } }"
        }
        
        console.print("\n[bold]Available GraphQL queries:[/bold]")
        for key, query in queries.items():
            console.print(f"{key}. {query}")
        
        choice = Prompt.ask("Choose query", choices=list(queries.keys()))
        query = queries[choice]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/graphql",
                json={"query": query}
            )
        
        if response.status_code == 200:
            result = response.json()
            console.print(Panel(json.dumps(result, indent=2), title="GraphQL Response"))
        else:
            console.print(f"[red]GraphQL failed: {response.text}[/red]")

def show_help():
    """Show help information."""
    console.print("\n[bold blue]Help Center Editor - Help[/bold blue]")
    console.print("\n[bold]Global Commands:[/bold]")
    console.print("• Type 'q', 'quit', or 'exit' at any prompt to return to main menu")
    console.print("• Press Ctrl+C to exit the application")
    console.print("• Type 'h' in main menu to show this help")
    
    console.print("\n[bold]Features:[/bold]")
    console.print("• [green]Categories[/green]: Create and manage content categories")
    console.print("• [green]Guides[/green]: Create and manage help articles with rich text")
    console.print("• [green]Media[/green]: Upload and attach images to guides")
    console.print("• [green]GraphQL[/green]: Test GraphQL queries against the API")
    
    console.print("\n[bold]Tips:[/bold]")
    console.print("• Use descriptive slugs for better URLs")
    console.print("• Rich text uses JSON format with 'blocks' structure")
    console.print("• Media files are uploaded to Google Cloud Storage")
    console.print("• All changes are saved immediately to the database")
    
    console.print("\n[bold]API Endpoints:[/bold]")
    console.print("• REST API: http://localhost:8000/dev-editor/")
    console.print("• GraphQL: http://localhost:8000/graphql")
    console.print("• Health: http://localhost:8000/health")

async def main():
    editor = HelpCenterEditor()
    
    try:
        while True:
            console.print("\n[bold blue]Help Center Editor[/bold blue]")
            console.print("1. List categories")
            console.print("2. Create category")
            console.print("3. List guides")
            console.print("4. Create guide")
            console.print("5. Upload media")
            console.print("6. Attach media to guide")
            console.print("7. List media")
            console.print("8. Test GraphQL")
            console.print("h. Help")
            console.print("[bold red]9. Exit (or type 'q', 'quit', 'exit')[/bold red]")
            
            choice = Prompt.ask("Choose option (or type 'q' to quit, 'h' for help)", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "h", "q", "quit", "exit"])
            
            if choice == "1":
                await editor.list_categories()
            elif choice == "2":
                await editor.create_category()
            elif choice == "3":
                await editor.list_guides()
            elif choice == "4":
                await editor.create_guide()
            elif choice == "5":
                guide_id = Prompt.ask("Guide ID (optional)", default="")
                await editor.upload_media(guide_id if guide_id else None)
            elif choice == "6":
                await editor.attach_media_to_guide()
            elif choice == "7":
                await editor.list_media()
            elif choice == "8":
                await editor.test_graphql()
            elif choice == "h":
                show_help()
            elif choice in ["9", "q", "quit", "exit"]:
                if Confirm.ask("Are you sure you want to exit?"):
                    console.print("[green]Goodbye![/green]")
                    break
                else:
                    continue
                
    finally:
        await editor.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)
