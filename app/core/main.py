from fastapi import FastAPI
from contextlib import asynccontextmanager
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.domain import schema
from app.core.db import init_db
from app.data.seeds import dev_seed

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Only if ENVIRONMENT=development
    import os
    if os.getenv("ENVIRONMENT") == "development":
        await dev_seed()

    yield
app = FastAPI(lifespan=lifespan)

@strawberry.type
class Query(schema.Query):
    pass

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
async def health_check():
    return {"status": "ok"}