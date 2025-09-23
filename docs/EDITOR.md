# Help Center Editor

A minimal CLI editor for managing your help center content.

## Quick Start

```bash
# Start the backend
make up

# Run the editor
make editor
```

## Features

### Guide Management
- Create guides with rich text content (JSON format)
- List all guides
- Attach media to guides

### Category Management
- Create categories
- List all categories
- Organize guides by category

### Media Management
- Upload images/screenshots
- Attach media to guides
- List all media
- Automatic guide association on upload

### GraphQL Testing
- Test GraphQL queries
- View data relationships
- Debug API responses

## Usage Examples

### Create a Guide with Screenshots

1. **Create Guide**: Choose option 4, enter title, slug, and body JSON
2. **Upload Media**: Choose option 5, provide file path and guide ID
3. **View Result**: Choose option 8 to test GraphQL queries

### Rich Text Body Format

```json
{
  "blocks": [
    {"type": "heading", "level": 1, "text": "Main Title"},
    {"type": "paragraph", "text": "Introduction text..."},
    {"type": "heading", "level": 2, "text": "Subsection"},
    {"type": "paragraph", "text": "More content..."}
  ]
}
```

### Media URLs

Media returns proper URLs that can be embedded in guide content:

```json
{
  "id": "uuid",
  "url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/helpcenter/filename.jpg",
  "alt": "Screenshot of the process"
}
```

## API Endpoints

The editor uses these REST endpoints:

- `GET /dev-editor/categories` - List categories
- `POST /dev-editor/categories` - Create category
- `GET /dev-editor/guides` - List guides
- `POST /dev-editor/guides` - Create guide
- `GET /dev-editor/media` - List media
- `POST /dev-editor/media/upload` - Upload media
- `POST /dev-editor/guides/{id}/media/{id}` - Attach media to guide

## GraphQL Queries

Test these queries in the editor:

```graphql
# Get all guides with their media
{
  guides {
    id
    title
    slug
    media {
      id
      url
      alt
    }
  }
}

# Get specific guide
{
  guide(slug: "your-guide-slug") {
    id
    title
    body
    media {
      id
      url
      alt
    }
  }
}
```

## Production Setup

For production, set up Cloudinary credentials:

```bash
# In .env.local
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

This will enable real image uploads instead of placeholder URLs.

## Tips

- Use descriptive alt text for accessibility
- Keep guide slugs URL-friendly (lowercase, hyphens)
- Test GraphQL queries to verify data relationships
- Media is automatically attached when uploading with guide_id
