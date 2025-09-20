from app.domain.models import Category
from app.core.db import async_session

async def dev_seed():
    """Insert some development data if not already present."""
    async with async_session() as session:
        # Check if categories exist
        result = await session.exec("SELECT COUNT(*) FROM category")
        count = result.first()[0]

        if count == 0:
            session.add_all([
                Category(name="Getting Started", slug="getting-started"),
                Category(name="FAQ", slug="faq"),
                Category(name="Troubleshooting", slug="troubleshooting"),
            ])
            await session.commit()