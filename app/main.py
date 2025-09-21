from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.core.db import get_session
from app.domain.resolvers import Query, Mutation


# -------------------------
# Lifespan
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)


# -------------------------
# GraphQL schema
# -------------------------
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(
    schema,
    context_getter=lambda: {"session": Depends(get_session)},
)
app.include_router(graphql_app, prefix="/graphql")


# -------------------------
# Health
# -------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# -------------------------
# Dev Editor Router
# -------------------------
from app.core import dev_editor
app.include_router(dev_editor.router)