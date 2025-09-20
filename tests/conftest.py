import pytest
from sqlmodel import SQLModel
from app.db import engine, Session
from app.seeds import seed

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    seed()

    yield

    SQLModel.metadata.drop_all(engine)