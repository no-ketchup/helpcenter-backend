"""
Help Center Backend - Main FastAPI Application

A production-ready help center backend with GraphQL and REST APIs.
"""

import os
import tempfile
from contextlib import asynccontextmanager

import strawberry
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.db import get_session
from app.core.logging import get_correlation_id, get_logger, setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.rate_limiting import (
    limiter,
    setup_rate_limiting,
)
from app.core.settings import ALLOWED_ORIGINS, ENVIRONMENT, LOG_LEVEL
from app.core.validation import create_error_response, handle_validation_error
from app.domain.resolvers import Mutation, Query
from app.domain.rest import dev_editor_router, guide_editor_router, media_editor_router

setup_logging(LOG_LEVEL)

# Handle GOOGLE_APPLICATION_CREDENTIALS_JSON if present
if creds_json := os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.write(creds_json.encode("utf-8"))
    tmp.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    setup_logging(LOG_LEVEL)
    logger = get_logger("startup")
    logger.info("Application starting up", extra={"environment": ENVIRONMENT})
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Help Center Backend",
    description="A production-ready help center backend with GraphQL and REST APIs",
    version="1.0.0",
    lifespan=lifespan,
)


class GraphQLCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware for GraphQL OPTIONS requests."""

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" and request.url.path == "/graphql":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "http://localhost:3000",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Access-Control-Max-Age": "86400",
                },
            )
        response = await call_next(request)
        return response


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(GraphQLCORSMiddleware)

# Setup rate limiting
setup_rate_limiting(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    correlation_id = get_correlation_id()
    request_id = getattr(request.state, "request_id", None)

    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append(
            {
                "field": field,
                "message": error["msg"],
                "value": error.get("input"),
                "code": error["type"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Input validation failed",
            "details": details,
            "correlation_id": correlation_id,
            "request_id": request_id,
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic ValidationError."""
    correlation_id = get_correlation_id()
    request_id = getattr(request.state, "request_id", None)

    return create_error_response(
        handle_validation_error(exc, correlation_id, request_id), correlation_id, request_id
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    correlation_id = get_correlation_id()
    request_id = getattr(request.state, "request_id", None)

    return create_error_response(exc, correlation_id, request_id)


schema = strawberry.Schema(query=Query, mutation=Mutation)


async def get_context():
    return {"get_session": get_session}


graphql_app = GraphQLRouter(schema, allow_queries_via_get=True, context_getter=get_context)


@app.options("/graphql")
@limiter.limit("1000/hour")
async def graphql_options(request: Request):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": ",".join(ALLOWED_ORIGINS),
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
        },
    )


app.include_router(graphql_app, prefix="/graphql")


app.include_router(dev_editor_router)
app.include_router(guide_editor_router)
app.include_router(media_editor_router)


@app.get("/health")
@limiter.limit("1000/hour")
async def health_check(request: Request):
    """Health check endpoint."""
    return {"status": "healthy", "environment": ENVIRONMENT}
