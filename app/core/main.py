from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException
from contextlib import asynccontextmanager
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.core.db import init_db
from app.core import settings
from app.domain.resolvers import Query, Mutation


# -------------------------
# Lifespan: run migrations / init DB
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


# Main app
app = FastAPI(lifespan=lifespan)


# -------------------------
# GraphQL schema
# -------------------------
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


# -------------------------
# Health
# -------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# -------------------------
# Dev Editor Guard
# -------------------------
async def verify_dev_editor_key(x_dev_editor_key: str = Header(None)):
    if not x_dev_editor_key or x_dev_editor_key != settings.DEV_EDITOR_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: invalid editor key")


# -------------------------
# Dev Editor Router
# -------------------------
dev_editor_router = APIRouter(
    prefix="/dev-editor",
    dependencies=[Depends(verify_dev_editor_key)],
)


@dev_editor_router.post("/insert-category")
async def insert_category(payload: dict):
    # TODO: replace stub with real mapper logic
    return {"message": "Category inserted", "payload": payload}


@dev_editor_router.post("/insert-guide")
async def insert_guide(payload: dict):
    # TODO: replace stub with real mapper logic
    return {"message": "Guide inserted", "payload": payload}


app.include_router(dev_editor_router)