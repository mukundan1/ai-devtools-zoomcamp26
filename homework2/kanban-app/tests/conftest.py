import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_database(tmp_path_factory):
    database_path = tmp_path_factory.mktemp("database") / "test.db"

    os.environ["DATABASE_URL"] = f"sqlite:///{database_path}"

    # Import after DATABASE_URL is configured because the application
    # creates its SQLAlchemy engine during module import.
    from backend.main import app

    return app


@pytest.fixture()
def client(test_database):
    from backend.main import SessionLocal, Task

    with TestClient(test_database) as test_client:
        # Keep each test isolated while preserving the application lifecycle.
        with SessionLocal() as db:
            db.query(Task).delete()
            db.commit()

        yield test_client
